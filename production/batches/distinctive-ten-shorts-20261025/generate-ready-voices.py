"""One finite batch, waiting for user game exit; no recurring automation or upload."""
from pathlib import Path
import datetime,json,subprocess,time,psutil,hashlib
from batch_job_lock import SerialJobLock, JobBusy, LOCK_PROTOCOL
SERIAL_JOB_LOCK_PROTOCOL = 'distinctive-ten-serial-v1'
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;L=B/'local';L.mkdir(exist_ok=True)
PY=R/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(v):
    v.update(serialProtocol=SERIAL_JOB_LOCK_PROTOCOL,pid=__import__('os').getpid(),processCreateTime=psutil.Process().create_time())
    target=L/'voice-queue-status.json';temp=target.with_suffix('.json.tmp')
    temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');temp.replace(target)
def resources():
    busy=[p.info['name'] for p in psutil.process_iter(['name']) if (p.info['name'] or '').lower() in ['monsterhunterwilds.exe','unity.exe','d2r.exe','diablo ii.exe']]
    free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(','))
    return busy,free,util
deadline=time.monotonic()+12*3600
while time.monotonic()<deadline:
    auth=read(R/'shared/publishing/video-production-control.json').get('scopedBatchAuthorizations',{}).get('explicit-ten-distinctive-shorts-20261025',{})
    if auth.get('status')!='active' or not auth.get('fullProductionAuthorized'):break
    pending=[];ready=[]
    for row in read(B/'batch.json')['projects']:
        p=R/'projects'/row['slug']
        audio=p/'production/local/audio-v1';voice=audio/'voice/narration.wav';timing=audio/'voice/narration.timing.json';levels=audio/'line-levels.json'
        if voice.exists():
            complete=timing.exists() and levels.exists() and read(levels).get('voiceSha256')==hashlib.file_digest(voice.open('rb'),'sha256').hexdigest() and read(levels).get('allRawPcmPreserved') is True
            if complete:continue
            failure=p/'production/local/voice-queue-failure.json'
            if not failure.exists():failure.write_text(json.dumps(dict(reason='Incomplete voice evidence preserved; inspect before retrying',voice=str(voice))),encoding='utf8')
        pending.append(row['slug']);plan=p/'planning/production-plan.json'
        if plan.exists() and read(plan).get('scriptFinalized') and read(plan).get('independentFootageViewed') and not (p/'production/local/voice-queue-failure.json').exists():ready.append(row['slug'])
    if not pending:write(dict(status='all-ten-voices-generated',finishedAt=datetime.datetime.now(datetime.timezone.utc).isoformat()));print('All ten voice jobs complete',flush=True);break
    busy,free,util=resources();reason='user-game-or-gpu-busy' if busy or free<4800 or util>=35 else 'waiting-for-source-script-preflight'
    write(dict(status='waiting',reason=reason,pending=pending,ready=ready,activeApps=busy,freeMiB=free,gpuPercent=util,updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    if not ready or busy or free<4800 or util>=35 or (R/'shared/output/GPU_HANDOFF.json').exists():time.sleep(30);continue
    slug=ready[0];p=R/'projects'/slug;log=p/'production/local/voice-job.log';log.parent.mkdir(parents=True,exist_ok=True)
    try:
        with SerialJobLock(slug=slug,stage='tts',wait_seconds=0):
            busy,free,util=resources()
            if busy or free<4800 or util>=35:continue
            print('VOICE_START',slug,flush=True);write(dict(status='generating',slug=slug,startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat()))
            with log.open('a',encoding='utf8') as f:result=subprocess.run([str(PY),'-X','utf8',str(p/'production/render-voice.py')],cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    except JobBusy:
        time.sleep(15);continue
    if result.returncode:(p/'production/local/voice-queue-failure.json').write_text(json.dumps(dict(exit=result.returncode,log=str(log))),encoding='utf8')
    print('VOICE_FINISHED',slug,result.returncode,flush=True)
else:write(dict(status='stopped-after-bounded-resource-wait',remaining='Inspect resource and source status before explicit resume'))
