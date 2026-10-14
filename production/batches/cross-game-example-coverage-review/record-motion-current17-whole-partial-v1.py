"""Record the first eight full expected/recognized texts already directly compared."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'current17-mixed-whole-partial-direct-review-v1.json';assert not out.exists()
notes={
 '00a':'Full overview question, ordered examples, benefit and first-example bridge recovered; punctuation/spacing alternatives only.',
 '01':'Complete sequence recovered. A모드 versus 에임 모드, 남아있는데 versus 남아 있는데, 이동에 versus 이동이 are recognition alternatives to compare in independent paragraphs;2022 numeric transcription preserves the year. No acoustic/human pronunciation conclusion.',
 '02':'All four full paragraphs recovered, including theory limitations and separate design roles; punctuation/spacing alternatives only.',
 '03':'All six full paragraphs recovered; independent aiming, edge-induced view changes, task continuity and comfort limitation preserved.',
 '04':'All four full paragraphs recovered; input/aim/added shake separation and adjustable options remain distinct.',
 '05':'All six full paragraphs recovered. Final 아니므로 recognized as 아님으로; independent final paragraph must be compared. No missing whole paragraph or duplicated whole paragraph observed.',
 '06':'All four paragraph sequences present. Whole recognition substitutes 도식의→도시계, 제안→제한 and 앞의→앞에 in paragraph3; hold that phrase for independent current paragraph recovery. No human acoustic failure conclusion and no final approval.',
 '06b':'Both complete causal-bridge paragraphs recovered; target reacquisition and separate trailer excerpts retained.'}
rows=[]
for sid,note in notes.items():
 p=R/f'current17-mixed-whole-asr-v1/{sid}.json';v=read(p)
 assert v['id']==sid and v['expectedKo'] and v['text'] and v['exactSourceStereoPcmBytesMatched']
 rows.append(dict(scene=sid,resultPath=p.relative_to(ROOT).as_posix(),resultSha256=sha(p),allExpectedAndRecognizedWholeTextDirectlyRead=True,observations=note,independentCurrentParagraphReviewPending=True,currentMixedApproval=False))
mix=read(R/'current-mix-execution-v1.json')
out.write_text(json.dumps(dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),directlyComparedWholeCount=8,requiredWholeCount=17,results=rows,mixAacSha256=mix['mixAacSha256'],decodedAacSha256=mix['decodedAacSha256'],all17WholeTextsDirectlyCompared=False,all81IndependentContextsDirectlyCompared=False,currentMixedAudioApproved=False,humanListeningApproved=False,humanPronunciationApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(directWholeTextComparisons=8,completeWholeReview=False,currentAudioApproved=False)))
