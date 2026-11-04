"""Synchronize only our stopped, isolated M22/M23 sources before first import."""
from pathlib import Path
import hashlib,json,shutil
import psutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for slug in ['game-math-skinning-normal-map','game-math-pipeline-shaders']:
    S=R/'projects'/slug/'production/unity-staging';record=read(S/'sandbox-preparation.json');dest=Path(record['sandbox']).resolve()
    assert dest.parent==S and dest.name.startswith('LocalUnity-')
    for proc in psutil.process_iter(['name','cmdline']):
        if (proc.info['name'] or '').lower()!='unity.exe':continue
        args=proc.info['cmdline'] or [];low=[x.lower() for x in args]
        if '-projectpath' in low:assert Path(args[low.index('-projectpath')+1]).resolve()!=dest,'Owned isolated editor still running; preserve it'
    code=sorted([*S.glob('*.cs'),*S.glob('*.shader')]);plan=read(S/'module-plan.json')
    if slug=='game-math-pipeline-shaders':
        dep=R/plan['dependencies'][0]['path'];assert hashlib.sha256(dep.read_bytes()).hexdigest()==plan['dependencies'][0]['sha256'];code=sorted([*code,dep])
    transport=B/'UnityLectureCapture.cs';fingerprint=hashlib.sha256(b''.join(p.name.encode()+b'\0'+p.read_bytes() for p in [*code,transport])).hexdigest()
    if record['fingerprint']==fingerprint:continue
    root=dest/'Assets/VideoScenes'/slug;archive=S/'local-source-history'/record['fingerprint'];archive.mkdir(parents=True,exist_ok=True)
    for p in root.rglob('*'):
        if p.is_file() and p.suffix in {'.cs','.shader'}:
            out=archive/p.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True)
            if not out.exists():shutil.copy2(p,out)
    for src in code:
        if src.name.endswith('Checks.cs'):continue
        out=root/('Editor' if src.name.endswith('SceneBuilder.cs') else '')/src.name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)
    shutil.copy2(transport,root/'Editor/UnityLectureCapture.cs')
    (root/'Editor/LectureBuildVersion.cs').write_text('namespace Yamyam.RemainingMathCapture { public static class LectureBuildVersion { public const string Value="'+fingerprint+'"; } }\n',encoding='utf-8')
    marker=read(dest/'MATH_CAPTURE_SANDBOX.json');marker.update(fingerprint=fingerprint,transportSha256=hashlib.sha256(transport.read_bytes()).hexdigest());save(dest/'MATH_CAPTURE_SANDBOX.json',marker)
    record.update(fingerprint=fingerprint,status='sources-prepared-not-launched');save(S/'sandbox-preparation.json',record)
    W=S/'local-preflight-v1';assert not (W/'progress.json').exists(),'Do not retarget a started preview'
    queue=read(W/'queue.json');queue['fingerprint']=fingerprint;save(W/'queue.json',queue)
    for jp in queue['jobs']:p=Path(jp);job=read(p);job['expectedFingerprint']=fingerprint;save(p,job)
    print(slug,'source synchronized; no Unity started')
