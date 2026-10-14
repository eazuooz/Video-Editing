"""Prepare only the single guide candidate plan and exact fresh CPU observer."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tts=read(O/'narration-07b-guide-repair-execution-v1.json');proof=read(O/'07b-guide-repair-voice-closure-verification-v1.json')
assert proof['restorationVerified'] and tts['actualOuterExitCode']==0 and len(tts['results'])==1
row=tts['results'][0];assert sha(ROOT/row['path'])==row['sha256']
ko=read(O/'script/07b-guide-repair-v1.ko.json')['scenes'][0]
plan=O/'guide-candidate-voice-review-plan-v1.json';assert not plan.exists()
plan.write_text(json.dumps(dict(inputs=[dict(id='07r-whole',path=row['path'],sha256=row['sha256'],expectedKo=ko['lines'])],candidateAdopted=False,humanListeningApproved=False,finalMixedApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
src=(B/'observe-orientation-cross-game-cpu-resource-v1.py').read_text('utf-8')
src=src.replace("resource-before-cross-game-CPU-v{a.version}","resource-before-guide-CPU-v{a.version}").replace('narration-cross-game-repair-execution-v1.json','narration-07b-guide-repair-execution-v1.json').replace('cross-game-repair-voice-closure-verification-v1.json','07b-guide-repair-voice-closure-verification-v1.json')
dst=B/'observe-orientation-guide-cpu-resource-v1.py';assert not dst.exists();dst.write_text(src,'utf-8')
print(json.dumps(dict(preparedPlan=plan.relative_to(ROOT).as_posix(),observer=dst.relative_to(ROOT).as_posix(),newModelJobs=0)))
