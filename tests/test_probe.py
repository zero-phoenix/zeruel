import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
import unittest.mock
from unittest.mock import patch
from zeruel.probe import EXPECTED, TOKEN, Blocked, child_environment, probe
from zeruel.server import Controller


def success(**extra):
    return json.dumps({'status': 'SUCCESS', 'response': json.dumps(EXPECTED) + chr(10), **extra})


class Reply:
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, n): return self.data


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)/'home'
        self.home.mkdir()
        self.binary = Path(self.temp.name)/'agy'
        self.binary.write_text('synthetic fixture')
        self.env = {'ZERUEL_PRIVATE_HOME':str(self.home),'ZERUEL_AGY_BIN':str(self.binary)}

    def credentials(self):
        (self.home/TOKEN).parent.mkdir(parents=True, exist_ok=True)
        (self.home/TOKEN).write_text('fixture-session')

    def test_requires_auth_without_invoking_cli(self):
        def fail(*args): self.fail('Must not invoke CLI before authentication')
        self.assertEqual(probe(self.env,fail)['state'],'blocked_auth')

    def test_missing_binary_blocks(self):
        self.credentials()
        self.assertEqual(probe({**self.env,'ZERUEL_AGY_BIN':str(self.home/'none')})['state'],'blocked_cli_missing')

    def test_all_paid_auth_routes_blocked(self):
        for name in ('GEMINI_API_KEY','GOOGLE_API_KEY','GOOGLE_APPLICATION_CREDENTIALS',
                     'GOOGLE_GENAI_USE_VERTEXAI','CLOUD_SHELL'):
            env = {**self.env,name:'secret'}
            self.assertEqual(probe(env)['state'],'blocked_paid_auth')

    def test_command_is_fixed_sandboxed_and_schema_bound(self):
        self.credentials()
        def run(command,env,cwd,timeout):
            self.assertNotIn('ZERUEL_ACCESS_TOKEN',env)
            self.assertEqual(env['HOME'],str(self.home))
            for flag in ('--sandbox','--disable-slash-commands','--print-timeout'):
                self.assertIn(flag,command)
            self.assertNotIn('--dangerously-skip-permissions',command)
            self.assertEqual(command[command.index('--model')+1],'gemini-3.8-flash-high')
            self.assertEqual(timeout,150)
            return 0,success(),''
        report=probe(self.env,run)
        self.assertEqual(report['state'],'synthetic_success')
        self.assertEqual(report['engine'],'antigravity-cli')
        self.assertFalse(report['subscription_verified'])
        self.assertFalse(report['cloud_gate_passed'])

    def test_quota_is_paused_and_errors_do_not_leak(self):
        self.credentials()
        report=probe(self.env,lambda *args:(1,'','429 secret-token-that-must-not-leak'))
        self.assertEqual(report['state'],'paused_quota')
        self.assertNotIn('secret-token',json.dumps(report))

    def test_error_envelopes_classified(self):
        self.credentials()
        cases=[(json.dumps({'status':'ERROR','error':'authentication failed or timed out'}),'blocked_auth'),
               (json.dumps({'status':'ERROR','error':'RESOURCE_EXHAUSTED'}),'paused_quota'),
               (json.dumps({'status':'ERROR','error':'boom'}),'failed_cli')]
        for out,state in cases:
            self.assertEqual(probe(self.env,lambda *a,o=out:(1,o,''))['state'],state)

    def test_incorrect_or_unstructured_output_rejected(self):
        self.credentials()
        for value in ('hello','[]',json.dumps({'status':'SUCCESS','response':'{"marker":"ZERUEL_OK","sum":41}'}),
                      json.dumps({'status':'SUCCESS','response':'Sure! {"marker":"ZERUEL_OK","sum":42}'}),
                      json.dumps({'status':'SUCCESS','response':''}),
                      json.dumps({'status':'FAILED','response':json.dumps(EXPECTED)})[:0] or 'null'):
            self.assertEqual(probe(self.env,lambda *args,v=value:(0,v,''))['state'],'failed_response')

    def test_contract_is_literal_zeruel_ok_42(self):
        # Literales, no EXPECTED: una prueba que deriva el éxito de la constante no puede refutarla.
        self.credentials()
        ok = json.dumps({'status': 'SUCCESS', 'response': '{"marker":"ZERUEL_OK","sum":42}'})
        bad = json.dumps({'status': 'SUCCESS', 'response': '{"marker":"ZERUEL_OK","sum":43}'})
        self.assertEqual(probe(self.env, lambda *a: (0, ok, ''))['state'], 'synthetic_success')
        self.assertEqual(probe(self.env, lambda *a: (0, bad, ''))['state'], 'failed_response')

    def test_timeout_does_not_retry(self):
        self.credentials()
        def run(*args): raise Blocked('paused_timeout')
        self.assertEqual(probe(self.env,run)['state'],'paused_timeout')

    def test_child_environment_strips_secrets(self):
        child=child_environment({'PATH':'bin','ZERUEL_ACCESS_TOKEN':'secret','GITHUB_TOKEN':'secret',
                                 'ZERUEL_CHECKPOINT_SECRET':'secret','GEMINI_API_KEY':'secret',
                                 'ZERUEL_GEMINI_FREE_KEY':'secret','ZERUEL_AGY_OAUTH_TOKEN':'secret'},self.home)
        self.assertNotIn('secret',json.dumps(child))
        self.assertEqual(child['PATH'],'bin')

    def test_free_tier_only_after_quota_and_never_leaks_key(self):
        self.credentials()
        env={**self.env,'ZERUEL_GEMINI_FREE_KEY':'free-key-fixture'}
        seen=[]
        def opener(request,timeout):
            seen.append(request)
            text=json.dumps(EXPECTED)
            return Reply(json.dumps({'candidates':[{'content':{'parts':[{'text':text}]}}]}).encode())
        report=probe(env,lambda *a:(0,success(),''),opener)
        self.assertEqual((report['engine'],len(seen)),('antigravity-cli',0))
        report=probe(env,lambda *a:(1,'','429'),opener)
        self.assertEqual(report['state'],'synthetic_success')
        self.assertEqual((report['engine'],report['primary_state']),('gemini-api-free-tier','paused_quota'))
        self.assertEqual(seen[0].get_header('X-goog-api-key'),'free-key-fixture')
        self.assertTrue(seen[0].full_url.startswith('https://generativelanguage.googleapis.com/'))
        self.assertIn('gemini-flash-latest',seen[0].full_url)
        self.assertNotIn('free-key',seen[0].full_url)
        self.assertNotIn('free-key',json.dumps(report))

    def test_free_tier_failures_fail_closed(self):
        self.credentials()
        env={**self.env,'ZERUEL_GEMINI_FREE_KEY':'k'}
        def quota(request,timeout): raise OSError('HTTP Error 429')
        self.assertEqual(probe(env,lambda *a:(1,'','429'),quota)['state'],'paused_quota')
        wrong=lambda r,t:Reply(json.dumps({'candidates':[{'content':{'parts':[{'text':'{"sum":41}'}]}}]}).encode())
        self.assertEqual(probe(env,lambda *a:(1,'','429'),wrong)['state'],'failed_response')
        self.assertEqual(probe(env,lambda *a:(1,'','authentication required'),wrong)['state'],'blocked_auth')

    def test_print_timeout_partial_output_is_paused(self):
        self.credentials()
        partial=json.dumps({'status':'SUCCESS','response':''})
        err='[agy] print timeout after 1m50s with turn in progress; returning partial output'
        self.assertEqual(probe(self.env,lambda *a:(0,partial,err))['state'],'paused_timeout')
        self.assertEqual(probe(self.env,lambda *a:(0,success(),err))['state'],'paused_timeout')

    def test_denied_tool_actions_fail_closed(self):
        self.credentials()
        out=success(denied_actions=[{'action':'command','display_name':'RunCommand'}])
        self.assertEqual(probe(self.env,lambda *a:(0,out,''))['state'],'failed_response')

    def test_free_quota_403_and_network_timeout(self):
        self.credentials()
        env={**self.env,'ZERUEL_GEMINI_FREE_KEY':'k'}
        def forbidden(r,timeout): raise OSError('HTTP Error 403: quotaExceeded')
        self.assertEqual(probe(env,lambda *a:(1,'','429'),forbidden)['state'],'paused_quota')
        self.assertEqual(probe(self.env,lambda *a:(1,'','dial tcp: i/o timed out'))['state'],'failed_cli')

    def test_free_tier_refuses_redirects(self):
        from zeruel.probe import NoRedirect
        self.assertIsNone(NoRedirect().redirect_request(None,None,302,'','','https://evil.example'))

    def test_empty_binary_variable_uses_default(self):
        from zeruel import probe as module
        self.assertEqual(module.probe({**self.env,'ZERUEL_AGY_BIN':''},
                         lambda *a:self.fail('no binary'))['state'],'blocked_cli_missing')


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

    def test_second_run_within_30_seconds_is_paused_cooldown(self):
        c=Controller(run_probe=lambda:{'state':'synthetic_success'})
        with patch.dict(os.environ,{},clear=True):
            self.assertEqual(c.start('a'*32)[0],202)
            self.assertTrue(c.lock.acquire(timeout=2));c.lock.release()
            code,body=c.start('b'*32)
            self.assertEqual((code,body['state']),(429,'paused_cooldown'))
            c.last_run-=31
            self.assertEqual(c.start('c'*32)[0],202)
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
