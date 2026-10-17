"""One selected-video pipeline stage; no scheduler or next-video advance."""
from pathlib import Path
import json,subprocess,sys,time,datetime,os
R=Path(__file__).resolve().parents[4];L=R/'projects/making-game-sequels/production/local/reference-preserving-v2';stateFile=L/'voice-review-execution.json';resume=L/'tts-scene07-correction-resume.json'
def selected():
 c=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))
 assert c['selectedVideo']=='making-game-sequels' and c['newProductionAuthorization']['fullProductionAuthorized'],'Scope changed; do not start another stage'
def save(status,**kw):stateFile.write_text(json.dumps(dict(pid=os.getpid(),status=status,updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw),indent=2)+'\n')
save('waiting-current-tts-batch');selected()
while True:
 selected()
 if resume.exists():
  s=json.loads(resume.read_text(encoding='utf8'))
  if s['status']=='failed':raise RuntimeError('Current TTS failed; preserve and inspect its log')
  if s['status']=='complete':break
 time.sleep(5)
selected();save('whole-current-narration-asr-running',device='cpu')
with (L/'voice-review.log').open('w',encoding='utf8') as f:
 result=subprocess.run([sys.executable,'-X','utf8','qwen3-tts/review_project_narration.py','--project','making-game-sequels','--manifest','projects/making-game-sequels/production/reference-preserving-v2/tts-manifest.json','--device','cpu'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
save('asr-ready-for-direct-full-text-review' if result.returncode==0 else 'failed',returncode=result.returncode);sys.exit(result.returncode)
