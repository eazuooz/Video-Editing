"""Finish the finite approved speech set, honoring explicit screen-share GPU gate.

This is a job coordinator, not a scheduled/next-video automation. It never
stops another task or infers human permission from a low GPU utilization.
"""
from pathlib import Path
import json,os,sys,time,subprocess,hashlib
import psutil
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';PY=R/'qwen3-tts/.venv/Scripts/python.exe'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
def status(**kw):
 p=L/'tts-coordinator-state.json';j=read(p)if p.exists()else{};j.update(updatedAt=time.time(),**kw);save(p,j)
def allowed_gpu():return read(H/'gpu-authorization.json')['gpuTtsAuthorizedNow']is True
def owned_process(record):
 try:
  p=psutil.Process(record['pid'])
  if abs(p.create_time()-record['created'])>.01:return None
  cmd=' '.join(p.cmdline())
  assert 'contrast-v5' in cmd and ('run_reviewed_cpu_tts.py'in cmd or 'render_narration.py'in cmd),'Foreign process must never be stopped'
  return p
 except(psutil.NoSuchProcess,psutil.ZombieProcess):return None
def protect_chunks():
 # Preserve stable existing takes, including any unaccepted best-of-three take.
 folder=L/'voice-reviewed/chunks';backup=L/'voice-reviewed/checkpoint-before-device-change';backup.mkdir(parents=True,exist_ok=True)
 for f in folder.glob('*.wav'):
  raw=f.read_bytes();name=f.stem+'.'+hashlib.sha256(raw).hexdigest()[:12]+'.wav';dest=backup/name
  if not dest.exists():dest.write_bytes(raw)
def wait_initial(record):
 switched=False
 while(p:=owned_process(record))is not None:
  if allowed_gpu():
   protect_chunks();status(stage='explicit-gpu-release-switch',stoppedOwnedCpu=record)
   p.terminate();p.wait(timeout=20);switched=True;break
  time.sleep(5)
 return switched
def invoke(device,logname):
 log=L/logname
 cmd=[str(PY),'-X','utf8']+([str(H/'run_reviewed_cpu_tts.py')]if device=='cpu'else[str(R/'qwen3-tts/render_narration.py'),'--project','animation-contrast-v5','--manifest',str((H/'narration/released-tts-manifest.json').relative_to(R)),'--batch-size','1','--device','cuda:0'])
 with log.open('ab')as stream:
  child=subprocess.Popen(cmd,cwd=R,stdout=stream,stderr=stream,creationflags=subprocess.CREATE_NO_WINDOW)
  record={'pid':child.pid,'created':psutil.Process(child.pid).create_time()};status(stage='final-speech-pass',device=device,child=record,log=str(log))
  while child.poll()is None:
   if device=='cpu'and allowed_gpu():
    protect_chunks();p=owned_process(record)
    if p:
     for x in p.children(recursive=True):
      if 'contrast-v5' in ' '.join(x.cmdline()):x.terminate()
     p.terminate();child.wait(timeout=20)
    return invoke('cuda:0','tts-reviewed-final-gpu.log')
   time.sleep(5)
  return child.returncode
def main():
 c=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert c['fullLocalProductionAuthorized']and c['candidateUserApproval']['text']=='이 목록으로 진행'
 initial=read(L/'tts-initial-process.json');status(stage='initial-cpu-pass-running',initial=initial,gpuGate='Wait for explicit end-of-sharing confirmation')
 wait_initial(initial)
 snap=L/'tts-input-snapshots';snap.mkdir(exist_ok=True)
 for name in ['released-tts.ko.json','released-tts-map.json','released-tts-manifest.json']:
  f=H/'narration'/name;dest=snap/(hashlib.sha256(f.read_bytes()).hexdigest()[:12]+'-'+name)
  if not dest.exists():dest.write_bytes(f.read_bytes())
 subprocess.run([sys.executable,str(H/'prepare_reviewed_tts.py')],cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 rc=invoke('cuda:0'if allowed_gpu()else'cpu','tts-reviewed-final.log')
 if rc and allowed_gpu():rc=invoke('cpu','tts-reviewed-final-cpu-fallback.log')
 entries=read(H/'narration/released-tts-map.json')['entries'];ready=[];missing=[]
 for row in entries:
  f=L/'voice-reviewed/chunks'/(row['key']+'-scene.wav')
  if f.is_file():ready.append({'key':row['key'],'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
  else:missing.append(row['key'])
 status(stage='speech-generated-needs-asr-and-ending-review'if rc==0 and not missing else'speech-pass-needs-attention',returncode=rc,entries=ready,missing=missing,sourceParagraphs=len(entries),actualHumanListening=False)
if __name__=='__main__':main()
