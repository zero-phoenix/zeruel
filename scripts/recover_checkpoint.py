"""Owner-only manual recovery of an uncertain checkpoint lease. Never calls the model.

Run it only after confirming the original worker finished (process stopped or Render
instance restarted). With a durable local report it stores that exact report; without
one it closes the ID as ``terminal_unknown`` (a tombstone), never as success.
"""

import argparse
import getpass
import json
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zeruel.checkpoint import PrivateCheckpoint  # noqa: E402
from zeruel.probe import home_path  # noqa: E402

HEX = re.compile(r"[a-f0-9]{32}")
CONFIRM = "owner_worker_finished"


def load_journal(directory, task_id):
    path = Path(directory) / (task_id + ".json")
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("generation"), str)
        or not HEX.fullmatch(value["generation"])
        or (value.get("report") is not None and not isinstance(value["report"], dict))
    ):
        raise ValueError("Invalid recovery journal")
    return value


def recover(gateway, task_id, journal, generation=None, unknown=False):
    """Returns the public record. Raises ValueError when recovery is not allowed."""
    if not HEX.fullmatch(task_id):
        raise ValueError("Invalid task id")
    report = journal.get("report") if journal else None
    generation = journal["generation"] if journal else generation
    if not isinstance(generation, str) or not HEX.fullmatch(generation):
        raise ValueError(
            "Generation unavailable; read it privately from the script properties"
        )
    if report is None and not unknown:
        raise ValueError(
            "No durable report: rerun with --unknown to close the ID as terminal_unknown"
        )
    if report is not None and unknown:
        raise ValueError("A durable report exists; --unknown would discard it")
    result = gateway.call(
        "recover", task_id, report, generation=generation, confirm=CONFIRM
    )
    record = result.get("record") or {}
    return {k: v for k, v in record.items() if k not in ("generation", "fingerprint")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument(
        "--journal-dir", default=str(home_path() / "checkpoint-recovery")
    )
    parser.add_argument(
        "--unknown", action="store_true", help="close without a durable report"
    )
    parser.add_argument("--confirm-worker-finished", action="store_true", required=True)
    args = parser.parse_args(argv)
    journal = load_journal(args.journal_dir, args.task_id)
    generation = None
    if journal is None:
        # Read privately; never passed as an argument so it stays out of shell history.
        generation = getpass.getpass(
            "Generation (32 hex, from private script properties): "
        ).strip()
    gateway = PrivateCheckpoint(
        os.environ.get("ZERUEL_CHECKPOINT_DEPLOYMENT_ID", ""),
        os.environ.get("ZERUEL_CHECKPOINT_SECRET", ""),
        json.loads(os.environ.get("ZERUEL_CHECKPOINT_OAUTH_JSON", "null")),
    )
    print(json.dumps(recover(gateway, args.task_id, journal, generation, args.unknown)))


if __name__ == "__main__":
    main()
