"""Recover an environment-only failure before inference; preserve v1 and all PCM."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failed=read(BASE/'observation-guides-whole-asr-execution-v1.json')
assert failed['exitCode']==1 and failed['completed']==0 and 'No module named' in failed['error'] and 'transformers' in failed['error']
assert not list((BASE/'observation-guides-whole-asr-v1').iterdir()), 'Never discard produced ASR results'
target=BASE/'review-observation-guides-whole-v2.py';assert not target.exists()
code=(BASE/'review-observation-guides-whole-v1.py').read_text('utf-8')
code=code.replace('observation-guides-whole-asr-execution-v1','observation-guides-whole-asr-execution-v2').replace('observation-guides-whole-asr-session-v1','observation-guides-whole-asr-session-v2').replace('observation-guides-whole-asr-v1','observation-guides-whole-asr-v2')
code=code.replace("try:\n    checkpoint()\n    import torch", "try:\n    state['historicalPreInferenceFailure']='projects/familiar-game-rules/production/observation-guides-whole-asr-execution-v1.json'\n    state['newEnvironmentUsesExistingQwenVenvWrapper']=True\n    checkpoint()\n    import torch")
target.write_text(code,encoding='utf-8')
evidence=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),failure='general conda environment missing transformers before any recognition',
 failedExecution='projects/familiar-game-rules/production/observation-guides-whole-asr-execution-v1.json',failedExecutionSha256=sha(BASE/'observation-guides-whole-asr-execution-v1.json'),
 completedRecognitionResults=0,allPCMUnchanged=True,failedDirectoryPreserved=True,recovery='Existing qwen3-tts/.venv/Scripts/python.exe wrapper used successfully by previous ASR; no installation or resynthesis',
 newWorker='projects/familiar-game-rules/production/review-observation-guides-whole-v2.py',newWorkerSha256=sha(target),executed=False)
(BASE/'observation-guides-whole-asr-recovery-v2.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(evidence,ensure_ascii=False))
