from http.server import ThreadingHTTPServer
import json
import threading
import unittest
import urllib.error
import urllib.request
from zeruel.google_auth import GoogleOwnerVerifier
from zeruel.server import Controller, make_handler

CLIENT = 'client.apps.googleusercontent.com'
OWNER = 'owner@example.test'
TOKEN = 'eyJ' + 'a' * 60


def info(**changes):
    value = {'aud': CLIENT, 'iss': 'https://accounts.google.com', 'email': OWNER,
             'email_verified': 'true', 'exp': '2000'}
    value.update(changes)
    return value


class VerifierTests(unittest.TestCase):
    def verifier(self, reply, calls=None):
        def fetch(token):
            if calls is not None: calls.append(token)
            if isinstance(reply, Exception): raise reply
            return reply
        return GoogleOwnerVerifier(CLIENT, OWNER, fetch=fetch, clock=lambda: 1000)

    def test_owner_accepted_case_insensitive(self):
        self.assertTrue(self.verifier(info(email='Owner@Example.test')).verify(TOKEN))

    def test_rejections(self):
        for reply in (info(email='other@example.test'), info(email_verified='false'), info(exp='999'),
                      info(aud='other-client'), info(iss='https://evil.example'), ['not', 'a', 'dict'],
                      OSError('network down'), {'exp': 'x'}):
            with self.subTest(reply=reply):
                self.assertFalse(self.verifier(reply).verify(TOKEN))

    def test_malformed_tokens_never_reach_google(self):
        calls = []
        verifier = self.verifier(info(), calls)
        for token in (None, '', 'short', 'x' * 5000):
            self.assertFalse(verifier.verify(token))
        self.assertEqual(calls, [])

    def test_cache_reuses_verified_token_until_expiry(self):
        calls = []
        verifier = self.verifier(info(), calls)
        self.assertTrue(verifier.verify(TOKEN) and verifier.verify(TOKEN))
        self.assertEqual(len(calls), 1)
        self.assertNotIn(TOKEN, json.dumps(verifier.cache))

    def test_requires_configuration(self):
        with self.assertRaises(ValueError):
            GoogleOwnerVerifier('', OWNER)


class GoogleHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        google = GoogleOwnerVerifier(CLIENT, OWNER, fetch=lambda t: info() if t == TOKEN else info(email='x@example.test'),
                                     clock=lambda: 1000)
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(
            Controller(run_probe=lambda: {'state': 'synthetic_success'}), 'x' * 40, google, CLIENT))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def get(self, path, auth=''):
        request = urllib.request.Request(self.url + path, headers={'Authorization': auth})
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def test_public_config_exposes_only_client_id(self):
        self.assertEqual(self.get('/api/config'), (200, {'google_client_id': CLIENT}))

    def test_owner_google_token_authorizes(self):
        self.assertEqual(self.get('/api/status', 'Google ' + TOKEN)[0], 200)

    def test_other_google_account_rejected(self):
        self.assertEqual(self.get('/api/status', 'Google ' + 'eyJ' + 'b' * 60)[0], 401)

    def test_google_disabled_without_verifier(self):
        server = make_handler(Controller(), 'x' * 40)
        self.assertIsNotNone(server)  # Construction without Google keeps token-only access.


if __name__ == '__main__': unittest.main()
