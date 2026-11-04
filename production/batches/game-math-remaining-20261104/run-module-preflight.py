"""Run one explicitly prepared M22/M23 preview queue, preserving other jobs."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, os, subprocess, time, uuid
import psutil

R=Path(__file__).resolve().parents[3]
LEASE=R/'shared/output/GPU_HANDOFF.json'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
spec=importlib.util.spec_from_file_location('idle_guard',R/'projects/game-math-shading-lights/production/run-capture-queue.py')
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--queue',required=True);ap.add_argument('--run',action='store_true');ap.add_argument('--wait-hours',type=float,default=6);a=ap.parse_args()
    qpath=Path(a.queue).resolve();q=read(qpath);slug=q['project']
    assert slug in {'game-math-skinning-normal-map','game-math-pipeline-shaders','game-math-velocity-derivatives','game-math-acceleration-integration','game-math-circular-motion','game-math-forces-friction'}
    project=R/'projects'/slug;assert qpath.is_relative_to(project/'production/unity-staging')
    sandbox=Path(q['sandbox']);marker=sandbox/'MATH_CAPTURE_SANDBOX.json'
    def authorized():
        c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
        assert c['productionAllowedNow'] and slug in c['projectSlugs']
        assert read(marker)['fingerprint']==q['fingerprint']
    authorized()
    for jp in q['jobs']:
        job=read(Path(jp));assert job['command']=='preflight' and job['projectSlug']==slug
        assert job['expectedFingerprint']==q['fingerprint'] and not job['speechTimingVerified']
    if not a.run:print(json.dumps({'ready':True,'jobs':len(q['jobs']),'rendererStarted':False}));return
    statefile=qpath.parent/'progress.json'
    if statefile.exists():
        old=read(statefile)
        try:assert abs(psutil.Process(old['pid']).create_time()-old['createTime'])>.1,'Same queue already active'
        except psutil.NoSuchProcess:pass
        assert old['status']!='images-ready-for-internal-visual-QA','Unchanged completed queue must not be repeated'
    state={'pid':os.getpid(),'createTime':psutil.Process().create_time(),'status':'waiting','startedAt':now(),'completed':[], 'finalVideo':False,'humanReview':False,'automation':False}
    owned=None
    def wait_idle():
        start=time.monotonic();stable=0
        while True:
            authorized();reason=G.idle_reason();stable=stable+1 if reason is None else 0
            state.update(status='waiting',reason=reason,checkedAt=now());save(statefile,state)
            if stable>=3:return
            if time.monotonic()-start>a.wait_hours*3600:raise RuntimeError('Bounded resource wait ended; other jobs preserved')
            time.sleep(5)
    def acquire():
        nonlocal owned
        deadline=time.monotonic()+a.wait_hours*3600
        while True:
            wait_idle();candidate=str(uuid.uuid4())
            try:
                with LEASE.open('x',encoding='utf-8') as f:json.dump({'owner':slug+'-preflight','id':candidate,'pid':os.getpid(),'createdAt':now()},f)
            except FileExistsError:
                if time.monotonic()>deadline:raise RuntimeError('Bounded resource wait ended; other jobs preserved')
                continue
            owned=candidate;return
    def release():
        nonlocal owned
        G.release_lease(owned)
        owned=None
    def run_unity(method,log,env=None,quit_after=False):
        command=[q['unity'],'-batchmode','-job-worker-count','2','-projectPath',str(sandbox),'-executeMethod',method,'-logFile',str(log)]
        if quit_after:command.append('-quit')
        child=subprocess.Popen(command,env=env,creationflags=CREATE)
        state.update(status='running-preflight',unityPid=child.pid);save(statefile,state)
        if child.wait():raise RuntimeError('Owned Unity job failed; preserved output and log need review')
    try:
        if q['rigValidationRequired']:
            evidence=sandbox/'rig-runtime-validation.json';receipt=qpath.parent/'rig-validation-receipt.json'
            if receipt.exists():
                d=read(receipt);assert d['fingerprint']==q['fingerprint'] and d['evidenceSha256']==sha(evidence)
            else:
                assert not evidence.exists(),'Existing unreceipted rig evidence needs inspection'
                state['current']='actual-rig-validation';acquire()
                run_unity('SkinNormalSceneBuilder.ValidateRigOnly',qpath.parent/'rig-validation.unity.log',quit_after=True)
                result=read(evidence);assert result['status']=='cpu-rig-validated-not-rendered' and len(result['probes'])==15
                assert all(p['cpuVsBakeWorldError']<=.0005 for p in result['probes'])
                save(receipt,{'fingerprint':q['fingerprint'],'evidence':str(evidence),'evidenceSha256':sha(evidence),'checkedAt':now(),'runtimeSkinningChecks':15,'visualQa':False});release()
        from PIL import Image
        for jp in q['jobs']:
            authorized();job=read(Path(jp));folder=Path(job['output']);success=folder/'capture-success.json'
            if success.exists():
                done=read(success);assert done['fingerprint']==q['fingerprint'] and done['completed']==len(job['sampleFrames'])
            else:
                assert not folder.exists() or not any(folder.iterdir()),'Prior partial preview preserved; inspect before resuming'
                state['current']=job['id'];acquire()
                env=os.environ.copy();env['YAMYAM_MATH_CAPTURE_JOB']=str(jp)
                entry='Yamyam.MotionMathCapture.UnityLectureCapture.Run' if slug in {'game-math-velocity-derivatives','game-math-acceleration-integration','game-math-circular-motion'} else 'Yamyam.RemainingMathCapture.UnityLectureCapture.Run'
                if slug=='game-math-forces-friction':entry='Yamyam.MechanicsCapture.UnityLectureCapture.Run'
                run_unity(entry,qpath.parent/(job['id']+'.unity.log'),env)
                done=read(success);assert done['fingerprint']==q['fingerprint'] and done['completed']==len(job['sampleFrames'])
                release()
            frames=[]
            for f in job['sampleFrames']:
                image=folder/f'frame-{f:06}.png'
                with Image.open(image) as im:assert im.size==(1920,1080)
                frames.append({'path':str(image),'sha256':sha(image)})
            assert (sandbox/done['scene']).exists()
            save(folder/'structural-check.json',{'fingerprint':q['fingerprint'],'frames':frames,'scene':done['scene'],'visualQa':False,'humanReview':False})
            state['completed'].append(job['id']);save(statefile,state)
        state.update(status='images-ready-for-internal-visual-QA',finishedAt=now(),reason=None);save(statefile,state)
    except BaseException as exc:
        state.update(status='failed-or-blocked',error=repr(exc),finishedAt=now());save(statefile,state);raise
    finally:release()
if __name__=='__main__':main()
