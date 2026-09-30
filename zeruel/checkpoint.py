"""Signed synthetic checkpoint gateway. Stores no credentials or documents."""
import hashlib
import hmac
import json
import time
import urllib.request
import uuid
from urllib.parse import urlparse, urlencode
import re
import threading


class Checkpoint:
    def __init__(self, url, secret):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "script.google.com" or not parsed.path.endswith("/exec"):
            raise ValueError("Expected a deployed Google Apps Script HTTPS endpoint")
        if len(secret) < 32:
            raise ValueError("Checkpoint secret must be at least 32 characters")
        self.url, self.secret = url, secret

    def envelope(self, action, task_id, report=None, generation=None, confirm=None):
        data = {"action": action, "id": task_id, "report": report, "generation": generation}
        if confirm is not None:
            data["confirm"] = confirm
        payload = json.dumps(data, separators=(",", ":"))
        timestamp = str(int(time.time()))
        nonce = uuid.uuid4().hex
        message = timestamp + "\n" + nonce + "\n" + payload
        signature = hmac.new(self.secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        return {"timestamp": timestamp, "nonce": nonce, "payload": payload, "signature": signature}

    def call(self, action, task_id, report=None, generation=None, confirm=None):
        raise ValueError("Public web checkpoint is disabled; configure owner OAuth")


class PrivateCheckpoint(Checkpoint):
    """Owner-only Apps Script API transport. Never follows credential redirects."""
    def __init__(self, deployment_id, secret, credentials):
        if not re.fullmatch(r"[A-Za-z0-9_-]{20,200}", deployment_id) or len(secret) < 32:
            raise ValueError("Invalid private checkpoint configuration")
        if not isinstance(credentials, dict) or any(not isinstance(credentials.get(k), str) or not credentials[k]
                for k in ("client_id", "client_secret", "refresh_token")):
            raise ValueError("Invalid owner OAuth credentials")
        self.url = "https://script.googleapis.com/v1/scripts/" + deployment_id + ":run"
        self.secret, self.credentials = secret, credentials
        self.lock = threading.Lock()
        self.access_token, self.expires_at = None, 0

    @staticmethod
    def request_json(url, body, headers):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        request = urllib.request.Request(url, data=body, headers=headers)
        with urllib.request.build_opener(NoRedirect).open(request, timeout=20) as response:
            return json.loads(response.read(65537))

    def token(self):
        with self.lock:
            if self.access_token and self.expires_at > time.time() + 360:
                return self.access_token
            fields = {k:self.credentials[k] for k in ("client_id", "client_secret", "refresh_token")}
            fields["grant_type"] = "refresh_token"
            result = self.request_json("https://oauth2.googleapis.com/token", urlencode(fields).encode(),
                                       {"Content-Type":"application/x-www-form-urlencoded"})
            if not isinstance(result.get("access_token"), str) or result.get("token_type", "").lower() != "bearer":
                raise ValueError("Owner OAuth refresh rejected")
            self.access_token = result["access_token"]
            self.expires_at = time.time() + int(result.get("expires_in", 0))
            return self.access_token

    def call(self, action, task_id, report=None, generation=None, confirm=None):
        body = json.dumps({"function":"runCheckpoint", "parameters":[self.envelope(action, task_id, report, generation, confirm)],
                           "devMode":False}).encode()
        value = self.request_json(self.url, body,
                {"Content-Type":"application/json", "Authorization":"Bearer " + self.token()})
        result = value.get("response", {}).get("result")
        if value.get("error") or not isinstance(result, dict) or not result.get("ok"):
            raise ValueError("Private checkpoint rejected")
        return result

