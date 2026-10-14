"""Preserve pre-model setup failure; prepare corrected ASR references without synthesis."""
from pathlib import Path
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
assert not (O/'cross-game-whole-asr-execution-v1.json').exists()
assert not (O/'cross-game-whole-asr-v1').exists()
out=O/'cross-game-voice-postexit-setup-failure-v1.json';assert not out.exists()
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),voiceOuterSession=5900,voiceOuterExitCode=0,voiceCompletion='9a347c',initialVerifier=dict(actualCompletion='f7eaf3',exitCode=1,error="Completed research status has no owner_pid; writer clears owner at completion."),dependentReadOnlyObserver=dict(actualCompletion='aa844e',exitCode=1,resourceCreated=False),dependentAsrPreflight=dict(actualCompletion='5dba03',exitCode=1,reason='Required resource not created after verifier error.',modelLoaded=False,stateCreated=False,recognizedTexts=0),correction='814eb1 verifier exit0 explicitly checks historical completed owner exact creation identity and unchanged completion status;7bcb51 fresh CPU resource exit0.',correctedAsrVersion=2,voiceResynthesized=False,researchOrForeignControlChanges=0),ensure_ascii=False,indent=2)+'\n','utf-8')
for old,new in [('review-orientation-cross-game-voice-v1.py','review-orientation-cross-game-voice-v2.py'),('register-orientation-cross-game-asr-v1.py','register-orientation-cross-game-asr-v2.py'),('record-orientation-cross-game-asr-exit-v1.py','record-orientation-cross-game-asr-exit-v2.py')]:
 src=(B/old).read_text('utf-8').replace('review-orientation-cross-game-voice-v1.py','review-orientation-cross-game-voice-v2.py').replace('-asr-execution-v1.json','-asr-execution-v2.json').replace('-asr-v1','-asr-v2').replace('cross-game-independent-context-plan-v1.json','cross-game-independent-context-plan-v2.json').replace('orientation/cross-game-contexts-v1','orientation/cross-game-contexts-v2')
 p=B/new;assert not p.exists();p.write_text(src,'utf-8');compile(src,str(p),'exec')
print('Prepared corrected CPU2/GPU0 ASRv2; prior pre-model failure preserved, models0.')
