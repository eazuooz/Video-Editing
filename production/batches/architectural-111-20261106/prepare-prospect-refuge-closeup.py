"""Additional-camera CPU preparation. Default readonly; --stage bytecopies to isolated project.
Never edits main capture/source/stage or launches Unity, model, GPU, video encoder.
"""
import argparse,base64,hashlib,json,os,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
P=ROOT/'projects/shorts-leveldesign-06-02';EVIDENCE=P/'native-evidence-v1.json'
MAIN_PROJECT=MEDIA/'unity-prospect-refuge-capture';PROJECT_ROOT=MEDIA/'unity-prospect-refuge-closeup-projects'
SOURCE=HERE/'prospect-refuge-closeup-source';FOLDER='Assets/VideoScenes/architectural-111-20261106/06-02-closeup';MAIN_FOLDER='Assets/VideoScenes/architectural-111-20261106/06-02'
REPORT=P/'closeup-staging-v1.json';COMPILER=MEDIA/'shorts-leveldesign-06-02/closeup-cpu-preflight/compile.json'
ENTRY='Yamyam.Architectural111.ProspectRefuge.Closeup.Editor.ProspectRefugeCloseupBuilder.Capture'
CONTRACT=dict(frames=600,width=1920,height=1080,fps=60,cameras=['closeup'],modes=['baseline','shifted'])
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def authorize():
 a=read(ROOT/'shared/publishing/video-production-control.json')['explicitArchitectural111Batch20261106'];assert a['status']not in('paused','stopped','cancelled')and a['automaticAdvanceWithinExactList']and not a['automaticAdvanceOutsideList']and not a['youtubeAuthorized']
 b=read(HERE/'batch.json');assert len(b['projects'])==111 and b['localFinalReviewOnly']and sha(ROOT/b['sourceCatalog'])==b['sourceCatalogSHA256']and any(r['topicId']=='06.02'for r in b['projects'])
 c=read(HERE/'checkpoint.json');assert c.get('currentTopicId')=='06.02'or c.get('nextSelectedTopicId')=='06.02'
def owned_main(path):
 parts=path.replace('\\','/').split('/');assert all(x not in('','.','..')for x in parts)and not Path(path).is_absolute()
 assert path.startswith(MAIN_FOLDER+'/')or path==MAIN_FOLDER+'.meta'or path.startswith('Assets/ThirdParty/KayKitAdventurers/')
 f=(MAIN_PROJECT/path).resolve();assert f.is_relative_to(MAIN_PROJECT.resolve());return f
def validate_compiler(c,files):
 assert c['compilerExitCode']==0
 prefixes='production/batches/architectural-111-20261106/'
 expected={prefixes+'prospect-refuge-unity-source/ProspectRefugeExperiment.cs':MAIN_FOLDER+'/ProspectRefugeExperiment.cs',prefixes+'prospect-refuge-unity-source/Editor/ProspectRefugeBuilder.cs':MAIN_FOLDER+'/Editor/ProspectRefugeBuilder.cs',prefixes+'prospect-refuge-closeup-source/ProspectRefugeCloseupCamera.cs':FOLDER+'/ProspectRefugeCloseupCamera.cs',prefixes+'prospect-refuge-closeup-source/Editor/ProspectRefugeCloseupBuilder.cs':FOLDER+'/Editor/ProspectRefugeCloseupBuilder.cs'}
 assert isinstance(c.get('sourceHashes'),dict)and set(c['sourceHashes'])==set(expected),'Exact nonempty four-source compile proof required'
 staged={r['target']:r for r in files if r['target'].endswith('.cs')};assert set(staged)==set(expected.values()),'Uncompiled imported C# input'
 for source,target in expected.items():assert sha(ROOT/source)==c['sourceHashes'][source]==staged[target]['sha256'],'Stale/mismatched compiled source'

def project_for(fingerprint):
 assert isinstance(fingerprint,str)and len(fingerprint)==64 and all(c in'0123456789abcdef'for c in fingerprint),'Canonical preparation fingerprint required'
 path=(PROJECT_ROOT/fingerprint[:24]).resolve();assert path.is_relative_to(PROJECT_ROOT.resolve());return path
def preflight():
 authorize();ev=read(EVIDENCE);assert ev['topicId']=='06.02'and ev['captureComplete']is True
 attempt=Path(ev['output']).resolve();assert attempt.is_relative_to((MEDIA/'shorts-leveldesign-06-02/native-attempts').resolve())
 for row in ev['captureProofs']:
  f=Path(row['path']).resolve();assert f.is_relative_to(attempt)and sha(f)==row['sha256'],'Main native proof changed'
 rec=read(attempt/'scene-record.json');assert rec['fingerprint']==ev['fingerprint']and rec['actualSceneFilesSaved']is True
 files=[];seen=set()
 for row in rec['files']+rec['sharedDependencies']:
  f=owned_main(row['path']);assert f.stat().st_size==row['bytes']and sha(f)==row['sha256'],'Main stage/source file changed'
  if row['path'].casefold()not in seen:files.append(dict(sourceAbsolute=str(f),target=row['path'],sha256=row['sha256']));seen.add(row['path'].casefold())
 for f in sorted(SOURCE.rglob('*')):
  if f.is_file():files.append(dict(sourceAbsolute=str(f.resolve()),target=FOLDER+'/'+f.relative_to(SOURCE).as_posix(),sha256=sha(f)))
 assert len({r['target'].casefold()for r in files})==len(files)
 config=read(SOURCE/'closeup-config.json');assert all(type(config[k])is int and config[k]==CONTRACT[k]for k in('frames','fps','width','height'))
 assert config['cameraOffset']==dict(x=3.2,y=2.8,z=-4.4)and config['lookOffset']==dict(x=0.,y=.9,z=.6)and config['verticalFieldOfView']==32.
 references=[]
 for mode in CONTRACT['modes']:
  folder=attempt/mode;references.append(dict(mode=mode,statesSHA256=sha(folder/'states.jsonl'),configSHA256=sha(folder/'capture-config.json'),commandTapeSHA256=sha(folder/'command-tape.json')))
 reference=dict(mainAttempt=str(attempt),mainFingerprint=ev['fingerprint'],modes=references)
 packages=(MAIN_PROJECT/'Packages/manifest.json').read_bytes()
 generated={FOLDER+'/main-reference.json':json.dumps(reference,sort_keys=True,separators=(',',':')), 'Packages/manifest.json':packages.decode('utf8'),'ProjectSettings/ProjectVersion.txt':'m_EditorVersion: 6000.6.0f1\n'}
 compiler=None
 if COMPILER.exists():
  c=read(COMPILER);validate_compiler(c,files)
  compiler=pin(COMPILER)
 identity=dict(topicId='06.02',mainCaptureFingerprint=ev['fingerprint'],files=files,generated=generated,config=config,editorVersion='6000.6.0f1',contract=CONTRACT)
 fingerprint=digest(identity)
 return dict(schemaVersion='06.02-closeup-staging-v1',topicId='06.02',project=str(project_for(fingerprint)),fingerprint=fingerprint,identity=identity,files=files,generated=generated,config=config,mainReference=reference,mainEvidenceAudit=pin(EVIDENCE),staticCompiler=compiler,editorVersion='6000.6.0f1',captureEntry=ENTRY,actualSceneFilesSaved=False,gpuStarted=False)
def stage(r):
 assert r['staticCompiler'],'Fresh static closeup compiler proof required';assert preflight()['fingerprint']==r['fingerprint']
 project=project_for(r['fingerprint']);assert Path(r['project']).resolve()==project,'Staging project must match preparation fingerprint'
 pending=[]
 for row in r['files']:
  src=Path(row['sourceAbsolute']).resolve();dst=(project/row['target']).resolve();assert dst.is_relative_to(project)and sha(src)==row['sha256'];assert not dst.exists()or sha(dst)==row['sha256'],'Preserve changed closeup staged file';pending.append((src,dst,row['sha256']))
 for target,text in r['generated'].items():assert not(project/target).exists()or(project/target).read_bytes()==text.encode('utf8'),'Preserve changed generated closeup inputs'
 for src,dst,value in pending:
  dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copy2(src,dst)
  assert sha(dst)==value
 for target,text in r['generated'].items():
  dst=project/target;dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():dst.write_bytes(text.encode('utf8'))
 if REPORT.exists()and read(REPORT).get('fingerprint')!=r['fingerprint']:
  old=read(REPORT);project_for(old['fingerprint']);archive=MEDIA/'shorts-leveldesign-06-02/closeup-staging-history'/old['fingerprint']/'closeup-staging-v1.json';archive.parent.mkdir(parents=True,exist_ok=True)
  if archive.exists():assert sha(archive)==sha(REPORT),'Preserve differing staged-history receipt'
  else:shutil.copy2(REPORT,archive)
 r['sourceStageComplete']=True;tmp=REPORT.with_suffix('.json.tmp');assert not tmp.exists();tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,REPORT)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',action='store_true');a=p.parse_args()
 try:r=preflight()
 except(FileNotFoundError,AssertionError)as e:
  if a.stage:raise
  print(json.dumps(dict(ready=False,reason=str(e),staged=False,gpuStarted=False)));return
 if a.stage:stage(r)
 print(json.dumps(dict(ready=bool(r['staticCompiler']),fingerprint=r['fingerprint'],project=r['project'],staged=a.stage,mainCaptureFingerprint=r['mainReference']['mainFingerprint'],gpuStarted=False)))
if __name__=='__main__':main()
