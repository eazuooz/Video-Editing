"""Finite selected06.02 supplementary native worker; explicit mode subset only.

No default stage/capture. A pilot subset is never all13complete. Physical capture
identity stays separate from CPU validator identity, allowing verified mode reuse.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,shutil,subprocess,time,uuid
from pathlib import Path
import psutil
from initialize import ROOT,HERE,MEDIA,read,save

def load(name,file):
 sp=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

core=load('supplement_isolated_native_primitives','run-prospect-refuge-native.py')
assert core.sha(core.__file__)=='4c7a90bcc4857a643703791db3f03373cdafc7aabc5631d52aaa6dbc2657b0a4','Audit changed native primitive before supplementary use'
prep=load('supplement_source_preparation','prepare-prospect-refuge-supplement.py')
PROTOCOL='architectural111-06-02-supplement-native-v1';OWNER='architectural-111-06-02-supplement-native'
core.runtime.PROTOCOL=PROTOCOL;core.runtime.OWNER=OWNER
FOLDER=prep.FOLDER;SHADER=prep.SHADER;CONTRACT=prep.CONTRACT;MODES=prep.MODES;ENCOUNTERS={'flying','shield','boss'}
core.FOLDER=FOLDER
RECORD=prep.RECORD;STAGING=prep.REPORT;STATE=MEDIA/'06-02-supplement-native-progress.json';WORKER=MEDIA/'06-02-supplement-native-worker.json'
ATTEMPTS=MEDIA/'shorts-leveldesign-06-02/supplementary-native-attempts';EVIDENCE=RECORD/'supplementary-native-evidence-v1.json'
EDITOR=Path(core.EDITOR);CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
sha=core.sha;digest=core.digest;f32=core.f32;near=core.near;vec=core.vec

def selected_modes(text):
 assert isinstance(text,str)and text,'Explicit --modes subset required; no automatic all13'
 rows=text.split(',');assert len(rows)==len(set(rows))and all(m in MODES for m in rows),'Unknown/duplicate/empty supplementary mode'
 return rows

def authorize(allow_imported_meta=False):
 current=prep.preflight();staged=read(STAGING)
 assert staged.get('sourceStageComplete')is True and staged['fingerprint']==current['fingerprint']and staged['files']==current['files'],'Fresh selected supplementary source staging required'
 assert staged['captureContract']==CONTRACT and staged['staticCompilerPreflight']==current['staticCompilerPreflight']
 project=Path(staged['project']).resolve();assert project==Path(current['project']).resolve()and project.parent==(MEDIA/'unity-prospect-refuge-supplement-capture').resolve()
 known={}
 if EVIDENCE.exists():
  previous=read(EVIDENCE)
  if previous.get('preparationFingerprint')==current['fingerprint']:known={r['target']:r for r in previous.get('actualStagedMeta',[])}
 changes=[]
 for row in staged['files']:
  source=(ROOT/row['source']).resolve();target=(project/row['target']).resolve()
  assert source.is_relative_to(ROOT.resolve())and target.is_relative_to(project)
  change=core.staged_input(row,source,target,known,allow_imported_meta)
  if change:changes.append(change)
 for row in staged['externalInputs']+staged['engineApiModules']:assert sha(row['path'])==row['sha256'],'External font/installed core API changed'
 version=core.project_version(project/'ProjectSettings/ProjectVersion.txt',staged['editorVersion'])
 assert EDITOR.is_file();manifest=project/'Packages/manifest.json';prep.validate_manifest(manifest)
 physical=dict(protocol=PROTOCOL,topicId='06.02',preparationFingerprint=current['fingerprint'],editorVersion=version['editorVersion'],
  editorBinarySHA256=sha(EDITOR),projectManifestSHA256=sha(manifest),contract=CONTRACT)
 capture=digest(physical)
 qa=[dict(path=str(p),sha256=sha(p))for p in[Path(__file__),Path(core.__file__),HERE/'run-first-native.py',Path(prep.__file__),HERE/'prepare-prospect-refuge-unity.py',HERE/'prospect-refuge-resource-qualification.py',Path(current['staticCompilerPreflight']['path'])]]
 return dict(protocol=PROTOCOL,owner=OWNER,topicId='06.02',captureFingerprint=capture,validatorFingerprint=digest(dict(captureFingerprint=capture,validatorPins=qa)),
  physicalIdentity=physical,validatorPins=qa,project=str(project),preparationFingerprint=current['fingerprint'],sourcePins=staged['files'],externalInputs=staged['externalInputs'],
  actualStagedMeta=changes,config=current['config'],captureEntry=current['captureEntry'],projectVersionAudit=version['sourceAudit'],sourcePreparationAudit=current['sourcePreparation'])

def command_at(c,frame):
 rows=[r for r in c['encounterCommands']if r['startFrame']<=frame<r['endFrameExclusive']];assert len(rows)==1,'Encounter tape gap/overlap';return rows[0]

def lerp(a,b,t):return f32(f32(a)+f32(f32(f32(b)-f32(a))*min(1.,max(0.,t))))
def progress(frame,start,end):return min(1.,max(0.,f32(f32(frame-start)/f32(end-start))))
def inverse(a,b,value):return min(1.,max(0.,f32(f32(value-f32(a))/f32(f32(b)-f32(a)))))

def scripted_position(mode,frame):
 if mode=='atrium':return dict(x=lerp(-2.4,2.4,progress(frame,120,600)),y=3.,z=f32(-3.4))
 if mode=='courtyard':
  z=lerp(-5.5,4.7,progress(frame,120,600));return dict(x=0.,y=lerp(-.7,0,inverse(-4.1,-2.6,z)),z=z)
 if mode=='alcove':
  return dict(x=lerp(0,3,progress(frame,120,300)),y=0.,z=-4.)if frame<300 else dict(x=3.,y=0.,z=lerp(-4,1.2,progress(frame,300,600)))
 if mode=='openings':
  z=lerp(-4.5,3.5,progress(frame,240,660));return dict(x=f32(3.6),y=lerp(0,3,inverse(-3.5,2.5,z)),z=z)
 if mode=='plaza':return dict(x=lerp(-4,4,progress(frame,120,600)),y=f32(1.6),z=f32(-2.8))
 if mode=='footings':return dict(x=lerp(-4,0,progress(frame,390,570))if frame<570 else lerp(0,4,progress(frame,570,690)),y=f32(.4),z=0.)
 if mode=='refuge':return dict(x=0.,y=f32(-.65),z=-2.)
 if mode=='protected':return dict(x=0.,y=0.,z=-2.)
 return dict(x=0.,y=0.,z=0.)

def expected_phase(mode,frame,c):
 if mode=='scale':return'narrow-to-intimate-boundary'if frame<240 else'intimate-to-open-boundary'
 if mode=='structure':return'columns-reveal-illustrated-support'if frame<240 else'wall-panels-withdraw-not-stress-simulation'
 if mode=='openings':return'ribbon-window-opening'if frame<240 else'interior-partitions-withdraw'if frame<420 else'ramp-to-usable-roof'
 if mode=='courtyard':return'scripted-observe'if frame<120 else'scripted-cross'if frame<600 else'scripted-new-observation'
 if mode=='alcove':return'projecting-wall-conceals-target'if frame<300 else'walk-around-projection'if frame<600 else'target-revealed'
 if mode=='footings':return'own-tool-illustration-lifts-board'if frame<180 else'place-board-across-open-ground'if frame<360 else'scripted-cross-supports-not-hazard-simulation'if frame<690 else'new-support-position'
 return command_at(c,frame)['id']if mode in ENCOUNTERS else'purposeful-outlook-and-section'

def expected_camera_eye(mode,frame,position,c):
 if mode in ENCOUNTERS:return dict(x=0.,y=f32(3.8),z=f32(-12.5))
 if mode=='scale':return dict(x=6.,y=4.,z=-8.)
 if mode=='structure':
  t=progress(frame,120,660);return dict(x=lerp(8,7,t),y=lerp(5,4,t),z=lerp(-10,-8,t))
 if mode=='footings':return dict(x=7.,y=5.,z=-10.)
 return dict(x=position['x'],y=f32(position['y']+f32(c['playerEyeHeight'])),z=position['z'])

def finite_vector(value):
 assert isinstance(value,dict)and set(value)=={'x','y','z'}and all(type(v)in(int,float)and math.isfinite(v)for v in value.values()),'Nonfinite/malformed native vector'

def check_ray(ray):
 assert isinstance(ray['id'],str)and ray['id']and isinstance(ray['meaning'],str)
 for key in('origin','desiredEndpoint','actualEndpoint'):finite_vector(ray[key])
 assert type(ray['blocked'])is bool
 a,b,h=(ray[k]for k in('origin','desiredEndpoint','actualEndpoint'));delta=[b[k]-a[k]for k in'xyz'];actual=[h[k]-a[k]for k in'xyz'];length=math.sqrt(sum(x*x for x in delta));hit=math.sqrt(sum(x*x for x in actual))
 assert near(ray['distance'],length)and hit<=length+.0002,'Ray distance/clipped hit escaped its declared segment'
 if ray['blocked']:
  assert isinstance(ray['hitCollider'],str)and ray['hitCollider'],'Blocked ray lacks actual collider'
  if length>1e-7:
   t=sum(x*y for x,y in zip(delta,actual))/(length*length)
   assert -.0002<=t<=1.0002 and math.sqrt(sum((actual[i]-t*delta[i])**2 for i in range(3)))<.0002,'Ray hit not collinear'
 else:assert vec(h,b)and ray['hitCollider']in(None,''),'Unblocked ray endpoint differs'

def check_projectiles(rows,frame,previous,c):
 assert isinstance(rows,list)and len({r['id']for r in rows})==len(rows),'Duplicate/malformed projectile IDs'
 old={p['id']:p for p in previous};new={p['id']:p for p in rows};assert set(old)<=set(new),'Projectile history disappeared'
 for p in rows:
  assert p['team']in('player','enemy')and type(p['alive'])is type(p['hit'])is bool
  assert type(p['hitAtFrame'])is int
  assert type(p['createdAtAppliedFrame'])is int and 0<=p['createdAtAppliedFrame']<frame
  for key in('previous','position','velocity','actualHitPoint'):finite_vector(p[key])
  speed=math.sqrt(sum(v*v for v in p['velocity'].values()));assert near(speed,c['shotSpeed']if p['team']=='player'else c['enemyShotSpeed']), 'Projectile speed differs from pinned config'
  if p['team']=='player':assert vec(p['velocity'],dict(x=c['shotSpeed'],y=0,z=0))
  if p['team']=='player':assert p['createdAtAppliedFrame']in c['fireFrames'],'Player shot outside exact fire tape'
  else:assert 150<=p['createdAtAppliedFrame']<600 and p['createdAtAppliedFrame']%120 in(30,42,54),'Enemy burst clock differs'
  if p['id']in old:
   before=old[p['id']];assert all(p[k]==before[k]for k in('team','createdAtAppliedFrame','velocity')),'Projectile identity/velocity changed'
   if before['alive']:assert vec(p['previous'],before['position'])
   else:assert all(p[k]==before[k]for k in('previous','position','alive','hit','hitCollider','hitAtFrame','actualHitPoint')),'Stopped projectile state changed'
  moving=p['id']not in old or old[p['id']]['alive']
  if moving:
   a,b=p['previous'],p['position'];distance=math.sqrt(sum((a[k]-b[k])**2 for k in'xyz'))
   if p['hit']:assert distance<=speed/60+.0002,'Projectile hit exceeded current step'
   else:assert vec(b,{k:f32(a[k]+f32(p['velocity'][k]*f32(1/60)))for k in'xyz'}),'Projectile step clock differs'
  if p['hit']:assert not p['alive']and p['hitCollider']and 0<p['hitAtFrame']<=frame and vec(p['position'],p['actualHitPoint'])
  else:assert p['hitAtFrame']==-1 and p['hitCollider']in(None,'')

def check_mode(folder,mode,prov,decode=True):
 folder=Path(folder);c=prov['config'];assert mode in MODES
 rec=read(folder/'mode-complete.json');assert rec==read(folder/'mode-contract.json'),'Incomplete/changed per-mode completion receipt'
 expected=dict(fingerprint=prov['captureFingerprint'],mode=mode,sourceKind='our-authored-illustration',**{k:v for k,v in CONTRACT.items()if k!='modes'})
 assert all(rec.get(k)==v for k,v in expected.items()),'Mode fingerprint/clock/camera contract differs'
 assert rec['actualSceneSaved']is True and rec['actualScenePath']==FOLDER+'/'+next(r['sceneFile']for r in c['scenes']if r['mode']==mode)
 assert sha(folder/'config.json')==rec['configSHA256']==sha(prep.SOURCE/'config.json'),'Raw config/tape provenance differs'
 core.validate_capture_config(read(folder/'config.json'),c);assert rec['frameConvention']==c['frameConvention']
 states=[json.loads(line)for line in(folder/'states.jsonl').read_text(encoding='utf8').splitlines()]
 rays=[json.loads(line)for line in(folder/'rays.jsonl').read_text(encoding='utf8').splitlines()]
 anchors=[json.loads(line)for line in(folder/'projected-anchors.jsonl').read_text(encoding='utf8').splitlines()]
 assert all(len(rows)==720 and[r['frame']for r in rows]==list(range(720))for rows in(states,rays,anchors)),'Missing/unordered native states/rays/anchors'
 before=None;vertical=0.;ray_ids=None;anchor_ids=None;collisions=0;hits={};grounded_flag=4
 for frame,(s,rr,aa)in enumerate(zip(states,rays,anchors)):
  assert s['mode']==mode and s['sourceKind']=='our-authored-illustration'and near(s['timeSeconds'],f32(frame/60),1e-7)
  assert s['phase']==expected_phase(mode,frame,c),'Illustration phase/current command clock differs'
  assert s['appliedCommandFrame']==frame-1 and type(s['collisionFlags'])is int and 0<=s['collisionFlags']<=7
  for key in('playerPosition','requestedPlayerPosition','actualMoveDelta','enemyPosition','secondEnemyPosition','playerCameraEye','playerCameraEuler','observerCameraEye','observerCameraEuler'):finite_vector(s[key])
  assert vec(s['observerCameraEye'],c['observerPosition'])and vec(s['playerCameraEye'],expected_camera_eye(mode,frame,s['playerPosition'],c)),'Camera eye detached from declared state'
  assert type(s['appliedJump'])is type(s['appliedFire'])is bool
  if not frame:
   assert s['appliedCommandId']=='initial-state'and not s['appliedJump']and not s['appliedFire']and vec(s['actualMoveDelta'],dict(x=0,y=0,z=0))and vec(s['requestedPlayerPosition'],s['playerPosition'])
   assert vec(s['playerPosition'],dict(x=-5,y=0,z=0)if mode in ENCOUNTERS else scripted_position(mode,0))
  else:
   assert vec(s['actualMoveDelta'],{k:s['playerPosition'][k]-before['playerPosition'][k]for k in'xyz'}),'Actual movement recurrence differs'
   if mode in ENCOUNTERS:
    cmd=command_at(c,frame-1);assert s['appliedCommandId']==cmd['id']and s['appliedJump']==(frame-1 in c['jumpFrames'])and s['appliedFire']==(frame-1 in c['fireFrames']),'Encounter command/jump/fire tape differs'
    grounded=bool(before['collisionFlags']&grounded_flag)
    if grounded and vertical<0:vertical=f32(-.25)
    if grounded and s['appliedJump']:vertical=f32(c['jumpSpeed'])
    dt=f32(1/60);vertical=f32(vertical-f32(f32(c['gravity'])*dt))
    wanted=dict(x=f32(before['playerPosition']['x']+f32(f32(cmd['velocityX'])*dt)),y=f32(before['playerPosition']['y']+f32(vertical*dt)),z=before['playerPosition']['z'])
    assert vec(s['requestedPlayerPosition'],wanted),'Physical Move requested input/gravity clock differs'
   else:
    assert s['appliedCommandId']=='scripted-geometric-illustration-route'and not s['appliedJump']and not s['appliedFire']and s['collisionFlags']==0
    assert vec(s['playerPosition'],scripted_position(mode,frame))and vec(s['requestedPlayerPosition'],s['playerPosition']),'Declared scripted illustration route differs'
  assert s['motionKind']==('CharacterController.Move with exact shared run/jump/fire tape'if mode in ENCOUNTERS else'declared scripted geometric illustration route')
  assert s['rays']==rr['rays'];ids=[r['id']for r in s['rays']];assert len(ids)==len(set(ids))
  if ray_ids is None:ray_ids=ids
  assert ids==ray_ids,'Ray binding IDs changed'
  for ray in s['rays']:check_ray(ray)
  check_projectiles(s['projectiles'],frame,before['projectiles']if before else[],c)
  old_ids={p['id']for p in before['projectiles']}if before else set();new=[p for p in s['projectiles']if p['id']not in old_ids]
  assert[p['id']for p in s['projectiles']]==['Own projectile '+str(i)for i in range(len(s['projectiles']))],'Projectile creation sequence differs'
  if mode in ENCOUNTERS:
   applied=frame-1;enemy_fire=150<=applied<600 and applied%120 in(30,42,54)
   assert sum(p['team']=='player'for p in new)==int(s['appliedFire'])and sum(p['team']=='enemy'for p in new)==int(enemy_fire),'Exact shared player/enemy fire clock differs'
   for projectile in new:
    if projectile['team']=='player':origin=dict(x=f32(s['playerPosition']['x']+.5),y=f32(s['playerPosition']['y']+1.),z=s['playerPosition']['z'])
    else:
     origin=dict(x=f32(before['enemyPosition']['x']-.6),y=f32(before['enemyPosition']['y']+(2. if mode=='boss'else 1.1)),z=before['enemyPosition']['z'])
     target=dict(s['playerPosition']);target['y']+=.95;aim={k:target[k]-origin[k]for k in'xyz'};length=math.sqrt(sum(v*v for v in aim.values()))
     assert length>0 and vec(projectile['velocity'],{k:v/length*c['enemyShotSpeed']for k,v in aim.items()}),'Enemy shot detached from own actual origin/target'
    assert vec(projectile['previous'],origin),'Projectile spawn detached from actual current actor state'
  if mode not in ENCOUNTERS:assert not s['projectiles'],'Scripted architecture illustration spawned encounter projectiles'
  for p in s['projectiles']:
   if p['hit']:hits[p['id']]=dict(team=p['team'],frame=p['hitAtFrame'],collider=p['hitCollider'])
  ids=[a['id']for a in aa['anchors']];assert ids and len(ids)==len(set(ids))
  if anchor_ids is None:anchor_ids=ids
  assert ids==anchor_ids,'Projected anchor IDs changed'
  for a in aa['anchors']:
   assert isinstance(a['role'],str)and type(a['active'])is bool
   for key in('world','playerViewport','observerViewport'):finite_vector(a[key])
   for name,view in(('playerInFrustum','playerViewport'),('observerInFrustum','observerViewport')):
    p=a[view];assert type(a[name])is bool and a[name]==(p['z']>0 and 0<=p['x']<=1 and 0<=p['y']<=1),'Frustum flag differs; it is not occlusion visibility'
  if s['collisionFlags']:collisions+=1
  before=s
 for camera in CONTRACT['cameras']:
  paths=sorted((folder/camera).glob('*.jpg'));assert[p.name for p in paths]==[f'{i:04}.jpg'for i in range(720)],'Missing/extra native camera frames'
  if decode:
   from PIL import Image
   for frame in[0,119,120,210,300,420,450,600,719]:
    with Image.open(paths[frame])as image:image.load();assert image.size==(1920,1080),'Decoded source is not FHD'
 return dict(mode=mode,frames=720,collisionFlagFrames=collisions,actualProjectileHits=hits,rayIds=ray_ids,anchorIds=anchor_ids,
  motionKind=states[0]['motionKind'],actualVisualReview=False,wholeMeshVisibilityMeasured=False,humanDecisionMeasured=False)

def scoped_file(folder,path):
 parts=path.replace('\\','/').split('/');assert parts and all(p not in('','.','..')for p in parts)and not Path(path).is_absolute(),'Noncanonical snapshot/export path'
 assert path.startswith(FOLDER+'/')or path==FOLDER+'.meta','Supplementary scene export escaped owned subtree'
 target=(Path(folder)/path).resolve();assert target.is_relative_to(Path(folder).resolve());return target

def validate_scene_record(folder,mode,prov,freeze=False):
 folder=Path(folder);record=read(folder/'scene-record.json');scene=FOLDER+'/'+next(r['sceneFile']for r in prov['config']['scenes']if r['mode']==mode)
 assert record['fingerprint']==prov['captureFingerprint']and record['mode']==mode and record['sourceKind']=='our-authored-illustration'
 assert record['actualSceneFilesSaved']is True and record['scenePaths']==[scene]and record['unityVersion']==prov['physicalIdentity']['editorVersion']
 assert len(record['animationClipNames'])==2 and any(n.endswith('Walking_A')for n in record['animationClipNames'])and any(n=='Idle'or n.endswith('|Idle')for n in record['animationClipNames'])
 rows=record['files'];assert rows and len({r['path'].casefold()for r in rows})==len(rows)and scene in{r['path']for r in rows}
 native_inputs={r['target']:r['sha256']for r in prov['sourcePins']if r['target'].startswith(FOLDER+'/')}
 assert {FOLDER+'/Experiment.cs',FOLDER+'/Editor/EditorBuilder.cs',FOLDER+'/config.json'}<=set(native_inputs)<={r['path']for r in rows},'Editable source/config missing from actual scene record'
 project=Path(prov['project']);snapshot=folder/'editable-snapshot';pins=[]
 for row in rows:
  if row['path']in native_inputs:assert row['sha256']==native_inputs[row['path']],'Saved native source differs from original physical pins'
  assert not Path(row['path']).suffix.lower()in('.ttf','.otf'),'Installed font binary must not enter exported assets'
  source=scoped_file(project,row['path']);target=scoped_file(snapshot,row['path'])
  actual=target if target.exists()else source
  assert actual.stat().st_size==row['bytes']and sha(actual)==row['sha256'],'Actual saved scene/dependency changed; preserve old attempt'
  if freeze and not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(actual,target)
  pins.append(dict(path=row['path'],sha256=row['sha256'],bytes=row['bytes']))
 required_dependencies={SHADER,SHADER+'.meta'}|{'Assets/ThirdParty/KayKitAdventurers/'+name for name in('Knight.fbx','Knight.fbx.meta','knight_texture.png','knight_texture.png.meta','LICENSE.txt','LICENSE.txt.meta','provenance.json','provenance.json.meta')}
 assert len(record['dependencies'])==len(required_dependencies)and{r['path']for r in record['dependencies']}==required_dependencies,'Missing/duplicate/unexpected shared source dependencies'
 for row in record['dependencies']:
  name=row['path'];rel=Path(name);assert not rel.is_absolute()and '..'not in rel.parts
  assert name in(SHADER,SHADER+'.meta')or(name.startswith('Assets/ThirdParty/KayKitAdventurers/')and rel.name in('Knight.fbx','Knight.fbx.meta','knight_texture.png','knight_texture.png.meta','LICENSE.txt','LICENSE.txt.meta','provenance.json','provenance.json.meta')),'Unexpected shared dependency'
  staged=project/rel;assert staged.stat().st_size==row['bytes']and sha(staged)==row['sha256'],'Actual shared dependency changed'
  original=ROOT/'unity/VideoEditing'/rel
  assert original.is_file()or name=='Assets/ThirdParty/KayKitAdventurers/provenance.json.meta','Original shared source missing'
  if original.exists()and sha(original)!=row['sha256']:assert rel.suffix=='.meta'and core.meta_guid(original)==core.meta_guid(staged),'Shared asset/source differs'
 return dict(scenePath=scene,files=pins,record=dict(path=str(folder/'scene-record.json'),sha256=sha(folder/'scene-record.json')),snapshotRoot=str(snapshot))

def mode_proof(folder,mode,prov,freeze=False):
 folder=Path(folder);summary=check_mode(folder,mode,prov);scene=validate_scene_record(folder,mode,prov,freeze)
 files=['config.json','mode-contract.json','mode-complete.json','scene-record.json','states.jsonl','rays.jsonl','projected-anchors.jsonl']
 proof=dict(schemaVersion='06.02-supplement-mode-proof-v1',mode=mode,captureFingerprint=prov['captureFingerprint'],validatorFingerprint=prov['validatorFingerprint'],
  sourceKind='our-authored-illustration',modeFolder=str(folder),summary=summary,sceneSnapshot=scene,
  files=[dict(path=name,sha256=sha(folder/name))for name in files],actualStagedMeta=prov['actualStagedMeta'],humanApproval=False,voicePreparationAllowed=False)
 framefile=folder/'frame-hashes-v1.json'
 if framefile.exists():
  prior=read(framefile);assert prior['captureFingerprint']==prov['captureFingerprint']and prior['mode']==mode
  expected={camera+'/'+f'{f:04}.jpg'for camera in CONTRACT['cameras']for f in range(720)}
  assert len(prior['frames'])==len(expected)and{r['path']for r in prior['frames']}==expected
  for row in prior['frames']:
   path=(folder/row['path']).resolve();assert path.is_relative_to(folder.resolve())and path.stat().st_size==row['bytes']and sha(path)==row['sha256'],'Immutable completed frame changed; inspect instead of auto recapture'
 if freeze:
  rows=[dict(path=p.relative_to(folder).as_posix(),sha256=sha(p),bytes=p.stat().st_size)for camera in CONTRACT['cameras']for p in sorted((folder/camera).glob('*.jpg'))]
  frame_record=dict(captureFingerprint=prov['captureFingerprint'],mode=mode,frames=rows)
  if framefile.exists():assert read(framefile)==frame_record,'Prior frame proof changed'
  else:save(framefile,frame_record)
  proof['frameHashManifest']=dict(path=str(framefile),sha256=sha(framefile))
  target=folder/('mode-proof-'+prov['validatorFingerprint'][:24]+'.json')
  if target.exists():assert read(target)==proof,'Prior current-validator mode proof changed'
  else:save(target,proof)
  proof['proofFile']=dict(path=str(target),sha256=sha(target))
 return proof

def cached_mode(folder,mode,prov):
 """Read actual data afresh. QA source changes never relabel original capture."""
 return mode_proof(folder,mode,prov,freeze=False)

def inventory(prov,freeze=False):
 found={};rejected=[]
 for attempt in sorted(ATTEMPTS.glob('*'),reverse=True)if ATTEMPTS.exists()else[]:
  try:
   old=read(attempt/'input-provenance.json')
   assert old['protocol']==PROTOCOL and old['owner']==OWNER and old['captureFingerprint']==prov['captureFingerprint']==digest(old['physicalIdentity'])and old['physicalIdentity']==prov['physicalIdentity']
   assert old['project']==prov['project']and old['sourcePins']==prov['sourcePins']and old['externalInputs']==prov['externalInputs']
  except(OSError,ValueError,KeyError,AssertionError):continue
  for mode in MODES:
   if mode in found:continue
   folder=attempt/'capture'/mode
   if not(folder/'mode-complete.json').exists():continue
   try:found[mode]=mode_proof(folder,mode,prov,freeze)
   except(OSError,ValueError,KeyError,AssertionError)as error:rejected.append(dict(mode=mode,folder=str(folder),reason=str(error)))
 return found,rejected

def export_modes(proofs,prov):
 """Copy only source-pinned own assets; shared assets/font binaries preserved."""
 exports={}
 for mode,proof in proofs.items():
  root=Path(proof['sceneSnapshot']['snapshotRoot'])
  for row in proof['sceneSnapshot']['files']:
   source=scoped_file(root,row['path']);assert source.stat().st_size==row['bytes']and sha(source)==row['sha256'],'Frozen editable source changed'
   target=scoped_file(ROOT/'unity/VideoEditing',row['path'])
   if row['path']in exports:assert exports[row['path']][2]==row['sha256'],'Conflicting source versions for same capture identity'
   assert not target.exists()or sha(target)==row['sha256'],'Preserve changed selected supplementary asset; explicit revision/archive required'
   exports[row['path']]=(source,target,row['sha256'])
 for source,target,value in exports.values():
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copy2(source,target)
  assert sha(target)==value
 return[dict(path=str(target.relative_to(ROOT)),sha256=value)for source,target,value in exports.values()]

def publish_native_evidence(proofs,prov,requested,rejected):
 exported=export_modes(proofs,prov)
 data=dict(schemaVersion='06.02-supplementary-native-evidence-v1',topicId='06.02',captureFingerprint=prov['captureFingerprint'],validatorFingerprint=prov['validatorFingerprint'],
  preparationFingerprint=prov['preparationFingerprint'],sourceKind='our-authored-illustration',requestedModes=requested,completedModes=[m for m in MODES if m in proofs],
  fullSupplementaryCaptureComplete=set(proofs)==set(MODES),selectedSubsetComplete=set(requested)<=set(proofs),modes=proofs,exportedFiles=exported,
  actualStagedMeta=prov['actualStagedMeta'],rejectedPriorModeAttempts=rejected,actualVisualReview=False,voicePreparationAllowed=False,humanApproval=False,platformActions=[],
  measurementLimits='Own scripted architecture paths versus actual CharacterController/projectile encounter trials are explicit per mode; sample rays/frustum flags are not whole-mesh visibility, commercial AI, structural safety or human behavior.')
 if EVIDENCE.exists():
  old=read(EVIDENCE)
  if old.get('captureFingerprint')==prov['captureFingerprint']:
   if set(old.get('completedModes',[]))==set(data['completedModes']):
    for field in('actualVisualReview','voicePreparationAllowed','humanApproval','platformActions'):data[field]=old.get(field,data[field])
   else:data['priorReviewScopes']=old.get('priorReviewScopes',[])+[dict(completedModes=old.get('completedModes',[]),**{field:old.get(field)for field in('actualVisualReview','voicePreparationAllowed','humanApproval','platformActions')})]
  else:
   history=MEDIA/'shorts-leveldesign-06-02/supplementary-evidence-history';history.mkdir(parents=True,exist_ok=True);shutil.copy2(EVIDENCE,history/(sha(EVIDENCE)+'.json'))
 save(EVIDENCE,data);return data

def no_live_selected_project(prov):
 for process in psutil.process_iter(['name','cmdline']):
  try:
   if(process.info['name']or'').lower()!='unity.exe':continue
   args=process.info['cmdline']
   if args is None:raise RuntimeError('Unreadable Unity process preserved before CPU source snapshot')
   if '-projectPath'in args and Path(args[args.index('-projectPath')+1]).resolve()==Path(prov['project']).resolve():raise RuntimeError('Selected supplementary Unity process remains live; preserve it')
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:raise RuntimeError('Unknown Unity process preserved')

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');parser.add_argument('--modes');parser.add_argument('--wait-hours',type=float,default=2);args=parser.parse_args()
 assert math.isfinite(args.wait_hours)and 0<=args.wait_hours<=24
 try:requested=selected_modes(args.modes);prov=authorize()
 except(FileNotFoundError,KeyError,AssertionError)as error:
  if args.execute:raise
  print(json.dumps(dict(ready=False,reason=str(error),newGpuStarted=False)));return
 if not args.execute:
  found,rejected=inventory(prov);print(json.dumps(dict(ready=True,captureFingerprint=prov['captureFingerprint'],validatorFingerprint=prov['validatorFingerprint'],requestedModes=requested,reusableModes=list(found),fullSupplementaryCaptureComplete=set(found)==set(MODES),resourceWait=core.busy_reason(),newGpuStarted=False)));return
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
   command=[str(EDITOR),'-batchmode','-projectPath',prov['project'],'-executeMethod',prov['captureEntry'],'-supplementOutput',str(capture),'-supplementFingerprint',prov['captureFingerprint'],'-supplementModes',','.join(missing),'-logFile',str(attempt/'unity.log')]
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
  state.update(status='selected-subset-complete-visual-review-pending',completed=True,completedModes=evidence['completedModes'],fullSupplementaryCaptureComplete=evidence['fullSupplementaryCaptureComplete'],evidence=str(EVIDENCE),newGpuStarted=child is not None);save(STATE,state)
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
 print(json.dumps(dict(status=state['status'],requestedModes=requested,completedModes=evidence['completedModes'],fullSupplementaryCaptureComplete=evidence['fullSupplementaryCaptureComplete'],newGpuStarted=child is not None,evidence=str(EVIDENCE))))

if __name__=='__main__':main()
