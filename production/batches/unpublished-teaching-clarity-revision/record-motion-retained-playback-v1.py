"""Record observed local UI endpoints without claiming unsampled frames/listening."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'retained-annotation-playback-observation-v1.json';assert not p.exists()
execution=read(R/'retained-annotation-render-execution-v1.json')
assert execution['actualExitCode']==0
rows=[]
for w in execution['windows']:
    assert sha(ROOT/w['video']['path'])==w['video']['sha256']
    rows.append(dict(scene=w['scene'],video=w['video'],
      observedStart=dict(currentTime=0,muted=True,playbackRate=1),
      observedEnd=dict(currentTime=w['frames']/60,muted=True,playbackRate=1)))
o=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),tabId='55',
 url='http://127.0.0.1:9250/motion-retained-annotations-review-v1.html',
 sixPlaybackEventRowsDirectlyRead=True,normalSpeedStartsAndEndsObserved=True,rows=rows,
 screenshotsDirectlyRead=['01 initial background post','03 playing at3.182301 aim and background','09 playing at2.90264 compact aim','11 ended at5 visible water direction'],
 noEveryIntermediateFrameClaim=True,wholeContinuousPlaybackApproved=False,wholeListeningApproved=False,
 selectedEncodedSamplesReview='retained-encoded-sample-direct-review-v1.json',
 selectedEncodedSamplesCount=150,selectedEncodedBoardsCount=27,
 finalCaptionPixelsApproved=False,currentMixedAudioApproved=False,
 nativePtsRemainTimingAuthority=True,localServerReused=True,newGitImages=0,researchManipulations=0)
p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(normalSpeedStartsAndEndsObserved=True,sceneCount=len(rows),everyIntermediateFrameApproved=False)))
