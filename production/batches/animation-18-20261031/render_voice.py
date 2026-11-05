"""Generate and read back one explicitly bound animation episode, waiting for a free GPU slot."""
from pathlib import Path
import sys,subprocess,json,time,msvcrt,hashlib
from screen_share import HOLD,ShareState
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
completed=l/'voice/narration.timing.json'
share=ShareState()
voice_runner=[sys.executable,'-X','utf8','-u',str(B/'screen_share.py')]

def review_matches():
 if not completed.exists() or not report.exists():return False
 data=read(report)
 if not data['complete']:return False
 for row in data['scenes']:
  wave=l/'voice/chunks'/(row['scene']+'-scene.wav')
  if not wave.is_file() or hashlib.sha256(wave.read_bytes()).hexdigest()!=row['audio_sha256']:
   return False
 return True

def problems():
 bad=[]
 for row in read(report)['scenes']:
  evidence=row['acousticChecks']
  if row['similarity']<.90 or evidence['duration']>=163.5 or (not evidence['endingHeuristicPassed'] and evidence['tailRatio']>.12):
   bad.append(row['scene'])
 return bad

def recognize():
 while True:
  with (l/'asr.log').open('wb') as log:
   rc=subprocess.call([*voice_runner,'qwen3-tts/review_project_narration.py',*args,'--device','cuda'],cwd=R,stdout=log,stderr=log)
  if rc==HOLD:continue
  if rc:raise RuntimeError(str(l/'asr.log'))
  if not review_matches():raise ValueError(f'{ep}: the ASR did not review the current scene files')
  return

def synthesize(scenes,limit):
 while True:
  if not share.clear() or (R/'shared/output/GPU_HANDOFF.json').exists():time.sleep(5);continue
  free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(','))
  if free<8192 or util>=15:time.sleep(8);continue
  voice_entry=str(B/'series_voice.py') if int(ep[1:])>=9 else 'qwen3-tts/render_narration.py'
  flags=[]
  if int(ep[1:])>=9:
   flags=['--max-group',str(limit)]
   if scenes:flags.extend(['--repair-scenes',','.join(scenes)])
  elif scenes:
   flags=['--force-scenes',','.join(scenes)]
  with (l/'tts.log').open('ab') as log:
   start=log.tell()
   rc=subprocess.call([*voice_runner,voice_entry,*args,*flags],cwd=R,stdout=log,stderr=log)
  if rc==HOLD:continue
  if rc:
   with (l/'tts.log').open('rb') as log:
    log.seek(start);message=log.read().decode('utf8',errors='replace')
   if any(t in message for t in ['Unregistered GPU','GPU capacity','GPU is reserved','GPU handoff']):time.sleep(15);continue
   if 'Generation limit in' in message and limit>95:
    limit=max(95,limit-65);continue
   raise RuntimeError(message[-1300:])
  return

if not completed.exists():synthesize([],210)
if not review_matches():recognize()
for limit in (145,95):
 bad=problems()
 if not bad:break
 print('Re-record only these scenes with shorter sentence groups:',bad,flush=True)
 synthesize(bad,limit)
 recognize()
if problems():raise ValueError(f'{ep}: inspect remaining voice scenes {problems()}')
