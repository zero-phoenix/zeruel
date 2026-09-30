import json
import unittest
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
