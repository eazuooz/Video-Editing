"""CPU-only synthetic correction contract fixtures; no Unity/resource query."""
from __future__ import annotations
import copy,hashlib,importlib.util,json,math,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('test_corrections_native',HERE/'run-prospect-refuge-corrections-native.py');n=importlib.util.module_from_spec(sp);sp.loader.exec_module(n)
p=n.prep

def dump(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False)+'\n',encoding='utf8');return path

def cross(a,b):return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def euler(forward):return dict(x=n.f32(math.degrees(-math.asin(max(-1.,min(1.,forward[1]))))%360),y=n.f32(math.degrees(math.atan2(forward[0],forward[2]))%360),z=0.)
def camera(eye,forward,fov=55):
 right=n.unit(cross([0.,1.,0.],forward));up=cross(forward,right);cot=1/math.tan(math.radians(fov/2));scales=[cot/(16/9),cot,1.,1.];bases=[right,up,forward,forward];matrix=[]
 for axis,scale in zip(bases,scales):matrix.extend([scale*x for x in axis]+[-scale*sum(axis[i]*n.xyz(eye)[i]for i in range(3))])
 return dict(position=eye,forward=dict(zip('xyz',forward)),fieldOfView=fov,aspect=n.f32(16/9),nearClip=n.f32(.04),farClip=80.,viewProjectionRowMajor=matrix)
def projected(world,c):
 delta=[world[k]-c['position'][k]for k in'xyz'];z=sum(x*y for x,y in zip(delta,n.xyz(c['forward'])));v=n.xyz(world)+[1.];clip=[sum(c['viewProjectionRowMajor'][i*4+j]*v[j]for j in range(4))for i in range(4)]
 return dict(x=.5+.5*clip[0]/clip[3],y=.5+.5*clip[1]/clip[3],z=z)if abs(z)>1e-8 else dict(x=0.,y=0.,z=z)
def ray(c,world):return dict(origin=c['position'],desiredEndpoint=world,actualEndpoint=world,blocked=False,hitCollider=None)

class CorrectionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.current=p.preflight();cls.config=cls.current['config'];cls.originals={m:n.lines(cls.current['sourceModes'][m]['states']['path'])for m in p.MODES};cls.anchors={m:n.lines(cls.current['sourceModes'][m]['anchors']['path'])for m in p.MODES}
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.prov=dict(captureFingerprint='f'*64,validatorFingerprint='e'*64,config=self.config,sourceReference=self.current['sourceReference'],sourceReferenceSHA256=self.current['sourceReferenceSHA256'],sourceModes=self.current['sourceModes'],sourcePins=self.current['files'],generatedPins=self.current['generatedFiles'],actualStagedMeta=[],project=str(self.root/'project'))
 def make_mode(self,mode):
  folder=self.root/mode;folder.mkdir();(folder/'config.json').write_bytes((p.SOURCE/'config.json').read_bytes());(folder/'source-reference.json').write_bytes(self.current['generatedFiles'][0]['contentUtf8'].encode('utf8'))
  ref=next(r for r in self.prov['sourceReference']['modes']if r['mode']==mode);receipt=dict(fingerprint=self.prov['captureFingerprint'],sourceCaptureFingerprint=p.SOURCE_CAPTURE,mode=mode,sourceKind=n.KIND,actualScenePath=n.FOLDER+'/'+next(r['sceneFile']for r in self.config['scenes']if r['mode']==mode),actualSceneSaved=True,frames=720,fps=60,width=1920,height=1080,cameras=['player','observer'],configSHA256=n.sha(folder/'config.json'),sourceReferenceSHA256=self.prov['sourceReferenceSHA256'],frameConvention=self.config['frameConvention'],**{k:v for k,v in ref.items()if k!='mode'})
  dump(folder/'mode-contract.json',receipt);dump(folder/'mode-complete.json',receipt);states=[];rays=[];anchors=[];route=[];previous=None
  for f,(o,oa)in enumerate(zip(self.originals[mode],self.anchors[mode])):
   pos={k:n.f32(v)for k,v in self.config['atriumPlayerPosition'].items()}if mode=='atrium'else o['playerPosition'];eye=dict(pos);eye['y']=n.f32(eye['y']+n.f32(1.65));body=[0.,0.,1.]
   if mode=='scale':eye=self.config['scaleCameraPosition'];forward=n.direction(eye,self.config['scaleCameraTarget'])
   elif mode=='atrium':forward=n.direction(eye,self.config['atriumLookAt']);body=n.direction({**pos,'y':0.},{**self.config['atriumLookAt'],'y':0.})
   else:
    eye=o['playerCameraEye'];forward=n.euler_forward(o['playerCameraEuler'])
    if mode=='courtyard'and f>=600:
     t=min(1.,n.f32((f-600)/90));forward=n.slerp_direction(forward,n.direction(eye,self.config['courtyardReobserveTarget']),t);body=n.slerp_direction(body,n.direction({**pos,'y':0.},{**self.config['courtyardReobserveTarget'],'y':0.}),t)
   point=dict(pos);point['y']=n.f32(point['y']+n.f32(.035))
   if not route or n.dist(route[-1],point)**2>1e-12:route.append(point)
   s=dict(frame=f,sourceClockFrame=f,appliedCommandFrame=f-1,timeSeconds=n.f32(f/60),mode=mode,sourceKind=n.KIND,correction=next(r['correction']for r in self.config['scenes']if r['mode']==mode),phase=n.expected_phase(mode,f),motionKind='stationary actor; original NPC clock'if mode=='atrium'else'declared scripted geometric illustration; corrected camera',playerPosition=pos,requestedPlayerPosition=pos,actualMoveDelta={k:n.f32(pos[k]-previous['playerPosition'][k])if previous else 0. for k in'xyz'},playerEuler=euler(body),enemyPosition=o['enemyPosition'],secondEnemyPosition=o['secondEnemyPosition'],playerCameraEye=eye,playerCameraEuler=euler(forward),observerCameraEye=o['observerCameraEye'],observerCameraEuler=o['observerCameraEuler'],routePointCount=len(route),rays=o['rays'],commercialImplementationMeasured=False,safetyMeasured=False,wholeMeshVisibilityMeasured=False)
   pc=camera(eye,forward,38 if mode=='scale'else 55);oc=camera(o['observerCameraEye'],n.euler_forward(o['observerCameraEuler']));aa=[]
   for source in oa['anchors']:
    world=source['world']
    if mode=='atrium'and source['id']in('player-head','player-torso','enclosed-loft'):
     world=dict(pos);world['y']=n.f32(pos['y']+n.f32({'player-head':1.55,'player-torso':.95,'enclosed-loft':.8}[source['id']]))
    aa.append(dict(id=source['id'],role=source['role'],active=source['active'],world=world))
   if mode=='refuge':aa.extend(dict(id=k,role='Synthetic additive test anchor',active=True,world=v)for k,v in dict(n.extra_world(self.config),**{'original-exterior-overhang-center':dict(x=0.,y=2.7,z=1.8)}).items())
   for a in aa:
    for prefix,c in(('player',pc),('observer',oc)):
     v=projected(a['world'],c);a[prefix+'Viewport']=v;a[prefix+'InFrustum']=c['nearClip']<v['z']<c['farClip']and 0<=v['x']<=1 and 0<=v['y']<=1;a[prefix+'CameraRay']=ray(c,a['world'])
   states.append(s);rays.append(dict(frame=f,rays=s['rays']));anchors.append(dict(frame=f,playerCamera=pc,observerCamera=oc,anchors=aa));previous=s
  for name,rows in[('states.jsonl',states),('rays.jsonl',rays),('projected-anchors.jsonl',anchors)]:(folder/name).write_text('\n'.join(json.dumps(r)for r in rows)+'\n',encoding='utf8')
  dump(folder/'corrected-route.json',dict(mode=mode,sourceKind=n.KIND,physicallySolved=False,points=route));return folder
 def pixels(self,missing=None):return patch.object(Path,'glob',autospec=True,side_effect=lambda parent,pattern:[]if parent.name==missing else[parent/f'{f:04}.jpg'for f in range(720)])
 def change(self,folder,name,f,fn):
  rows=n.lines(folder/name);fn(rows[f]);(folder/name).write_text('\n'.join(json.dumps(r)for r in rows)+'\n')
 def scene_fixture(self,mode='scale'):
  folder=self.root/('scene-fixture-'+mode);folder.mkdir();scene=n.FOLDER+'/'+next(r['sceneFile']for r in self.config['scenes']if r['mode']==mode);ref=next(r for r in self.prov['sourceReference']['modes']if r['mode']==mode)
  wanted=[ref['sourceScenePath'],ref['sourceScenePath']+'.meta',n.OLD_FOLDER+'/Experiment.cs',n.OLD_FOLDER+'/Experiment.cs.meta',n.FOLDER+'/CorrectionDriver.cs',n.FOLDER+'/Editor/CorrectionBuilder.cs',n.FOLDER+'/config.json',n.SHADER,n.SHADER+'.meta']+['Assets/ThirdParty/KayKitAdventurers/'+name for name in('Knight.fbx','Knight.fbx.meta','knight_texture.png','knight_texture.png.meta')]
  sources={r['target']:Path(r['source']).read_bytes()for r in self.prov['sourcePins']if r['target']in wanted};sources[n.FOLDER+'/source-reference.json']=self.current['generatedFiles'][0]['contentUtf8'].encode();sources[scene]=b'SYNTHETIC editable scene, never native evidence';sources[scene+'.meta']=('guid: '+hashlib.sha256(('synthetic-new-scene-'+mode).encode()).hexdigest()[:32]+'\n').encode();sources[n.FOLDER+'/CorrectionDriver.cs.meta']=b'guid: '+b'e'*32+b'\n';staged=Path(self.prov['project'])/(n.FOLDER+'/CorrectionDriver.cs.meta');staged.parent.mkdir(parents=True,exist_ok=True);staged.write_bytes(sources[n.FOLDER+'/CorrectionDriver.cs.meta']);sources[n.FOLDER+'.meta']=b'folderAsset: yes\nguid: '+b'b'*32+b'\n';rootmeta=Path(self.prov['project'])/(n.FOLDER+'.meta');rootmeta.parent.mkdir(parents=True,exist_ok=True);rootmeta.write_bytes(sources[n.FOLDER+'.meta']);rows=[]
  for name,data in sources.items():
   relative='editable/'+hashlib.sha256(name.encode()).hexdigest()+'.bin';f=folder/relative;f.parent.mkdir(exist_ok=True);f.write_bytes(data);rows.append(dict(path=name,sha256=n.sha(f),bytes=len(data),snapshotRelativePath=relative))
  geometry=[]
  if mode=='refuge':
   assets={}
   for name in('Meshes/SectionalInteriorCeiling.asset','Materials/SectionalInteriorCeiling.mat'):
    canonical=n.FOLDER+'/'+name;relative='editable/'+hashlib.sha256(canonical.encode()).hexdigest()+'.bin';actual=folder/relative;actual.write_bytes(b'SYNTHETIC ceiling asset');rows.append(dict(path=canonical,sha256=n.sha(actual),bytes=actual.stat().st_size,snapshotRelativePath=relative));assets[name]=n.sha(actual)
   geometry=[dict(id='interior-ceiling',colliderLayer=26,actualColliderWorldMin=dict(x=-3.,y=1.65,z=-5.),actualColliderWorldMax=dict(x=3.,y=1.75,z=-1.),actualMeshWorldMin=dict(x=-3.,y=1.65,z=-5.),actualMeshWorldMax=dict(x=3.,y=1.65,z=-1.),playerFootPoint=dict(x=0.,y=-.65,z=-2.),ceilingAbovePlayerPoint=dict(x=0.,y=1.65,z=-2.),originalExteriorOverhangWorldMin=dict(x=-3.3,y=2.575,z=.6),originalExteriorOverhangWorldMax=dict(x=3.3,y=2.825,z=3.),meshAssetPath=n.FOLDER+'/Meshes/SectionalInteriorCeiling.asset',meshAssetSHA256=assets['Meshes/SectionalInteriorCeiling.asset'],materialAssetPath=n.FOLDER+'/Materials/SectionalInteriorCeiling.mat',materialAssetSHA256=assets['Materials/SectionalInteriorCeiling.mat'])]
  record=dict(fingerprint=self.prov['captureFingerprint'],sourceCaptureFingerprint=p.SOURCE_CAPTURE,mode=mode,sourceKind=n.KIND,unityVersion='6000.6.0f1',actualSceneFilesSaved=True,savedAtFrame=0,scenePaths=[scene],files=rows,additiveGeometry=geometry)
  dump(folder/'scene-record.json',record);return folder,record
 def test_exact_four_modes_and_explicit_subset(self):
  self.assertEqual(p.MODES,['scale','atrium','courtyard','refuge']);p.validate_config(copy.deepcopy(self.config));self.assertEqual(n.selected_modes('refuge,scale'),['refuge','scale'])
  for text in(None,'','all','scale,scale','../refuge','flying','scale,'):
   with self.subTest(text=text),self.assertRaises(AssertionError):n.selected_modes(text)
 def test_three_mode_old_config_rejected(self):
  c=copy.deepcopy(self.config);c['scenes'].pop()
  with self.assertRaises(AssertionError):p.validate_config(c)
 def test_ceiling_shape_change_rejected(self):
  c=copy.deepcopy(self.config);c['interiorCeilingUndersideY']=2.7
  with self.assertRaises(AssertionError):p.validate_config(c)
 def test_source_scene_traversal_rejected(self):
  c=copy.deepcopy(self.config);c['scenes'][0]['sourceSceneFile']='../old.unity'
  with self.assertRaises(AssertionError):p.validate_config(c)
 def test_no_default_stage_or_capture(self):
  with patch('sys.argv',['worker']),patch.object(n.subprocess,'Popen')as pop,patch.object(p,'stage')as stage:n.main()
  pop.assert_not_called();stage.assert_not_called()
 def test_all_four_complete_synthetic_corrected_modes(self):
  for mode in p.MODES:
   folder=self.make_mode(mode)
   with self.pixels():summary=n.check_mode(folder,mode,self.prov,decode=False)
   self.assertEqual(summary['frames'],720);self.assertFalse(summary['actualVisualReview'])
 def test_missing_camera_declines(self):
  folder=self.make_mode('scale')
  with self.pixels('observer'),self.assertRaisesRegex(AssertionError,'camera frames'):n.check_mode(folder,'scale',self.prov,decode=False)
 def test_wrong_completion_or_raw_config_declines(self):
  folder=self.make_mode('scale');r=n.read(folder/'mode-complete.json');r['frames']=600;dump(folder/'mode-complete.json',r)
  with self.assertRaises(AssertionError):n.check_mode(folder,'scale',self.prov,False)
 def test_raw_source_reference_tamper_declines(self):
  folder=self.make_mode('scale');(folder/'source-reference.json').write_text('{}')
  with self.assertRaisesRegex(AssertionError,'source-reference'):n.check_mode(folder,'scale',self.prov,False)
 def test_missing_state_clock_declines(self):
  folder=self.make_mode('scale');self.change(folder,'states.jsonl',314,lambda s:s.update(sourceClockFrame=313))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'clock'):n.check_mode(folder,'scale',self.prov,False)
 def test_atrium_stale_actor_or_requested_oldroute_declines(self):
  folder=self.make_mode('atrium');self.change(folder,'states.jsonl',400,lambda s:s.update(playerPosition=self.originals['atrium'][400]['playerPosition']))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'actor pose'):n.check_mode(folder,'atrium',self.prov,False)
 def test_changed_npc_clock_declines(self):
  folder=self.make_mode('atrium');self.change(folder,'states.jsonl',400,lambda s:s['enemyPosition'].update(x=99.))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'NPC/observer'):n.check_mode(folder,'atrium',self.prov,False)
 def test_route_count_stale_declines(self):
  folder=self.make_mode('atrium');self.change(folder,'states.jsonl',400,lambda s:s.update(routePointCount=401))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'Route'):n.check_mode(folder,'atrium',self.prov,False)
 def test_measured_safety_claim_declines(self):
  folder=self.make_mode('refuge');self.change(folder,'states.jsonl',0,lambda s:s.update(safetyMeasured=True))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'cannot claim'):n.check_mode(folder,'refuge',self.prov,False)
 def test_changed_unchanged_world_anchor_declines(self):
  folder=self.make_mode('courtyard');self.change(folder,'projected-anchors.jsonl',300,lambda a:a['anchors'][2]['world'].update(x=5.))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'World/actor anchor'):n.check_mode(folder,'courtyard',self.prov,False)
 def test_camera_matrix_projection_mismatch_declines(self):
  folder=self.make_mode('scale');self.change(folder,'projected-anchors.jsonl',0,lambda a:a['playerCamera']['viewProjectionRowMajor'].__setitem__(3,9.))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'Projection'):n.check_mode(folder,'scale',self.prov,False)
 def test_camera_anchor_ray_detached_origin_declines(self):
  folder=self.make_mode('scale');self.change(folder,'projected-anchors.jsonl',0,lambda a:a['anchors'][0]['playerCameraRay']['origin'].update(x=999.))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'Camera ray detached'):n.check_mode(folder,'scale',self.prov,False)
 def test_courtyard_camera_before_turn_cannot_change(self):
  folder=self.make_mode('courtyard');self.change(folder,'states.jsonl',400,lambda s:s['playerCameraEuler'].update(y=180.))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'direction'):n.check_mode(folder,'courtyard',self.prov,False)
 def test_refuge_ceiling_anchor_is_actual_location(self):
  folder=self.make_mode('refuge');self.change(folder,'projected-anchors.jsonl',0,lambda a:next(x for x in a['anchors']if x['id']=='interior-ceiling-front-edge-center')['world'].update(y=2.7))
  with self.pixels(),self.assertRaisesRegex(AssertionError,'ceiling anchor'):n.check_mode(folder,'refuge',self.prov,False)
 def test_segment_box_actual_clipped_ceiling_and_origin_inside(self):
  hit=n.segment_box(dict(x=0.,y=0.,z=-2.),dict(x=0.,y=3.,z=-2.),dict(x=-3.,y=1.65,z=-5.),dict(x=3.,y=1.75,z=-1.));self.assertAlmostEqual(hit['y'],1.65)
  self.assertIsNone(n.segment_box(dict(x=0.,y=1.7,z=-2.),dict(x=0.,y=3.,z=-2.),dict(x=-3.,y=1.65,z=-5.),dict(x=3.,y=1.75,z=-1.)))
 def test_flat_snapshot_path_and_actual_bytes(self):
  name=n.FOLDER+'/example.unity';data=b'SYNTHETIC editable bytes';relative='editable/'+hashlib.sha256(name.encode()).hexdigest()+'.bin';file=self.root/relative;file.parent.mkdir();file.write_bytes(data);row=dict(path=name,snapshotRelativePath=relative,sha256=n.sha(file),bytes=len(data));self.assertEqual(n.snapshot_file(self.root,row),file)
  row['snapshotRelativePath']='editable/../bad.bin'
  with self.assertRaisesRegex(AssertionError,'Flat snapshot'):n.snapshot_file(self.root,row)
 def test_asset_export_traversal_external_fonts_and_other_scope_decline(self):
  for value in('../outside','C:/escape','Assets/Unrelated/scene.unity',n.FOLDER+'/../other','Assets/ThirdParty/KayKitAdventurers/font.ttf',n.FOLDER+'\\bad.unity'):
   with self.subTest(value=value),self.assertRaises(AssertionError):n.canonical_asset(value)
 def test_snapshot_changed_hash_declines(self):
  name=n.FOLDER+'/example.unity';relative='editable/'+hashlib.sha256(name.encode()).hexdigest()+'.bin';file=self.root/relative;file.parent.mkdir();file.write_bytes(b'changed')
  with self.assertRaisesRegex(AssertionError,'snapshot changed'):n.snapshot_file(self.root,dict(path=name,snapshotRelativePath=relative,sha256='0'*64,bytes=7))
 def test_physical_vs_validator_identity_keeps_original_capture(self):
  physical=dict(contract=p.CONTRACT,prep='same');self.assertEqual(n.digest(physical),n.digest(copy.deepcopy(physical)));self.assertNotEqual(n.digest(dict(physical=physical,qa='old')),n.digest(dict(physical=physical,qa='new')))
 def test_unchanged_nine_original_modes_are_references_only(self):
  self.assertEqual(len(self.current['unaffectedOriginalModes']),9);self.assertFalse(set(self.current['unaffectedOriginalModes'])&set(p.MODES))
 def test_no_invented_textrendering_package(self):
  self.assertEqual(len(p.MANIFEST['dependencies']),5);self.assertNotIn('com.unity.modules.textrendering',p.MANIFEST['dependencies'])
 def test_failed_scope_staging_has_no_writes(self):
  report=dict(self.current,project=str(self.root/'escape'))
  with patch.object(p,'preflight',return_value=report),self.assertRaises(AssertionError):p.stage(report)
  self.assertFalse((self.root/'escape').exists())
 def test_complete_flat_editable_scene_positive(self):
  folder,r=self.scene_fixture();proof=n.validate_scene_record(folder,'scale',self.prov);self.assertTrue(proof['scenePath'].endswith('Corrected.unity'))
 def test_source_guid_original_scene_hash_mismatch_declines(self):
  folder,r=self.scene_fixture();row=next(x for x in r['files']if x['path'].endswith('P02-BodyRelativeScale.unity.meta'));f=folder/row['snapshotRelativePath'];f.write_bytes(b'guid: '+b'd'*32+b'\n');row.update(sha256=n.sha(f),bytes=f.stat().st_size);dump(folder/'scene-record.json',r)
  with self.assertRaisesRegex(AssertionError,'GUID'):n.validate_scene_record(folder,'scale',self.prov)
 def test_other_mode_scene_in_snapshot_declines(self):
  folder,r=self.scene_fixture();name=n.FOLDER+'/P12-DepressedRefugeSection-Corrected.unity';relative='editable/'+hashlib.sha256(name.encode()).hexdigest()+'.bin';file=folder/relative;file.write_bytes(b'SYNTHETIC');r['files'].append(dict(path=name,snapshotRelativePath=relative,sha256=n.sha(file),bytes=file.stat().st_size));dump(folder/'scene-record.json',r)
  with self.assertRaisesRegex(AssertionError,'Other mode'):n.validate_scene_record(folder,'scale',self.prov)
 def replace_snapshot_meta(self,folder,record,name,data):
  row=next(x for x in record['files']if x['path']==name);file=folder/row['snapshotRelativePath'];file.write_bytes(data);row.update(sha256=n.sha(file),bytes=file.stat().st_size);dump(folder/'scene-record.json',record)
 def test_missing_old_runtime_and_driver_metadata_decline(self):
  for name in(n.OLD_FOLDER+'/Experiment.cs',n.OLD_FOLDER+'/Experiment.cs.meta',n.FOLDER+'/CorrectionDriver.cs.meta'):
   folder,r=self.scene_fixture();r['files']=[x for x in r['files']if x['path']!=name];dump(folder/'scene-record.json',r)
   with self.subTest(name=name),self.assertRaisesRegex(AssertionError,'missing'):n.validate_scene_record(folder,'scale',self.prov)
   import shutil;shutil.rmtree(folder)
 def test_saved_scene_guid_invalid_or_same_as_original_declines(self):
  for data in(b'guid: invalid\n',b'guid: '+b'0'*32+b'\n',None):
   folder,r=self.scene_fixture();scene=r['scenePaths'][0];old=next(x for x in r['files']if x['path'].endswith('P02-BodyRelativeScale.unity.meta'));oldbytes=(folder/old['snapshotRelativePath']).read_bytes();self.replace_snapshot_meta(folder,r,scene+'.meta',oldbytes if data is None else data)
   with self.subTest(data=data),self.assertRaises(AssertionError):n.validate_scene_record(folder,'scale',self.prov)
   import shutil;shutil.rmtree(folder)
 def test_generated_source_meta_is_actual_staged_guid_and_bytes(self):
  folder,r=self.scene_fixture();name=n.FOLDER+'/CorrectionDriver.cs.meta';self.replace_snapshot_meta(folder,r,name,b'guid: '+b'f'*32+b'\n')
  with self.assertRaisesRegex(AssertionError,'actual staged'):n.validate_scene_record(folder,'scale',self.prov)
 def test_valid_refuge_flat_snapshot_and_exact_old_overhang(self):
  folder,r=self.scene_fixture('refuge');proof=n.validate_scene_record(folder,'refuge',self.prov);self.assertEqual(proof['additiveGeometry'][0]['colliderLayer'],26)
  r['additiveGeometry'][0]['originalExteriorOverhangWorldMax']['y']=2.9;dump(folder/'scene-record.json',r)
  with self.assertRaisesRegex(AssertionError,'overhang bounds'):n.validate_scene_record(folder,'refuge',self.prov)
 def test_scene_export_guid_unique_across_actual_selected_mode_snapshots(self):
  proofs={}
  for mode in p.MODES:
   folder,r=self.scene_fixture(mode);snapshot=n.validate_scene_record(folder,mode,self.prov);proofs[mode]=dict(sceneSnapshot=snapshot)
  self.assertEqual(len(n.validate_export_scene_guids(proofs,self.prov)),4)
  one=proofs['scale']['sceneSnapshot'];two=proofs['atrium']['sceneSnapshot'];first=next(x for x in one['files']if x['path']==one['scenePath']+'.meta');second=next(x for x in two['files']if x['path']==two['scenePath']+'.meta');f=Path(two['snapshotRoot'])/second['snapshotRelativePath'];f.write_bytes((Path(one['snapshotRoot'])/first['snapshotRelativePath']).read_bytes());second.update(sha256=n.sha(f),bytes=f.stat().st_size)
  with self.assertRaisesRegex(AssertionError,'collides'):n.validate_export_scene_guids(proofs,self.prov)
 def projection_anchor(self,world,c):
  v=projected(world,c);return dict(world=world,playerViewport=v,playerInFrustum=c['nearClip']<v['z']<c['farClip']and 0<=v['x']<=1 and 0<=v['y']<=1,playerCameraRay=ray(c,world))
 def test_behind_near_illconditioned_raw_uv_is_not_visible_evidence(self):
  c=camera(dict(x=0.,y=0.,z=0.),[0.,0.,1.]);a=self.projection_anchor(dict(x=0.,y=.1,z=-.000019),c);a['playerViewport']['y']=5036.24365234375;n.check_projection(a,c,'player');self.assertFalse(a['playerInFrustum'])
 def test_behind_near_fake_visible_flag_still_declines(self):
  c=camera(dict(x=0.,y=0.,z=0.),[0.,0.,1.]);a=self.projection_anchor(dict(x=0.,y=.1,z=-.000019),c);a['playerInFrustum']=True
  with self.assertRaisesRegex(AssertionError,'Frustum'):n.check_projection(a,c,'player')
 def test_front_depth_even_xy_offscreen_keeps_exact_original_tolerance(self):
  c=camera(dict(x=0.,y=0.,z=0.),[0.,0.,1.]);a=self.projection_anchor(dict(x=10.,y=10.,z=1.),c);self.assertFalse(a['playerInFrustum']);a['playerViewport']['x']+=.0003
  with self.assertRaisesRegex(AssertionError,'Projection'):n.check_projection(a,c,'player')
 def test_far_clipped_uv_remains_raw_and_not_visible_but_depth_checked(self):
  c=camera(dict(x=0.,y=0.,z=0.),[0.,0.,1.]);a=self.projection_anchor(dict(x=0.,y=1.,z=81.),c);a['playerViewport']['y']=999.;n.check_projection(a,c,'player');a['playerInFrustum']=True
  with self.assertRaisesRegex(AssertionError,'Frustum'):n.check_projection(a,c,'player')
  a['playerInFrustum']=False;a['playerViewport']['z']=90.
  with self.assertRaisesRegex(AssertionError,'Projected depth'):n.check_projection(a,c,'player')
 def test_owned_root_meta_requires_exact_staged_bytes_and_canonical_guid(self):
  folder,r=self.scene_fixture();self.replace_snapshot_meta(folder,r,n.FOLDER+'.meta',b'guid: '+b'a'*32+b'\n')
  with self.assertRaisesRegex(AssertionError,'actual staged'):n.validate_scene_record(folder,'scale',self.prov)
 def test_missing_actual_mesh_rig_dependency_declines(self):
  folder,r=self.scene_fixture();r['files']=[x for x in r['files']if not x['path'].endswith('Knight.fbx')];dump(folder/'scene-record.json',r)
  with self.assertRaisesRegex(AssertionError,'missing'):n.validate_scene_record(folder,'scale',self.prov)
 def test_partial_inventory_reuses_only_verified_modes_and_rejects_bad_complete(self):
  attempts=self.root/'attempts';attempt=attempts/'one';attempt.mkdir(parents=True);prov=dict(self.prov,protocol=n.PROTOCOL,owner=n.OWNER,physicalIdentity=dict(native='same'),project='same');prov['captureFingerprint']=n.digest(prov['physicalIdentity']);dump(attempt/'input-provenance.json',prov)
  for mode in('scale','refuge'):dump(attempt/'capture'/mode/'mode-complete.json',{})
  def check(folder,mode,prov,freeze):
   if mode=='refuge':raise AssertionError('actual invalid data')
   return dict(mode=mode,actualVisualReview=False)
  with patch.object(n,'ATTEMPTS',attempts),patch.object(n,'mode_proof',side_effect=check):found,rejected=n.inventory(prov)
  self.assertEqual(list(found),['scale']);self.assertEqual(rejected[0]['mode'],'refuge')
 def test_changed_physical_identity_never_reuses_modes(self):
  attempts=self.root/'attempts';attempt=attempts/'one';attempt.mkdir(parents=True);prov=dict(self.prov,protocol=n.PROTOCOL,owner=n.OWNER,physicalIdentity=dict(native='same'),project='same');prov['captureFingerprint']=n.digest(prov['physicalIdentity']);before=copy.deepcopy(prov);before['physicalIdentity']['native']='changed';dump(attempt/'input-provenance.json',before);dump(attempt/'capture'/'scale'/'mode-complete.json',{})
  with patch.object(n,'ATTEMPTS',attempts),patch.object(n,'mode_proof')as proof:found,rejected=n.inventory(prov)
  self.assertEqual(found,{});proof.assert_not_called()
 def test_proven_dead_singleton_recovers_own_marker_only(self):
  file=dump(self.root/'worker.json',dict(protocol=n.PROTOCOL,owner=n.OWNER,token='own',pid=100,createTime=10.,child=None))
  worker=n.core.runtime.SingleWorker(file,is_alive=lambda r:False).acquire();self.assertEqual(worker.previous['token'],'own');worker.close();self.assertFalse(file.exists())
 def test_launch_gap_keeps_lease_while_exact_owned_unregistered_child_exists(self):
  fake=type('P',(),{'info':dict(name='Unity.exe',cmdline=['Unity.exe','-correctionFingerprint','f'*64,'-correctionOutput','EXACT-OUTPUT'])})()
  with patch.object(n.core.runtime.psutil,'process_iter',return_value=[fake]):self.assertTrue(n.core.runtime.unrecorded_child_alive(dict(phase='launching',child=None,fingerprint='f'*64,output='EXACT-OUTPUT')))
 def test_own_protocol_exact_not_foreign(self):
  self.assertTrue(n.core.runtime.ours(dict(protocol=n.PROTOCOL,owner=n.OWNER,token='owned')))
  self.assertFalse(n.core.runtime.ours(dict(protocol=n.PROTOCOL,owner='foreign',token='foreign')))
 def test_foreign_lease_never_recovered(self):
  file=dump(self.root/'lease.json',dict(protocol='foreign',owner='foreign',token='foreign-token'))
  with patch.object(n.core.runtime,'LEASE',file):n.core.runtime.recover_own_lease({'foreign-token'})
  self.assertTrue(file.exists())
 def test_live_singleton_owner_preserved(self):
  file=dump(self.root/'worker.json',dict(protocol=n.PROTOCOL,owner=n.OWNER,pid=100,createTime=10.))
  with patch.object(n.core.runtime,'alive',return_value=True),self.assertRaises(RuntimeError):n.core.runtime.SingleWorker(file).acquire()
  self.assertTrue(file.exists())

if __name__=='__main__':unittest.main(verbosity=2)
