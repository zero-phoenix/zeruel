import time
import json
import unittest
import unittest.mock
from unittest.mock import patch
from zeruel.checkpoint import Checkpoint, PrivateCheckpoint


class PrivateCheckpointTests(unittest.TestCase):
    def gateway(self):
        return PrivateCheckpoint('A'*30, 'synthetic-secret-'*3,
                {'client_id':'client','client_secret':'fixture','refresh_token':'fixture-refresh'})

    def test_public_transport_disabled(self):
        with self.assertRaises(ValueError):
            Checkpoint('https://script.google.com/a/exec','x'*32).call('get','a'*32)

    def test_refresh_cached_and_private_function_fixed(self):
        gateway=self.gateway()
        with patch.object(gateway,'request_json',side_effect=[
            {'access_token':'fixture-access','token_type':'Bearer','expires_in':3600},
            {'response':{'result':{'ok':True,'record':None}}},
            {'response':{'result':{'ok':True,'record':None}}}]) as request:
            gateway.call('get','a'*32);gateway.call('get','a'*32)
            self.assertEqual(request.call_count,3)
            args=request.call_args_list[1].args
            self.assertTrue(args[0].startswith('https://script.googleapis.com/v1/scripts/'))
            body=json.loads(args[1]);self.assertEqual(body['function'],'runCheckpoint')
            self.assertFalse(body['devMode'])
            self.assertEqual(args[2]['Authorization'],'Bearer fixture-access')

    def test_permission_error_fails_closed(self):
        gateway=self.gateway()
        with patch.object(gateway,'token',return_value='fixture-access'), patch.object(
                gateway,'request_json',return_value={'error':{'message':'sensitive diagnostic'}}):
            with self.assertRaisesRegex(ValueError,'^Private checkpoint rejected$'):
                gateway.call('claim','a'*32)

    def test_expiring_token_is_refreshed(self):
        gateway=self.gateway();gateway.access_token='old';gateway.expires_at=0
        with patch.object(gateway,'request_json',return_value={
                'access_token':'new','token_type':'Bearer','expires_in':3600}) as request:
            self.assertEqual(gateway.token(),'new');request.assert_called_once()

    def test_token_renews_only_inside_360_second_margin(self):
        gateway=self.gateway();gateway.access_token='old'
        with patch.object(gateway,'request_json',return_value={
                'access_token':'new','token_type':'Bearer','expires_in':3600}) as request:
            gateway.expires_at=time.time()+400
            self.assertEqual(gateway.token(),'old');request.assert_not_called()
            gateway.expires_at=time.time()+300
            self.assertEqual(gateway.token(),'new');request.assert_called_once()

    def test_refresh_between_claim_and_complete_keeps_generation(self):
        gateway=self.gateway()
        with patch.object(gateway,'request_json',side_effect=[
            {'access_token':'first','token_type':'Bearer','expires_in':3600},
            {'response':{'result':{'ok':True,'claimed':True,'generation':'b'*32}}},
            {'access_token':'second','token_type':'Bearer','expires_in':3600},
            {'response':{'result':{'ok':True,'record':None}}}]) as request:
            gateway.call('claim','a'*32);gateway.expires_at=0
            gateway.call('complete','a'*32,{'state':'failed_runtime'},generation='b'*32)
            last=request.call_args_list[3].args
            self.assertEqual(last[2]['Authorization'],'Bearer second')
            envelope=json.loads(json.loads(last[1])['parameters'][0]['payload'])
            self.assertEqual(envelope['generation'],'b'*32)
            self.assertNotIn('confirm',envelope)

    def test_revoked_refresh_token_fails_closed_without_secrets(self):
        gateway=self.gateway()
        with patch.object(gateway,'request_json',return_value={'error':'invalid_grant'}):
            with self.assertRaises(ValueError) as caught:
                gateway.call('get','a'*32)
        for secret in ('fixture','fixture-refresh','synthetic-secret-'):
            self.assertNotIn(secret,str(caught.exception))
        self.assertIsNone(gateway.access_token)

    def test_non_object_json_reply_fails_closed_as_value_error(self):
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self, n): return b'[1]'
        opener = unittest.mock.Mock(); opener.open.return_value = Reply()
        with patch('urllib.request.build_opener', return_value=opener):
            with self.assertRaisesRegex(ValueError, '^Unexpected checkpoint reply$'):
                PrivateCheckpoint.request_json('https://script.googleapis.com/x', b'{}', {})
