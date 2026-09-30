"""Fixed, tool-free Gemini subscription probe. Never accepts user documents."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

VERSION = "0.62.0"
EXPECTED = {"marker": "ZERUEL_OK", "sum": 42}
PROMPT = ('This is a synthetic connectivity test. Do not use tools or read files. '
          'Return only this JSON object, without markdown: {"marker":"ZERUEL_OK","sum":42}')
FORBIDDEN = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI",
             "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_GENAI_USE_GCA", "CLOUD_SHELL")


class Blocked(Exception):
    def __init__(self, state):
        self.state = state


def home_path():
    return Path(os.environ.get("ZERUEL_PRIVATE_HOME", "work/private/gemini-home")).resolve()


def prepare(home):
    """Use an isolated CLI profile; never edit the user's existing profile."""
    folder = home / ".gemini"
    folder.mkdir(parents=True, exist_ok=True)
    settings = {"security": {"auth": {"selectedType": "oauth-personal",
                                     "enforcedType": "oauth-personal"}},
                "general": {"enableAutoUpdate": False},
                "telemetry": {"enabled": False},
                "mcpServers": {}, "hooks": {},
                "tools": {"exclude": ["run_shell_command", "read_file", "read_many_files",
                           "list_directory", "glob", "grep_search", "write_file", "replace",
                           "web_fetch", "google_web_search", "save_memory", "write_todos",
                           "activate_skill", "ask_user", "enter_plan_mode", "exit_plan_mode"]}}
    target = folder / "settings.json"
    target.write_text(json.dumps(settings), encoding="utf-8")
    policies = folder / "policies"
    policies.mkdir(exist_ok=True)
    (policies / "zeruel.toml").write_text(
        '[[rule]]\ntoolName = "*"\ndecision = "deny"\npriority = 999\n', encoding="utf-8")
    if os.name != "nt":
        home.chmod(0o700)
        folder.chmod(0o700)
        target.chmod(0o600)
    return folder


def preflight(env, home, bundle):
    if any(env.get(name) for name in FORBIDDEN):
        raise Blocked("blocked_paid_auth")
    if not bundle.is_file():
        raise Blocked("blocked_cli_missing")
    # A separate, explicitly authenticated profile is required. No extraction
    # from Antigravity, Codex, browser sessions or the user's Gemini profile.
    creds = home / ".gemini" / "oauth_creds.json"
    if not creds.is_file():
        raise Blocked("blocked_auth")


def child_environment(env, home):
    # Do not expose Render's service secrets, GitHub tokens or checkpoint key
    # to the model's process. OAuth credentials remain in its private profile.
    allowed = ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE",
               "APPDATA", "LOCALAPPDATA", "LANG", "LC_ALL", "SSL_CERT_FILE",
               "SSL_CERT_DIR", "NODE_EXTRA_CA_CERTS")
    result = {key: env[key] for key in allowed if key in env}
    result["GEMINI_CLI_HOME"] = str(home)
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
            os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise Blocked("paused_timeout")


def classify_error(text):
    value = text.lower()
    if any(term in value for term in ("429", "resource_exhausted", "quota", "rate limit")):
        return "paused_quota"
    if any(term in value for term in ("401", "403", "unauthorized", "authentication", "login", "invalid_grant")):
        return "blocked_auth"
    return "failed_cli"


def probe(env=None, runner=run_child):
    env = dict(os.environ if env is None else env)
    home = Path(env.get("ZERUEL_PRIVATE_HOME", "work/private/gemini-home")).resolve()
    bundle = Path(env.get("ZERUEL_CLI_BUNDLE", "work/gemini-cli/package/bundle/gemini.js")).resolve()
    started = time.monotonic()
    report = {"state": "disconnected", "cli_version": VERSION,
              "synthetic_only": True, "subscription_verified": False,
              "cloud_gate_passed": False}
    try:
        preflight(env, home, bundle)
        prepare(home)
        scratch = home / "synthetic-workspace"
        scratch.mkdir(exist_ok=True)
        code, out, err = runner([env.get("ZERUEL_NODE", "node"), str(bundle),
                                "-p", PROMPT, "--output-format", "json"],
                               child_environment(env, home), str(scratch), 120)
        if code:
            raise Blocked(classify_error(err + out))
        try:
            envelope = json.loads(out)
            if envelope.get("error"):
                # Never publish raw exception messages: they may contain tokens.
                raise Blocked(classify_error(json.dumps(envelope["error"])))
            response = envelope.get("response", "")
            parsed = json.loads(response)
        except (ValueError, TypeError, AttributeError):
            raise Blocked("failed_response")
        if parsed != EXPECTED:
            raise Blocked("failed_response")
        report.update(state="synthetic_success", result=EXPECTED)
        # Connectivity alone does not prove plan entitlement or restart safety.
    except Blocked as exc:
        report["state"] = exc.state
    except (OSError, ValueError):
        report["state"] = "failed_runtime"
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    if sys.platform != "win32":
        import resource
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        report["children_peak_rss_kib"] = usage.ru_maxrss
        report["children_cpu_seconds"] = round(usage.ru_utime + usage.ru_stime, 3)
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
