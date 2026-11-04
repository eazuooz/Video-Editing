"""Create a fresh isolated curve runtime; no costly job is launched here."""
from pathlib import Path
import argparse,hashlib,json,shutil
S=Path(__file__).resolve().parent;R=S.parents[3];U=R/'unity/VideoEditing'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True,choices=['game-math-parametric-hermite','game-math-bezier-subdivision','game-math-splines-continuity']);ap.add_argument('--destination',required=True);a=ap.parse_args();slug=a.project
 T=R/'projects'/slug/'production/unity-staging';dest=(T/a.destination).resolve();assert dest.parent==T and dest.name.startswith('LocalUnity-') and not dest.exists()
 c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow'] and slug in c['projectSlugs']
 episode={'game-math-parametric-hermite':31,'game-math-bezier-subdivision':32,'game-math-splines-continuity':33}[slug]
 upstream=R/'production/batches/game-math-remaining-20261104/UnityLectureCapture.cs';transport=upstream.read_text(encoding='utf-8');before='string factory=job.projectSlug=="game-math-skinning-normal-map"?"SkinNormalSceneBuilder":job.projectSlug=="game-math-pipeline-shaders"?"PipelineSceneBuilder":null;';assert transport.count(before)==1
 transport=transport.replace(before,'string factory=job.projectSlug=="'+slug+'"?"CurveSceneBuilder":null;').replace('^m(22|23)-[a-z0-9-]+$',f'^m{episode}-[a-z0-9-]+$').replace('Yamyam.RemainingMathCapture','Yamyam.CurveCapture')
 files=[p for p in sorted(S.glob('Curve*.cs')) if not p.name.endswith('Checks.cs')];fp=hashlib.sha256(b''.join(p.name.encode()+b'\0'+p.read_bytes() for p in files)+transport.encode()).hexdigest()
 code=dest/'Assets/VideoScenes'/slug;editor=code/'Editor';editor.mkdir(parents=True)
 for p in files:shutil.copy2(p,(editor if p.name.endswith('SceneBuilder.cs') else code)/p.name)
 (editor/'UnityLectureCapture.cs').write_text(transport,encoding='utf-8');(editor/'LectureBuildVersion.cs').write_text('namespace Yamyam.CurveCapture {public static class LectureBuildVersion {public const string Value="'+fp+'";}}',encoding='utf-8')
 save(dest/'Packages/manifest.json',{'dependencies':{'com.unity.render-pipelines.universal':'17.6.0','com.unity.ugui':'2.6.0','com.unity.modules.imageconversion':'1.0.0','com.unity.modules.physics':'1.0.0','com.unity.modules.ui':'1.0.0','com.unity.modules.uielements':'1.0.0'}})
 (dest/'ProjectSettings').mkdir();shutil.copy2(U/'ProjectSettings/ProjectVersion.txt',dest/'ProjectSettings/ProjectVersion.txt')
 save(dest/'MATH_CAPTURE_SANDBOX.json',dict(projectSlug=slug,fingerprint=fp,assets=[],runtimeQa=False,sharedProjectChanged=False,transportSourceSha256=hashlib.sha256(upstream.read_bytes()).hexdigest()))
 save(T/'sandbox-preparation.json',dict(sandbox=str(dest),fingerprint=fp,rendererStarted=False))
 save(T.parents[1]/'planning/unity-plan.json',dict(project=slug,renderer='Unity',editor='6000.6.0f1',pipeline='URP17.6.0',sourceKind='Our analytic curve implementation',assetRecords=[],sharedAssetPaths=[],assetChoice='Curves, control polygons and derivatives are the narrated objects themselves; self-authored mathematical geometry. No decorative imported character is needed.',sceneConfigurations=str(T/'curve-shots.json'),sharedSource=str(S),sandbox=str(dest),capture=dict(width=1920,height=1080,fps=60),runtimeQa=False,sceneSaved=False))
 print(json.dumps(dict(project=slug,fingerprint=fp,sandbox=str(dest))))
if __name__=='__main__':main()
