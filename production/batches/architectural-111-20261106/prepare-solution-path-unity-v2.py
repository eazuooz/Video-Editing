"""11.05 CPU-only source/API preparation. Default readonly; --stage is explicit.
Never launches Unity, a model, media encode or platform tool. Static compile is
an existing hash-bound three-source Roslyn receipt, not an actual render pass.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106');TOPIC='11.05';P=ROOT/'projects/shorts-leveldesign-11-05';BASE=MEDIA/P.name
SOURCE=HERE/'solution-path-unity-source-v2';ASSET=ROOT/'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers';FOLDER='Assets/VideoScenes/architectural-111-20261106/11-05-SolutionPathV2';SHADER='Assets/VideoScenes/architectural-111-20261106/ArchitecturalSurface.shader'
REPORT=P/'native-controller-preparation-v2.json';PROJECTS=MEDIA/'11-05-unity-proj';ENTRY='Yamyam.Architectural111.SolutionPathV2.Editor.EditorBuilder.Capture';VERSION='6000.6.0f1';AUTH='explicitArchitectural111Batch20261106'
MODES=['construction','branches-a','branches-b','templates-a','templates-b','threats-a','threats-b','broken-link'];CS=['GraphModel.cs','Experiment.cs','Editor/EditorBuilder.cs'];ASSETS=['Knight.fbx','Knight.fbx.meta','knight_texture.png','knight_texture.png.meta','LICENSE.txt','LICENSE.txt.meta','provenance.json','provenance.json.meta']
class Pending(RuntimeError):pass
def need(ok,message):
 if not ok:raise Pending(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
def canonical(name):
 need(isinstance(name,str)and'\\'not in name and not name.startswith('/')and not re.match(r'^[A-Za-z]:',name),'Noncanonical relative path');need(all(x not in('','.','..')for x in name.split('/')),'Traversal/noncanonical path');return name

def authority():
 a=read(ROOT/'shared/publishing/video-production-control.json')[AUTH];need(a.get('userEvidence')=='111개 전체 제작 들어가줘'and a.get('status')not in('paused','stopped','cancelled'),'Exact111 authority is inactive')
 need(a.get('automaticAdvanceWithinExactList')and not a.get('automaticAdvanceOutsideList')and not a.get('youtubeAuthorized')and a.get('humanFinalReviewRequired'),'Local exact111 boundary changed')
 b=read(HERE/'batch.json');need(len(b['projects'])==111 and b['localFinalReviewOnly']and sha(ROOT/b['sourceCatalog'])==b['sourceCatalogSHA256'],'Exact catalog changed')
 need(read(HERE/'checkpoint.json').get('currentTopicId')==TOPIC,'11.05 is not currently selected');p=read(P/'project.json');need(p['topicId']==TOPIC and p['localFinalReviewOnly']and not p['youtubeAuthorized'],'Selected project boundary changed')

def compiler_proof(config_sha):
 expected={name:sha(SOURCE/name)for name in CS};found=[]
 for p in sorted((BASE/'unity-cpu-preflight').glob('*/compile-receipt.json'),reverse=True):
  try:
   c=read(p)
   if c.get('schemaVersion')!='11-05-solution-path-static-compiler-v1'or c.get('compilerExitCode')!=0 or c.get('staticCompilationPassed')is not True or c.get('sourceHashes')!=expected:continue
   if c.get('config')!=pin(SOURCE/'config.json'):continue
   need(set(c['sourceHashes'])==set(CS),'Exact nonempty3-source compile proof required')
   for name in('compiler','dotnet','actualResponseFile'):
    q=c[name];need(sha(q['path'])==q['sha256'],'Compiler proof artifact changed')
   lines=Path(c['actualResponseFile']['path']).read_text(encoding='utf-8-sig').splitlines();actual=[Path(x.strip().strip('"')).resolve()for x in lines if x.strip().strip('"').lower().endswith('.cs')]
   need(len(actual)==3 and set(actual)=={(SOURCE/n).resolve()for n in CS},'Compiler did not compile exactly the three imported C# sources')
   need(c.get('unityEditorLaunched')is False and c.get('gpuStarted')is False,'Static compiler proof is mislabeled');found.append(pin(p))
  except(OSError,ValueError,KeyError,Pending):continue
 return found[0]if found else None

def preflight():
 authority();config=read(SOURCE/'config.json');need((config['frames'],config['fps'],config['width'],config['height'])==(1200,60,1920,1080),'Finite source capture contract changed')
 need([r['id']for r in config['modes']]==MODES and all(Path(r['sceneFile']).name==r['sceneFile']and r['sceneFile'].endswith('.unity')for r in config['modes']),'Exact8 independent scenes/modes required')
 library=read(ROOT/'shared/assets/unity-asset-library.json');need(library['targetEditorVersion']==VERSION,'Unity library version differs');license=read(ASSET/'provenance.json');need(license['license']=='CC0','Knight license changed')
 for r in license['files']:need(sha(ASSET/r['path'])==r['sha256'],'Licensed raw asset changed')
 files=[]
 for name in CS+['config.json']:
  files.append(dict(source=(SOURCE/name).relative_to(ROOT).as_posix(),target=FOLDER+'/'+name,sha256=sha(SOURCE/name)))
 for name in ASSETS:files.append(dict(source=(ASSET/name).relative_to(ROOT).as_posix(),target='Assets/ThirdParty/KayKitAdventurers/'+name,sha256=sha(ASSET/name)))
 for name in(SHADER,SHADER+'.meta'):files.append(dict(source='unity/VideoEditing/'+name,target=name,sha256=sha(ROOT/'unity/VideoEditing'/name)))
 for r in files:canonical(r['source']);canonical(r['target'])
 need(len({r['target'].casefold()for r in files})==len(files),'Duplicate staged paths')
 packages=dict(dependencies={k:'1.0.0'for k in('com.unity.modules.physics','com.unity.modules.animation','com.unity.modules.imgui','com.unity.modules.jsonserialize','com.unity.modules.imageconversion')})
 generated={'Packages/manifest.json':json.dumps(packages,indent=2)+'\n','ProjectSettings/ProjectVersion.txt':'m_EditorVersion: '+VERSION+'\n'}
 contract=dict(frames=1200,fps=60,width=1920,height=1080,cameras=['player','observer'],modes=MODES)
 identity=dict(topicId=TOPIC,editorVersion=VERSION,files=files,generated=generated,contract=contract,configSHA256=sha(SOURCE/'config.json'),font=pin('C:/Windows/Fonts/malgun.ttf'))
 fp=digest(identity);project=PROJECTS/fp[:16];compiler=compiler_proof(identity['configSHA256'])
 return dict(schemaVersion='11-05-native-controller-preparation-v1',topicId=TOPIC,fingerprint=fp,physicalInputFingerprint=fp,identity=identity,project=str(project),sourceStageComplete=False,files=files,generated=generated,config=config,captureContract=contract,captureEntry=ENTRY,cliKeys=['-solutionOutput','-solutionFingerprint','-solutionModes'],intendedScenePaths=[FOLDER+'/'+r['sceneFile']for r in config['modes']],staticCompilerProof=compiler,assetLibrary=pin(ROOT/'shared/assets/unity-asset-library.json'),assetProvenance=pin(ASSET/'provenance.json'),sourceKind='Own graph/flat3Dwalk implementation; not commercial Spelunky algorithm or gameplay',actualSceneFilesSaved=False,nativeCaptureComplete=False,unityLaunched=False,gpuStarted=False,humanApproval=False,platformActions=[],executionPolicy='Root must explicitly choose --modes construction pilot after review. No automatic all8 capture; subset fingerprint is independent; matching physical/mode sources may be reused without rewriting original proofs.',controllerSources=[pin(HERE/n)for n in('prepare-solution-path-unity-v2.py','run-solution-path-native-v2.py','verify-solution-path-native-v2.py','verify-solution-path-animation-v2.py')],resourceRuntime=pin(HERE/'run-first-native.py'),resourceClassifier=dict(source=pin(HERE/'prospect-refuge-resource-qualification.py'),classifierOriginTopicId='06.02',currentJobTopicId='11.05',scope='Only exact previously audited two idle Edge trees; unchanged8GiBguard and fresh identity/CPU/IO/TCP/GPU checks; no ownership/completion/termination grant'),maximumFlatSnapshotPathLength=len(str(BASE/'native-attempts'/'YYYYMMDD-HHMMSS-0000000000'/'capture'/'construction'/'editable'/('f'*64+'.bin'))))

def stage(result):
 need(result['staticCompilerProof'],'Actual exact3-source API compiler proof required before --stage');need(preflight()['fingerprint']==result['fingerprint'],'Source changed before stage');project=Path(result['project']).resolve();need(project.is_relative_to(PROJECTS.resolve()),'Isolated project escaped scope')
 pairs=[]
 for r in result['files']:
  src=(ROOT/r['source']).resolve();dst=(project/r['target']).resolve();need(src.is_relative_to(ROOT)and dst.is_relative_to(project)and sha(src)==r['sha256'],'Stage input escaped scope/changed');need(not dst.exists()or sha(dst)==r['sha256'],'Preserve changed staged input');pairs.append((src,dst))
 for name,text in result['generated'].items():need(not(project/name).exists()or(project/name).read_bytes()==text.encode('utf-8'),'Preserve changed isolated settings')
 for src,dst in pairs:
  dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copy2(src,dst)
 for name,text in result['generated'].items():
  dst=project/name;dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():dst.write_bytes(text.encode('utf-8'))
 if REPORT.exists()and read(REPORT).get('fingerprint')!=result['fingerprint']:
  old=REPORT.read_bytes();dest=BASE/'preparation-history'/sha(REPORT)/REPORT.name;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():need(dest.read_bytes()==old,'Changed historical prep receipt')
  else:dest.write_bytes(old)
 result['sourceStageComplete']=True;save(REPORT,result)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',action='store_true');a=p.parse_args()
 try:
  r=preflight()
  if a.stage:stage(r)
  print(json.dumps(dict(ready=bool(r['staticCompilerProof']),topicId=TOPIC,physicalInputFingerprint=r['fingerprint'],staged=a.stage,project=r['project'],compilerProof=r['staticCompilerProof'],unityLaunched=False,gpuStarted=False),ensure_ascii=False));return 0
 except(Exception)as e:
  if a.stage:raise
  print(json.dumps(dict(ready=False,pending=str(e),staged=False,unityLaunched=False,gpuStarted=False),ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
