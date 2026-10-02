"""Obtain the owner's OAuth refresh token for the Apps Script checkpoint.

Usage: python tools/get_checkpoint_oauth.py <client_secret_*.json>

Desktop OAuth client, loopback redirect with PKCE, scope userinfo.email only.
Writes {client_id, client_secret, refresh_token} to
%USERPROFILE%/.zeruel-private/checkpoint-oauth.json and never prints secrets.
"""
import base64, hashlib, http.server, json, os, secrets, sys, urllib.parse, urllib.request, webbrowser

SCOPE = "https://www.googleapis.com/auth/userinfo.email"
OUT = os.path.join(os.path.expanduser("~"), ".zeruel-private", "checkpoint-oauth.json")


def main(path, out_file=None):
    destination = out_file or os.environ.get("ZERUEL_OAUTH_OUT", OUT)
    with open(path, encoding="utf-8") as f:
        client = json.load(f)["installed"]
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] == state and "code" in q:
                result["code"] = q["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Zeruel: puedes cerrar esta pestaña.".encode())

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    redirect = f"http://127.0.0.1:{server.server_port}"
    url = client["auth_uri"] + "?" + urllib.parse.urlencode({
        "client_id": client["client_id"], "redirect_uri": redirect, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent", "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256"})
    print("Abriendo el navegador para autorizar con la cuenta del propietario...")
    webbrowser.open(url)
    server.timeout = 300
    while "code" not in result:
        server.handle_request()
    body = urllib.parse.urlencode({
        "code": result["code"], "client_id": client["client_id"], "client_secret": client["client_secret"],
        "redirect_uri": redirect, "grant_type": "authorization_code", "code_verifier": verifier}).encode()
    with urllib.request.urlopen(client["token_uri"], body, timeout=30) as r:
        token = json.load(r)
    if "refresh_token" not in token:
        sys.exit("Google no devolvió refresh_token; revoca el acceso previo y repite.")
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with open(destination, "w", encoding="utf-8") as f:
        json.dump({"client_id": client["client_id"], "client_secret": client["client_secret"],
                   "refresh_token": token["refresh_token"]}, f)
    print(f"Guardado en {destination} (no se muestra el contenido). Ámbitos: {token.get('scope')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    custom_out = sys.argv[2] if len(sys.argv) > 2 else None
    main(sys.argv[1], custom_out)
