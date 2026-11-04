"""Prepare M23's isolated licensed-asset project; no Unity/GPU launch."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,re
S=Path(__file__).resolve().parent;R=S.parents[3];SOURCE=R/'unity/VideoEditing'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination',default='LocalUnity-v1');a=ap.parse_args()
    dest=(S/a.destination).resolve();assert dest.parent==S and dest.name.startswith('LocalUnity-') and not dest.exists()
    control=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf-8'))['explicitMathRemainingBatch20261104'];assert control['productionAllowedNow'] and 'game-math-pipeline-shaders' in control['projectSlugs']
    module=json.loads((S/'module-plan.json').read_text(encoding='utf-8'));record=json.loads((R/'projects/game-math-skinning-normal-map/production/unity-staging/module-plan.json').read_text(encoding='utf-8'))['assetRecord'];source=SOURCE/record['assetPath']
    assert sha(source)==record['verifiedSourceHash'];assert Path(SOURCE/record['licenseEvidence'].removeprefix('unity/VideoEditing/')).is_file()
    assets=SOURCE/'Assets/ThirdParty/KayKitAdventurers';files=[assets/name for name in ('Knight.fbx','Knight.fbx.meta','knight_texture.png','knight_texture.png.meta','LICENSE.txt')]
    assert all(p.is_file() for p in files)
    dest.mkdir();provenance=[]
    for src in files:
        out=dest/src.relative_to(SOURCE);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)
        if src.name=='Knight.fbx.meta':out.write_text(re.sub(r'(isReadable:\s*)0\b',r'\g<1>1',out.read_text(encoding='utf-8-sig')),encoding='utf-8')
        provenance.append({'path':out.relative_to(dest).as_posix(),'sourceSha256':sha(src),'copiedSha256':sha(out),'change':'Read/Write only in isolated FBX import' if src.name=='Knight.fbx.meta' else None})
    transport=R/'production/batches/game-math-remaining-20261104/UnityLectureCapture.cs'
    dependency=R/module['dependencies'][0]['path'];assert sha(dependency)==module['dependencies'][0]['sha256'];code=sorted([*S.glob('*.cs'),*S.glob('*.shader'),dependency]);fingerprint=hashlib.sha256(b''.join(p.name.encode()+b'\0'+p.read_bytes() for p in [*code,transport])).hexdigest()
    for src in code:
        if src.name.endswith('Checks.cs'):continue
        out=dest/'Assets/VideoScenes/game-math-pipeline-shaders'/('Editor' if src.name=='PipelineSceneBuilder.cs' else '')/src.name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)
    editor=dest/'Assets/VideoScenes/game-math-pipeline-shaders/Editor'
    shutil.copy2(transport,editor/transport.name)
    (editor/'LectureBuildVersion.cs').write_text('namespace Yamyam.RemainingMathCapture { public static class LectureBuildVersion { public const string Value="'+fingerprint+'"; } }\n',encoding='utf-8')
    (dest/'Packages').mkdir();(dest/'ProjectSettings').mkdir()
    deps={'com.unity.render-pipelines.universal':'17.6.0','com.unity.ugui':'2.6.0','com.unity.modules.animation':'1.0.0','com.unity.modules.imageconversion':'1.0.0','com.unity.modules.physics':'1.0.0','com.unity.modules.ui':'1.0.0','com.unity.modules.uielements':'1.0.0'}
    (dest/'Packages/manifest.json').write_text(json.dumps({'dependencies':deps},indent=2)+'\n',encoding='utf-8')
    shutil.copy2(SOURCE/'ProjectSettings/ProjectVersion.txt',dest/'ProjectSettings/ProjectVersion.txt')
    data={'at':datetime.now(timezone.utc).isoformat(),'fingerprint':fingerprint,'sharedProjectChanged':False,'unityStarted':False,'source':str(SOURCE),'project':str(dest),'assets':provenance,'license':record['license'],'licenseSource':record['source'],'capture':'pending actual runtime validation and 1080p60 render','font':'Local OS Malgun Gothic; font binaries not copied'}
    (dest/'M23_SANDBOX.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (dest/'MATH_CAPTURE_SANDBOX.json').write_text(json.dumps({'projectSlug':'game-math-pipeline-shaders','fingerprint':fingerprint,'transportSha256':sha(transport)},indent=2)+'\n',encoding='utf-8')
    (S/'sandbox-preparation.json').write_text(json.dumps({'status':'prepared-not-launched','sandbox':str(dest),'fingerprint':fingerprint,'manifest':str(dest/'M23_SANDBOX.json')},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sandbox':str(dest),'files':len(provenance),'startedUnity':False}))
if __name__=='__main__':main()
