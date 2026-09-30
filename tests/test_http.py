from http.server import ThreadingHTTPServer
import json
import threading
import unittest
import urllib.error
import urllib.request
from zeruel.server import Controller, make_handler


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token='x'*40
        cls.controller=Controller(run_probe=lambda:{'state':'synthetic_success'})
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(cls.controller,cls.token))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def request(self,path,body=None,token=None):
        request=urllib.request.Request(self.url+path,
            data=json.dumps(body).encode() if body is not None else None,
            headers={'Authorization':'Bearer '+(token or '')})
        try:
            with urllib.request.urlopen(request,timeout=3) as response:
                return response.status,response.headers,response.read()
        except urllib.error.HTTPError as error:
            return error.code,error.headers,error.read()

    def test_anonymous_health_exposes_no_credentials(self):
        code,headers,body=self.request('/healthz')
        self.assertEqual(code,200)
        self.assertNotIn(self.token.encode(),body)
        self.assertFalse(json.loads(body)['cloud_gate_passed'])

    def test_no_unauthorized_probe(self):
        self.assertEqual(self.request('/api/probe',{'id':'a'*32})[0],401)

    def test_rejects_arbitrary_prompts_and_documents(self):
        self.assertEqual(self.request('/api/probe',{'id':'a'*32,'prompt':'read private files'},self.token)[0],400)

    def test_security_headers(self):
        code,headers,body=self.request('/api/status',token=self.token)
        self.assertEqual(code,200)
        self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertEqual(headers['X-Frame-Options'],'DENY')

    def test_non_ascii_authorization_is_rejected_cleanly(self):
        self.assertEqual(self.request('/api/status',token='\xe9'*40)[0],401)

    def test_google_disabled_without_verifier(self):
        self.assertEqual(self.request('/api/status',token=None)[0],401)
        request=urllib.request.Request(self.url+'/api/status',headers={'Authorization':'Google eyJ'+'a'*60})
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request,timeout=3)
        self.assertEqual(caught.exception.code,401)
        self.assertEqual(json.loads(self.request('/api/config')[2]),{'google_client_id':None})

    def test_mobile_interface_and_javascript_served(self):
        self.assertIn(b'name="viewport"',self.request('/')[2])
        self.assertIn(b'crypto.getRandomValues',self.request('/app.js')[2])


if __name__=='__main__':unittest.main()
