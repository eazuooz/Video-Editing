"""06.02 source-only CPU preflight. Default writes nothing and launches no process.
--stage only after a hash-bound static C# compiler proof; never starts Unity/GPU.
C source owner keeps unity-preparation-v1.json; this helper owns unity-staging-v1.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
PROJECT=MEDIA/'unity-prospect-refuge-capture';SOURCE=HERE/'prospect-refuge-unity-source'
ASSET=ROOT/'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers'
FOLDER='Assets/VideoScenes/architectural-111-20261106/06-02'
RECORD=ROOT/'projects/shorts-leveldesign-06-02';SOURCE_REPORT=RECORD/'unity-preparation-v1.json';REPORT=RECORD/'unity-staging-v1.json'
ENTRY='Yamyam.Architectural111.ProspectRefuge.Editor.ProspectRefugeBuilder.Capture'
AUTH='explicitArchitectural111Batch20261106'
CONTRACT=dict(frames=600,fps=60,width=1920,height=1080,cameras=['player','observer'],modes=['baseline','shifted'])
SCENES=[FOLDER+'/S02-ProspectRefuge-Baseline.unity',FOLDER+'/S03-ProspectRefuge-Shifted.unity']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def finite_tree(x):
 if isinstance(x,dict):
  for v in x.values():finite_tree(v)
 elif isinstance(x,list):
  for v in x:finite_tree(v)
 elif type(x)in(int,float):assert math.isfinite(x),'Finite config values required'
 elif not isinstance(x,str):raise AssertionError('Only explicit numeric/string config fields allowed')
def validate_config(c):
 finite_tree(c)
 assert c['schemaVersion']=='06-02-prospect-refuge-capture-v1' and c['onlyChangedParameter']=='secondCoverOffsetX'
 assert all(type(c[k])is int and c[k]==CONTRACT[k]for k in ('frames','fps','width','height'))
 assert c['baselineSecondCoverOffsetX']==0 and c['shiftedSecondCoverOffsetX']>0
 assert c['capsuleHeight']>2*c['capsuleRadius']>0 and 0<c['skinWidth']<c['capsuleRadius'] and c['stepOffset']>=0 and c['groundStickSpeed']>0
 assert 0<c['hipsSampleHeight']<c['torsoSampleHeight']<c['headSampleHeight']<c['capsuleHeight']
 assert c['firstCoverCenter']['y']+c['firstCoverSize']['y']/2<c['headSampleHeight']<c['secondCoverSize']['y']
 assert 0<c['enemyTurnStartSeconds']<c['enemyTurnEndSeconds']<c['enemyPauseStartSeconds']<c['frames']/c['fps']
 assert 0<c['enemyHorizontalHalfFovDegrees']<90 and c['enemyRange']>0
 assert len(c['commands'])==4 and len({r['id']for r in c['commands']})==4
 end=0
 for r in c['commands']:
  assert set(r)=={'id','startFrame','endFrameExclusive','velocity'} and isinstance(r['id'],str)and r['id']
  assert type(r['startFrame'])is type(r['endFrameExclusive'])is int and r['startFrame']==end<r['endFrameExclusive']<=c['frames']
  assert set(r['velocity'])=={'x','y','z'} and r['velocity']['y']==0;end=r['endFrameExclusive']
 assert end==600
 return dict(status='finite-config-and-contiguous-tape-validated; actual-physics-unverified',appliedInputFrames=[0,598],lastCaptureFrame=599,changedParameter='secondCoverOffsetX',humanDecisionMeasured=False)
def authorization():
 a=read(ROOT/'shared/publishing/video-production-control.json')[AUTH]
 assert a['userEvidence']=='111개 전체 제작 들어가줘'and a['status']not in('paused','stopped','cancelled')
 assert a['automaticAdvanceWithinExactList']and not a['automaticAdvanceOutsideList']and a['humanFinalReviewRequired']and not a['youtubeAuthorized']
 batch=read(HERE/'batch.json');assert len(batch['projects'])==111 and batch['localFinalReviewOnly']and sha(ROOT/batch['sourceCatalog'])==batch['sourceCatalogSHA256']
 assert any(r['topicId']=='06.02'and r['slug']==RECORD.name for r in batch['projects'])
 selected=read(HERE/'checkpoint.json');assert selected.get('nextSelectedTopicId')=='06.02' or selected.get('currentTopicId')=='06.02','Only currently selected06.02 capture authorized'
 pr=read(RECORD/'project.json');assert pr['topicId']=='06.02'and pr['localFinalReviewOnly']
def preflight():
 authorization();config=read(SOURCE/'capture-config.json');smoke=validate_config(config)
 source_report=read(SOURCE_REPORT);assert source_report['topicId']=='06.02'
 expected_sources={'ProspectRefugeExperiment.cs','Editor/ProspectRefugeBuilder.cs','capture-config.json'}
 reported=set()
 for row in source_report['sourceInputs']:
  path=(ROOT/row['path']).resolve();assert path.is_relative_to(SOURCE.resolve())and sha(path)==row['sha256'],'Source-owner preparation pin changed';reported.add(path.relative_to(SOURCE.resolve()).as_posix())
 assert reported==expected_sources
 actual={f.relative_to(SOURCE).as_posix()for f in SOURCE.rglob('*')if f.is_file()}
 assert actual<=expected_sources|{name+'.meta'for name in expected_sources}and expected_sources<=actual,'Unexpected native source input'
 library=read(ROOT/'shared/assets/unity-asset-library.json');assert library['targetEditorVersion']=='6000.6.0f1'
 provenance=read(ASSET/'provenance.json');assert provenance['license']=='CC0';files=[]
 for row in provenance['files']:
  src=ASSET/row['path'];assert sha(src)==row['sha256']
  for f in(src,Path(str(src)+'.meta')):
   if f.exists():files.append(dict(source=f.relative_to(ROOT).as_posix(),target='Assets/ThirdParty/KayKitAdventurers/'+f.name,sha256=sha(f)))
 files.append(dict(source=(ASSET/'provenance.json').relative_to(ROOT).as_posix(),target='Assets/ThirdParty/KayKitAdventurers/provenance.json',sha256=sha(ASSET/'provenance.json')))
 for f in sorted(SOURCE.rglob('*')):
  if f.is_file():files.append(dict(source=f.relative_to(ROOT).as_posix(),target=FOLDER+'/'+f.relative_to(SOURCE).as_posix(),sha256=sha(f)))
 shader=HERE/'unity-source/ArchitecturalSurface.shader';files.append(dict(source=shader.relative_to(ROOT).as_posix(),target=FOLDER+'/ArchitecturalSurface.shader',sha256=sha(shader)))
 assert {FOLDER+'/'+s for s in ('ProspectRefugeExperiment.cs','Editor/ProspectRefugeBuilder.cs','capture-config.json')}<={r['target']for r in files}
 assert len({r['target'].casefold()for r in files})==len(files),'Duplicate staged target'
 compiler_path=MEDIA/'shorts-leveldesign-06-02/unity-cpu-preflight/compile.json';compiler=None
 if compiler_path.exists():
  checked=read(compiler_path);assert checked['compilerExitCode']==0 and checked['sourceHashes']
  for name,value in checked['sourceHashes'].items():assert sha(SOURCE/name)==value,'Static compiler proof is stale'
  assert {'ProspectRefugeExperiment.cs','Editor/ProspectRefugeBuilder.cs'}<=set(checked['sourceHashes'])
  compiler=dict(path=str(compiler_path),sha256=sha(compiler_path),compilerExitCode=0,scope=checked['scope'])
 result=dict(schemaVersion='06-02-unity-staging-v1',topicId='06.02',project=str(PROJECT),editorVersion='6000.6.0f1',renderPipeline='Isolated Built-in; actual Unity capture pending',sourcePreparation=dict(path=str(SOURCE_REPORT),sha256=sha(SOURCE_REPORT)),config=config,files=files,assetProvenance=provenance,staticCompilerPreflight=compiler,preparerSHA256=sha(__file__),intendedScenes=SCENES,captureEntry=ENTRY,cliKeys=['-prospectRefugeOutput','-prospectRefugeFingerprint','-prospectRefugeModes'],captureContract=CONTRACT,configSmoke=smoke,actualSceneFilesSaved=False,unityLaunched=False,captureStarted=False,resourceGate='Scoped singleton/shared cooperative GPU lease plus exact current11106.02 authority and fresh user-app/game/editor/model/media/resource checks before Unity launch',sourceKind='Own physical collision and declared-point visibility implementation, not commercial gameplay',outputContract=dict(modeFiles=['mode-complete.json','mode-contract.json','capture-config.json','command-tape.json','trace.csv','states.jsonl','rays.jsonl','projected-anchors.jsonl','player/0000.jpg..0599.jpg','observer/0000.jpg..0599.jpg'],rootFiles=['scene-record.json']),humanApproval=False,platformActions=[])
 result['fingerprint']=digest(dict(topicId='06.02',config=config,sourcePins=files,editorVersion=result['editorVersion'],captureContract=CONTRACT))
 return result
def stage(r):
 assert r['staticCompilerPreflight'],'Fresh static C# API compile required before staging'
 assert r['fingerprint']==preflight()['fingerprint'],'Inputs changed before source staging'
 generated={'Packages/manifest.json':(json.dumps(dict(dependencies={k:'1.0.0'for k in('com.unity.modules.physics','com.unity.modules.animation','com.unity.modules.imgui','com.unity.modules.jsonserialize','com.unity.modules.imageconversion')}),indent=2)+'\n').encode(),'ProjectSettings/ProjectVersion.txt':b'm_EditorVersion: 6000.6.0f1\n'}
 targets=[]
 for row in r['files']:
  src=(ROOT/row['source']).resolve();dst=(PROJECT/row['target']).resolve();assert src.is_relative_to(ROOT.resolve())and dst.is_relative_to(PROJECT.resolve())and sha(src)==row['sha256']
  assert not dst.exists()or sha(dst)==row['sha256'],'Preserve changed staged input';targets.append((src,dst,row['sha256']))
 for name,data in generated.items():assert not(PROJECT/name).exists()or(PROJECT/name).read_bytes()==data,'Preserve changed project settings'
 for src,dst,value in targets:
  dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copy2(src,dst)
  assert sha(dst)==value
 for name,data in generated.items():
  f=PROJECT/name;f.parent.mkdir(parents=True,exist_ok=True)
  if not f.exists():f.write_bytes(data)
 r['sourceStageComplete']=True;tmp=REPORT.with_suffix('.json.tmp');assert not tmp.exists();tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,REPORT)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',action='store_true');a=p.parse_args()
 try:r=preflight()
 except(FileNotFoundError,AssertionError)as e:
  if a.stage:raise
  print(json.dumps(dict(ready=False,reason=str(e),staged=False,unityLaunched=False,captureStarted=False)));return
 if a.stage:stage(r)
 print(json.dumps(dict(ready=bool(r['staticCompilerPreflight']),sourceInputsReady=True,reason=None if r['staticCompilerPreflight']else'Static compiler proof required before staging',fingerprint=r['fingerprint'],staged=a.stage,project=str(PROJECT),report=str(REPORT)if a.stage else None,unityLaunched=False,captureStarted=False)))
if __name__=='__main__':main()
