"""Authorized local completion only; no publication or next-video actions."""
from pathlib import Path
import time,subprocess,sys,json,atexit,uuid
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local';Q=L/'qa';Q.mkdir(exist_ok=True)
PY=R/'qwen3-tts/.venv/Scripts/python.exe'
def run(args):
 result=subprocess.run([str(x) for x in args],cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
 print(result.stdout,result.stderr,flush=True)
 result.check_returncode()
complete=L/'narration/ai-2d-game-assets.timing.json'
while not complete.exists():time.sleep(10)
while (R/'shared/output/GPU_HANDOFF.json').exists():time.sleep(5)
if not (P/'production/audio-qa.json').exists():run([PY,'-X','utf8',P/'production/build_audio.py'])
else:
 import hashlib
 qa=json.loads((P/'production/audio-qa.json').read_text('utf-8'))
 assert qa['mixSha256']==hashlib.file_digest((L/'final-mix.wav').open('rb'),'sha256').hexdigest()
 print('Reuse hash-verified current audio mix',flush=True)
# The model is the same cached primary Whisper used to inspect supplied sources.
# Two distinct current-audio readbacks: narration for timing, final mix for QA.
sys.path.insert(0,str(R/'qwen3-tts'))
from gpu_handoff_guard import schedule_gpu_handoff
while True:
 try:schedule_gpu_handoff('ai-2d-game-assets','cuda:0',False,8192);break
 except SystemExit as err:
  if 'Unregistered GPU activity' in str(err):
   import psutil
   free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()[0].split(','))
   known=any(p.info['name']=='LunaDefense.exe' for p in psutil.process_iter(['name']))
   # 2026-11-08 readback: LunaDefense has exited; the only CUDA Python
   # context is our completed Comfy8191 server, with an empty queue.
   owned_comfy=any(p.pid==84768 and '8191' in ' '.join(p.info.get('cmdline') or []) for p in psutil.process_iter(['cmdline']))
   lease=R/'shared/output/GPU_HANDOFF.json'
   if (known or owned_comfy) and free>=10000 and util<=25 and not lease.exists():
    me=psutil.Process();token=str(uuid.uuid4());record={'schemaVersion':1,'token':token,'project':'ai-2d-game-assets','state':'tts_running','queueDir':None,'idleGpu':False,'coordinator':{'pid':me.pid,'createTime':me.create_time()},'work':'Whisper current-narration and final-mix QA; same inspected low-load admission','gpuBefore':{'freeMiB':free,'utilization':util}}
    try:
     with lease.open('x',encoding='utf-8') as f:json.dump(record,f)
    except FileExistsError:continue
    def release():
     if lease.exists() and json.loads(lease.read_text('utf-8')).get('token')==token:lease.unlink()
    atexit.register(release);break
  print(err,flush=True);time.sleep(10)
for audio,out,mode in [(L/'narration-aligned.wav',Q/'narration.txt','word'),(L/'final-mix.wav',Q/'mix.txt','segment')]:
 if out.exists() and out.with_suffix('.timestamps.json').exists():continue
 with (Q/(out.stem+'-execution.log')).open('w',encoding='utf-8') as log:
  subprocess.run([str(PY),'-X','utf8','-u',str(R/'qwen3-tts/transcribe_reference.py'),str(audio),'--output',str(out),'--device','cuda','--timestamps',mode],cwd=R,check=True,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 print('ASR complete',out.name,flush=True)
run([PY,'-X','utf8',P/'production/build_captions.py'])
print('Captions and current-audio QA evidence ready; awaiting direct review before final assembly.',flush=True)
