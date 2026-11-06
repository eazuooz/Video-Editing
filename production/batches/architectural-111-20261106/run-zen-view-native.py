"""Finite07.04 capture; read-only preflight by default, one owned lease/worker.

Reuse the proven singleton/resource functions in an isolated module instance;
never edit or update the first film's source, worker, state or deliverables.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,os,re,shutil,struct,subprocess,time,uuid
from pathlib import Path
import psutil
from initialize import ROOT,HERE,MEDIA,AUTH_KEY,read,save

spec=importlib.util.spec_from_file_location('zen_view_native_resource_runtime',HERE/'run-first-native.py')
runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
PROTOCOL='architectural111-07-04-native-v1';OWNER='architectural-111-07-04-native'
runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
PROJECT_RECORD=ROOT/'projects/shorts-leveldesign-07-04'
PREP=PROJECT_RECORD/'unity-preparation-v1.json';STATE=MEDIA/'07-04-native-progress.json';WORKER=MEDIA/'07-04-native-worker.json'
ATTEMPTS=MEDIA/'shorts-leveldesign-07-04/native-attempts';EDITOR=Path(runtime.EDITOR)
UNITY_ROOT=ROOT/'unity/VideoEditing';FOLDER='Assets/VideoScenes/architectural-111-20261106/07-04'
BROWSER_AUDIT=PROJECT_RECORD/'resource-idle-browser-audit-v1.json'
CONTRACT=dict(frames=480,width=1920,height=1080,fps=60,cameras=['player','observer'],modes=['narrow','wide'])
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
def sha(path):
 with Path(path).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def idle_browser_members():
 """Preserve only the two inspected disconnected/idle groups; inspect afresh."""
 if not BROWSER_AUDIT.is_file():return set()
 allowed=set();gpu=[]
 try:
  audit=read(BROWSER_AUDIT)
  for group in audit['groups']:
   root=psutil.Process(group['root']['pid'])
   if abs(root.create_time()-group['root']['createTime'])>=.01 or root.parent() is not None:continue
   members=[root]+root.children(recursive=True);expected={r['pid']:r for r in group['members']}
   if {p.pid for p in members}!=set(expected):continue
   if any(abs(p.create_time()-expected[p.pid]['createTime'])>=.01 or digest(p.cmdline())!=expected[p.pid]['commandSHA256'] for p in members):continue
   first={p.pid:p.cpu_times().user+p.cpu_times().system for p in members};time.sleep(1)
   if {p.pid for p in [root]+root.children(recursive=True)}!=set(expected):continue
   delta=sum(p.cpu_times().user+p.cpu_times().system-first[p.pid] for p in members)
   if delta<0 or delta>.05:continue
   allowed.update(expected);gpu.extend(r['pid'] for r in group['members'] if r['gpuProcess'])
  if not allowed or not gpu:return set()
  pattern='^pid_('+'|'.join(str(int(p)) for p in gpu)+')_'
  command="$a=@(Get-CimInstance -ClassName Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine | Where-Object { $_.Name -match '"+pattern+"' }); [pscustomobject]@{count=$a.Count;maximum=($a|Measure-Object -Property UtilizationPercentage -Maximum).Maximum} | ConvertTo-Json -Compress"
  proc=subprocess.run(['powershell.exe','-NoProfile','-Command',command],stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=CREATE,timeout=25)
  if proc.returncode:return set()
  metrics=json.loads(proc.stdout)
  return allowed if metrics['count']>0 and metrics['maximum']==0 else set()
 except (OSError,ValueError,KeyError,psutil.NoSuchProcess,psutil.AccessDenied,subprocess.TimeoutExpired):return set()

def busy_reason(own_token=None):
 reason=runtime.busy_reason(own_token)
 if reason:return reason
 games={'sc2_x64.exe','starcraft.exe','starcraft64.exe','diabloiii.exe','noita.exe','teardown.exe','factorio.exe','valheim.exe','cs2.exe','hl2.exe','left4dead2.exe'}
 idle=None
 for process in psutil.process_iter(['name','cmdline']):
  try:
   name=(process.info['name'] or '').lower();args=process.info['cmdline'] or []
   if name in games:return 'User game process is running; preserve it and wait'
   if name=='unrealeditor-cmd.exe':return 'Another Unreal command-line renderer is running'
   if name in ('chrome.exe','msedge.exe','chromium.exe') and any(x.startswith('--headless') for x in args):
    if idle is None:idle=idle_browser_members()
    if getattr(process,'pid',None) not in idle:return 'Another active or unverified headless browser/render job is running'
  except (psutil.NoSuchProcess,psutil.AccessDenied):continue
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
 assert isinstance(actual,dict) and actual.keys()==expected.keys(),'Capture config keys differ'
 for key,value in expected.items():
  if type(value) is int:
   assert type(actual[key]) is int and actual[key]==value,'Exact integer config differs: '+key
  else:
   assert type(value) is float and float32_bits(actual[key])==float32_bits(value),'Float32 config differs: '+key

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

def authorize(allow_imported_meta=False):
 control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
 assert control['status'] not in ('paused','stopped','cancelled') and control['automaticAdvanceWithinExactList']
 assert not control['automaticAdvanceOutsideList'] and not control['youtubeAuthorized']
 batch=read(HERE/'batch.json');assert len(batch['projects'])==111 and batch['localFinalReviewOnly']
 assert sha(ROOT/batch['sourceCatalog'])==batch['sourceCatalogSHA256']
 assert any(r['topicId']=='07.04' and r['slug']==PROJECT_RECORD.name for r in batch['projects'])
 prep=read(PREP);assert prep['sourceStageComplete'] and prep['captureContract']==CONTRACT and prep['topicId']=='07.04'
 project=Path(prep['project']).resolve();assert project== (MEDIA/'unity-zen-view-capture').resolve()
 pins=[];meta_changes=[]
 previous=read(PROJECT_RECORD/'native-evidence-v1.json') if (PROJECT_RECORD/'native-evidence-v1.json').exists() else {}
 known={r['target']:r for r in previous.get('actualStagedMeta',[]) if previous.get('topicId')=='07.04' and previous.get('captureComplete')}
 for row in prep['files']:
  source=(ROOT/row['source']).resolve();target=(project/row['target']).resolve()
  assert source.is_relative_to(ROOT.resolve()) and target.is_relative_to(project)
  change=staged_input(row,source,target,known,allow_imported_meta)
  if change:meta_changes.append(change)
  pins.append(dict(source=row['source'],target=row['target'],sha256=row['sha256']))
 version=project_version(project/'ProjectSettings/ProjectVersion.txt',prep['editorVersion'])
 for path in [PREP,Path(__file__),HERE/'run-first-native.py',HERE/'prepare-zen-view-unity.py',BROWSER_AUDIT,project/'Packages/manifest.json']:
  pins.append(dict(path=str(path),sha256=sha(path)))
 assert EDITOR.is_file()
 assert shutil.disk_usage(MEDIA).free>=4*1024**3,'Insufficient C space for native frames and reserve; preserve existing media'
 result=dict(protocol=PROTOCOL,topicId='07.04',preparationFingerprint=prep['fingerprint'],project=str(project),captureEntry=prep['captureEntry'],contract=CONTRACT,editorVersion=version['editorVersion'],pins=pins)
 result['fingerprint']=digest(result);result['stagedMetaChanges']=meta_changes;result['projectVersionAudit']=version['sourceAudit'];return result

def export_paths(value,project):
 parts=value.replace('\\','/').split('/')
 assert all(p not in ('','.','..') for p in parts),'Noncanonical export path'
 rel=Path(value);assert not rel.is_absolute()
 source=(project/rel).resolve();target=(UNITY_ROOT/rel).resolve()
 owned_source=project/FOLDER;owned_target=UNITY_ROOT/FOLDER
 assert owned_source.resolve()==owned_source and owned_target.resolve()==owned_target,'Owned export roots must not redirect to another scene'
 if value==FOLDER+'.meta':assert source==Path(str(owned_source)+'.meta') and target==Path(str(owned_target)+'.meta')
 else:assert source.is_relative_to(owned_source) and target.is_relative_to(owned_target),'Export escaped exact07.04 subtree'
 return source,target

def check_mode(folder,mode,fp,config):
 folder=Path(folder)/mode;rec=read(folder/'mode-complete.json')
 expected=dict(fingerprint=fp,mode=mode,**{k:v for k,v in CONTRACT.items() if k!='modes'})
 assert all(rec.get(k)==v for k,v in expected.items()),'Actual mode receipt/clock differs'
 snapshot=read(folder/'capture-config.json');validate_capture_config(snapshot['contract'],config);assert snapshot['mode']==mode
 width=config[mode+'Width'];assert float32_bits(snapshot['openingWidth'])==float32_bits(width),'Snapshot opening width differs'
 with (folder/'trace.csv').open(encoding='utf-8-sig') as handle:trace=list(csv.DictReader(handle))
 assert len(trace)==480 and [int(r['frame']) for r in trace]==list(range(480))
 for i,r in enumerate(trace):
  assert all(math.isfinite(float(r[k])) for k in ['timeSeconds','openingWidth','eyeX','eyeY','eyeZ'])
  assert abs(float(r['timeSeconds'])-i/60)<.00001 and abs(float(r['openingWidth'])-width)<.00001
  expected_x=config['pathStartX']+(config['pathEndX']-config['pathStartX'])*i/479
  assert abs(float(r['eyeX'])-expected_x)<.00001 and abs(float(r['eyeY'])-config['eyeHeight'])<.00001 and abs(float(r['eyeZ'])-config['pathZ'])<.00001
  assert r['centerVisible'] in ('0','1') and r['centerBlocked'] in ('0','1') and r['centerInFrustum'] in ('0','1')
  assert (r['centerVisible']=='1')==(r['centerBlocked']=='0' and r['centerInFrustum']=='1')
  assert 0<=int(r['sampleVisibleCount'])<=int(r['sampleCount']) and int(r['sampleCount'])==5
 visible=[int(r['frame']) for r in trace if r['centerVisible']=='1']
 expected_frames=range(225,255) if mode=='narrow' else range(480)
 assert visible==list(expected_frames),'Actual collider/FOV visibility differs from analytical geometry; preserve and diagnose'
 for filename in ['rays.jsonl','projected-anchors.jsonl']:
  rows=[json.loads(line) for line in (folder/filename).read_text().splitlines()]
  assert len(rows)==480 and [r['frame'] for r in rows]==list(range(480))
  if filename=='rays.jsonl':assert all(len(r['rays'])==7 for r in rows),'Five landmark samples differ from seven observer sight guides'
 from PIL import Image
 for camera in CONTRACT['cameras']:
  paths=sorted((folder/camera).glob('*.jpg'));assert [p.name for p in paths]==[f'{i:04}.jpg' for i in range(480)]
  for i in [0,224,225,239,254,255,479]:
   with Image.open(paths[i]) as image:image.load();assert image.size==(1920,1080)
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

def verify_export(output,prov,config):
 traces={m:check_mode(output,m,prov['fingerprint'],config) for m in CONTRACT['modes']}
 for a,b in zip(traces['narrow'],traces['wide']):
  assert all(a[k]==b[k] for k in ['frame','timeSeconds','eyeX','eyeY','eyeZ']),'Only width may change; camera clocks/paths must match'
 rec=read(output/'scene-record.json');assert rec['fingerprint']==prov['fingerprint'] and rec['actualSceneFilesSaved']
 assert sorted(rec['scenePaths'])==sorted([FOLDER+'/S02-ZenView-Narrow.unity',FOLDER+'/S03-ZenView-Wide.unity'])
 project=Path(prov['project']).resolve();exports=[];seen=set();shared_meta=[]
 assert rec['files'] and {FOLDER+'/S02-ZenView-Narrow.unity',FOLDER+'/S03-ZenView-Wide.unity'}<={r['path'] for r in rec['files']},'Actual saved scenes missing from export proof'
 for row in rec['files']:
  assert row['path'].startswith(FOLDER+'/') or row['path']==FOLDER+'.meta'
  source,target=export_paths(row['path'],project);key=str(target).casefold();assert key not in seen,'Duplicate export target';seen.add(key)
  assert source.stat().st_size==row['bytes'] and sha(source)==row['sha256']
  assert not target.exists() or sha(target)==row['sha256'],'Preserve changed selected scene; archive/review a new revision explicitly before replacement'
  exports.append((source,target,row))
 for row in rec['sharedDependencies']:
  assert row['path'].startswith('Assets/ThirdParty/KayKitAdventurers/')
  rel=Path(row['path']);assert '..' not in rel.parts and not rel.is_absolute()
  staged=project/rel;original=UNITY_ROOT/rel;assert sha(staged)==row['sha256']
  if sha(original)!=row['sha256']:
   assert rel.suffix.lower()=='.meta' and meta_guid(original)==meta_guid(staged),'Shared licensed input dependency differs'
   shared_meta.append(dict(path=row['path'],sourceSHA256=sha(original),stagedSHA256=row['sha256'],guid=meta_guid(original),sourcePreserved=True))
 for source,target,row in exports:
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copy2(source,target)
  assert sha(target)==row['sha256']
 frames=[dict(path=p.relative_to(output).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for m in CONTRACT['modes'] for c in CONTRACT['cameras'] for p in sorted((output/m/c).glob('*.jpg'))]
 frame_path=output/'frame-hashes-v1.json';frame_record=dict(fingerprint=prov['fingerprint'],frames=frames)
 if frame_path.exists():assert read(frame_path)==frame_record,'Prior native frame hash record differs'
 else:save(frame_path,frame_record)
 proof_paths=[output/'scene-record.json',frame_path]+[output/m/f for m in CONTRACT['modes'] for f in ['mode-complete.json','capture-config.json','trace.csv','rays.jsonl','projected-anchors.jsonl']]
 evidence=dict(schemaVersion='07-04-native-evidence-v1',topicId='07.04',fingerprint=prov['fingerprint'],nativePreparationFingerprint=prov['preparationFingerprint'],captureComplete=True,output=str(output),contract=CONTRACT,
  captureProofs=[dict(path=str(p),sha256=sha(p)) for p in proof_paths],savedScenePaths=['unity/VideoEditing/'+s for s in rec['scenePaths']],
  frameHashManifest=dict(path=str(frame_path),sha256=sha(frame_path)),
  exportedFiles=[dict(path=str(t.relative_to(ROOT)),sha256=r['sha256']) for s,t,r in exports],
  actualStagedMeta=prov['stagedMetaChanges'],sharedImportedMetadata=shared_meta,
  observedCenterTarget=dict(narrowVisibleFrames=[225,254],narrowVisibleCount=30,wideVisibleFrames=[0,479],wideVisibleCount=480,measures='Actual collider-raycast sample-point visibility, not pixel/ocean coverage'),
  actualVisualReview=False,humanApproval=False,voicePreparationAllowed=False,platformActions=[])
 save(PROJECT_RECORD/'native-evidence-v1.json',evidence);return evidence

def completed_native(prov,config):
 """QA/helper revisions never force a new capture of unchanged native inputs."""
 path=PROJECT_RECORD/'native-evidence-v1.json'
 if not path.exists():return None
 evidence=read(path)
 if evidence.get('nativePreparationFingerprint')!=prov['preparationFingerprint']:return None
 assert evidence.get('topicId')=='07.04' and evidence.get('captureComplete') is True
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

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=6);args=parser.parse_args()
 prov=authorize();config=read(PREP)['config'];prior=completed_native(prov,config)
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
  state=dict(protocol=PROTOCOL,owner=OWNER,**runtime.identity(),child=None,status='recovering',fingerprint=prov['fingerprint'],output=str(output),gpuStarted=False,completed=False,recoverableLeaseTokens=sorted(known),scope='07.04 native only; no nextfilm/model/platform')
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
   command=[str(EDITOR),'-batchmode','-projectPath',prov['project'],'-executeMethod',prov['captureEntry'],'-zenViewOutput',str(output),'-zenViewFingerprint',prov['fingerprint'],'-zenViewModes',','.join(missing),'-logFile',str(output/'unity.log')]
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
   if runtime.ours(rec) and rec['token']==owned and not live:runtime.LEASE.unlink()
  worker.close(remove=not live)
 print(json.dumps(dict(status=state['status'],output=state['output'],evidence=state['evidence'],actualVisualReview=False)))
if __name__=='__main__':main()
