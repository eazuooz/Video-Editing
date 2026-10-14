"""Seal actually read final samples and the observed normal playback, before promotion."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
out=R/'current17-final-encoded-pixel-direct-review-v1.json'
assert not out.exists()
notes=read(R/'current17-final-direct-review-notes-v1.json')
assert notes['boardsRead']==list(range(1,239)) and notes['finalApproval']['bounded']
mix=read(R/'current-mix-execution-v2.json')
for row in mix['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256']
assert len(mix['protectedInputs'])==71
pair=read(R/'current17-final-pair-execution-v2.json')
ps=read(R/'current17-final-pair-execution-v2.session.json')
xs=read(R/'current17-final-pixel-execution-v1.session.json')
assert ps['actualOuterExitCode']==xs['actualOuterExitCode']==0
assert not ps['workerCurrentlyAlive'] and not xs['workerCurrentlyAlive']
for row in pair['pair']:
 assert sha(ROOT/row['path'])==row['sha256']
 assert row['wholeDecodeExitCode']==0 and row['allPts1500Verified'] and row['identicalReviewedWholeAacPackets']
x=read(R/'current17-final-pixel-execution-v1.json');ip=ROOT/x['index'];i=read(ip)
assert sha(ip)==x['indexSha256'] and i['all220CuesAnd37PieceCutBoundariesIncluded']
assert len(i['samples'])==1425 and len(i['boards'])==238
for row in i['samples']+i['boards']:assert sha(ROOT/row['path'])==row['sha256']
covered=[n for b in i['boards'] for n in b['sampleIndices']]
assert covered==list(range(1,1426))
assert all(s['pts']==s['frame']*1500 for s in i['samples'])
end=read(R/'publishing/current17-flow-end-status-v1.json')
assert end['ended'] and end['paused'] and end['currentTime']==end['duration']==853.1 and end['rate']==1 and end['muted']
flow=dict(schemaVersion=1,observedAt=now,source=i['source'],sourceSha256=i['sourceSha256'],browserId='3',tabId='99',normalSpeed=1,muted=True,observedStart={'currentTime':.00586,'paused':False,'rate':1,'muted':True,'duration':853.1},observedProgressSeconds=[82.573277,378.74555,713.166075],observedEnd=end,noSeekOrReloadDuringObservedFlow=True,wholeNormalSpeedStartToEndObserved=True,allIntermediateFramesContinuouslyInspected=False,humanListeningApproved=False,evidence=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p)) for p in [R/'publishing/current17-flow-end-v1.ax.txt',R/'publishing/current17-flow-end-status-v1.json',R/'publishing/current17-flow-end-v1.png']])
save(R/'current17-final-normal-playback-direct-review-v1.json',flow)
plan=read(R/'measured-current17-plan-v2.json');assert plan['ratioErrorFrames']<=1 and plan['totalFrames']==51186
review=dict(schemaVersion=1,reviewedAt=now,source=i['source'],sourceSha256=i['sourceSha256'],index=str(ip.relative_to(ROOT)).replace('\\','/'),indexSha256=sha(ip),samples=i['samples'],boards=[dict(b,directlyReviewed=True) for b in i['boards']],directObservations=notes['notes'],all1425PlannedEncodedSamplesDirectlyRead=True,all238BoardsDirectlyRead=True,all220CuesFirstMidLastIncluded=True,all37CutsAnd29PcmPlacementsIncluded=True,correctedLeadingGapCueIds=[115,121,122,143,146,148],allExactAbsolutePtsVerified=True,sampledFixedCaptionAndUiClearanceApproved=True,narrationTimedMovingAnnotationSamplesApproved=True,normalPlaybackReview='current17-final-normal-playback-direct-review-v1.json',sampledDefects=[],retainedOriginalPieceCount=20,all71ProtectedInputsUnchangedBeforeMainPromotion=True,measuredTimingApproved=True,finalRatioApproved=True,bodyFrames=plan['bodyFrames'],actualFrames=plan['actualFrames'],explanationFrames=plan['explanationFrames'],ratioErrorFrames=plan['ratioErrorFrames'],technicalQaPassed=True,currentMixedReview='current17-mixed-complete-direct-review-v2.json',allContinuousFramesInspected=False,humanAcousticListeningApproved=False,publicRightsApproved=False,newGitMedia=0)
save(out,review)
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now,stage='final-current17-reviewed-awaiting-main-promotion-and-delivery',measuredTimingApproved=True,finalRatioApproved=True,allFinalPixelsApproved=True,finalPixelApprovalScope='All1425 planned encoded samples/238boards covering every220 cue and37cut; normal1x start/end. No claim every continuous frame.',qaApproved=True,currentFinalPixelReview=out.name,currentFinalNormalPlaybackReview='current17-final-normal-playback-direct-review-v1.json',activeOwnedWorkers=0,next='Explicit root main promotion with exact backup and70other protected SHA; collect four outputs; private upload/settings/selectGit/current09slot before corresponding obsolete deletion.')
t=R/'latest-checkpoint.json.writing';t.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,R/'latest-checkpoint.json')
print(json.dumps(dict(boards=238,samples=1425,cues=220,cuts=37,pairDecode=[0,0],normalEnded=True,protected=71,ratioErrorFrames=plan['ratioErrorFrames'],mainPromoted=False)))
