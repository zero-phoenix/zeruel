"""Authenticated mobile interface for the synthetic milestone only."""
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import threading
import time
from .checkpoint import Checkpoint
from .probe import home_path, prepare, probe

ROOT = Path(__file__).resolve().parent.parent


class Controller:
    def __init__(self, gateway=None, run_probe=probe):
        self.gateway = gateway
        self.run_probe = run_probe
        self.lock = threading.Lock()
        self.status = {"state": "paused", "cloud_gate_passed": False}
        self.last_run = 0.0

    def start(self, task_id):
        if not re.fullmatch(r"[a-f0-9]{32}", task_id):
            return 400, {"state": "invalid_request"}
        if not self.lock.acquire(blocking=False):
            return 409, {"state": "active"}
        transferred = False
        try:
            if os.environ.get("RENDER") and self.gateway is None:
                return 503, {"state": "blocked_persistence"}
            if self.gateway:
                result = self.gateway.call("claim", task_id)
                if not result.get("claimed"):
                    self.status = result.get("record") or {"state": "active"}
                    return 200, self.status
            elif time.monotonic() - self.last_run < 30:
                return 429, {"state": "paused_cooldown"}
            self.status = {"id": task_id, "state": "active", "cloud_gate_passed": False}
            self.last_run = time.monotonic()
            threading.Thread(target=self.work, args=(task_id,), daemon=True).start()
            transferred = True
            return 202, self.status
        except (OSError, ValueError):
            return 503, {"state": "blocked_checkpoint"}
        finally:
            # Work thread owns release only when it was actually started.
            if not transferred:
                self.lock.release()

    def work(self, task_id):
        try:
            try:
                report = self.run_probe()
            except Exception:
                report = {"state": "failed_runtime", "cloud_gate_passed": False}
            self.status = {"id": task_id, **report}
            if self.gateway:
                try:
                    self.gateway.call("complete", task_id, report)
                    self.status["checkpoint_saved"] = True
                except (OSError, ValueError):
                    self.status.update(state="blocked_checkpoint", checkpoint_saved=False)
        finally:
            self.lock.release()

    def read(self, task_id=None):
        if task_id and self.gateway:
            return self.gateway.call("get", task_id).get("record") or {"state": "not_found"}
        return self.status


def make_handler(controller, token):
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
            return hmac.compare_digest(supplied, "Bearer " + token)

        def do_GET(self):
            if self.path == "/healthz":
                return self.send(200, {"service": "zeruel-synthetic-probe", "cloud_gate_passed": False})
            if self.path == "/":
                return self.send(200, (ROOT / "web" / "index.html").read_bytes(), "text/html; charset=utf-8")
            if self.path == "/app.js":
                return self.send(200, (ROOT / "web" / "app.js").read_bytes(), "text/javascript; charset=utf-8")
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
    credentials = os.environ.get("ZERUEL_GEMINI_OAUTH_JSON")
    if credentials:
        data = json.loads(credentials)
        if not isinstance(data, dict) or not data.get("refresh_token"):
            raise SystemExit("Invalid OAuth credential format")
        path = home_path() / ".gemini" / "oauth_creds.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        if os.name != "nt":
            path.chmod(0o600)
    gateway = None
    if os.environ.get("ZERUEL_CHECKPOINT_URL"):
        gateway = Checkpoint(os.environ["ZERUEL_CHECKPOINT_URL"], os.environ.get("ZERUEL_CHECKPOINT_SECRET", ""))
    controller = Controller(gateway)
    host = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    server = ThreadingHTTPServer((host, int(os.environ.get("PORT", "8765"))), make_handler(controller, token))
    print("Zeruel synthetic probe ready; desktop observation is disabled.", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
