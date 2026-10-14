"""Fresh continuation identity; completed Orientation/Motion work is inherited, not rerun."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import psutil

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
B=ROOT/'production/batches/cross-game-example-coverage-review'
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(p,o):
    t=p.with_name(p.name+'.'+str(os.getpid())+'.writing')
    t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
out=R/'resource-and-annotation-handoff-v32.json';assert not out.exists()
prior_path=R/'resource-and-annotation-handoff-v31.json';prior=read(prior_path)
assert prior['scheduleReplacementVerified'] and prior['scheduleGitCommit']=='c8a656139dbb6d430a4e0572237f5e5de5a5a78d'
main_sha=sha(ROOT/'projects/game-math-orientation-matrices/project.json')
assert main_sha=='08bc7bdd71de66956ce145aeeba1fe7d301275d4ab637f8b13e4c79f9a04a278'
index=ROOT/'.git/index';index_before=sha(index)
git='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
entries_before=subprocess.check_output([git,'ls-files','--stage','-z'],cwd=ROOT)
baseline=read(V/'baseline-preservation-v1.json')
for item in baseline['protectedInputs']:
    assert sha(ROOT/item['path'])==item['sha256'],item['path']
source_path=V/'source-acquisition-execution-v2.json';source=read(source_path)
identities=[]
for expected in [source['worker']]+[c for c in source['children'] if c['status']=='running']:
    try:
        p=psutil.Process(expected['pid'])
        if abs(p.create_time()-expected['createTime'])<.02:
            identities.append(dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),
                expectedInputCommand=expected['command'],alive=True,kind=expected.get('kind','worker')))
    except psutil.NoSuchProcess:pass
assert any(x['kind']=='worker' for x in identities), 'Read current actual exit before recording another continuation phase'
helper=psutil.Process(27140)
assert abs(helper.create_time()-1791509666.8377817)<.02 and helper.cwd()==str(ROOT)
assert helper.cmdline()[-1]=='production/batches/sakurai-planning-game-design/proof-presenting-game-scores/serve-native-review-v1.py'
research=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')
assert sha(research)=='bbeac85c5f493baec614eeb5fae13f15d8b9b913f58631dce2d2ee211f07b0b8'
confirmation=read(O/'publishing/obsolete-deletion-action-time-confirmation-v1.json')
assert not confirmation['permanentDeletionExecuted'] and confirmation['userAnswer'] is None and confirmation['questionCount']==1
gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True)
assert gpu.returncode==0
cim=subprocess.run(['powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','node.exe','ffmpeg.exe') } | Select-Object ProcessId,ParentProcessId,Name,CreationDate,CommandLine | ConvertTo-Json -Depth 4 -Compress"],capture_output=True,encoding='utf8',errors='replace')
assert cim.returncode==0
(V/'handoff-resource-v32.cim.json').write_text(cim.stdout,'utf8')
stamp=datetime.now(timezone.utc).isoformat()
next_text='Hierarchy jBR Oct14 09AsiaSeoul remains unchanged. First3official sources actual92565/exit0 and native79458/exit0 are closed;64boards/371samples all read, with5new precise normal1x endpoints sealed. Reuse additional official Timberborn6TN source v2 actual36150/live exact command/create/state. After actual outer exit close via record-hierarchical-source-worker-v2.py actual exit/chunk, then fresh native resourcev2 and one prepared extract-hierarchical-native-candidates-v2.py (499new unique points/87boards/input-t-bounded); actual register/closure and new direct reviews only. No repeated371points/64boards/downloads/decode/whole-playback. Select exact4game actions before independent causal KOEN/overview, preserving original12PCM/60paragraphs/14pieces/white/Nimbus/branding/member. Do not alter baseline before final reviewed4files/private-settings/Git/saved schedule replacement. Both old deletion questions once pending; no repeats or deletion. Continue authorized closest future work through normal-transform-UV then pause own continuation; no new lectures/Sakurai6.'
record=dict(schemaVersion=2,recordedAt=stamp,stage='hierarchical-first-native-and-normal-source-review-complete;additional-official-source-running',
    previousHandoff=dict(path=prior_path.relative_to(ROOT).as_posix(),sha256=sha(prior_path)),
    completedOrientation=dict(videoId='orq0TMVkFts',productionCommit=prior['productionGitCommit'],
        scheduleCommit=prior['scheduleGitCommit'],actualScheduledAt=prior['actualScheduledAt'],
        fullSettingsComplete=True,scheduleSavedReopened=True,priorProofInherited=True,
        mediaUploadPlaybackGitRepeated=0,currentMainSha256=main_sha,currentMainTransition='current34-main-schedule-update-v1.json',old79GuardRun=False),
    hierarchy=dict(baselineVideoId='jBRt3xatdPk',currentActualScheduledAt='2026-10-14T09:00:00+09:00',
        baselineReservationChanged=False,protectedInputsChecked=49,all49ProtectedShaIdentical=True,
        original12PcmPreserved=True,original60KoEnParagraphsPreserved=True,original14PiecesPreserved=True,
        whitePalettePreserved=True,continuousNimbusPreserved=True,
        duplicateCurrentStrictCheckPassed=True,duplicateInventoryProjects=89,duplicateInventoryInputs=516,
        duplicateUnchanged501InputsInherited=True,duplicateNew15InputsWholeReviewed=True,
        firstSourceSession=92565,firstSourceExit=0,firstNativeSession=79458,firstNativeExit=0,
        firstNativeBoardsViewed=64,firstNativeSamples=371,newPreciseNormalIntervals=5,
        timberbornShortHeld=True,additionalSourceId='6TNjosDftog',additionalSourceSession=36150,
        additionalSourceState=source_path.relative_to(ROOT).as_posix(),additionalSourceActualOuterExit=None,
        additionalSourceActualIdentities=identities,newPreparedNativePoints=499,newPreparedNativeBoards=87,
        newPreparedNativeInputTimeBounded=True,oldNativePointsRepeated=0,
        sourcePrimaryRightsContextRecorded=True,publicRightsApproved=False,fourGameTeachingApproved=False,
        newNarrationWritten=False,newTtsStarted=False,newProductionRenderStarted=False,newActualVideoId=None,
        newGitDelivery=False,newScheduleReplacement=False),
    activeOwnedMediaWorkers=1,currentOwnedGpuJobs=0,resourceObservedAt=stamp,
    cpuPercent=psutil.cpu_percent(interval=.3),availableRamBytes=psutil.virtual_memory().available,
    gpuCsv=gpu.stdout.strip(),gpuTtsEligible=False,
    helper9250=dict(pid=helper.pid,createTime=helper.create_time(),command=helper.cmdline(),cwd=helper.cwd(),newServerStarted=False),
    completedResearchStatusSha256=sha(research),researchCompleted=1088,researchWorkerAlive=False,
    foreignProcessesOrLeaseChanged=False,foreignPart2LightingPreserved=True,
    currentExternalIndexSha256=index_before,currentExternalIndexEntriesSha256=hashlib.sha256(entries_before).hexdigest(),
    oldMotionDelete=dict(videoId='mBDd9VzSTkA',questionAlreadyAskedOnce=True,answerReceived=False,deletePerformed=False),
    oldOrientationDelete=dict(videoId='6-kP65hrZcI',confirmation=prior['orientationOldDelete']['confirmation'],
        currentConfirmationSha256=sha(O/'publishing/obsolete-deletion-action-time-confirmation-v1.json'),
        questionAlreadyAskedOnce=True,answerReceived=False,deletePerformed=False),
    newGitImages=0,newGitMedia=0,humanWholeListeningApproved=False,humanPronunciationApproved=False,
    optionalCcPropagationPending=True,automaticDubbingHumanReviewPending=True,next=next_text)
record['boundHierarchyRecords']=[dict(path=(V/n).relative_to(ROOT).as_posix(),sha256=sha(V/n)) for n in [
    'baseline-preservation-v1.json','current-content-and-studio-direct-review-v1.json',
    'duplicate-content-and-studio-direct-review-v1.json','duplicate-current-check-verification-v1.json',
    'source-acquisition-execution-v1.session.json','native-candidate-extraction-execution-v1.session.json',
    'native-candidate-direct-review-v2.json','candidate-normal-playback-observation-v2.json',
    'source-primary-rights-and-recent-use-v1.json','source-acquisition-execution-v2.session.json']]
assert sha(index)==index_before and subprocess.check_output([git,'ls-files','--stage','-z'],cwd=ROOT)==entries_before
record['externalIndexBytesAndEntriesPreserved']=True
save(out,record)
for cp_path in [V/'latest-checkpoint.json',R/'latest-checkpoint.json']:
    raw=cp_path.read_bytes();cp=read(cp_path)
    cp.update(recordedAt=stamp,latestHandoff=out.relative_to(ROOT).as_posix())
    if cp_path.parent==V:
        cp.update(activeOwnedWorkers=1,actualAdditionalSourceWorker=identities[0],
            additionalSourceOuterSession=36150,next=next_text)
    else:cp.update(activeContinuationSlug='hierarchical-game-outlines',activeContinuationOwnedWorkers=1,next=next_text)
    assert cp_path.read_bytes()==raw;save(cp_path,cp)
qpath=B/'queue.json';raw=qpath.read_bytes();q=read(qpath)
q['currentHierarchicalReview'].update(latestHandoff=out.relative_to(ROOT).as_posix(),activeOwnedWorkers=1,
    additionalSourceActualIdentities=identities,newPreparedNativePoints=499,newPreparedNativeBoards=87)
q.update(updatedAt=stamp,currentResourceHandoff=out.relative_to(ROOT).as_posix(),next=next_text)
assert qpath.read_bytes()==raw;save(qpath,q)
print(json.dumps(dict(handoff=out.relative_to(ROOT).as_posix(),activeOwnedMediaWorkers=1,actualSourceSession=36150,
    sourceIdentities=identities,all49ProtectedShaIdentical=True,externalIndexPreserved=True,preparedOnly499Points=True)))
