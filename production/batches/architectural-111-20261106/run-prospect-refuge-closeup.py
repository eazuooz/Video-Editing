"""Finite third-camera derivative of accepted06.02 capture. Default readonly.
Reuses the isolated proven lifecycle/resource gate; no main source/state mutation.
"""
import argparse,hashlib,importlib.util,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent

def module(name,file):
 sp=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
prep=module('prospect_closeup_prepare_runtime','prepare-prospect-refuge-closeup.py')
n=module('prospect_closeup_private_native_lifecycle','run-prospect-refuge-native.py')
PROTOCOL='architectural111-06-02-closeup-v1';OWNER='architectural-111-06-02-closeup'
RECORD=prep.P/'closeup';EVIDENCE=RECORD/'native-evidence-v1.json';PREP=prep.REPORT
ATTEMPTS=prep.MEDIA/'shorts-leveldesign-06-02/closeup-attempts';PROJECT=Path(prep.read(PREP)['project']).resolve()if PREP.exists()else prep.project_for('0'*64)
STATE=prep.MEDIA/'06-02-closeup-progress.json';WORKER=prep.MEDIA/'06-02-closeup-worker.json'
CONTRACT=prep.CONTRACT;read=n.read;sha=n.sha;save=n.save;pin=prep.pin
n.PROTOCOL=PROTOCOL;n.OWNER=OWNER;n.runtime.PROTOCOL=PROTOCOL;n.runtime.OWNER=OWNER
n.PROJECT_RECORD=RECORD;n.PREP=PREP;n.STATE=STATE;n.WORKER=WORKER;n.ATTEMPTS=ATTEMPTS;n.CONTRACT=CONTRACT;n.FOLDER=prep.FOLDER

def f32(v):return n.struct.unpack('<f',n.float32_bits(v))[0]
def equal_state(a,b,path='FrameState'):
 if path.endswith('.hitColliderEntityId'):
  assert isinstance(a,str)and isinstance(b,str),'Native entity IDs must remain strings';return
 if isinstance(a,dict):
  assert isinstance(b,dict)and a.keys()==b.keys(),'State keys differ: '+path
  for k,v in a.items():equal_state(v,b[k],path+'.'+k)
 elif isinstance(a,list):
  assert isinstance(b,list)and len(a)==len(b),'State array differs: '+path
  for i,(x,y)in enumerate(zip(a,b)):equal_state(x,y,path+'['+str(i)+']')
 elif type(a)is float:assert type(b)is float and n.float32_bits(a)==n.float32_bits(b),'Float32 replay changed: '+path
 else:assert type(a)is type(b)and a==b,'Shared replay changed: '+path

def authorize(allow_imported_meta=False):
 global PROJECT
 current=prep.preflight();r=read(PREP);
 assert Path(r['project']).resolve()==prep.project_for(r['fingerprint']),'Derivative project is not bound to its preparation fingerprint'
 PROJECT=Path(r['project']).resolve()
 assert r.get('sourceStageComplete')and r['fingerprint']==current['fingerprint']and r['staticCompiler']==current['staticCompiler']and r['staticCompiler'],'Missing/stale closeup stage/compile'
 assert r['files']==current['files']and r['generated']==current['generated']
 prior=read(EVIDENCE)if EVIDENCE.exists()else{};known={x['target']:x for x in prior.get('actualStagedMeta',[])if prior.get('captureComplete')};changes=[]
 for row in r['files']:
  source=Path(row['sourceAbsolute']).resolve();target=(PROJECT/row['target']).resolve();assert target.is_relative_to(PROJECT.resolve())
  change=n.staged_input(row,source,target,known,allow_imported_meta)
  if change:changes.append(change)
 expected_code={row['target']for row in r['files']if row['target'].endswith('.cs')}
 actual_code={path.relative_to(PROJECT).as_posix()for path in(PROJECT/'Assets').rglob('*')if path.is_file()and path.suffix.lower()in('.cs','.dll','.asmdef','.asmref')}
 assert actual_code==expected_code,'Unpinned imported executable source in derivative project'
 for target,text in r['generated'].items():
  if target=='ProjectSettings/ProjectVersion.txt':continue
  assert(PROJECT/target).read_bytes()==text.encode('utf8'),'Generated derivative inputs changed'
 version=n.project_version(PROJECT/'ProjectSettings/ProjectVersion.txt','6000.6.0f1')
 pins=[dict(sourceAbsolute=x['sourceAbsolute'],target=x['target'],sha256=x['sha256'])for x in r['files']]
 for path in[Path(__file__),Path(prep.__file__),HERE/'run-prospect-refuge-native.py',HERE/'prospect-refuge-resource-qualification.py',HERE/'run-first-native.py',Path(r['staticCompiler']['path'])]:pins.append(pin(path))
 assert n.EDITOR.is_file()and n.shutil.disk_usage(prep.MEDIA).free>=3*1024**3
 result=dict(protocol=PROTOCOL,topicId='06.02',preparationFingerprint=r['fingerprint'],mainFingerprint=r['mainReference']['mainFingerprint'],project=str(PROJECT),captureEntry=prep.ENTRY,contract=CONTRACT,editorVersion='6000.6.0f1',pins=pins)
 result['fingerprint']=n.digest(result);result['stagedMetaChanges']=changes;result['mainEvidenceAudit']=current['mainEvidenceAudit'];result['projectVersionAudit']=version['sourceAudit'];return result

def snapshot_relative(canonical):
 return 'editable/'+hashlib.sha256(canonical.encode('utf8')).hexdigest()+'.bin'

def vector_close(a,b,tol=.0001):return set(a)==set(b)=={'x','y','z'}and all(n.near(a[k],b[k],tol)for k in a)
def check_mode(output,mode,fp,config):
 assert mode in CONTRACT['modes'];folder=Path(output)/mode;rec=read(folder/'mode-complete.json');stage=read(PREP);reference=stage['mainReference'];expected=next(x for x in reference['modes']if x['mode']==mode)
 assert all(rec.get(k)==v for k,v in dict(fingerprint=fp,mainFingerprint=reference['mainFingerprint'],mode=mode,frames=600,fps=60,width=1920,height=1080,camera='closeup',statesCompared=600,allSharedStatesEqual=True,mainStatesSHA256=expected['statesSHA256'],closeupConfigSHA256=sha(prep.SOURCE/'closeup-config.json'),comparisonPolicy=config['comparisonPolicy']).items()),'Wrong derivative receipt/provenance'
 proof=read(folder/'mode-scene-record.json');scene=prep.FOLDER+('/S02-ProspectRefuge-Closeup-Baseline.unity'if mode=='baseline'else'/S03-ProspectRefuge-Closeup-Shifted.unity')
 assert all(proof.get(k)==v for k,v in dict(fingerprint=fp,mainFingerprint=reference['mainFingerprint'],mode=mode,scenePath=scene,mainSourceFrame=0,actualSceneFilesSaved=True).items()),'Per-mode saved scene identity differs'
 required={scene,scene+'.meta'}|{prep.FOLDER+'/'+name+suffix for name in['ProspectRefugeCloseupCamera.cs','Editor/ProspectRefugeCloseupBuilder.cs','closeup-config.json','main-reference.json']for suffix in['','.meta']}
 assert proof['files']and required<={x['path']for x in proof['files']},'Per-mode editable source proof incomplete'
 seen=set();seen_storage=set()
 for item in proof['files']:
  path=item['path'];parts=path.split('/');assert '\\'not in path and all(x not in('','.','..')for x in parts)and(path.startswith(prep.FOLDER+'/')or path==prep.FOLDER+'.meta')and path.casefold()not in seen,'Per-mode source escaped, noncanonical or duplicated';seen.add(path.casefold())
  assert not(path.endswith('.unity')or path.endswith('.unity.meta'))or path in(scene,scene+'.meta'),'Other mode scene is not this mode source'
  assert item['snapshotRelativePath']==snapshot_relative(path)and item['snapshotRelativePath']not in seen_storage,'Noncanonical or duplicate per-mode snapshot path';seen_storage.add(item['snapshotRelativePath'])
  snapshot=(folder/item['snapshotRelativePath']).resolve();source=(PROJECT/path).resolve();assert snapshot.is_relative_to((folder/'editable').resolve())and source.is_relative_to(PROJECT.resolve())
  assert source.stat().st_size==snapshot.stat().st_size==item['bytes']and sha(source)==sha(snapshot)==item['sha256'],'Per-mode editable source snapshot changed'
 original=Path(reference['mainAttempt'])/mode/'states.jsonl';assert sha(original)==expected['statesSHA256'];main=[json.loads(x)for x in original.read_text(encoding='utf8').splitlines()];states=[json.loads(x)for x in(folder/'states.jsonl').read_text(encoding='utf8').splitlines()];projections=[json.loads(x)for x in(folder/'projected-anchors.jsonl').read_text(encoding='utf8').splitlines()]
 assert len(main)==len(states)==len(projections)==600
 mainconfig=read(Path(reference['mainAttempt'])/mode/'capture-config.json');offset=mainconfig[mode+'SecondCoverOffsetX']
 for f,(a,b,c)in enumerate(zip(main,states,projections)):
  equal_state(a,b);assert a['frame']==b['frame']==c['frame']==c['mainSourceFrame']==f
  for ray in b['bodyRays']:assert isinstance(ray['hitColliderEntityId'],str)and bool(ray['hitColliderEntityId'])==ray['blocked']
  position={k:f32(f32(v)+f32(config['cameraOffset'][k]))for k,v in a['playerPosition'].items()};focus={k:f32(f32(v)+f32(config['lookOffset'][k]))for k,v in a['playerPosition'].items()}
  assert vector_close(c['position'],position)and vector_close(c['focus'],focus),'Derived camera pose detached from main actor'
  delta={k:focus[k]-position[k]for k in position};length=math.sqrt(sum(v*v for v in delta.values()));assert vector_close(c['forward'],{k:v/length for k,v in delta.items()})
  assert n.float32_bits(c['mainPlayerAspect'])==n.float32_bits(config['width']/config['height'])and n.float32_bits(c['mainObserverAspect'])==n.float32_bits(config['width']/config['height']),'Original capture aspect not restored'
  for key,source in[('fieldOfView','verticalFieldOfView'),('nearClip','nearClip'),('farClip','farClip')]:assert n.float32_bits(c[key])==n.float32_bits(config[source])
  matrix=c['viewProjectionRowMajor'];assert len(matrix)==16 and all(type(v)in(int,float)and math.isfinite(v)for v in matrix)
  points={'player-ground':a['playerPosition'],'main-player-camera-eye':a['playerCameraEye'],'enemy-eye':a['enemyEye']}
  for ray in a['bodyRays']:points['body-'+ray['id']]=ray['desiredEndpoint'];points['enemy-ray-'+ray['id']+'-actual-end']=ray['actualEndpoint']
  for which in['first','second']:
   center=dict(mainconfig[which+'CoverCenter']);center['x']+=offset if which=='second'else 0;size=mainconfig[which+'CoverSize']['y']
   for name,sign in[('top',1),('bottom',-1)]:point=dict(center);point['y']+=sign*size*.5;points[which+'-cover-'+name]=point
  anchors=c['anchors'];assert len(anchors)==len(points)and{x['id']for x in anchors}==set(points)
  for item in anchors:
   assert vector_close(item['world'],points[item['id']]),'Projection not bound to original point'
   v=item['viewport'];world=[item['world'][k]for k in'xyz']+[1.];clip=[sum(matrix[r*4+i]*world[i]for i in range(4))for r in range(4)]
   assert abs(clip[3])>1e-6 and n.near(v['x'],.5+.5*clip[0]/clip[3],.0002)and n.near(v['y'],.5+.5*clip[1]/clip[3],.0002),'Actual point projection differs'
   assert n.near(v['z'],sum((item['world'][k]-c['position'][k])*c['forward'][k]for k in'xyz'),.0002)
   assert item['inFrustum']==(c['nearClip']<v['z']<c['farClip']and 0<=v['x']<=1 and 0<=v['y']<=1)
   end=item['actualCameraRayEndpoint'];assert all(type(x)in(int,float)and math.isfinite(x)for x in end.values())and type(item['environmentBlocked'])is bool and type(item['inFrustum'])is bool
   desired=[item['world'][k]-c['position'][k]for k in'xyz'];actual=[end[k]-c['position'][k]for k in'xyz'];dd=sum(v*v for v in desired);aa=sum(v*v for v in actual);dot=sum(a*b for a,b in zip(desired,actual));cross=math.sqrt(max(0.,dd*aa-dot*dot));assert aa<=dd+.001 and dot>=-.0001 and cross/max(math.sqrt(dd),1e-8)<.001,'Camera ray endpoint leaves actual sight segment'
   if item['environmentBlocked']:assert isinstance(item['hitCollider'],str)and item['hitCollider']
   else:assert vector_close(end,item['world'])
 from PIL import Image
 paths=sorted((folder/'closeup').glob('*.jpg'));assert[x.name for x in paths]==[f'{f:04}.jpg'for f in range(600)]
 for f in[0,89,90,164,165,300,359,360,419,599]:
  with Image.open(paths[f])as im:im.load();assert im.size==(1920,1080)
 return states

def verify_export(output,prov,config):
 for mode in CONTRACT['modes']:check_mode(output,mode,prov['fingerprint'],config)
 rec=read(Path(output)/'scene-record.json');assert rec['fingerprint']==prov['fingerprint']and rec['mainFingerprint']==prov['mainFingerprint']and rec['actualSceneFilesSaved']is True
 expected=[prep.FOLDER+'/S02-ProspectRefuge-Closeup-Baseline.unity',prep.FOLDER+'/S03-ProspectRefuge-Closeup-Shifted.unity'];assert sorted(rec['scenePaths'])==sorted(expected)
 exports=[];seen=set()
 for row in rec['files']:
  source,target=n.export_paths(row['path'],PROJECT);assert str(target).casefold()not in seen;seen.add(str(target).casefold())
  assert source.stat().st_size==row['bytes']and sha(source)==row['sha256'];assert not target.exists()or sha(target)==row['sha256'],'Preserve changed closeup editable source';exports.append((source,target,row))
 assert set(expected)<={r['path']for r in rec['files']}
 for source,target,row in exports:
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():n.shutil.copy2(source,target)
  assert sha(target)==row['sha256']
 files=[dict(path=p.relative_to(output).as_posix(),sha256=sha(p),bytes=p.stat().st_size)for mode in CONTRACT['modes']for p in sorted((Path(output)/mode/'closeup').glob('*.jpg'))]
 manifest=Path(output)/'frame-hashes-v1.json';value=dict(fingerprint=prov['fingerprint'],frames=files)
 if manifest.exists():assert read(manifest)==value
 else:save(manifest,value)
 proofs=[Path(output)/'scene-record.json',manifest]+[Path(output)/m/f for m in CONTRACT['modes']for f in['mode-complete.json','mode-scene-record.json','states.jsonl','projected-anchors.jsonl']]
 evidence=dict(schemaVersion='06.02-closeup-native-evidence-v1',topicId='06.02',fingerprint=prov['fingerprint'],nativePreparationFingerprint=prov['preparationFingerprint'],mainCaptureFingerprint=prov['mainFingerprint'],captureComplete=True,output=str(output),contract=CONTRACT,captureProofs=[pin(p)for p in proofs],frameHashManifest=pin(manifest),savedScenePaths=['unity/VideoEditing/'+p for p in rec['scenePaths']],exportedFiles=[dict(path=str(t.relative_to(prep.ROOT)),sha256=r['sha256'])for s,t,r in exports],actualStagedMeta=prov['stagedMetaChanges'],mainEvidenceAudit=prov['mainEvidenceAudit'],actualVisualReview=False,humanApproval=False,voicePreparationAllowed=False,platformActions=[])
 save(EVIDENCE,evidence);return evidence

def completed_native(prov,config):
 if not EVIDENCE.exists():return None
 ev=read(EVIDENCE)
 if ev['nativePreparationFingerprint']!=prov['preparationFingerprint']:return None
 assert ev['captureComplete']and ev['mainCaptureFingerprint']==prov['mainFingerprint'];out=Path(ev['output']).resolve();assert out.is_relative_to(ATTEMPTS.resolve())
 for row in ev['captureProofs']:assert Path(row['path']).resolve().is_relative_to(out)and sha(row['path'])==row['sha256']
 for mode in CONTRACT['modes']:check_mode(out,mode,ev['fingerprint'],config)
 for row in read(ev['frameHashManifest']['path'])['frames']:
  p=(out/row['path']).resolve();assert p.is_relative_to(out)and sha(p)==row['sha256']
 for row in ev['exportedFiles']:
  path=(prep.ROOT/row['path']).resolve();assert path.is_relative_to((n.UNITY_ROOT/prep.FOLDER).resolve())or path==Path(str(n.UNITY_ROOT/prep.FOLDER)+'.meta');assert sha(path)==row['sha256']
 return ev
n.authorize=authorize;n.check_mode=check_mode;n.verify_export=verify_export;n.completed_native=completed_native

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=2);parser.parse_args()
 n.main()
if __name__=='__main__':main()
