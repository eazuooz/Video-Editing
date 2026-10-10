from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
q=read(R/'additive-mc-qa-v3.json');q2=read(R/'additive-mc-qa-v2.json')
assert q['actualFrames']==403 and q['actualDecodeExitCode']==0 and q['allFramePtsExact']
assert q['sampleCount']==36 and q['boardCount']==6 and q['maxNonWhitePixelsBelow910']==0
for data in (q,q2):
 assert sha(ROOT/data['source'])==data['sourceSha256']
 for x in data['samples']+data['boards']:assert sha(ROOT/x['path'])==x['sha256']
review=dict(recordedAt=now,sourceSha256=q['sourceSha256'],all36SamplesAnd6BoardsDirectlyRead=True,
 allFramePtsExact=True,wholeDecodeExitCode=0,maxNonWhitePixelsBelow910=0,
 selectedGoalSamplesApproved=True,projectedFacesOcclusionAndRotationReadable=True,
 labelLeaderAndFooterClearanceApproved=True,remainingSelectedSampleIssues=[],
 selectedOpening=dict(source=q2['source'],sourceSha256=q2['sourceSha256'],firstFrame=0,frames=480,
  evidence='additive-mc-direct-review-v2.json',selectedSampleReviewPassed=True),
 selectedGoal=dict(source=q['source'],sourceSha256=q['sourceSha256'],firstFrame=0,frames=403),
 totalSelectedFrames=883,actualMCRenderFfmpegExitCode=None,qaOuterExitCode=0,
 playback=dict(tabId='55',helper='motion-additive-mc-selected-review-v3.html',muted=True,rate=1,
  openingObservedStart=.154064,openingObservedAutoPause=8.267837,openingExactCutEndSeconds=8,
  openingBrowserEndpointOvershootNotExactCut=True,goalObservedStart=.143177,
  goalObservedEnd=6.716667,goalEnded=True,goalObservedSeekSeconds=4,
  allBetweenFramesContinuouslyObserved=False,wholeContinuousListeningApproved=False),
 narrationTimedFinalAnimationApproved=False,finalCaptionedPixelsApproved=False,
 v1AndV2HeldHistoryPreserved=True,originalScenesRerendered=0,newImageGitAdded=0)
assert not (R/'additive-mc-direct-review-v3.json').exists()
save(R/'additive-mc-direct-review-v3.json',review)
e=read(R/'additive-mc-execution-v3.json');e.update(actualRenderComplete=True,
 completionEvidence='CUA tab59 Render enabled after target render; actual403 frames and wholedecode0.',
 actualFfmpegExitCode=None,qaOuterExitCode=0,selectedSampleReview='additive-mc-direct-review-v3.json')
save(R/'additive-mc-execution-v3.json',e)
p=read(R/'retained-annotation-preflight-execution-v1.json')
assert p['actualOuterExitCode']==0 and p['samples']==127 and p['boards']==24
observations={
 '01':'Aim reticle and nozzle move while the left blue upright/background briefly stay stable. No visible water stream in this selected window; label aim, not water.',
 '03':'Free aim moves over a mostly stable staircase/tree background. Compare reticle/nozzle versus a real background edge; no clinical comfort claim.',
 '05':'Near tower posts and farther trees/fence change screen position while the player relocates. Rapid turn around frames100..120 needs hidden annotations until the same anchor is reacquired.',
 '07':'Different Talos excerpt tilts upward, then returns toward the floor. Wall/roof edges and the visible laser change screen orientation; do not imply uninterrupted action from preceding cuts.',
 '09':'Slide target remains identifiable as the view moves. Most frames have no spray; actual jet begins near330. Separate aim marker from water direction and retain floor/side-face cues.',
 '11':'View shifts among tower faces and then up toward bridge crossbar. Visible spray later follows the reticle; label background edge separately from local tool action.'}
for w in p['windows']:
 assert sha(ROOT/w['source'])==w['sourceSha256']
 for x in w['samples']+w['boards']:assert sha(ROOT/x['path'])==x['sha256']
 w.update(allSelectedSamplesDirectlyRead=True,observation=observations[w['scene']],
  semanticAnchorsApproved=False,finalCaptionedPixelsApproved=False)
p.update(stage='all-source-window-samples-read-annotation-tracking-pending',directReviewAt=now,
 all127SamplesAnd24BoardsDirectlyRead=True,allBetweenFramesContinuouslyObserved=False)
save(R/'retained-annotation-preflight-execution-v1.json',p)
c=read(R/'latest-checkpoint.json');c.update(recordedAt=now,stage='retained-gameplay-annotation-tracking',
 ttsStarted=True,ttsActualOuterExitCode=0,modelLoaded=True,
 additiveMcSelectedSampleReview='additive-mc-direct-review-v3.json',
 original12PcmPreserved=True,selectedAdditiveMcFrames=883,
 retainedAnnotationSourceReview='retained-annotation-preflight-execution-v1.json',
 next='Track semantic marks on six retained gameplay windows, review moving pixels, then assemble measured14-scene narration and current Nimbus mix.')
c['ownedJob']=dict(lastCompleted='retained annotation source preflight',sessionId=54103,
 actualOuterExitCode=0,cpuThreads=2,gpuJobs=0,foreignProcessesChanged=0,
 serverPid=77444,serverCreate='2026-10-11T02:34:49.455401+09:00',serverSessionId=70827,
 serverState='retained Vite9253; last target render complete; check actual survival before reuse')
save(R/'latest-checkpoint.json',c)
print(json.dumps(dict(selectedMcFrames=883,allSourceSamplesRead=127,allSourceBoardsRead=24,finalApproved=False)))
