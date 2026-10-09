"""Seal the already directly read native edge boards, without media work."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,time,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except PermissionError:
            if n==39:raise
            time.sleep(.15)
stamp=datetime.now(timezone.utc).isoformat();p=BASE/'current-source-edge-extraction-v2.json';s=read(p)
assert s['exitCode']==0 and len(s['sources'])==3
assert not psutil.pid_exists(s['pid']) or abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01
proof=BASE/'current-native-source-edge-direct-review-v2.json';assert not proof.exists()
notes={
 'brotato-full-release':dict(observation='All five detected hard-cut triples and both interval edges directly read. Floors, avatars and weapon patterns change between separate montage shots.',detectedHardCuts=[550,880,1493,1748,2423],allInternalCutCoverageApproved=False,limitation='The .22 scene detector only produced candidates; lower-contrast changes/dissolves from the earlier full coarse review still require exact coverage before final cut QA.',candidateIntervalsSeconds=[[2,52]]),
 'drgs-engineer-crystalline-01':dict(observation='0–2.983 is OVERCLOCK selection. At4s gameplay/level-up beam resumes. At46 and51s GET TO THE DROP POD/countdown overlays appear rather than a selection menu. Later movement/pod approach is visible;64s starts fading and64.3s is dark.',candidateIntervalsSeconds=[[4,46],[53,63.8]],excludedSeconds=[[0,4],[46,53],[63.8,64.333333]],extensionTo64_3Approved=False,finalContinuousActionAndCaptionPixelsApproved=False),
 'drgs-engineer-crystalline-03':dict(observation='0/.5/.983/1s is active pursuit and movement.23.983s remains gameplay;25–25.5s level-up beam and25.983–26.5s menus are excluded.40.983/41s and66.983–68s remain active gameplay without fade.',candidateIntervalsSeconds=[[0,24],[41,68.1]],excludedSeconds=[[24,41]],candidateEdgeExtensionsDirectlySupported=True,finalContinuousActionAndCaptionPixelsApproved=False)}
rows=[]
for src in s['sources']:
    for f in src['frameEntries']:assert sha(ROOT/f['path'])==f['sha256']
    for b in src['boards']:assert sha(ROOT/b['path'])==b['sha256'];b['directlyRead']=True
    src['allBoardsDirectlyRead']=True
    rows.append(dict(stem=src['stem'],sourcePath=src['sourcePath'],sourceSha256=src['sourceSha256'],boards=src['boards'],frames=src['frameEntries'],review=notes[src['stem']]))
assert sum(len(r['frames']) for r in rows)==53 and sum(len(r['boards']) for r in rows)==10
save(proof,dict(schemaVersion=1,reviewedAt=stamp,sessionId=9061,actualExitCodeObserved=0,processIdentityAbsent=True,all53FramesAnd10BoardsDirectlyRead=True,sources=rows,completedTwoSourcesAnd34FramesPreserved=True,initialSharedQueuePermissionErrorHistory=s['failureHistory'],externalLocksRemoved=0,foreignProcessesChanged=0,localOnly=True,newGitRasterFiles=0,allFinalPixelsApproved=False,finalSourceAllocationApproved=False,bodyRatioApproved=False))
s.update(sessionId=9061,actualExitObserved=True,actualExitCodeObserved=0,processIdentityAbsentVerifiedAt=stamp,allBoardsDirectlyRead=True,directReview=proof.relative_to(ROOT).as_posix());save(p,s)
sp=BASE/'current-source-edge-extraction-v2.session.json';session=read(sp);session.update(actualExitObserved=True,exitCode=0,status='closed-exit0-direct-native-edges-read',observedAt=stamp);save(sp,session)
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=stamp,stage='current-voice-approved-source-allocation-preparation',currentNativeEdgeReview=proof.relative_to(ROOT).as_posix(),currentJoinedMiningVoiceApproved=True,currentJoinedMiningReview='projects/similar-game-design/production/current-mining-join-asr-direct-review-v1.json',nextAction='Inspect fresh official gameplay before any further observation narration. Preserve all approved current67 PCM and original white explanation; finalize meaningful source allocation and60:40 after measured additions.')
cp['ownedJob'].update(sessionId=9061,status='closed-exit0-direct-native-edges-read',workerExpectedRunning=False);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for n in range(40):
    raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='similar-game-design');item.update(stage=cp['stage'],currentExecution=cp['ownedJob'],currentNativeEdgeReview=cp['currentNativeEdgeReview'],currentJoinedMiningVoiceApproved=True,nextAction=cp['nextAction']);q.update(updatedAt=stamp,lastProgressAt=stamp)
    if qp.read_text('utf-8-sig')==raw:save(qp,q);break
    time.sleep(.15)
else:raise RuntimeError('Concurrent queue write')
print(json.dumps(dict(frames=53,boards=10,closedSession=9061,currentMiningJoinApproved=True,finalSourceAllocationApproved=False)))
