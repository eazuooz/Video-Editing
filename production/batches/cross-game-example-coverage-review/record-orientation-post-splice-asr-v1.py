"""Associate actual post-splice session, then verify its observed outer closure."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,subprocess,psutil,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['register','exit'],required=True);ap.add_argument('--session',type=int,required=True);ap.add_argument('--outer-exit',type=int);ap.add_argument('--completion',required=True);a=ap.parse_args()
sp=O/'post-splice-current-voice-asr-execution-v1.json';raw=sp.read_bytes();state=read(sp);sessionp=sp.with_name(sp.stem+'.session.json');at=datetime.now(timezone.utc).isoformat()
if a.mode=='register':
 p=psutil.Process(state['pid']);assert abs(p.create_time()-state['createTime'])<.01 and p.cmdline()==state['commandLine'] and p.cwd()==state['cwd'];assert not sessionp.exists()
 p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
 cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={p.pid}" | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],text=True,encoding='utf-8',errors='replace')
 session=dict(registeredAt=at,pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),sessionId=a.session,actualInitialCompletion=a.completion,cimActual=cim,cpuThreads=2,gpuJobs=0,state=sp.relative_to(ROOT).as_posix(),log=sp.relative_to(ROOT).as_posix(),logFormat='Live structured JSON with status/results; actual outer stdout remains tool session.',next='After actual outer exit record closure then directly compare new21a whole/complete seam and07b-p06 bounded alternate decoder.')
 sessionp.write_text(json.dumps(session,ensure_ascii=False,indent=2)+'\n','utf-8')
 qp=B/'queue.json';qraw=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(ownedJob=session,activeOwnedWorkers=1,actualSession=a.session,next=session['next']);assert qp.read_bytes()==qraw;qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
else:
 if not sessionp.exists():
  assert a.session==10938 and a.outer_exit==0 and a.completion=='de2fff' and state['exitCode']==0 and state['completed']==3
  # The short CPU worker ended before attempted live registration. Bind its
  # actual outer return to the saved identity; never claim a live CIM read.
  sessionp.write_text(json.dumps(dict(pid=state['pid'],createTime=state['createTime'],commandLine=state['commandLine'],cwd=state['cwd'],sessionId=a.session,actualInitialCompletion='e0fb36',actualCompletion=a.completion,lateSessionAssociation=True,liveRegistrationSucceeded=False,failedLiveRegistration='90985f exit1,worker already closed; no controls changed',associationMethod='Actual original exec session completion plus saved execution identity and current CIM absence',state=sp.relative_to(ROOT).as_posix()),ensure_ascii=False,indent=2)+'\n','utf-8')
 session=read(sessionp);assert session['sessionId']==a.session and not psutil.pid_exists(state['pid']);assert state['exitCode']==a.outer_exit
 if a.outer_exit==0:assert state['completed']==state['total']==3
 tts=read(O/'narration-cross-game-repair-execution-v1.json');plan=read(ROOT/state['plan']);assert sha(ROOT/state['plan'])==state['planSha256']
 for x in tts['protectedInputs']+tts['results']+plan['inputs']:assert sha(ROOT/x['path'])==x['sha256']
 cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={state["pid"]}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json'],text=True,encoding='utf-8',errors='replace');assert not cim.strip()
 state.update(actualExitObserved=True,actualOuterSession=a.session,actualOuterExitCode=a.outer_exit,actualCompletion=a.completion,cimAbsence=cim,protectedAndAllCurrentPcmShaMatched=True,closedObservedAt=at);assert sp.read_bytes()==raw;sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
 cp=read(O/'latest-checkpoint.json');cp.update(activeOwnedWorkers=0,ownedJob=None,stage='post-splice-ASR-closed-directcomparison-pending',next='Read allthree fulltexts/currentword landmarks. Adopt21a only after whole/seam completeness, then measuredManim/cuttracking/currentfinalmix.');(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
 qp=B/'queue.json';qraw=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);assert qp.read_bytes()==qraw;qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(mode=a.mode,session=a.session,pid=state['pid'],createTime=state['createTime'],completion=a.completion,outerExit=a.outer_exit)))
