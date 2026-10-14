"""Preserve pre-worker v1 failure; allow only the actual identical-argv Python launcher."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,py_compile
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
record=O/'current34-mix-premodel-launcher-failure-v1.json'
assert not record.exists() and not (O/'current34-mix-execution-v1.json').exists()
assert not (ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-mix-v1').exists()
record.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),actualOuterExitCode=1,initialChunk='8287e1',sessionId=None,failedScript='production/batches/cross-game-example-coverage-review/build-orientation-current34-mix-v1.py',scriptSha256=hashlib.sha256((B/'build-orientation-current34-mix-v1.py').read_bytes()).hexdigest(),failure='Duplicate guard treated the identical-argv approved Python launcher as another heavy worker.',newWorkerStateCreated=False,newPcmCreated=False,newMediaCreated=False,modelLoaded=False,newGpuJobs=0,researchManipulations=0),indent=2)+'\n','utf-8')
p=B/'build-orientation-current34-mix-v1.py';q=B/'build-orientation-current34-mix-v2.py';assert not q.exists()
t=p.read_text('utf-8-sig').replace('current34-mix-v1','current34-mix-v2').replace('current34-mix-execution-v1','current34-mix-execution-v2')
t=t.replace(" for p in psutil.process_iter(['pid','name','cmdline']):", " launcher=psutil.Process().parent();same_launcher=launcher is not None and launcher.name().lower()=='python.exe' and launcher.cmdline()[1:]==psutil.Process().cmdline()[1:]\n allowed_launcher_pid=launcher.pid if same_launcher else None\n for p in psutil.process_iter(['pid','name','cmdline']):")
t=t.replace("assert p.pid==os.getpid() or (p.info['name']", "assert p.pid in (os.getpid(),allowed_launcher_pid) or (p.info['name']")
assert 'allowed_launcher_pid' in t
q.write_text(t,'utf-8');py_compile.compile(str(q),doraise=True)
print('Prepared v2 exact Python-launcher identity guard; v1 pre-state exit1 preserved.')
