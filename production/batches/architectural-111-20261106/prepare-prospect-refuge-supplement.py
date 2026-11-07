"""Exact06.02 supplementary source preflight; default never stages/launches Unity.

Reuse the immutable main source-only staging primitives in an isolated module.
Only an explicit --stage writes this separate fingerprinted C project/report.
"""
from __future__ import annotations
import argparse,importlib.util,json,math,os,re,shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
SOURCE=HERE/'prospect-refuge-supplement-source';RECORD=ROOT/'projects/shorts-leveldesign-06-02'
SOURCE_REPORT=RECORD/'supplementary-unity-preparation-v1.json';REPORT=RECORD/'supplementary-unity-staging-v1.json'
FOLDER='Assets/VideoScenes/architectural-111-20261106/06-02-Supplement'
SHADER='Assets/VideoScenes/architectural-111-20261106/ArchitecturalSurface.shader'
ENTRY='Yamyam.Architectural111.ProspectRefugeSupplement.Editor.EditorBuilder.Capture'
MODES=['scale','protected','atrium','structure','openings','refuge','courtyard','plaza','alcove','flying','shield','boss','footings']
CONTRACT=dict(frames=720,fps=60,width=1920,height=1080,cameras=['player','observer'],modes=MODES)
BASE_PREP_SHA='906e9f38cc13161b32b455bd3fe710f5b84ce9b8b2e8fbaf3f75a79ea3ffb74a'
MANIFEST=dict(dependencies={name:'1.0.0'for name in('com.unity.modules.physics','com.unity.modules.animation','com.unity.modules.imgui','com.unity.modules.jsonserialize','com.unity.modules.imageconversion')})
API_RSP=MEDIA/'unity-prospect-refuge-capture/Library/Bee/artifacts/1900b0aEDbg.dag/Assembly-CSharp.rsp'
ENGINE_MODULES=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data/Managed/UnityEngine')

def base_module():
 p=HERE/'prepare-prospect-refuge-unity.py';sp=importlib.util.spec_from_file_location('supplement_isolated_source_primitives',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 assert m.sha(p)==BASE_PREP_SHA,'Main staging primitive changed; audit before updating supplementary adapter'
 return m

base=base_module();read=base.read;sha=base.sha;digest=base.digest

def validate_config(c):
 base.finite_tree(c)
 assert c['schemaVersion']=='06.02-supplement-unity-config-v1'and c['sourceKind']=='our-authored-illustration'and c['sceneFolder']==FOLDER
 assert all(type(c[k])is int and c[k]==CONTRACT[k]for k in('frames','fps','width','height'))
 assert isinstance(c['frameConvention'],str)and 'frame0'in c['frameConvention']and '719/60'in c['frameConvention']
 assert [r['mode']for r in c['scenes']]==MODES and len({r['sceneFile']for r in c['scenes']})==len(MODES)
 for row in c['scenes']:
  assert re.fullmatch(r'[A-Za-z0-9_-]+\.unity',row['sceneFile'])and row['purpose']and row['paragraphs']
  assert all(type(n)is int and n>0 for n in row['paragraphs'])
 assert c['playerHeight']>2*c['playerRadius']>0 and 0<c['playerEyeHeight']<c['playerHeight']
 assert all(c[k]>0 for k in('gravity','jumpSpeed','walkSpeed','shotSpeed','enemyShotSpeed'))
 assert set(c['observerPosition'])==set(c['observerLookAt'])=={'x','y','z'}
 assert c['observerPosition']!=c['observerLookAt']
 end=0;ids=set()
 for row in c['encounterCommands']:
  assert set(row)=={'id','startFrame','endFrameExclusive','velocityX'}and row['id']and row['id']not in ids;ids.add(row['id'])
  assert type(row['startFrame'])is type(row['endFrameExclusive'])is int and row['startFrame']==end<row['endFrameExclusive']<=720
  assert type(row['velocityX'])in(int,float)and math.isfinite(row['velocityX']);end=row['endFrameExclusive']
 assert end==720 and len(ids)==5
 for key in('jumpFrames','fireFrames'):
  assert c[key]==sorted(set(c[key]))and all(type(f)is int and 0<=f<719 for f in c[key])
 return dict(frames=720,sourceKind='our-authored-illustration',sameEncounterTapeModes=['flying','shield','boss'],humanDecisionMeasured=False,
             geometricRoutesAreScripted=True,encounterRoutesUseCharacterController=True,fullThirteenModeCaptureClaim=False)

def preflight():
 base.authorization();c=read(SOURCE/'config.json');smoke=validate_config(c);report=read(SOURCE_REPORT)
 assert report['topicId']=='06.02'and report['plannedSceneCount']==13,'Final13mode source owner preparation required'
 expected={'Experiment.cs','Editor/EditorBuilder.cs','config.json'};actual={p.relative_to(SOURCE).as_posix()for p in SOURCE.rglob('*')if p.is_file()}
 assert expected<=actual<=expected|{n+'.meta'for n in expected},'Unexpected/missing supplementary source input'
 reported=set()
 for row in report['sourceInputs']:
  p=(ROOT/row['path']).resolve();assert p.is_relative_to(SOURCE.resolve())and sha(p)==row['sha256'],'Source owner pin changed'
  reported.add(p.relative_to(SOURCE.resolve()).as_posix())
 assert reported==expected
 assert [r['mode']for r in report['plannedScenes']]==MODES
 compiler=report['staticCompilerPreflight'];cp=Path(compiler['path']).resolve()
 assert cp.is_relative_to((MEDIA/'shorts-leveldesign-06-02').resolve())and sha(cp)==compiler['sha256'],'Current source-bound CPUcompile proof required'
 checked=read(cp);assert checked['compilerExitCode']==0
 assert set(checked['sourceHashes'])=={'Experiment.cs','Editor/EditorBuilder.cs'}
 for name,value in checked['sourceHashes'].items():assert sha(SOURCE/name)==value,'Supplementary static compiler proof stale'
 provenance=read(base.ASSET/'provenance.json');assert provenance['license']=='CC0';files=[]
 for row in provenance['files']:
  src=base.ASSET/row['path'];assert sha(src)==row['sha256']
  for p in(src,Path(str(src)+'.meta')):
   if p.exists():files.append(dict(source=p.relative_to(ROOT).as_posix(),target='Assets/ThirdParty/KayKitAdventurers/'+p.name,sha256=sha(p)))
 p=base.ASSET/'provenance.json';files.append(dict(source=p.relative_to(ROOT).as_posix(),target='Assets/ThirdParty/KayKitAdventurers/provenance.json',sha256=sha(p)))
 if Path(str(p)+'.meta').exists():
  p=Path(str(p)+'.meta');files.append(dict(source=p.relative_to(ROOT).as_posix(),target='Assets/ThirdParty/KayKitAdventurers/provenance.json.meta',sha256=sha(p)))
 for p in sorted(SOURCE.rglob('*')):
  if p.is_file():files.append(dict(source=p.relative_to(ROOT).as_posix(),target=FOLDER+'/'+p.relative_to(SOURCE).as_posix(),sha256=sha(p)))
 shader=ROOT/'unity/VideoEditing'/SHADER
 assert sha(shader)==sha(HERE/'unity-source/ArchitecturalSurface.shader'),'Shared canonical shader changed'
 for p in(shader,Path(str(shader)+'.meta')):
  assert p.is_file();files.append(dict(source=p.relative_to(ROOT).as_posix(),target=SHADER+('.meta'if p.suffix=='.meta'else''),sha256=sha(p)))
 assert len({r['target'].casefold()for r in files})==len(files)
 font=Path('C:/Windows/Fonts/malgun.ttf');assert font.is_file(),'Installed dynamicfont source required; never redistribute its binary'
 external=[dict(path=str(font),sha256=sha(font),role='Installed OS font used by serialized dynamicfont descriptor; binary not staged/exported')]
 rsp=API_RSP.read_text(encoding='utf-8-sig');api=[]
 for name in('UnityEngine.TextCoreFontEngineModule.dll','UnityEngine.TextCoreTextEngineModule.dll','UnityEngine.TextRenderingModule.dll'):
  path=ENGINE_MODULES/name;assert name in rsp and path.is_file(),'Actual Unity-generated core API reference proof required'
  api.append(dict(path=str(path),sha256=sha(path)))
 identity=dict(topicId='06.02',config=c,sourcePins=files,externalInputs=external,engineApiModules=api,editorVersion='6000.6.0f1',projectManifest=MANIFEST,captureContract=CONTRACT)
 fp=digest(identity);project=MEDIA/'unity-prospect-refuge-supplement-capture'/fp[:24]
 return dict(schemaVersion='06.02-supplementary-unity-staging-v1',topicId='06.02',fingerprint=fp,project=str(project),editorVersion='6000.6.0f1',
  renderPipeline='Isolated Built-in; no Editor launched by preparer',config=c,files=files,externalInputs=external,engineApiModules=api,captureEntry=ENTRY,captureContract=CONTRACT,
  intendedScenes=[FOLDER+'/'+r['sceneFile']for r in c['scenes']],sourcePreparation=dict(path=str(SOURCE_REPORT),sha256=sha(SOURCE_REPORT)),
  staticCompilerPreflight=dict(path=str(cp),sha256=sha(cp),compilerExitCode=0),preparerSHA256=sha(__file__),basePreparerSHA256=BASE_PREP_SHA,projectManifest=MANIFEST,
  apiReferenceEvidence=dict(path=str(API_RSP),sha256=sha(API_RSP),basis='Actual Unity-generated Assembly-CSharp references with verified five-module manifest; TextRendering is core, not an invented UPMpackage'),
  sourceKind='our-authored-illustration',configSmoke=smoke,actualSceneFilesSaved=False,unityLaunched=False,captureStarted=False,humanApproval=False,platformActions=[])

def stage(report):
 assert report['staticCompilerPreflight']and report['fingerprint']==preflight()['fingerprint'],'Fresh source/compile preparation required'
 project=Path(report['project']).resolve();assert project.parent==(MEDIA/'unity-prospect-refuge-supplement-capture').resolve()and project.name==report['fingerprint'][:24]
 generated={'Packages/manifest.json':(json.dumps(MANIFEST,indent=2)+'\n').encode(),'ProjectSettings/ProjectVersion.txt':b'm_EditorVersion: 6000.6.0f1\n'}
 targets=[]
 for row in report['files']:
  source=(ROOT/row['source']).resolve();target=(project/row['target']).resolve()
  assert source.is_relative_to(ROOT.resolve())and target.is_relative_to(project)and sha(source)==row['sha256']
  assert not target.exists()or sha(target)==row['sha256'],'Preserve changed staged supplementary input';targets.append((source,target,row['sha256']))
 for name,data in generated.items():assert not(project/name).exists()or(project/name).read_bytes()==data,'Preserve changed supplementary project settings'
 for source,target,value in targets:
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copy2(source,target)
  assert sha(target)==value
 for name,data in generated.items():
  target=project/name;target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():target.write_bytes(data)
 validate_manifest(project/'Packages/manifest.json');report['sourceStageComplete']=True
 tmp=REPORT.with_suffix('.json.tmp');assert not tmp.exists();tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,REPORT)

def validate_manifest(path):
 assert read(path)==MANIFEST,'Exact verified five-module Built-in manifest required; no unverified package additions'

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',action='store_true');args=parser.parse_args()
 try:report=preflight()
 except(FileNotFoundError,KeyError,AssertionError)as error:
  if args.stage:raise
  print(json.dumps(dict(ready=False,reason=str(error),staged=False,unityLaunched=False)));return
 if args.stage:stage(report)
 print(json.dumps(dict(ready=True,fingerprint=report['fingerprint'],project=report['project'],staged=args.stage,unityLaunched=False,actualSavedScenes=False)))

if __name__=='__main__':main()
