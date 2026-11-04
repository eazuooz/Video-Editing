"""Provision the five source-matched licensed props in an isolated M27 project."""
from pathlib import Path
import argparse,hashlib,json,re,shutil
S=Path(__file__).resolve().parent;R=S.parents[3];U=R/'unity/VideoEditing'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--destination',required=True);args=ap.parse_args();dest=(S/args.destination).resolve();assert dest.parent==S and dest.name.startswith('LocalUnity-') and not dest.exists()
 control=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert control['productionAllowedNow'] and 'game-math-forces-friction' in control['projectSlugs']
 roots=[U/'Assets/ThirdParty/YamyamAssetLibrary'/name for name in ['002-analog-memory-80s-90s-crt-vhs-rooms-godot-unity-blend','004-viking-world-stylized-environment']]
 names={'robot':'EAThe80_Robot_Toy_01a_PRE.prefab','box':'EAThe80_Prop_Cardbox_01a_PRE.prefab','book':'EAThe80_Prop_Book_01a_PRE.prefab','sandwich':'EAThe80_Prop_BreadJam_01a_PRE.prefab','pot':'FlowerPot_1.prefab'}
 pattern=re.compile(r'guid:\s*([0-9a-f]{32})');index={};selected=set();pending=[];assets=[]
 for root in roots:
  for meta in root.rglob('*.meta'):
   match=pattern.search(meta.read_text(encoding='utf-8-sig',errors='ignore'))
   if match:index[match[1]]=Path(str(meta)[:-5])
 for role,name in names.items():
  paths=[p for root in roots for p in root.rglob(name)];assert len(paths)==1,(role,paths);p=paths[0];pending.append(p)
  assets.append(dict(role=role,assetPath=p.relative_to(U).as_posix(),guid=pattern.search(Path(str(p)+'.meta').read_text(encoding='utf-8-sig'))[1],sourceSha256=sha(p),productId='004' if role=='pot' else '002',runtimeInspected=False,rigUsed=False))
 unresolved=set()
 while pending:
  p=pending.pop()
  if p in selected:continue
  assert p.is_file();selected.add(p);data=Path(str(p)+'.meta').read_bytes()
  if p.suffix in {'.prefab','.mat','.asset','.controller','.anim'}:data+=p.read_bytes()
  for guid in pattern.findall(data.decode('utf-8',errors='ignore')):
   if guid in index:pending.append(index[guid])
   elif not guid.startswith('0000000000000000'):unresolved.add(guid)
 dest.mkdir();records=[]
 for p in sorted(selected):
  for src in [p,Path(str(p)+'.meta')]:
   out=dest/src.relative_to(U);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out);records.append(dict(path=out.relative_to(dest).as_posix(),sha256=sha(src),bytes=src.stat().st_size))
 upstream=R/'production/batches/game-math-remaining-20261104/UnityLectureCapture.cs';transport=upstream.read_text(encoding='utf-8')
 before='string factory=job.projectSlug=="game-math-skinning-normal-map"?"SkinNormalSceneBuilder":job.projectSlug=="game-math-pipeline-shaders"?"PipelineSceneBuilder":null;';assert transport.count(before)==1
 transport=transport.replace(before,'string factory=job.projectSlug=="game-math-forces-friction"?"MechanicsSceneBuilder":null;').replace('^m(22|23)-[a-z0-9-]+$','^m27-[a-z0-9-]+$').replace('Yamyam.RemainingMathCapture','Yamyam.MechanicsCapture')
 files=[p for p in sorted(S.glob('Mechanics*.cs')) if not p.name.endswith('Checks.cs')];fp=hashlib.sha256(b''.join(p.name.encode()+b'\0'+p.read_bytes() for p in files)+transport.encode()).hexdigest()
 code=dest/'Assets/VideoScenes/game-math-forces-friction';editor=code/'Editor';editor.mkdir(parents=True)
 for p in files:shutil.copy2(p,(editor if p.name.endswith('SceneBuilder.cs') else code)/p.name)
 (editor/'UnityLectureCapture.cs').write_text(transport,encoding='utf-8');(editor/'LectureBuildVersion.cs').write_text('namespace Yamyam.MechanicsCapture {public static class LectureBuildVersion {public const string Value="'+fp+'";}}',encoding='utf-8')
 save(dest/'Packages/manifest.json',{'dependencies':{'com.unity.render-pipelines.universal':'17.6.0','com.unity.ugui':'2.6.0','com.unity.modules.imageconversion':'1.0.0','com.unity.modules.physics':'1.0.0','com.unity.modules.ui':'1.0.0','com.unity.modules.uielements':'1.0.0'}})
 (dest/'ProjectSettings').mkdir();shutil.copy2(U/'ProjectSettings/ProjectVersion.txt',dest/'ProjectSettings/ProjectVersion.txt')
 save(dest/'MATH_CAPTURE_SANDBOX.json',dict(projectSlug='game-math-forces-friction',fingerprint=fp,assets=records,unresolvedGuids=sorted(unresolved),runtimeQa=False,sharedProjectChanged=False,transportSourceSha256=sha(upstream)))
 save(S/'sandbox-preparation.json',dict(sandbox=str(dest),fingerprint=fp,rendererStarted=False))
 prior=read(R/'projects/game-math-shading-lights/planning/unity-plan.json')['assetRecords'][0]
 for asset in assets:
  asset.update(source=prior['source'] if asset['productId']=='002' else 'https://rg-poly.itch.io/viking-world-stylized-environment',license=prior['license'] if asset['productId']=='002' else 'Publisher current page explicitly says CC0 licensed; personal and commercial use, no attribution required.',licenseEvidence='M21 verified publisher license record reused' if asset['productId']=='002' else 'Publisher page License line95 directly read 2026-11-05 KST',limits='Import and actual appearance pending; vendor originals unchanged. Bread-with-jam prop is a food stand-in in an explicitly illustrative free-fall example.' if asset['role']=='sandwich' else 'Static prop motion; no character rig or actual game measurement claimed.')
 save(S.parents[1]/'planning/unity-plan.json',dict(project='game-math-forces-friction',renderer='Unity',editor='6000.6.0f1',pipeline='URP17.6.0',sourceKind='Our analytic mechanics implementation',assetRecords=assets,sharedAssetPaths=[a['assetPath'] for a in assets],sceneConfigurations=str(S/'force-shots.json'),sandbox=str(dest),capture=dict(width=1920,height=1080,fps=60),runtimeQa=False,sceneSaved=False))
 print(json.dumps(dict(prepared=True,files=len(records),bytes=sum(x['bytes'] for x in records),unresolvedGuids=sorted(unresolved))))
if __name__=='__main__':main()
