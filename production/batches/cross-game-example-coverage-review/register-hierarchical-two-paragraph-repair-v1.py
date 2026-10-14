"""Associate an actual outer session with the live process identity, no duplicate launch."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,psutil,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
ap=argparse.ArgumentParser();ap.add_argument('--session',type=int,required=True);ap.add_argument('--initial',required=True);a=ap.parse_args()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,x):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
found=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if any(x.endswith('render-hierarchical-two-paragraph-repair-v1.py') for x in p.info['cmdline'] or []):found.append(dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd()))
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
parents={psutil.Process(x['pid']).ppid() for x in found}
workers=[x for x in found if x['pid'] not in parents]
assert len(workers)==1,found
row=workers[0];row['launcherIdentities']=[x for x in found if x['pid']!=row['pid']]
row.update(sessionId=a.session,actualInitialCompletion=a.initial,status='running',startedAt=datetime.now(timezone.utc).isoformat(),cpuThreads=2,gpuJobs=1,state='projects/hierarchical-game-outlines/revision-teaching-clarity-v1/narration-two-paragraph-repair-execution-v1.json',log='projects/hierarchical-game-outlines/revision-teaching-clarity-v1/narration-two-paragraph-repair-v1.log',resource='projects/hierarchical-game-outlines/revision-teaching-clarity-v1/resource-before-two-paragraph-repair-voice-v1.json',next='Actual outer exit then owned closure/completed research preservation verification; whole2 and2independent currentPCM ASR once.')
session=O/'narration-two-paragraph-repair-session-v1.json';assert not session.exists();save(session,row)
statep=O/'narration-two-paragraph-repair-execution-v1.json'
if statep.exists():
 state=read(statep);assert state['actualPid']==row['pid'] and abs(state['createTime']-row['createTime'])<.01;state['sessionId']=a.session;save(statep,state)
cp=read(O/'latest-checkpoint.json');cp.update(ownedJob=row,activeOwnedWorkers=1,crossGameVoiceStarted=True,newTtsStarted=True,stage='single-two-candidate-voice-running');save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentHierarchicalReview'].update(stage=cp['stage'],ownedJob=row,activeOwnedWorkers=1,crossGameVoiceRequest=cp['crossGameVoiceRequest'],currentDuplicateCheckPassed=True,next=row['next']);q['updatedAt']=datetime.now(timezone.utc).isoformat();assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(row))
