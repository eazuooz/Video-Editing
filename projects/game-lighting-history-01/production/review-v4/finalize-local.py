"""Record verified v4 visual review; preserve exact v3 narration/captions/timeline."""
import pathlib,json,hashlib,datetime,copy,runpy
import av
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/review-v4';B=P/'production/local/review-v3'
def rd(p):return json.loads(p.read_text('utf8'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
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
 runpy.run_path(str(P/'production/beginner-revision-v1/production-authority.py'))['require_selected_production']()
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();plan=rd(B/'plan.json');pair=rd(O/'pair/execution.json');visual=rd(O/'pair/visual-execution.json');qa=rd(O/'qa/index.json');joins=rd(O/'qa/joins.json');approval=rd(O/'qa/direct-review.json')
 assert pair['exitCode']==0 and len(pair['outputs'])==2 and len(qa['items'])==29
 assert approval['reviewedIds']==[x['id'] for x in qa['items']] and approval['joinBoardsReviewed']==list(range(joins['boards']))
 assert approval['annotationSha256']==pair['annotationSha256']==visual['inputs']['annotationSha256']==sha(H/'annotations.json')
 assert visual['inputs']['baselinePlanSha256']==pair['planSha256']==sha(B/'plan.json')
 reviewed={}
 for name,source in [('clean','visual.mp4'),('captioned','captioned-video.mp4')]:
  before=packets(O/'pair'/source);after=packets(O/'pair'/(name+'.mp4'));assert before==after;reviewed[name]=after
 assert all(x['sourceAacPacketMatch'] and x['fullVideoAudioDecodeExitCode']==0 for x in pair['outputs'].values())
 old=rd(P/'production/review-v3/final-review-summary.json')
 summary=dict(revision='review-v4',reviewedAt=now,status='internally-reviewed-human-drive-review-pending',frameCount=plan['frames'],seconds=plan['seconds'],format='1920x1080 60fps',outputs=pair['outputs'],
  annotationPlan=rel(H/'annotations.json'),annotationSha256=sha(H/'annotations.json'),baselinePlan=rel(B/'plan.json'),baselinePlanSha256=sha(B/'plan.json'),technicalEvidence=rel(O/'pair/execution.json'),fullDecodeBothPassed=True,
  visualReview=dict(annotationCount=29,patches=28,encodedMotionSamples=sum(len(x['frames']) for x in qa['items']),motionBoards=sum(x['boards'] for x in qa['items']),directReview=approval,captionAndJoinSamples=len(joins['items']),captionAndJoinBoards=joins['boards'],maxCaptionRegionRmse=joins['maxCaptionRegionRmse'],retainedPackets=visual['retainedPackets'],finalMuxVideoPacketMatch=reviewed,baselineReview=rel(P/'production/review-v3/final-review-summary.json'),baselineReviewSha256=sha(P/'production/review-v3/final-review-summary.json'),continuousHumanPlayback=False),
  learningObjective='일반인이 별도 자료 없이 영상만으로 용어, 보는 대상, 조건의 변화와 결과를 연결해 이해한다. 표식은 관찰을 돕고 실제 측정값으로 가장하지 않는다.',
  ratio=old['ratio'],audio=dict(status='reused-exact-AAC-payload-and-timestamps',sourceReview=old['audio'],newTts=False,newAsr=False,humanListening='pending',pronunciation='pending'),
  captions=dict(status='unchanged-content-and-timing; all changed-GOP cue pixels reviewed',koSha256=sha(B/'captions.ko.srt'),enSha256=sha(B/'captions.en.srt')),
  repairs=['Character selection follows per-frame visible editor anchors; label moved away from head.','Torso contour clears before fast orbit.','ASS timestamps aligned to60fps intervals; no transient missing-stroke frames.'],baselinePreserved=True,driveUserReview='pending',youtubeUploadAuthorized=False)
 wr(H/'final-review-summary.json',summary);wr(O/'pair/final-review.json',summary)
 pair.update(status='internally-reviewed-awaiting-drive-user-review',allFinalPixelsApproved=True,pixelReview=rel(H/'final-review-summary.json'));wr(O/'pair/execution.json',pair)
 # Recover the actual successful prior upload; do not upload v3 a third time.
 receiptPath=P/'production/review-v3/drive-final-review-receipt.json';v3=rd(receiptPath)
 v3.update(status='uploaded-playback-error-superseded-by-v4-in-progress',fileId='1YBVmH1v08MhFHcnbKP9j5c92EbGssf4U',versionId='0B__JCPwFbAsxK3l1ekw5dzdYMEpHZHZ1cEpYcmE4NkRBbHZnPQ',url='https://drive.google.com/file/d/1YBVmH1v08MhFHcnbKP9j5c92EbGssf4U/view',localPath=rel(B/'pair/captioned.mp4'),remoteSizeStatus='matches-local-complete-master',accessStatus='verified-owner-only',observedUi='항목1개 업로드 완료; file viewer 동영상을 로드할 수 없습니다. 다시 시도하세요.',processingAndPlaybackStatus='viewer-load-error; streaming not verified',recovery='Previously starting-only second request completed; actual file ID/size/revision and owner-only permissions recovered from Drive. No duplicate retry.',verifiedAt=now)
 wr(receiptPath,v3)
 m=rd(P/'project.json')
 if 'baselineDeliveryBeforeReviewV4' not in m:m['baselineDeliveryBeforeReviewV4']={k:copy.deepcopy(m[k]) for k in ['paths','finalRender','activeRevision','driveFinalReview','productionGates','productionState']}
 m['baselineDeliveryBeforeReviewV4']['driveFinalReview']=v3
 m.update(status='review-v4-ready-for-drive',publishReady=False)
 m['paths'].update(videoClean=rel(O/'pair/clean.mp4'),videoBurnedCaptions=rel(O/'pair/captioned.mp4'))
 m['editing']['timingStatus']='v4-visual-only; exact-v3-timing-and-57:43-ratio'
 m['finalRender']=dict(status=summary['status'],frames=plan['frames'],durationSeconds=plan['seconds'],outputs=pair['outputs'],technicalEvidence=rel(O/'pair/execution.json'),pixelEvidence=rel(H/'final-review-summary.json'),knownIssues=['Human final listening/pronunciation pending','Public rights review pending','Existing truncated member handle preserved'])
 m['revisionInProgress'].update(id='review-v4',status='local-complete-awaiting-drive-review',plan=rel(H/'annotations.json'),newOutputVerified=True)
 m['activeRevision'].update(id='review-v4',parentRevision='review-v3',status='ready-for-drive-final-review',plan=rel(B/'plan.json'),annotationPlan=rel(H/'annotations.json'),planSha256=sha(B/'plan.json'),newFinalRenderComplete=True,baselineDeliveryPreservedIn='baselineDeliveryBeforeReviewV4',finalReviewApproved=False,newYouTubeUploadAuthorized=False)
 m['productionGates'].update(finalRendered=True,allEncodedPixelsReviewed=True,outputCollected=False,uploaded=False,driveReviewCopyUploaded=False,drivePlaybackVerified=False,driveRemoteHashVerified=False)
 m['productionState'].update(updatedAt=now,currentEncodedReview=rel(H/'final-review-summary.json'),currentPairEvidence=rel(O/'pair/execution.json'),ownedGpuJobs=0,ownedCpuAsrJobs=0)
 m['driveFinalReview']=dict(version='review-v4',status='upload-pending',userReview='pending',youtubeUploadAuthorized=False,previousFiles=['1BE71qxJxW1wyBfUX60IKcJrQbgSl_ISc','1YBVmH1v08MhFHcnbKP9j5c92EbGssf4U'])
 wr(P/'project.json',m)
 cp=rd(P/'production/checkpoint.json');cp.update(updatedAt=now,stage='review-v4-local-complete-drive-upload-next',nextAction='Collect current four outputs; upload captioned1080p60 v4 once, verify playback/access then trash only superseded selected-video review copies. User reviews before YouTube.',activeOwnedHeavyJob=None,activeJob=None)
 cp['reviewV3'].update(status='local-complete-drive-upload-confirmed-playback-error',driveFileId=v3['fileId'])
 cp['reviewV4'].update(status='local-complete',finalReview=rel(H/'final-review-summary.json'),outputs=pair['outputs'],annotationCount=29,allChangedCaptionPixelsReviewed=True)
 cp['gates'].update(allFinalCaptionPixelsReviewed=True,finalRenderComplete=True,collected=False,uploaded=False,driveUserReview=False,driveCopyUploaded=False,drivePlaybackVerified=False,driveRemoteHashVerified=False)
 cp['driveFinalReview']=m['driveFinalReview'];wr(P/'production/checkpoint.json',cp)
 ledger=rd(P/'production/review-ledger.json');ledger.update(updatedAt=now,localProductionComplete=True,privateUploadComplete=False,deliveryComplete=False,allPlatformChecksPassed=False,gitDeliveryComplete=False)
 ledger['reviewV4'].update(status='local-complete-drive-pending',finalReview=rel(H/'final-review-summary.json'),fullEncodedPair=pair['outputs'],bodyRatio=summary['ratio'],narrationAndAudio='unchanged-exact-AAC; prior text and level review reused',humanListening='pending',pronunciation='pending');wr(P/'production/review-ledger.json',ledger)
 controlPath=R/'shared/publishing/video-production-control.json';control=rd(controlPath);control['selectedVideoRevision'].update(status='review-v4-local-complete-drive-review-next',finalReview=rel(H/'final-review-summary.json'));wr(controlPath,control)
 print('v4 verified local pair recorded; Drive user review remains pending')
if __name__=='__main__':main()
