"""Source-only four-mode correction preparation; never edits the original13.

Default readiness only. Explicit--stage copies pinned source/asset bytes into a
short fresh C project and generates the exact four-scene source-reference.json.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,re,shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
SOURCE=HERE/'prospect-refuge-supplement-corrections-source';RECORD=ROOT/'projects/shorts-leveldesign-06-02'
OWNER_REPORT=RECORD/'supplementary-corrections-preparation-v1.json';REPORT=RECORD/'supplementary-corrections-unity-staging-v1.json'
OLD_EVIDENCE=RECORD/'supplementary-native-evidence-v1.json'
FOLDER='Assets/VideoScenes/architectural-111-20261106/06-02-Supplement-corrections'
OLD_FOLDER='Assets/VideoScenes/architectural-111-20261106/06-02-Supplement'
SHADER='Assets/VideoScenes/architectural-111-20261106/ArchitecturalSurface.shader'
SOURCE_CAPTURE='c2d208c20794101504b14ba89950526a5afb8ce58c48ed2f78e5f7bdd33c2c73'
MODES=['scale','atrium','courtyard','refuge'];CONTRACT=dict(frames=720,fps=60,width=1920,height=1080,cameras=['player','observer'],modes=MODES)
ENTRY='Yamyam.Architectural111.ProspectRefugeSupplement.Corrections.Editor.CorrectionBuilder.Capture'

def load():
 path=HERE/'prepare-prospect-refuge-supplement.py';sp=importlib.util.spec_from_file_location('corrections_source_primitives',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 assert m.sha(path)=='59b611103b813f62b042d0a53e1cbcf5af18344b24c8260c1e068d05537effa2','Audit changed old source primitive first'
 return m

oldprep=load();sha=oldprep.sha;read=oldprep.read;digest=oldprep.digest;MANIFEST=oldprep.MANIFEST

def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def canonical(path):return path.replace('\\','/')

def validate_config(c):
 oldprep.base.finite_tree(c)
 assert all(type(c[k])is int and c[k]==CONTRACT[k]for k in('frames','fps','width','height'))
 assert c['sourceKind']=='our-authored-corrected-illustration'and c['sceneFolder']==FOLDER and c['sourceSceneFolder']==OLD_FOLDER
 assert [r['mode']for r in c['scenes']]==MODES
 for row in c['scenes']:
  for name in('sceneFile','sourceSceneFile'):assert re.fullmatch(r'[A-Za-z0-9_-]+\.unity',row[name]),'Canonical scene filename required'
  assert row['sceneFile']!=row['sourceSceneFile']and row['correction']and row['purpose']
 assert c['scaleVerticalFieldOfView']==38 and c['scaleCameraPosition']==dict(x=0,y=3,z=-8)and c['scaleCameraTarget']==dict(x=0,y=1.1,z=0)
 assert c['atriumPlayerPosition']==dict(x=-2.4,y=3,z=-3.4)and c['atriumLookAt']==dict(x=0,y=.8,z=1.8)
 assert {k:c[k]for k in('interiorCeilingUndersideY','interiorCeilingThickness','interiorCeilingWidth','interiorCeilingMinZ','interiorCeilingMaxZ')}==dict(interiorCeilingUndersideY=1.65,interiorCeilingThickness=.1,interiorCeilingWidth=6,interiorCeilingMinZ=-5,interiorCeilingMaxZ=-1)
 assert c['courtyardTurnStartFrame']==600 and c['courtyardTurnEndFrame']==690 and c['courtyardReobserveTarget']==dict(x=0,y=1.1,z=.5)
 return c

def preflight():
 oldprep.base.authorization();c=validate_config(read(SOURCE/'config.json'));owner=read(OWNER_REPORT)
 assert owner['topicId']=='06.02'and owner['plannedSceneCount']==4 and owner['sourceSceneFolder']==OLD_FOLDER and owner['sceneFolder']==FOLDER
 expected={'CorrectionDriver.cs','Editor/CorrectionBuilder.cs','config.json'};actual={p.relative_to(SOURCE).as_posix()for p in SOURCE.rglob('*')if p.is_file()}
 assert expected<=actual<=expected|{n+'.meta'for n in expected}
 assert {str((ROOT/r['path']).resolve().relative_to(SOURCE.resolve())).replace('\\','/')for r in owner['sourceInputs']}==expected
 for row in owner['sourceInputs']:assert sha(ROOT/row['path'])==row['sha256'],'New corrective source owner pin changed'
 compiler=owner['staticCompilerPreflight'];assert sha(compiler['path'])==compiler['sha256'];compile=read(compiler['path']);assert compile['compilerExitCode']==0
 expected_compile={str((SOURCE/'CorrectionDriver.cs').resolve()),str((SOURCE/'Editor/CorrectionBuilder.cs').resolve()),str((HERE/'prospect-refuge-supplement-source/Experiment.cs').resolve()),str((HERE/'prospect-refuge-supplement-source/Editor/EditorBuilder.cs').resolve())}
 rows=compile['sourceHashes'];assert {str((ROOT/name).resolve())for name in rows}==expected_compile
 for name,value in rows.items():assert sha(ROOT/name)==value,'Current four-source static compiler proof stale'
 original=read(OLD_EVIDENCE);assert original['captureFingerprint']==SOURCE_CAPTURE and original['fullSupplementaryCaptureComplete']is True and len(original['completedModes'])==13
 files=[];targets={};external=[];refs=[];mode_inputs={}
 def add(source,target,kind):
  source=Path(source).resolve();assert source.is_file();value=sha(source)
  if target in targets:assert targets[target]==value;return
  targets[target]=value;files.append(dict(source=str(source),target=target,sha256=value,sourceKind=kind))
 for row in original['exportedFiles']:
  relative=canonical(row['path']);assert relative.startswith('unity/VideoEditing/'+OLD_FOLDER+'/')or relative=='unity/VideoEditing/'+OLD_FOLDER+'.meta'
  source=ROOT/row['path'];assert sha(source)==row['sha256'],'Preserved original asset/export changed'
  add(source,relative[len('unity/VideoEditing/'):],'preserved-original-editable')
 for mode in MODES:
  proof=original['modes'][mode];folder=Path(proof['modeFolder']).resolve();assert folder.is_relative_to((MEDIA/'shorts-leveldesign-06-02/supplementary-native-attempts').resolve())
  assert sha(proof['proofFile']['path'])==proof['proofFile']['sha256']and sha(proof['frameHashManifest']['path'])==proof['frameHashManifest']['sha256']
  scene=proof['sceneSnapshot']['scenePath'];assert scene==OLD_FOLDER+'/'+next(r['sourceSceneFile']for r in c['scenes']if r['mode']==mode)
  scene_path=ROOT/'unity/VideoEditing'/scene;meta=Path(str(scene_path)+'.meta');assert targets[scene]==sha(scene_path)and targets[scene+'.meta']==sha(meta)
  refs.append(dict(mode=mode,sourceScenePath=scene,sourceSceneSHA256=sha(scene_path),sourceSceneMetaSHA256=sha(meta)))
  provenance=read(folder.parent.parent/'input-provenance.json');project=Path(provenance['project']).resolve()
  assert project.parent==(MEDIA/'unity-prospect-refuge-supplement-capture').resolve()and provenance['captureFingerprint']==SOURCE_CAPTURE
  record=read(folder/'scene-record.json');assert record['fingerprint']==SOURCE_CAPTURE and record['scenePaths']==[scene]
  for dependency in record['dependencies']:
   target=dependency['path'];assert target in(SHADER,SHADER+'.meta')or target.startswith('Assets/ThirdParty/KayKitAdventurers/')
   source=project/target;assert sha(source)==dependency['sha256'];add(source,target,'preserved-actual-imported-dependency')
  mode_inputs[mode]=dict(modeFolder=str(folder),states=pin(folder/'states.jsonl'),anchors=pin(folder/'projected-anchors.jsonl'),rays=pin(folder/'rays.jsonl'),sceneRecord=pin(folder/'scene-record.json'),modeProof=proof['proofFile'],frameHashManifest=proof['frameHashManifest'])
  external.extend([mode_inputs[mode][key]for key in('states','anchors','rays','sceneRecord')])
 for source in sorted(SOURCE.rglob('*')):
  if source.is_file():add(source,FOLDER+'/'+source.relative_to(SOURCE).as_posix(),'correction-owned-source')
 source_reference=dict(sourceCaptureFingerprint=SOURCE_CAPTURE,modes=refs)
 reference_bytes=(json.dumps(source_reference,ensure_ascii=False,indent=2)+'\n').encode('utf8')
 generated=[dict(target=FOLDER+'/source-reference.json',sha256=hashlib.sha256(reference_bytes).hexdigest(),contentUtf8=reference_bytes.decode('utf8'))]
 font=Path('C:/Windows/Fonts/malgun.ttf');external.append(pin(font));api=[];rsp=oldprep.API_RSP.read_text(encoding='utf-8-sig')
 for name in('UnityEngine.TextCoreFontEngineModule.dll','UnityEngine.TextCoreTextEngineModule.dll','UnityEngine.TextRenderingModule.dll'):
  module=oldprep.ENGINE_MODULES/name;assert name in rsp;api.append(pin(module))
 files.sort(key=lambda r:r['target']);assert len({r['target'].casefold()for r in files})==len(files)
 identity=dict(topicId='06.02',sourceCaptureFingerprint=SOURCE_CAPTURE,sourceFiles=files,generatedFiles=generated,externalInputs=external,engineApiModules=api,config=c,editorVersion='6000.6.0f1',projectManifest=MANIFEST,contract=CONTRACT)
 fp=digest(identity);project=MEDIA/'06-02-corr-proj'/fp[:16]
 longest=max(len(str(project/row['target']))+5 for row in files+generated);assert longest<=250,'Shorten isolated source path before Unity/Mono'
 return dict(schemaVersion='06.02-corrections-unity-staging-v1',topicId='06.02',fingerprint=fp,project=str(project),sourceCaptureFingerprint=SOURCE_CAPTURE,
  sourceReference=source_reference,sourceReferenceSHA256=generated[0]['sha256'],config=c,files=files,generatedFiles=generated,externalInputs=external,engineApiModules=api,
  sourceModes=mode_inputs,unaffectedOriginalModes={m:dict(modeFolder=original['modes'][m]['modeFolder'],modeProof=original['modes'][m]['proofFile'],frameHashManifest=original['modes'][m]['frameHashManifest'])for m in original['completedModes']if m not in MODES},
  originalEvidenceAudit=pin(OLD_EVIDENCE),sourceOwnerAudit=pin(OWNER_REPORT),staticCompilerPreflight=dict(path=compiler['path'],sha256=compiler['sha256'],compilerExitCode=0),
  captureContract=CONTRACT,captureEntry=ENTRY,editorVersion='6000.6.0f1',projectManifest=MANIFEST,maxStagedPathWithMeta=longest,preparerSHA256=sha(__file__),
  actualSceneFilesSaved=False,stageComplete=False,unityLaunched=False,voicePreparationAllowed=False,humanApproval=False,platformActions=[])

def stage(report):
 assert report['fingerprint']==preflight()['fingerprint']and report['staticCompilerPreflight']['compilerExitCode']==0
 project=Path(report['project']).resolve();assert project.parent==(MEDIA/'06-02-corr-proj').resolve()and project.name==report['fingerprint'][:16]
 rows=[]
 for row in report['files']:
  source=Path(row['source']).resolve();target=(project/row['target']).resolve();assert target.is_relative_to(project)and sha(source)==row['sha256']
  assert not target.exists()or sha(target)==row['sha256'],'Preserve changed staged corrective input';rows.append((source,target,row['sha256']))
 generated={row['target']:row['contentUtf8'].encode('utf8')for row in report['generatedFiles']}
 generated.update({'Packages/manifest.json':(json.dumps(MANIFEST,indent=2)+'\n').encode(),'ProjectSettings/ProjectVersion.txt':b'm_EditorVersion: 6000.6.0f1\n'})
 for name,data in generated.items():assert not(project/name).exists()or(project/name).read_bytes()==data,'Preserve changed generated correction input'
 for source,target,value in rows:
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copy2(source,target)
  assert sha(target)==value
 for name,data in generated.items():
  target=project/name;target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():target.write_bytes(data)
 oldprep.validate_manifest(project/'Packages/manifest.json');report['stageComplete']=True
 tmp=REPORT.with_suffix('.json.tmp');assert not tmp.exists();tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,REPORT)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',action='store_true');args=parser.parse_args()
 try:r=preflight()
 except(FileNotFoundError,KeyError,AssertionError)as error:
  if args.stage:raise
  print(json.dumps(dict(ready=False,reason=str(error),staged=False,unityLaunched=False)));return
 if args.stage:stage(r)
 print(json.dumps(dict(ready=True,fingerprint=r['fingerprint'],project=r['project'],staged=args.stage,unityLaunched=False,maxStagedPathWithMeta=r['maxStagedPathWithMeta'])))

if __name__=='__main__':main()
