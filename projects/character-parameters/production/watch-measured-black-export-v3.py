"""Observe this one UI-launched FFmpeg handle and its actual Windows exit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,o):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def ident(p):return dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd())
def checkpoint(state):
 cp_path=BASE/'latest-checkpoint.json';cp=read(cp_path);cp.update(recordedAt=now(),stage=state['status'],ownedJob=dict(state=rel(EP),processIdentity=state['watcherIdentity'],child=state.get('child'),sessionId=state.get('sessionId')),nextAction='Finish this single measured black export, then verify all PTS/decode and review measured motion/cue pixels. Native/captions/mix/final QA pending.');save(cp_path,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(10):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(i for i in q['items'] if i['slug']=='character-parameters')
  item.update(stage=state['status'],currentExecution=cp['ownedJob'],nextAction=cp['nextAction']);q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);return
  time.sleep(.15)
 raise RuntimeError('Concurrent queue modification')
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
rp=ROOT/args.resource;r=read(rp);assert r['ownHeavyJobs']==0
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<180
EP=BASE/'measured-black-export-execution-v3.json';assert not EP.exists()
out=ROOT/'shared/output/character-parameters/black-structural-preview-v1/character-parameters-black-measured-v3.mp4';assert not out.exists()
state=dict(schemaVersion=3,status='waiting-for-owned-measured-black-UI-export',startedAt=now(),watcherIdentity=ident(psutil.Process()),child=None,sessionId=None,exitCode=None,
 cpuThreads=2,gpuJobs=0,resource=args.resource,resourceSha256=sha(rp),preparation=rel(BASE/'measured-mc-preparation-v3.json'),preparationSha256=sha(BASE/'measured-mc-preparation-v3.json'),output=rel(out),finalPixelsApproved=False,finalTimingApproved=False,processMutations=0)
save(EP,state);checkpoint(state)
deadline=time.time()+180
while time.time()<deadline:
 matches=[]
 for p in psutil.process_iter(['name','cmdline']):
  try:
   cmd=' '.join(p.info['cmdline'] or []).replace('\\','/').lower()
   if p.info['name']=='ffmpeg.exe' and str(out).replace('\\','/').lower() in cmd:matches.append(p)
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 if matches:
  assert len(matches)==1;child=matches[0];break
 time.sleep(.15)
else:
 state.update(status='no-owned-export-observed-preserve-state',exitCode=1,finishedAt=now());save(EP,state);checkpoint(state);raise RuntimeError('Owned FFmpeg export not observed')
state.update(status='measured-black-UI-export-running',child=ident(child));save(EP,state);checkpoint(state)
# On Windows psutil opens a process handle and waits for its exit code. This
# records the actual child exit, independently of the editor's render UI.
code=child.wait(timeout=1800)
state.update(status='measured-black-export-ended-input-review-pending' if code==0 else 'measured-black-export-failed-preserve-output',exitCode=code,finishedAt=now(),childExited=True)
if out.exists():state.update(outputSha256=sha(out),outputBytes=out.stat().st_size)
save(EP,state);checkpoint(state);print(json.dumps(dict(childExitCode=code,output=rel(out),bytes=state.get('outputBytes')),ensure_ascii=False),flush=True)
assert code==0
