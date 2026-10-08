"""Record observed download exit and a pre-state CPU guard rejection honestly."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
    for retry in range(40):
        try:os.replace(t,p);return
        except OSError:
            if retry==39:raise
            time.sleep(.15)
sp=BASE/'gauss129-acquisition-execution-v1.json';s=read(sp)
assert s['exitCode']==0 and s['pid']==47696 and s['sessionId']==20241
probe=subprocess.run(['powershell','-NoProfile','-Command','Get-CimInstance Win32_Process -Filter "ProcessId=47696 or ProcessId=47740" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4'],capture_output=True,text=True,check=True)
assert not probe.stdout.strip(),'Unexpected live/reused PID requires identity review'
s.update(actualExitObserved=True,actualSessionExitCodeObserved=0,actualCimPidAbsent=True,exitObservedAt=now());save(sp,s)
assert not (BASE/'gauss129-native-inspection-execution-v1.json').exists()
assert not (ROOT/'shared/output/player-customization/research/gauss-devstream129-native-v1').exists()
wait=dict(schemaVersion=1,slug='player-customization',recordedAt=now(),
    resourceEvidence='shared/output/player-customization/research/resources-before-gauss129-native-v1.json',
    observedCpuLoadPercent=85.0,requiredCpuLoadPercentBelow=85.0,attemptedWorker='projects/player-customization/production/inspect-gauss129-native-v1.py',
    actualAttemptExitCode=1,rejectedBeforeStateAndMedia=True,sourcePreserved=True,foreignProcessesTerminated=0,
    next='Recheck real resources; run this never-started native inspection only when its actual guard passes.')
wp=BASE/'gauss129-native-prestart-resource-wait-v1.json';save(wp,wait)
cpp=BASE/'latest-checkpoint.json';cp=read(cpp)
job=dict(status='fresh-gauss-download-completed',pid=s['pid'],commandLine=s['commandLine'],sessionId=s['sessionId'],
    processIdentity=s['processIdentity'],state=sp.relative_to(ROOT).as_posix(),cpuThreads=2,gpu=0,singleJob=True,exitCode=0,workerExpectedRunning=False,actualSessionExitCodeObserved=0,actualCimPidAbsent=True)
cp.update(stage='fresh-gauss-native-awaiting-resource-headroom',ownedJob=job,recordedAt=now(),
    currentParagraphRoleCandidate='projects/player-customization/planning/current16-paragraph-roles-v2.json',
    gauss129NativeResourceWait=wp.relative_to(ROOT).as_posix(),
    nextAction=wait['next']+' Preserve all64KOEN/current14125441PCM samples and completed white/native media; final allocation/ratio/mix/render/private remain false.')
if not any(x.get('sessionId')==20241 for x in cp.get('executionHistory',[])):
    cp.setdefault('executionHistory',[]).append(dict(**job,finishedAt=s['finishedAt']))
save(cpp,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization')
i.update(stage=cp['stage'],currentExecution=job,currentParagraphRoleCandidate=cp['currentParagraphRoleCandidate'],gauss129NativeResourceWait=cp['gauss129NativeResourceWait'],nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
print(json.dumps(dict(acquisitionExit0Observed=True,cimAbsent=True,nativeStarted=False,guardCpuPercent=85.0,paragraphRoleCandidatePrepared=True)))
