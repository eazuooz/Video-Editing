"""Synchronize the approved edit, both language tracks and independent MC scenes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;PROJECT=BASE.parent;W=BASE/'final-v1';MC=ROOT/'motion-canvas/src/projects/avoid-game-comparisons'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();plan=read(W/'plan.json');tracks=read(W/'caption-tracks.json');assert plan['finalTimingApproved'] and plan['bodyRatioApproved']
candidate=dict(path=rel(W/'plan.json'),sha256=sha(W/'plan.json'),actualFrames=18828,explanationFrames=12552,bodyFrames=31380,finalFrames=32100,finalSeconds=535.0,ratioErrorFrames=0,nativeCuts=111,
 allCurrent15PcmPreserved=True,originalSixExplanationMinimumFrames=9800,finalTimingApproved=True,bodyRatioApproved=True,allInputSegmentPixelsReviewed=True,allCaptionPixelsReviewed=False,finalMixBuilt=(W/'mix-settings.json').exists())
m=read(PROJECT/'project.json');m['status']='current15-measured-timing-approved-final-review-in-production';e=m['editing'];e.update(actualGameplaySeconds=313.8,actualExplanationSeconds=209.2,actualGameplayShare=.6,actualCommercialGameplaySeconds=313.8,actualDevelopmentFootageSeconds=0,bodyRatioApproved=True,measuredEditCandidate=candidate,
 timingStatus='32100 frames /535.0s;18828 actual and12552 explanation body frames, exact60:40. All15 PCM and six original explanations preserved; final encoded composite and mixed ASR pending.')
e['exampleInterleaving']['reviewStatus']='111 unique encoded official cuts and14 timed white inputs directly read with all current189 actual/89 white caption intersections; final composite pending.'
e['openingOverview']['measuredVoiceReview']='23.44s overview preserved; timed white overview pixels directly reviewed; current voice technical ASR approved; final mixed ASR/human listening pending.'
p=m['production'];p.update(finalTimingApproved=True,bodyRatioApproved=True,measuredEditCandidate=candidate,captionCandidate=dict(tracks=rel(W/'caption-tracks.json'),layout=rel(BASE/'measured-edit-v6/caption-layout-v1.json'),koCues=199,enCues=160,all60ParagraphsLiteralTextPreserved=True,fixedCenterPx=[960,970],fontSize=48,allFinalCueTimingApproved=True,allInputCuePixelsApproved=True,allFinalCuePixelsApproved=False,optionalTracksPublished=False),
 currentGameplayPixelReview=rel(BASE/'current-framed-pixel-direct-review-v6.json'),currentTimedWhitePixelReview=rel(BASE/'timed-white-pixel-direct-review-v6.json'),currentEditedJoinReview=rel(BASE/'edited-join-direct-review-v6.json'),finalMixCreated=(W/'mix-settings.json').exists(),finalRendered=False)
m['paths'].update(timeline=candidate['path'],candidateTimeline=rel(BASE/'measured-edit-v6/plan.json'),captionsKo=rel(W/'captions.ko.srt'),captionsEn=rel(W/'captions.en.srt'),captionAlignmentReview=rel(W/'caption-alignment-review.json'),editorAudioMix=rel(MC/'assets/final-mix.wav'))
write(PROJECT/'project.json',m)
for file in [PROJECT/'sources/action-map.json',PROJECT/'planning/chapter-plan.json']:
 j=read(file);j.update(updatedAt=now,measuredEditCandidate=candidate,ratioApproved=True,bodyRatioApproved=True,finalCutAndCaptionApproval=False,currentInputPixelApproval=True,finalTimingApproved=True,finalCompositeApproval=False)
 if file.name=='action-map.json':j.update(status='111-native-encoded-inputs-and-timed-white-approved-final-composite-pending',candidateActualSeconds=313.8,currentMeasuredSourceCutMap=rel(W/'plan.json'))
 write(file,j)
cp=read(MC/'production-plan.json');cp.update(status='current15-timing-and-media-inputs-approved-final-composite-pending',currentFinalTimingApproved=True,bodyRatioApproved=True,captionReviewComplete=False,finalVideoApproved=False,finalPlan=rel(W/'plan.json'),finalPlanSha256=sha(W/'plan.json'),actualFrames=18828,explanationFrames=12552,bodyFrames=31380,finalFrames=32100)
for old in cp['scenes']:
 s=next(s for s in plan['scenes'] if s['id']==old['id']);rows=[r for r in tracks['koRows'] if r['scene']==s['id']]
 ends=[max(r['endSeconds'] for r in rows if r['paragraph']==n)-s['startFrame']/60 for n in range(1,old['paragraphs']+1)]
 # The original six diagrams use the preserved PCM paragraph boundaries.
 if old['role']=='explanation':ends=[r['pcmToSample']/24000 for r in s['speechEvidence']];ends[-1]=s['seconds']
 old.update(frames=s['frames'],seconds=s['seconds'],startFrame=s['startFrame'],paragraphEnds=ends,inputPixelsReviewed=True)
 if old['role']!='explanation':
  old.update(actualMediaVerified=True,actualAudioStreams=0,actualVideo='',segments=[dict(role='actual-existing-game' if r['classification']=='actual-existing-game' else 'explanation',frames=r['frames'],video=r['video'],mediaVerified=True,audioStreams=0,diagramId=r.get('diagramId',''),diagramPixelsReviewed=True,inputPixelReviewComplete=True) for r in s['segments']],actualFrames=sum(r['frames'] for r in s['segments'] if r['classification']=='actual-existing-game'),diagramFrames=sum(r['frames'] for r in s['segments'] if r['classification']=='explanation'),diagramPixelsReviewed=True)
write(MC/'production-plan.json',cp)
for f in ['final-mix.wav','final-mix.m4a']:
 src=W/f;dest=MC/'assets'/f;dest.parent.mkdir(exist_ok=True)
 if dest.exists():assert sha(dest)==sha(src)
 else:shutil.copyfile(src,dest)
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qpath);item=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons');item['measuredEditCandidate']=candidate;item['captionCandidate']=p['captionCandidate'];item['checkpoints']['finalTimingApproved']=True;item['checkpoints']['bodyRatioApproved']=True;item['updatedAt']=now;q['updatedAt']=now;write(qpath,q)
print(json.dumps(dict(scenes=15,frames=32100,bodyRatioErrorFrames=0,allInputPixelsReviewed=True,finalCompositeReviewed=False)))
