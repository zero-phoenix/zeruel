"""Signed synthetic checkpoint gateway. Stores no credentials or documents."""
import hashlib
import hmac
import json
import time
import urllib.request
import uuid
from urllib.parse import urlparse


class Checkpoint:
    def __init__(self, url, secret):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "script.google.com" or not parsed.path.endswith("/exec"):
            raise ValueError("Expected a deployed Google Apps Script HTTPS endpoint")
        if len(secret) < 32:
            raise ValueError("Checkpoint secret must be at least 32 characters")
        self.url, self.secret = url, secret

    def call(self, action, task_id, report=None):
        payload = json.dumps({"action": action, "id": task_id, "report": report}, separators=(",", ":"))
        timestamp = str(int(time.time()))
        nonce = uuid.uuid4().hex
        message = timestamp + "\n" + nonce + "\n" + payload
        signature = hmac.new(self.secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        body = json.dumps({"timestamp": timestamp, "nonce": nonce, "payload": payload,
                           "signature": signature}).encode()
        request = urllib.request.Request(self.url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=20) as response:
            value = json.load(response)
        if not value.get("ok"):
            raise ValueError("Checkpoint request rejected")
        return value
