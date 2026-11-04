"""Provision only M24 from already verified owned source assets; no GPU launch."""
from pathlib import Path
import argparse,hashlib,json,shutil,re
P=Path(__file__).resolve().parent;R=P.parents[3];S=R/'unity/VideoEditing'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--destination',default='LocalUnity-v1');parser.add_argument('--project',default='game-math-velocity-derivatives',choices=['game-math-velocity-derivatives','game-math-acceleration-integration','game-math-circular-motion']);args=parser.parse_args()
    slug=args.project;episode={'game-math-velocity-derivatives':'M24','game-math-acceleration-integration':'M25','game-math-circular-motion':'M26'}[slug]
    targetRoot=R/'projects'/slug/'production/unity-staging';targetRoot.mkdir(parents=True,exist_ok=True)
    destination=(targetRoot/args.destination).resolve();assert destination.parent==targetRoot and destination.name.startswith('LocalUnity-') and not destination.exists()
    control=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert control['productionAllowedNow'] and slug in control['projectSlugs']
    sourcePrep=read(R/'projects/game-math-shading-lights/production/unity-staging/sandbox-preparation.json');prior=read(Path(sourcePrep['sandbox'])/'M21_SANDBOX.json')
    records=prior['ownedAssets']
    # This vendor material contains an old HDRP material-version subasset.
    # Its live Material uses the separately resolved URP Lit shader. Preserve
    # the original payload and explicitly record the unused editor reference.
    assert set(prior['unresolvedGuids'])<={'da692e001514ec24dbc4cca1949ff7e8'}
    for rec in records:
        if not rec['path'].endswith('.mat'):continue
        text=(S/rec['path']).read_text(encoding='utf-8-sig')
        for part in re.split(r'(?=--- !u!)',text):
            if 'da692e001514ec24dbc4cca1949ff7e8' in part:assert part.startswith('--- !u!114') and 'hdPluginSubTargetMaterialVersions' in part
        assert 'm_Shader: {fileID: 4800000, guid: 933532a4fcc9baf4fa0491de14d08ed7' in text
    for rec in records:
        src=(S/rec['path']).resolve();assert src.is_relative_to(S) and sha(src)==rec['sourceSha256']
    destination.mkdir()
    for rec in records:
        src=S/rec['path'];out=destination/rec['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)
    upstream=R/'production/batches/game-math-remaining-20261104/UnityLectureCapture.cs'
    transport=upstream.read_text(encoding='utf-8')
    before='string factory=job.projectSlug=="game-math-skinning-normal-map"?"SkinNormalSceneBuilder":job.projectSlug=="game-math-pipeline-shaders"?"PipelineSceneBuilder":null;'
    assert transport.count(before)==1
    transport=transport.replace(before,'string factory=job.projectSlug=="'+slug+'"?"MotionSceneBuilder":null;').replace('^m(22|23)-[a-z0-9-]+$', '^'+episode.lower()+'-[a-z0-9-]+$').replace('Yamyam.RemainingMathCapture','Yamyam.MotionMathCapture')
    sources=[p for p in sorted(P.glob('*.cs')) if not p.name.endswith('Checks.cs')]
    payloads={p.name:p.read_bytes() for p in sources}
    payloads['MotionSceneBuilder.cs']=payloads['MotionSceneBuilder.cs'].decode('utf-8-sig').replace('game-math-velocity-derivatives',slug).replace('M24',episode).encode('utf-8')
    fingerprint=hashlib.sha256(b''.join(name.encode()+b'\0'+data for name,data in payloads.items())+transport.encode()).hexdigest()
    root=destination/('Assets/VideoScenes/'+slug);editor=root/'Editor';editor.mkdir(parents=True)
    for name,data in payloads.items():((editor if name.endswith('SceneBuilder.cs') else root)/name).write_bytes(data)
    (editor/'UnityLectureCapture.cs').write_text(transport,encoding='utf-8')
    (editor/'LectureBuildVersion.cs').write_text('namespace Yamyam.MotionMathCapture { public static class LectureBuildVersion { public const string Value="'+fingerprint+'"; } }\n',encoding='utf-8')
    write(destination/'Packages/manifest.json',{'dependencies':{'com.unity.render-pipelines.universal':'17.6.0','com.unity.ugui':'2.6.0','com.unity.modules.imageconversion':'1.0.0','com.unity.modules.physics':'1.0.0','com.unity.modules.ui':'1.0.0','com.unity.modules.uielements':'1.0.0'}})
    (destination/'ProjectSettings').mkdir();shutil.copy2(S/'ProjectSettings/ProjectVersion.txt',destination/'ProjectSettings/ProjectVersion.txt')
    write(destination/'MATH_CAPTURE_SANDBOX.json',{'projectSlug':slug,'fingerprint':fingerprint,'assets':records,'sharedProjectChanged':False,'transportSourceSha256':sha(upstream),'transportModification':'Exact scoped '+episode+' factory/ID/namespace substitution only','sourceReuse':str(P),'unusedEditorReference':{'guid':'da692e001514ec24dbc4cca1949ff7e8','evidence':'Only hidden MonoBehaviour version13/hdPluginSubTargetMaterialVersions subasset; actual shader GUID is resolved URP Lit','runtimeMaterialQa':'pending'},'font':'OS Malgun Gothic; no font binary copied'})
    write(targetRoot/'sandbox-preparation.json',{'sandbox':str(destination),'fingerprint':fingerprint,'status':'prepared-not-launched','unityStarted':False})
    print(episode,'isolated sources prepared; no Unity process started.')
if __name__=='__main__':main()
