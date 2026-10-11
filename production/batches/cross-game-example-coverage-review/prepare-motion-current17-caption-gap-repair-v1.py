"""Prepare caption builder V4; current ASR first words can include long quiet gaps."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=B/'prepare-motion-current17-captions-v3.py';dest=B/'prepare-motion-current17-captions-v4.py';assert not dest.exists()
text=src.read_text('utf-8-sig')
old="   assert end-start>2/60\n"
new="""   proposedStart=start
   # Word timestamps may include observation-only silence. Use exact placement
   # windows to exclude known long gaps from the word's caption onset.
   wordEnd=context['startSample']/48000+first['timestamp'][1]-.3
   voiceWindows=sorted((v['destinationStartSample']/24000,(v['destinationStartSample']+v['sourceEndSample']-v['sourceStartSample'])/24000) for v in plan['voicePlacements'] if v['sceneId']==sid)
   correctedGaps=[]
   for (_,leftEnd),(rightStart,_) in zip(voiceWindows,voiceWindows[1:]):
    if rightStart-leftEnd>=.5 and start<=rightStart<wordEnd:
     correctedGaps.append(dict(start=leftEnd,end=rightStart))
     start=rightStart
   assert end-start>2/60
"""
assert text.count(old)==1;text=text.replace(old,new)
old2="finalCueTimingDirectlyReviewed=False))";new2="finalCueTimingDirectlyReviewed=False,proposedWordStart=proposedStart,knownQuietGapsExcludedFromFirstWord=correctedGaps))"
assert text.count(old2)==1;text=text.replace(old2,new2)
dest.write_text(text,'utf-8')
p=R/'current17-mixed-contexts-asr-v3/07b-p02.json';v=json.loads(p.read_text('utf-8-sig'))
plan=R/'measured-current17-plan-v2.json';pv=json.loads(plan.read_text('utf-8-sig'))
placement=next(x for x in pv['voicePlacements'] if x['sceneId']=='07b' and x['sourceStartSample']==197040)
out=R/'current17-caption-word-leading-gap-observation-v1.json';assert not out.exists()
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),currentContext='07b-p02',resultSha256=sha(p),planSha256=sha(plan),firstWord=v['words'][0],contextStart=v['startSample']/48000,actualPlacedSpeechSegmentStart=placement['destinationStartSample']/24000,proposedWordStart=v['startSample']/48000,leadingQuietWouldShowCaptionSecondsEarly=placement['destinationStartSample']/24000-v['startSample']/48000,preparedBuilder=dest.relative_to(ROOT).as_posix(),preparedBuilderSha256=sha(dest),executed=False,all41TimingReviewApproved=False,finding='Current independent first-word interval covers long observation silence. Caption builder must clamp only observed placement gaps; all41 timing rows still require direct comparison. No media or PCM changed.'),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(prepared=dest.name,firstCueLeadingQuietSeconds=placement['destinationStartSample']/24000-v['startSample']/48000,captionBuilderExecuted=False)))
