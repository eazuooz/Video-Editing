"""Finite, resumable M21 captures. Never edits or terminates another project."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,time,uuid
import psutil
P=Path(__file__).resolve().parents[1];R=P.parents[1];LEASE=R/'shared/output/GPU_HANDOFF.json'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def authorized():
    c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
    assert c['productionAllowedNow'] and P.name in c['projectSlugs']
def idle_reason(own=None):
    if LEASE.exists() and read(LEASE).get('id')!=own:return 'Another scoped GPU job holds the lease'
    for p in psutil.process_iter(['pid','name','exe','cmdline']):
        i=p.info;name=(i['name'] or '').lower();exe=(i['exe'] or '').replace('\\','/').lower();args=[a.lower() for a in i['cmdline'] or []]
        if '/steamapps/common/' in exe or name in ('overwatch.exe','d2r.exe'):return 'Game process still running'
        if name=='unity.exe' and '-batchmode' in args:
            importer='-name' in args and args[args.index('-name')+1].startswith('assetimportworker')
            if not importer:return 'Other Unity batch job still running'
        if name=='unrealeditor.exe' and any(a.startswith('-moviepipeline') or a=='-renderoffscreen' for a in args):return 'Other Unreal render still running'
        if name.startswith('python') and any(k in ' '.join(args) for k in ('--synthesize','render_narration','review-source-voice.py','faster_whisper','torchrun')):return 'Other model job still running'
        if name=='ffmpeg.exe':return 'Other media encode still running'
    samples=[]
    for _ in range(3):
        v=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=CREATE)
        free,use=map(int,v.splitlines()[0].split(','));samples.append((free,use));time.sleep(.4)
    if any(f<8192 or u>35 for f,u in samples):return f'Insufficient idle headroom: {samples}'
    return None
def verify(job,folder):
    receipt=folder/'capture-success.json';video=folder/'unity.mp4'
    if not receipt.exists():return False
    d=read(receipt);assert d['compiledFingerprint']==job['expectedFingerprint'] and d['completed']==job['frames']
    ffprobe=str(Path(job['ffmpeg']).with_name('ffprobe.exe'))
    meta=json.loads(subprocess.check_output([ffprobe,'-v','error','-show_streams','-of','json',str(video)],creationflags=CREATE))
    stream=next(s for s in meta['streams'] if s['codec_type']=='video')
    assert (stream['width'],stream['height'],stream['r_frame_rate'],int(stream['nb_frames']))==(1920,1080,'60/1',job['frames'])
    save(folder/'encoded-structure.json',{'sourceFingerprint':job['expectedFingerprint'],'frames':job['frames'],'width':1920,'height':1080,'fps':'60/1','fullDecodeQa':False,'visualQa':False})
    return True
def prepare_comparison(job,queue):
    if 'comparisonDependencies' not in job:return
    records=[];lookup={read(Path(p))['sceneId']:read(Path(p)) for p in queue['jobs']}
    target=Path(job['output']).parent.parent/'comparison-frames';target.mkdir(exist_ok=True)
    for d in job['comparisonDependencies']:
        source=lookup[d['scene']];folder=Path(source['output']);assert verify(source,folder)
        image=target/(d['scene']+'.png')
        if not image.exists():subprocess.run([job['ffmpeg'],'-v','error','-ss',str(source['frames']/60*.7),'-i',str(folder/'unity.mp4'),'-frames:v','1','-n',str(image)],check=True,creationflags=CREATE)
        records.append({'imagePath':str(image),'sha256':sha(image),'label':d['label'],'sourceKind':d['sourceKind'],'crop':{'x':0,'y':0,'width':1,'height':1}})
    job['comparisonFrames']=records
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--queue',required=True);ap.add_argument('--render',action='store_true');ap.add_argument('--wait-hours',type=float,default=6);a=ap.parse_args()
    qpath=Path(a.queue).resolve();assert qpath.is_relative_to(P/'production/local')
    queue=read(qpath);assert queue['project']==P.name
    authorized();assert queue['wordAlignmentSha256']==sha(Path(queue['wordAlignment']))
    alignment=read(Path(queue['wordAlignment']));assert not alignment['flags']
    marker=Path(queue['sandbox'])/'M21_SANDBOX.json';assert read(marker)['fingerprint']==queue['fingerprint']
    if not a.render:print(json.dumps({'ready':True,'jobs':len(queue['jobs']),'modelOrRendererStarted':False}));return
    statefile=qpath.parent/'progress.json'
    if statefile.exists():
        old=read(statefile)
        try:assert abs(psutil.Process(old['pid']).create_time()-old['createTime'])>.1,'Capture queue already running'
        except psutil.NoSuchProcess:pass
    state={'pid':os.getpid(),'createTime':psutil.Process().create_time(),'status':'waiting','completed':[],'startedAt':now(),'finalReviewReady':False,'automation':False};owned=None
    try:
        for jobpath in queue['jobs']:
            authorized();job=read(Path(jobpath));folder=Path(job['output'])
            if verify(job,folder):state['completed'].append(job['id']);continue
            if folder.exists() and any(folder.iterdir()):raise RuntimeError(f'Partial prior capture preserved for inspection: {folder}')
            start=time.monotonic()
            while True:
                reason=idle_reason();state.update(status='waiting',reason=reason,checkedAt=now(),current=job['id']);save(statefile,state)
                if reason is None:break
                if time.monotonic()-start>a.wait_hours*3600:raise RuntimeError('Bounded resource wait ended')
                time.sleep(30)
            assert read(marker)['fingerprint']==queue['fingerprint']
            owned=str(uuid.uuid4())
            with LEASE.open('x',encoding='utf-8') as f:json.dump({'owner':P.name+'-capture','id':owned,'pid':os.getpid(),'createdAt':now()},f)
            prepare_comparison(job,queue);save(Path(jobpath),job)
            env=os.environ.copy();env['YAMYAM_M21_JOB']=jobpath
            p=subprocess.Popen([queue['unity'],'-batchmode','-job-worker-count','2','-projectPath',queue['sandbox'],'-executeMethod','Yamyam.GameMath.LightLab.LightLabCapture.Run','-logFile',str(qpath.parent/(job['id']+'.unity.log'))],env=env,creationflags=CREATE)
            state.update(status='capturing',unityPid=p.pid,current=job['id']);save(statefile,state)
            code=p.wait()
            if code or not verify(job,folder):raise RuntimeError('Capture failed; inspect preserved output/log before resuming')
            if LEASE.exists() and read(LEASE).get('id')==owned:LEASE.unlink()
            owned=None;state['completed'].append(job['id']);save(statefile,state)
        state.update(status='body-captures-complete-compositing-and-QA-pending',finishedAt=now());save(statefile,state)
    except BaseException as exc:state.update(status='failed-or-blocked',error=repr(exc),finishedAt=now());save(statefile,state);raise
    finally:
        if owned and LEASE.exists() and read(LEASE).get('id')==owned:LEASE.unlink()
if __name__=='__main__':main()
