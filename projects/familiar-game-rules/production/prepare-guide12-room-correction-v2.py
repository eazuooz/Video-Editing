"""Correct a source-specific noun, preserving all older text/audio/evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
plan_path=BASE.parent/'planning/observation-guides-v1.json'
request_path=BASE/'observation-guide-tts-request-v1.json'
g=read(plan_path)['guides'][0];assert g['id']=='12'
old=dict(g)
g.update(title='분홍색 방의 대상과 계단 위의 대상',
 ko='분홍색 방에서 대상을 겨눕니다. 다음 계단 컷에서는 높은 쪽으로 화면을 돌리죠. 대상의 높이와 방향 잡기를 함께 따라가 보세요.',
 en='The player aims at targets in the pink room. The next stairway shot turns the view upward. Follow the target’s height and the change in direction together.',
 path='shared/output/narration/familiar-game-rules/observation-guides-v2/12.wav',
 visibleActionAndConnection='Pink-lit room at FVk8–9s and separate upward stair/escalator shots. No door pigment, exact keys, strategy or developer intent is inferred.',
 finalWordActionAlignment=False,framingApproved=False)
g['text']=g['ko']
review_path=BASE/'guide12-room-noun-direct-review-v2.json'
assert not review_path.exists()
boards=[]
for name,note in [
 ('FVkDc6u_4GQ-03.jpg','6s door kick/6.5–7s window targets;8–9s clearly pink-lit room with enemies by doors. Doors vary beige/orange under lighting; avoid asserting their pigment.'),
 ('FVkDc6u_4GQ-04.jpg','9s pink room targets,9.5–10.5s separate grey/red-lit corridor firing. Cannot label all8–10.5s as one pink-door shot.')]:
 p=ROOT/'shared/output/familiar-game-rules/research/additional-native-v1/boards'/name
 boards.append(dict(path=rel(p),sha256=sha(p),allSixSamplesDirectlyRead=True,observation=note))
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=datetime.now(timezone.utc).isoformat(),guide='12',
 oldText=old['ko'],newText=g['ko'],oldEnglish=old['en'],newEnglish=g['en'],boards=boards,
 reason='Retain the visible aim/height/direction comparison while replacing an uncertain door-colour assertion with the directly visible pink room.',
 beforeTtsPairedTextReviewed=True,centralQuestionChanged=False,chapterClaimChanged=False,overviewPromiseChanged=False,
 oldGuideAudioPreserved=old['path'],oldGuideAudioSha256=sha(ROOT/old['path']),original11PcmPreserved=True,
 otherSevenGuidesPreserved=True,wholeAsrDirectReview=False,independentContextReview=False,joinsApproved=False,
 humanWholeListening='pending',pronunciation='pending',currentCanonicalScriptUnchanged=True,
 priorTimingCandidate='projects/familiar-game-rules/production/measured-word-timing-candidate-v1.json',
 priorCaptionsCandidate='projects/familiar-game-rules/production/word-caption-candidate-v1/captions.json',
 priorCandidateMayBeAdopted=False,finalTimingApproved=False,newGitImages=0)
review_path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
req=read(request_path)
protected=req['protectedInputs']+[dict(path=x['path'],sha256=sha(ROOT/x['path'])) for x in read(plan_path)['guides']]
req.update(guides=[g],revision='only-guide12-room-noun-v2',protectedInputs=protected,
 baselineRequest=rel(request_path),baselineRequestSha256=sha(request_path),
 textReview=rel(review_path),textReviewSha256=sha(review_path),guideCount=1,
 previouslySynthesizedGuidesRepeated=False,allOtherSevenGuidePcmPreserved=True,
 finalTimingApproved=False,preparedAt=datetime.now(timezone.utc).isoformat())
dest=BASE/'guide12-room-tts-request-v2.json';assert not dest.exists()
dest.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(guides=1,originalPcmPreserved=True,otherSevenPcmPreserved=True,request=rel(dest))))
