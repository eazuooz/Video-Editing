"""One finite follow-on: existing voice -> word alignment evidence. No next video."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,os,subprocess,time,uuid,shutil,argparse
import psutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--audio-revision',default='audio-v1');ap.add_argument('--reuse-from');ap.add_argument('--wait-hours',type=float,default=6);args=ap.parse_args()
c=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow'] and args.project in c['projectSlugs']
assert __import__('re').fullmatch(r'audio-v\d+',args.audio_revision)
P=R/'projects'/args.project;A=P/'production/local'/args.audio_revision
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def now():return datetime.now(timezone.utc).isoformat()
statefile=A/'finite-word-review.json';lease=R/'shared/output/GPU_HANDOFF.json';owned=None
if statefile.exists():
    old=read(statefile)
    if old.get('status')=='word-evidence-ready-content-review-pending':
        print('Existing word-alignment evidence preserved; no repeated transcription.');raise SystemExit(0)
    try:assert abs(psutil.Process(old['pid']).create_time()-old['createTime'])>.1,'Same finite follow-on already active'
    except psutil.NoSuchProcess:pass
    archive=A/'review-attempts';archive.mkdir(exist_ok=True)
    attempt=archive/f'attempt-{len(list(archive.iterdir()))+1:02}';attempt.mkdir()
    for name in ('finite-word-review.json','word-review.stdout.log','word-review.stderr.log'):
        p=A/name
        if p.exists():shutil.copy2(p,attempt/name)
s={'pid':os.getpid(),'createTime':psutil.Process().create_time(),'status':'waiting-for-current-voice','startedAt':now(),'scope':args.project+' word timestamps only','nextVideo':False,'automationCreated':False}
def save():statefile.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('guard',R/'projects/game-math-shading-lights/production/run-capture-queue.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
deadline=time.monotonic()+args.wait_hours*3600
try:
    while True:
        c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow'] and args.project in c['projectSlugs'];voice=read(A/'finite-worker.json')
        if voice['status']=='failed-or-blocked':raise RuntimeError('Voice did not finish; no replacement synthesis started')
        reason='Existing narration generation is still active'
        if voice['status']=='voice-generated-review-pending':
            if args.reuse_from and not (A/'review/reused-pcm-evidence.json').exists():
                assert __import__('re').fullmatch(r'audio-v\d+',args.reuse_from) and args.reuse_from!=args.audio_revision
                subprocess.run([str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(B/'reuse-unchanged-word-evidence.py'),'--project',P.name,'--source',args.reuse_from,'--target',args.audio_revision],cwd=R,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            reason=G.idle_reason()
        s.update(reason=reason,checkedAt=now());save()
        if reason is None:
            free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])
            if free<9216:reason='Word alignment needs 9 GiB idle memory';s.update(reason=reason);save()
            else:
                # Reserve before child imports/loads the long WAV. Another waiting
                # production job may become ready in the same second.
                candidate=str(uuid.uuid4())
                try:
                    with lease.open('x',encoding='utf-8') as f:json.dump({'owner':P.name+'-word-review','id':candidate,'pid':os.getpid(),'createdAt':now()},f)
                except FileExistsError:reason='Another job acquired the shared resource first'
                else:owned=candidate;break
        if time.monotonic()>deadline:raise RuntimeError('Bounded wait ended; other jobs preserved')
        time.sleep(20)
    s.update(status='transcribing-word-timestamps');save()
    with (A/'word-review.stdout.log').open('w',encoding='utf-8') as out,(A/'word-review.stderr.log').open('w',encoding='utf-8') as err:
        child=subprocess.Popen([str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(B/'review-source-voice.py'),'--project',P.name,'--audio-revision',args.audio_revision,'--transcribe','--device','cuda','--lease-id',owned],cwd=R,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        s['asrPid']=child.pid;save();code=child.wait()
    if code:raise RuntimeError('Word review failed; inspect preserved partial evidence')
    s.update(status='word-evidence-ready-content-review-pending',finishedAt=now());save()
except BaseException as exc:s.update(status='failed-or-blocked',error=repr(exc),finishedAt=now());save();raise
finally:
    G.release_lease(owned)
