"""CPU-only current-hash read-back evidence; never listening approval."""
import hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
state_path=BASE/'action-asr-execution.json'
log_path=BASE/'action-asr.log'
now=lambda:datetime.now(timezone.utc).isoformat()
state={'pid':os.getpid(),'startedAt':now(),'status':'running','device':'cpu','threads':2,'scenes':['02','04','06','08','10','12'],'log':log_path.relative_to(ROOT).as_posix(),'evidenceOnly':True,'humanListening':'pending'}
def save():
    state['updatedAt']=now()
    state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save()
command=[sys.executable,'qwen3-tts/review_project_narration.py','--project','game-reward-planning','--device','cpu','--scenes',','.join(state['scenes']),'--watch']
env=os.environ.copy();env.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2')
with log_path.open('w',encoding='utf-8') as log:
    worker=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    state.update(workerPid=worker.pid,command=command);save()
    code=worker.wait()
state.update(status='finished-evidence-awaiting-direct-review' if code==0 else 'failed',exitCode=code,endedAt=now());save()
print(json.dumps(state,ensure_ascii=False),flush=True)
sys.exit(code)
