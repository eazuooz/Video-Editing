"""Synthetic CPU-only supplementary preparation/capture/recovery fixtures.

Fake states/images are validator inputs, never actual native production proof.
No Editor, GPU, model, resource qualification or production staging is invoked.
"""
import copy,importlib.util,io,json,math,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock,patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
sp=importlib.util.spec_from_file_location('supplement_native_cpu_fixture',HERE/'run-prospect-refuge-supplement-native.py');n=importlib.util.module_from_spec(sp);sp.loader.exec_module(n);p=n.prep

class SupplementTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-supplement-cpu-');self.root=Path(self.tmp.name);self.c=p.read(p.SOURCE/'config.json');self.prov=dict(config=self.c,captureFingerprint='f'*64,validatorFingerprint='v'*64,project=str(self.root/'project'),physicalIdentity=dict(editorVersion='6000.6.0f1'),actualStagedMeta=[])
 def tearDown(self):self.tmp.cleanup()
 def write(self,path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf8');return path
 def mode(self,mode='scale',folder=None):
  folder=folder or self.root/mode;folder.mkdir(parents=True);(folder/'config.json').write_bytes((p.SOURCE/'config.json').read_bytes());scene=n.FOLDER+'/'+next(r['sceneFile']for r in self.c['scenes']if r['mode']==mode)
  receipt=dict(fingerprint=self.prov['captureFingerprint'],mode=mode,sourceKind='our-authored-illustration',configSHA256=n.sha(folder/'config.json'),frameConvention=self.c['frameConvention'],actualSceneSaved=True,actualScenePath=scene,**{k:v for k,v in n.CONTRACT.items()if k!='modes'});self.write(folder/'mode-contract.json',receipt);self.write(folder/'mode-complete.json',receipt)
  states=[];rays=[];anchors=[];previous=None;vertical=0.;shots=[]
  for frame in range(720):
   cmd=n.command_at(self.c,max(0,frame-1));jump=frame>0 and frame-1 in self.c['jumpFrames'];fire=frame>0 and frame-1 in self.c['fireFrames'];flags=0
   if mode in n.ENCOUNTERS:
    if frame:
     grounded=bool(previous['collisionFlags']&4)
     if grounded and vertical<0:vertical=n.f32(-.25)
     if grounded and jump:vertical=n.f32(self.c['jumpSpeed'])
     dt=n.f32(1/60);vertical=n.f32(vertical-n.f32(n.f32(self.c['gravity'])*dt));requested=dict(x=n.f32(previous['playerPosition']['x']+n.f32(n.f32(cmd['velocityX'])*dt)),y=n.f32(previous['playerPosition']['y']+n.f32(vertical*dt)),z=0.)
     position=dict(requested)
     if position['y']<0:position['y']=0.;flags=4
    else:position=requested=dict(x=-5.,y=0.,z=0.)
   else:position=requested=n.scripted_position(mode,frame)
   delta={k:position[k]-previous['playerPosition'][k]for k in'xyz'}if previous else dict(x=0.,y=0.,z=0.)
   ray=dict(id='synthetic-declared-ray',meaning='Synthetic fixture only',origin=dict(x=0.,y=1.,z=0.),desiredEndpoint=dict(x=0.,y=1.,z=2.),actualEndpoint=dict(x=0.,y=1.,z=2.),blocked=False,hitCollider=None,distance=2.)
   if mode in n.ENCOUNTERS and frame:
    teams=(['player']if fire else[])+(['enemy']if 150<=frame-1<600 and(frame-1)%120 in(30,42,54)else[])
    for team in teams:
     if team=='player':origin=dict(x=n.f32(position['x']+.5),y=n.f32(position['y']+1.),z=0.);velocity=dict(x=self.c['shotSpeed'],y=0.,z=0.)
     else:
      origin=dict(x=n.f32(4.8-.6),y=2. if mode=='boss'else n.f32(1.1),z=0.);target=dict(position);target['y']+=.95;aim={k:target[k]-origin[k]for k in'xyz'};length=math.sqrt(sum(v*v for v in aim.values()));velocity={k:n.f32(v/length*self.c['enemyShotSpeed'])for k,v in aim.items()}
     shots.append(dict(id='Own projectile '+str(len(shots)),team=team,previous=origin,position=origin,velocity=velocity,actualHitPoint=dict(x=0.,y=0.,z=0.),alive=True,hit=False,createdAtAppliedFrame=frame-1,hitAtFrame=-1,hitCollider=None))
    for shot in shots:
     if not shot['alive']:continue
     shot['previous']=dict(shot['position']);shot['position']={k:n.f32(shot['position'][k]+n.f32(shot['velocity'][k]*n.f32(1/60)))for k in'xyz'}
     if abs(shot['position']['x'])>11:shot['alive']=False
   s=dict(frame=frame,appliedCommandFrame=frame-1,collisionFlags=flags,timeSeconds=n.f32(frame/60),mode=mode,sourceKind='our-authored-illustration',phase=n.expected_phase(mode,frame,self.c),appliedCommandId='initial-state'if not frame else cmd['id']if mode in n.ENCOUNTERS else'scripted-geometric-illustration-route',motionKind='CharacterController.Move with exact shared run/jump/fire tape'if mode in n.ENCOUNTERS else'declared scripted geometric illustration route',playerPosition=position,requestedPlayerPosition=requested,actualMoveDelta=delta,enemyPosition=dict(x=4.8,y=0,z=0),secondEnemyPosition=dict(x=0,y=0,z=0),playerCameraEye=n.expected_camera_eye(mode,frame,position,self.c),playerCameraEuler=dict(x=0,y=0,z=0),observerCameraEye=self.c['observerPosition'],observerCameraEuler=dict(x=0,y=0,z=0),appliedJump=jump if mode in n.ENCOUNTERS else False,appliedFire=fire if mode in n.ENCOUNTERS else False,rays=[ray],projectiles=copy.deepcopy(shots));states.append(s);previous=s
   rays.append(dict(frame=frame,rays=[ray]));anchors.append(dict(frame=frame,anchors=[dict(id='fixture-body-head',role='Synthetic source-bound point',world=dict(x=0,y=1.55,z=0),playerViewport=dict(x=.5,y=.5,z=1),observerViewport=dict(x=.5,y=.5,z=1),active=True,playerInFrustum=True,observerInFrustum=True)]))
  for name,rows in[('states.jsonl',states),('rays.jsonl',rays),('projected-anchors.jsonl',anchors)]:(folder/name).write_text('\n'.join(json.dumps(r)for r in rows)+'\n',encoding='utf8')
  return folder
 def saved_scene_fixture(self,folder,mode='scale'):
  project=Path(self.prov['project']);workspace=self.root/'workspace';scene=n.FOLDER+'/'+next(r['sceneFile']for r in self.c['scenes']if r['mode']==mode);files=[];pins=[]
  for name in['Experiment.cs','Editor/EditorBuilder.cs','config.json',Path(scene).name]:
   path=project/n.FOLDER/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((p.SOURCE/'config.json').read_bytes()if name=='config.json'else b'SYNTHETIC CPU fixture, never Unity scene/source proof')
   row=dict(path=n.FOLDER+'/'+name,sha256=n.sha(path),bytes=path.stat().st_size);files.append(row)
   if name in['Experiment.cs','Editor/EditorBuilder.cs','config.json']:pins.append(dict(source='synthetic-only/'+name,target=row['path'],sha256=row['sha256']))
  dependencies=[]
  names=[n.SHADER,n.SHADER+'.meta']+['Assets/ThirdParty/KayKitAdventurers/'+name for name in['Knight.fbx','Knight.fbx.meta','knight_texture.png','knight_texture.png.meta','LICENSE.txt','LICENSE.txt.meta','provenance.json','provenance.json.meta']]
  for name in names:
   data=b'guid: '+b'a'*32+b'\n'if name.endswith('.meta')else b'SYNTHETIC shared bytes'
   for base in[project,workspace/'unity/VideoEditing']:
    path=base/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
   path=project/name;dependencies.append(dict(path=name,sha256=n.sha(path),bytes=path.stat().st_size))
  self.prov.update(sourcePins=pins,externalInputs=[],protocol=n.PROTOCOL,owner=n.OWNER)
  self.write(folder/'scene-record.json',dict(fingerprint=self.prov['captureFingerprint'],mode=mode,sourceKind='our-authored-illustration',actualSceneFilesSaved=True,scenePaths=[scene],unityVersion='6000.6.0f1',animationClipNames=['Idle','Walking_A'],files=files,dependencies=dependencies))
  for camera in n.CONTRACT['cameras']:
   for frame in range(720):
    path=folder/camera/f'{frame:04}.jpg';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'SYNTHETIC pixel fixture')
  return workspace
 def full_pixels(self):
  image=MagicMock();image.__enter__.return_value.size=(1920,1080);return patch('PIL.Image.open',return_value=image)
 def pixels(self,missing=None):
  return patch.object(Path,'glob',autospec=True,side_effect=lambda parent,pattern:[]if parent.name==missing else[parent/f'{f:04}.jpg'for f in range(720)])
 def mutate(self,folder,name,frame,change):
  path=folder/name;rows=[json.loads(line)for line in path.read_text().splitlines()];change(rows[frame]);path.write_text('\n'.join(json.dumps(row)for row in rows)+'\n')
 def test_thirteen_exact_scope_and_required_explicit_subset(self):
  self.assertEqual(len(p.MODES),13);p.validate_config(self.c);self.assertEqual(n.selected_modes('flying,shield,boss'),['flying','shield','boss'])
  for text in(None,'','all','scale,scale','../scale','flying,','other'):
   with self.subTest(text=text),self.assertRaises(AssertionError):n.selected_modes(text)
 def test_config_missing_mode_wrong_frame_or_tape_gap_rejected(self):
  for kind in('mode','frames','gap','camera'):
   c=copy.deepcopy(self.c)
   if kind=='mode':c['scenes'].pop()
   elif kind=='frames':c['frames']=600
   elif kind=='gap':c['encounterCommands'][1]['startFrame']+=1
   else:c['observerLookAt']=dict(c['observerPosition'])
   with self.subTest(kind=kind),self.assertRaises(AssertionError):p.validate_config(c)
 def test_scene_filename_traversal_and_nonfinite_config_rejected(self):
  for value in('../outside.unity','C:/bad.unity','scene.txt'):
   c=copy.deepcopy(self.c);c['scenes'][0]['sceneFile']=value
   with self.assertRaises(AssertionError):p.validate_config(c)
  c=copy.deepcopy(self.c);c['gravity']=float('nan')
  with self.assertRaises(AssertionError):p.validate_config(c)
 def test_verified_manifest_accepts_five_and_rejects_invented_text_package(self):
  path=self.write(self.root/'manifest.json',p.MANIFEST);p.validate_manifest(path);bad=copy.deepcopy(p.MANIFEST);bad['dependencies']['com.unity.modules.textrendering']='1.0.0';self.write(path,bad)
  with self.assertRaisesRegex(AssertionError,'verified five'):p.validate_manifest(path)
 def test_source_staging_requires_compile_and_correct_scoped_project(self):
  with self.assertRaises((KeyError,AssertionError)):p.stage(dict(staticCompilerPreflight=None))
  report=dict(staticCompilerPreflight={'compilerExitCode':0},fingerprint='f'*64,project=str(self.root/'outside'),files=[])
  with patch.object(p,'preflight',return_value=report),self.assertRaises(AssertionError):p.stage(report)
  self.assertFalse((self.root/'outside').exists())
 def test_temporary_only_staging_keeps_exact_verified_manifest(self):
  report=dict(staticCompilerPreflight={'compilerExitCode':0},fingerprint='f'*64,project=str(self.root/'unity-prospect-refuge-supplement-capture'/('f'*24)),files=[])
  with patch.object(p,'MEDIA',self.root),patch.object(p,'REPORT',self.root/'staging.json'),patch.object(p,'preflight',return_value=report):p.stage(report)
  self.assertEqual(p.read(Path(report['project'])/'Packages/manifest.json'),p.MANIFEST)
 def test_all_modes_scripted_routes_finite_and_encounter_control_distinct(self):
  for mode in set(p.MODES)-n.ENCOUNTERS:
   for f in(0,120,210,300,360,420,570,600,690,719):n.finite_vector(n.scripted_position(mode,f))
  self.assertEqual(n.scripted_position('footings',719)['x'],4.)
 def test_complete_synthetic_scripted_mode_positive(self):
  folder=self.mode()
  with self.pixels():summary=n.check_mode(folder,'scale',self.prov,decode=False)
  self.assertEqual(summary['frames'],720);self.assertFalse(summary['actualVisualReview'])
 def test_complete_synthetic_encounter_tape_gravity_and_fire_positive(self):
  folder=self.mode('boss')
  with self.pixels():summary=n.check_mode(folder,'boss',self.prov,decode=False)
  self.assertEqual(summary['motionKind'],'CharacterController.Move with exact shared run/jump/fire tape')
 def test_missing_frames_or_camera_and_wrong_decoded_dimensions_rejected(self):
  folder=self.mode()
  with self.pixels(missing='observer'),self.assertRaisesRegex(AssertionError,'camera frames'):n.check_mode(folder,'scale',self.prov,decode=False)
  image=MagicMock();image.__enter__.return_value.size=(1280,720)
  with self.pixels(),patch('PIL.Image.open',return_value=image),self.assertRaisesRegex(AssertionError,'FHD'):n.check_mode(folder,'scale',self.prov)
 def test_config_or_tape_hash_drift_rejected(self):
  folder=self.mode();(folder/'config.json').write_bytes((folder/'config.json').read_bytes()+b' ')
  with self.assertRaisesRegex(AssertionError,'provenance'):n.check_mode(folder,'scale',self.prov,decode=False)
 def test_completion_missing_or_wrong_mode_fingerprint_rejected(self):
  folder=self.mode();receipt=p.read(folder/'mode-complete.json');receipt['fingerprint']='wrong';self.write(folder/'mode-complete.json',receipt)
  with self.assertRaisesRegex(AssertionError,'completion'):n.check_mode(folder,'scale',self.prov,decode=False)
 def test_missing_state_and_wrong_clock_rejected(self):
  folder=self.mode();self.mutate(folder,'states.jsonl',0,lambda row:row.update(frame=1))
  with self.assertRaisesRegex(AssertionError,'unordered'):n.check_mode(folder,'scale',self.prov,decode=False)
 def test_scripted_position_and_collision_claim_drift_rejected(self):
  folder=self.mode();self.mutate(folder,'states.jsonl',100,lambda row:row.update(collisionFlags=4))
  with self.assertRaises(AssertionError):n.check_mode(folder,'scale',self.prov,decode=False)
 def test_encounter_command_jump_fire_or_requested_delta_drift_rejected(self):
  folder=self.mode('boss');self.mutate(folder,'states.jsonl',151,lambda row:row.update(appliedFire=False))
  with self.assertRaisesRegex(AssertionError,'tape differs'):n.check_mode(folder,'boss',self.prov,decode=False)
 def test_actual_move_recurrence_drift_rejected(self):
  folder=self.mode();self.mutate(folder,'states.jsonl',10,lambda row:row['actualMoveDelta'].update(x=1))
  with self.assertRaisesRegex(AssertionError,'recurrence'):n.check_mode(folder,'scale',self.prov,decode=False)
 def test_detached_ray_file_or_invalid_clipped_hit_rejected(self):
  folder=self.mode();self.mutate(folder,'rays.jsonl',20,lambda row:row['rays'][0].update(distance=99))
  with self.assertRaises(AssertionError):n.check_mode(folder,'scale',self.prov,decode=False)
  ray=dict(id='declared',meaning='test',origin=dict(x=0,y=1,z=0),desiredEndpoint=dict(x=0,y=1,z=2),actualEndpoint=dict(x=1,y=1,z=1),blocked=True,hitCollider='actual',distance=2)
  with self.assertRaisesRegex(AssertionError,'collinear'):n.check_ray(ray)
 def test_projectile_wrong_speed_and_fire_clock_rejected(self):
  shot=dict(id='Own projectile 0',team='player',createdAtAppliedFrame=150,previous=dict(x=0,y=1,z=0),position=dict(x=1,y=1,z=0),velocity=dict(x=99,y=0,z=0),actualHitPoint=dict(x=0,y=0,z=0),alive=True,hit=False,hitAtFrame=-1,hitCollider=None)
  with self.assertRaisesRegex(AssertionError,'speed'):n.check_projectiles([shot],151,[],self.c)
 def test_anchor_frustum_is_not_visibility_and_wrong_flag_rejected(self):
  folder=self.mode();self.mutate(folder,'projected-anchors.jsonl',30,lambda row:row['anchors'][0].update(playerInFrustum=False))
  with self.assertRaisesRegex(AssertionError,'Frustum'):n.check_mode(folder,'scale',self.prov,decode=False)
 def test_scene_export_path_traversal_and_wrong_subtree_rejected(self):
  for name in(n.FOLDER+'/../06-02/file',n.FOLDER+'//bad','Assets/foreign.unity','C:/outside'):
   with self.subTest(name=name),self.assertRaises(AssertionError):n.scoped_file(self.root,name)
  self.assertEqual(n.scoped_file(self.root,n.FOLDER+'.meta'),self.root/(n.FOLDER+'.meta'))
 def test_per_mode_saved_scene_record_required_and_unknown_dependency_blocked(self):
  folder=self.mode();self.write(folder/'scene-record.json',dict(fingerprint='f'*64,mode='scale',sourceKind='our-authored-illustration',actualSceneFilesSaved=False))
  with self.assertRaises(AssertionError):n.validate_scene_record(folder,'scale',self.prov)
 def test_completed_mode_snapshot_reused_after_only_qa_revision(self):
  self.prov['captureFingerprint']=n.digest(self.prov['physicalIdentity']);attempt=self.root/'attempts/one';folder=self.mode(folder=attempt/'capture/scale');workspace=self.saved_scene_fixture(folder)
  with patch.object(n,'ROOT',workspace),self.full_pixels():first=n.mode_proof(folder,'scale',self.prov,freeze=True)
  self.write(attempt/'input-provenance.json',self.prov);new=copy.deepcopy(self.prov);new['validatorFingerprint']='c'*64
  with patch.object(n,'ROOT',workspace),patch.object(n,'ATTEMPTS',self.root/'attempts'),self.full_pixels(),patch.object(n.subprocess,'Popen',side_effect=AssertionError('Never recapture forQA revision')):found,rejected=n.inventory(new,freeze=True)
  self.assertEqual(set(found),{'scale'});self.assertFalse(rejected);self.assertEqual(found['scale']['captureFingerprint'],first['captureFingerprint']);self.assertNotEqual(found['scale']['validatorFingerprint'],first['validatorFingerprint'])
 def test_missing_shared_dependency_or_changed_scene_source_rejected(self):
  folder=self.mode();workspace=self.saved_scene_fixture(folder);path=folder/'scene-record.json';record=p.read(path);old=copy.deepcopy(record);record['dependencies'].pop();self.write(path,record)
  with patch.object(n,'ROOT',workspace),self.assertRaisesRegex(AssertionError,'dependencies'):n.validate_scene_record(folder,'scale',self.prov)
  self.write(path,old);source=Path(self.prov['project'])/old['scenePaths'][0];source.write_bytes(b'changed source')
  with patch.object(n,'ROOT',workspace),self.assertRaisesRegex(AssertionError,'changed'):n.validate_scene_record(folder,'scale',self.prov)
 def test_completed_frozen_frame_tamper_never_silently_reused(self):
  folder=self.mode();workspace=self.saved_scene_fixture(folder)
  with patch.object(n,'ROOT',workspace),self.full_pixels():n.mode_proof(folder,'scale',self.prov,freeze=True)
  (folder/'player/0000.jpg').write_bytes(b'changed')
  with patch.object(n,'ROOT',workspace),self.full_pixels(),self.assertRaisesRegex(AssertionError,'Immutable completed frame'):n.mode_proof(folder,'scale',self.prov,freeze=False)
 def test_foreign_or_unknown_lease_is_never_recovered(self):
  lease=self.write(self.root/'lease.json',dict(protocol='foreign',owner='foreign',token='x',pid=1,createTime=1));old=lease.read_bytes();self.assertFalse(n.core.runtime.recover_own_lease({'x'},lease,lambda r:False,lambda r:False));self.assertEqual(lease.read_bytes(),old)
 def test_live_child_preserves_own_lease(self):
  lease=self.write(self.root/'lease.json',dict(protocol=n.PROTOCOL,owner=n.OWNER,token='x',pid=1,createTime=1,phase='running',child=dict(pid=2,createTime=2)))
  self.assertFalse(n.core.runtime.recover_own_lease({'x'},lease,lambda r:bool(r and r.get('pid')==2),lambda r:False));self.assertTrue(lease.exists())
 def test_separate_singleton_rejects_main_or_live_owner(self):
  marker=self.write(self.root/'worker.json',dict(protocol='architectural111-06-02-native-v1',owner='architectural-111-06-02-native',token='old',pid=1,createTime=1));old=marker.read_bytes()
  with self.assertRaises(RuntimeError):n.core.runtime.SingleWorker(marker,is_alive=lambda r:False).acquire()
  self.assertEqual(marker.read_bytes(),old)
 def test_dead_own_singleton_only_is_recovered(self):
  marker=self.write(self.root/'worker.json',dict(protocol=n.PROTOCOL,owner=n.OWNER,token='old',pid=1,createTime=1,child=None));w=n.core.runtime.SingleWorker(marker,is_alive=lambda r:False).acquire()
  try:self.assertEqual(w.previous['token'],'old');self.assertEqual(w.record['owner'],n.OWNER)
  finally:w.close()
 def test_default_no_stage_gpu_or_queue_without_explicit_modes(self):
  with patch.object(sys,'argv',['run-supplement']),patch.object(n,'authorize',side_effect=AssertionError('Mustrejectmodefirst')),patch.object(n.subprocess,'Popen',side_effect=AssertionError('Nojob')),patch('sys.stdout',new_callable=io.StringIO)as output:n.main()
  self.assertFalse(json.loads(output.getvalue())['ready'])
 def test_subset_completion_cannot_claim_all_thirteen(self):
  partial={mode:{}for mode in['flying','shield','boss']};self.assertFalse(set(partial)==set(n.MODES))
  with patch.object(n,'export_modes',return_value=[]),patch.object(n,'EVIDENCE',self.root/'evidence.json'):
   result=n.publish_native_evidence(partial,{**self.prov,'preparationFingerprint':'p'},['flying','shield','boss'],[])
  self.assertTrue(result['selectedSubsetComplete']);self.assertFalse(result['fullSupplementaryCaptureComplete']);self.assertFalse(result['voicePreparationAllowed'])
 def test_expanded_mode_scope_does_not_inherit_unseen_visual_approval(self):
  path=self.write(self.root/'evidence.json',dict(captureFingerprint='f'*64,completedModes=['flying'],actualVisualReview=True,humanApproval=True,voicePreparationAllowed=True,platformActions=[]))
  with patch.object(n,'export_modes',return_value=[]),patch.object(n,'EVIDENCE',path):result=n.publish_native_evidence(dict(flying={},shield={}),{**self.prov,'preparationFingerprint':'p'},['shield'],[])
  self.assertFalse(result['actualVisualReview']);self.assertFalse(result['humanApproval']);self.assertTrue(result['priorReviewScopes'][0]['humanApproval'])
 def test_source_requests_fresh_capture_subdir_and_pins_base_guards(self):
  source=Path(n.__file__).read_text();self.assertIn("capture=attempt/'capture';assert not capture.exists()",source);self.assertIn("'-logFile',str(attempt/'unity.log')",source);self.assertIn('core.busy_reason(token)',source);self.assertIn('core.runtime.unrecorded_child_alive(lease)',source)

if __name__=='__main__':unittest.main(verbosity=2)
