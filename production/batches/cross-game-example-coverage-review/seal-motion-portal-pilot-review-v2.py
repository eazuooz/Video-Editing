from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
p=R/'portal-annotation-pilot-execution-v2.json';s=read(p)
try:
    proc=psutil.Process(s['pid'])
    assert abs(proc.create_time()-s['createTime'])>=.01,'Worker still alive'
except psutil.NoSuchProcess:pass
assert s['exitCode']==0 and s['frames']==180 and len(s['samples'])==12
for x in s['samples']:assert sha(ROOT/x['path'])==x['sha256']
assert sha(ROOT/s['path'])==s['sha256']
s.update(actualExitObserved=True,actualOuterExitCode=0,
    actualExitEvidence='exec_command chunk b9b193 exit_code0; synchronous completion, no running session id returned',
    workerCurrentlyAlive=False)
save(p,s)
out=R/'portal-annotation-pilot-direct-review-v2.json';assert not out.exists()
review=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),
    actualOuterExitCode=0,actualSessionId=None,actualExecChunk='b9b193',
    priorDefectReview='portal-annotation-pilot-direct-review-v1.json',
    all12EncodedSamplesDirectlyRead=True,samples=s['samples'],videoPath=s['path'],videoSha256=s['sha256'],
    findings=['Frames0,1,15,30,45,60 hide the cyan wall label and endpoint; the previous false cube targeting is absent.',
        'Frames75,90,105,120,150,179 show cyan endpoints on the visible right wall and red endpoints on the upper cube edge.',
        'Both labels/source credit/fixed mock caption are clear in all12 full-resolution encoded samples.'],
    normalSpeedPlayback=dict(tabId='86',url='http://127.0.0.1:9250/motion-portal-annotation-pilot-v2.html',
        actualStart=dict(time=.251838,rate=1,paused=False,muted=True,ended=False),
        actualEnd=dict(time=3,duration=3,rate=1,paused=True,muted=True,ended=True),
        endpointPixelsDirectlyRead=True,everyIntermediatePlaybackFrameDirectlyObserved=False),
    selectedEncodedSampleGeometryApproved=True,normal1xStartEndVerified=True,
    wholeContinuousMovingAnnotationApproved=False,narrationTimed=False,finalCueApproval=False,
    allFinalPixelsApproved=False,sourceAudioAdopted=False,engineWorldAxisClaim=False,gitImagesAdded=0)
save(out,review)
c=read(R/'latest-checkpoint.json');c.update(recordedAt=review['reviewedAt'],
    stage='Portal-v2-bounded-pilot12samples-and-normal1x-endpoints-reviewed-awaiting-current-voice',
    portalPilotReview=str(out.relative_to(R)),
    ownedJob=dict(pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],cwd=s['cwd'],
        actualOuterExitCode=0,sessionId=None,workerCurrentlyAlive=False),
    next='Refresh changed full duplicate contents/current Studio, then fresh foreign research-restoration and stable-GPU evidence before a single new voice request. Keep pilot approval bounded; final narration/cues still pending.')
save(R/'latest-checkpoint.json',c)
qpath=ROOT/'production/batches/cross-game-example-coverage-review/queue.json';q=read(qpath)
q['currentMotionReview'].update(stage=c['stage'],portalPilotReview=str(out.relative_to(ROOT)),ownedJob=c['ownedJob'],next=c['next'])
save(qpath,q)
print('V2 all12 samples/normal1x endpoints verified; bounded approval only, final voice/cues/media pending.')
