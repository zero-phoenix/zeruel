"""Owner-only Google Sign-In: accepts a Google ID token only for the owner's verified address."""
import base64
import collections
import hashlib
import json
import threading
import time
from urllib.parse import urlencode
from urllib.request import urlopen

TOKENINFO = "https://oauth2.googleapis.com/tokeninfo"
ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
MAX_CHECKS_PER_MINUTE = 10  # Caps outbound tokeninfo calls so junk tokens cannot flood Google or Render.


def fetch_tokeninfo(id_token):
    # POST keeps the ID token out of URLs and access logs.
    with urlopen(TOKENINFO, urlencode({"id_token": id_token}).encode(), timeout=5) as response:
        return json.load(response)


def unverified_claims(id_token):
    """Decode the JWT payload WITHOUT checking the signature (used only as a cheap local pre-filter)."""
    parts = id_token.split(".")
    if len(parts) != 3:
        return None
    try:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
    except (ValueError, UnicodeError):
        return None
    return claims if isinstance(claims, dict) else None


class GoogleOwnerVerifier:
    def __init__(self, client_id, owner_email, fetch=fetch_tokeninfo, clock=time.time):
        if not client_id or not owner_email:
            raise ValueError("client_id and owner_email are required")
        self.client_id, self.owner = client_id, owner_email.strip().lower()
        self.fetch, self.clock = fetch, clock
        self.cache = {}  # sha256(token) -> expiry; the token itself is never stored.
        self.checks = collections.deque()  # timestamps of recent tokeninfo calls
        self.lock = threading.Lock()

    def accepted(self, claims, now):
        try:
            return (claims.get("aud") == self.client_id and claims.get("iss") in ISSUERS
                    and str(claims.get("email", "")).lower() == self.owner
                    and int(claims.get("exp", 0)) > now)
        except (TypeError, ValueError):
            return False

    def verify(self, id_token):
        return self.check(id_token)[0]

    def reject_reason(self, claims, now):
        """Category of a rejection, never the address itself (it is personal data)."""
        try:
            if claims.get("aud") != self.client_id or claims.get("iss") not in ISSUERS:
                return "wrong_audience"
            if str(claims.get("email", "")).lower() != self.owner:
                return "not_owner"
            if int(claims.get("exp", 0)) <= now:
                return "expired"
        except (TypeError, ValueError):
            return "malformed"
        return "unverified_email"

    def check(self, id_token):
        """Returns (accepted, reason); reason is a fixed category safe to log."""
        if not isinstance(id_token, str) or not 20 <= len(id_token) <= 4096:
            return False, "malformed"
        key = hashlib.sha256(id_token.encode("utf-8", "surrogateescape")).hexdigest()
        now = self.clock()
        with self.lock:
            expiry = self.cache.get(key)
        if expiry and expiry > now:
            return True, "ok"
        # Local pre-filter: tokens that do not even claim to be the owner's never reach Google.
        claims = unverified_claims(id_token)
        if claims is None:
            return False, "malformed"
        if not self.accepted(claims, now):
            return False, self.reject_reason(claims, now)
        with self.lock:
            while self.checks and self.checks[0] <= now - 60:
                self.checks.popleft()
            if len(self.checks) >= MAX_CHECKS_PER_MINUTE:
                return False, "rate_limited"
            self.checks.append(now)
        try:
            info = self.fetch(id_token)  # Google remains the source of truth for the signature.
            now = self.clock()  # The token may expire while tokeninfo is in flight.
            ok = (isinstance(info, dict) and self.accepted(info, now)
                  and str(info.get("email_verified", "")).lower() == "true")
        except Exception:
            return False, "tokeninfo_failed"  # Fail closed on network errors or malformed replies.
        if ok:
            with self.lock:
                self.cache = {k: v for k, v in self.cache.items() if v > now}
                if len(self.cache) < 64:
                    self.cache[key] = int(info["exp"])
        if ok:
            return True, "ok"
        return False, self.reject_reason(info, now) if isinstance(info, dict) else "malformed"
