"""Bind completed direct observations to the actual current pair, with honest scope."""
from pathlib import Path
import json,hashlib,datetime,sys,psutil
P=Path(__file__).resolve().parent;R=P.parents[3];H=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (P/'final-direct-review-v1.json').exists()
t=read(P/'final-timeline-v1.json');q=read(P/'qa-execution-v1.json');plan=read(P/'final-pixel-plan-v1.json');seen=read(P/'pixel-direct-observations-v1.json');normal=read(P/'normal-direct-review-v1.json')
assert q['exitCode']==0 and seen['allObserved'] and normal['ended'] and normal['playbackRate']==1 and normal['muted']
try:assert abs(psutil.Process(q['worker']['pid']).create_time()-q['worker']['createTime'])>.01
except psutil.NoSuchProcess:pass
assert seen['boards']==[x['path'] for x in plan['boards']]
for x in plan['boards']+plan['samples']:assert sha(R/x['path'])==x['sha256'],x['path']
cap=P/'hierarchical-game-outlines.captioned.review.mp4';clean=P/'hierarchical-game-outlines.clean.review.mp4'
assert sha(cap)==plan['captionedSha256']==normal['captionedSha256'] and abs(normal['duration']-t['totalFrames']/60)<.02
for x in read(P/'preservation.json')['files']:assert sha(R/x['path'])==x['sha256'],x['path']
for name in ['narration.ko.json','narration.en.json','captions.ko.srt','captions.en.srt','publishing/description.ko.txt','publishing/description.en.txt']:
 text=(P/name).read_text(encoding='utf-8').lower()
 assert not any(w in text for w in ['사쿠라이','마사히로','sakurai','桜井']),name
assert t['actualFrames']+t['explanationFrames']==t['bodyFrames'] and abs(t['actualFrames']-.6*t['bodyFrames'])<=1
mix=read(P/'mix-direct-review-v1.json');assert mix['approvedForEditing'] and sha(R/mix['audio'])==mix['audioSha256']
at=datetime.datetime.now(datetime.timezone.utc).isoformat()
j=dict(reviewedAt=at,captionedSha256=sha(cap),cleanSha256=sha(clean),timelineSha256=sha(P/'final-timeline-v1.json'),frames=t['totalFrames'],durationSeconds=t['totalFrames']/60,actualFrames=t['actualFrames'],explanationFrames=t['explanationFrames'],captionCuesKo=len(t['captionsKo']),captionCuesEn=len(t['captionsEn']),currentSamples=len(plan['samples']),currentBoards=len(plan['boards']),allPlannedSamplesDirectlyRead=True,allContinuousFramesReviewed=False,normalPlayback='normal-direct-review-v1.json',pixelObservations='pixel-direct-observations-v1.json',technicalQa='qa-execution-v1.json',mixReview='mix-direct-review-v1.json',preservedPriorFiles=len(read(P/'preservation.json')['files']),referenceNamesRemovedFromCurrentSpokenAndCaptionedText=True,pokemonDocument='Independently authored illustrative planning notes, not original development documents',rendererSelection='Simple text/indentation for document hierarchy; existing approved explanatory assets retained',approvedForPrivateUpload=True,humanFullListening=False,pronunciationApproved=False,publicRightsApproved=False,pending=['Human full listening and pronunciation','Prior menu uploader reuse permission/public-rights clearance','Original Nimbus/branding and truncated-member-handle review','External media backup'])
write(P/'final-direct-review-v1.json',j)
ledger=read(H/'production/review-ledger.json');ledger['entries'].append(dict(check='pokemon-opening-current-final-review',status='pass-for-private-editorial-delivery',scopeVersion='pokemon-opening-v2',evidence=rel(P/'final-direct-review-v1.json'),sha256=sha(P/'final-direct-review-v1.json'),allContinuousFramesReviewed=False,humanFullListening=False));ledger.update(updatedAt=at,userReviewPending=True,automaticNextVideo=False);write(H/'production/review-ledger.json',ledger)
cp=read(P/'latest-checkpoint.json');cp.update(updatedAt=at,stage='current-final-reviewed-ready-collection',worker=None,finalPair=True,finalQA=True,next='Promote only selected project paths, collect the four files, then upload one current captioned file privately.');write(P/'latest-checkpoint.json',cp)
print(json.dumps(j,ensure_ascii=False))
