"""Bind an observed exec session; close only after its actual outer exit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--state',required=True);a.add_argument('--session',required=True);a.add_argument('--session-id',type=int,required=True);a.add_argument('--outer-exit-code',type=int);v=a.parse_args()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sp=ROOT/v.state;session=ROOT/v.session;s=read(sp);stamp=datetime.now(timezone.utc).isoformat()
row=dict(sessionId=v.session_id,pid=s['pid'],createTime=s['createTime'],command=s['command'],cwd=s['cwd'],observedAt=stamp)
if v.outer_exit_code is None:
 p=psutil.Process(s['pid']);assert abs(p.create_time()-s['createTime'])<.01 and p.cmdline()==s['command']
 row['actualIdentityVerified']=True
else:
 assert s['exitCode']==v.outer_exit_code
 if psutil.pid_exists(s['pid']):assert abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01,'Original worker still alive'
 row.update(outerExitCode=v.outer_exit_code,outerExitDirectlyObserved=True,sessionClosed=True)
 s.update(sessionId=v.session_id,outerExitCode=v.outer_exit_code,outerExitDirectlyObserved=True,sessionClosed=True,outerExitObservedAt=stamp)
 sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n','utf-8')
 cp=read(BASE/'latest-checkpoint.json')
 if cp.get('ownedJob',{}).get('pid')==s['pid']:
  cp['ownedJob'].update(sessionId=v.session_id,exitCode=v.outer_exit_code,outerExitDirectlyObserved=True,sessionClosed=True,workerExpectedRunning=False);cp['recordedAt']=stamp
  (BASE/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items']if x['slug']=='character-parameters')
 for key in ['currentExecution','currentJob','ownedJob']:
  if i.get(key,{}).get('pid')==s['pid']:i[key].update(sessionId=v.session_id,exitCode=v.outer_exit_code,outerExitDirectlyObserved=True,sessionClosed=True,workerExpectedRunning=False)
 q['updatedAt']=stamp;qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
session.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(row))
