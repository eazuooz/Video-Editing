"""CPU-only11.05 controller fixtures. No Unity/resource query/stage/model/media launch."""
import importlib.util,json,hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
S=Path(__file__).with_name('run-solution-path-native-v2.py');spec=importlib.util.spec_from_file_location('solution_native_test',S);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v),encoding='utf-8')
class Tests(unittest.TestCase):
 def test_actual_model_selected_seed(self):
  g=m.graph_expected(173,0,0,False);self.assertEqual(g['mandatoryRoute'],[1,5,6,7,11,10,9,8,12,13,14]);self.assertTrue(m.reachable(g));self.assertIn('sealed',g['roomRoles'])
 def test_100_seed_graphs_and_negative(self):
  for seed in range(100):
   self.assertTrue(m.reachable(m.graph_expected(seed,0,0,False)));self.assertFalse(m.reachable(m.graph_expected(seed,0,0,True)))
 def test_branch_only_graph_change(self):
  a=m.graph_expected(173,0,0,False);b=m.graph_expected(173,1,0,False);self.assertEqual(a['mandatoryRoute'],b['mandatoryRoute']);self.assertEqual(a['roomVariants'],b['roomVariants']);self.assertNotEqual(a['edges'],b['edges'])
 def test_template_only_graph_change(self):
  a=m.graph_expected(173,0,0,False);b=m.graph_expected(173,0,1,False);self.assertEqual(a['edges'],b['edges']);self.assertTrue(all(x!=y for x,y in zip(a['roomVariants'],b['roomVariants'])))
 def test_enemy_offset_perpendicular_to_mid_straight(self):
  c=json.loads((m.prep.SOURCE/'config.json').read_text(encoding='utf-8-sig'));g=m.graph_expected(173,0,0,False);focus,perp=m.enemy_basis(c,g);self.assertEqual(focus,[3.,0.,-3.]);self.assertEqual(perp,[0.,0.,1.]);self.assertEqual(sum(x*y for x,y in zip(perp,[-1.,0.,0.])),0.)
 def test_nonzero_metadata_guid_required(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x.meta';p.write_text('guid: '+'0'*32+'\n')
   with self.assertRaises(m.Pending):m.guid(p)
   p.write_text('guid: '+'a'*32+'\n');self.assertEqual(m.guid(p),'a'*32)
 def test_subset_request_identity(self):
  self.assertNotEqual(m.request_fp('f'*64,['construction']),m.request_fp('f'*64,m.prep.MODES));self.assertEqual(m.modes_arg('threats-b,construction'),['construction','threats-b'])
 def test_bad_mode_sets(self):
  for value in('',None,'construction,construction','../03.02','unknown'):
   with self.assertRaises(m.Pending):m.modes_arg(value)
 def test_exact_hub_serve_only(self):
  row=dict(pid=9,name='Unity.exe',exe=str(m.HUB),cmdline=[str(m.HUB),'serve']);self.assertIsNone(m.process_reason(row,1))
  for args in([str(m.HUB),'serve','-batchmode'],[str(m.HUB),'serve-editor']):self.assertIsNotNone(m.process_reason(dict(row,cmdline=args),1))
  self.assertIsNotNone(m.process_reason(dict(row,exe=str(m.EDITOR),cmdline=[str(m.EDITOR),'-batchmode']),1))
 def test_game_media_model_headless_guards(self):
  for name,args in [('factorio.exe',[]),('spelunky.exe',[]),('spelunky_classic.exe',[]),('spel2.exe',[]),('ffmpeg.exe',[]),('python.exe',['python.exe','--recognize']),('msedge.exe',['msedge.exe','--headless=new'])]:self.assertIsNotNone(m.process_reason(dict(pid=2,name=name,exe='C:/apps/'+name,cmdline=args),1))
 def test_no_gpu_query_when_custom_guard_blocks(self):
  class Fake:info=dict(pid=2,name='factorio.exe',exe='C:/factorio.exe',cmdline=[])
  with patch.object(m.psutil,'process_iter',return_value=[Fake()]),patch.object(m.rt,'busy_reason',side_effect=AssertionError('mustnotqueryGPU')):self.assertIsNotNone(m.busy_reason())
 def test_changed_classifier_source_blocks_before_resource_calls(self):
  with patch.object(m,'sha',return_value='0'*64),patch.object(m.psutil,'process_iter',side_effect=AssertionError('mustnotinspectresources')),patch.object(m.qualifier,'qualify',side_effect=AssertionError('mustnotqualify')):
   with self.assertRaises(m.Pending):m.busy_reason()
 def test_legacy_classifier_scope_only_output_base_changed(self):
  q=m.qualifier;self.assertEqual(q.BASE,m.BASE/'resource-observations');self.assertIn('shorts-leveldesign-06-02',str(q.AUDIT));self.assertIn('shorts-leveldesign-06-02',str(q.SAMPLES));self.assertEqual(set(q.PROFILES),{24696,66848});self.assertEqual(len(q.EXPECTED),16)
 def test_qualified_headless_still_requires_exact_current_identity(self):
  q=m.qualifier;argv=[q.EDGE_EXE,'--headless=new'];signature=(1,1.5,q.argv_sha(argv));info=dict(pid=2,ppid=1,create_time=1.5,name='msedge.exe',exe=q.EDGE_EXE,cmdline=argv)
  with patch.dict(q.EXPECTED,{2:signature},clear=True):
   self.assertIsNone(m.process_reason(info,99,{2}))
   for changed in(dict(info,create_time=1.6),dict(info,cmdline=argv+['--remote-debugging-port=9']),dict(info,cmdline=None),dict(info,pid=3)):
    self.assertIsNotNone(m.process_reason(changed,99,{2}))
 def test_low_headroom_cannot_be_qualified(self):
  with tempfile.TemporaryDirectory()as d,patch.object(m.qualifier,'BASE',Path(d)),patch.object(m.qualifier,'snapshot',side_effect=AssertionError('mustnotinspectwhenbaseguarddeclines')):
   result=m.qualifier.qualify(base_guard=lambda:'GPU headroom insufficient (7443 MiB free,16% use)');self.assertFalse(result['qualified']);self.assertEqual(result['qualifiedPids'],[]);self.assertIn('7443',result['reason'])
 def test_unknown_headless_after_qualification_blocks(self):
  class Fake:info=dict(pid=99999,ppid=1,create_time=1.,name='msedge.exe',exe=m.qualifier.EDGE_EXE,cmdline=['msedge.exe','--headless=new'])
  with patch.object(m.psutil,'process_iter',return_value=[Fake()]),patch.object(m.qualifier,'qualify',return_value=dict(qualified=True,qualifiedPids=[2],reason=None,evidence={})),patch.object(m.rt,'busy_reason',return_value=None):self.assertIsNotNone(m.busy_reason('ours'))
 def test_classifier_base_guard_receives_own_token_and_no_grant(self):
  def qualify(base_guard):
   self.assertIsNone(base_guard());return dict(qualified=True,qualifiedPids=[],reason=None,evidence={})
  with patch.object(m.psutil,'process_iter',return_value=[]),patch.object(m.qualifier,'qualify',side_effect=qualify),patch.object(m.rt,'busy_reason',return_value=None)as guard:
   self.assertIsNone(m.busy_reason('ours'));self.assertEqual([x.args for x in guard.call_args_list],[('ours',),('ours',)]);self.assertEqual(m.LAST_RESOURCE_CLASSIFICATION['classifierOriginTopicId'],'06.02');self.assertEqual(m.LAST_RESOURCE_CLASSIFICATION['currentJobTopicId'],'11.05');self.assertFalse(m.LAST_RESOURCE_CLASSIFICATION['ownershipGranted']);self.assertFalse(m.LAST_RESOURCE_CLASSIFICATION['processTerminationAuthorized'])
 def test_launch_gap_exact_and_unknown(self):
  command=['Unity.exe','-solutionOutput','unique','-solutionFingerprint','f'*64];r=dict(phase='launching',child=None,launchCommand=command)
  class Fake:info=dict(name='unity.exe',cmdline=command)
  with patch.object(m.psutil,'process_iter',return_value=[Fake()]):self.assertTrue(m.gap_alive(r))
  Fake.info=dict(name='unity.exe',cmdline=None)
  with patch.object(m.psutil,'process_iter',return_value=[Fake()]):self.assertTrue(m.gap_alive(r))
  Fake.info=dict(name='unity.exe',cmdline=['Unity.exe','different'])
  with patch.object(m.psutil,'process_iter',return_value=[Fake()]):self.assertFalse(m.gap_alive(r))
 def test_foreign_lease_preserved(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'lease.json';write(p,dict(protocol='foreign',owner='other',token='x',pid=1,createTime=1,phase='reserved'));before=p.read_bytes();self.assertFalse(m.rt.recover_own_lease({'x'},lease=p,is_alive=lambda r:False,unrecorded=lambda r:False));self.assertEqual(p.read_bytes(),before)
 def test_own_live_child_lease_preserved(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'lease.json';write(p,dict(protocol=m.PROTOCOL,owner=m.OWNER,token='x',pid=1,createTime=1,phase='running',child=dict(pid=2,createTime=2)));before=p.read_bytes();self.assertFalse(m.rt.recover_own_lease({'x'},lease=p,is_alive=lambda r:bool(r and r.get('pid')==2),unrecorded=lambda r:False));self.assertEqual(p.read_bytes(),before)
 def test_launch_gap_lease_preserved_then_recovered(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'lease.json';write(p,dict(protocol=m.PROTOCOL,owner=m.OWNER,token='x',pid=1,createTime=1,phase='launching'));self.assertFalse(m.rt.recover_own_lease({'x'},lease=p,is_alive=lambda r:False,unrecorded=lambda r:True));self.assertTrue(p.exists());self.assertTrue(m.rt.recover_own_lease({'x'},lease=p,is_alive=lambda r:False,unrecorded=lambda r:False));self.assertFalse(p.exists())
 def test_singleton_preserves_live_old_record(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'worker.json';write(p,dict(protocol=m.PROTOCOL,owner=m.OWNER,token='old',pid=11,createTime=1,child=None));before=p.read_bytes()
   with self.assertRaises(RuntimeError):m.rt.SingleWorker(p,is_alive=lambda r:bool(r)).acquire()
   self.assertEqual(before,p.read_bytes())
 def test_singleton_recovers_only_dead_owned(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'worker.json';write(p,dict(protocol=m.PROTOCOL,owner=m.OWNER,token='old',pid=11,createTime=1,child=None));worker=m.rt.SingleWorker(p,is_alive=lambda r:False).acquire()
   try:self.assertEqual(worker.previous['token'],'old');self.assertNotEqual(worker.record['token'],'old')
   finally:worker.close()
 def test_flat_snapshot_and_tamper(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);name=m.FOLDER+'/S02-Construction.unity';data=b'ownscene';r=dict(path=name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),snapshotFile='editable/'+hashlib.sha256(name.encode()).hexdigest()+'.bin');p=root/r['snapshotFile'];p.parent.mkdir();p.write_bytes(data);self.assertEqual(m.snapshot_paths(r,root)[0],name);p.write_bytes(b'wrong')
   with self.assertRaises(m.Pending):m.snapshot_paths(r,root)
 def test_flat_snapshot_wrong_name_and_traversal(self):
  for name in('../03.02/scene.unity','C:/scene.unity','Assets//bad','Assets/../03.02'):
   with self.assertRaises(m.Pending):m.prep.canonical(name)
  with tempfile.TemporaryDirectory()as d:
   with self.assertRaises(m.Pending):m.snapshot_paths(dict(path=m.FOLDER+'/x',snapshotFile='editable/wrong.bin'),Path(d))
 def test_owned_export_scope(self):
  self.assertEqual(m.export_target(m.FOLDER+'.meta'),Path(str(m.UNITY/m.FOLDER)+'.meta').resolve())
  for name in('Assets/VideoScenes/architectural-111-20261106/03-02/x.unity',m.FOLDER+'/../03-02/x.unity',str((m.UNITY/m.FOLDER).resolve()),m.FOLDER+'-other/x.unity'):
   with self.assertRaises(m.Pending):m.export_target(name)
 def test_wrong_mode_fp_rejected_before_frames(self):
  with tempfile.TemporaryDirectory()as d:
   a=Path(d);physical='a'*64;requested=['construction'];fp=m.request_fp(physical,requested);write(a/'input-provenance.json',dict(physicalInputFingerprint=physical,fingerprint=fp,requestedModes=requested));c=json.loads((m.prep.SOURCE/'config.json').read_text(encoding='utf-8-sig'));done=dict(fingerprint='wrong',mode='construction',frames=1200,fps=60,width=1920,height=1080,cameras=['player','observer'],actualSceneSaved=True,frameConvention='capture0=initial; command f produces capture f+1');write(a/'capture/construction/mode-complete.json',done);write(a/'capture/construction/mode-contract.json',done)
   with self.assertRaises(m.Pending):m.check_mode(a,'construction',dict(physicalInputFingerprint=physical,config=c))
 def test_finite_reference_tape_not_feedback(self):
  c=json.loads((m.prep.SOURCE/'config.json').read_text(encoding='utf-8-sig'));a=m.graph_expected(c['seed'],0,0,False);b=m.graph_expected(c['seed'],1,1,False)
  for i in range(1200):self.assertEqual(m.planned(c,a,i),m.planned(c,b,i))
 def test_projection_camera_and_self_hit_semantics(self):
  v=lambda x,y,z:dict(x=x,y=y,z=z)
  state=dict(playerVP=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],playerCameraPosition=v(0,0,0));ray=dict(origin=v(0,0,0),target=v(0,0,1),hit=True,hitPoint=v(0,0,1),hitCollider='actual target',targetDistance=1,hitDistance=1,hitBeforeTarget=False);anchor=dict(world=v(0,0,1),playerViewport=v(.5,.5,1),playerRay=ray);m.projection(anchor,state,'player');anchor['playerRay']['hitBeforeTarget']=True
  with self.assertRaises(m.Pending):m.projection(anchor,state,'player')
 def test_saved_import_requires_exact_recorded_hash(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);original=root/'original.meta';original.write_text('fileFormatVersion: 2\nguid: '+'a'*32+'\n');name=m.FOLDER+'/shared.meta';snapname='editable/'+hashlib.sha256(name.encode()).hexdigest()+'.bin';target=root/snapname;target.parent.mkdir();target.write_text('fileFormatVersion: 3\nguid: '+'a'*32+'\n');row=dict(source='original.meta',target=name,sha256=m.sha(original));snapshot=dict(path=name,snapshotFile=snapname,sha256=m.sha(target),bytes=target.stat().st_size);record=dict(target=name,sourceSHA256=row['sha256'],stagedSHA256=snapshot['sha256'],guid='a'*32)
   with patch.object(m,'ROOT',root):
    m.saved_input(row,snapshot,root,[record])
    for changes in([],[dict(record,stagedSHA256='0'*64)]):
     with self.assertRaises(m.Pending):m.saved_input(row,snapshot,root,changes)
 def test_compiler_exact_three_positive_then_stale_rejected(self):
  with tempfile.TemporaryDirectory()as d:
   base=Path(d);source=base/'src';folder=base/'unity-cpu-preflight/x';source.mkdir();folder.mkdir(parents=True)
   for name in m.prep.CS:(source/name).parent.mkdir(parents=True,exist_ok=True);(source/name).write_text('// fixture only; not actual compiled source')
   (source/'config.json').write_text('{}');rsp=folder/'fixture.rsp';rsp.write_text('\n'.join('"'+str((source/n).resolve())+'"'for n in m.prep.CS));compiler=folder/'compiler.fixture';compiler.write_bytes(b'fixture');dotnet=folder/'dotnet.fixture';dotnet.write_bytes(b'fixture')
   c=dict(schemaVersion='11-05-solution-path-static-compiler-v1',compilerExitCode=0,staticCompilationPassed=True,sourceHashes={n:m.sha(source/n)for n in m.prep.CS},config=m.pin(source/'config.json'),compiler=m.pin(compiler),dotnet=m.pin(dotnet),actualResponseFile=m.pin(rsp),unityEditorLaunched=False,gpuStarted=False);write(folder/'compile-receipt.json',c)
   with patch.object(m.prep,'SOURCE',source),patch.object(m.prep,'BASE',base):
    self.assertIsNotNone(m.prep.compiler_proof(m.sha(source/'config.json')));(source/'GraphModel.cs').write_text('// changed')
    self.assertIsNone(m.prep.compiler_proof(m.sha(source/'config.json')))
 def test_compiler_empty_and_changed_sources_rejected(self):
  with tempfile.TemporaryDirectory()as d:
   base=Path(d);source=base/'src';folder=base/'unity-cpu-preflight/x';source.mkdir()
   for name in m.prep.CS:
    (source/name).parent.mkdir(parents=True,exist_ok=True);(source/name).write_text('//fixture')
   (source/'config.json').write_text('{}');write(folder/'compile-receipt.json',dict(schemaVersion='11-05-solution-path-static-compiler-v1',compilerExitCode=0,staticCompilationPassed=True,sourceHashes={},config=dict(path=str(source/'config.json'),sha256=m.sha(source/'config.json'))))
   with patch.object(m.prep,'SOURCE',source),patch.object(m.prep,'BASE',base):self.assertIsNone(m.prep.compiler_proof(m.sha(source/'config.json')))
if __name__=='__main__':unittest.main(verbosity=2)
