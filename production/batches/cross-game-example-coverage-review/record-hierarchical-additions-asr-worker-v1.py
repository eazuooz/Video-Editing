"""Bind or close a real outer ASR session; never launch a second recognizer."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
B=ROOT/'production/batches/cross-game-example-coverage-review'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(8*1024*1024),b''):h.update(c)
 return h.hexdigest()
def save(p,x):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(t,p)
def live(x):
 try:return abs(psutil.Process(x['pid']).create_time()-x['createTime'])<.01
 except psutil.NoSuchProcess:return False
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['whole','contexts'],required=True)
ap.add_argument('--action',choices=['register','closed'],required=True);ap.add_argument('--session',type=int,required=True)
ap.add_argument('--chunk',required=True);ap.add_argument('--outer-exit',type=int);a=ap.parse_args()
state_path=V/f'additions-{a.mode}-asr-execution-v1.json';session_path=state_path.with_name(state_path.stem+'.session.json')
stamp=datetime.now(timezone.utc).isoformat()
if a.action=='register':
 assert not session_path.exists()
 matches=[]
 for p in psutil.process_iter(['pid','create_time','cmdline']):
  try:
   cmd=p.cmdline()
   if any(x.endswith('review-hierarchical-additions-voice-v1.py') for x in cmd) and '--mode' in cmd and cmd[cmd.index('--mode')+1]==a.mode:
    matches.append(dict(pid=p.pid,createTime=p.create_time(),commandLine=cmd,cwd=p.cwd()))
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 parents={psutil.Process(x['pid']).ppid() for x in matches};deep=[x for x in matches if x['pid'] not in parents];assert len(deep)==1,matches
 row=deep[0];row.update(sessionId=a.session,initialCompletion=a.chunk,registeredAt=stamp,cpuThreads=2,gpuJobs=0,
  launcherIdentities=[x for x in matches if x['pid']!=row['pid']],mode=a.mode)
 save(session_path,row)
 if state_path.exists():
  d=read(state_path);assert d['pid']==row['pid'] and d['createTime']==row['createTime'];d['sessionId']=a.session;save(state_path,d)
else:
 assert a.outer_exit is not None
 row=read(session_path);d=read(state_path);assert row['sessionId']==a.session and not d.get('actualExitObserved')
 assert not live(row) and all(not live(x) for x in row['launcherIdentities'])
 assert d['exitCode']==a.outer_exit
 if a.outer_exit==0:assert d['completed']==d['total']
 tts=read(V/'narration-additions-execution-v1.json')
 for x in tts['protectedInputs']+tts['results']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
 cim=subprocess.check_output(['powershell.exe','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={row["pid"]}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json'],encoding='utf8',errors='replace');assert not cim.strip()
 d.update(actualExitObserved=True,actualOuterExitCode=a.outer_exit,actualOuterSession=a.session,
  actualCompletionChunk=a.chunk,closedAt=stamp,workerAndLauncherDead=True,allProtectedAndCurrentPcmShaMatched=True)
 save(state_path,d);row.update(actualOuterExitCode=a.outer_exit,completionChunk=a.chunk,workerAndLauncherDead=True,closedAt=stamp);save(session_path,row)
cp_path=V/'latest-checkpoint.json';cp=read(cp_path)
cp.update(recordedAt=stamp,activeOwnedWorkers=1 if a.action=='register' else 0,
 ownedJob=row if a.action=='register' else None,
 stage=f'additions-{a.mode}-asr-{a.action}',
 next='Use the actual single ASR state/session until outer exit; then read all recognized full text/current words and exact independent boundaries. No TTS/source/native repeat.')
save(cp_path,cp)
qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentHierarchicalReview'].update(stage=cp['stage'],ownedJob=cp['ownedJob'],activeOwnedWorkers=cp['activeOwnedWorkers'],next=cp['next']);q['updatedAt']=stamp
assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(mode=a.mode,action=a.action,actualSession=a.session,identity=row,outerExit=a.outer_exit)))
