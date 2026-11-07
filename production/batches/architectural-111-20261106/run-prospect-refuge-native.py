"""Finite06.02 capture; read-only preflight by default, one owned lease/worker.

Reuse the proven singleton/resource functions in an isolated module instance;
never edit or update the first film's source, worker, state or deliverables.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,os,re,shutil,struct,subprocess,time,uuid
from pathlib import Path
import psutil
from initialize import ROOT,HERE,MEDIA,AUTH_KEY,read,save

spec=importlib.util.spec_from_file_location('prospect_refuge_native_resource_runtime',HERE/'run-first-native.py')
runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
PROTOCOL='architectural111-06-02-native-v1';OWNER='architectural-111-06-02-native'
runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
PROJECT_RECORD=ROOT/'projects/shorts-leveldesign-06-02'
PREP=PROJECT_RECORD/'unity-staging-v1.json';STATE=MEDIA/'06-02-native-progress.json';WORKER=MEDIA/'06-02-native-worker.json'
ATTEMPTS=MEDIA/'shorts-leveldesign-06-02/native-attempts';EDITOR=Path(runtime.EDITOR)
UNITY_ROOT=ROOT/'unity/VideoEditing';FOLDER='Assets/VideoScenes/architectural-111-20261106/06-02'
CONTRACT=dict(frames=600,width=1920,height=1080,fps=60,cameras=['player','observer'],modes=['baseline','shifted'])
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
def sha(path):
 with Path(path).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def busy_reason(own_token=None):
 reason=runtime.busy_reason(own_token)
 if reason:return reason
 headless=set()
 games={'sc2_x64.exe','starcraft.exe','starcraft64.exe','diabloiii.exe','noita.exe','teardown.exe','factorio.exe','valheim.exe','cs2.exe','hl2.exe','left4dead2.exe'}
 for process in psutil.process_iter(['name','cmdline']):
  try:
   name=(process.info['name']or'').lower();args=process.info['cmdline']or[]
   if name.startswith('python')and any(k in' '.join(args).lower()for k in('--recognize','--synthesize','render_narration','faster_whisper','torchrun')):return 'Another native/model child is running'
   if name in games:return 'User game process is running; preserve it and wait'
   if name=='unrealeditor-cmd.exe':return 'Another Unreal command-line renderer is running'
   if name in('chrome.exe','msedge.exe','chromium.exe'):
    if process.info['cmdline']is None:return 'Unreadable browser process preserved; resource state unknown'
    if any(x.startswith('--headless')for x in args):headless.add(process.pid)
  except(psutil.NoSuchProcess,psutil.AccessDenied):continue
 if headless:
  spec=importlib.util.spec_from_file_location('prospect_refuge_exact_resource_qualification',HERE/'prospect-refuge-resource-qualification.py')
  qualification=importlib.util.module_from_spec(spec);spec.loader.exec_module(qualification)
  result=qualification.qualify(lambda:runtime.busy_reason(own_token))
  if not result['qualified']:return result['reason']or'Headless browser resource qualification unknown'
  if not headless<=set(result['qualifiedPids']):return 'Another unverified headless browser/render job is running'
 return None

def meta_guid(path):
 matches=re.findall(r'^guid:\s*([0-9a-f]{32})\s*$',Path(path).read_text(encoding='utf-8-sig'),re.M|re.I)
 assert len(matches)==1,'Imported metadata lacks one canonical GUID';return matches[0].lower()

def staged_input(row,source,target,known,allow_imported_meta=False):
 assert sha(source)==row['sha256'],'Original source input changed'
 staged_sha=sha(target)
 if staged_sha==row['sha256']:return None
 assert source.suffix.lower()==target.suffix.lower()=='.meta','Staged native input changed'
 guid=meta_guid(source);assert meta_guid(target)==guid,'Staged import changed source GUID'
 change=dict(target=row['target'],sourceSHA256=row['sha256'],stagedSHA256=staged_sha,guid=guid)
 assert allow_imported_meta or known.get(row['target'])==change,'Unrecorded staged metadata change; inspect before GPU launch'
 return change

def float32_bits(value):
 assert type(value) in (int,float) and math.isfinite(value),'Finite nonboolean numeric config required'
 try:bits=struct.pack('<f',value)
 except (OverflowError,struct.error):raise AssertionError('Config value exceeds finite float32')
 assert math.isfinite(struct.unpack('<f',bits)[0]),'Config value exceeds finite float32'
 return bits

def validate_capture_config(actual,expected):
 if isinstance(expected,dict):
  assert isinstance(actual,dict)and actual.keys()==expected.keys(),'Capture config keys differ'
  for k,v in expected.items():validate_capture_config(actual[k],v)
 elif isinstance(expected,list):
  assert isinstance(actual,list)and len(actual)==len(expected),'Capture config list differs'
  for a,b in zip(actual,expected):validate_capture_config(a,b)
 elif type(expected)is int:assert type(actual)is int and actual==expected,'Exact integer config differs'
 elif type(expected)is float:assert float32_bits(actual)==float32_bits(expected),'Float32 config differs'
 else:assert type(actual)is type(expected)and actual==expected,'Literal config differs'

def project_version(path,expected):
 fields={}
 for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
  if not line.strip():continue
  key,separator,value=line.partition(':');key=key.strip();value=value.strip()
  assert separator and key in ('m_EditorVersion','m_EditorVersionWithRevision') and key not in fields,'Unexpected or duplicate project version field'
  fields[key]=value
 assert fields.get('m_EditorVersion')==expected,'Canonical Unity editor version changed'
 revision=None
 if 'm_EditorVersionWithRevision' in fields:
  match=re.fullmatch(re.escape(expected)+r'\s*\(([0-9a-fA-F]{12})\)',fields['m_EditorVersionWithRevision'])
  assert match,'Unity revision must retain canonical editor version and12hex identifier'
  revision=match[1].lower()
 return dict(editorVersion=expected,sourceAudit=dict(path=str(Path(path).resolve()),sha256=sha(path),withRevision=revision))

def preparation_module():
 spec=importlib.util.spec_from_file_location('prospect_refuge_source_staging_contract',HERE/'prepare-prospect-refuge-unity.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def authorize(allow_imported_meta=False):
 prepare=preparation_module();current=prepare.preflight();prep=read(PREP)
 assert prep['sourceStageComplete']and prep['captureContract']==CONTRACT and prep['topicId']=='06.02'
 assert prep['fingerprint']==current['fingerprint'],'Prepared source/config/tape/provenance changed'
 assert prep['files']==current['files']and prep['staticCompilerPreflight']==current['staticCompilerPreflight']and prep['staticCompilerPreflight'],'Fresh source-bound static compile required'
 project=Path(prep['project']).resolve();assert project==(MEDIA/'unity-prospect-refuge-capture').resolve()
 pins=[];meta_changes=[]
 previous=read(PROJECT_RECORD/'native-evidence-v1.json')if(PROJECT_RECORD/'native-evidence-v1.json').exists()else{}
 known={r['target']:r for r in previous.get('actualStagedMeta',[])if previous.get('topicId')=='06.02'and previous.get('captureComplete')}
 for row in prep['files']:
  source=(ROOT/row['source']).resolve();target=(project/row['target']).resolve()
  assert source.is_relative_to(ROOT.resolve())and target.is_relative_to(project)
  change=staged_input(row,source,target,known,allow_imported_meta)
  if change:meta_changes.append(change)
  pins.append(dict(source=row['source'],target=row['target'],sha256=row['sha256']))
 version=project_version(project/'ProjectSettings/ProjectVersion.txt',prep['editorVersion'])
 for path in[Path(__file__),HERE/'prospect-refuge-resource-qualification.py',HERE/'run-first-native.py',HERE/'prepare-prospect-refuge-unity.py',Path(prep['staticCompilerPreflight']['path']),project/'Packages/manifest.json']:
  pins.append(dict(path=str(path),sha256=sha(path)))
 assert EDITOR.is_file();assert shutil.disk_usage(MEDIA).free>=5*1024**3,'Insufficient C space for600frames x2cases x2cameras and reserve'
 result=dict(protocol=PROTOCOL,topicId='06.02',preparationFingerprint=prep['fingerprint'],project=str(project),captureEntry=prep['captureEntry'],contract=CONTRACT,editorVersion=version['editorVersion'],pins=pins)
 result['fingerprint']=digest(result);result['stagedMetaChanges']=meta_changes;result['projectVersionAudit']=version['sourceAudit'];result['stagingAudit']=dict(path=str(PREP),sha256=sha(PREP));result['sourcePreparationAudit']=current['sourcePreparation'];return result

def export_paths(value,project):
 parts=value.replace('\\','/').split('/')
 assert all(p not in ('','.','..') for p in parts),'Noncanonical export path'
 rel=Path(value);assert not rel.is_absolute()
 source=(project/rel).resolve();target=(UNITY_ROOT/rel).resolve()
 owned_source=project/FOLDER;owned_target=UNITY_ROOT/FOLDER
 assert owned_source.resolve()==owned_source and owned_target.resolve()==owned_target,'Owned export roots must not redirect to another scene'
 if value==FOLDER+'.meta':assert source==Path(str(owned_source)+'.meta') and target==Path(str(owned_target)+'.meta')
 else:assert source.is_relative_to(owned_source) and target.is_relative_to(owned_target),'Export escaped exact06.02 subtree'
 return source,target

def command_at(c,f):
 rows=[r for r in c['commands']if r['startFrame']<=f<r['endFrameExclusive']];assert len(rows)==1,'Input tape gap/overlap';return rows[0]
def near(a,b,tolerance=.0002):return math.isfinite(float(a))and math.isfinite(float(b))and abs(float(a)-float(b))<=tolerance
def vec(a,b):return set(a)==set(b)=={'x','y','z'}and all(near(a[k],b[k])for k in a)
def f32(value):return struct.unpack('<f',struct.pack('<f',value))[0]
def enemy_at(c,f):
 # Exact C# float clock/config/operator order and Mathf.Lerp; no wider tolerance.
 t=f32(f32(f)/f32(c['fps']));start=f32(c['enemyTurnStartSeconds']);turn=f32(c['enemyTurnEndSeconds']);pause=f32(c['enemyPauseStartSeconds']);speed=f32(c['enemyWalkSpeed']);base=f32(c['enemyStartX'])
 if t<start:return(f32(base+f32(speed*t)),90.,'patrol-outbound')
 turn_x=f32(base+f32(speed*start))
 if t<turn:
  alpha=f32(f32(t-start)/f32(turn-start));alpha=min(1.,max(0.,alpha))
  return(turn_x,f32(90.+f32(180.*alpha)),'scripted-waypoint-turn')
 return(f32(turn_x-f32(speed*f32(min(t,pause)-turn))),270.,'patrol-return'if t<pause else'scripted-waypoint-pause')
def check_ray(ray,origin,target,camera=False,range_limit=20.,half_fov=70.,yaw=0.):
 for v in(ray['origin'],ray['desiredEndpoint'],ray['actualEndpoint']):assert set(v)=={'x','y','z'}and all(type(n)in(int,float)and math.isfinite(n)for n in v.values())
 assert vec(ray['origin'],origin)and vec(ray['desiredEndpoint'],target),'Ray detached from actual state'
 for k in('blocked','inRange','inFieldOfView','cameraInFrustum','seen'):assert type(ray[k])is bool
 assert ray['seen']==(not ray['blocked']and ray['inRange']and(ray['cameraInFrustum']if camera else ray['inFieldOfView'])),'Visibility rule differs'
 dx=target['x']-origin['x'];dz=target['z']-origin['z'];flat=math.hypot(dx,dz);angle=0. if flat<1e-9 else math.degrees(math.acos(max(-1.,min(1.,(dx*math.sin(math.radians(yaw))+dz*math.cos(math.radians(yaw)))/flat))))
 assert near(ray['horizontalAngleDegrees'],angle,.002)and ray['inFieldOfView']==(ray['horizontalAngleDegrees']<=half_fov)and ray['inRange']==(ray['distance']<=range_limit)
 distance=math.sqrt(sum((target[k]-origin[k])**2 for k in origin));actual=math.sqrt(sum((ray['actualEndpoint'][k]-origin[k])**2 for k in origin));assert near(ray['distance'],distance)and actual<=distance+.0002
 if ray['blocked']:assert isinstance(ray['hitCollider'],str)and ray['hitCollider']and isinstance(ray['hitColliderEntityId'],str)and bool(ray['hitColliderEntityId'])
 else:assert vec(ray['actualEndpoint'],target)and ray['hitColliderEntityId']==''

def check_mode(folder,mode,fp,c):
 assert mode in CONTRACT['modes'];folder=Path(folder)/mode;rec=read(folder/'mode-complete.json')
 expected=dict(fingerprint=fp,mode=mode,**{k:v for k,v in CONTRACT.items()if k!='modes'});assert all(rec.get(k)==v for k,v in expected.items()),'Actual mode receipt/clock differs'
 assert rec==read(folder/'mode-contract.json'),'Completion differs from original mode contract'
 assert rec['configSHA256']==sha(folder/'capture-config.json')==sha(HERE/'prospect-refuge-unity-source/capture-config.json'),'Raw config provenance changed';validate_capture_config(read(folder/'capture-config.json'),c)
 tape=read(folder/'command-tape.json');assert set(tape)=={'commands'}and sha(folder/'command-tape.json')==rec['commandTapeSHA256'],'Actual serialized command tape differs';validate_capture_config(tape['commands'],c['commands'])
 assert rec['frameConvention']=='Frame0 before Move; capture f, then apply command f once for1/60s to capture f+1; both cameras share evaluated frame'
 with(folder/'trace.csv').open(encoding='utf-8-sig')as h:trace=list(csv.DictReader(h))
 data={name:[(line,json.loads(line))for line in(folder/name).read_text(encoding='utf8').splitlines()]for name in['states.jsonl','rays.jsonl','projected-anchors.jsonl']}
 assert len(trace)==600 and[int(r['frame'])for r in trace]==list(range(600)),'Missing/unordered trace'
 for rows in data.values():assert len(rows)==600 and[r['frame']for text,r in rows]==list(range(600)),'Missing/unordered state/rays/anchors'
 offset=c[mode+'SecondCoverOffsetX'];previous=None
 required={'player-ground','player-camera-eye','enemy-eye','enemy-torso-observation-target','second-cover-center','camera-observation-actual-hit-end'}|{'body-'+v for v in('head','torso','hips')}|{'ray-'+v+'-actual-hit-end'for v in('head','torso','hips')}
 for f,row in enumerate(trace):
  raw,st=data['states.jsonl'][f];rays=data['rays.jsonl'][f][1];anchors=data['projected-anchors.jsonl'][f][1]
  assert row['stateSHA256']==hashlib.sha256(raw.encode('utf8')).hexdigest(),'Trace/state SHA mismatch'
  assert near(row['timeSeconds'],f/60)and near(st['timeSeconds'],f/60)and near(row['secondCoverOffsetX'],offset)and near(st['secondCoverOffsetX'],offset)
  cmd=command_at(c,f);applied=command_at(c,f-1)if f else dict(id='initial-state',velocity=dict(x=0.,y=0.,z=0.))
  assert st['appliedCommandFrame']==int(row['appliedCommandFrame'])==f-1 and st['appliedCommandId']==row['appliedCommandId']==applied['id']and st['nextCommandId']==row['nextCommandId']==cmd['id']
  assert vec(st['appliedVelocity'],applied['velocity'])and vec(st['nextVelocity'],cmd['velocity'])
  for axis in'xyz':
   key=axis.upper();assert near(row['command'+key],applied['velocity'][axis])and near(row['player'+key],st['playerPosition'][axis])and near(row['requested'+key],st['requestedPlayerPosition'][axis])and near(row['actualDelta'+key],st['actualMoveDelta'][axis])
   if previous:
    desired=previous['playerPosition'][axis]+(applied['velocity'][axis]-(c['groundStickSpeed']if axis=='y'else 0))/60
    assert near(st['requestedPlayerPosition'][axis],desired)and near(st['playerPosition'][axis]-previous['playerPosition'][axis],st['actualMoveDelta'][axis]),'Move recurrence differs'
  if not f:assert vec(st['playerPosition'],c['playerStart'])and vec(st['requestedPlayerPosition'],c['playerStart'])and vec(st['actualMoveDelta'],dict(x=0,y=0,z=0))
  x,yaw,phase=enemy_at(c,f);assert vec(st['enemyPosition'],dict(x=x,y=0,z=c['enemyZ']))and near(st['enemyYawDegrees'],yaw)and st['enemyPhase']==row['enemyPhase']==phase
  assert vec(st['enemyEye'],dict(x=x,y=c['enemyEyeHeight'],z=c['enemyZ']))and vec(st['playerCameraEye'],{k:v+(c['cameraEyeHeight']if k=='y'else 0)for k,v in st['playerPosition'].items()})
  assert vec(st['cameraRotationEuler'],dict(x=c['cameraPitchDegrees'],y=c['cameraYawDegrees'],z=0))and vec(st['observerCameraPosition'],c['observerPosition'])and vec(st['observerCameraRotationEuler'],dict(x=90,y=0,z=0))
  assert type(st['collisionFlags'])is int and 0<=st['collisionFlags']<=7 and int(row['collisionFlags'])==st['collisionFlags']
  for prefix,key in [('enemy','enemyPosition'),('enemyEye','enemyEye'),('cameraEye','playerCameraEye'),('observer','observerCameraPosition')]:
   for axis in'xyz':assert near(row[prefix+axis.upper()],st[key][axis])
  for prefix,key in [('camera','cameraRotationEuler'),('observer','observerCameraRotationEuler')]:
   for label,axis in [('Pitch','x'),('Yaw','y'),('Roll','z')]:assert near(row[prefix+label],st[key][axis])
  assert near(row['enemyYaw'],st['enemyYawDegrees'])
  assert st['bodyRays']==rays['enemyToBody']and len(st['bodyRays'])==3
  for ray,name,height in zip(st['bodyRays'],('head','torso','hips'),('headSampleHeight','torsoSampleHeight','hipsSampleHeight')):
   assert ray['id']==name;target={k:v+(c[height]if k=='y'else 0)for k,v in st['playerPosition'].items()};check_ray(ray,st['enemyEye'],target,False,c['enemyRange'],c['enemyHorizontalHalfFovDegrees'],st['enemyYawDegrees']);assert int(row[name+'Seen'])==int(ray['seen'])
  observe=rays['playerCameraToEnemy'];check_ray(observe,st['playerCameraEye'],{k:v+(c['enemyTargetHeight']if k=='y'else 0)for k,v in st['enemyPosition'].items()},True,c['enemyRange'],180.,c['cameraYawDegrees'])
  seen=sum(r['seen']for r in st['bodyRays']);blocked=sum(r['blocked']for r in st['bodyRays']);assert st['seenBodySamples']==int(row['seenBodySamples'])==seen and st['blockedBodySamples']==int(row['blockedBodySamples'])==blocked
  assert st['enemySeesAnyDeclaredBodySample']==bool(int(row['enemySeesAnySample']))==(seen>0)and st['playerCameraCanObserveEnemyTorso']==bool(int(row['playerCameraObservesEnemyTorso']))==observe['seen']
  aa=anchors['anchors'];assert len(aa)==len(required)and{r['id']for r in aa}==required
  for anchor in aa:
   for k in('world','playerViewport','observerViewport'):assert set(anchor[k])=={'x','y','z'}and all(type(v)in(int,float)and math.isfinite(v)for v in anchor[k].values())
  view=next(r['playerViewport']for r in aa if r['id']=='enemy-torso-observation-target');assert observe['cameraInFrustum']==(.04<view['z']<80 and 0<=view['x']<=1 and 0<=view['y']<=1)
  amap={r['id']:r['world']for r in aa};assert vec(amap['player-ground'],st['playerPosition'])and vec(amap['player-camera-eye'],st['playerCameraEye'])and vec(amap['enemy-eye'],st['enemyEye'])
  assert vec(amap['second-cover-center'],{k:v+(offset if k=='x'else 0)for k,v in c['secondCoverCenter'].items()})and vec(amap['camera-observation-actual-hit-end'],observe['actualEndpoint'])and vec(amap['enemy-torso-observation-target'],observe['desiredEndpoint'])
  for ray in st['bodyRays']:assert vec(amap['body-'+ray['id']],ray['desiredEndpoint'])and vec(amap['ray-'+ray['id']+'-actual-hit-end'],ray['actualEndpoint'])
  previous=st
 assert trace[0]['headSeen']=='0'and int(trace[0]['blockedBodySamples'])==2,'Initial partial-cover/facing hypothesis differs'
 assert int(trace[-1]['blockedBodySamples'])==(3 if mode=='baseline'else 0)and int(trace[-1]['seenBodySamples'])==(0 if mode=='baseline'else 3),'Actual end-protection hypothesis differs; preserve and diagnose'
 from PIL import Image
 for camera in CONTRACT['cameras']:
  paths=sorted((folder/camera).glob('*.jpg'));assert[p.name for p in paths]==[f'{i:04}.jpg'for i in range(600)],'Missing/extra actual capture frame'
  for i in[0,89,90,164,165,359,360,599]:
   with Image.open(paths[i])as im:im.load();assert im.size==(1920,1080)
 return trace

def scan(prov,config):
 complete=None;reusable={}
 for attempt in sorted(ATTEMPTS.glob('*'),reverse=True) if ATTEMPTS.exists() else []:
  try:
   if read(attempt/'input-provenance.json')['fingerprint']!=prov['fingerprint']:continue
  except (OSError,ValueError,KeyError):continue
  valid={}
  for mode in CONTRACT['modes']:
   try:check_mode(attempt,mode,prov['fingerprint'],config);valid[mode]=attempt
   except (OSError,ValueError,KeyError,AssertionError):pass
  for mode,path in valid.items():reusable.setdefault(mode,path)
  if len(valid)==2 and (attempt/'scene-record.json').is_file():complete=attempt;break
 return complete,reusable

def stage(prov,reusable):
 output=ATTEMPTS/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]);output.mkdir(parents=True)
 save(output/'input-provenance.json',prov)
 for mode,source in reusable.items():
  for path in (source/mode).rglob('*'):
   if not path.is_file():continue
   target=output/mode/path.relative_to(source/mode);target.parent.mkdir(parents=True,exist_ok=True)
   try:os.link(path,target)
   except OSError:shutil.copy2(path,target)
   assert sha(path)==sha(target)
 return output

def verify_export(output,prov,config,inspect_only=False):
 traces={m:check_mode(output,m,prov['fingerprint'],config) for m in CONTRACT['modes']}
 for a,b in zip(traces['baseline'],traces['shifted']):
  assert all(a[k]==b[k]for k in ['frame','timeSeconds','appliedCommandFrame','appliedCommandId','nextCommandId','commandX','commandY','commandZ','playerX','playerY','playerZ','enemyX','enemyY','enemyZ','enemyYaw','enemyPhase','cameraPitch','cameraYaw','cameraRoll','observerX','observerY','observerZ','observerPitch','observerYaw','observerRoll']),'Only cover offset may change; input/player/enemy/camera clocks must match'
 rec=read(output/'scene-record.json');assert rec['fingerprint']==prov['fingerprint'] and rec['actualSceneFilesSaved']
 assert sorted(rec['scenePaths'])==sorted([FOLDER+'/S02-ProspectRefuge-Baseline.unity',FOLDER+'/S03-ProspectRefuge-Shifted.unity'])
 project=Path(prov['project']).resolve();exports=[];seen=set();shared_meta=[]
 assert rec['files'] and {FOLDER+'/S02-ProspectRefuge-Baseline.unity',FOLDER+'/S03-ProspectRefuge-Shifted.unity'}<={r['path'] for r in rec['files']},'Actual saved scenes missing from export proof'
 for row in rec['files']:
  assert row['path'].startswith(FOLDER+'/') or row['path']==FOLDER+'.meta'
  source,target=export_paths(row['path'],project);key=str(target).casefold();assert key not in seen,'Duplicate export target';seen.add(key)
  assert source.stat().st_size==row['bytes'] and sha(source)==row['sha256']
  assert not target.exists() or sha(target)==row['sha256'],'Preserve changed selected scene; archive/review a new revision explicitly before replacement'
  exports.append((source,target,row))
 export_rows={r['path']:r for r in rec['files']}
 for row in rec['sharedDependencies']:
  rel=Path(row['path']);assert '..'not in rel.parts and not rel.is_absolute()
  staged=project/rel;assert sha(staged)==row['sha256']
  if row['path'].startswith(FOLDER+'/'):
   assert row['path']in export_rows and export_rows[row['path']]==row,'Owned shared shader not in exact export proof';continue
  assert row['path'].startswith('Assets/ThirdParty/KayKitAdventurers/')and rel.name in('Knight.fbx','Knight.fbx.meta','knight_texture.png','knight_texture.png.meta','LICENSE.txt','LICENSE.txt.meta','provenance.json')
  original=UNITY_ROOT/rel
  if sha(original)!=row['sha256']:
   assert rel.suffix.lower()=='.meta'and meta_guid(original)==meta_guid(staged),'Shared licensed dependency differs'
   shared_meta.append(dict(path=row['path'],sourceSHA256=sha(original),stagedSHA256=row['sha256'],guid=meta_guid(original),sourcePreserved=True))
 if inspect_only:return dict(topicId='06.02',nativeValidationComplete=True,captureFingerprint=prov['fingerprint'],output=str(output),filesToExport=len(exports),newGpuStarted=False,actualVisualReview=False,evidenceWritten=False)
 for source,target,row in exports:
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copy2(source,target)
  assert sha(target)==row['sha256']
 frames=[dict(path=p.relative_to(output).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for m in CONTRACT['modes'] for c in CONTRACT['cameras'] for p in sorted((output/m/c).glob('*.jpg'))]
 frame_path=output/'frame-hashes-v1.json';frame_record=dict(fingerprint=prov['fingerprint'],frames=frames)
 if frame_path.exists():assert read(frame_path)==frame_record,'Prior native frame hash record differs'
 else:save(frame_path,frame_record)
 proof_paths=[output/'scene-record.json',frame_path]+[output/m/f for m in CONTRACT['modes'] for f in ['mode-complete.json','mode-contract.json','capture-config.json','command-tape.json','trace.csv','states.jsonl','rays.jsonl','projected-anchors.jsonl']]
 evidence=dict(schemaVersion='06-02-native-evidence-v1',topicId='06.02',fingerprint=prov['fingerprint'],nativePreparationFingerprint=prov['preparationFingerprint'],captureComplete=True,output=str(output),contract=CONTRACT,
  captureProofs=[dict(path=str(p),sha256=sha(p)) for p in proof_paths],savedScenePaths=['unity/VideoEditing/'+s for s in rec['scenePaths']],
  frameHashManifest=dict(path=str(frame_path),sha256=sha(frame_path)),
  exportedFiles=[dict(path=str(t.relative_to(ROOT)),sha256=r['sha256']) for s,t,r in exports],
  actualStagedMeta=prov['stagedMetaChanges'],sharedImportedMetadata=shared_meta,
  declaredSampleResults={m:dict(framesAnyDeclaredSampleSeen=sum(int(r['enemySeesAnySample'])for r in tr),lastFrameSeenBodySamples=int(tr[-1]['seenBodySamples']),lastFrameBlockedBodySamples=int(tr[-1]['blockedBodySamples']))for m,tr in traces.items()},
  measurementLimits='Actual3declared body points/raycast and fixed tape only; not whole-mesh pixel visibility, human decision or commercial AI',
  actualVisualReview=False,humanApproval=False,voicePreparationAllowed=False,platformActions=[])
 save(PROJECT_RECORD/'native-evidence-v1.json',evidence);return evidence

def completed_native(prov,config):
 """QA/helper revisions never force a new capture of unchanged native inputs."""
 path=PROJECT_RECORD/'native-evidence-v1.json'
 if not path.exists():return None
 evidence=read(path)
 if evidence.get('nativePreparationFingerprint')!=prov['preparationFingerprint']:return None
 assert evidence.get('topicId')=='06.02' and evidence.get('captureComplete') is True
 output=Path(evidence['output']).resolve();assert output.is_relative_to(ATTEMPTS.resolve())
 for row in evidence['captureProofs']:
  source=Path(row['path']).resolve();assert source.is_relative_to(output) and sha(source)==row['sha256'],'Existing native proof changed; inspect before any new render'
 for mode in CONTRACT['modes']:check_mode(output,mode,evidence['fingerprint'],config)
 manifest=read(evidence['frameHashManifest']['path']);assert manifest['fingerprint']==evidence['fingerprint']
 expected={f'{m}/{c}/{i:04}.jpg' for m in CONTRACT['modes'] for c in CONTRACT['cameras'] for i in range(CONTRACT['frames'])}
 assert len(manifest['frames'])==len(expected) and {r['path'] for r in manifest['frames']}==expected
 for row in manifest['frames']:
  source=(output/row['path']).resolve();assert source.is_relative_to(output) and sha(source)==row['sha256'],'Existing native frame changed'
 for row in evidence['exportedFiles']:
  dest=(ROOT/row['path']).resolve();owned=(UNITY_ROOT/FOLDER).resolve()
  assert dest.is_relative_to(owned) or dest==Path(str(owned)+'.meta')
  assert sha(dest)==row['sha256'],'Editable scene source changed; preserve for review'
 return evidence

NATIVE_IDENTITY_FIELDS=('protocol','topicId','preparationFingerprint','project','captureEntry','contract','editorVersion','pins')

def historical_native_compatibility(old,current):
 """Only this Python validator may differ; every native/engine/asset pin stays exact."""
 assert old['fingerprint']==digest({k:old[k]for k in NATIVE_IDENTITY_FIELDS}),'Historical input fingerprint invalid'
 assert current['fingerprint']==digest({k:current[k]for k in NATIVE_IDENTITY_FIELDS}),'Current validator fingerprint invalid'
 for key in NATIVE_IDENTITY_FIELDS:
  if key!='pins':assert old[key]==current[key],'Historical physical/native identity differs: '+key
 own=str(Path(__file__).resolve()).casefold()
 def split(rows):
  qa=[];native=[]
  for row in rows:
   (qa if 'path'in row and str(Path(row['path']).resolve()).casefold()==own else native).append(row)
  assert len(qa)==1,'Expected one exact selected validator pin';return qa[0],native
 old_qa,old_native=split(old['pins']);current_qa,current_native=split(current['pins'])
 assert old_native==current_native,'Historical native/source/assets/editor/helper pins differ'
 proof=dict(oldValidatorSHA256=old_qa['sha256'],currentValidatorSHA256=current_qa['sha256'],nativePinsUnchanged=True)
 if old_qa!=current_qa:
  assert set(old_qa)==set(current_qa)=={'path','sha256'}and old_qa['path']==current_qa['path'],'Only selected validator SHA may differ'
  prior=MEDIA/'shorts-leveldesign-06-02/native-validation-history'/old_qa['sha256'][:24]/Path(__file__).name
  assert sha(prior)==old_qa['sha256'],'Preserved original validator source proof missing/changed'
  proof['preservedOriginalValidator']=dict(path=str(prior),sha256=sha(prior))
 return proof

def adoption_state(output,old):
 """Require a completed actual own launch, not an arbitrary cached folder."""
 state=read(STATE)
 assert state.get('protocol')==PROTOCOL and state.get('owner')==OWNER and state.get('fingerprint')==old['fingerprint']
 assert Path(state['output']).resolve()==output and state.get('gpuStarted')is True and state.get('unityExitCode')==0,'Actual selected exit0 capture required'
 assert state.get('child') and set(state['child'])>={'pid','createTime'},'Actual child identity required'
 assert not runtime.alive(state)and not runtime.alive(state['child']),'Existing native worker/child remains alive or unknown'
 command=state['command'];assert command.count('-prospectRefugeModes')==1
 modes=command[command.index('-prospectRefugeModes')+1];parts=modes.split(',')
 assert parts and len(parts)==len(set(parts))and set(parts)<=set(CONTRACT['modes'])
 expected=[str(EDITOR),'-batchmode','-projectPath',old['project'],'-executeMethod',old['captureEntry'],'-prospectRefugeOutput',str(output),'-prospectRefugeFingerprint',old['fingerprint'],'-prospectRefugeModes',modes,'-logFile',str(output/'unity.log')]
 assert command==expected,'Historical launch command differs from exact selected native capture'
 return dict(path=str(STATE),sha256=sha(STATE),worker=dict(pid=state['pid'],createTime=state['createTime']),child=state['child'],unityExitCode=0)

def adoption_plan(attempt):
 output=Path(attempt).resolve();assert output.parent==ATTEMPTS.resolve(),'Adopt only one exact existing selected native attempt'
 old=read(output/'input-provenance.json');state_proof=adoption_state(output,old)
 if WORKER.exists():
  marker=read(WORKER);assert runtime.ours(marker)and not runtime.alive(marker)and not runtime.alive(marker.get('child')),'Existing native singleton preserved'
 # The dead exit0 actual capture above justifies checking imported metadata.
 current=authorize(allow_imported_meta=True);compatibility=historical_native_compatibility(old,current)
 config=read(PREP)['config'];bound=dict(old);bound['stagedMetaChanges']=current['stagedMetaChanges']
 inspection=verify_export(output,bound,config,inspect_only=True)
 plan=dict(topicId='06.02',status='historical-native-verified-CPU-adoption-ready',captureFingerprint=old['fingerprint'],currentValidatorFingerprint=current['fingerprint'],
  actualLaunch=state_proof,inputProvenance=dict(path=str(output/'input-provenance.json'),sha256=sha(output/'input-provenance.json')),compatibility=compatibility,
  currentValidatorPins=current['pins'],inspection=inspection,newGpuStarted=False,actualVisualReview=False)
 return output,bound,current,config,plan

def adopt_existing_attempt(attempt,execute=False):
 output,old,current,config,plan=adoption_plan(attempt)
 if (PROJECT_RECORD/'native-evidence-v1.json').exists():
  prior=completed_native(current,config)
  assert prior and Path(prior['output']).resolve()==output and prior['fingerprint']==old['fingerprint'],'Different/incomplete native evidence preserved'
  return dict(status='already-adopted-existing-native-CPU-only',captureFingerprint=old['fingerprint'],currentValidatorFingerprint=current['fingerprint'],newGpuStarted=False,evidenceUnchanged=True)
 if not execute:return plan
 worker=runtime.SingleWorker(WORKER).acquire()
 try:
  assert sha(STATE)==plan['actualLaunch']['sha256'],'Historical actual launch record changed'
  adoption_state(output,old)
  fresh=authorize(allow_imported_meta=True)
  assert fresh['fingerprint']==current['fingerprint'],'Selected inputs changed before CPU adoption'
  historical_native_compatibility(old,fresh)
  evidence=verify_export(output,old,config)
  assert authorize(allow_imported_meta=True)['fingerprint']==current['fingerprint'],'Selected inputs changed during CPU adoption'
  receipt=output/('native-validation-recovery-'+current['fingerprint'][:24]+'.json')
  if receipt.exists():assert read(receipt)==plan,'Preserve prior CPU validation recovery receipt'
  else:save(receipt,plan)
  evidence['currentValidatorFingerprint']=current['fingerprint']
  evidence['validationRecovery']=dict(kind='CPU-only float32 validator correction; original capture identity retained',path=str(receipt),sha256=sha(receipt),captureFingerprint=old['fingerprint'],currentValidatorFingerprint=current['fingerprint'])
  save(PROJECT_RECORD/'native-evidence-v1.json',evidence)
 finally:worker.close()
 return dict(status='native-adopted-CPU-only-visual-review-pending',captureFingerprint=old['fingerprint'],currentValidatorFingerprint=current['fingerprint'],newGpuStarted=False,evidence=str(PROJECT_RECORD/'native-evidence-v1.json'))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=6);parser.add_argument('--adopt-attempt');args=parser.parse_args()
 assert math.isfinite(args.wait_hours)and 0<=args.wait_hours<=24,'Finite resource wait0..24hours required'
 if args.adopt_attempt:
  print(json.dumps(adopt_existing_attempt(args.adopt_attempt,args.execute)));return
 try:prov=authorize()
 except(FileNotFoundError,AssertionError)as error:
  if args.execute:raise
  print(json.dumps(dict(ready=False,reason=str(error),gpuStarted=False)));return
 config=read(PREP)['config'];prior=completed_native(prov,config)
 if prior:
  print(json.dumps(dict(status='existing-native-complete-reused-CPU-only',output=prior['output'],captureFingerprint=prior['fingerprint'],currentValidatorFingerprint=prov['fingerprint'],newGpuStarted=False,actualVisualReview=prior.get('actualVisualReview',False))));return
 complete,reusable=scan(prov,config)
 if not args.execute:print(json.dumps(dict(ready=True,fingerprint=prov['fingerprint'],existingComplete=str(complete) if complete else None,reusableModes=list(reusable),resourceWait=busy_reason(),gpuStarted=False)));return
 worker=runtime.SingleWorker(WORKER).acquire();owned=None;child=None;state={}
 try:
  old=read(STATE) if STATE.exists() else {}
  if runtime.alive(old) or runtime.alive(old.get('child')):raise RuntimeError('Existing worker/child remains alive or unknown')
  known={r.get('leaseToken') for r in [old,worker.previous or {}] if r.get('leaseToken')}
  for r in [old,worker.previous or {}]:known.update(r.get('recoverableLeaseTokens',[]))
  worker.update(recoverableLeaseTokens=sorted(known));runtime.recover_own_lease(known)
  output=complete or stage(prov,reusable)
  state=dict(protocol=PROTOCOL,owner=OWNER,**runtime.identity(),child=None,status='recovering',fingerprint=prov['fingerprint'],output=str(output),gpuStarted=False,completed=False,recoverableLeaseTokens=sorted(known),scope='06.02 native only; no nextfilm/model/platform')
  save(STATE,state)
  if not complete and len(reusable)<2:
   deadline=time.monotonic()+max(0,args.wait_hours)*3600
   while owned is None:
    assert authorize()['fingerprint']==prov['fingerprint'],'Native inputs changed while waiting; no GPU work started'
    runtime.recover_own_lease(known);reason=busy_reason();state.update(status='waiting-for-resources',reason=reason,checkedAt=time.time());save(STATE,state)
    if not reason:
     token=uuid.uuid4().hex;lease=dict(protocol=PROTOCOL,owner=OWNER,token=token,**runtime.identity(),child=None,phase='reserved',fingerprint=prov['fingerprint'],output=str(output),createdAt=time.time())
     try:
      with runtime.LEASE.open('x',encoding='utf8') as f:json.dump(lease,f)
     except FileExistsError:pass
     else:owned=token;worker.update(leaseToken=token);state['leaseToken']=token;save(STATE,state)
    if owned is None:
     if time.monotonic()>=deadline:raise RuntimeError('Finite resource wait ended; user apps/foreign lease preserved')
     time.sleep(10)
   assert authorize()['fingerprint']==prov['fingerprint']
   assert busy_reason(owned) is None,'Resource changed before launch'
   missing=[m for m in CONTRACT['modes'] if m not in reusable]
   lease=read(runtime.LEASE);assert runtime.ours(lease) and lease['token']==owned;lease['phase']='launching';save(runtime.LEASE,lease)
   command=[str(EDITOR),'-batchmode','-projectPath',prov['project'],'-executeMethod',prov['captureEntry'],'-prospectRefugeOutput',str(output),'-prospectRefugeFingerprint',prov['fingerprint'],'-prospectRefugeModes',','.join(missing),'-logFile',str(output/'unity.log')]
   child=subprocess.Popen(command,cwd=ROOT,creationflags=CREATE)
   child_id=runtime.identity(child.pid);worker.update(child=child_id);lease.update(child=child_id,phase='running');save(runtime.LEASE,lease)
   state.update(status='unity-capture-running',child=child_id,command=command,gpuStarted=True);save(STATE,state)
   code=child.wait();state['unityExitCode']=code
   if code:raise RuntimeError('Unity returned '+str(code)+'; preserve actual log/partial outputs')
  elif not complete:
   # Both complete modes came from older attempts: export evidence must come
   # from a proven matching capture, never invented or recopied from a new build.
   candidates=[p for p in set(reusable.values()) if (p/'scene-record.json').is_file()]
   assert candidates,'Complete modes lack saved scene proof; inspect before new export'
   shutil.copy2(candidates[0]/'scene-record.json',output/'scene-record.json')
  post=authorize(allow_imported_meta=child is not None and state.get('unityExitCode')==0);assert post['fingerprint']==prov['fingerprint']
  evidence=verify_export(output,post,config);state.update(status='native-complete-visual-review-pending',completed=True,evidence=str(PROJECT_RECORD/'native-evidence-v1.json'),savedScenePaths=evidence['savedScenePaths']);save(STATE,state)
 except BaseException as error:
  if state:
   state.update(status='failed-preserved',error=str(error),completed=False,checkedAt=time.time());save(STATE,state)
  raise
 finally:
  live=child is not None and child.poll() is None
  if owned and runtime.LEASE.exists():
   rec=read(runtime.LEASE)
   if runtime.ours(rec)and rec['token']==owned:
    live=live or runtime.unrecorded_child_alive(rec)
    if not live:runtime.LEASE.unlink()
  worker.close(remove=not live)
 print(json.dumps(dict(status=state['status'],output=state['output'],evidence=state['evidence'],actualVisualReview=False)))
if __name__=='__main__':main()
