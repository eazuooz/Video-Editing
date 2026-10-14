"""Bind actual session without pretending a finished worker was live."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,subprocess,psutil,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--action',choices=['register','exit'],required=True);ap.add_argument('--session',type=int);ap.add_argument('--completion',required=True);ap.add_argument('--outer-exit',type=int);a=ap.parse_args()
sp=O/'additional-bank-native-extraction-v1.json';s=read(sp);sess=sp.with_name(sp.stem+'.session.json');at=datetime.now(timezone.utc).isoformat()
cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={s["pid"]}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json'],text=True,encoding='utf-8',errors='replace')
if a.action=='register':
 assert a.session is not None and not sess.exists();p=psutil.Process(s['pid']);assert abs(p.create_time()-s['createTime'])<.01 and p.cmdline()==s['commandLine'] and p.cwd()==s['cwd']
 save(sess,dict(registeredAt=at,sessionId=a.session,pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],cwd=s['cwd'],initialCompletion=a.completion,cimActual=cim));s['sessionId']=a.session;save(sp,s)
else:
 assert s['exitCode']==a.outer_exit and not cim.strip() and not psutil.pid_exists(s['pid'])
 if a.outer_exit==0:
  m=read(ROOT/s['manifest']);assert m['exactSourcePtsVerified'] and len(m['samples'])==53 and len(m['boards'])==12
  for x in m['sources']:assert sha(ROOT/x['sourcePath'])==x['sourceSha256'] and x['exactPtsMatched']
  for x in m['samples']+m['boards']:assert sha(ROOT/x['path'])==x['sha256']
  for x in m['samples']:assert x['pts']==x['nativeFrame']*256
  t=read(O/'narration-07b-guide-repair-execution-v1.json')
  for x in t['protectedInputs']+t['results']:assert sha(ROOT/x['path'])==x['sha256']
 if sess.exists():assert read(sess)['sessionId']==a.session
 s.update(actualSession=a.session,actualShellReturnedNoSession=a.session is None,actualOuterExitCode=a.outer_exit,actualCompletion=a.completion,actualExitObserved=True,cimAbsence=cim,closedAt=at,protectedShaMatched=True);save(sp,s)
 cp=read(O/'latest-checkpoint.json');cp.update(activeOwnedWorkers=0,ownedJob=None,stage=s['status']);save(O/'latest-checkpoint.json',cp);q=read(B/'queue.json');q['currentOrientationReview'].update(activeOwnedWorkers=0,ownedJob=None,stage=s['status'],actualSession=a.session);q['updatedAt']=at;save(B/'queue.json',q)
print(json.dumps(dict(action=a.action,session=a.session,outerExit=a.outer_exit,pid=s['pid'])))
