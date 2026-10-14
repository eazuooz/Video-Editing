"""Prepare a new one-source version without reusing the three-source request."""
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
failure=V/'timber-stream-preparation-shell-failure-v1.json'
assert not failure.exists()
failure.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
    actualShellChunk='65e70e',actualExitCode=1,phase='PowerShell argument parsing before preparer/observer/acquisition',
    actualError="Nested quote ended the Python -c argument; state[results] was parsed as a shell command.",
    secondObservedChunk='ca3876',secondActualExitCode=1,secondError='New observer file did not exist because preparation never completed.',
    newObserverStarted=False,newAcquisitionStarted=False,newMediaProduced=False,
    existingThreeSourcesAnd64BoardsPreserved=True,repair='Saved Python preparer file; structured replacements avoid nested shell quoting.'),
    ensure_ascii=False,indent=2)+'\n','utf8')
src=(B/'acquire-hierarchical-official-sources-v1.py').read_text('utf8')
for old,new in [('source-research-v1','source-research-v2'),
    ('source-acquisition-execution-v1','source-acquisition-execution-v2'),
    ('source-acquisition-logs-v1','source-acquisition-logs-v2'),
    ('source-cpu-resource-verification-v1','source-cpu-resource-verification-v2'),
    ('acquire-hierarchical-official-sources-v1.py','acquire-hierarchical-official-sources-v2.py'),
    ('len(sources) == 3','len(sources) == 1'),('wholeDecodes=3','wholeDecodes=1')]:
    assert old in src,old
    src=src.replace(old,new)
p=B/'acquire-hierarchical-official-sources-v2.py';assert not p.exists();p.write_text(src,'utf8')
obs=(B/'observe-hierarchical-source-cpu-resource-v1.py').read_text('utf8')
obs=obs.replace('source-cpu-resource-verification-v1','source-cpu-resource-verification-v2')
obs=obs.replace('source-resource-v1.cim.json','source-resource-v2.cim.json')
obs=obs.replace('one sequential candidate-source acquisition;CPU2/GPU0;no model/TTS/render',
    'one additional clearer Timberborn developer stream;CPU2/GPU0;no model/TTS/render')
p=B/'observe-hierarchical-source-cpu-resource-v2.py';assert not p.exists();p.write_text(obs,'utf8')
rec=(B/'record-hierarchical-source-worker-v1.py').read_text('utf8')
rec=rec.replace('source-acquisition-execution-v1','source-acquisition-execution-v2')
assert "len(state['results'])==3" in rec
rec=rec.replace("len(state['results'])==3","len(state['results'])==1")
rec=rec.replace('All source acquisition/decode completed.','Additional official Timberborn stream acquisition/decode completed.')
rec=rec.replace('inspect the three new candidate sources','inspect only this additional candidate source')
rec=rec.replace('sourceExecution=state_path.relative_to(ROOT).as_posix()',
    'additionalSourceExecution=state_path.relative_to(ROOT).as_posix()')
rec=rec.replace('actualSourceOuterSession=a.session,actualSourceOuterExitCode=a.outer_exit',
    'additionalSourceOuterSession=a.session,additionalSourceOuterExitCode=a.outer_exit')
rec=rec.replace("['sourceAcquisitionActualSession']","['additionalSourceAcquisitionActualSession']")
p=B/'record-hierarchical-source-worker-v2.py';assert not p.exists();p.write_text(rec,'utf8')
for p in [B/'acquire-hierarchical-official-sources-v2.py',B/'observe-hierarchical-source-cpu-resource-v2.py',B/'record-hierarchical-source-worker-v2.py']:
    compile(p.read_text('utf8'),str(p),'exec')
print('New one-source acquisition/observer/recorder V2 prepared; no worker started by this preparer.')
