"""DeepSeek assistant for reviewing PUBLIC code only, with a shared spend ledger.

Key: environment variable DEEPSEEK_API_KEY (never a file in the repo, never printed).
Ledger: DEEPSEEK_LEDGER (default ~/.zeruel-private/deepseek_ledger.json), outside the repo.
Budget: US$1 total authorized by the owner, shared across assistants and computers;
carry the committed amount forward with DEEPSEEK_SPENT_BEFORE when the ledger is new.

Usage: python tools/deepseek_assist.py <prompt_file> <out_file> [max_output_tokens]
Never send conversations, screenshots, case files, personal memory or secrets.
"""

import json
import os
from pathlib import Path
import sys
import time
import urllib.request

BUDGET = 1.00
PEAK_IN, PEAK_OUT = (
    0.30,
    1.20,
)  # US$/1M tokens (peak, conservative), deepseek-flash, checked 29/09/2026
MODEL, EFFORT = "deepseek-flash", "max"
LEDGER = Path(
    os.environ.get("DEEPSEEK_LEDGER")
    or Path.home() / ".zeruel-private" / "deepseek_ledger.json"
)


def with_ledger(fn):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    lock = LEDGER.with_suffix(".lock")
    for _ in range(100):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            time.sleep(0.1)
    else:
        raise SystemExit("Ledger locked; another assistant is reserving budget")
    try:
        data = (
            json.loads(LEDGER.read_text())
            if LEDGER.exists()
            else {
                "entries": [],
                "spent_before": float(os.environ.get("DEEPSEEK_SPENT_BEFORE", "0")),
            }
        )
        out = fn(data)
        tmp = LEDGER.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=1))
        tmp.replace(LEDGER)
        return out
    finally:
        os.close(fd)
        os.remove(lock)


def committed(data):
    return data.get("spent_before", 0) + sum(
        e.get("actual", e["reserved"]) for e in data["entries"]
    )


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise SystemExit("Set DEEPSEEK_API_KEY privately (never in chat or the repo)")
    prompt = Path(sys.argv[1]).read_text(encoding="utf-8")
    # Reasoning tokens count as output: below ~60000 the answer can come back empty.
    max_out = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
    est_in = len(prompt) // 2 + 2000
    reserve = round(est_in * PEAK_IN / 1e6 + max_out * PEAK_OUT / 1e6, 6)
    rid = time.strftime("%Y%m%dT%H%M%S")

    def reserve_fn(d):
        if committed(d) + reserve > BUDGET:
            raise SystemExit(
                f"Budget exceeded: committed {committed(d):.4f} + {reserve:.4f} > {BUDGET}"
            )
        d["entries"].append({"id": rid, "reserved": reserve, "state": "reserved"})

    with_ledger(reserve_fn)
    body = json.dumps(
        {
            "model": MODEL,
            "reasoning_effort": EFFORT,
            "max_tokens": max_out,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode()
    request = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
    )
    try:
        with urllib.request.urlopen(request, timeout=1200) as response:
            result = json.load(response)
    except (
        Exception
    ) as exc:  # uncertain: keep the reservation, never retry automatically
        with_ledger(
            lambda d: [
                e.update(state="uncertain") for e in d["entries"] if e["id"] == rid
            ]
        )
        raise SystemExit("Uncertain call; reservation kept: " + type(exc).__name__)
    usage = result.get("usage", {})
    actual = round(
        usage.get("prompt_tokens", est_in) * PEAK_IN / 1e6
        + usage.get("completion_tokens", max_out) * PEAK_OUT / 1e6,
        6,
    )
    with_ledger(
        lambda d: [
            e.update(state="done", actual=actual, usage=usage)
            for e in d["entries"]
            if e["id"] == rid
        ]
    )
    Path(sys.argv[2]).write_text(
        result["choices"][0]["message"]["content"], encoding="utf-8"
    )
    print(f"ok cost<=US${actual:.4f} tokens={usage}")


if __name__ == "__main__":
    main()
