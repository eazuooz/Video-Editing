"""Record direct changed12 review; prepare its measured candidate, not approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
state=read(BASE/'guide12-room-contexts-asr-execution-v2.json')
assert state['exitCode']==0 and state['actualExitObserved'] and state['completed']==2
review_path=BASE/'guide12-room-contexts-direct-review-v2.json';assert not review_path.exists()
contexts=[]
for name,note in [
 ('12-complete-ending','Both complete sentences appear once; independentwordend6.20+offset2.34=8.54 equals the current whole ending. No extra greeting/truncated final word/full-sentence repetition observed. Human articulation remains pending.'),
 ('12-complete-join','Complete prior original paragraph, corrected room guide and complete following paragraph appear once. The unchangedoriginal조준에 is recognised as조준의 here. Preserve this particle difference for human listening; do not regenerate original PCM or copy recognition into the subtitle.')]:
 p=BASE/'guide12-room-contexts-asr-v2'/f'{name}.json';d=read(p)
 assert sha(ROOT/d['sourcePath'])==d['sourceSha256']
 contexts.append(dict(id=name,path=rel(p),sha256=sha(p),allExpectedAndActualTextAndWordTimestampsDirectlyRead=True,
  wordCount=len(d['words']),observation=note,audioPath=d['sourcePath'],audioSha256=d['sourceSha256']))
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now(),contexts=contexts,
 wholeReview=rel(BASE/'guide12-room-whole-direct-review-v2.json'),wholeReviewSha256=sha(BASE/'guide12-room-whole-direct-review-v2.json'),
 structuralContentReviewComplete=True,allChanged12CompleteContextsDirectlyRead=True,
 fullSentenceOmissionObserved=False,fullSentenceRepetitionObserved=False,extraGreetingObserved=False,
 pending=['Human whole listening and articulation','Unchangedoriginal조준에/조준의 recognizer variation','Source/cue motion and final mix readback'],
 asrApproved=False,narrationApproved=False,finalMixedAsrApproved=False,finalTimelineAdopted=False,newGitImages=0)
review_path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
tts=read(BASE/'guide12-room-tts-execution-v2.json')['results'][0]
plan=read(BASE/'measured-word-timing-candidate-v1.json')
p=next(x for x in plan['pieces'] if x['id']=='12')
old_audio=dict(path=p['audioPath'],sha256=p['audioSha256'],samples=p['samples'],seconds=p['sourceSeconds'])
new_frames=math.ceil(tts['samples']*60/24000);observation=p['durationFrames']-new_frames
assert new_frames==514 and observation==14
p.update(audioPath=tts['path'],audioSha256=tts['sha256'],samples=tts['samples'],sourceSeconds=tts['seconds'],
 voiceContainerFrames=new_frames,afterVoiceFrames=observation,
 paddingPurpose='After the complete spoken target-height observation, retain14frames(.233333s) of the same related moving game shot for viewers to follow its direction. No freeze/loop/slowdown; pending actual motion/caption review.',
 sourcePixelsReviewed=False,captionPixelsReviewed=False)
plan.update(preparedAt=now(),status='changed12-room-noun-measured-candidate; every actual source/cue/motion pending',
 baselineCandidate=rel(BASE/'measured-word-timing-candidate-v1.json'),baselineCandidateSha256=sha(BASE/'measured-word-timing-candidate-v1.json'),
 correctedGuide12=tts,correctedGuide12Review=rel(review_path),correctedGuide12ReviewSha256=sha(review_path),
 historicalGuide12Preserved=old_audio,newGuidePcmSecondsPreserved=76.96008333333334,allSpeechSeconds=373.68008333333334,
 originalPcmSecondsPreserved=296.72,originalWhiteSecondsPreserved=147.2,finalTimingApproved=False,bodyRatioApproved=False,
 finalTimelineAdopted=False,finalWordActionAlignment=False,allSourceSegmentPixelsReviewed=False,
 allDiagramPixelsReviewed=False,allFinalCaptionPixelsReviewed=False,finalMixedAsrApproved=False)
assert sum(r['frames'] for p in plan['pieces'] for r in p['roleSegments'] if r['role']=='actual-existing-game')==13710
dest=BASE/'measured-word-timing-candidate-v2.json';assert not dest.exists();dest.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(changed12ContextsDirectlyRead=2,currentSpeechSeconds=plan['allSpeechSeconds'],
 candidateFrames=23570,ratioApproved=False,finalPixelsApproved=False)))
