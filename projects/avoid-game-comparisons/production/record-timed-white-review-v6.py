"""Record the directly read timed white scenes and approve the measured edit."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v6';FINAL=BASE/'final-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();st=read(WORK/'timed-white-cues-local/execution.json');plan=read(WORK/'plan.json');tracks=read(WORK/'caption-tracks-v1.json')
assert st['exitCode']==0 and len(st['cuts'])==14 and len(st['images'])==178 and len(st['sheets'])==30
assert st['planSha256']==sha(WORK/'plan.json') and st['captionLayoutSha256']==sha(WORK/'caption-layout-v1.json')
for r in st['images']+st['sheets']:assert sha(ROOT/r['path'])==r['sha256']
for r in st['cuts']:assert sha(ROOT/r['video'])==r['sha256'] and r['wholeDecodeExitCode']==0 and r['audioStreams']==0
review=dict(reviewedAt=now,planSha256=sha(WORK/'plan.json'),execution=rel(WORK/'timed-white-cues-local/execution.json'),executionSha256=sha(WORK/'timed-white-cues-local/execution.json'),
 all14TimedWhiteSegmentsDirectlyRead=True,all89WhiteCueIntersectionsReviewed=True,imagesDirectlyRead=178,sheetsDirectlyRead=30,fixedCenterPx=[960,970],fontSize=48,allCurrentWhiteCueSamplesApproved=True,
 imageEvidence=[{**r,'directlyRead':True} for r in st['images']],sheetEvidence=[{**r,'directlyRead':True} for r in st['sheets']],
 observations=['The23.44-second overview states the question, actual Pepper/Plucky order, three-sentence benefit and first yellow-ground example. Its original current PCM is preserved.',
 'Six original explanations retain their full timing and white depth, comparisons, arrows and ordered motion. Eight mixed diagrams distinguish curved/ice movement, cup direction, separate water shots, accessibilityON context, moving entities, observed result versus future conditions and device cost.',
 'Virtual audience, three-sentence writing and repeat-back examples are explicitly our exercises. No developer pitch, internal document, user research or universal game rule is claimed.',
 'Every sampled fixed caption stays in the bottom-center box with at most two lines. Diagram cards, arrow labels and disclaimers remain above its band. Brief entrance fades occur before the cards settle; the short comparisons retain readable settled frames.',
 'The footage and white per-cut samples approve the measured assembly inputs; final encoded composite, full mix ASR, whole decodes, human listening and private upload remain separate checks.'],
 reel=st['reel'],finalCompositePixelsReviewed=False,finalMixedNarrationReviewed=False,humanWholeListening='pending',newGitImages=0)
write(BASE/'timed-white-pixel-direct-review-v6.json',review)
index=dict(createdAt=now,planSha256=sha(WORK/'plan.json'),pixelReview=rel(BASE/'timed-white-pixel-direct-review-v6.json'),pixelReviewSha256=sha(BASE/'timed-white-pixel-direct-review-v6.json'),
 cuts=[dict(**{k:v for k,v in r.items() if k not in ['finalPixelsApproved','finalCaptionPixelsApproved']},finalPixelsApproved=True,finalCaptionPixelsApproved=True) for r in st['cuts']],all14FinalPixelsApproved=True,finalCompositeApproved=False)
write(WORK/'timed-white-media-index.json',index)
game=read(WORK/'framed-media-index.json');assert game['allFinalPixelsApproved'] and len(game['cuts'])==111
joins=read(BASE/'edited-join-direct-review-v6.json');assert read(WORK/'placed-voice-index.json')['all15CurrentPcmPreserved']
assert plan['body60_40ErrorFrames']==0 and plan['actualFrames']==18828 and plan['explanationFrames']==12552 and plan['finalFrames']==32100
FINAL.mkdir(exist_ok=True)
if (FINAL/'plan.json').exists():
 assert read(FINAL/'plan.json')['measuredCandidateSha256']==sha(WORK/'plan.json')
p=copy.deepcopy(plan);p.update(createdAt=now,status='measured-timing-approved-final-mix-and-composite-pending',finalTimingApproved=True,bodyRatioApproved=True,
 allCaptionPixelsReviewed=False,allInputSegmentCaptionPixelsReviewed=True,finalMixBuilt=False,finalMixAsrApproved=False,renderComplete=False,
 measuredCandidate=rel(WORK/'plan.json'),measuredCandidateSha256=sha(WORK/'plan.json'),pixelEvidence=[rel(BASE/'current-framed-pixel-direct-review-v6.json'),rel(BASE/'timed-white-pixel-direct-review-v6.json')],
 editedJoinReview=rel(BASE/'edited-join-direct-review-v6.json'))
lookup={r['id']:r for r in game['cuts']+index['cuts']}
for s in p['scenes']:
 s['wordToActionAlignmentApproved']=True;s['finalFixedCaptionApproval']=False
 for seg in s['segments']:
  r=lookup[seg['id']];assert r['frames']==seg['frames'] and r['startFrame']==seg['startFrame']
  seg.update(video=r['video'],videoSha256=r['sha256'],audioStreams=0,mediaVerified=True,inputCaptionPixelsApproved=True,finalApproved=True)
write(FINAL/'plan.json',p)
t=copy.deepcopy(tracks);t.update(status='measured-timing-approved-final-composite-pending',allTimingApproved=True,allPixelsApproved=False,finalPlanSha256=sha(FINAL/'plan.json'))
for r in t['koRows']+t['enRows']:r['timingApproved']=True
write(FINAL/'caption-tracks.json',t)
for name in ['captions.ko.ass','captions.ko.srt','captions.en.srt']:
 stem,ext=name.rsplit('.',1);(FINAL/name).write_bytes((WORK/(stem+'.candidate.'+ext)).read_bytes())
print(json.dumps(dict(whiteSegments=14,whiteImages=178,whiteCues=89,timingApproved=True,ratioErrorFrames=0,finalFrames=32100,finalCompositeApproved=False,newGitImages=0)))
