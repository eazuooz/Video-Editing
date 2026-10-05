"""Record direct whole-script comparison of new edited voice readbacks."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,difflib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v6'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();p=WORK/'edited-join-asr-execution.json';d=read(p)
assert d['readbackComplete'] and d['exitCode']==0 and len(d['results'])==6
norm=lambda x:''.join(c for c in x if c.isalnum())
rows=[]
for r in d['results']:
 assert sha(ROOT/r['audioPath'])==r['audioSha256']
 r.update(directReview=True,directReviewAt=now)
 q=WORK/'edited-join-asr-local'/(r['id']+'.json');a=read(q);a.update(directReview=True,directReviewAt=now);write(q,a)
 rows.append(dict(id=r['id'],audioPath=r['audioPath'],audioSha256=r['audioSha256'],readbackPath=q.relative_to(ROOT).as_posix(),readbackSha256=sha(q),expectedKo=r['expectedKo'],actualAsr=r['text'],expectedWasRecognizerPrompt=False,
  normalizedCharacterMatch=difflib.SequenceMatcher(None,norm(r['expectedKo']),norm(r['text']),autojunk=False).ratio() if r['expectedKo'] else None,
  directWholeOrContextReview=True,observedOmission=False,observedSentenceRepeat=False,observedInventedGreeting=False,observedMissingFinalSyllable=False))
d.update(status='closed-all3-edited-whole-scenes-and3-joins-directly-reviewed',directReview=True,directReviewAt=now,sessionId=88128);write(p,d)
review=dict(schemaVersion=1,reviewedAt=now,scope='New edited10/12/13 whole PCM and three independent quiet-join contexts. This is separate from the yet unbuilt Nimbus final mix.',execution=p.relative_to(ROOT).as_posix(),executionSha256=sha(p),rows=rows,
 technicalWholeScriptAndJoinComparisonApproved=True,all15SourcePcmPreserved=True,editedVoiceAsrApproved=True,finalMixBuilt=False,finalMixAsrApproved=False,
 humanWholeListening='pending',humanPronunciationApproval='pending',uncertainties=[
 '10 spacing/punctuation varies around 색 공/색공 and 탈것/탈 것도; all five paragraphs and the independent Pepper transition preserve the intended observations and caution.',
 '12 all five paragraphs and both quiet contexts preserve fight/stair/desk/rocket, firing, unconfirmed cost/win condition, three-sentence exercise and listener restatement. No omitted or repeated sentence was observed.',
 '13 retains the earlier 적되/적대 recognition uncertainty. Its caution about exact inputs and universal object rules remains present. No new meaning loss observed; pronunciation is not human-approved.',
 'Whisper emitted an ending-timestamp warning for the13 whole readback; preserve the actual warning. All final written words including 드러납니다 were returned, with no null word timestamp in the saved result. A returned transcript is not proof of human pronunciation approval.'],
 sourceAudioUsed=False,newSynthesis=0,newGitImages=0)
write(BASE/'edited-join-direct-review-v6.json',review)
print(json.dumps(dict(wholeEditedScenes=3,wholeParagraphs=13,independentJoins=3,technicalReviewApproved=True,finalMixAsrApproved=False,humanListening='pending')))
