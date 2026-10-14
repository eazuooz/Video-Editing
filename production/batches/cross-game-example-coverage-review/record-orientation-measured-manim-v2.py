"""Bind actual live render session and verify the observed outer closure."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,argparse,subprocess,psutil,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 temp=p.with_name(p.name+'.'+str(os.getpid())+'.writing');temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,p)
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['register','exit'],required=True);ap.add_argument('--session',type=int,required=True);ap.add_argument('--completion',required=True);ap.add_argument('--outer-exit',type=int);a=ap.parse_args()
sp=O/'measured-manim-execution-v2.json';s=read(sp);sessionp=sp.with_name(sp.stem+'.session.json');at=datetime.now(timezone.utc).isoformat()
if a.mode=='register':
 p=psutil.Process(s['pid']);assert abs(p.create_time()-s['createTime'])<.01 and p.cmdline()==s['commandLine'] and p.cwd()==s['cwd'];assert not sessionp.exists()
 p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
 cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={p.pid}" | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],text=True,encoding='utf-8',errors='replace')
 session=dict(registeredAt=at,pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),sessionId=a.session,actualInitialCompletion=a.completion,cimActual=cim,cpuThreads=2,gpuJobs=0,state=rel(sp),log='shared/output/unpublished-teaching-clarity-revision/orientation/measured-manim-v2/render-<scene>.log',next='Wait actual session closure, then verify all7 outputs/wholedecode/PTS/protectedSHA and directly read every sampled board. Silent measured scenes are not finalmixed/captionedvideo approval.')
 save(sessionp,session);s['sessionId']=a.session;save(sp,s)
else:
 session=read(sessionp);assert session['sessionId']==a.session and not psutil.pid_exists(s['pid']) and s['workerExitCode']==a.outer_exit
 if a.outer_exit==0:
  assert len(s['scenes'])==7
  for row in s['scenes']:
   assert row['renderExitCode']==row['wholeDecodeExitCode']==row['extractExitCode']==0
   for x in row['samples']+row['boards']:assert sha(ROOT/x['path'])==x['sha256']
   assert sha(ROOT/row['output'])==row['outputSha256']
 for x in read(O/'narration-cross-game-repair-execution-v1.json')['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
 cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={s["pid"]}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json'],text=True,encoding='utf-8',errors='replace');assert not cim.strip()
 s.update(actualOuterExitObserved=True,actualOuterExitCode=a.outer_exit,actualCompletion=a.completion,cimAbsence=cim,closedObservedAt=at);save(sp,s)
cp=read(O/'latest-checkpoint.json');cp.update(stage=s['status'],activeOwnedWorkers=1 if a.mode=='register' else 0,ownedJob=session if a.mode=='register' else None,measuredManimExecution=rel(sp),next=session['next']);save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=cp['activeOwnedWorkers'],ownedJob=cp['ownedJob'],measuredManimExecution=rel(sp),next=cp['next']);q['updatedAt']=at;assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(mode=a.mode,session=a.session,pid=s['pid'],createTime=s['createTime'],outerExit=a.outer_exit,completion=a.completion)))
