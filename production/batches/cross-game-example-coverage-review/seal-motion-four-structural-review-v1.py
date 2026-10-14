"""Seal the 30 directly inspected encoded prototype samples; never final timing approval."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
qa=read(R/'structural-prototype-qa-v1.json')
assert qa['encodedSamples']==30 and len(qa['boards'])==8 and qa['wholeDecodeExitCodes']==[0,0,0]
for x in qa['boards']+qa['allSamples']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
selected=[]
for sid,version in [('07b',2),('08b',1),('11b',3)]:
    e=read(R/f'structural-prototype-render-execution-v{version}.json')
    row=next(x for x in e['completed'] if x['id']==sid)
    assert e['actualExitCode']==0 and row['actualFfmpegExitCode']==0
    assert sha(ROOT/row['path'])==row['sha256'] and sha(ROOT/row['source'])==row['sourceSha256']
    selected.append(dict(version=version,**row))
v=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),
    qaPath=str((R/'structural-prototype-qa-v1.json').relative_to(ROOT)),qaSha256=sha(R/'structural-prototype-qa-v1.json'),
    selected=selected,allSelectedEncodedSamplesRead=True,directlyReadSamples=qa['allSamples'],directlyReadBoards=qa['boards'],
    observations={
      '07b':'Projected cube, floor, wall and device have distinct faces. View yaw and cube approach change the red connection. Ten selected frames show separate labels and floor above the reserved caption area.',
      '08b':'Projected doorway/floor and travelling yellow destination marker precede the board moving aside. Destination, doorway and footer remain separated at all ten sampled frames.',
      '11b':'Four task-to-cue rows have projected front/top/side faces. Yellow emphasis progresses from cleaning to puzzle, cube/device and destination/hand. V3 task labels clear their own and adjacent boxes in all ten samples.'},
    historicalRepairs=['V1 portal floor approached its relationship label; V2 shifts/scales the geometry.',
      'V1 transfer header/row labels were close to boxes; V2 adjusts header, V3 separates row labels. Historical renders retained; no claim that all historical samples were read.'],
    prototypeStructuralPixelReviewApproved=True,wholeContinuousPlayback=False,
    scope='Silent 6-second structural prototypes, sampled encoded pixels only; illustrative relationships, not engine-world measurements or comfort outcomes.',
    measuredNarrationTimed=False,finalTimingApproved=False,finalCueApproval=False,allFinalPixelsApproved=False,
    technicalFinalQaApproved=False,newPrivateUploaded=False,gitDelivered=False,gameplayAnnotationApproved=False,
    mediaAndQaGitAdded=0)
(R/'structural-prototype-direct-review-v1.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
print('30 exact encoded samples/8 boards and selected 07bV2/08bV1/11bV3 hashes sealed; final narration/caption approval false.')
