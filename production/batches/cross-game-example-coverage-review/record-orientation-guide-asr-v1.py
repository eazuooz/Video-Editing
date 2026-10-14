"""Bind actual live CPU session or verify its actual closed exit and protected bytes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['candidate','spliced'],required=True);ap.add_argument('--action',choices=['register','exit'],required=True);ap.add_argument('--session',type=int,required=True);ap.add_argument('--completion',required=True);ap.add_argument('--outer-exit',type=int);a=ap.parse_args()
sp=O/f'guide-{a.mode}-voice-asr-execution-v1.json';s=read(sp);sess=sp.with_name(sp.stem+'.session.json');at=datetime.now(timezone.utc).isoformat()
if a.action=='register':
 p=psutil.Process(s['pid']);assert abs(p.create_time()-s['createTime'])<.01 and p.cmdline()==s['commandLine'] and p.cwd()==s['cwd'];assert not sess.exists()
 cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={p.pid}" | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json'],text=True,encoding='utf-8',errors='replace')
 save(sess,dict(registeredAt=at,pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),sessionId=a.session,actualInitialCompletion=a.completion,cimActual=cim,cpuThreads=2,gpuJobs=0,state=rel(sp)));s['sessionId']=a.session;save(sp,s)
else:
 session=read(sess);assert session['sessionId']==a.session and not psutil.pid_exists(s['pid']) and s['exitCode']==a.outer_exit
 if a.outer_exit==0:assert s['completed']==s['total']
 plan=read(ROOT/s['plan']);tts=read(O/'narration-07b-guide-repair-execution-v1.json')
 for x in tts['protectedInputs']+tts['results']+plan['inputs']:assert sha(ROOT/x['path'])==x['sha256']
 cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={s["pid"]}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json'],text=True,encoding='utf-8',errors='replace');assert not cim.strip()
 s.update(actualOuterSession=a.session,actualOuterExitCode=a.outer_exit,actualCompletion=a.completion,actualExitObserved=True,cimAbsence=cim,protectedAndCurrentPcmShaMatched=True,closedObservedAt=at);save(sp,s)
 cp=read(O/'latest-checkpoint.json');cp.update(stage=s['status'],activeOwnedWorkers=0,ownedJob=None);save(O/'latest-checkpoint.json',cp)
 qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=s['status'],activeOwnedWorkers=0,ownedJob=None);q['updatedAt']=at;assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(action=a.action,mode=a.mode,session=a.session,pid=s['pid'],createTime=s['createTime'],outerExit=a.outer_exit,completion=a.completion)))
