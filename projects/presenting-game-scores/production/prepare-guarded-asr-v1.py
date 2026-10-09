from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,py_compile
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
reference=ROOT/'projects/similar-game-design/production/review-current-voice-v1.py'
text=reference.read_text('utf-8-sig')
assert "len(tts['results']) == 13" in text and "== 51" in text
text=text.replace('similar-game-design','presenting-game-scores').replace("len(tts['results']) == 13","len(tts['results']) == 10")
text=text.replace("len(script['scenes']) == 13","len(script['scenes']) == 10").replace("sum(len(x['lines']) for x in script['scenes']) == 51","sum(len(x['lines']) for x in script['scenes']) == 30")
text=text.replace("len(plan['contexts']) >= 13","len(plan['contexts']) >= 10").replace('current-thirteen-voice','current-ten-voice')
target=BASE/'review-current-voice-v1.py'
assert not target.exists(),'Preserve already-prepared or running own worker'
target.write_text(text,'utf-8')
py_compile.compile(str(target),doraise=True)
proof=dict(schemaVersion=1,slug='presenting-game-scores',preparedAt=datetime.now(timezone.utc).isoformat(),
 worker=target.relative_to(ROOT).as_posix(),workerSha256=hashlib.sha256(target.read_bytes()).hexdigest(),
 sourceReusableWorker=reference.relative_to(ROOT).as_posix(),sourceSha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
 plannedWholeScenes=10,plannedMinimumIndependentCompleteContexts=10,expectedScriptIsRecognizerPrompt=False,cpuThreads=2,gpu=0,
 refusesWithoutSuccessfulObservedTtsExit=True,refusesWithoutOwnedResearchRestorationProof=True,
 refusesStaleProtectedContent=True,refusesOldOrExistingAsrExecution=True,
 requiresFreshResourceEvidence=True,contextsRequireWholeTextDirectReviewAndExactPcmBoundaryPlan=True,
 executed=False,modelLoaded=False,asrApproved=False,finalMixedAsrApproved=False,humanWholeListening='pending',humanPronunciation='pending')
(BASE/'prepared-current-asr-v1.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Prepared guarded CPU2 whole/context recognizer; syntax checked, not executed or approved.')
