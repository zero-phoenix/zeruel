import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
import unittest.mock
from unittest.mock import patch
from zeruel.probe import EXPECTED, Blocked, child_environment, probe
from zeruel.server import Controller


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)/'home'
        (self.home/'.gemini').mkdir(parents=True)
        self.bundle = Path(self.temp.name)/'cli.js'
        self.bundle.write_text('synthetic fixture')
        self.env = {'ZERUEL_PRIVATE_HOME':str(self.home),'ZERUEL_CLI_BUNDLE':str(self.bundle)}

    def credentials(self):
        (self.home/'.gemini'/'oauth_creds.json').write_text('{}')

    def test_requires_auth_without_invoking_cli(self):
        def fail(*args): self.fail('Must not invoke CLI before authentication')
        self.assertEqual(probe(self.env,fail)['state'],'blocked_auth')

    def test_all_paid_auth_routes_blocked(self):
        for name in ('GEMINI_API_KEY','GOOGLE_API_KEY','GOOGLE_APPLICATION_CREDENTIALS',
                     'GOOGLE_GENAI_USE_VERTEXAI','CLOUD_SHELL'):
            env = {**self.env,name:'secret'}
            self.assertEqual(probe(env)['state'],'blocked_paid_auth')

    def test_success_is_not_entitlement_or_cloud_proof(self):
        self.credentials()
        def run(command,env,cwd,timeout):
            self.assertNotIn('ZERUEL_ACCESS_TOKEN',env)
            self.assertNotIn('secret',str(command))
            self.assertEqual(timeout,120)
            return 0,json.dumps({'response':json.dumps(EXPECTED)}),''
        report=probe(self.env,run)
        self.assertEqual(report['state'],'synthetic_success')
        self.assertFalse(report['subscription_verified'])
        self.assertFalse(report['cloud_gate_passed'])

    def test_quota_is_paused_and_errors_do_not_leak(self):
        self.credentials()
        report=probe(self.env,lambda *args:(1,'','429 secret-token-that-must-not-leak'))
        self.assertEqual(report['state'],'paused_quota')
        self.assertNotIn('secret-token',json.dumps(report))

    def test_envelope_error_is_rejected(self):
        self.credentials()
        report=probe(self.env,lambda *args:(0,json.dumps({'error':{'message':'invalid_grant'}}),''))
        self.assertEqual(report['state'],'blocked_auth')

    def test_incorrect_or_unstructured_output_rejected(self):
        self.credentials()
        for value in ('hello',json.dumps({'response':'{"sum":41}'}), '[]'):
            self.assertEqual(probe(self.env,lambda *args:(0,value,''))['state'],'failed_response')

    def test_timeout_does_not_retry(self):
        self.credentials()
        def run(*args): raise Blocked('paused_timeout')
        self.assertEqual(probe(self.env,run)['state'],'paused_timeout')

    def test_child_environment_strips_secrets(self):
        child=child_environment({'PATH':'bin','ZERUEL_ACCESS_TOKEN':'secret','GITHUB_TOKEN':'secret',
                                 'ZERUEL_CHECKPOINT_SECRET':'secret','GEMINI_API_KEY':'secret'},self.home)
        self.assertNotIn('secret',json.dumps(child))
        self.assertEqual(child['PATH'],'bin')


class ControllerTests(unittest.TestCase):
    def test_single_execution_and_lock_release(self):
        entered,finish=threading.Event(),threading.Event()
        def run():
            entered.set();finish.wait(3)
            return {'state':'synthetic_success'}
        c=Controller(run_probe=run)
        with patch.dict(os.environ,{},clear=True):
            self.assertEqual(c.start('a'*32)[0],202)
            self.assertTrue(entered.wait(1))
            self.assertEqual(c.start('b'*32)[0],409)
            finish.set()
            self.assertTrue(c.lock.acquire(timeout=2));c.lock.release()

    def test_cloud_without_persistence_never_invokes_model(self):
        c=Controller(run_probe=lambda:self.fail('no model call'))
        with patch.dict(os.environ,{'RENDER':'true'}):
            self.assertEqual(c.start('a'*32)[1]['state'],'blocked_persistence')
            self.assertTrue(c.lock.acquire(False));c.lock.release()

    def test_completed_checkpoint_does_not_run_again(self):
        class Gateway:
            def call(self,*args):return {'claimed':False,'record':{'id':'a'*32,'state':'synthetic_success'}}
        c=Controller(Gateway(),lambda:self.fail('duplicate execution'))
        self.assertEqual(c.start('a'*32)[0],200)
        self.assertTrue(c.lock.acquire(False));c.lock.release()

    def test_other_active_checkpoint_releases_local_lock(self):
        class Gateway:
            def call(self,*args):return {'claimed':False,'record':{'id':'a'*32,'state':'active'}}
        c=Controller(Gateway())
        self.assertEqual(c.start('a'*32)[0],200)
        self.assertTrue(c.lock.acquire(False));c.lock.release()

    def test_invalid_id(self):
        self.assertEqual(Controller().start('../secrets')[0],400)


if __name__=='__main__':unittest.main()


class ProbeHardeningTests(unittest.TestCase):
    def test_empty_private_home_never_resolves_to_cwd(self):
        from zeruel import probe as module
        with unittest.mock.patch.dict(module.os.environ, {'ZERUEL_PRIVATE_HOME': ''}):
            self.assertNotEqual(module.home_path(), module.Path.cwd())
            self.assertTrue(str(module.home_path()).endswith('gemini-home'))

    def test_child_cpu_is_reported_per_run(self):
        from zeruel import probe as module
        with unittest.mock.patch.object(module, 'children_usage', side_effect=[(100, 50.0), (120, 52.5)]):
            report = module.probe({'ZERUEL_PRIVATE_HOME': tempfile.mkdtemp()})
        self.assertEqual(report['children_cpu_seconds'], 2.5)
        self.assertEqual(report['children_peak_rss_kib'], 120)
