"""Owner-only Google Sign-In: accepts a Google ID token only for the owner's verified address."""
import hashlib
import json
import threading
import time
from urllib.parse import urlencode
from urllib.request import urlopen

TOKENINFO = "https://oauth2.googleapis.com/tokeninfo"
ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


def fetch_tokeninfo(id_token):
    # POST keeps the ID token out of URLs and access logs.
    with urlopen(TOKENINFO, urlencode({"id_token": id_token}).encode(), timeout=5) as response:
        return json.load(response)


class GoogleOwnerVerifier:
    def __init__(self, client_id, owner_email, fetch=fetch_tokeninfo, clock=time.time):
        if not client_id or not owner_email:
            raise ValueError("client_id and owner_email are required")
        self.client_id, self.owner = client_id, owner_email.strip().lower()
        self.fetch, self.clock = fetch, clock
        self.cache = {}  # sha256(token) -> expiry; the token itself is never stored.
        self.lock = threading.Lock()

    def verify(self, id_token):
        if not isinstance(id_token, str) or not 20 <= len(id_token) <= 4096:
            return False
        key = hashlib.sha256(id_token.encode()).hexdigest()
        now = self.clock()
        with self.lock:
            expiry = self.cache.get(key)
        if expiry and expiry > now:
            return True
        try:
            info = self.fetch(id_token)
            accepted = (isinstance(info, dict) and info.get("aud") == self.client_id
                and info.get("iss") in ISSUERS
                and str(info.get("email", "")).lower() == self.owner
                and str(info.get("email_verified", "")).lower() == "true"
                and int(info.get("exp", 0)) > now)
        except Exception:
            return False  # Fail closed on network errors or malformed replies.
        if accepted:
            with self.lock:
                self.cache = {k: v for k, v in self.cache.items() if v > now}
                if len(self.cache) < 64:
                    self.cache[key] = int(info["exp"])
        return accepted
