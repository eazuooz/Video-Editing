"""Pure CPU safety fixtures; no live resource query/browser/Unity/model/job.

Snapshots are synthetic guard inputs. Their successful classification is never
saved as actual resource or native production evidence.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prospect_resource_cpu_fixture', HERE/'prospect-refuge-resource-qualification.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


def fixture():
    before = dict(monotonic=100.0, rows=[], processParents={}, errors=[], controllers={},
                  headlessPids=list(q.PROFILES)+list(q.GPU_PIDS.values()), sameProfilePids=list(q.EXPECTED),
                  gpuCounters={str(pid): [0, 0] for pid in q.GPU_PIDS.values()})
    for pid, (ppid, created, signature) in q.EXPECTED.items():
        before['rows'].append(dict(pid=pid, ppid=ppid, created=created, cmdSHA256=signature, name='msedge.exe',
                                   exe=q.EDGE_EXE, cpuSeconds=1.0, readBytes=10, writeBytes=20, tcp=[]))
        before['processParents'][str(pid)] = ppid
    before['controllers'] = {str(pid): 'absent' for pid in q.CONTROLLERS.values()}
    after = copy.deepcopy(before)
    after['monotonic'] = 103.0
    return before, after


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.a, self.b = fixture()

    def row(self, pid=24696, snapshot=None):
        return next(r for r in (snapshot or self.b)['rows'] if r['pid'] == pid)

    def declined(self, text=None, before_reason=None, after_reason=None):
        result = q.evaluate_pair(self.a, self.b, before_reason, after_reason)
        self.assertFalse(result['qualified'])
        self.assertEqual(result['qualifiedPids'], [])
        if text:
            self.assertIn(text, result['reason'])

    def remove_tree(self, root):
        members = q.expected_tree(root)
        for snapshot in (self.a, self.b):
            snapshot['rows'] = [r for r in snapshot['rows'] if r['pid'] not in members]
            snapshot['processParents'] = {pid: pp for pid, pp in snapshot['processParents'].items() if int(pid) not in members}
            snapshot['headlessPids'] = [pid for pid in snapshot['headlessPids'] if pid not in members]
            snapshot['sameProfilePids'] = [pid for pid in snapshot['sameProfilePids'] if pid not in members]
            snapshot['gpuCounters'].pop(str(q.GPU_PIDS[root]), None)

    def test_exact_two_idle_trees_positive(self):
        result = q.evaluate_pair(self.a, self.b)
        self.assertTrue(result['qualified'])
        self.assertEqual(set(result['qualifiedPids']), set(q.EXPECTED))
        self.assertFalse(result['ownershipVerified'])
        self.assertFalse(result['processTerminationAuthorized'])

    def test_missing_dead_root_and_whole_tree_okay(self):
        self.remove_tree(24696)
        self.assertEqual(set(q.evaluate_pair(self.a, self.b)['qualifiedPids']), q.expected_tree(66848))
        self.remove_tree(66848)
        self.assertTrue(q.evaluate_pair(self.a, self.b)['qualified'])

    def test_missing_root_but_children_preserved_and_blocked(self):
        self.b['rows'] = [r for r in self.b['rows'] if r['pid'] != 24696]
        self.declined('descendant')

    def test_root_pid_reused(self):
        self.row()['created'] += 100
        self.declined('signature')

    def test_child_pid_reused(self):
        self.row(79116)['created'] += 100
        self.declined('signature')

    def test_exact_argv_signature_change_blocks(self):
        self.row()['cmdSHA256'] = '0'*64
        self.declined('signature')

    def test_executable_change_blocks(self):
        self.row()['exe'] = 'c:/other/msedge.exe'
        self.declined('signature')

    def test_parent_change_blocks(self):
        self.row(79116)['ppid'] = 42
        self.declined('signature')

    def test_new_child_even_nonheadless_blocks(self):
        self.b['processParents']['99999'] = 24696
        self.declined('New/unregistered')

    def test_missing_child_blocks(self):
        self.b['rows'] = [r for r in self.b['rows'] if r['pid'] != 18612]
        self.declined('eight-process')

    def test_present_reused_or_unreadable_controller_blocks(self):
        for value in ('present-or-reused', 'unknown', None):
            with self.subTest(value=value):
                self.b['controllers']['17188'] = value
                self.declined('controller')

    def test_cpu_read_or_write_activity_blocks(self):
        for key in ('cpuSeconds', 'readBytes', 'writeBytes'):
            with self.subTest(key=key):
                self.a, self.b = fixture()
                self.row(18612)[key] += .001
                self.declined('became active')

    def test_unknown_new_headless_and_profile_share_block(self):
        for field in ('headlessPids', 'sameProfilePids'):
            with self.subTest(field=field):
                self.a, self.b = fixture()
                self.b[field].append(99999)
                self.declined()

    def test_unknown_browser_metadata_blocks(self):
        self.b['errors'].append('Unreadable browser argv PID99999')
        self.declined('unreadable')

    def test_unknown_tcp_enum_with_any_nonzero_peer_blocks(self):
        for remote in (['127.0.0.1', 50000], ['0.0.0.0', 1], ['203.0.113.1', 0]):
            with self.subTest(remote=remote):
                self.row()['tcp'] = [dict(status='NONE', remote=remote)]
                self.declined('TCP peer')

    def test_zero_peer_unknown_enum_remains_explicitly_allowed(self):
        self.row()['tcp'] = [dict(status='NONE', local=['127.0.0.1', 57599], remote=[])]
        self.assertTrue(q.evaluate_pair(self.a, self.b)['qualified'])

    def test_unreadable_tcp_and_inconsistent_established_block(self):
        self.row()['tcp'] = None
        self.declined('TCP metadata')
        self.row()['tcp'] = [dict(status='ESTABLISHED', remote=[])]
        self.declined('TCP peer')

    def test_unavailable_or_nonzero_or_nonfinite_gpu_blocks(self):
        for value in (None, [], [.1], [float('nan')], ['0']):
            with self.subTest(value=value):
                self.b['gpuCounters']['79116'] = value
                self.declined('GPU counters')

    def test_global_gpu_guard_before_and_after_must_be_clear(self):
        self.declined('insufficient', before_reason='GPU headroom insufficient')
        self.declined('lease', after_reason='Another scoped job holds GPU lease')

    def test_interval_too_short_or_unbounded_blocks(self):
        for duration in (0, 1.99, 31.0, float('nan')):
            with self.subTest(duration=duration):
                self.b['monotonic'] = self.a['monotonic'] + duration
                self.declined('interval')

    def test_counter_query_warmup_longer_zero_activity_interval_allowed(self):
        self.b['monotonic'] = self.a['monotonic'] + 9.11
        result = q.evaluate_pair(self.a, self.b)
        self.assertTrue(result['qualified'])
        self.assertAlmostEqual(result['sampleIntervalSeconds'], 9.11)
        # Warmup allowance never substitutes for the original idle conditions.
        self.row(18612)['cpuSeconds'] += .001
        self.declined('became active')

    def test_only_fixed_audited_roots_can_be_qualified(self):
        self.assertEqual(set(q.PROFILES), {24696, 66848})
        self.assertEqual(len(q.EXPECTED), 16)
        self.assertEqual([len(q.expected_tree(root)) for root in q.PROFILES], [8, 8])
        # Independent exact stored OS argv proof, not a live browser query.
        data = json.loads(q.SAMPLES.read_text(encoding='utf-8'))
        rows = {r['pid']: r for r in data['samples'][-1]['selectedProcesses'] if r.get('name') == 'msedge.exe'}
        self.assertEqual(q.sha(q.SAMPLES), q.SAMPLES_SHA)
        for pid, (ppid, created, signature) in q.EXPECTED.items():
            self.assertEqual(rows[pid]['ppid'], ppid)
            self.assertEqual(rows[pid]['created'], created)
            self.assertEqual(q.argv_sha(rows[pid]['cmd']), signature)

    def test_qualified_receipt_preserves_no_mutation_and_base_guard_rechecked(self):
        with tempfile.TemporaryDirectory(prefix='yamyam-resource-cpu-') as name:
            base = Path(name)
            audit, samples = base/'audit', base/'samples'
            audit.write_bytes(b'synthetic audit'); samples.write_bytes(b'synthetic samples')
            with patch.object(q, 'BASE', base), patch.object(q, 'AUDIT', audit), patch.object(q, 'SAMPLES', samples), \
                 patch.object(q, 'AUDIT_SHA', q.sha(audit)), patch.object(q, 'SAMPLES_SHA', q.sha(samples)), \
                 patch.object(q, 'snapshot', side_effect=[self.a, self.b]), patch.object(q.time, 'sleep'), \
                 patch.object(q.subprocess, 'run', side_effect=AssertionError('No real OS/GPU query in fixture')):
                guard_calls = []
                result = q.qualify(lambda: guard_calls.append(True))
            self.assertTrue(result['qualified'])
            self.assertEqual(guard_calls, [True, True])
            receipt = json.loads(Path(result['evidence']['path']).read_text(encoding='utf-8'))
            self.assertFalse(receipt['processMutationPerformed'])
            self.assertFalse(receipt['browserAccessPerformed'])
            self.assertEqual(audit.read_bytes(), b'synthetic audit')

    def test_changed_pinned_audit_never_samples_or_qualifies(self):
        with tempfile.TemporaryDirectory(prefix='yamyam-resource-pin-cpu-') as name:
            base = Path(name); bad = base/'audit'; bad.write_bytes(b'changed')
            with patch.object(q, 'BASE', base), patch.object(q, 'AUDIT', bad), \
                 patch.object(q, 'snapshot', side_effect=AssertionError('Changed proof must stop before sampling')):
                result = q.qualify(lambda: None)
            self.assertFalse(result['qualified'])
            self.assertIn('evidence changed', result['reason'])

    def test_runner_identity_pins_qualifier_and_keeps_base_guard(self):
        source = (HERE/'run-prospect-refuge-native.py').read_text(encoding='utf-8')
        authorize = source.split('def authorize(', 1)[1].split('def export_paths(', 1)[0]
        self.assertIn("HERE/'prospect-refuge-resource-qualification.py'", authorize)
        busy = source.split('def busy_reason(', 1)[1].split('def meta_guid(', 1)[0]
        self.assertIn('reason=runtime.busy_reason(own_token)', busy)
        self.assertIn('qualification.qualify(lambda:runtime.busy_reason(own_token))', busy)
        self.assertIn("if not result['qualified']", busy)


if __name__ == '__main__':
    unittest.main(verbosity=2)
