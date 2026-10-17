"""Stop only this task's old CPU script at a completed scene, then resume fresh text."""
from pathlib import Path
import sys,time,json,subprocess,datetime
import psutil
R=Path(__file__).resolve().parents[4];L=R/'projects/making-game-sequels/production/local/reference-preserving-v2';log=L/'tts-cpu.log';pid=int(sys.argv[1]);receipt=L/'tts-scene07-correction-resume.json'
target=psutil.Process(pid);cmd=target.cmdline();assert 'qwen3-tts/render_narration.py' in ' '.join(cmd) and 'making-game-sequels' in cmd and 'cpu' in cmd
started=target.create_time()
while target.is_running():
 assert target.create_time()==started,'PID changed; do not terminate it'
 text=log.read_text(encoding='utf8',errors='replace')
 if 'Rendered 06-scene' in text:
  target.terminate();target.wait(timeout=30);break
 time.sleep(2)
assert not target.is_running()
state={'stoppedPid':pid,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'boundary':'scene06 complete; before scene07 output','foreignProcessesChanged':False,'sameModelAndReference':True,'status':'resuming-corrected-scene07'}
receipt.write_text(json.dumps(state,indent=2)+'\n')
with (L/'tts-cpu-corrected.log').open('w',encoding='utf8') as out:
 result=subprocess.run([sys.executable,'-X','utf8','qwen3-tts/render_narration.py','--project','making-game-sequels','--manifest','projects/making-game-sequels/production/reference-preserving-v2/tts-manifest.json','--batch-size','1','--device','cpu'],cwd=R,stdout=out,stderr=subprocess.STDOUT)
state.update(status='complete' if result.returncode==0 else 'failed',returncode=result.returncode,finishedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());receipt.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state));sys.exit(result.returncode)
