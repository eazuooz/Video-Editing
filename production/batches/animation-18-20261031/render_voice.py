"""Generate and read back one explicitly bound animation episode, waiting for a free GPU slot."""
from pathlib import Path
import sys,subprocess,json,time,msvcrt
B=Path(__file__).resolve().parent;R=B.parents[2];ep=sys.argv[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
batch=read(B/'batch.json');assert ep in batch['episodeIds'] and batch['ttsAuthorized']
row=next(x for x in read(R/'shared/publishing/video-worklist.json')['rows'] if x['id']==ep)
p=R/'projects'/row['slug'];h=p/'production/series-v1';l=p/'production/local/series-v1';m=h/'tts-manifest.json'
assert read(h/'source-selection.json')['episode']==ep and (h/'production-binding.json').is_file()
args=['--project',row['slug'],'--manifest',m.relative_to(R).as_posix()]
report=l/'voice/narration.asr-review.json'
# Preparation and assembly can arrive at the same selected voice work concurrently.
# Windows releases this byte-range lock even if a process exits unexpectedly.
lease=(l/'voice-job.lock').open('a+b')
if lease.seek(0,2)==0:lease.write(b'0');lease.flush()
while True:
 try:
  lease.seek(0);msvcrt.locking(lease.fileno(),msvcrt.LK_NBLCK,1);break
 except OSError:time.sleep(7)
if report.exists() and read(report)['complete']:sys.exit(0)
completed=l/'voice/narration.timing.json'
while not completed.exists():
 if (R/'shared/output/GPU_HANDOFF.json').exists():time.sleep(15);continue
 free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(','))
 if free<8192 or util>=15:time.sleep(12);continue
 with (l/'tts.log').open('wb') as log:
  rc=subprocess.call([sys.executable,'-X','utf8','-u','qwen3-tts/render_narration.py',*args],cwd=R,stdout=log,stderr=log)
 if rc:
  message=(l/'tts.log').read_text('utf-8',errors='replace')
  if any(t in message for t in ['Unregistered GPU','GPU capacity','GPU is reserved','GPU handoff']):time.sleep(15);continue
  raise RuntimeError(message[-1300:])
with (l/'asr.log').open('wb') as log:
 subprocess.run([sys.executable,'-X','utf8','-u','qwen3-tts/review_project_narration.py',*args,'--device','cuda'],cwd=R,stdout=log,stderr=log,check=True)
assert read(report)['complete']
