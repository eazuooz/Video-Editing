"""One finite selected additions job, explicitly deferred until gaming/GPU work ends.

This is not a scheduler or recurring automation. Never interrupts applications,
changes a foreign lease, or falls back to CPU. Stops if selection changes.
"""
from pathlib import Path
import json,subprocess,time,datetime,sys
import psutil
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local/fairness-60s';status=L/'gpu-wait-job.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(v):status.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 end=time.monotonic()+8*3600;record=dict(kind='single-finite-TTS-job',project=P.name,revision='fairness-60s',pid=psutil.Process().pid,createTime=psutil.Process().create_time(),startedAt=now(),userEvidence='게임 종료 뒤 GPU로 진행',recurring=False,cpuFallback=False,foreignProcessesChanged=False)
 output=R/'shared/output/narration/shorts-forgiving-hitbox/fairness60-additions-v1/fairness60-additions-v1.wav'
 assert not output.exists(),'Preserve the generated additions; do not regenerate'
 while time.monotonic()<end:
  control=read(R/'shared/publishing/video-production-control.json')['shortsRecurringAuthorization']
  if control['selectedShort']!=P.name or control['latestSelection']['selectedRevision']!='fairness-60s':record.update(state='stopped-selection-changed',finishedAt=now());save(record);return
  games=[p.info['name'] for p in psutil.process_iter(['name']) if (p.info['name'] or '').lower()=='monsterhunterwilds.exe'];lease=(R/'shared/output/GPU_HANDOFF.json').exists()
  raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True);free=int(raw.splitlines()[0].strip())
  clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True);foreignpython=any('python' in x.lower() for x in clients.splitlines())
  record.update(state='waiting-for-game-and-GPU',lastCheckedAt=now(),gameRunning=bool(games),foreignLeaseExists=lease,freeMiB=free,foreignGpuPythonActive=foreignpython);save(record)
  if not games and not lease and not foreignpython and free>=8500:
   record.update(state='generating-additions',generationStartedAt=now());save(record)
   with (L/'tts-additions.log').open('ab') as log:
    code=subprocess.call([sys.executable,'-X','utf8',str(P/'production/render-voice-fairness60.py')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
   record.update(state='complete-additions' if code==0 else 'generation-failed',exitCode=code,finishedAt=now());save(record);print(json.dumps(record),flush=True);return
  time.sleep(30)
 record.update(state='wait-expired-without-generation',finishedAt=now());save(record);print(json.dumps(record),flush=True)
if __name__=='__main__':main()
