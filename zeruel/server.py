"""Authenticated mobile interface for the synthetic milestone only."""
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import threading
import time
from .checkpoint import PrivateCheckpoint
from .google_auth import GoogleOwnerVerifier
from .probe import TOKEN, home_path, prepare, probe

ROOT = Path(__file__).resolve().parent.parent


class Controller:
    def __init__(self, gateway=None, run_probe=probe, recovery_dir=None):
        self.gateway, self.run_probe = gateway, run_probe
        self.recovery_dir = Path(recovery_dir) if recovery_dir else home_path() / "checkpoint-recovery"
        self.pending = {}
        self.lock = threading.Lock()
        self.status = {"state": "paused", "cloud_gate_passed": False}
        self.last_run = 0.0

    @staticmethod
    def public(record):
        allowed = {"id", "state", "started", "completed", "elapsed_seconds", "children_peak_rss_kib",
                   "children_cpu_seconds", "result", "checkpoint_saved", "recovered",
                   "engine", "model", "primary_state"}
        return {**{k: v for k, v in record.items() if k in allowed}, "cloud_gate_passed": False}

    def journal(self, task_id, value):
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        if os.name != "nt":
            self.recovery_dir.chmod(0o700)
        temporary = self.recovery_dir / (task_id + ".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            if os.name != "nt":
                os.chmod(temporary, 0o600)
            json.dump(value, stream)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(self.recovery_dir / (task_id + ".json"))

    def persist(self, task_id, pending):
        self.pending[task_id] = pending
        try:
            self.journal(task_id, pending)
            self.gateway.call("complete", task_id, pending["report"], generation=pending["generation"])
            self.status = self.public({"id": task_id, **pending["report"], "checkpoint_saved": True})
            # Keep the report for idempotent persistence retries after restart.
            return 200, self.status
        except (OSError, ValueError, TypeError):
            self.status = {"id": task_id, "state": "blocked_checkpoint", "checkpoint_saved": False,
                           "cloud_gate_passed": False}
            return 503, self.status

    def start(self, task_id):
        if not re.fullmatch(r"[a-f0-9]{32}", task_id):
            return 400, {"state": "invalid_request", "cloud_gate_passed": False}
        if not self.lock.acquire(blocking=False):
            return 409, {"state": "active", "cloud_gate_passed": False}
        transferred = False
        try:
            if os.environ.get("RENDER") and self.gateway is None:
                return 503, {"state": "blocked_persistence", "cloud_gate_passed": False}
            generation = None
            if self.gateway:
                pending = self.pending.get(task_id)
                path = self.recovery_dir / (task_id + ".json")
                if pending is None and path.exists():
                    pending = json.loads(path.read_text(encoding="utf-8"))
                if pending is not None:
                    if (not isinstance(pending, dict) or
                            not isinstance(pending.get("generation"), str) or
                            not re.fullmatch(r"[a-f0-9]{32}", pending["generation"]) or
                            (pending.get("report") is not None and not isinstance(pending["report"], dict))):
                        raise ValueError("Invalid recovery journal")
                    if pending.get("report") is not None:
                        return self.persist(task_id, pending)
                    self.status = {"id": task_id, "state": "paused_uncertain", "cloud_gate_passed": False}
                    return 200, self.status
                result = self.gateway.call("claim", task_id)
                if not result.get("claimed"):
                    self.status = self.public(result.get("record") or {"state": "paused_uncertain"})
                    # An existing lease belongs to an earlier worker; no local report proves its outcome.
                    if self.status["state"] == "active" and self.status.get("id") == task_id:
                        self.status["state"] = "paused_uncertain"
                    return 200, self.status
                generation = result.get("generation")
                if not isinstance(generation, str) or not re.fullmatch(r"[a-f0-9]{32}", generation):
                    raise ValueError("Missing lease generation")
                intent = {"generation": generation, "report": None}
                self.pending[task_id] = intent
                self.journal(task_id, intent)
            elif time.monotonic() - self.last_run < 30:
                return 429, {"state": "paused_cooldown", "cloud_gate_passed": False}
            self.status = {"id": task_id, "state": "active", "cloud_gate_passed": False}
            self.last_run = time.monotonic()
            threading.Thread(target=self.work, args=(task_id, generation), daemon=True).start()
            transferred = True
            return 202, self.status
        except (OSError, ValueError, TypeError):
            return 503, {"state": "blocked_checkpoint", "cloud_gate_passed": False}
        finally:
            if not transferred:
                self.lock.release()

    def work(self, task_id, generation=None):
        try:
            try:
                report = self.public(self.run_probe())
            except Exception:
                report = {"state": "failed_runtime", "cloud_gate_passed": False}
            self.status = {"id": task_id, **report}
            if self.gateway:
                self.persist(task_id, {"generation": generation, "report": report})
        finally:
            self.lock.release()

    def read(self, task_id=None):
        if task_id and self.gateway:
            record = self.public(self.gateway.call("get", task_id).get("record") or {"state": "not_found"})
            if record["state"] == "active" and not self.lock.locked():
                record["state"] = "paused_uncertain"
            return record
        return self.public(self.status)


def make_handler(controller, token, google=None, google_client_id=None):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, *args):
            # Access logs must never include headers, secrets or request bodies.
            pass

        def send(self, code, content, content_type="application/json"):
            data = content if isinstance(content, bytes) else json.dumps(content).encode()
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(data)

        def authorized(self):
            supplied = self.headers.get("Authorization", "")
            if supplied.startswith("Google "):
                # Owner-only Google Sign-In; any other account is rejected.
                return google is not None and google.verify(supplied[len("Google "):])
            # Bytes comparison: non-ASCII header values must yield 401, not an unhandled TypeError.
            return hmac.compare_digest(supplied.encode("utf-8", "surrogateescape"),
                                       ("Bearer " + token).encode("utf-8"))

        def do_GET(self):
            if self.path == "/healthz":
                return self.send(200, {"service": "zeruel-synthetic-probe", "cloud_gate_passed": False})
            if self.path == "/":
                return self.send(200, (ROOT / "web" / "index.html").read_bytes(), "text/html; charset=utf-8")
            if self.path == "/app.js":
                return self.send(200, (ROOT / "web" / "app.js").read_bytes(), "text/javascript; charset=utf-8")
            if self.path == "/api/config":
                # The OAuth client ID is public by design; no secret is exposed here.
                return self.send(200, {"google_client_id": google_client_id if google else None})
            if not self.authorized():
                return self.send(401, {"state": "disconnected"})
            if self.path == "/api/status":
                return self.send(200, controller.read())
            prefix = "/api/checkpoint/"
            if self.path.startswith(prefix) and re.fullmatch(r"[a-f0-9]{32}", self.path[len(prefix):]):
                try:
                    return self.send(200, controller.read(self.path[len(prefix):]))
                except (OSError, ValueError):
                    return self.send(503, {"state": "blocked_checkpoint"})
            self.send(404, {"state": "not_found"})

        def do_POST(self):
            if not self.authorized():
                return self.send(401, {"state": "disconnected"})
            if self.path != "/api/probe":
                return self.send(404, {"state": "not_found"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size <= 0 or size > 1024:
                    return self.send(413, {"state": "invalid_request"})
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict) or set(data) != {"id"} or not isinstance(data["id"], str):
                    return self.send(400, {"state": "synthetic_only"})
                code, value = controller.start(data["id"])
                return self.send(code, value)
            except (ValueError, TypeError):
                return self.send(400, {"state": "invalid_request"})
    return Handler


def main():
    token = os.environ.get("ZERUEL_ACCESS_TOKEN", "")
    if len(token) < 32:
        raise SystemExit("Configure ZERUEL_ACCESS_TOKEN (at least 32 characters); never place it in a URL.")
    prepare(home_path())
    # Import occurs only if the owner explicitly provisions this secret.
    # No automatic extraction of credentials from other applications.
    credentials = os.environ.get("ZERUEL_AGY_OAUTH_TOKEN", "").strip()
    if credentials:
        # The agy session file the owner created for Zeruel, provisioned as a Render secret.
        path = home_path() / TOKEN
        path.write_text(credentials, encoding="utf-8")
        if os.name != "nt":
            path.chmod(0o600)
    gateway = None
    if os.environ.get("ZERUEL_CHECKPOINT_URL"):
        raise SystemExit("Public checkpoint URLs are disabled; use owner OAuth.")
    if os.environ.get("ZERUEL_CHECKPOINT_DEPLOYMENT_ID"):
        gateway = PrivateCheckpoint(os.environ["ZERUEL_CHECKPOINT_DEPLOYMENT_ID"],
            os.environ.get("ZERUEL_CHECKPOINT_SECRET", ""),
            json.loads(os.environ.get("ZERUEL_CHECKPOINT_OAUTH_JSON", "null")))
    controller = Controller(gateway)
    client_id = os.environ.get("ZERUEL_GOOGLE_CLIENT_ID", "").strip()
    owner = os.environ.get("ZERUEL_OWNER_EMAIL", "").strip()
    google = GoogleOwnerVerifier(client_id, owner) if client_id and owner else None
    host = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    server = ThreadingHTTPServer((host, int(os.environ.get("PORT", "8765"))),
                                 make_handler(controller, token, google, client_id))
    print("Zeruel synthetic probe ready; desktop observation is disabled.", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
