"""One finite follow-on: existing voice -> word alignment evidence. No next video."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,os,subprocess,time
import psutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;P=R/'projects/game-math-shading-lights';A=P/'production/local/audio-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def now():return datetime.now(timezone.utc).isoformat()
statefile=A/'finite-word-review.json'
if statefile.exists():
    old=read(statefile)
    try:assert abs(psutil.Process(old['pid']).create_time()-old['createTime'])>.1,'Same finite follow-on already active'
    except psutil.NoSuchProcess:pass
s={'pid':os.getpid(),'createTime':psutil.Process().create_time(),'status':'waiting-for-current-voice','startedAt':now(),'scope':'M21 word timestamps only','nextVideo':False,'automationCreated':False}
def save():statefile.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('guard',P/'production/run-capture-queue.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
deadline=time.monotonic()+6*3600
try:
    while True:
        G.authorized();voice=read(A/'finite-worker.json')
        if voice['status']=='failed-or-blocked':raise RuntimeError('Voice did not finish; no replacement synthesis started')
        reason='Existing narration generation is still active'
        if voice['status']=='voice-generated-review-pending':reason=G.idle_reason()
        s.update(reason=reason,checkedAt=now());save()
        if reason is None:break
        if time.monotonic()>deadline:raise RuntimeError('Bounded wait ended; other jobs preserved')
        time.sleep(20)
    s.update(status='transcribing-word-timestamps');save()
    with (A/'word-review.stdout.log').open('w',encoding='utf-8') as out,(A/'word-review.stderr.log').open('w',encoding='utf-8') as err:
        child=subprocess.Popen([str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(B/'review-source-voice.py'),'--project',P.name,'--transcribe','--device','cuda'],cwd=R,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        s['asrPid']=child.pid;save();code=child.wait()
    if code:raise RuntimeError('Word review failed; inspect preserved partial evidence')
    s.update(status='word-evidence-ready-content-review-pending',finishedAt=now());save()
except BaseException as exc:s.update(status='failed-or-blocked',error=repr(exc),finishedAt=now());save();raise
