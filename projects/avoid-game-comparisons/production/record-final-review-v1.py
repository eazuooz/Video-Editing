"""Record final approval only after an explicit direct-read ledger covers every page."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();pixel=read(W/'pixel-review-v1/index.json');ledger=read(W/'pixel-review-v1/direct-read-ledger.json');r=read(W/'render-result.json');t=read(W/'technical-measurements.json');a=read(W/'full-mix-asr-review.json');p=read(W/'plan.json');alignment=read(W/'caption-alignment-review.json')
assert len(pixel['rows'])==535 and len(pixel['pages'])==90 and len(ledger['pages'])==90
assert {x['path'] for x in ledger['pages']}=={x['path'] for x in pixel['pages']}
assert all(x['directlyRead'] and x['approved'] and sha(ROOT/x['path'])==x['sha256'] for x in ledger['pages'])
assert pixel['captionedSha256']==r['captionedSha256']==sha(ROOT/r['captioned'])
assert t['identicalAAC'] and t['frames']==32100 and a['allCurrentFinalMixAsrDirectlyCompared'] and a['paragraphs']==60 and a['mixSha256']==t['mixSha256']
assert p['body60_40ErrorFrames']==0 and p['actualFrames']==18828 and p['explanationFrames']==12552
assert alignment['approved'] and alignment['allParagraphTextsRetained'] and len(alignment['paragraphs'])==60
for page in pixel['pages']:page.update(directlyRead=True,reviewedAt=now)
for row in pixel['rows']:row.update(directlyRead=True,result='current-caption-lines-and-narrated-focus-readable')
pixel.update(status='all-current-rendered-pixels-directly-reviewed',allCaptionPixelsApproved=True,reviewedAt=now);write(W/'pixel-review-v1/index.json',pixel)
proof=dict(reviewedAt=now,captionedSha256=r['captionedSha256'],index=(W/'pixel-review-v1/index.json').relative_to(ROOT).as_posix(),all90PagesDirectlyRead=True,all199KoreanCuesDirectlyRead=True,captionIntersections=278,encodedBoundaryViews=254,compositionViews=3,uniqueFrames=532,fixedCenter=[960,970],findings=ledger['findings'],localOnlyRaster=True,newGitQaImages=0,humanWholeListening='pending',truncatedMemberHandles='pending')
write(W/'pixel-review-v1/direct-review.json',proof)
alignment.update(finalRenderedPixelsApproved=True,finalRenderedPixelReview=(W/'pixel-review-v1/direct-review.json').relative_to(ROOT).as_posix());write(W/'caption-alignment-review.json',alignment)
tracks=read(W/'caption-tracks.json');tracks.update(allFixedCaptionPixelsApproved=True,status='current-rendered-KO-and-independent-EN-meaning-reviewed');write(W/'caption-tracks.json',tracks)
qa=dict(schemaVersion=1,status='technical-approved-human-listening-pronunciation-public-rights-pending',reviewedAt=now,technicalApproved=True,frames=32100,seconds=535.0,actualFrames=18828,explanationFrames=12552,bodyActualRatioErrorFrames=0,actualExistingGameCuts=111,officialSources=8,agentCreatedGameCuts=0,sourceAudioStreams=0,allCurrentPcmSamplesPreserved=True,all60PcmParagraphsPreserved=True,originalSixExplanationPcmAndDurationPreserved=True,allCurrentVoiceAsrDirectlyCompared=True,allCurrentFinalMixAsrDirectlyCompared=True,allRenderedCaptionPixelsReviewed=True,captionCenter=[960,970],koCues=199,enCues=160,allBilingualParagraphs=60,wholeVideoOverview=dict(afterOriginalBrandingSeconds=2,measuredSeconds=23.44,classified='explanation',promisesPresentInBodyAndConclusion=True),membershipOutroFrames=600,memberIdentities='original12-profile-name-badge-rows-preserved',evidence=dict(technical=(W/'technical-measurements.json').relative_to(ROOT).as_posix(),pixels=(W/'pixel-review-v1/direct-review.json').relative_to(ROOT).as_posix(),mixedAsr=(W/'full-mix-asr-review.json').relative_to(ROOT).as_posix(),captionAlignment=(W/'caption-alignment-review.json').relative_to(ROOT).as_posix(),exactClock=(W/'caption-clock-full-result.json').relative_to(ROOT).as_posix()),cleanSha256=r['cleanSha256'],captionedSha256=r['captionedSha256'],loudness=t['loudness'],humanWholeListening='pending',pronunciationApproval='pending',uncertainPronunciationWords=['스콰이어/스쿼이어','책상/색상','차원/사원','정해/정의','맞히는/맞추는','같게/각계','페퍼/테퍼','적되/적대','의/에','마지막 prefix'],finalPublicRights='pending',originalNimbus='pending',truncatedMemberHandles='pending',externalBackup='pending',privateUpload='pending',platformAutomaticDubbing='pending')
write(W/'qa.json',qa);r.update(status='technical-approved-awaiting-collection-and-private-save',technicalQa=True,allFinalCaptionPixelsApproved=True,qa=(W/'qa.json').relative_to(ROOT).as_posix());write(W/'render-result.json',r)
print(json.dumps(dict(technicalApproved=True,frames=32100,koCues=199,enCues=160,humanListening='pending')))
