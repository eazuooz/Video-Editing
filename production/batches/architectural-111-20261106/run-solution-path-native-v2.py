"""Finite11.05 native controller. Default readonly; explicit subset --modes required to execute.
Only matching physical/mode proofs may be reused; original subset fingerprints
and immutable flat editable snapshots are retained. Never starts another topic.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,re,shutil,struct,subprocess,time,uuid
from pathlib import Path
import psutil
from initialize import ROOT,HERE,MEDIA,read,save

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prep=module('solution_path_preparer',HERE/'prepare-solution-path-unity-v2.py');rt=module('solution_path_isolated_resource',HERE/'run-first-native.py')
PROTOCOL='architectural111-11-05-native-v2';OWNER='architectural-111-11-05-native';rt.PROTOCOL=PROTOCOL;rt.OWNER=OWNER
P=prep.P;BASE=prep.BASE;ATTEMPTS=BASE/'native-attempts';STATE=MEDIA/'11-05-native-progress.json';WORKER=MEDIA/'11-05-native-worker.json';EVIDENCE=P/'native-evidence-v2.json';EDITOR=Path(rt.EDITOR);UNITY=ROOT/'unity/VideoEditing';FOLDER=prep.FOLDER
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0);HUB=Path('C:/Program Files/Unity Hub/resources/unity.exe').resolve()
need=prep.need;sha=prep.sha;pin=prep.pin;digest=prep.digest;Pending=prep.Pending
QUALIFIER=HERE/'prospect-refuge-resource-qualification.py';QUALIFIER_SHA='2dbb128a891fabf9c440e5790b88481c7901fbf087098557c540b19b8ecd5f5d';need(sha(QUALIFIER)==QUALIFIER_SHA,'Reviewed exact-tree resource classifier changed')
ANIMATION_VALIDATOR=HERE/'verify-solution-path-animation-v2.py';ANIMATION_VALIDATOR_SHA='aad9f29d766e29d6ee713c53fd88b7a64d3e8134452f30f0f90adf4c20ff1c76';need(sha(ANIMATION_VALIDATOR)==ANIMATION_VALIDATOR_SHA,'Reviewed animation diagnostic validator changed')
animation_validator=module('solution_path_animation_diagnostics_v2',ANIMATION_VALIDATOR)
qualifier=module('solution_path_exact_legacy_idle_classifier',QUALIFIER);qualifier.BASE=BASE/'resource-observations';LAST_RESOURCE_CLASSIFICATION=None

def modes_arg(value):
 names=value.split(',')if isinstance(value,str)and value else []
 need(names and len(set(names))==len(names)and all(x in prep.MODES for x in names),'Explicit nonempty unique scoped modes required');return [x for x in prep.MODES if x in names]
def request_fp(physical,modes):return digest(dict(topicId='11.05',physicalInputFingerprint=physical,requestedModes=modes,frameConvention='capture0=initial; command f produces capture f+1'))
def guid(path):
 found=re.findall(r'^guid:\s*([0-9a-fA-F]{32})\s*$',Path(path).read_text(encoding='utf-8-sig'),re.M);need(len(found)==1 and found[0]!='0'*32,'One nonzero canonical metadata GUID required');return found[0].lower()
def version(path):
 fields={}
 for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
  if not line.strip():continue
  k,sep,v=line.partition(':');need(sep and k.strip()in('m_EditorVersion','m_EditorVersionWithRevision')and k.strip()not in fields,'Unexpected editor version format');fields[k.strip()]=v.strip()
 need(fields.get('m_EditorVersion')==prep.VERSION,'Canonical editor version changed')
 if 'm_EditorVersionWithRevision'in fields:need(re.fullmatch(re.escape(prep.VERSION)+r'\s*\([0-9a-fA-F]{12}\)',fields['m_EditorVersionWithRevision']),'Wrong editor revision/version')
 return pin(path)
def gap_alive(record):
 if not record or record.get('phase')!='launching'or record.get('child'):return False
 command=record.get('launchCommand')
 if not isinstance(command,list)or not command:return True
 for p in psutil.process_iter(['name','cmdline']):
  try:
   if(p.info.get('name')or'').lower()!='unity.exe':continue
   if p.info.get('cmdline')is None or p.info['cmdline']==command:return True
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:return True
 return False
def live(record):return rt.alive(record)or gap_alive(record)
def pending_child(record):return bool(record)and(rt.alive(record.get('child'))or gap_alive(record))
def hub_serve(info):
 try:return Path(info.get('exe')or'').resolve()==HUB and info.get('cmdline')==[str(HUB),'serve']
 except(OSError,ValueError):return False
def process_reason(info,own_pid,qualified=frozenset()):
 if info.get('pid')==own_pid:return None
 name=(info.get('name')or'').lower();args=info.get('cmdline');exe=(info.get('exe')or'').replace('\\','/').lower()
 if name=='unity.exe':return None if hub_serve(info)else'Another actual Unity Editor/batch or unknown Unity process is running'
 if name in('unrealeditor.exe','unrealeditor-cmd.exe'):return'Another Unreal Editor/renderer is running'
 if '/steamapps/common/'in exe or name in{'overwatch.exe','d2r.exe','spelunky.exe','spelunky_classic.exe','spel2.exe','factorio.exe','starcraft.exe','starcraft64.exe','sc2_x64.exe','hl2.exe','noita.exe','teardown.exe','valheim.exe','cs2.exe','left4dead2.exe'}:return'User game process is running; preserve it'
 if name=='ffmpeg.exe':return'Another media process is running'
 if name in('chrome.exe','msedge.exe','chromium.exe')and(args is None or any(x.startswith('--headless')for x in args)):
  signature=qualifier.EXPECTED.get(info.get('pid'));same=bool(signature and args is not None and info.get('pid')in qualified and info.get('ppid')==signature[0]and type(info.get('create_time'))in(int,float)and abs(info['create_time']-signature[1])<=.001 and qualifier.argv_sha(args)==signature[2]and exe==qualifier.EDGE_EXE)
  if not same:return'Active, changed, unreadable or unverified headless renderer preserved'
 if name.startswith('python')and(args is None or any(k in' '.join(args).lower()for k in('--synthesize','--recognize','render_narration','faster_whisper','torchrun','voice-repair','run-selected-voice'))):return'Another or uninspected model/recognizer process is running'
 return None
def busy_reason(token=None):
 need(sha(QUALIFIER)==QUALIFIER_SHA,'Reviewed classifier source changed during finite wait')
 global LAST_RESOURCE_CLASSIFICATION
 fields=['pid','ppid','create_time','name','exe','cmdline']
 for p in psutil.process_iter(fields):
  try:
   info=p.info;args=info.get('cmdline')
   if(info.get('name')or'').lower()in('chrome.exe','msedge.exe','chromium.exe')and args is not None and any(x.startswith('--headless')for x in args):continue
   reason=process_reason(info,os.getpid())
   if reason:return reason
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:return'Uninspected process identity preserved'
 result=qualifier.qualify(base_guard=lambda:rt.busy_reason(token))
 LAST_RESOURCE_CLASSIFICATION=dict(classifier=pin(QUALIFIER),classifierOriginTopicId='06.02',currentJobTopicId='11.05',classificationOnly=True,ownershipGranted=False,completionGranted=False,processTerminationAuthorized=False,result=result)
 if not result.get('qualified'):return result.get('reason')or'Exact-tree resource qualification incomplete'
 qualified=frozenset(result['qualifiedPids'])
 for p in psutil.process_iter(fields):
  try:
   reason=process_reason(p.info,os.getpid(),qualified)
   if reason:return reason
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:return'Uninspected process identity preserved'
 return rt.busy_reason(token)

def authorize(allow_imported_meta=False):
 fresh=prep.preflight();need(fresh['staticCompilerProof'],'Exact source API compiler proof missing');stored=read(prep.REPORT);need(stored.get('sourceStageComplete')is True and stored.get('fingerprint')==fresh['fingerprint'],'Explicit --stage is required for exact current source')
 project=Path(fresh['project']).resolve();need(project.is_relative_to(prep.PROJECTS.resolve()),'Isolated project escaped scope');known={}
 if EVIDENCE.exists():
  e=read(EVIDENCE)
  if e.get('physicalInputFingerprint')==fresh['fingerprint']:
   for row in e.get('captureProofs',[]):need(sha(row['path'])==row['sha256'],'Prior native proof changed')
   known={r['target']:r for r in e.get('actualStagedMeta',[])}
 changes=[]
 for row in fresh['files']:
  source=ROOT/row['source'];target=project/row['target'];need(target.is_file()and sha(source)==row['sha256'],'Missing/changed original or staged input')
  actual=sha(target)
  if actual!=row['sha256']:
   need(source.suffix==target.suffix=='.meta'and guid(source)==guid(target),'Only same-GUID imported metadata can differ')
   change=dict(target=row['target'],sourceSHA256=row['sha256'],stagedSHA256=actual,guid=guid(source));need(allow_imported_meta or known.get(row['target'])==change,'Unrecorded imported metadata drift; inspect before GPU');changes.append(change)
 for name,text in fresh['generated'].items():
  if name.endswith('ProjectVersion.txt'):version(project/name)
  else:need((project/name).read_bytes()==text.encode('utf-8'),'Isolated package manifest changed')
 return dict(topicId='11.05',physicalInputFingerprint=fresh['fingerprint'],project=str(project),captureEntry=prep.ENTRY,contract=fresh['captureContract'],config=fresh['config'],files=fresh['files'],actualStagedMeta=changes,compilerProof=fresh['staticCompilerProof'],validatorFingerprint=digest(dict(physical=fresh['fingerprint'],runner=sha(__file__),preparer=sha(prep.__file__),runtime=sha(HERE/'run-first-native.py'),resourceClassifier=QUALIFIER_SHA,animationDiagnosticValidator=ANIMATION_VALIDATOR_SHA)),animationDiagnosticValidator=pin(ANIMATION_VALIDATOR))

def seed_stream(seed,channel):
 state=(seed^channel)&0xffffffff
 if state==0:state=0x9e3779b9
 while True:
  state^=(state<<13)&0xffffffff;state^=state>>17;state^=(state<<5)&0xffffffff;state&=0xffffffff;yield state

def graph_expected(seed,side,template,broken):
 rng=seed_stream(seed,0xa341316c);x=next(rng)%4;route=[x]
 for y in range(4):
  target=next(rng)%4
  while x!=target:x+=1 if x<target else-1;route.append(y*4+x)
  if y<3:route.append((y+1)*4+x)
 edges=[];active=set(route);roles=['mandatory'if i in active else'sealed'for i in range(16)]
 def edge(a,b,role):return dict(a=min(a,b),b=max(a,b),role=role)
 for a,b in zip(route,route[1:]):edges.append(edge(a,b,'mandatory'))
 rng=seed_stream(seed,(0xc8013ea4+side*0x9e3779b9)&0xffffffff)
 for _ in range(max(0,16-len(route)-1)):
  choices=[edge(a,b,'side')for a in range(16)if a in active for b in range(16)if b not in active and abs(a//4-b//4)+abs(a%4-b%4)==1]
  if not choices:break
  e=choices[next(rng)%len(choices)];room=e['b']if e['a']in active else e['a'];active.add(room);roles[room]='side';edges.append(e)
 rng=seed_stream(seed,0xad90777d);variants=[(next(rng)%2+template)%2 for _ in range(16)];ba=bb=-1
 if broken:
  k=max(1,len(route)//2);ba,bb=route[k-1:k+1];edges=[e for e in edges if(e['a'],e['b'])!=(min(ba,bb),max(ba,bb))]
 return dict(seed=seed,sideVariant=side,templateVariant=template,entrance=route[0],exit=route[-1],mandatoryRoute=route,roomVariants=variants,roomRoles=roles,edges=edges,brokenConnector=broken,brokenA=ba,brokenB=bb)
def reachable(graph,count=None):
 seen={graph['entrance']};edges=graph['edges']if count is None else graph['edges'][:count]
 while True:
  new=seen|{e['b']for e in edges if e['a']in seen}|{e['a']for e in edges if e['b']in seen}
  if new==seen:return graph['exit']in seen
  seen=new
def enemy_basis(c,g):
 route=g['mandatoryRoute'];middle=len(route)//2;best=-1
 center=lambda r:[(r%4-1.5)*c['cellSize'],0.,(1.5-r//4)*c['cellSize']]
 for i in range(1,len(route)-1):
  a,b,d=[center(route[k])for k in(i-1,i,i+1)];incoming=[y-x for x,y in zip(a,b)];outgoing=[y-x for x,y in zip(b,d)]
  if sum((x-y)**2 for x,y in zip(incoming,outgoing))<1e-8 and(best<0 or abs(i-middle)<abs(best-middle)):best=i
 need(best>=0,'Own source requires a straight enemy focus');focus=center(route[best]);target=center(route[best+1]);norm=math.dist(focus,target);t=[(y-x)/norm for x,y in zip(focus,target)];return focus,[t[2],0.,-t[0]]
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def finite(v):
 if isinstance(v,dict):return all(finite(x)for x in v.values())
 if isinstance(v,list):return all(finite(x)for x in v)
 return type(v)not in(int,float)or math.isfinite(v)
def vec(v):need(isinstance(v,dict)and set(v)=={'x','y','z'}and all(type(x)in(int,float)and math.isfinite(x)for x in v.values()),'Finite actual Vector3 required');return[v[k]for k in('x','y','z')]
def close(a,b,tol=0.0002):return len(a)==len(b)and all(abs(x-y)<=tol for x,y in zip(a,b))
def planned(c,g,frame):
 length=f32(f32(max(0,f32((frame-c['traversalStartFrame'])/c['fps'])))*c['walkSpeed']);segment=math.floor(f32(length/c['cellSize']))
 center=lambda room:[f32((room%4-1.5)*c['cellSize']),0.,f32((1.5-room//4)*c['cellSize'])]
 if segment>=len(g['mandatoryRoute'])-1:return center(g['exit'])
 a,b=[center(g['mandatoryRoute'][i])for i in(segment,segment+1)];t=f32(f32(length/c['cellSize'])-segment);return[f32(x+f32(f32(y-x)*t))for x,y in zip(a,b)]
def projection(anchor,state,camera):
 world=vec(anchor['world']);v=vec(anchor[camera+'Viewport']);matrix=state[camera+'VP'];need(len(matrix)==16 and all(type(x)in(int,float)and math.isfinite(x)for x in matrix),'Finite actual VP matrix required')
 # Match the captured Unity float matrix/vector arithmetic. Float64 dot products
 # amplify cancellation at small positive w for offscreen points; keep every
 # original tolerance and check, rather than skipping those anchors.
 point=[*world,1.];clip=[]
 for r in range(4):
  value=f32(matrix[r*4]*point[0])
  for k in range(1,4):value=f32(value+f32(matrix[r*4+k]*point[k]))
  clip.append(value)
 depth=clip[3]if camera=='player'else vec(state['observerCameraPosition'])[1]-world[1];need(abs(v[2]-depth)<=.0003,'Actual camera-space depth differs')
 if .04<v[2]<100:
  need(abs(clip[3])>1e-10 and close([f32(f32(f32(clip[k]/clip[3])+1.)*.5)for k in(0,1)],v[:2]),'Projection does not come from actual camera matrix')
 ray=anchor[camera+'Ray'];need(close(vec(ray['origin']),vec(state[camera+'CameraPosition']))and close(vec(ray['target']),world),'Ray is not anchored to actual camera/object')
 distance=math.dist(vec(ray['origin']),world);need(abs(ray['targetDistance']-distance)<=.0003,'Actual ray target distance differs')
 need(type(ray['hit'])is bool and type(ray['hitBeforeTarget'])is bool,'Actual ray flags required')
 if ray['hit']:need(isinstance(ray['hitCollider'],str)and bool(ray['hitCollider'])and abs(math.dist(vec(ray['origin']),vec(ray['hitPoint']))-ray['hitDistance'])<=.0005,'Actual hit point/name/distance inconsistent')
 else:need(ray.get('hitCollider')in(None,'')and close(vec(ray['hitPoint']),world)and abs(ray['hitDistance']-distance)<=.0003,'Unblocked ray evidence inconsistent')
 if abs(ray['hitDistance']-(ray['targetDistance']-.08))>.0001:need(ray['hitBeforeTarget']==(ray['hit']and ray['hitDistance']<ray['targetDistance']-.08),'Target-surface hit confused with earlier occluder')

def snapshot_paths(row,mode_folder):
 name=prep.canonical(row['path']);snap=prep.canonical(row['snapshotFile']);need(snap=='editable/'+hashlib.sha256(name.encode('utf-8')).hexdigest()+'.bin','Flat snapshot name is not canonical source-path SHA256');p=(mode_folder/snap).resolve();need(p.is_relative_to(mode_folder.resolve())and p.is_file()and p.stat().st_size==row['bytes']and sha(p)==row['sha256'],'Missing/changed editable snapshot');return name,p

def saved_input(row,snapshot,folder,changes):
 actual=snapshot['sha256']
 if actual==row['sha256']:return
 recorded=next((r for r in changes if r['target']==row['target']),None)
 need(row['target'].endswith('.meta')and recorded is not None and recorded['sourceSHA256']==row['sha256']and recorded['stagedSHA256']==actual and recorded['guid']==guid(ROOT/row['source'])==guid(snapshot_paths(snapshot,folder)[1]),'Saved metadata must match exact recorded same-GUID import hash')

def export_target(name):
 prep.canonical(name);target=(UNITY/name).resolve();owned=(UNITY/FOLDER).resolve();need(target.is_relative_to(owned)or target==Path(str(owned)+'.meta'),'Export escaped owned11.05 subtree');return target

def check_mode(attempt,mode,prov):
 request=read(attempt/'input-provenance.json');need(request.get('physicalInputFingerprint')==prov['physicalInputFingerprint']and request.get('fingerprint')==request_fp(prov['physicalInputFingerprint'],request['requestedModes'])and mode in request['requestedModes'],'Wrong request/subset physical fingerprint')
 folder=attempt/'capture'/mode;c=prov['config'];spec=next(r for r in c['modes']if r['id']==mode);done=read(folder/'mode-complete.json');contract=read(folder/'mode-contract.json')
 need(done==contract and done.get('fingerprint')==request['fingerprint']and done.get('mode')==mode and all(done[k]==c[k]for k in('frames','fps','width','height'))and done.get('cameras')==['player','observer']and done.get('actualSceneSaved')is True and done.get('frameConvention')=='capture0=initial; command f produces capture f+1','Incomplete/wrong mode capture')
 need(done['configSHA256']==sha(prep.SOURCE/'config.json')==sha(folder/'config.json')and done['graphSHA256']==sha(folder/'generation-graph.json'),'Config/graph source bytes changed')
 graph=read(folder/'generation-graph.json');need(graph==graph_expected(c['seed'],spec['sideVariant'],spec['templateVariant'],spec['broken']),'Actual graph differs from the source-bound own model')
 rec=read(folder/'mode-scene-record.json');scene=FOLDER+'/'+spec['sceneFile'];need(rec.get('fingerprint')==request['fingerprint']and rec.get('mode')==mode and rec.get('unityVersion')==prep.VERSION and rec.get('actualSceneFilesSaved')is True and rec.get('sourceKind')=='our-own-implementation'and rec.get('scenePaths')==[scene]and done['scenePath']==scene,'Missing/wrong pre-frame saved-scene proof')
 need(len(rec.get('animationClips',[]))==2 and rec['animationClips'][0].lower().endswith('idle')and rec['animationClips'][1].lower().endswith('walking_a'),'Actual Idle/Walking_A clip names required')
 files=rec['files'];deps=rec['dependencies'];seen=set();allpins={}
 for row in files+deps:
  name,snap=snapshot_paths(row,folder);need(name.casefold()not in seen,'Duplicate/case-colliding snapshot path');seen.add(name.casefold());allpins[name]=row
  need((name.startswith(FOLDER+'/')or name==FOLDER+'.meta')if row in files else(name in['Assets/ThirdParty/KayKitAdventurers/'+n for n in prep.ASSETS]+[prep.SHADER,prep.SHADER+'.meta']),'Snapshot escaped owned/shared scope')
 need({scene,scene+'.meta',FOLDER+'.meta',FOLDER+'/config.json',FOLDER+'/config.json.meta',*[FOLDER+'/'+n for n in prep.CS],*[FOLDER+'/'+n+'.meta'for n in prep.CS]}<=set(allpins),'Current scene/config/source metadata missing from saved proof')
 for name in [scene+'.meta',FOLDER+'.meta',FOLDER+'/config.json.meta']+[FOLDER+'/'+n+'.meta'for n in prep.CS]:guid(snapshot_paths(allpins[name],folder)[1])
 runtime_guid=guid(snapshot_paths(allpins[FOLDER+'/Experiment.cs.meta'],folder)[1]);need(re.search(r'm_Script:\s*\{[^}]*guid:\s*'+runtime_guid+r'[,\s}]',snapshot_paths(allpins[scene],folder)[1].read_text(encoding='utf-8-sig')),'Saved scene does not bind actual runtime script GUID')
 for row in prov['files']:
  need(row['target']in allpins,'Staged input absent from saved proof');saved_input(row,allpins[row['target']],folder,prov['actualStagedMeta'])
 states=[json.loads(x)for x in(folder/'states.jsonl').read_text(encoding='utf-8-sig').splitlines()];anchors=[json.loads(x)for x in(folder/'projected-anchors.jsonl').read_text(encoding='utf-8-sig').splitlines()]
 need(len(states)==len(anchors)==1200,'Incomplete state/anchor clock');ids=None;priorpos=None;main=len(graph['mandatoryRoute'])-1
 for frame,(s,a)in enumerate(zip(states,anchors)):
  need(s['frame']==a['frame']==frame and s['appliedCommandFrame']==frame-1 and s['mode']==mode and s.get('sourceKind')=='our-own-implementation'and s['safePlayTested']is False and finite(s)and finite(a),'Wrong actual state/clock/safety claim')
  count=len(graph['edges'])if not spec['construction']or frame>=360 else 0 if frame<60 else math.floor(f32(f32((frame-60)/180)*main))if frame<240 else main+math.floor(f32(f32((frame-240)/120)*(len(graph['edges'])-main)))
  need(s['visibleConnectorCount']==count and s['modelExitConnected']==reachable(graph)and s['visiblePortExitConnected']==reachable(graph,count),'Graph connection/readout differs')
  need(close(vec(s['plannedPlayerPosition']),planned(c,graph,frame)),'Reference command path drift')
  expected=[0.,0.,0.]if frame==0 else[f32(b-a)for a,b in zip(planned(c,graph,frame-1),planned(c,graph,frame))];need(close(vec(s['requestedDelta']),expected),'Fixed command tape changed')
  pos=vec(s['playerPosition']);need(close(vec(s['actualDelta']),[0.,0.,0.]if priorpos is None else[b-a for a,b in zip(priorpos,pos)]),'Actual displacement is not trace-consistent');priorpos=pos
  need(type(s['collisionFlags'])is int and 0<=s['collisionFlags']<=7 and len(s['contactColliderIds'])==len(s['contactColliderNames'])and all(isinstance(x,str)and x for x in s['contactColliderIds']+s['contactColliderNames']),'Contact/collision evidence inconsistent')
  focus,perp=enemy_basis(c,graph);offset=f32((1.8 if spec['enemyVariant']==0 else 0.)+f32(math.sin(f32(frame/c['fps']))*.15));need(close(vec(s['enemyReferenceCenter']),focus)and close(vec(s['enemyOffsetDirection']),perp)and close(vec(s['enemyPosition']),[f32(x+f32(y*offset))for x,y in zip(focus,perp)]),'Enemy offset is not actual route-perpendicular/source-clock position')
  exitpoints=[r for r in a['anchors']if r['id']=='derived-bottom-exit'];need(len(exitpoints)==1 and exitpoints[0]['active']==(not spec['construction']or frame>=240),'Construction exit marker revealed before its generation phase')
  current=[r['id']for r in a['anchors']];need(len(set(current))==len(current)and(ids is None or ids==current),'Anchor identities drift');ids=current
  for row in a['anchors']:
   need(type(row['active'])is bool,'Actual anchor hierarchy active flag required')
   for camera in('player','observer'):projection(row,s,camera)
 from PIL import Image
 for camera in('player','observer'):
  paths=sorted((folder/camera).glob('*.jpg'));need([p.name for p in paths]==[f'{i:04}.jpg'for i in range(1200)],'Incomplete/noncanonical actual JPEG sequence')
  for i in(0,59,60,239,240,359,360,449,450,479,480,999,1000,1079,1080,1199):
   with Image.open(paths[i])as im:im.load();need(im.size==(1920,1080)and im.format=='JPEG','Wrong native image dimensions/format')
 need(sha(ANIMATION_VALIDATOR)==ANIMATION_VALIDATOR_SHA,'Animation diagnostic validator changed during inspection')
 diagnostics=animation_validator.validate(folder,request['fingerprint'],mode)
 return dict(folder=folder,request=request,sceneRecord=rec,graph=graph,states=states,animationDiagnostics=diagnostics)

def scan(prov,targets):
 reusable={}
 for attempt in sorted(ATTEMPTS.glob('*'),reverse=True)if ATTEMPTS.exists()else[]:
  for mode in targets:
   if mode in reusable:continue
   try:check_mode(attempt,mode,prov);reusable[mode]=attempt
   except(OSError,ValueError,KeyError,AssertionError,Pending):pass
 return reusable

def export_and_record(prov,targets,found,request_fingerprint):
 validated={mode:check_mode(attempt,mode,prov)for mode,attempt in found.items()};exports={};proofs=[];frames=[];meta_guids={}
 for mode,v in validated.items():
  folder=v['folder'];proofs.extend(pin(folder/n)for n in('mode-complete.json','mode-contract.json','config.json','generation-graph.json','mode-scene-record.json','states.jsonl','projected-anchors.jsonl','animation-diagnostics.jsonl','animation-diagnostics-summary.json'))
  for row in v['sceneRecord']['files']:
   name,source=snapshot_paths(row,folder);target=export_target(name)
   if name.endswith('.meta'):
    value=guid(source);need(value not in meta_guids or meta_guids[value]==name,'Different editable paths share a GUID');meta_guids[value]=name
   if name in exports:need(exports[name][2]['sha256']==row['sha256'],'Different per-mode editable versions; preserve and diagnose')
   else:exports[name]=(source,target,row)
  for camera in('player','observer'):
   for p in sorted((folder/camera).glob('*.jpg')):frames.append(dict(mode=mode,camera=camera,path=str(p),sha256=sha(p),bytes=p.stat().st_size))
 for source,target,row in exports.values():need(not target.exists()or sha(target)==row['sha256'],'Preserve different existing owned editable source')
 for source,target,row in exports.values():
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copy2(source,target)
  need(sha(target)==row['sha256'],'Export bytes changed')
 physical=prov['physicalInputFingerprint'];receipt=BASE/'native-proof-sets'/digest(dict(physical=physical,targets=targets,proofs=proofs))[:24];receipt.mkdir(parents=True,exist_ok=True);framepath=receipt/'frame-hashes.json';record=dict(physicalInputFingerprint=physical,frames=frames)
 if framepath.exists():need(read(framepath)==record,'Existing raw frame hash set differs')
 else:save(framepath,record)
 complete=set(found)==set(prep.MODES);e=dict(schemaVersion='11-05-native-evidence-v1',topicId='11.05',fingerprint=digest(dict(physical=physical,proofs=proofs)),physicalInputFingerprint=physical,requestedCaptureFingerprint=request_fingerprint,validatorFingerprint=prov['validatorFingerprint'],captureComplete=complete,subsetCaptureComplete=all(m in found for m in targets),requestedModes=targets,capturedModes=list(found),remainingModes=[m for m in prep.MODES if m not in found],modeSources={m:dict(attempt=str(found[m]),originalRequestFingerprint=validated[m]['request']['fingerprint'])for m in found},captureProofs=proofs+[pin(framepath)],frameHashManifest=pin(framepath),actualStagedMeta=prov['actualStagedMeta'],savedScenePaths=['unity/VideoEditing/'+FOLDER+'/'+next(r['sceneFile']for r in prov['config']['modes']if r['id']==m)for m in found],exportedFiles=[dict(path=str(t.relative_to(ROOT)),sha256=r['sha256'])for s,t,r in exports.values()],actualVisualReview=False,voicePreparationAllowed=False,humanApproval=False,platformActions=[])
 save(receipt/'native-evidence.json',e);save(EVIDENCE,e);return e

def execute(prov,targets,wait_hours):
 need(0<=wait_hours<=6 and math.isfinite(wait_hours),'Finite0..6hour wait required');worker=rt.SingleWorker(WORKER,is_alive=live).acquire();owned=None;child=None;state={};lease=None
 try:
  old=read(STATE)if STATE.exists()else{};need(not live(old)and not pending_child(old),'Prior worker or launch-gap child preserved')
  known=set(old.get('recoverableLeaseTokens',[]))|set((worker.previous or{}).get('recoverableLeaseTokens',[]));known.update(x for x in(old.get('leaseToken'),(worker.previous or{}).get('leaseToken'))if x)
  worker.update(recoverableLeaseTokens=sorted(known));rt.recover_own_lease(known,is_alive=live,unrecorded=gap_alive)
  found=scan(prov,targets);missing=[m for m in targets if m not in found];fp=request_fp(prov['physicalInputFingerprint'],targets);attempt=None
  if missing:
   attempt=ATTEMPTS/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]);attempt.mkdir(parents=True,exist_ok=False);save(attempt/'input-provenance.json',dict(prov,fingerprint=fp,requestedModes=targets,actuallyRequestedMissingModes=missing))
  state=dict(protocol=PROTOCOL,owner=OWNER,**rt.identity(),token=worker.record['token'],status='recovering',phase='reserved',child=None,fingerprint=fp,physicalInputFingerprint=prov['physicalInputFingerprint'],requestedModes=targets,output=str(attempt)if attempt else None,gpuStarted=False,completed=False,recoverableLeaseTokens=sorted(known));save(STATE,state)
  if missing:
   deadline=time.monotonic()+wait_hours*3600
   while owned is None:
    need(authorize()['validatorFingerprint']==prov['validatorFingerprint'],'Input/helper changed while waiting');rt.recover_own_lease(known,is_alive=live,unrecorded=gap_alive);reason=busy_reason();state.update(status='waiting-for-resources',reason=reason,checkedAt=time.time());save(STATE,state)
    if not reason:
     token=uuid.uuid4().hex;lease=dict(protocol=PROTOCOL,owner=OWNER,token=token,**rt.identity(),child=None,phase='reserved',fingerprint=fp,output=str(attempt))
     try:
      with rt.LEASE.open('x',encoding='utf-8')as f:json.dump(lease,f)
     except FileExistsError:pass
     else:owned=token;known.add(token);worker.update(leaseToken=token,recoverableLeaseTokens=sorted(known));state.update(leaseToken=token,recoverableLeaseTokens=sorted(known));save(STATE,state)
    if owned is None:
     need(time.monotonic()<deadline,'Finite resource wait ended; foreign applications/lease preserved');time.sleep(10)
   need(authorize()['validatorFingerprint']==prov['validatorFingerprint']and busy_reason(owned)is None,'Resource/input/helper changed before launch')
   output=attempt/'capture';command=[str(EDITOR),'-batchmode','-projectPath',prov['project'],'-executeMethod',prov['captureEntry'],'-solutionOutput',str(output),'-solutionFingerprint',fp,'-solutionModes',','.join(missing),'-logFile',str(attempt/'unity.log')]
   state.update(status='launching-owned-Unity',phase='launching',launchCommand=command,launchStartedAt=time.time());worker.update(phase='launching',launchCommand=command,launchStartedAt=state['launchStartedAt']);lease.update(phase='launching',launchCommand=command,launchStartedAt=state['launchStartedAt']);save(rt.LEASE,lease);save(STATE,state)
   child=subprocess.Popen(command,cwd=ROOT,creationflags=CREATE);identity=dict(rt.identity(child.pid),argv=command,commandSHA256=digest(command));worker.update(phase='running',child=identity);lease.update(phase='running',child=identity);save(rt.LEASE,lease);state.update(status='unity-capture-running',phase='running',child=identity,gpuStarted=True);save(STATE,state)
   code=child.wait();state['unityExitCode']=code;save(STATE,state);need(code==0,'Unity failed; preserve log/partial actual outputs')
   prov=authorize(allow_imported_meta=True)
   for mode in missing:check_mode(attempt,mode,prov);found[mode]=attempt
  evidence=export_and_record(prov,targets,found,fp);state.update(status='native-subset-complete-visual-review-pending',completed=True,captureComplete=evidence['captureComplete'],evidence=pin(EVIDENCE));save(STATE,state);return evidence
 except BaseException as error:
  if state:state.update(status='failed-preserved',error=repr(error),completed=False);save(STATE,state)
  raise
 finally:
  active=(child is not None and child.poll()is None)or gap_alive(worker.record)
  if owned and rt.LEASE.exists():
   rec=read(rt.LEASE)
   if rt.ours(rec)and rec['token']==owned and not active:rt.LEASE.unlink()
  worker.close(remove=not active)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--modes');p.add_argument('--wait-hours',type=float,default=2);a=p.parse_args()
 try:
  need(not a.execute or a.modes,'--execute requires explicit --modes; no automatic all8 job');targets=modes_arg(a.modes or'construction');prov=authorize()
  if a.execute:result=execute(prov,targets,a.wait_hours)
  else:result=dict(ready=True,topicId='11.05',requestedModes=targets,requestFingerprint=request_fp(prov['physicalInputFingerprint'],targets),physicalInputFingerprint=prov['physicalInputFingerprint'],reusableModes=list(scan(prov,targets)),resourceWait=busy_reason(),resourceClassification=LAST_RESOURCE_CLASSIFICATION,gpuStarted=False,unityLaunched=False)
  print(json.dumps(result,ensure_ascii=False));return 0
 except Exception as error:
  if a.execute:raise
  print(json.dumps(dict(ready=False,pending=str(error),gpuStarted=False,unityLaunched=False),ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
