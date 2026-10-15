"""Record direct visual review and expose the verified v3 pair to the collector.

Run only after inspecting qa/board-00..34, mobile-375 and full-resolution samples.
Does not encode, regenerate speech, upload, or approve human listening.
"""
import pathlib,json,hashlib,datetime,copy
import av
R=pathlib.Path(__file__).resolve().parents[4]
P=R/'projects/game-lighting-history-01'; H=pathlib.Path(__file__).parent; O=P/'production/local/review-v3'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(R).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def packets(p):
 h=hashlib.sha256();n=0
 with av.open(str(p)) as c:
  s=c.streams.video[0];extra=hashlib.sha256(s.codec_context.extradata).hexdigest()
  for q in c.demux(s):
   if q.pts is not None:h.update(bytes(q));n+=1
 return dict(sha256=h.hexdigest(),frames=n,extradataSha256=extra)
def main():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 plan=rd(O/'plan.json');pair=rd(O/'pair/execution.json');visual=rd(O/'pair/visual-execution.json');qa=rd(O/'qa/index.json')
 assert pair['exitCode']==0 and len(pair['outputs'])==2 and len(qa['items'])==414 and qa['boards']==35
 assert pair['planSha256']==sha(O/'plan.json')==visual['planSha256']
 reviewed={}
 for name,source in [('clean','visual.mp4'),('captioned','captioned-video.mp4')]:
  before=packets(O/'pair'/source);after=packets(O/'pair'/(name+'.mp4'));assert before==after
  reviewed[name]=after
 asr=rd(O/'mixed-asr-direct-review.json');levels=rd(O/'local-level-review.json')
 assert asr['contentCoverageApproved'] and asr['allCurrentMixedTextsDirectlyCompared'] and levels['measurementPass']
 summary=dict(revision='review-v3',reviewedAt=now,status='internally-reviewed-human-drive-review-pending',planSha256=sha(O/'plan.json'),outputs=pair['outputs'],
  technicalEvidence=rel(O/'pair/execution.json'),fullDecodeBothPassed=True,frameCount=plan['frames'],seconds=plan['seconds'],format='1920x1080 60fps',
  visualReview=dict(index=rel(O/'qa/index.json'),indexSha256=sha(O/'qa/index.json'),boardsReviewed=list(range(35)),sampledFrames=414,
   method=qa['method'],mobileWidth=375,mobileSamples=16,full1080Samples=[19629,72675,111961],
   findings=['DOOM rear-wall is behind the character throughout sampled motion; true foreground occlusion retained.',
    'Normal, surface-to-light and incoming-ray directions are distinct. Inner-product results follow the spoken numerical steps.',
    'RNM basis stays attached to the surface; fixed stored colors, changing weights and the 0.793 sum are visible.',
    'Shadow Map, PCF, PCSS, Variance Shadow Maps, Virtual Shadow Maps and CSM names are explicit.',
    'Fixed captions remain inside frame and do not cover the teaching focus; full-size and 375px samples inspected.'],
   defectsFound=[],continuousHumanPlayback=False,retainedEvidence=visual['retainedPackets'],finalMuxVideoPacketMatch=reviewed),
  ratio=dict(actualFrames=plan['actualFrames'],explanationFrames=plan['explanationFrames'],bodyFrames=plan['bodyFrames'],target=plan['ratioTarget'],roundingErrorFrames=plan['ratioRoundingErrorFrames']),
  audio=dict(fullCurrentAsr=rel(O/'mixed-asr-direct-review.json'),localLevels=rel(O/'local-level-review.json'),humanListening='pending',pronunciation='pending',
   listeningFocus='08-r8 first word 구현에서는: source ASR matches; encoded-context ASR variants remain ambiguous, not a confirmed pronunciation defect.'),
  baselinePreserved=True,driveUserReview='pending',youtubeUploadAuthorized=False)
 wr(O/'pair/final-review.json',summary);wr(H/'final-review-summary.json',summary)
 pair.update(status='internally-reviewed-awaiting-drive-user-review',allFinalPixelsApproved=True,pixelReview=rel(H/'final-review-summary.json'));wr(O/'pair/execution.json',pair)
 # Keep the hashed render plan immutable; approvals live in this review and ledger.
 m=rd(P/'project.json')
 if 'baselineDeliveryBeforeReviewV3' not in m:m['baselineDeliveryBeforeReviewV3']={k:copy.deepcopy(m[k]) for k in ['paths','finalRender','activeRevision','driveFinalReview','productionGates','productionState']}
 m.update(status='review-v3-ready-for-drive',publishReady=False)
 for lang in ['ko','en']:
  current=rd(H/f'complete-narration.{lang}.json');old=rd(P/f'script/narration.{lang}.json');titles={s['id']:s.get('title',s['id']) for s in old['scenes']}
  current['scenes']=[dict(id=c['chapter'],title=titles.get(c['chapter'],c['chapter']),lines=[c.get('narration',c.get('text'))],orderedParagraphKeys=c.get('orderedKeys',[])) for c in current['chapters']]
  current.update(schemaVersion=1,status='complete-current-encoded-narration-content-reviewed',humanListening='pending')
  wr(H/f'complete-narration.{lang}.json',current)
 m['paths'].update(script=rel(H/'complete-narration.ko.json'),scriptEn=rel(H/'complete-narration.en.json'),audioReport=rel(O/'mix-execution.json'),audioMix=rel(O/'final-mix.m4a'),narration=rel(O/'narration-current.wav'),captionsKo=rel(O/'captions.ko.srt'),captionsEn=rel(O/'captions.en.srt'),videoClean=rel(O/'pair/clean.mp4'),videoBurnedCaptions=rel(O/'pair/captioned.mp4'),captionAlignmentReview=rel(O/'caption-alignment-review.json'))
 m['editing'].update(actualGameplaySeconds=plan['actualFrames']/60,actualExplanationSeconds=plan['explanationFrames']/60,actualGameplayShare=plan['actualFrames']/plan['bodyFrames'],plannedActualSeconds=plan['actualFrames']/60,plannedExplanationSeconds=plan['explanationFrames']/60,timingStatus='v3-measured-57:43-within-one-frame')
 m['video']['durationSeconds']=plan['seconds']
 m['finalRender']=dict(status=summary['status'],frames=plan['frames'],durationSeconds=plan['seconds'],outputs=pair['outputs'],technicalEvidence=rel(O/'pair/execution.json'),pixelEvidence=rel(H/'final-review-summary.json'),knownIssues=['Human final listening/pronunciation pending','Public rights review pending','Existing truncated member handle preserved'])
 m['revisionInProgress'].update(id='review-v3',status='local-complete-awaiting-drive-review',plan=rel(H/'design.json'),newOutputVerified=True)
 m['activeRevision'].update(id='review-v3',parentRevision='continuity-v2',status='ready-for-drive-final-review',plan=rel(O/'plan.json'),planSha256=sha(O/'plan.json'),newFinalRenderComplete=True,baselineDeliveryPreservedIn='baselineDeliveryBeforeReviewV3',finalReviewApproved=False,newYouTubeUploadAuthorized=False)
 m['productionGates'].update(finalRendered=True,allEncodedPixelsReviewed=True,finalMixedAsrApproved=True,finalRatioMeasured=True,final60to40Measured=False,outputCollected=False,uploaded=False,driveReviewCopyUploaded=False,drivePlaybackVerified=False,driveRemoteHashVerified=False)
 m['productionState'].update(updatedAt=now,currentParagraphPairs=155,currentFinalPlan=rel(O/'plan.json'),currentVoiceAsrExecution=rel(O/'source-review.json'),currentVoiceDirectReview=rel(O/'source-review.json'),currentVoiceReview='Eight changed source paragraphs plus all 13 current encoded chapter texts compared; human listening/pronunciation pending.',currentMixedReview=rel(O/'mixed-asr-direct-review.json'),currentCaptionAlignment=rel(O/'caption-alignment-review.json'),currentEncodedReview=rel(H/'final-review-summary.json'),currentPairEvidence=rel(O/'pair/execution.json'),currentLocalLevels=rel(O/'local-level-review.json'),ownedGpuJobs=0,ownedCpuAsrJobs=0)
 m['driveFinalReview']=dict(version='review-v3',status='upload-pending',userReview='pending',youtubeUploadAuthorized=False,previousFileId='1BE71qxJxW1wyBfUX60IKcJrQbgSl_ISc')
 wr(P/'project.json',m)
 timeline=rd(P/'production/current-rebuild-timeline.json');timeline.update(canonicalPlan=rel(O/'plan.json'),canonicalPlanSha256=sha(O/'plan.json'),scenes=plan['nodes'],voice=plan['voice']);wr(P/'production/current-rebuild-timeline.json',timeline)
 cp=rd(P/'production/checkpoint.json');cp.update(updatedAt=now,stage='review-v3-local-complete-drive-upload-next',nextAction='Collect four verified outputs once; upload captioned 1080p60 master as new Drive v3; preserve v2; await user review before YouTube.',activeOwnedHeavyJob=None,activeJob=None)
 cp['reviewV3'].update(status='local-complete',currentFullMixAsr='all13-current-chapters-directly-compared',finalReview=rel(H/'final-review-summary.json'),outputs=pair['outputs'])
 cp['gates'].update(finalTimelineApproved=True,bodyRatioApproved=True,allFinalCaptionPixelsReviewed=True,finalRenderComplete=True,collected=False,uploaded=False,finalMixedAsrApproved=True,driveUserReview=False,driveCopyUploaded=False,drivePlaybackVerified=False,driveRemoteHashVerified=False)
 cp['driveFinalReview']=m['driveFinalReview'];wr(P/'production/checkpoint.json',cp)
 ledger=rd(P/'production/review-ledger.json');ledger.update(updatedAt=now,localProductionComplete=True,privateUploadComplete=False,deliveryComplete=False,allPlatformChecksPassed=False,gitDeliveryComplete=False)
 ledger['reviewV3'].update(status='local-complete-drive-pending',finalReview=rel(H/'final-review-summary.json'),fullEncodedPair=pair['outputs'],bodyRatio=summary['ratio'],fullCurrentMixAsr='content-compared',humanListening='pending',pronunciation='pending',localLevelMeasurement='passed')
 wr(P/'production/review-ledger.json',ledger)
 print('v3 local pair and direct visual review recorded; human review remains pending')
if __name__=='__main__':main()
