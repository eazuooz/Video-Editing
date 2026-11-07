"""Pure synthetic guard/provenance fixtures; no actual prepare/resources/media."""
import copy,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('atlas_source_tests',HERE/'run-solution-path-structure-atlas-v1.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class Atlas(unittest.TestCase):
 def manifest_fixture(self,root):
  attempt=root/'attempts/synthetic';attempt.mkdir(parents=True);stage=attempt/'staged';stage.mkdir()
  inputs=[];sources=[];staged=[]
  for i,name in enumerate(a.SOURCE_NAMES):
   source=root/name;source.write_text('synthetic source '+str(i),encoding='utf8');snapshot=stage/name;snapshot.write_bytes(source.read_bytes())
   inputs.append(a.pin(source));sources.append(dict(path=str(source),name=name));staged.append(dict(name=name,**a.pin(snapshot)))
  font=root/'font.ttf';font.write_bytes(b'syntheticfont');(stage/'NotoSansKR-VF.ttf').write_bytes(font.read_bytes())
  packets=[dict(fingerprint=str(i+1)*64,mode='construction',nativeFrame=i)for i in range(2)]
  recipe=dict(fingerprint='c'*64,picturePlanFingerprint='d'*64,packets=packets,aliases=[])
  prov=dict(ready=True,topicId='11.05',sourceJob=dict(path='synthetic/source-job.json',sha256='e'*64),recipe=recipe,
   producer=dict(synthetic=True),inputPins=inputs,stagedSources=sources,font=a.pin(font),fingerprint='f'*64)
  parent=dict(pid=123,createTime=10.,argv=['synthetic-python','synthetic-atlas']);parent['commandSHA256']=a.digest(parent['argv'])
  job=dict(prov,schemaVersion='11.05-structure-atlas-execution-job-v1',attempt=str(attempt.resolve()),
   lifecycle=dict(protocol=a.PROTOCOL,owner=a.OWNER,token='synthetic-token',leasePath=str(a.ROOT/'shared/output/GPU_HANDOFF.json'),parent=parent))
  execution=attempt/'execution-job.json';execution.write_text(json.dumps(job),encoding='utf8')
  frames=[]
  for i,packet in enumerate(packets):
   header=bytearray(26);header[:8]=b'\x89PNG\r\n\x1a\n';header[12:16]=b'IHDR';header[16:20]=(1080).to_bytes(4,'big');header[20:24]=(900).to_bytes(4,'big');header[25]=6
   image=attempt/f'atlas-{i:06}.png';image.write_bytes(header)
   frames.append(dict(atlasIndex=i,packetFingerprint=packet['fingerprint'],mode=packet['mode'],nativeFrame=packet['nativeFrame'],image=a.pin(image)))
  m=dict(schemaVersion='11.05-structure-atlas-manifest-v2',topicId='11.05',complete=True,job=prov['sourceJob'],jobFingerprint=recipe['fingerprint'],
   picturePlanFingerprint=recipe['picturePlanFingerprint'],producer=prov['producer'],inputPins=inputs,aliases=[],canvas=[1080,900],assetFrames=2,
   executionJob=a.pin(execution),actualSdk=dict(result=0,settings=dict(fps=60,size=dict(x=1080,y=900),background=None,range=[0,.0125])),
   stagedSources=staged,stagedFont=a.pin(stage/'NotoSansKR-VF.ttf'),frames=frames,actualVisualReview=False,actual375Reviewed=False,
   actualSpeechTimingVerified=False,nativePixelVisibilityClaim=False,humanApproval=False)
  path=attempt/'render-manifest.json';path.write_text(json.dumps(m),encoding='utf8');return path,prov,m
 def test_synthetic_saved_manifest_revalidates_source_job_staged_bytes_and_png_headers(self):
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp);path,prov,m=self.manifest_fixture(root)
   with patch.object(a,'ATTEMPTS',root/'attempts'):self.assertEqual(a.validate_manifest(path,prov),m)
 def test_manifest_wrong_context_asset_indices_scope_or_approval_rejected(self):
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp);path,prov,original=self.manifest_fixture(root)
   changes=[lambda m:m.update(jobFingerprint='0'*64),lambda m:m.update(producer={}),lambda m:m['frames'][0].update(atlasIndex=1),
    lambda m:m['frames'][0].update(nativeFrame=99),lambda m:m['frames'][0]['image'].update(path=str(root/'outside.png')),
    lambda m:m['actualSdk']['settings'].update(fps=30),lambda m:m.update(humanApproval=True),lambda m:m.update(actualSpeechTimingVerified=True)]
   for change in changes:
    m=copy.deepcopy(original);change(m);path.write_text(json.dumps(m),encoding='utf8')
    with patch.object(a,'ATTEMPTS',root/'attempts'):self.assertRaises(a.Pending,a.validate_manifest,path,prov)
 def test_manifest_actual_staged_source_font_or_execution_tamper_rejected(self):
  for target in('source','font','execution'):
   with tempfile.TemporaryDirectory()as temp:
    root=Path(temp);path,prov,m=self.manifest_fixture(root)
    changed={'source':m['stagedSources'][0]['path'],'font':m['stagedFont']['path'],'execution':m['executionJob']['path']}[target]
    Path(changed).write_bytes(b'changed')
    with patch.object(a,'ATTEMPTS',root/'attempts'):self.assertRaises(a.Pending,a.validate_manifest,path,prov)
 def test_import_and_default_pending_do_not_import_builder_or_query_resources(self):
  with patch.object(a,'checked_sources'),patch.object(a,'load',side_effect=AssertionError('No actual backend')),patch.object(a.subprocess,'check_output',side_effect=AssertionError('No GPU query')):
   result=a.prepare()
  self.assertFalse(result['ready']);self.assertFalse(result['jobLaunched'])
 def test_pinned_core_and_worker_sources_are_exact(self):
  a.checked_sources()
 def test_imported_self_source_drift_blocks_before_dependencies_or_resources(self):
  with patch.object(a,'sha',return_value='0'*64)as hashed,patch.object(a,'load',side_effect=AssertionError('No backend')):
   self.assertRaisesRegex(a.Pending,'Imported coordinator source changed',a.checked_sources)
  self.assertEqual(hashed.call_count,1)
 def test_foreign_native_reason_never_queries_or_exempts_gpu(self):
  with patch.object(a.subprocess,'check_output',side_effect=AssertionError('No extra query')):
   self.assertEqual(a.resource_reason(SimpleNamespace(busy_reason=lambda _: 'Foreign lease')), 'Foreign lease')
 def test_exact8gib_and_less_than15_policy(self):
  native=SimpleNamespace(busy_reason=lambda _:None)
  for text,blocked in [('8192,14',False),('8191,0',True),('9000,15',True),('9000,16',True)]:
   with patch.object(a.subprocess,'check_output',return_value=text):
    self.assertEqual(a.resource_reason(native)is not None,blocked)
 def test_pid_birth_reuse_is_dead_but_unreadable_identity_is_preserved(self):
  row=dict(pid=123,createTime=10.,argv=['old'])
  with patch.object(a.psutil,'Process',return_value=SimpleNamespace(create_time=lambda:11.)):
   self.assertFalse(a.alive(row))
  with patch.object(a.psutil,'Process',side_effect=a.psutil.AccessDenied(123)):self.assertTrue(a.alive(row))
  with patch.object(a.psutil,'Process',return_value=SimpleNamespace(create_time=lambda:10.,cmdline=lambda:['changed'])):
   self.assertTrue(a.alive(row))
 def test_unknown_owned_renderer_tree_keeps_lease_without_ownership_grant(self):
  process=SimpleNamespace(pid=10,info=dict(name='chrome.exe',cmdline=None))
  with patch.object(a.psutil,'process_iter',return_value=[process]):
   self.assertEqual(a.matching_owned('synthetic-attempt'),[dict(pid=10,unknown=True)])
 def test_recovery_never_archives_foreign_or_live_or_gap_lease(self):
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp);lease=root/'lease.json';calls=[]
   rt=SimpleNamespace(LEASE=lease,ours=lambda r:r.get('owner')==a.OWNER,archive=lambda *_:calls.append('archive'))
   for rec,live,gap in [(dict(owner='foreign',token='t'),False,False),(dict(owner=a.OWNER,token='t',output=str(root/'attempt')),True,False),(dict(owner=a.OWNER,token='t',output=str(root/'attempt')),False,True)]:
    lease.write_text(json.dumps(rec),encoding='utf8');before=lease.read_bytes()
    with patch.object(a,'ATTEMPTS',root),patch.object(a,'alive',return_value=live),patch.object(a,'matching_owned',return_value=[{}]if gap else[]):a.recover_own(rt,{'t'})
    self.assertEqual(lease.read_bytes(),before)
   self.assertEqual(calls,[])
 def test_dead_scoped_complete_tree_can_release_only_known_token(self):
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp);lease=root/'lease.json';lease.write_text(json.dumps(dict(owner=a.OWNER,token='t',output=str(root/'attempt'))),encoding='utf8');calls=[]
   rt=SimpleNamespace(LEASE=lease,ours=lambda _:True,archive=lambda *_:calls.append('archive'))
   with patch.object(a,'ATTEMPTS',root),patch.object(a,'alive',return_value=False),patch.object(a,'matching_owned',return_value=[]):
    a.recover_own(rt,{'unknown'});self.assertEqual(calls,[]);a.recover_own(rt,{'t'})
   self.assertEqual(calls,['archive'])
 def run_launch(self,root,foreign=False,gap=False):
  lease=root/'lease.json';state=root/'state.json';state.write_bytes(b'previous');events=[]
  if foreign:lease.write_text(json.dumps(dict(owner='foreign',token='x')),encoding='utf8')
  oldlease=lease.read_bytes()if foreign else None
  class Worker:
   previous=None
   def acquire(self):events.append('acquire');return self
   def update(self,**value):events.append(('update',value))
   def close(self,**value):events.append(('close',value))
  worker=Worker();rt=SimpleNamespace(LEASE=lease,SingleWorker=lambda *args,**kwargs:worker,ours=lambda r:r.get('owner')==a.OWNER)
  prov=dict(ready=True,topicId='11.05',fingerprint='a'*64,tools=dict(node=dict(path='synthetic-node')),producer={},recipe={})
  ident=dict(pid=123,createTime=10.,argv=['synthetic-controller'],commandSHA256='b'*64,ppid=1,exe='synthetic-python')
  def no_popen(command,**kwargs):
   rec=a.read(lease);self.assertEqual(rec['phase'],'launching');self.assertEqual(rec['pendingCommand'],command)
   self.assertTrue(any(isinstance(e,tuple)and e[0]=='update'and e[1].get('pendingCommand')==command for e in events))
   self.assertEqual(a.read(Path(rec['output'])/'launch.json')['command'],command)
   raise OSError('Synthetic launch gap; no actual process')
  with patch.object(a,'prepare',return_value=prov),patch.object(a,'libraries',return_value=(SimpleNamespace(),rt)),patch.object(a,'identity',return_value=ident), \
       patch.object(a,'resource_reason',return_value=None),patch.object(a,'LAST_RESOURCE_CHECK',{}),patch.object(a,'recover_own'),patch.object(a,'matching_owned',return_value=[dict(unknown=True)]if gap else[]), \
       patch.object(a,'MEDIA',root),patch.object(a,'ATTEMPTS',root/'attempts'),patch.object(a,'STATE',state),patch.object(a,'WORKER',root/'worker'), \
       patch.object(a.shutil,'disk_usage',return_value=SimpleNamespace(free=10*1024**3)),patch.object(a.subprocess,'Popen',side_effect=no_popen):
   try:result=a.execute('synthetic-job','synthetic-caption','synthetic-mix')
   except OSError as e:result=dict(error=str(e))
  return result,lease,state,oldlease,events
 def test_durable_exact_command_precedes_any_popen_and_failure_is_preserved(self):
  with tempfile.TemporaryDirectory()as temp:
   result,lease,state,_,events=self.run_launch(Path(temp))
   self.assertIn('Synthetic launch gap',result['error']);self.assertFalse(lease.exists())
   self.assertEqual(a.read(state)['status'],'failed-preserved')
 def test_foreign_lease_race_never_changes_foreign_bytes_or_old_state(self):
  with tempfile.TemporaryDirectory()as temp:
   result,lease,state,before,events=self.run_launch(Path(temp),foreign=True)
   self.assertEqual(result['exitCode'],75);self.assertEqual(lease.read_bytes(),before);self.assertEqual(state.read_bytes(),b'previous')
 def test_unknown_launch_gap_retains_lease_and_singleton_marker(self):
  with tempfile.TemporaryDirectory()as temp:
   result,lease,state,_,events=self.run_launch(Path(temp),gap=True)
   self.assertTrue(lease.exists());self.assertEqual(a.read(lease)['phase'],'launching')
   self.assertIn(('close',dict(remove=False)),events)
if __name__=='__main__':unittest.main(verbosity=2)
