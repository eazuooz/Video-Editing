"""Seal the first eleven complete expected/current texts directly read in this turn."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=O/'current34-mixed-whole-partial-direct-review-v1.json';assert not out.exists()
ids=['01','01b','02a','02','03','03b','04','05','06a','06','07'];rows=[]
observations={
 '01':'All four complete question/benefit/order/results sentences recovered; no content omission/repetition in this recognition.',
 '01b':'Full example-order sentence recovered; expected 배치에 recognized 배치의. Independent current paragraph required; no phonetic approval.',
 '02a':'All four complete prerequisite/torso-screen/red-screen-change-limit sentences recovered, including final coordinate disclaimer; added silent observation produced no extra recognized sentence.',
 '02':'All six complete sentences, position/attitude/one-vector limitation and diagram transition recovered. A word-ending timestamp warning requires current independent complete end review; no automatic cue timing approval.',
 '03':'All six sentence contexts present. Expected 각변위 recognized 각변인; independent paragraph05 recovery required. 3D/two angles/three rotational freedoms otherwise preserved.',
 '03b':'All five complete game-prerequisite/curve/jump/inversion/landing/forward-plus-up comparison sentences recovered across inserted observation gap.',
 '04':'All six complete local/world basis and right-hand sentences present; spoken x/y/z and numbers normalized to symbols/digits. No engine-axis measurement claim added.',
 '05':'All six body/screen/building/camera/axis-definition/disclaimer sentences recovered.',
 '06a':'All three whole prerequisite and basis-table contexts recovered. 방의 기준에서 recognized 방에 기준해서; independent current paragraph03 required for word/particle comparison.',
 '06':'All six convention/column/transposition/input-output contexts present. Expected 책은 recognized 최근 in paragraph04; independent complete paragraph04 required. R/x/y/z normalized to symbols.',
 '07':'All six complete rotation/numeric-column/weighted-sum sentences recovered; result (-1,2,0) and negative second column retained. Numerals/symbols normalized.'}
for sid in ids:
 p=O/f'current34-mixed-whole-asr-v1/{sid}.json';r=read(p)
 assert r['id']==sid and r['expectedKo'] and r['text'] and not r['expectedWasRecognizerPrompt']
 rows.append(dict(id=sid,result=p.relative_to(ROOT).as_posix(),resultSha256=sha(p),expectedWhole=r['expectedKo'],recognizedWhole=r['text'],wholeTextsDirectlyCompared=True,observation=observations[sid],currentIndependentReviewRequired=True,humanListeningApproved=False,humanPronunciationApproved=False))
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),currentMixExecution='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/current34-mix-execution-v2.json',currentMixExecutionSha256=sha(O/'current34-mix-execution-v2.json'),directReadToolChunk='69a856',rows=rows,reviewedCompleteScenes=11,all34WholeTextsDirectlyCompared=False,currentMixedAudioApproved=False,independent180Pending=True,modelRerun=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print('Sealed all11 complete expected/current texts; four recognition alternatives remain for independent current contexts.')
