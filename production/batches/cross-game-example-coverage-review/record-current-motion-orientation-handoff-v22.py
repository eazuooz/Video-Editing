"""Read-only resource/byte observation and owned checkpoint handoff."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,subprocess,psutil,os
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'resource-and-annotation-handoff-v22.json';assert not out.exists()
private=read(R/'publishing/private-settings-direct-review-v1.json')
schedule=read(R/'publishing/schedule-direct-review-v1.json')
git=read(R/'publishing/schedule-git-verification-v1.json')
assert private['actualVideoId']==schedule['actualVideoId']==git['actualVideoId']=='lXjDBqONLWs'
assert private['fullAvailableSettingsVerified'] and schedule['savedAndReopened'] and schedule['futureScheduledListVerified']
assert git['exactLocalRemoteMatch'] and git['allFinalRemoteBlobsVerified']
tts=read(O/'narration-tts-execution-v2.json')
motion=read(R/'current17-main-promotion-v1.json')
for row in motion['otherProtectedInputs']+tts['protectedInputs']+tts['results']:
    assert sha(ROOT/row['path'])==row['sha256'],row['path']
processes=[]; own=[]
for p in psutil.process_iter(['pid','create_time','name','cmdline']):
    try:
        cmd=' '.join(p.info['cmdline'] or [])
        if (p.info['name'] or '').lower() in ('python.exe','ffmpeg.exe','node.exe'):
            processes.append(dict(pid=p.pid,createTime=p.info['create_time'],commandLine=p.info['cmdline'],cwd=p.cwd()))
            if p.pid!=os.getpid() and any(s in cmd for s in ['unpublished-teaching-clarity-revision','cross-game-example-coverage-review']) and any(s in cmd for s in ['render-orientation','review-orientation','extract-orientation','render-motion','review-motion','build-motion-current17','assemble-motion-current17','extract-motion']):own.append(p.pid)
    except(psutil.NoSuchProcess,psutil.AccessDenied):pass
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
cpu=psutil.cpu_percent(interval=2);ram=psutil.virtual_memory().available//1024
assert not own
now=datetime.now(timezone.utc).isoformat()
evidence=[R/'publishing/private-settings-direct-review-v1.json',R/'publishing/schedule-direct-review-v1.json',R/'publishing/schedule-git-verification-v1.json',O/'cross-game-native-direct-review-v1.json',O/'additions-whole-and-independent-direct-review-v1.json',O/'space-enlarged-static-direct-review-v3.json']
data=dict(recordedAt=now,previousHandoff='resource-and-annotation-handoff-v21.json',activeOwnedWorkers=0,currentResource=dict(cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,gpuObservation=gpu,processes=processes,cimActual=cim),motionOther70ProtectedShaMatched=True,orientation47ProtectedShaMatched=True,orientation6PcmShaMatched=True,
    motion=dict(actualVideoId='lXjDBqONLWs',productionReviewed=True,outputsCollected=True,privateSettingsVerified=True,gitDelivered=True,actualScheduledAt=schedule['scheduledAt'],savedScheduleReopened=True,oldVideoId='mBDd9VzSTkA',oldActualVisibility='private',oldDeleted=False,deletionConfirmationPending=True,repeatQuestion=False,humanListeningApproved=False,publicRightsApproved=False),
    orientation=dict(baselineVideoId='6-kP65hrZcI',whole6AsrClosed=True,independent22AsrClosed=True,nativeExtractionClosed=True,nativeSamplesDirectlyRead=217,nativeBoardsDirectlyRead=45,enlargedSpaceStatic8Reviewed=True,currentHeldParagraph='21a-p01',new3GameScriptsPrepared=False,movingCropApproved=False,minimumFourGameFinalApproved=False,finalDeliveryApproved=False),
    completedResearch=dict(pid75876CurrentlyAlive=False,status='complete_pending_visual_review',completed=1088,total=1088,restarted=False),processControlChanges=0,
    evidence=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in evidence],
    next='Do not repeat completed motion upload/QA/Git/schedule or deletion question. Prepare orientation3game paired causal scripts and21a-p01 scoped repair. Run no voice model until source/currentduplicate/freshresource guards pass. Complete current scope through normal-transform-UV then pause; no newSakurai6.')
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
qp=B/'queue.json'; raw=qp.read_bytes();q=read(qp);cp=read(O/'latest-checkpoint.json')
q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,nativeSourcePlanningReview=cp['crossGameNativeReview'],nativeSamplesDirectlyRead=217,nativeBoardsDirectlyRead=45,enlargedSpaceStaticReview=cp['spaceEnlargedStaticReview'],unmixedCurrentVoiceReview=cp['additionsCurrentDirectReview'],heldParagraphs=['21a-p01'],minimumFourGamesApproved=False,next=cp['next'])
q['currentOrientationReview']['ownedJob'].update(status='closed-native-pixels-directly-reviewed',allSamplesDirectlyRead=True,sourceSelectionApproved=True)
q['currentMotionReview']['currentStudioScheduleInterpretation']='Reviewed replacement lXjDBqONLWs Oct12 09:00Asia/Seoul saved/reopened and future list verified. Obsolete mBDd9VzSTkA is private; permanent deletion awaits one action-time confirmation.'
q['updatedAt']=now;q['latestHandoff']=out.relative_to(ROOT).as_posix()
assert qp.read_bytes()==raw
qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(handoff=out.relative_to(ROOT).as_posix(),cpu=cpu,ramKiB=ram,gpu=gpu,ownHeavy=0,motionReady=True,orientation217NativeReviewed=True,held='21a-p01')))
