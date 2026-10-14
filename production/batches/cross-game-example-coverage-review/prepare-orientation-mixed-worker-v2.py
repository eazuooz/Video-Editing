"""Preserve pre-state shell false positive; restrict duplicate scan to heavy runtimes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
assert not (O/'current34-mixed-detailed-render-execution-v1.json').exists()
assert not (ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-mixed-detailed-v1').exists()
old=B/'render-orientation-mixed-detailed-v1.py';source=old.read_text('utf-8')
needle="if 'cross-game-example-coverage-review' in cmd and any(k in cmd"
assert source.count(needle)==1
source=source.replace(needle,"if (p.info['name'] or '').lower() in ['python.exe','ffmpeg.exe','node.exe'] and 'cross-game-example-coverage-review' in cmd and any(k in cmd")
source=source.replace('current34-mixed-detailed-v1','current34-mixed-detailed-v2').replace('current34-mixed-detailed-render-execution-v1','current34-mixed-detailed-render-execution-v2')
out=B/'render-orientation-mixed-detailed-v2.py';assert not out.exists();out.write_text(source,'utf-8')
record=B/'record-orientation-mixed-detailed-worker-v1.py';rout=B/'record-orientation-mixed-detailed-worker-v2.py';assert not rout.exists();rout.write_text(record.read_text('utf-8').replace('current34-mixed-detailed-render-execution-v1','current34-mixed-detailed-render-execution-v2'),'utf-8')
proof=json.loads((O/'narration-07b-guide-repair-execution-v1.json').read_text('utf-8-sig'))
for x in proof['protectedInputs']+proof['results']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
p=O/'current34-mixed-detailed-prestate-failure-v1.json';assert not p.exists()
p.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),actualCompletion='509222',actualOuterExitCode=1,actualSession=None,error='assert not own before state/output creation',cause='Scanner matched the PowerShell execution command because it had no runtime-name filter. Fresh resource32 had zero actual owned heavy runtimes.',stateCreated=False,outputDirectoryCreated=False,newEncodedMedia=0,newTts=0,newAsr=0,newMix=0,protected79AndCandidateUnchanged=True,oldWrapperPreserved=old.relative_to(ROOT).as_posix(),newWrapperPrepared=out.relative_to(ROOT).as_posix(),correction='Require python.exe/ffmpeg.exe/node.exe in duplicate-heavy scan, retaining exact parent Python launcher exclusion and current resource/duplicate/protected gates.'),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preStateFailurePreserved=True,preparedV2=True,newMedia=0)))
