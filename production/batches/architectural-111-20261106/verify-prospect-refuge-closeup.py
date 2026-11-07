"""CPU-only derivative provenance/clock/projection/recovery tests.
Synthetic closeup fixtures copy existing accepted state data, calculate mockcamera
projections and mockpixels; they are NOT actual replay/capture/visibility proof.
"""
import copy,hashlib,importlib.util,json,math,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock,patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
sp=importlib.util.spec_from_file_location('closeup_cpu_fixture',HERE/'run-prospect-refuge-closeup.py');r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r);prep=r.prep
class CloseupTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-closeup-cpu-');self.base=Path(self.tmp.name);self.config=prep.read(prep.SOURCE/'closeup-config.json')
 def tearDown(self):self.tmp.cleanup()
 def write(self,p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v),encoding='utf8');return p
 def first(self):return json.loads((Path(prep.read(prep.EVIDENCE)['output'])/'baseline/states.jsonl').read_text().splitlines()[0])
 def fixture(self):
  main=Path(prep.read(prep.EVIDENCE)['output']);mode='baseline';folder=self.base/mode;folder.mkdir();reference=dict(mainAttempt=str(main),mainFingerprint=prep.read(prep.EVIDENCE)['fingerprint'],modes=[dict(mode=m,statesSHA256=prep.sha(main/m/'states.jsonl'))for m in['baseline','shifted']]);stage=self.write(self.base/'stage.json',dict(mainReference=reference));raw=(main/mode/'states.jsonl').read_text();(folder/'states.jsonl').write_text(raw);states=[json.loads(x)for x in raw.splitlines()];config=prep.read(main/mode/'capture-config.json');projections=[]
  def dot(a,b):return sum(x*y for x,y in zip(a,b))
  def cross(a,b):return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
  def norm(v):length=math.sqrt(dot(v,v));return[x/length for x in v]
  for f,s in enumerate(states):
   pos={k:r.f32(r.f32(v)+r.f32(self.config['cameraOffset'][k]))for k,v in s['playerPosition'].items()};focus={k:r.f32(r.f32(v)+r.f32(self.config['lookOffset'][k]))for k,v in s['playerPosition'].items()};forward=norm([focus[k]-pos[k]for k in'xyz']);right=norm(cross([0,1,0],forward));up=cross(forward,right);cot=1/math.tan(math.radians(32)/2);matrix=[]
   for axis,scale in[(right,cot/(16/9)),(up,cot),(forward,1),(forward,1)]:matrix += [v*scale for v in axis]+[-dot(axis,list(pos.values()))*scale]
   points={'player-ground':s['playerPosition'],'main-player-camera-eye':s['playerCameraEye'],'enemy-eye':s['enemyEye']}
   for ray in s['bodyRays']:points['body-'+ray['id']]=ray['desiredEndpoint'];points['enemy-ray-'+ray['id']+'-actual-end']=ray['actualEndpoint']
   for which in['first','second']:
    center=dict(config[which+'CoverCenter']);size=config[which+'CoverSize']['y']
    for name,sign in[('top',1),('bottom',-1)]:v=dict(center);v['y']+=sign*size*.5;points[which+'-cover-'+name]=v
   anchors=[]
   for name,p in points.items():
    delta=[p[k]-pos[k]for k in'xyz'];depth=dot(delta,forward);v=dict(x=.5+.5*dot(delta,right)*cot/(16/9)/depth,y=.5+.5*dot(delta,up)*cot/depth,z=depth);anchors.append(dict(id=name,world=p,viewport=v,environmentBlocked=False,actualCameraRayEndpoint=p,hitCollider=None,inFrustum=.04<depth<80 and 0<=v['x']<=1 and 0<=v['y']<=1))
   projections.append(dict(frame=f,mainSourceFrame=f,position=pos,forward=dict(zip('xyz',forward)),focus=focus,fieldOfView=32.,nearClip=.04,farClip=80.,mainPlayerAspect=16/9,mainObserverAspect=16/9,viewProjectionRowMajor=matrix,anchors=anchors))
  (folder/'projected-anchors.jsonl').write_text('\n'.join(json.dumps(x)for x in projections)+'\n');self.write(folder/'mode-complete.json',dict(fingerprint='f'*64,mainFingerprint=reference['mainFingerprint'],mode=mode,frames=600,fps=60,width=1920,height=1080,camera='closeup',statesCompared=600,allSharedStatesEqual=True,mainStatesSHA256=reference['modes'][0]['statesSHA256'],closeupConfigSHA256=prep.sha(prep.SOURCE/'closeup-config.json'),comparisonPolicy=self.config['comparisonPolicy']))
  scene=prep.FOLDER+'/S02-ProspectRefuge-Closeup-Baseline.unity';project=self.base/'source-stage';files=[]
  items={scene:b'Synthetic editable scene; not a native capture',scene+'.meta':b'guid: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n'}
  for name in['ProspectRefugeCloseupCamera.cs','Editor/ProspectRefugeCloseupBuilder.cs','closeup-config.json','main-reference.json']:
   rel=prep.FOLDER+'/'+name;items[rel]=(prep.SOURCE/name).read_bytes()if name!='main-reference.json'else json.dumps(reference).encode();items[rel+'.meta']=('guid: '+hashlib.md5(rel.encode()).hexdigest()+'\n').encode()
  for rel,data in items.items():
   src=project/rel;src.parent.mkdir(parents=True,exist_ok=True);src.write_bytes(data);snapshot=folder/r.snapshot_relative(rel);snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(data);files.append(dict(path=rel,snapshotRelativePath=r.snapshot_relative(rel),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
  self.write(folder/'mode-scene-record.json',dict(fingerprint='f'*64,mainFingerprint=reference['mainFingerprint'],mode=mode,scenePath=scene,mainSourceFrame=0,actualSceneFilesSaved=True,files=files))
  return folder,stage
 def pixel_mocks(self):
  image=MagicMock();image.__enter__.return_value.size=(1920,1080)
  return patch('PIL.Image.open',return_value=image),patch.object(Path,'glob',autospec=True,side_effect=lambda parent,pattern:[parent/f'{i:04}.jpg'for i in range(600)])
 def test_exact_shared_state_permits_only_native_entity_identity(self):
  a=self.first();b=copy.deepcopy(a)
  for ray in b['bodyRays']:ray['hitColliderEntityId']='new-native-id'if ray['blocked']else''
  r.equal_state(a,b)
 def test_changed_player_camera_observer_input_or_body_sample_rejected(self):
  a=self.first()
  for key in('playerPosition','playerCameraEye','observerCameraPosition','appliedVelocity'):
   b=copy.deepcopy(a);b[key]['x']+=.01
   with self.subTest(key=key),self.assertRaises(AssertionError):r.equal_state(a,b)
  b=copy.deepcopy(a);b['bodyRays'][0]['blocked']=not b['bodyRays'][0]['blocked']
  with self.assertRaises(AssertionError):r.equal_state(a,b)
 def test_state_key_type_and_clock_aliases_rejected(self):
  a=self.first()
  for change in('extra','boolframe','missing'):
   b=copy.deepcopy(a)
   if change=='extra':b['new']=0
   elif change=='boolframe':b['frame']=False
   else:del b['observerCameraPosition']
   with self.subTest(change=change),self.assertRaises(AssertionError):r.equal_state(a,b)
 def test_exact_four_source_compiler_receipt(self):
  current=prep.preflight();proof=prep.read(prep.COMPILER);prep.validate_compiler(proof,current['files'])
  for change in('empty','missing','stale','extra'):
   c=copy.deepcopy(proof)
   if change=='empty':c['sourceHashes']={}
   elif change=='missing':del c['sourceHashes'][next(iter(c['sourceHashes']))]
   elif change=='stale':c['sourceHashes'][next(iter(c['sourceHashes']))]='0'*64
   else:c['sourceHashes']['extra.cs']='0'*64
   with self.subTest(change=change),self.assertRaises(AssertionError):prep.validate_compiler(c,current['files'])
 def test_decline_bad_source_before_any_stage_write(self):
  with patch.object(prep,'PROJECT_ROOT',self.base/'projects'),patch.object(prep,'REPORT',self.base/'stage.json'):
   current=prep.preflight();current['files'][0]['sha256']='0'*64
   with self.assertRaises(AssertionError):prep.stage(current)
  self.assertFalse((self.base/'projects').exists());self.assertFalse((self.base/'stage.json').exists())
 def test_source_scope_rejects_traversal_or_another_episode(self):
  for path in('Assets/VideoScenes/architectural-111-20261106/06-02/../07-04/file','Assets/elsewhere/file','C:/outside/file'):
   with self.subTest(path=path),self.assertRaises(AssertionError):prep.owned_main(path)
 def test_synthetic_projection_receipt_positive_without_native_pixels(self):
  folder,stage=self.fixture();a,b=self.pixel_mocks()
  with patch.object(r,'PREP',stage),patch.object(r,'PROJECT',self.base/'source-stage'),a,b:self.assertEqual(len(r.check_mode(self.base,'baseline','f'*64,self.config)),600)
 def test_changed_projection_and_wrong_capture_identity_rejected(self):
  folder,stage=self.fixture()
  with patch.object(r,'PREP',stage),patch.object(r,'PROJECT',self.base/'source-stage'),self.assertRaisesRegex(AssertionError,'receipt'):r.check_mode(self.base,'baseline','bad',self.config)
  file=folder/'projected-anchors.jsonl';rows=[json.loads(x)for x in file.read_text().splitlines()];rows[0]['anchors'][0]['viewport']['x']+=.1;file.write_text('\n'.join(json.dumps(x)for x in rows)+'\n')
  with patch.object(r,'PREP',stage),patch.object(r,'PROJECT',self.base/'source-stage'),self.assertRaisesRegex(AssertionError,'projection'):r.check_mode(self.base,'baseline','f'*64,self.config)
 def test_per_mode_scene_proof_missing_tampered_mode_or_fp_rejected(self):
  folder,stage=self.fixture();proof=folder/'mode-scene-record.json';original=proof.read_bytes();payload=json.loads(original)
  for change in['missing','snapshot','wrong-mode','wrong-fp']:
   proof.write_bytes(original)
   if change=='missing':proof.unlink()
   elif change=='snapshot':
    item=payload['files'][0];(folder/item['snapshotRelativePath']).write_bytes(b'tampered')
   else:
    changed=copy.deepcopy(payload);changed['mode'if change=='wrong-mode'else'fingerprint']='wrong';proof.write_text(json.dumps(changed))
   with self.subTest(change=change),patch.object(r,'PREP',stage),patch.object(r,'PROJECT',self.base/'source-stage'),self.assertRaises((AssertionError,FileNotFoundError)):r.check_mode(self.base,'baseline','f'*64,self.config)
   if change=='snapshot':
    item=payload['files'][0];(folder/item['snapshotRelativePath']).write_bytes((self.base/'source-stage'/item['path']).read_bytes())
 def test_actual_main_serialized_empty_and_raw_null_remain_distinct(self):
  original=self.first();ray=next(x for x in original['bodyRays']if not x['blocked']);self.assertEqual(ray['hitCollider'],'')
  source=(HERE/'prospect-refuge-unity-source/ProspectRefugeExperiment.cs').read_text();self.assertIn('hitCollider=blocked?hit.collider.name:null',source)
  raw=copy.deepcopy(original);next(x for x in raw['bodyRays']if not x['blocked'])['hitCollider']=None
  with self.assertRaises(AssertionError):r.equal_state(original,raw)
  serialized=json.loads(json.dumps(original));r.equal_state(original,serialized)
  builder=(prep.SOURCE/'Editor/ProspectRefugeCloseupBuilder.cs').read_text()
  self.assertIn('string stateJson=JsonUtility.ToJson(rig.CurrentState);',builder)
  self.assertIn('Same(JsonUtility.FromJson<FrameState>(originalLines[frame]),JsonUtility.FromJson<FrameState>(stateJson),"FrameState")',builder)
  self.assertIn('states.WriteLine(stateJson);',builder)
 def test_blocked_nonempty_collider_name_is_not_an_alias(self):
  original=self.first();changed=copy.deepcopy(original);blocked=next(x for x in changed['bodyRays']if x['blocked']);self.assertTrue(blocked['hitCollider']);blocked['hitCollider']='wrong-blocked-cover'
  with self.assertRaises(AssertionError):r.equal_state(original,changed)
 def test_fingerprint_projects_never_refresh_legacy_project(self):
  a=prep.project_for('a'*64);b=prep.project_for('b'*64);self.assertNotEqual(a,b);self.assertTrue(a.is_relative_to(prep.PROJECT_ROOT.resolve()))
  self.assertNotEqual(a,prep.MEDIA/'unity-prospect-refuge-closeup')
  for bad in('short','../'+'a'*61,'A'*64):
   with self.subTest(bad=bad),self.assertRaises(AssertionError):prep.project_for(bad)
 def test_flat_snapshot_names_are_path_hashes_not_content_or_traversal(self):
  path=prep.FOLDER+'/S02-ProspectRefuge-Closeup-Baseline.unity.meta';expected='editable/'+hashlib.sha256(path.encode('utf8')).hexdigest()+'.bin';self.assertEqual(r.snapshot_relative(path),expected);self.assertEqual(len(expected),77)
  folder,stage=self.fixture();proof=folder/'mode-scene-record.json';original=json.loads(proof.read_text())
  for kind in('nested','traversal','duplicate'):
   payload=copy.deepcopy(original)
   if kind=='nested':payload['files'][0]['snapshotRelativePath']='editable-source/'+payload['files'][0]['path']
   elif kind=='traversal':payload['files'][0]['snapshotRelativePath']='editable/../wrong.bin'
   else:payload['files'].append(copy.deepcopy(payload['files'][0]))
   proof.write_text(json.dumps(payload))
   with self.subTest(kind=kind),patch.object(r,'PREP',stage),patch.object(r,'PROJECT',self.base/'source-stage'),self.assertRaises(AssertionError):r.check_mode(self.base,'baseline','f'*64,self.config)
 def test_windows_separator_is_canonical_before_scene_filter(self):
  builder=(prep.SOURCE/'Editor/ProspectRefugeCloseupBuilder.cs').read_text();self.assertLess(builder.index("string canonical=path.Replace"),builder.index('if((canonical.EndsWith'))
  canonical=prep.FOLDER+'/S02-ProspectRefuge-Closeup-Baseline.unity';raw=prep.FOLDER+'\\S02-ProspectRefuge-Closeup-Baseline.unity';self.assertNotEqual(raw,canonical);self.assertEqual(raw.replace('\\','/'),canonical)
 def test_original_camera_aspect_restoration_and_mismatch_rejection(self):
  source=(prep.SOURCE/'Editor/ProspectRefugeCloseupBuilder.cs').read_text();self.assertIn('RestoreSourceAspect(rig);rig.ResetExperiment()',source)
  follow=(prep.SOURCE/'ProspectRefugeCloseupCamera.cs').read_text();self.assertIn('rig.playerCamera.aspect=aspect;rig.observerCamera.aspect=aspect;',follow)
  folder,stage=self.fixture();f=folder/'projected-anchors.jsonl';rows=[json.loads(x)for x in f.read_text().splitlines()];rows[0]['mainPlayerAspect']=4/3;f.write_text('\n'.join(json.dumps(x)for x in rows)+'\n')
  with patch.object(r,'PREP',stage),patch.object(r,'PROJECT',self.base/'source-stage'),self.assertRaisesRegex(AssertionError,'aspect'):r.check_mode(self.base,'baseline','f'*64,self.config)
 def test_isolated_protocol_and_exact_folder(self):
  self.assertEqual(r.n.runtime.PROTOCOL,'architectural111-06-02-closeup-v1');self.assertEqual(r.n.runtime.OWNER,'architectural-111-06-02-closeup');self.assertEqual(r.n.FOLDER,prep.FOLDER);self.assertNotEqual(r.n.WORKER,prep.MEDIA/'06-02-native-worker.json')
 def test_foreign_and_live_gap_lease_preserved(self):
  f=self.write(self.base/'lease.json',dict(protocol='foreign',owner='other',token='t',pid=1,createTime=1,phase='reserved'))
  self.assertFalse(r.n.runtime.recover_own_lease({'t'},f,lambda x:False,lambda x:False));self.assertTrue(f.exists())
  self.write(f,dict(protocol=r.PROTOCOL,owner=r.OWNER,token='t',pid=1,createTime=1,phase='launching',fingerprint='f',output='out'))
  self.assertFalse(r.n.runtime.recover_own_lease({'t'},f,lambda x:False,lambda x:True));self.assertTrue(f.exists())
 def test_no_gpu_or_implicit_stage_default(self):
  with patch.object(r.n,'main')as main,patch.object(sys,'argv',['closeup']):r.main();main.assert_called_once()
  with patch.object(sys,'argv',['closeup','--adopt-attempt','foreign']),self.assertRaises(SystemExit):r.main()
if __name__=='__main__':unittest.main(verbosity=2)
