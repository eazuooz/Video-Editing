"""Record one actual ASR session identity/exit; no worker or research control."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, os, time
import psutil
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
FOLDER=BASE/'voice-clarity-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,d):
    temp=p.with_name(p.name+'.session-writing');temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,p)
ap=argparse.ArgumentParser();ap.add_argument('--session-id',type=int,required=True);ap.add_argument('--actual-exit-code',type=int);args=ap.parse_args()
path=FOLDER/'asr-execution.json';state=read(path)
try:
    process=psutil.Process(state['pid']);same=abs(process.create_time()-state['createTime'])<.01
except psutil.NoSuchProcess: same=False
if args.actual_exit_code is None:
    assert same and state['exitCode'] is None
    assert process.cmdline()==state['commandLine'] and Path(process.cwd()).resolve()==ROOT
else:
    assert not same and state['exitCode']==args.actual_exit_code
sessionPath=FOLDER/'asr-session.json'
if sessionPath.exists():
    previous=read(sessionPath);assert previous['sessionId']==args.session_id and previous['pid']==state['pid']
session=dict(observedAt=datetime.now(timezone.utc).isoformat(),pid=state['pid'],createTime=state['createTime'],sessionId=args.session_id,
             commandLine=state['commandLine'],cwd=state['cwd'],actualExitObserved=args.actual_exit_code is not None,
             actualOuterExitCode=args.actual_exit_code,processOrControlMutations=0)
save(sessionPath,session)
state.update(sessionId=args.session_id,actualExitObserved=args.actual_exit_code is not None,actualOuterExitCode=args.actual_exit_code)
save(path,state)
cpPath=BASE/'latest-checkpoint.json';cp=read(cpPath)
assert cp['ownedJob']['pid']==state['pid']
cp['ownedJob'].update(sessionId=args.session_id,actualExitObserved=args.actual_exit_code is not None,
                      workerExpectedRunning=args.actual_exit_code is None,exitCode=args.actual_exit_code)
cp['recordedAt']=session['observedAt'];save(cpPath,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(10):
    raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='character-parameters')
    item['currentExecution']=cp['ownedJob'];q['updatedAt']=session['observedAt']
    if qp.read_text('utf-8-sig')==raw: save(qp,q);break
    time.sleep(.15)
else: raise RuntimeError('Concurrent queue write; preserve other task changes')
print(json.dumps(session,ensure_ascii=False))
