"""Bounded scheduling pause of our CPU launcher; actual children keep running."""
from pathlib import Path
import datetime,hashlib,json,time
import psutil
ROOT=Path(__file__).resolve().parents[3];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');RUN=MEDIA/'production-resume-20261115T055255Z';TARGET=MEDIA/'shorts-mario64-lakitu-camera/film-v7/clean-proof.json';OUT=RUN/'finite-film-priority-observation-v3.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
 assert not OUT.exists();wp=MEDIA/'finite-lesson-completion-v9/worker.json'
 if TARGET.exists()or not wp.exists():print('No priority pause needed.',flush=True);return
 record=read(wp);p=psutil.Process(record['pid']);birth=p.create_time();assert abs(birth-record['createTime'])<.001;script=ROOT/'production/batches/original-tech-twelve-20261115/run-finite-lesson-completion-v9.py';assert Path(p.cmdline()[4]).resolve()==script and p.status()!=psutil.STATUS_STOPPED
 info=dict(startedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cpuLauncher=dict(pid=p.pid,createTime=birth,script=pin(script)),childrenPreserved=[dict(pid=c.pid,createTime=c.create_time(),name=c.name())for c in p.children(recursive=True)],actualModelOrRendererSuspended=False,foreignProcessesOrLeasesModified=False,guardOrThresholdModified=False,limitSeconds=720,newRecurringAutomation=False);paused=False
 try:
  p.suspend();paused=True;deadline=time.monotonic()+720;print('Own CPU launcher paused for a bounded final-film turn; its active child continues normally.',flush=True)
  while time.monotonic()<deadline and not TARGET.exists():
   if not psutil.pid_exists(p.pid)or abs(psutil.Process(p.pid).create_time()-birth)>.001:break
   time.sleep(10)
  info['reason']='Camera clean proof now exists'if TARGET.exists()else'Finite scheduling window ended'
 finally:
  if paused and psutil.pid_exists(p.pid)and abs(psutil.Process(p.pid).create_time()-birth)<.001:p.resume();info['ownCpuLauncherResumed']=True
  else:info['ownCpuLauncherResumed']=False
  info.update(endedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cameraCleanProof=pin(TARGET)if TARGET.exists()else None);OUT.write_text(json.dumps(info,indent=2)+'\n','utf8');print(json.dumps(dict(priorityWindowEnded=True,reason=info.get('reason'),resumed=info['ownCpuLauncherResumed'])),flush=True)
if __name__=='__main__':main()
