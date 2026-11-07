"""Synthetic06.02 input/native-receipt/recovery checks. No Unity/GPU/model/media subprocess.
Positive capture fixtures use analytic fake states and mocked image pixels; never actual native proof.
"""
import copy,csv,hashlib,importlib.util,io,json,math,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch,MagicMock
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
def module(name,file):
 sp=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
n=module('prospect_native_cpu_fixture','run-prospect-refuge-native.py');prep=module('prospect_prepare_cpu_fixture','prepare-prospect-refuge-unity.py');g=module('prospect_geometry_cpu_fixture','verify-prospect-refuge-geometry.py')
class NativeTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-prospect-native-cpu-');self.base=Path(self.tmp.name);self.config=n.read(HERE/'prospect-refuge-unity-source/capture-config.json')
 def tearDown(self):self.tmp.cleanup()
 def write(self,p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False),encoding='utf8');return p
 def mode_fixture(self,mode='baseline'):
  c=self.config;folder=self.base/mode;folder.mkdir();cfg=folder/'capture-config.json';cfg.write_bytes((HERE/'prospect-refuge-unity-source/capture-config.json').read_bytes());tape=self.write(folder/'command-tape.json',dict(commands=c['commands']))
  rec=dict(fingerprint='f'*64,mode=mode,configSHA256=n.sha(cfg),commandTapeSHA256=n.sha(tape),frameConvention='Frame0 before Move; capture f, then apply command f once for1/60s to capture f+1; both cameras share evaluated frame',**{k:v for k,v in n.CONTRACT.items()if k!='modes'})
  self.write(folder/'mode-contract.json',rec);self.write(folder/'mode-complete.json',rec);states=[];rays=[];anchors=[];trace=[];offset=c[mode+'SecondCoverOffsetX'];previous=None
  def vd(values):return dict(zip('xyz',values))
  def ray(origin,target,blocked,angle,in_fov,camera=False):
   return dict(id='',hitCollider='synthetic-cover'if blocked else None,hitColliderEntityId='synthetic-native-entity'if blocked else '',origin=origin,desiredEndpoint=target,actualEndpoint={k:(origin[k]+target[k])/2 for k in origin}if blocked else target.copy(),distance=math.dist(list(origin.values()),list(target.values())),horizontalAngleDegrees=angle,blocked=blocked,inRange=True,inFieldOfView=in_fov,cameraInFrustum=camera,seen=not blocked and(camera or in_fov))
  for f in range(600):
   player=vd(g.predicted_player(c,f));x,yaw,phase=n.enemy_at(c,f);enemy=dict(x=x,y=0.,z=c['enemyZ']);eye=dict(x=x,y=c['enemyEyeHeight'],z=c['enemyZ']);camera={k:v+(c['cameraEyeHeight']if k=='y'else 0)for k,v in player.items()};cmd=n.command_at(c,f);applied=n.command_at(c,f-1)if f else dict(id='initial-state',velocity=dict(x=0.,y=0.,z=0.));velocity=applied['velocity'];delta={k:player[k]-previous[k]for k in player}if previous else dict(x=0.,y=0.,z=0.);requested={k:previous[k]+(velocity[k]-(c['groundStickSpeed']if k=='y'else 0))/60 for k in player}if previous else player.copy()
   body=[]
   for name,height,calc in zip(('head','torso','hips'),('headSampleHeight','torsoSampleHeight','hipsSampleHeight'),g.rays(c,f,offset)):
    target={k:v+(c[height]if k=='y'else 0)for k,v in player.items()};r=ray(eye,target,calc['blocked'],calc['angle'],calc['inFov']);r['id']=name;body.append(r)
   target={k:v+(c['enemyTargetHeight']if k=='y'else 0)for k,v in enemy.items()};angle=math.degrees(math.acos((target['z']-camera['z'])/math.hypot(target['x']-camera['x'],target['z']-camera['z'])));observe=ray(camera,target,False,angle,True,True);observe['id']='player-camera-to-enemy-torso'
   st=dict(frame=f,timeSeconds=f/60,secondCoverOffsetX=offset,appliedCommandFrame=f-1,appliedCommandId=applied['id'],appliedVelocity=velocity,nextCommandId=cmd['id'],nextVelocity=cmd['velocity'],playerPosition=player,requestedPlayerPosition=requested,actualMoveDelta=delta,collisionFlags=0,enemyPosition=enemy,enemyEye=eye,enemyYawDegrees=yaw,enemyPhase=phase,playerCameraEye=camera,cameraRotationEuler=dict(x=c['cameraPitchDegrees'],y=c['cameraYawDegrees'],z=0),observerCameraPosition=c['observerPosition'],observerCameraRotationEuler=dict(x=90,y=0,z=0),bodyRays=body,seenBodySamples=sum(r['seen']for r in body),blockedBodySamples=sum(r['blocked']for r in body),enemySeesAnyDeclaredBodySample=any(r['seen']for r in body),playerCameraCanObserveEnemyTorso=observe['seen']);raw=json.dumps(st,separators=(',',':'));states.append(raw)
   rays.append(json.dumps(dict(frame=f,enemyToBody=body,playerCameraToEnemy=observe)))
   points={'player-ground':player,'player-camera-eye':camera,'enemy-eye':eye,'enemy-torso-observation-target':observe['desiredEndpoint'],'second-cover-center':{k:v+(offset if k=='x'else 0)for k,v in c['secondCoverCenter'].items()},'camera-observation-actual-hit-end':observe['actualEndpoint']}
   for r in body:points['body-'+r['id']]=r['desiredEndpoint'];points['ray-'+r['id']+'-actual-hit-end']=r['actualEndpoint']
   anchors.append(json.dumps(dict(frame=f,anchors=[dict(id=k,world=v,playerViewport=dict(x=.5,y=.5,z=10),observerViewport=dict(x=.5,y=.5,z=10))for k,v in points.items()])))
   row=dict(frame=f,timeSeconds=f/60,secondCoverOffsetX=offset,appliedCommandFrame=f-1,appliedCommandId=applied['id'],nextCommandId=cmd['id'],collisionFlags=0,enemyYaw=yaw,enemyPhase=phase,seenBodySamples=st['seenBodySamples'],blockedBodySamples=st['blockedBodySamples'],enemySeesAnySample=int(st['enemySeesAnyDeclaredBodySample']),playerCameraObservesEnemyTorso=int(observe['seen']),stateSHA256=hashlib.sha256(raw.encode()).hexdigest())
   for prefix,v in [('command',velocity),('player',player),('requested',requested),('actualDelta',delta),('enemy',enemy),('enemyEye',eye),('cameraEye',camera),('observer',c['observerPosition'])]:
    for k,value in v.items():row[prefix+k.upper()]=value
   for prefix,v in [('camera',st['cameraRotationEuler']),('observer',st['observerCameraRotationEuler'])]:
    for k,axis in [('Pitch','x'),('Yaw','y'),('Roll','z')]:row[prefix+k]=v[axis]
   for r in body:row[r['id']+'Seen']=int(r['seen'])
   trace.append(row);previous=player
  for name,rows in [('states.jsonl',states),('rays.jsonl',rays),('projected-anchors.jsonl',anchors)]:(folder/name).write_text('\n'.join(rows)+'\n',encoding='utf8')
  with(folder/'trace.csv').open('w',newline='',encoding='utf8')as h:w=csv.DictWriter(h,fieldnames=list(trace[0]));w.writeheader();w.writerows(trace)
  return folder
 def pixel_mocks(self):
  image=MagicMock();image.__enter__.return_value.size=(1920,1080)
  return patch('PIL.Image.open',return_value=image),patch.object(Path,'glob',autospec=True,side_effect=lambda parent,pattern:[parent/f'{i:04}.jpg'for i in range(600)])
 def test_current_config_and_tape_input_schema(self):self.assertFalse(prep.validate_config(self.config)['humanDecisionMeasured'])
 def test_input_tape_gaps_overlap_or_changed_frame_count_rejected(self):
  for kind in('gap','overlap','boolcount','lastend'):
   c=copy.deepcopy(self.config)
   if kind=='gap':c['commands'][1]['startFrame']+=1
   elif kind=='overlap':c['commands'][1]['startFrame']-=1
   elif kind=='boolcount':c['frames']=True
   else:c['commands'][-1]['endFrameExclusive']=599
   with self.subTest(kind=kind),self.assertRaises(AssertionError):prep.validate_config(c)
 def test_nonfinite_capsule_fov_and_foreign_variable_rejected(self):
  for key,value in [('skinWidth',float('nan')),('capsuleHeight',.1),('enemyHorizontalHalfFovDegrees',100),('onlyChangedParameter','enemySpeed')]:
   c=copy.deepcopy(self.config);c[key]=value
   with self.subTest(key=key),self.assertRaises(AssertionError):prep.validate_config(c)
 def test_recursive_float32_keys_strings_and_exact_ints(self):
  n.validate_capture_config(dict(v=[dict(x=1.649999976158142,id='same',frames=600)]),dict(v=[dict(x=1.65,id='same',frames=600)]))
  for bad in(dict(v=[dict(x=1.65,id='changed',frames=600)]),dict(v=[dict(x=True,id='same',frames=600)]),dict(v=[dict(x=1.65,id='same',frames=600.)]),dict(v=[])):
   with self.assertRaises(AssertionError):n.validate_capture_config(bad,dict(v=[dict(x=1.65,id='same',frames=600)]))
 def test_exact_mode_schema_positive_with_synthetic_pixels_only(self):
  for mode in('baseline','shifted'):
   self.mode_fixture(mode);a,b=self.pixel_mocks()
   with a,b:self.assertEqual(len(n.check_mode(self.base,mode,'f'*64,self.config)),600)
 def test_wrong_fingerprint_and_incomplete_trace_rejected(self):
  folder=self.mode_fixture()
  with self.assertRaisesRegex(AssertionError,'receipt'):n.check_mode(self.base,'baseline','wrong',self.config)
  trace=(folder/'trace.csv').read_text();(folder/'trace.csv').write_text('\n'.join(trace.splitlines()[:-1])+'\n')
  with self.assertRaisesRegex(AssertionError,'trace'):n.check_mode(self.base,'baseline','f'*64,self.config)
 def test_changed_serialized_tape_and_state_hash_rejected(self):
  folder=self.mode_fixture();tape=folder/'command-tape.json';old=tape.read_bytes();tape.write_bytes(old+b' ')
  with self.assertRaisesRegex(AssertionError,'tape'):n.check_mode(self.base,'baseline','f'*64,self.config)
  tape.write_bytes(old);file=folder/'states.jsonl';text=file.read_text();file.write_text(text.replace('initial-state','changed-state',1))
  with self.assertRaisesRegex(AssertionError,'SHA'):n.check_mode(self.base,'baseline','f'*64,self.config)
 def test_canonical_unity_version_drift_is_audit_only(self):
  f=self.base/'version';f.write_text('m_EditorVersion: 6000.6.0f1\nm_EditorVersionWithRevision: 6000.6.0f1 (f7f8ed4d1e24)\n');self.assertEqual(n.project_version(f,'6000.6.0f1')['editorVersion'],'6000.6.0f1')
  f.write_text('m_EditorVersion: 6000.5.0f1\n')
  with self.assertRaises(AssertionError):n.project_version(f,'6000.6.0f1')
 def test_owned_export_paths_never_escape_06(self):
  with patch.object(n,'UNITY_ROOT',self.base/'original'):
   source,target=n.export_paths(n.FOLDER+'.meta',self.base/'stage');self.assertEqual(target,self.base/'original'/(n.FOLDER+'.meta'))
   for value in(n.FOLDER+'/../07-04/file.unity','Assets/VideoScenes/architectural-111-20261106/07-04/f.unity','C:/outside.unity',n.FOLDER+'//bad'):
    with self.subTest(value=value),self.assertRaises(AssertionError):n.export_paths(value,self.base/'stage')
 def test_import_meta_same_guid_only_after_known_or_owned_completion(self):
  a=self.base/'a.meta';b=self.base/'b.meta';a.write_text('guid: '+'a'*32+'\n');b.write_text('guid: '+'a'*32+'\nimporter: changed\n');row=dict(target='Assets/a.meta',sha256=n.sha(a))
  with self.assertRaises(AssertionError):n.staged_input(row,a,b,{})
  proof=n.staged_input(row,a,b,{},True);self.assertEqual(n.staged_input(row,a,b,{row['target']:proof}),proof)
  b.write_text('guid: '+'b'*32+'\n')
  with self.assertRaises(AssertionError):n.staged_input(row,a,b,{},True)
 def test_foreign_lease_and_unrecorded_launch_gap_preserved(self):
  lease=self.write(self.base/'lease.json',dict(protocol='foreign',owner='someone',token='t',pid=1,createTime=1,phase='reserved'))
  self.assertFalse(n.runtime.recover_own_lease({'t'},lease,lambda r:False,lambda r:False));self.assertTrue(lease.exists())
  rec=dict(protocol=n.PROTOCOL,owner=n.OWNER,token='t',pid=1,createTime=1,phase='launching',fingerprint='f',output='out');self.write(lease,rec)
  self.assertFalse(n.runtime.recover_own_lease({'t'},lease,lambda r:False,lambda r:True));self.assertTrue(lease.exists())
  self.assertTrue(n.runtime.recover_own_lease({'t'},lease,lambda r:False,lambda r:False));self.assertFalse(lease.exists())
 def test_live_child_and_missing_identity_preserve_lease(self):
  for child in(dict(pid=2,createTime=2),dict(pid=2)):
   lease=self.write(self.base/'lease.json',dict(protocol=n.PROTOCOL,owner=n.OWNER,token='t',pid=1,createTime=1,phase='running',child=child))
   self.assertFalse(n.runtime.recover_own_lease({'t'},lease,lambda r:bool(r and r.get('pid')==2),lambda r:False));self.assertTrue(lease.exists())
 def test_singleton_refuses_foreign_marker_without_overwrite(self):
  f=self.write(self.base/'worker.json',dict(protocol='foreign'));before=f.read_bytes()
  with self.assertRaises(RuntimeError):n.runtime.SingleWorker(f,is_alive=lambda r:False).acquire()
  self.assertEqual(f.read_bytes(),before)
 def test_singleton_recovers_only_dead_own_marker(self):
  f=self.write(self.base/'worker.json',dict(protocol=n.PROTOCOL,owner=n.OWNER,token='old',pid=1,createTime=1,child=None))
  w=n.runtime.SingleWorker(f,is_alive=lambda r:False).acquire()
  try:self.assertEqual(w.previous['token'],'old');self.assertEqual(w.record['protocol'],n.PROTOCOL)
  finally:w.close()
 def test_entity_id_provenance_string_no_integer_alias(self):
  origin=dict(x=0.,y=0.,z=0.);target=dict(x=0.,y=0.,z=1.);ray=dict(origin=origin,desiredEndpoint=target,actualEndpoint=dict(x=0.,y=0.,z=.5),distance=1.,horizontalAngleDegrees=0.,hitCollider='own-cover',hitColliderEntityId='native-entity',blocked=True,inRange=True,inFieldOfView=True,cameraInFrustum=False,seen=False)
  n.check_ray(ray,origin,target)
  for value in('',0,True):
   bad=copy.deepcopy(ray);bad['hitColliderEntityId']=value
   with self.subTest(value=value),self.assertRaises(AssertionError):n.check_ray(bad,origin,target)
  ray.update(blocked=False,seen=True,actualEndpoint=target,hitColliderEntityId='');n.check_ray(ray,origin,target)
 def test_pid_reuse_and_access_denied_identity_are_conservative(self):
  with patch.object(n.runtime.psutil,'Process',return_value=SimpleNamespace(create_time=lambda:2.)):
   self.assertFalse(n.runtime.alive(dict(pid=1,createTime=1.)));self.assertTrue(n.runtime.alive(dict(pid=1)))
  with patch.object(n.runtime.psutil,'Process',side_effect=n.psutil.AccessDenied(1)):self.assertTrue(n.runtime.alive(dict(pid=1,createTime=1.)))
 def test_stage_without_static_compile_writes_nothing(self):
  with patch.object(prep,'PROJECT',self.base/'project'),patch.object(prep,'REPORT',self.base/'staging.json'),self.assertRaisesRegex(AssertionError,'compile'):prep.stage(dict(staticCompilerPreflight=None))
  self.assertFalse((self.base/'project').exists());self.assertFalse((self.base/'staging.json').exists())
 def test_model_child_blocks_even_without_lease(self):
  process=SimpleNamespace(info=dict(name='python.exe',cmdline=['python','worker.py','--recognize','job.json']))
  with patch.object(n.runtime,'busy_reason',return_value=None),patch.object(n.psutil,'process_iter',return_value=[process]):self.assertIn('model',n.busy_reason())
 def test_popen_bookkeeping_gap_preserves_own_lease_and_marker(self):
  lease=self.base/'lease.json';state=self.base/'state.json';output=self.base/'output';output.mkdir();prov=dict(fingerprint='f'*64,project='synthetic-stage',captureEntry='Synthetic.Capture');calls=[]
  record={};worker=SimpleNamespace(previous=None,record=record,update=lambda **k:record.update(k),close=lambda **k:calls.append(k));factory=SimpleNamespace(acquire=lambda:worker)
  with patch.object(sys,'argv',['runner','--execute','--wait-hours','0']),patch.object(n,'authorize',return_value=prov),patch.object(n,'PREP',self.write(self.base/'prep.json',dict(config={}))),patch.object(n,'completed_native',return_value=None),patch.object(n,'scan',return_value=(None,{})),patch.object(n,'stage',return_value=output),patch.object(n,'STATE',state),patch.object(n.runtime,'LEASE',lease),patch.object(n.runtime,'SingleWorker',return_value=factory),patch.object(n.runtime,'identity',return_value=dict(pid=1,createTime=1.)),patch.object(n.runtime,'alive',return_value=False),patch.object(n.runtime,'recover_own_lease',return_value=False),patch.object(n,'busy_reason',return_value=None),patch.object(n.runtime,'unrecorded_child_alive',return_value=True),patch.object(n.subprocess,'Popen',side_effect=RuntimeError('synthetic-Popen-gap')),self.assertRaisesRegex(RuntimeError,'Popen-gap'):n.main()
  self.assertTrue(lease.exists());self.assertEqual(n.read(lease)['phase'],'launching');self.assertEqual(calls[-1],dict(remove=False))
 def test_current_source_authority_never_freezes_editorial_hashes(self):
  source=Path(n.__file__).read_text();part=source[source.index('def authorize('):source.index('def export_paths(')]
  self.assertIn("prepare.preflight()",part);self.assertNotIn("HERE/'checkpoint.json'",part);self.assertNotIn('narration-draft',part)
 def test_default_no_stage_or_process_when_staging_report_missing(self):
  with patch.object(sys,'argv',['run-prospect-refuge-native.py']),patch.object(n,'authorize',side_effect=FileNotFoundError('staging missing')),patch.object(n.subprocess,'Popen',side_effect=AssertionError('No launch')),patch('sys.stdout',new_callable=io.StringIO)as out:
   n.main();self.assertFalse(json.loads(out.getvalue())['ready'])
 def test_existing_live_state_not_overwritten_on_decline(self):
  state=self.write(self.base/'state.json',dict(pid=1,createTime=1,child=dict(pid=2,createTime=2),status='live'));before=state.read_bytes();worker=SimpleNamespace(previous=None,record={},update=lambda **k:None,close=lambda **k:None);factory=SimpleNamespace(acquire=lambda:worker)
  with patch.object(sys,'argv',['runner','--execute']),patch.object(n,'authorize',return_value={'fingerprint':'f'}),patch.object(n,'PREP',self.write(self.base/'prep.json',dict(config={}))),patch.object(n,'completed_native',return_value=None),patch.object(n,'scan',return_value=(None,{})),patch.object(n,'STATE',state),patch.object(n.runtime,'SingleWorker',return_value=factory),patch.object(n.runtime,'alive',return_value=True),self.assertRaises(RuntimeError):n.main()
  self.assertEqual(state.read_bytes(),before)
 def test_float32_patrol_actual_frame314_and_phase_boundaries(self):
  self.assertEqual(n.enemy_at(self.config,314),(5.,229.99977111816406,'scripted-waypoint-turn'))
  for frame,phase in[(299,'patrol-outbound'),(300,'scripted-waypoint-turn'),(317,'scripted-waypoint-turn'),(318,'patrol-return'),(377,'patrol-return'),(378,'scripted-waypoint-pause')]:
   with self.subTest(frame=frame):self.assertEqual(n.enemy_at(self.config,frame)[2],phase)
  self.assertEqual(n.f32(self.config['enemyTurnEndSeconds']),5.300000190734863)
  self.assertFalse(n.near(229.99977111816406,230.00000000000014)) #Tolerance remains unchanged.
 def test_actual_preserved_all600_patrol_states_each_mode(self):
  attempt=n.MEDIA/'shorts-leveldesign-06-02/native-attempts/20261107-063637-cd2000d213'
  if not attempt.exists():self.skipTest('Actual selected capture not available on this machine; synthetic fixtures remain separate')
  pins={'baseline':'5b80497baf16301fa514bde8ed4f7b16528484510a0a1e12d770f1261c274c24','shifted':'c1bfddc4796ee9efd9b99654e0f581a5282bce96ef96beee8950bfe5b9850846'}
  for mode,expected_sha in pins.items():
   path=attempt/mode/'states.jsonl';self.assertEqual(n.sha(path),expected_sha);rows=[json.loads(s)for s in path.read_text(encoding='utf8').splitlines()];self.assertEqual(len(rows),600)
   for frame,row in enumerate(rows):
    x,yaw,phase=n.enemy_at(self.config,frame)
    with self.subTest(mode=mode,frame=frame):self.assertTrue(n.near(row['enemyPosition']['x'],x));self.assertTrue(n.near(row['enemyYawDegrees'],yaw));self.assertEqual(row['enemyPhase'],phase)
 def compatibility_fixture(self):
  data=dict(protocol=n.PROTOCOL,topicId='06.02',preparationFingerprint='physical-prep',project='same-native-project',captureEntry='Same.Capture',contract=n.CONTRACT,editorVersion='6000.6.0f1',pins=[dict(source='same.cs',target='Assets/same.cs',sha256='a'*64),dict(path=str(Path(n.__file__).resolve()),sha256='old')])
  content=b'preserved original validator';oldsha=hashlib.sha256(content).hexdigest();data['pins'][-1]['sha256']=oldsha
  previous=self.base/'shorts-leveldesign-06-02/native-validation-history'/oldsha[:24]/Path(n.__file__).name;previous.parent.mkdir(parents=True);previous.write_bytes(content)
  data['fingerprint']=n.digest({k:data[k]for k in n.NATIVE_IDENTITY_FIELDS});current=copy.deepcopy(data);current['pins'][-1]['sha256']='b'*64;current['fingerprint']=n.digest({k:current[k]for k in n.NATIVE_IDENTITY_FIELDS})
  return data,current,previous
 def test_cpu_adoption_only_validator_sha_delta_is_allowed(self):
  old,current,previous=self.compatibility_fixture()
  with patch.object(n,'MEDIA',self.base):proof=n.historical_native_compatibility(old,current)
  self.assertTrue(proof['nativePinsUnchanged']);self.assertEqual(proof['preservedOriginalValidator']['sha256'],n.sha(previous))
 def test_cpu_adoption_rejects_changed_native_or_engine_pin(self):
  old,current,_=self.compatibility_fixture()
  for kind in('native','engine','preparation','helper'):
   new=copy.deepcopy(current)
   if kind=='native':new['pins'][0]['sha256']='c'*64
   elif kind=='engine':new['editorVersion']='6000.5.0f1'
   elif kind=='preparation':new['preparationFingerprint']='new-physical-prep'
   else:
    old=copy.deepcopy(old);old['pins'].insert(0,dict(path='same-resource-helper.py',sha256='d'*64));old['fingerprint']=n.digest({k:old[k]for k in n.NATIVE_IDENTITY_FIELDS});new['pins'].insert(0,dict(path='same-resource-helper.py',sha256='e'*64))
   new['fingerprint']=n.digest({k:new[k]for k in n.NATIVE_IDENTITY_FIELDS})
   with self.subTest(kind=kind),patch.object(n,'MEDIA',self.base),self.assertRaises(AssertionError):n.historical_native_compatibility(old,new)
 def test_cpu_adoption_requires_old_input_digest_and_preserved_source(self):
  old,current,previous=self.compatibility_fixture()
  with patch.object(n,'MEDIA',self.base):
   bad=copy.deepcopy(old);bad['fingerprint']='forged'
   with self.assertRaisesRegex(AssertionError,'fingerprint'):n.historical_native_compatibility(bad,current)
   previous.write_bytes(b'tampered')
   with self.assertRaisesRegex(AssertionError,'source proof'):n.historical_native_compatibility(old,current)
 def test_cpu_adoption_readonly_never_locks_or_launches(self):
  attempt=self.base/'attempt';attempt.mkdir();old=dict(fingerprint='old');current=dict(fingerprint='current');plan=dict(status='read-only-ready',newGpuStarted=False)
  with patch.object(n,'adoption_plan',return_value=(attempt,old,current,{},plan)),patch.object(n,'PROJECT_RECORD',self.base/'project'),patch.object(n.runtime,'SingleWorker',side_effect=AssertionError('Readonly must not lock')),patch.object(n.subprocess,'Popen',side_effect=AssertionError('No native/model launch')):
   self.assertEqual(n.adopt_existing_attempt(attempt),plan)
  self.assertEqual(list(attempt.iterdir()),[])
 def test_cpu_adoption_existing_advanced_evidence_is_never_rewritten(self):
  attempt=self.base/'attempt';attempt.mkdir();project=self.base/'project';e=self.write(project/'native-evidence-v1.json',dict(captureComplete=True,actualVisualReview=True,humanApproval=True));before=e.read_bytes();old=dict(fingerprint='old');current=dict(fingerprint='current');prior=dict(output=str(attempt),fingerprint='old',actualVisualReview=True,humanApproval=True)
  with patch.object(n,'adoption_plan',return_value=(attempt,old,current,{},{})),patch.object(n,'PROJECT_RECORD',project),patch.object(n,'completed_native',return_value=prior),patch.object(n,'verify_export',side_effect=AssertionError('Advanced evidence must not be overwritten')):
   self.assertTrue(n.adopt_existing_attempt(attempt,True)['evidenceUnchanged'])
  self.assertEqual(e.read_bytes(),before)
 def test_cpu_adoption_execute_keeps_capture_identity_and_foreign_lease(self):
  attempt=self.base/'attempt';attempt.mkdir();project=self.base/'project';state=self.write(self.base/'failed-state.json',dict(status='failed-preserved'));before=state.read_bytes();foreign=self.write(self.base/'foreign-lease.json',dict(owner='foreign',token='preserve'));lease_bytes=foreign.read_bytes()
  old=dict(fingerprint='o'*64);current=dict(fingerprint='c'*64);plan=dict(actualLaunch=dict(sha256=n.sha(state)),captureFingerprint=old['fingerprint'],currentValidatorFingerprint=current['fingerprint']);closed=[];worker=SimpleNamespace(close=lambda:closed.append(True));factory=SimpleNamespace(acquire=lambda:worker);export_calls=[]
  def exporter(output,prov,config):export_calls.append(prov['fingerprint']);return dict(fingerprint=prov['fingerprint'],actualVisualReview=False,humanApproval=False)
  with patch.object(n,'adoption_plan',return_value=(attempt,old,current,{},plan)),patch.object(n,'PROJECT_RECORD',project),patch.object(n,'STATE',state),patch.object(n.runtime,'LEASE',foreign),patch.object(n.runtime,'SingleWorker',return_value=factory),patch.object(n,'adoption_state',return_value={}),patch.object(n,'authorize',return_value=current),patch.object(n,'historical_native_compatibility',return_value={}),patch.object(n,'verify_export',side_effect=exporter),patch.object(n,'busy_reason',side_effect=AssertionError('No GPU resource/job stage')),patch.object(n.subprocess,'Popen',side_effect=AssertionError('No launch')):
   result=n.adopt_existing_attempt(attempt,True)
  self.assertFalse(result['newGpuStarted']);self.assertEqual(export_calls,['o'*64]);self.assertEqual(closed,[True]);self.assertEqual(state.read_bytes(),before);self.assertEqual(foreign.read_bytes(),lease_bytes)
  evidence=n.read(project/'native-evidence-v1.json');self.assertEqual(evidence['fingerprint'],'o'*64);self.assertEqual(evidence['currentValidatorFingerprint'],'c'*64);self.assertFalse(evidence['humanApproval'])
 def test_cpu_adoption_live_or_unknown_child_and_wrong_exit_block(self):
  output=self.base/'attempt';old=dict(fingerprint='old',project='same-project',captureEntry='Same.Capture');state=dict(protocol=n.PROTOCOL,owner=n.OWNER,pid=1,createTime=1,child=dict(pid=2,createTime=2),fingerprint='old',output=str(output),gpuStarted=True,unityExitCode=0)
  state['command']=[str(n.EDITOR),'-batchmode','-projectPath',old['project'],'-executeMethod',old['captureEntry'],'-prospectRefugeOutput',str(output),'-prospectRefugeFingerprint','old','-prospectRefugeModes','baseline,shifted','-logFile',str(output/'unity.log')];file=self.write(self.base/'state.json',state)
  with patch.object(n,'STATE',file),patch.object(n.runtime,'alive',return_value=True),self.assertRaisesRegex(AssertionError,'alive or unknown'):n.adoption_state(output,old)
  state['unityExitCode']=1;self.write(file,state)
  with patch.object(n,'STATE',file),patch.object(n.runtime,'alive',return_value=False),self.assertRaisesRegex(AssertionError,'exit0'):n.adoption_state(output,old)
 def test_cpu_adoption_does_not_accept_outside_attempt_tree(self):
  with patch.object(n,'ATTEMPTS',self.base/'allowed'),self.assertRaisesRegex(AssertionError,'exact existing'):n.adoption_plan(self.base/'outside')
if __name__=='__main__':unittest.main(verbosity=2)
