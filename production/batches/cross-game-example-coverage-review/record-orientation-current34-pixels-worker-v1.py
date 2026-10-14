"""Register or close the actual current34 guide/pair pixel extraction session."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess
import psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,v):
    t=p.with_name(p.name+'.record-writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['guides','pair'],required=True)
ap.add_argument('--session',type=int,required=True);ap.add_argument('--initial')
ap.add_argument('--outer-exit',type=int);ap.add_argument('--completion');a=ap.parse_args()
sp=O/f'current34-{a.mode}-pixel-execution-v1.json';ss=sp.with_name(sp.stem+'.session.json');s=read(sp)
try:
    p=psutil.Process(s['pid']);same=abs(p.create_time()-s['createTime'])<.01
    if same:assert p.cmdline()==s['commandLine'] and p.cwd()==s['cwd']
    alive=same and p.is_running()
except psutil.NoSuchProcess:alive=False
cim=subprocess.check_output(['powershell','-NoProfile','-Command',
    f"Get-CimInstance Win32_Process -Filter 'ProcessId={s['pid']}' | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json"],text=True,encoding='utf-8',errors='replace')
if a.outer_exit is None:
    assert a.initial and not ss.exists()
    save(ss,dict(recordedAt=now(),sessionId=a.session,initialChunk=a.initial,pid=s['pid'],createTime=s['createTime'],
        commandLine=s['commandLine'],cwd=s['cwd'],workerAliveAtRegistration=alive,cimActual=cim))
    s['sessionId']=a.session
else:
    assert a.completion and not alive and s['exitCode']==a.outer_exit and read(ss)['sessionId']==a.session
    proof=read(O/'narration-07b-guide-repair-execution-v1.json')
    for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
    if a.outer_exit==0:
        assert len(s['results'])==(8 if a.mode=='guides' else 1)
        for row in s['results']:
            assert row['extractExitCode']==0 and row['allSelectedEncodedPtsExact']
            assert sha(ROOT/row['video'])==row['videoSha256']
            for x in row['samples']:
                assert x['pts']==x['frame']*1500 and sha(ROOT/x['path'])==x['sha256']
            for x in row['boards']:assert sha(ROOT/x['path'])==x['sha256']
    s.update(actualOuterExitCode=a.outer_exit,actualExitObserved=True,actualSession=a.session,completionChunk=a.completion,
        workerDead=True,closureObservedAt=now(),closureCimActual=cim,all79ProtectedInputsUnchanged=True,repairCandidateUnchanged=True)
    cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=s['status']+'-actual-closed',activeOwnedWorkers=0,ownedJob=None,
        next='Directly inspect every planned encoded sample and normal UI playback. Final244-caption pixels, delivery/settings/Git/schedule remain unapproved.')
    save(O/'latest-checkpoint.json',cp)
    qp=B/'queue.json';old=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==old;save(qp,q)
save(sp,s)
print(json.dumps(dict(mode=a.mode,session=a.session,alive=alive,outerExit=a.outer_exit,registered=a.outer_exit is None)))
