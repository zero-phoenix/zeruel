import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from zeruel.server import Controller
import importlib.util
import inspect
import zeruel.server as server_module

_spec = importlib.util.spec_from_file_location('recover_checkpoint',
        Path(__file__).resolve().parent.parent / 'scripts' / 'recover_checkpoint.py')
recover_checkpoint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(recover_checkpoint)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.task = 'a' * 32
        self.generation = 'b' * 32
        self.gateway = Mock()
        self.gateway.call.return_value = {'claimed': True, 'generation': self.generation}
        self.probe = Mock(return_value={'state': 'synthetic_success', 'generation': 'private',
                                       'payload': 'private', 'cloud_gate_passed': True})
        self.controller = Controller(self.gateway, self.probe, self.temp.name)

    def run_work(self):
        with patch('zeruel.server.threading.Thread') as thread:
            self.assertEqual(self.controller.start(self.task)[0], 202)
        self.controller.work(self.task, self.generation)

    def test_failed_save_retries_persistence_without_model_and_survives_restart(self):
        self.gateway.call.side_effect = [{'claimed': True, 'generation': self.generation}, OSError('offline')]
        self.run_work()
        self.assertEqual(self.controller.read()['state'], 'blocked_checkpoint')
        saved = json.loads((Path(self.temp.name) / (self.task + '.json')).read_text())
        self.assertEqual(saved['report']['state'], 'synthetic_success')
        self.gateway.call.side_effect = None
        restarted = Controller(self.gateway, self.probe, self.temp.name)
        self.assertEqual(restarted.start(self.task)[0], 200)
        self.probe.assert_called_once()
        self.assertEqual(self.gateway.call.call_args.kwargs['generation'], self.generation)
        self.assertFalse(restarted.read()['cloud_gate_passed'])
        self.assertNotIn('generation', restarted.read())
        self.assertNotIn('payload', restarted.read())

    def test_restart_with_intent_without_report_is_uncertain(self):
        self.controller.journal(self.task, {'generation': self.generation, 'report': None})
        self.assertEqual(self.controller.start(self.task)[1]['state'], 'paused_uncertain')
        self.gateway.call.assert_not_called()
        self.probe.assert_not_called()

    def test_remote_active_without_local_report_never_runs(self):
        self.gateway.call.return_value = {'claimed': False, 'record': {'id': self.task, 'state': 'active',
                                                                     'generation': self.generation}}
        self.assertEqual(self.controller.start(self.task)[1]['state'], 'paused_uncertain')
        self.probe.assert_not_called()

    def test_local_journal_failure_before_model_does_not_run(self):
        with patch.object(self.controller, 'journal', side_effect=OSError('disk')):
            self.assertEqual(self.controller.start(self.task)[0], 503)
        self.assertEqual(self.controller.start(self.task)[1]['state'], 'paused_uncertain')
        self.probe.assert_not_called()

    def test_report_kept_in_memory_after_disk_failure_can_retry(self):
        self.controller.lock.acquire()
        with patch.object(self.controller, 'journal', side_effect=OSError('disk')):
            self.controller.work(self.task, self.generation)
        self.assertEqual(self.controller.start(self.task)[0], 200)
        self.probe.assert_called_once()

    def test_missing_generation_fails_closed(self):
        self.gateway.call.return_value = {'claimed': True}
        self.assertEqual(self.controller.start(self.task)[0], 503)
        self.probe.assert_not_called()

    def test_corrupt_journal_fails_closed(self):
        for contents in ['[1]', '{', '{"generation":32,"report":null}', '{"generation":"' + self.generation + '","report":[]}']:
            (Path(self.temp.name) / (self.task + '.json')).write_text(contents)
            self.assertEqual(self.controller.start(self.task)[0], 503)
        self.probe.assert_not_called()
        self.gateway.call.assert_not_called()

    def test_partial_tmp_without_journal_uses_remote_uncertain_lease(self):
        (Path(self.temp.name) / (self.task + '.tmp')).write_text('{')
        self.gateway.call.return_value = {'claimed': False, 'record': {'id': self.task, 'state': 'active'}}
        self.assertEqual(self.controller.start(self.task)[1]['state'], 'paused_uncertain')
        self.probe.assert_not_called()


class ManualRecoveryTests(unittest.TestCase):
    task, generation = 'a' * 32, 'b' * 32

    def setUp(self):
        self.gateway = Mock()
        self.gateway.call.return_value = {'ok': True, 'record': {'id': self.task, 'state': 'terminal_unknown',
                                          'generation': 'x', 'fingerprint': 'x', 'cloud_gate_passed': False}}

    def test_durable_report_is_sent_verbatim_with_owner_confirmation(self):
        report = {'state': 'synthetic_success'}
        recover_checkpoint.recover(self.gateway, self.task, {'generation': self.generation, 'report': report})
        self.gateway.call.assert_called_once_with('recover', self.task, report, generation=self.generation,
                                                  confirm='owner_worker_finished')

    def test_missing_report_requires_explicit_unknown_and_never_success(self):
        journal = {'generation': self.generation, 'report': None}
        with self.assertRaisesRegex(ValueError, '--unknown'):
            recover_checkpoint.recover(self.gateway, self.task, journal)
        self.gateway.call.assert_not_called()
        record = recover_checkpoint.recover(self.gateway, self.task, journal, unknown=True)
        self.assertIsNone(self.gateway.call.call_args.args[2])
        self.assertNotIn('generation', record)
        self.assertNotIn('fingerprint', record)

    def test_unknown_cannot_discard_durable_report(self):
        with self.assertRaises(ValueError):
            recover_checkpoint.recover(self.gateway, self.task,
                {'generation': self.generation, 'report': {'state': 'failed_runtime'}}, unknown=True)
        self.gateway.call.assert_not_called()

    def test_absent_journal_needs_valid_private_generation(self):
        for generation in (None, '', 'z' * 32):
            with self.assertRaises(ValueError):
                recover_checkpoint.recover(self.gateway, self.task, None, generation, unknown=True)
        self.gateway.call.assert_not_called()
        recover_checkpoint.recover(self.gateway, self.task, None, self.generation, unknown=True)
        self.assertEqual(self.gateway.call.call_args.kwargs['generation'], self.generation)

    def test_corrupt_journal_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            for contents in ['{', '[]', '{"generation":"short","report":null}']:
                (Path(folder) / (self.task + '.json')).write_text(contents)
                with self.assertRaises(ValueError):
                    recover_checkpoint.load_journal(folder, self.task)
            self.assertIsNone(recover_checkpoint.load_journal(folder, 'c' * 32))

    def test_recovery_never_invokes_model(self):
        probe = Mock()
        controller = Controller(self.gateway, probe, tempfile.mkdtemp())
        recover_checkpoint.recover(self.gateway, self.task, None, self.generation, unknown=True)
        probe.assert_not_called()
        self.assertFalse(controller.lock.locked())

    def test_server_never_calls_recovery(self):
        # Recovery is a manual owner command only; no HTTP route or controller path reaches it.
        self.assertNotIn("'recover'", inspect.getsource(server_module))
        self.assertNotIn('"recover"', inspect.getsource(server_module))

