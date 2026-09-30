"""Fixed, tool-free Google AI Pro probe through Antigravity CLI. Never accepts user documents."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request

VERSION = "1.2.14"  # Antigravity CLI (agy), pinned; Gemini CLI stopped serving AI Pro on 18/06/2026
MODEL = "gemini-3.8-flash-high"
EXPECTED = {"marker": "ZERUEL_OK", "sum": 42}
PROMPT = ('This is a synthetic connectivity test. Do not use tools or read files. '
          'Return only this JSON object, without markdown: {"marker":"ZERUEL_OK","sum":42}')
# Any of these would move agy off the owner's subscription onto a billable route.
FORBIDDEN = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI",
             "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_GENAI_USE_GCA", "CLOUD_SHELL")
TOKEN = Path(".gemini") / "antigravity-cli" / "antigravity-oauth-token"
FREE_HOST = "generativelanguage.googleapis.com"
FREE_MODEL = "gemini-flash-latest"  # fixed; no variable can point the fallback at another model
FREE_URL = "https://" + FREE_HOST + "/v1beta/models/" + FREE_MODEL + ":generateContent"


class Blocked(Exception):
    def __init__(self, state):
        self.state = state


def home_path():
    # An empty value must not resolve to the current directory.
    return Path(os.environ.get("ZERUEL_PRIVATE_HOME") or "work/private/gemini-home").resolve()


def prepare(home):
    """Isolated agy home (HOME for the child); never the user's own profile."""
    folder = home / TOKEN.parent
    folder.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        home.chmod(0o700)
        folder.chmod(0o700)
    return folder


def preflight(env, home, binary):
    if any(env.get(name) for name in FORBIDDEN):
        raise Blocked("blocked_paid_auth")
    if not binary.is_file():
        raise Blocked("blocked_cli_missing")
    # A session created explicitly for Zeruel by the owner's sign-in. Never copied
    # from the Antigravity desktop app, browser sessions or another profile.
    if not (home / TOKEN).is_file():
        raise Blocked("blocked_auth")


def child_environment(env, home):
    # Do not expose Render's service secrets, GitHub tokens or checkpoint key
    # to the model's process. OAuth credentials remain in its private profile.
    allowed = ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE",
               "APPDATA", "LOCALAPPDATA", "LANG", "LC_ALL", "SSL_CERT_FILE",
               "SSL_CERT_DIR", "NODE_EXTRA_CA_CERTS")
    result = {key: env[key] for key in allowed if key in env}
    for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA"):
        result[name] = str(home)
    result["NO_BROWSER"] = "true"
    return result


def run_child(command, env, cwd, timeout):
    kwargs = {"env": env, "cwd": cwd, "stdin": subprocess.DEVNULL,
              "stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True,
              "encoding": "utf-8", "errors": "replace"}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    else:
        kwargs["start_new_session"] = True
    process = subprocess.Popen(command, **kwargs)
    try:
        out, err = process.communicate(timeout=timeout)
        return process.returncode, out, err
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           creationflags=subprocess.CREATE_NO_WINDOW, check=False)
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Exited between the timeout and the kill.
        try:
            process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=10)
        raise Blocked("paused_timeout")


def classify_error(text):
    value = text.lower()
    if any(term in value for term in ("429", "resource_exhausted", "quota", "rate limit")):
        return "paused_quota"
    if any(term in value for term in ("401", "403", "unauthorized", "authentication", "login", "invalid_grant",
                                      "authentication failed or timed out")):
        return "blocked_auth"
    return "failed_cli"


def children_usage():
    if sys.platform == "win32":
        return None
    import resource
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak = usage.ru_maxrss // 1024 if sys.platform == "darwin" else usage.ru_maxrss  # macOS reports bytes
    return peak, usage.ru_utime + usage.ru_stime


class NoRedirect(urllib.request.HTTPRedirectHandler):
    # A redirect would resend the API key header to another host.
    def redirect_request(self, *args):
        return None


def free_open(request, timeout):
    return urllib.request.build_opener(NoRedirect).open(request, timeout=timeout)


def free_tier(key, opener=free_open):
    """Owner-approved fallback after AI Pro quota: synthetic prompt only, key sent as header."""
    body = json.dumps({"contents": [{"parts": [{"text": PROMPT}]}],
                       "generationConfig": {"responseMimeType": "application/json"}}).encode()
    request = urllib.request.Request(FREE_URL, data=body,
                                     headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with opener(request, timeout=60) as response:
            value = json.loads(response.read(65537))
        text = value["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
    except OSError as exc:
        # 429 or a 403 quotaExceeded both mean the free quota is exhausted.
        detail = str(getattr(exc, "code", "")) + " " + str(exc)
        raise Blocked("paused_quota" if classify_error(detail) == "paused_quota" or "429" in detail
                      else "failed_cli")
    except (ValueError, TypeError, KeyError, IndexError):
        raise Blocked("failed_response")
    if parsed != EXPECTED:
        raise Blocked("failed_response")


def probe(env=None, runner=run_child, opener=free_open):
    env = dict(os.environ if env is None else env)
    home = Path(env.get("ZERUEL_PRIVATE_HOME") or "work/private/gemini-home").resolve()
    binary = Path(env.get("ZERUEL_AGY_BIN") or "work/agy/agy").resolve()
    started = time.monotonic()
    baseline = children_usage()
    report = {"state": "disconnected", "engine": "antigravity-cli", "model": MODEL, "cli_version": VERSION,
              "synthetic_only": True, "subscription_verified": False, "cloud_gate_passed": False}
    try:
        preflight(env, home, binary)
        prepare(home)
        scratch = home / "synthetic-workspace"
        scratch.mkdir(exist_ok=True)
        code, out, err = runner([str(binary), "-p", PROMPT, "--output-format", "json", "--model", MODEL,
                                 "--sandbox", "--disable-slash-commands", "--print-timeout", "110s"],
                                child_environment(env, home), str(scratch), 150)
        try:
            envelope = json.loads(out)
            if not isinstance(envelope, dict):
                raise ValueError
        except (ValueError, TypeError):
            raise Blocked(classify_error(err) if code else "failed_response")
        if "print timeout" in err or envelope.get("status") == "TIMEOUT":
            # agy returns partial output after --print-timeout; never treat it as an answer.
            raise Blocked("paused_timeout")
        if envelope.get("denied_actions"):
            # The model tried a tool; print mode denied it, but the run is not a clean answer.
            raise Blocked("failed_response")
        if code or envelope.get("status") != "SUCCESS" or envelope.get("error"):
            # Never publish raw error text: it may contain tokens.
            raise Blocked(classify_error(json.dumps(envelope.get("error")) + err))
        # --json-schema is not used: agy implements it as an internal tool that stalls on 0.1 CPU.
        # The reply must be exactly the expected object; anything else fails closed.
        try:
            parsed = json.loads(envelope.get("response") or "")
        except (ValueError, TypeError):
            raise Blocked("failed_response")
        if parsed != EXPECTED:
            raise Blocked("failed_response")
        report.update(state="synthetic_success", result=EXPECTED)
        # Connectivity alone does not prove plan entitlement or restart safety.
    except Blocked as exc:
        report["state"] = exc.state
    except (OSError, ValueError):
        report["state"] = "failed_runtime"
    key = env.get("ZERUEL_GEMINI_FREE_KEY", "")
    if report["state"] == "paused_quota" and key:
        report.update(engine="gemini-api-free-tier", model=FREE_MODEL, primary_state="paused_quota")
        try:
            free_tier(key, opener)
            report.update(state="synthetic_success", result=EXPECTED)
        except Blocked as exc:
            report["state"] = exc.state
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    usage = children_usage()
    if usage and baseline:
        # RUSAGE_CHILDREN is cumulative for the server's lifetime: report this run's CPU only.
        # Peak RSS cannot be isolated per run; it is the lifetime maximum of finished children.
        report["children_peak_rss_kib"] = usage[0]
        report["children_cpu_seconds"] = round(usage[1] - baseline[1], 3)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        path = prepare(home_path())
        print(json.dumps({"state": "blocked_auth", "isolated_profile": str(path)}, indent=2))
        return 0
    report = probe()
    print(json.dumps(report, indent=2))
    return 0 if report["state"] == "synthetic_success" else 2


if __name__ == "__main__":
    raise SystemExit(main())
