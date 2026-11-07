"""Bounded wrapper tests + unchanged selected-voice synthetic PCM fixtures."""
from __future__ import annotations
import argparse,importlib.util,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
w=module('solution_voice_worker_v4_under_test',HERE/'run-solution-path-voice-v4.py')
BASE_TEST_SHA='685d8c95abfd5a12bc0bd47630929265b18b829539923ecd665a4a920ae6fd59'
if w.sha(HERE/'verify-selected-voice-worker.py')!=BASE_TEST_SHA:raise RuntimeError('Reviewed synthetic base fixtures changed')
old=module('solution_voice_unchanged_pcm_fixtures',HERE/'verify-selected-voice-worker.py')
def args():return argparse.Namespace(topic='11.05',native_evidence=None,native_qa=None,narration=None,semantic_components=None,wait_hours=.01)
class Adapter(unittest.TestCase):
 def test_common_pcm_recovery_launch_functions_are_original(self):
  for name,original in w.COMMON_FUNCTIONS.items():self.assertIs(getattr(w.base,name),original)
 def test_rejects_other_topic_before_preparation(self):
  a=args();a.topic='07.04'
  with patch.object(w.prep,'prepare',side_effect=AssertionError('not scoped')):
   self.assertRaises(ValueError,w.configure,a.topic);self.assertRaises(ValueError,w.prepared,a)
 def test_current_readonly_preflight_never_queries_or_queues(self):
  with patch.object(w.base,'busy_reason',side_effect=AssertionError('no GPU query')),patch.object(w.base,'execute',side_effect=AssertionError('no queue')),patch.object(w,'invocation',side_effect=AssertionError('no snapshot')),patch.object(w.prep.core,'validate_profile',side_effect=AssertionError('no weights')),patch('sys.stdout',new_callable=io.StringIO)as out:
   w.main([]);self.assertFalse(json.loads(out.getvalue())['ready']);self.assertFalse(json.loads(out.getvalue())['resourceChecked'])
 def test_unready_execute_request_does_not_queue(self):
  with patch.object(w,'prepared',side_effect=w.prep.Pending('current provisional')),patch.object(w.base,'execute')as execute,patch.object(w,'invocation')as invocation,patch('sys.stdout',new_callable=io.StringIO)as out:
   w.main(['--execute']);execute.assert_not_called();invocation.assert_not_called();self.assertFalse(json.loads(out.getvalue())['jobLaunched'])
 def test_fresh_source_pin_rejects_change_before_preparer(self):
  actual=w.sha
  with patch.object(w,'sha',side_effect=lambda p:'0'*64 if Path(p).name=='run-solution-path-native-v4.py'else actual(p)),patch.object(w.prep,'prepare')as prepared:
   self.assertRaisesRegex(RuntimeError,'Reviewed voice source changed',w.prepared,args());prepared.assert_not_called()
 def test_resource_gate_keeps_native_decline_and_strict_voice15percent(self):
  with patch.object(w.resource,'busy_reason',return_value='foreign lease preserved'),patch.object(w.base.subprocess,'check_output')as gpu:
   self.assertEqual(w.base.busy_reason(),'foreign lease preserved');gpu.assert_not_called()
  with patch.object(w.resource,'busy_reason',return_value=None):
   for sample,blocked in[('9000,14',False),('9000,15',True),('8191,0',True)]:
    with patch.object(w.base.subprocess,'check_output',return_value=sample):self.assertEqual(w.base.busy_reason()is not None,blocked)
 def test_native_resource_hook_never_acquires_or_recovers_lease(self):
  with patch.object(w.resource,'busy_reason',return_value='busy'),patch.object(w.resource.rt,'recover_own_lease',side_effect=AssertionError('no recovery'))as recover,patch.object(w.resource.rt.SingleWorker,'acquire',side_effect=AssertionError('no native worker'))as acquire:
   self.assertEqual(w.audited_native_busy(),'busy');recover.assert_not_called();acquire.assert_not_called()
 def test_immutable_invocation_and_other_identity_completion(self):
  with tempfile.TemporaryDirectory()as tmp,patch.object(w,'BASE',Path(tmp)),patch.object(w.base,'identity',return_value=dict(pid=123,createTime=1,argv=['python',str(Path(w.__file__).resolve())],commandSHA256='fixture')):
   prov=dict(ready=True,voiceReady=True,fingerprint='a'*64,preparationFingerprint='b'*64,identity=dict(scenes=[]),inputs=[]);path=w.invocation(prov,args());record=w.base.read(path)
   for row in record['sources']:self.assertEqual(w.sha(row['snapshot']['path']),row['source']['sha256'])
   ctx=dict(owner='fixture',state=Path(tmp)/'state.json',evidence=Path(tmp)/'evidence.json',worker=Path(tmp)/'worker.json');w.base.immutable_json(ctx['state'],dict(protocol=w.base.PROTOCOL,owner='fixture',fingerprint=prov['fingerprint'],pid=999,createTime=2,argv=record['wrapperProcess']['argv'],commandSHA256='fixture',completed=True,status='old-complete'))
   w.completion_observation(path,ctx,RuntimeError('different source'));observed=w.base.read(path.parent/'completion-observation.json');self.assertFalse(observed['currentStateMatchesInvocation']);self.assertFalse(observed['completedObserved']);self.assertFalse(observed['humanApproval'])
def load_tests(loader,tests,pattern):
 suite=loader.loadTestsFromTestCase(Adapter)
 for name in['test_variable_scene_raw_concatenation_preserves_engine_and_all_samples','test_same_voice_metadata_change_reuses_complete_output_without_stage_or_model','test_live_worker_record_is_preserved','test_orphan_completed_outputs_recover_cpu_only_with_exact_request_pins','test_tampered_completed_pcm_is_not_silently_reused']:suite.addTest(old.SelectedWorker(name))
 return suite
if __name__=='__main__':unittest.main(verbosity=2)
