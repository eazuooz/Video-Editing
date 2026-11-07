"""Finite selected06.02 four-mode correction capture; default readiness only.

Original13 modes are never recaptured, rewritten or relabelled. Each completed
corrected mode retains its physical identity and flat editable snapshots; current
CPU validator identity is separate. No voice/movie/human approval is implied.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,shutil,struct,subprocess,time,uuid
from pathlib import Path
import psutil
from initialize import ROOT,HERE,MEDIA,read,save

def load(name,file):
 sp=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

old=load('corrections_frozen_supplement_runtime','run-prospect-refuge-supplement-native.py')
assert old.sha(old.__file__)=='9c6244e46c86b4bc129507345ae270b6ff321ed736059f04141307eb74e6efe8','Audit changed supplement primitive before correction use'
core=old.core;prep=load('corrections_source_preparation','prepare-prospect-refuge-corrections.py')
PROTOCOL='architectural111-06-02-supplement-corrections-v1';OWNER='architectural-111-06-02-supplement-corrections'
core.runtime.PROTOCOL=PROTOCOL;core.runtime.OWNER=OWNER
FOLDER=prep.FOLDER;OLD_FOLDER=prep.OLD_FOLDER;SHADER=prep.SHADER;MODES=prep.MODES;CONTRACT=prep.CONTRACT
STATE=MEDIA/'06-02-corrections-native-progress.json';WORKER=MEDIA/'06-02-corrections-native-worker.json'
ATTEMPTS=MEDIA/'06-02-corr-runs';EVIDENCE=prep.RECORD/'supplementary-corrections-native-evidence-v1.json'
EDITOR=Path(core.EDITOR);CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
sha=core.sha;digest=core.digest;f32=core.f32;near=core.near;vec=core.vec
KIND='our-authored-corrected-illustration';CEILING='OUR ADDITIVE SECTION: shared interior low ceiling'
EXTRA_ANCHORS={'interior-ceiling-underside-above-player','interior-ceiling-floor-below-player','interior-ceiling-front-edge-center','interior-ceiling-front-left','interior-ceiling-front-right','original-exterior-overhang-center'}

def selected_modes(text):
 assert isinstance(text,str)and text,'Explicit --modes subset required; no automatic all4'
 rows=text.split(',');assert len(rows)==len(set(rows))and all(m in MODES for m in rows),'Unknown/duplicate/empty correction mode';return rows

def pinned(row):
 assert Path(row['path']).is_file()and sha(row['path'])==row['sha256'],'Pinned source/raw proof changed'

def authorize(allow_imported_meta=False):
 current=prep.preflight();staged=read(prep.REPORT)
 assert staged.get('stageComplete')is True and staged['fingerprint']==current['fingerprint']and staged['files']==current['files']and staged['generatedFiles']==current['generatedFiles'],'Fresh selected correction staging required'
 assert staged['captureContract']==CONTRACT and staged['staticCompilerPreflight']==current['staticCompilerPreflight']
 project=Path(staged['project']).resolve();assert project==Path(current['project']).resolve()and project.parent==(MEDIA/'06-02-corr-proj').resolve()
 known={}
 if EVIDENCE.exists():
  previous=read(EVIDENCE)
  if previous.get('preparationFingerprint')==current['fingerprint']:known={r['target']:r for r in previous.get('actualStagedMeta',[])}
 changes=[]
 for row in staged['files']:
  source=Path(row['source']).resolve();target=(project/row['target']).resolve();assert target.is_relative_to(project)
  change=core.staged_input(row,source,target,known,allow_imported_meta)
  if change:changes.append(change)
 for row in staged['generatedFiles']:
  target=(project/row['target']).resolve();assert target.is_relative_to(project)and sha(target)==row['sha256'],'Generated source-reference changed'
 for row in staged['externalInputs']+staged['engineApiModules']:pinned(row)
 version=core.project_version(project/'ProjectSettings/ProjectVersion.txt','6000.6.0f1');assert EDITOR.is_file()
 prep.oldprep.validate_manifest(project/'Packages/manifest.json')
 physical=dict(protocol=PROTOCOL,topicId='06.02',preparationFingerprint=current['fingerprint'],sourceCaptureFingerprint=prep.SOURCE_CAPTURE,editorVersion=version['editorVersion'],editorBinarySHA256=sha(EDITOR),projectManifestSHA256=sha(project/'Packages/manifest.json'),contract=CONTRACT)
 capture=digest(physical)
 qa=[dict(path=str(p),sha256=sha(p))for p in[Path(__file__),Path(prep.__file__),Path(old.__file__),Path(core.__file__),HERE/'run-first-native.py',HERE/'prospect-refuge-resource-qualification.py',Path(current['staticCompilerPreflight']['path'])]]
 return dict(protocol=PROTOCOL,owner=OWNER,topicId='06.02',captureFingerprint=capture,validatorFingerprint=digest(dict(captureFingerprint=capture,validatorPins=qa)),physicalIdentity=physical,validatorPins=qa,project=str(project),preparationFingerprint=current['fingerprint'],sourcePins=staged['files'],generatedPins=staged['generatedFiles'],externalInputs=staged['externalInputs'],actualStagedMeta=changes,config=current['config'],sourceReference=current['sourceReference'],sourceReferenceSHA256=current['sourceReferenceSHA256'],sourceModes=current['sourceModes'],unaffectedOriginalModes=current['unaffectedOriginalModes'],captureEntry=current['captureEntry'],originalEvidenceAudit=current['originalEvidenceAudit'],sourceOwnerAudit=current['sourceOwnerAudit'],projectVersionAudit=version['sourceAudit'])

def lines(path):return[json.loads(line)for line in Path(path).read_text(encoding='utf8').splitlines()]
def same_float(a,b):return core.float32_bits(a)==core.float32_bits(b)
def same_vec(a,b):return all(same_float(a[k],b[k])for k in'xyz')
def xyz(row):return[row[k]for k in'xyz']
def dist(a,b):return math.sqrt(sum((a[k]-b[k])**2 for k in'xyz'))
def unit(v):
 size=math.sqrt(sum(x*x for x in v));assert size>1e-9;return[x/size for x in v]
def direction(a,b):return unit([b[k]-a[k]for k in'xyz'])
def euler_forward(e):
 pitch,yaw=map(math.radians,[e['x'],e['y']]);return[math.sin(yaw)*math.cos(pitch),-math.sin(pitch),math.cos(yaw)*math.cos(pitch)]
def look_quaternion(forward):
 # Unity LookRotation's positive-up orthonormal basis; quaternion sign has no
 # effect except the exact180deg tie, where largest-diagonal branch is pinned.
 z=unit(forward);x=unit([z[2],0.,-z[0]]);y=[z[1]*x[2]-z[2]*x[1],z[2]*x[0]-z[0]*x[2],z[0]*x[1]-z[1]*x[0]]
 m=[[x[i],y[i],z[i]]for i in range(3)];tr=sum(m[i][i]for i in range(3))
 if tr>0:
  t=math.sqrt(tr+1.)*2;return[(m[2][1]-m[1][2])/t,(m[0][2]-m[2][0])/t,(m[1][0]-m[0][1])/t,t*.25]
 i=max(range(3),key=lambda j:m[j][j]);j=(i+1)%3;k=(i+2)%3;t=math.sqrt(1+m[i][i]-m[j][j]-m[k][k])*2;q=[0.]*4;q[i]=t*.25;q[j]=(m[j][i]+m[i][j])/t;q[k]=(m[k][i]+m[i][k])/t;q[3]=(m[k][j]-m[j][k])/t;return q

def slerp_direction(a,b,t):
 qa,qb=look_quaternion(a),look_quaternion(b);dot=sum(x*y for x,y in zip(qa,qb))
 if dot<0:qb=[-x for x in qb];dot=-dot
 dot=min(1.,max(-1.,dot))
 if dot>.9995:q=unit([(1-t)*x+t*y for x,y in zip(qa,qb)])
 else:
  angle=math.acos(dot);q=[(math.sin((1-t)*angle)*x+math.sin(t*angle)*y)/math.sin(angle)for x,y in zip(qa,qb)]
 x,y,z,w=q;return[2*(x*z+w*y),2*(y*z-w*x),1-2*(x*x+y*y)]
def forward_close(actual,expected):
 assert max(abs(a-b)for a,b in zip(actual,expected))<.00008,'Actual camera/body direction differs from selected correction'

def expected_phase(mode,frame):
 if mode=='scale':return'narrow-to-intimate-boundary'if frame<240 else'intimate-to-open-boundary'
 if mode=='atrium':return'stationary-private-room-observes-public-circulation'
 if mode=='refuge':return'sectional-interior-ceiling-and-original-outward-view'
 return'scripted-observe'if frame<120 else'scripted-cross'if frame<600 else'turn-toward-courtyard'if frame<690 else'new-outward-observation'

def segment_box(a,b,lo,hi):
 # PhysX does not report the collider containing its ray origin.
 if all(lo[k]<=a[k]<=hi[k]for k in'xyz'):return None
 first,last=0.,1.
 for k in'xyz':
  d=b[k]-a[k]
  if abs(d)<1e-12:
   if not lo[k]<=a[k]<=hi[k]:return None
  else:
   p,q=sorted(((lo[k]-a[k])/d,(hi[k]-a[k])/d));first=max(first,p);last=min(last,q)
   if first>last:return None
 if first<0 or first>1:return None
 return{k:a[k]+first*(b[k]-a[k])for k in'xyz'}

def check_camera_ray(ray,camera,target):
 for k in('origin','desiredEndpoint','actualEndpoint'):old.finite_vector(ray[k])
 assert vec(ray['origin'],camera['position'])and vec(ray['desiredEndpoint'],target),'Camera ray detached from actual camera/anchor'
 old.check_ray(dict(ray,id='actual-camera-to-anchor',meaning='Sample ray, not whole object visibility',distance=dist(ray['origin'],ray['desiredEndpoint'])))

def check_camera(camera,state,prefix,expected_forward,expected_fov):
 for k in('position','forward'):old.finite_vector(camera[k])
 assert same_vec(camera['position'],state[prefix+'CameraEye'])and near(camera['aspect'],f32(16/9),1e-7)and near(camera['fieldOfView'],expected_fov,1e-5),'Camera proof detached from actual state/contract'
 assert camera['nearClip']>0 and camera['farClip']>camera['nearClip']and near(sum(v*v for v in camera['forward'].values()),1.,.00002)
 forward_close(xyz(camera['forward']),expected_forward);forward_close(euler_forward(state[prefix+'CameraEuler']),expected_forward)
 m=camera['viewProjectionRowMajor'];assert len(m)==16 and all(type(v)in(int,float)and math.isfinite(v)for v in m),'Malformed actual projection matrix'

def check_projection(anchor,camera,prefix):
 p=anchor[prefix+'Viewport'];old.finite_vector(p);world=anchor['world'];delta=[world[k]-camera['position'][k]for k in'xyz'];depth=sum(x*y for x,y in zip(delta,xyz(camera['forward'])))
 assert near(p['z'],depth,.00008),'Projected depth not actual camera/world anchor'
 m=camera['viewProjectionRowMajor'];v=xyz(world)+[1.];clip=[sum(m[i*4+j]*v[j]for j in range(4))for i in range(4)]
 # Raw UV behind the physical near plane can be arbitrarily ill-conditioned
 # (actual frame221 head depth~-1.9e-5m). Keep it in the trace, but never
 # interpret its divided XY as visible geometry. Every point within the
 # actual near/far depth interval, even XY-offscreen, keeps the original
 # absolute2e-4 projection test. Depth/frustum/camera/rays remain unconditional.
 if camera['nearClip']<p['z']<camera['farClip']:
  assert clip[3]>1e-5,'Front-depth point has invalid actual projection divisor'
  assert near(p['x'],.5+.5*clip[0]/clip[3],.0002)and near(p['y'],.5+.5*clip[1]/clip[3],.0002),'Projection is not from its actual camera matrix'
 flag=camera['nearClip']<p['z']<camera['farClip']and 0<=p['x']<=1 and 0<=p['y']<=1
 assert type(anchor[prefix+'InFrustum'])is bool and anchor[prefix+'InFrustum']==flag,'Frustum is not occlusion visibility'
 check_camera_ray(anchor[prefix+'CameraRay'],camera,world)


def extra_world(c):
 y=f32(c['interiorCeilingUndersideY']);z=f32(c['interiorCeilingMaxZ']);x=f32(c['interiorCeilingWidth']*.5)
 return{'interior-ceiling-underside-above-player':dict(x=0.,y=y,z=-2.),'interior-ceiling-floor-below-player':dict(x=0.,y=f32(-.65),z=-2.),'interior-ceiling-front-edge-center':dict(x=0.,y=y,z=z),'interior-ceiling-front-left':dict(x=-x,y=y,z=z),'interior-ceiling-front-right':dict(x=x,y=y,z=z)}

def check_state(s,previous,original,mode,c,route):
 f=s['frame'];assert s['sourceClockFrame']==f and s['appliedCommandFrame']==f-1 and same_float(s['timeSeconds'],f32(f/60)),'Corrected/source frame clock differs'
 assert s['mode']==mode and s['sourceKind']==KIND and s['correction']==next(r['correction']for r in c['scenes']if r['mode']==mode)and s['phase']==expected_phase(mode,f)
 assert s['motionKind']==('stationary actor; original NPC clock'if mode=='atrium'else'declared scripted geometric illustration; corrected camera')
 assert all(s[k]is False for k in('commercialImplementationMeasured','safetyMeasured','wholeMeshVisibilityMeasured')),'Illustration cannot claim commercial/safety/whole-mesh measurement'
 for k in('playerPosition','requestedPlayerPosition','actualMoveDelta','playerEuler','enemyPosition','secondEnemyPosition','playerCameraEye','playerCameraEuler','observerCameraEye','observerCameraEuler'):old.finite_vector(s[k])
 for k in('enemyPosition','secondEnemyPosition','observerCameraEye','observerCameraEuler'):assert same_vec(s[k],original[k]),'Unchanged NPC/observer source clock differs'
 position={k:f32(v)for k,v in c['atriumPlayerPosition'].items()}if mode=='atrium'else original['playerPosition']
 assert same_vec(s['playerPosition'],position)and same_vec(s['requestedPlayerPosition'],position),'Corrected actor pose is stale/changed beyond selected mode'
 delta={k:f32(position[k]-previous['playerPosition'][k])if previous else 0. for k in'xyz'}
 assert same_vec(s['actualMoveDelta'],delta),'Actual corrected delta is stale'
 point=dict(position);point['y']=f32(point['y']+f32(.035))
 if not route or dist(route[-1],point)**2>1e-12:route.append(point)
 assert s['routePointCount']==len(route),'Route still describes old pre-correction actor path'
 if mode=='scale':eye={k:f32(v)for k,v in c['scaleCameraPosition'].items()};forward=direction(eye,c['scaleCameraTarget'])
 elif mode=='atrium':
  eye=dict(position);eye['y']=f32(eye['y']+f32(1.65));forward=direction(eye,c['atriumLookAt']);body=direction({**position,'y':0.},{**c['atriumLookAt'],'y':0.});forward_close(euler_forward(s['playerEuler']),body)
 else:
  eye=original['playerCameraEye'];forward=euler_forward(original['playerCameraEuler'])
  if mode=='courtyard'and f>=600:
   t=f32((f-600)/90);t=min(1.,max(0.,t));forward=slerp_direction(forward,direction(eye,c['courtyardReobserveTarget']),t)
   body=slerp_direction([0.,0.,1.],direction({**position,'y':0.},{**c['courtyardReobserveTarget'],'y':0.}),t);forward_close(euler_forward(s['playerEuler']),body)
  else:forward_close(euler_forward(s['playerEuler']),[0.,0.,1.])
 assert same_vec(s['playerCameraEye'],eye),'Selected actual camera position differs'
 return forward

def check_mode(folder,mode,prov,decode=True):
 folder=Path(folder);c=prov['config'];assert mode in MODES
 receipt=read(folder/'mode-complete.json');assert receipt==read(folder/'mode-contract.json'),'Missing/changed per-mode completion receipt'
 ref=next(r for r in prov['sourceReference']['modes']if r['mode']==mode);scene=FOLDER+'/'+next(r['sceneFile']for r in c['scenes']if r['mode']==mode)
 expected=dict(fingerprint=prov['captureFingerprint'],sourceCaptureFingerprint=prep.SOURCE_CAPTURE,mode=mode,sourceKind=KIND,actualScenePath=scene,actualSceneSaved=True,**{k:v for k,v in CONTRACT.items()if k!='modes'},**{k:v for k,v in ref.items()if k!='mode'})
 assert all(receipt.get(k)==v for k,v in expected.items()),'Corrected mode physical/scene/clock provenance differs'
 assert sha(folder/'config.json')==receipt['configSHA256']==sha(prep.SOURCE/'config.json')and sha(folder/'source-reference.json')==receipt['sourceReferenceSHA256']==prov['sourceReferenceSHA256'],'Correction config/source-reference bytes changed'
 core.validate_capture_config(read(folder/'config.json'),c);assert read(folder/'source-reference.json')==prov['sourceReference']and receipt['frameConvention']==c['frameConvention']
 source=prov['sourceModes'][mode]
 for key in('states','anchors','rays'):pinned(source[key])
 originals=lines(source['states']['path']);oldanchors=lines(source['anchors']['path'])
 states=lines(folder/'states.jsonl');rays=lines(folder/'rays.jsonl');anchors=lines(folder/'projected-anchors.jsonl')
 assert all(len(rows)==720 and[r['frame']for r in rows]==list(range(720))for rows in(states,rays,anchors,originals,oldanchors)),'Missing/unordered actual frame/state evidence'
 route=[];previous=None;projection_count=0
 for f,(s,rr,aa,o,oa)in enumerate(zip(states,rays,anchors,originals,oldanchors)):
  forward=check_state(s,previous,o,mode,c,route);assert s['rays']==rr['rays']and[r['id']for r in s['rays']]==[r['id']for r in o['rays']],'Fresh bound rays missing/changed'
  for actual,before in zip(s['rays'],o['rays']):
   old.check_ray(actual)
   for k in('id','meaning','origin','desiredEndpoint','distance'):assert actual[k]==before[k],'Original declared ray inputs changed'
   expected_hit=None
   if mode=='refuge':expected_hit=segment_box(actual['origin'],actual['desiredEndpoint'],dict(x=-3.,y=f32(1.65),z=-5.),dict(x=3.,y=f32(f32(1.65)+f32(.1)),z=-1.))
   if expected_hit is not None and dist(actual['origin'],expected_hit)<dist(before['origin'],before['actualEndpoint'])-.0001:
    assert actual['blocked']and actual['hitCollider']==CEILING and vec(actual['actualEndpoint'],expected_hit),'Additive physical ceiling ray hit differs'
   else:
    assert actual['blocked']==before['blocked'] and (actual['hitCollider']in(None,'')if not before['blocked']else actual['hitCollider']==before['hitCollider'])
    assert vec(actual['actualEndpoint'],before['actualEndpoint']),'Unchanged body ray output differs'
  check_camera(aa['playerCamera'],s,'player',forward,38 if mode=='scale'else 55)
  check_camera(aa['observerCamera'],s,'observer',euler_forward(o['observerCameraEuler']),55)
  oldmap={a['id']:a for a in oa['anchors']};ids=[a['id']for a in aa['anchors']]
  assert len(ids)==len(set(ids))and set(ids)==set(oldmap)|(EXTRA_ANCHORS if mode=='refuge'else set()),'Actual anchors added/removed outside selected correction'
  for a in aa['anchors']:
   old.finite_vector(a['world']);assert type(a['active'])is bool
   if a['id']in oldmap:
    before=oldmap[a['id']];assert a['role']==before['role']and a['active']==before['active'],'Unchanged anchor semantic/active state differs'
    expected_world=before['world']
    if mode=='atrium'and a['id']in('player-head','player-torso','enclosed-loft'):
     expected_world={k:f32(v)for k,v in c['atriumPlayerPosition'].items()};expected_world['y']=f32(expected_world['y']+f32({'player-head':1.55,'player-torso':.95,'enclosed-loft':.8}[a['id']]))
    assert same_vec(a['world'],expected_world),'World/actor anchor changed beyond declared correction'
   elif a['id']in extra_world(c):assert vec(a['world'],extra_world(c)[a['id']]),'Additive ceiling anchor not bound to real geometry'
   else:assert vec(a['world'],dict(x=0.,y=2.7,z=1.8)),'Original exterior overhang anchor differs'
   for prefix in('player','observer'):check_projection(a,aa[prefix+'Camera'],prefix);projection_count+=1
  previous=s
 final=read(folder/'corrected-route.json');assert final['mode']==mode and final['sourceKind']==KIND and final['physicallySolved']is False and len(final['points'])==len(route)and all(same_vec(a,b)for a,b in zip(final['points'],route)),'Saved corrected route is stale or falsely physical'
 for camera in CONTRACT['cameras']:
  paths=sorted((folder/camera).glob('*.jpg'));assert[p.name for p in paths]==[f'{f:04}.jpg'for f in range(720)],'Missing/extra actual camera frames'
  if decode:
   from PIL import Image
   for f in(0,119,120,239,240,599,600,645,690,719):
    with Image.open(paths[f])as image:image.load();assert image.size==(1920,1080),'Actual decoded source is not FHD'
 return dict(mode=mode,frames=720,projectionChecks=projection_count,routePoints=len(route),sourceKind=KIND,actualVisualReview=False,wholeMeshVisibilityMeasured=False,humanDecisionMeasured=False)


def canonical_asset(value):
 assert isinstance(value,str)and value and'\\'not in value and ':'not in value
 assert all(p not in('','.','..')for p in value.split('/'))and not Path(value).is_absolute(),'Noncanonical editable path'
 assert value.startswith(FOLDER+'/')or value==FOLDER+'.meta'or value.startswith(OLD_FOLDER+'/')or value==OLD_FOLDER+'.meta'or value.startswith('Assets/ThirdParty/KayKitAdventurers/')or value in(SHADER,SHADER+'.meta'),'Editable source escaped exact correction dependencies'
 assert Path(value).suffix.lower()not in('.ttf','.otf'),'External font binary must never enter editable export'
 return value

def snapshot_file(folder,row):
 name=canonical_asset(row['path']);expected='editable/'+hashlib.sha256(name.encode('utf8')).hexdigest()+'.bin';assert row['snapshotRelativePath']==expected,'Flat snapshot path must hash exact canonical asset path'
 actual=(Path(folder)/expected).resolve();assert actual.is_relative_to(Path(folder).resolve())and actual.stat().st_size==row['bytes']and sha(actual)==row['sha256'],'Immutable flat editable snapshot changed';return actual

def validate_scene_record(folder,mode,prov,freeze=False):
 folder=Path(folder);record=read(folder/'scene-record.json');c=prov['config'];scene=FOLDER+'/'+next(r['sceneFile']for r in c['scenes']if r['mode']==mode);ref=next(r for r in prov['sourceReference']['modes']if r['mode']==mode)
 assert record['fingerprint']==prov['captureFingerprint']and record['sourceCaptureFingerprint']==prep.SOURCE_CAPTURE and record['mode']==mode and record['sourceKind']==KIND and record['unityVersion']=='6000.6.0f1'
 assert record['actualSceneFilesSaved']is True and record['savedAtFrame']==0 and record['scenePaths']==[scene]
 rows=record['files'];names=[r['path']for r in rows];assert rows and len(names)==len(set(n.casefold()for n in names))
 assert{FOLDER+'.meta',scene,scene+'.meta',ref['sourceScenePath'],ref['sourceScenePath']+'.meta',OLD_FOLDER+'/Experiment.cs',OLD_FOLDER+'/Experiment.cs.meta',FOLDER+'/CorrectionDriver.cs',FOLDER+'/CorrectionDriver.cs.meta',FOLDER+'/Editor/CorrectionBuilder.cs',FOLDER+'/config.json',FOLDER+'/source-reference.json',SHADER,SHADER+'.meta','Assets/ThirdParty/KayKitAdventurers/Knight.fbx','Assets/ThirdParty/KayKitAdventurers/Knight.fbx.meta','Assets/ThirdParty/KayKitAdventurers/knight_texture.png','Assets/ThirdParty/KayKitAdventurers/knight_texture.png.meta'}<=set(names),'Editable original scene/current source/config/metadata missing'
 expected={r['target']:r['sha256']for r in prov['sourcePins']};expected.update({r['target']:r['sha256']for r in prov['generatedPins']});known={r['target']:r for r in prov['actualStagedMeta']}
 for row in rows:
  name=canonical_asset(row['path']);actual=snapshot_file(folder,row)
  if name.endswith(('.unity','.unity.meta')):assert name in(scene,scene+'.meta',ref['sourceScenePath'],ref['sourceScenePath']+'.meta'),'Other mode scene entered selected editable snapshot'
  if name in expected and sha(actual)!=expected[name]:
   assert name.endswith('.meta')and known.get(name,{}).get('stagedSHA256')==sha(actual)and core.meta_guid(actual)==core.meta_guid(next(Path(r['source'])for r in prov['sourcePins']if r['target']==name)),'Pinned original/source/import GUID changed'
  elif not(name.startswith(FOLDER+'/')or name==FOLDER+'.meta'):assert name in expected,'Unknown original/shared dependency cannot be accepted'
 assert next(r['sha256']for r in rows if r['path']==ref['sourceScenePath'])==ref['sourceSceneSHA256']and next(r['sha256']for r in rows if r['path']==ref['sourceScenePath']+'.meta')==ref['sourceSceneMetaSHA256'],'Original scene/GUID proof changed'
 by_name={row['path']:row for row in rows}
 # Original source metadata retains its pinned GUID. Newly imported script
 # metadata has no fabricated pre-import hash: bind its actual staged bytes
 # and canonical GUID to the immutable capture snapshot explicitly instead.
 source_meta=[]
 for name in(OLD_FOLDER+'/Experiment.cs.meta',FOLDER+'/CorrectionDriver.cs.meta',FOLDER+'.meta'):
  actual=snapshot_file(folder,by_name[name]);guid=core.meta_guid(actual);assert guid!='0'*32,'Source metadata GUID cannot be empty'
  if name in expected:
   source=next(Path(r['source'])for r in prov['sourcePins']if r['target']==name);assert guid==core.meta_guid(source),'Pinned source metadata GUID changed'
  else:
   staged=(Path(prov['project'])/name).resolve();assert staged.is_relative_to(Path(prov['project']).resolve())and staged.is_file()and sha(staged)==sha(actual)and core.meta_guid(staged)==guid,'Generated source metadata differs from actual staged import'
  source_meta.append(dict(path=name,sha256=sha(actual),guid=guid,provenance='pinned-original-source'if name in expected else'actual-staged-generated-import'))
 scene_guid=core.meta_guid(snapshot_file(folder,by_name[scene+'.meta']));old_guid=core.meta_guid(snapshot_file(folder,by_name[ref['sourceScenePath']+'.meta']))
 assert scene_guid!='0'*32 and scene_guid!=old_guid,'Saved corrected scene GUID must be valid and distinct from original'
 geometry=record['additiveGeometry']
 if mode!='refuge':assert geometry==[],'Unexpected additive physical geometry'
 else:
  assert len(geometry)==1;g=geometry[0];assert g['id']=='interior-ceiling'and g['colliderLayer']==26
  for key,expected_vec in [('actualColliderWorldMin',dict(x=-3.,y=1.65,z=-5.)),('actualColliderWorldMax',dict(x=3.,y=1.75,z=-1.)),('actualMeshWorldMin',dict(x=-3.,y=1.65,z=-5.)),('actualMeshWorldMax',dict(x=3.,y=1.65,z=-1.)),('playerFootPoint',dict(x=0.,y=-.65,z=-2.)),('ceilingAbovePlayerPoint',dict(x=0.,y=1.65,z=-2.))]:assert vec(g[key],expected_vec),'Actual additive ceiling bounds/actor relation differs'
  assert vec(g['originalExteriorOverhangWorldMin'],dict(x=-3.3,y=2.575,z=.6))and vec(g['originalExteriorOverhangWorldMax'],dict(x=3.3,y=2.825,z=3.)),'Original exterior overhang bounds changed or conflated with interior ceiling'
  for stem in('mesh','material'):
   name=g[stem+'AssetPath'];assert name.startswith(FOLDER+'/'+('Meshes/'if stem=='mesh'else'Materials/'))and next(r['sha256']for r in rows if r['path']==name)==g[stem+'AssetSHA256'],'Actual persistent ceiling asset absent'
 return dict(scenePath=scene,files=rows,record=dict(path=str(folder/'scene-record.json'),sha256=sha(folder/'scene-record.json')),snapshotRoot=str(folder),additiveGeometry=geometry,sceneGUID=scene_guid,originalSceneGUID=old_guid,sourceMetadata=source_meta)


def mode_proof(folder,mode,prov,freeze=False):
 folder=Path(folder);summary=check_mode(folder,mode,prov);scene=validate_scene_record(folder,mode,prov,freeze)
 names=['config.json','source-reference.json','mode-contract.json','mode-complete.json','scene-record.json','states.jsonl','rays.jsonl','projected-anchors.jsonl','corrected-route.json']
 proof=dict(schemaVersion='06.02-correction-mode-proof-v1',mode=mode,captureFingerprint=prov['captureFingerprint'],validatorFingerprint=prov['validatorFingerprint'],modeFolder=str(folder),summary=summary,sceneSnapshot=scene,files=[dict(path=n,sha256=sha(folder/n))for n in names],actualStagedMeta=prov['actualStagedMeta'],humanApproval=False,voicePreparationAllowed=False)
 framefile=folder/'frame-hashes-v1.json';rows=[dict(path=p.relative_to(folder).as_posix(),sha256=sha(p),bytes=p.stat().st_size)for camera in CONTRACT['cameras']for p in sorted((folder/camera).glob('*.jpg'))];frame_record=dict(captureFingerprint=prov['captureFingerprint'],mode=mode,frames=rows)
 if framefile.exists():assert read(framefile)==frame_record,'Prior completed actual frame changed; preserve instead of recapture'
 if freeze:
  if not framefile.exists():save(framefile,frame_record)
  proof['frameHashManifest']=dict(path=str(framefile),sha256=sha(framefile));target=folder/('mode-proof-'+prov['validatorFingerprint'][:24]+'.json')
  if target.exists():assert read(target)==proof,'Prior current-validator proof changed'
  else:save(target,proof)
  proof['proofFile']=dict(path=str(target),sha256=sha(target))
 return proof

def inventory(prov,freeze=False):
 found={};rejected=[]
 for attempt in sorted(ATTEMPTS.glob('*'),reverse=True)if ATTEMPTS.exists()else[]:
  try:
   previous=read(attempt/'input-provenance.json');assert previous['protocol']==PROTOCOL and previous['owner']==OWNER and previous['captureFingerprint']==prov['captureFingerprint']==digest(previous['physicalIdentity'])and previous['physicalIdentity']==prov['physicalIdentity']and previous['project']==prov['project']and previous['sourcePins']==prov['sourcePins']and previous['generatedPins']==prov['generatedPins']
  except(OSError,ValueError,KeyError,AssertionError):continue
  for mode in MODES:
   if mode in found:continue
   folder=attempt/'capture'/mode
   if not(folder/'mode-complete.json').exists():continue
   try:found[mode]=mode_proof(folder,mode,prov,freeze)
   except(OSError,ValueError,KeyError,AssertionError)as error:rejected.append(dict(mode=mode,folder=str(folder),reason=str(error)))
 return found,rejected

def validate_export_scene_guids(proofs,prov):
 guids={};old_guids=set()
 for ref in prov['sourceReference']['modes']:
  name=ref['sourceScenePath']+'.meta';source=next(Path(r['source'])for r in prov['sourcePins']if r['target']==name);assert sha(source)==ref['sourceSceneMetaSHA256'],'Original scene GUID source changed';old_guids.add(core.meta_guid(source))
 assert len(old_guids)==len(MODES),'Original selected scene GUIDs are not unique'
 for mode,proof in proofs.items():
  snapshot=proof['sceneSnapshot'];name=snapshot['scenePath']+'.meta';row=next(r for r in snapshot['files']if r['path']==name);guid=core.meta_guid(snapshot_file(snapshot['snapshotRoot'],row))
  assert guid!='0'*32 and guid not in old_guids and guid not in guids,'Corrected scene GUID collides with original or another corrected export'
  guids[guid]=mode
 return guids

def export_modes(proofs,prov):
 validate_export_scene_guids(proofs,prov);exports={}
 for mode,proof in proofs.items():
  folder=Path(proof['sceneSnapshot']['snapshotRoot'])
  for row in proof['sceneSnapshot']['files']:
   name=canonical_asset(row['path']);source=snapshot_file(folder,row)
   if not(name.startswith(FOLDER+'/')or name==FOLDER+'.meta'):continue
   target=(ROOT/'unity/VideoEditing'/name).resolve();assert target.is_relative_to((ROOT/'unity/VideoEditing'/FOLDER).resolve())or target==Path(str(ROOT/'unity/VideoEditing'/FOLDER)+'.meta')
   if name in exports:assert exports[name][2]==row['sha256'],'Conflicting correction source versions across completed modes'
   assert not target.exists()or sha(target)==row['sha256'],'Preserve changed correction editable export; explicit revision required';exports[name]=(source,target,row['sha256'])
 for source,target,value in exports.values():
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copy2(source,target)
  assert sha(target)==value
 # Original13 output source/assets stay bit-identical; images are referenced.
 for row in prov['sourcePins']:
  if row['sourceKind']=='preserved-original-editable':assert sha(row['source'])==row['sha256'],'Original13 editable bytes changed'
 return[dict(path=str(t.relative_to(ROOT)),sha256=v)for s,t,v in exports.values()]

def publish_native_evidence(proofs,prov,requested,rejected):
 exported=export_modes(proofs,prov)
 data=dict(schemaVersion='06.02-supplementary-corrections-native-evidence-v1',topicId='06.02',captureFingerprint=prov['captureFingerprint'],validatorFingerprint=prov['validatorFingerprint'],preparationFingerprint=prov['preparationFingerprint'],sourceCaptureFingerprint=prep.SOURCE_CAPTURE,sourceKind=KIND,requestedModes=requested,completedModes=[m for m in MODES if m in proofs],fullCorrectionCaptureComplete=set(proofs)==set(MODES),selectedSubsetComplete=set(requested)<=set(proofs),modes=proofs,unaffectedOriginalModes=prov['unaffectedOriginalModes'],originalEvidenceAudit=prov['originalEvidenceAudit'],exportedFiles=exported,actualStagedMeta=prov['actualStagedMeta'],rejectedPriorModeAttempts=rejected,actualVisualReview=False,voicePreparationAllowed=False,humanApproval=False,platformActions=[],measurementLimits='Four corrected authored geometric illustrations only. Original9 modes are referenced unchanged; no commercial AI, human decision, structural safety, whole-mesh visibility or final movie approval.')
 if EVIDENCE.exists():
  previous=read(EVIDENCE)
  if previous.get('captureFingerprint')==prov['captureFingerprint']and previous.get('completedModes')==data['completedModes']:
   for key in('actualVisualReview','voicePreparationAllowed','humanApproval','platformActions'):data[key]=previous.get(key,data[key])
  else:
   history=MEDIA/'shorts-leveldesign-06-02/correction-evidence-history';history.mkdir(parents=True,exist_ok=True);shutil.copy2(EVIDENCE,history/(sha(EVIDENCE)+'.json'))
 save(EVIDENCE,data);return data

no_live_selected_project=old.no_live_selected_project

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');parser.add_argument('--modes');parser.add_argument('--wait-hours',type=float,default=2);args=parser.parse_args()
 assert math.isfinite(args.wait_hours)and 0<=args.wait_hours<=24
 try:requested=selected_modes(args.modes);prov=authorize()
 except(FileNotFoundError,KeyError,AssertionError)as error:
  if args.execute:raise
  print(json.dumps(dict(ready=False,reason=str(error),newGpuStarted=False)));return
 if not args.execute:
  found,rejected=inventory(prov);print(json.dumps(dict(ready=True,captureFingerprint=prov['captureFingerprint'],validatorFingerprint=prov['validatorFingerprint'],requestedModes=requested,reusableModes=list(found),fullCorrectionCaptureComplete=set(found)==set(MODES),resourceWait=core.busy_reason(),newGpuStarted=False)));return
 worker=core.runtime.SingleWorker(WORKER).acquire();token=None;child=None;state={};current=prov
 try:
  old=read(STATE)if STATE.exists()else{}
  assert not core.runtime.alive(old)and not core.runtime.alive(old.get('child')),'Live/unknown prior worker preserved'
  known={r.get('leaseToken')for r in[old,worker.previous or{}]if r.get('leaseToken')}
  for record in[old,worker.previous or{}]:known.update(record.get('recoverableLeaseTokens',[]))
  worker.update(recoverableLeaseTokens=sorted(known));core.runtime.recover_own_lease(known);no_live_selected_project(prov)
  found,rejected=inventory(prov,freeze=True);missing=[m for m in requested if m not in found]
  assert not any(r['mode']in missing for r in rejected),'Completed actual mode failed current validation; preserve and diagnose before any recapture'
  if missing:
   needed=len(missing)*720*2*1024**2+4*1024**3;assert shutil.disk_usage(MEDIA).free>=needed,'Insufficient space for selected native subset/reserve'
   attempt=ATTEMPTS/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]);attempt.mkdir(parents=True)
   capture=attempt/'capture';assert not capture.exists();save(attempt/'input-provenance.json',prov)
   state=dict(protocol=PROTOCOL,owner=OWNER,**core.runtime.identity(),child=None,status='waiting-for-resources',fingerprint=prov['captureFingerprint'],validatorFingerprint=prov['validatorFingerprint'],attempt=str(attempt),output=str(capture),requestedModes=requested,missingModes=missing,completed=False,gpuStarted=False,recoverableLeaseTokens=sorted(known));save(STATE,state)
   deadline=time.monotonic()+args.wait_hours*3600
   while token is None:
    fresh=authorize();assert fresh['validatorFingerprint']==prov['validatorFingerprint'],'Selected source/QA changed while waiting'
    core.runtime.recover_own_lease(known);reason=core.busy_reason();state.update(reason=reason,checkedAt=time.time());save(STATE,state)
    if not reason:
     value=uuid.uuid4().hex;lease=dict(protocol=PROTOCOL,owner=OWNER,token=value,**core.runtime.identity(),child=None,phase='reserved',fingerprint=prov['captureFingerprint'],output=str(capture),createdAt=time.time())
     try:
      with core.runtime.LEASE.open('x',encoding='utf8')as handle:json.dump(lease,handle)
     except FileExistsError:pass
     else:token=value;worker.update(leaseToken=token);state['leaseToken']=token;save(STATE,state)
    if token is None:
     if time.monotonic()>=deadline:raise RuntimeError('Finite resource wait ended; all apps/foreign leases preserved')
     time.sleep(10)
   assert authorize()['validatorFingerprint']==prov['validatorFingerprint']and core.busy_reason(token)is None,'Resource/source changed before Unity launch'
   lease=read(core.runtime.LEASE);assert core.runtime.ours(lease)and lease['token']==token;lease['phase']='launching';save(core.runtime.LEASE,lease)
   command=[str(EDITOR),'-batchmode','-projectPath',prov['project'],'-executeMethod',prov['captureEntry'],'-correctionOutput',str(capture),'-correctionFingerprint',prov['captureFingerprint'],'-correctionModes',','.join(missing),'-logFile',str(attempt/'unity.log')]
   save(attempt/'launch-request.json',dict(command=command,captureFingerprint=prov['captureFingerprint'],validatorFingerprint=prov['validatorFingerprint'],requestedModes=missing))
   child=subprocess.Popen(command,cwd=ROOT,creationflags=CREATE);identity=core.runtime.identity(child.pid);worker.update(child=identity);lease.update(child=identity,phase='running');save(core.runtime.LEASE,lease)
   state.update(status='unity-capture-running',child=identity,command=command,gpuStarted=True);save(STATE,state);code=child.wait();state['unityExitCode']=code;save(STATE,state)
   current=authorize(allow_imported_meta=True);assert current['captureFingerprint']==prov['captureFingerprint']and current['validatorFingerprint']==prov['validatorFingerprint'],'Source/QA changed during capture'
   no_live_selected_project(current);found,rejected=inventory(current,freeze=True)
   evidence=publish_native_evidence(found,current,requested,rejected)
   if code:raise RuntimeError('Unity exit'+str(code)+'; completed modes preserved: '+','.join(evidence['completedModes']))
   assert set(requested)<=set(found),'Selected subset incomplete; preserve raw failed modes'
  else:
   state=dict(protocol=PROTOCOL,owner=OWNER,**core.runtime.identity(),child=None,fingerprint=prov['captureFingerprint'],validatorFingerprint=prov['validatorFingerprint'],requestedModes=requested,gpuStarted=False,completed=False)
   evidence=publish_native_evidence(found,current,requested,rejected)
  state.update(status='selected-subset-complete-visual-review-pending',completed=True,completedModes=evidence['completedModes'],fullCorrectionCaptureComplete=evidence['fullCorrectionCaptureComplete'],evidence=str(EVIDENCE),newGpuStarted=child is not None);save(STATE,state)
 except BaseException as error:
  if state:state.update(status='failed-preserved',error=str(error),completed=False,checkedAt=time.time());save(STATE,state)
  raise
 finally:
  live=child is not None and child.poll()is None
  if token and core.runtime.LEASE.exists():
   lease=read(core.runtime.LEASE)
   if core.runtime.ours(lease)and lease['token']==token:
    live=live or core.runtime.unrecorded_child_alive(lease)
    if not live:core.runtime.LEASE.unlink()
  worker.close(remove=not live)
 print(json.dumps(dict(status=state['status'],requestedModes=requested,completedModes=evidence['completedModes'],fullCorrectionCaptureComplete=evidence['fullCorrectionCaptureComplete'],newGpuStarted=child is not None,evidence=str(EVIDENCE))))

if __name__=='__main__':main()
