"""Offscreen MRQ capture of an already saved owned sequence; serialized GPU."""
from pathlib import Path
import sys,json,subprocess,time,hashlib,datetime,uuid,atexit,psutil
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3'
sys.path.insert(0,str(R/'qwen3-tts'))
from gpu_handoff_guard import schedule_gpu_handoff
def main():
 cid=sys.argv[1];receipt=L/'unreal'/f'{cid}-build.json';j=json.loads(receipt.read_text())
 auth=json.loads((H/'authorization.json').read_text());control=R/'shared/publishing/video-production-control.json'
 assert auth['renderAuthorized'] and json.loads(control.read_text(encoding='utf-8-sig'))['finiteBatchAuthorizations']['animation-18-20261031']['renderAuthorized']
 dest=L/'unreal/renders'/j.get('renderFolder',cid)
 if dest.exists() and len(list(dest.glob('*.png')))==j['frames']:print('Frames already complete',cid);return
 lease=R/'shared/output/GPU_HANDOFF.json';token=str(uuid.uuid4());me=psutil.Process()
 while True:
  if lease.exists():time.sleep(5);continue
  raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW)
  free,util=map(int,raw.splitlines()[0].replace(' ','').split(','))
  if free<4096:time.sleep(5);continue
  state={'project':'animation-exaggeration','state':'native-unreal-capture','token':token,'coordinator':{'pid':me.pid,'createTime':me.create_time()},'gpuBefore':{'freeMiB':free,'utilization':util},'scope':'Lightweight owned UE stage; existing GUI processes untouched; preserve every active production lease.'}
  try:
   with lease.open('x') as f:json.dump(state,f)
   break
  except FileExistsError:continue
 def release():
  if lease.exists() and json.loads(lease.read_text()).get('token')==token:lease.unlink()
 atexit.register(release)
 args=['C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(L/'unreal-worker/A02Worker.uproject'),j['level'],'-game','-LevelSequence='+j['sequence'],'-MoviePipelineConfig='+j['captureConfig'],'-RenderOffscreen','-unattended','-nosound','-NoScreenMessages','-NoLoadingScreen','-notexturestreaming','-resx=1920','-resy=1080','-abslog='+str(L/'unreal'/f'{cid}-render.log')]
 with (L/'unreal'/f'{cid}-render.stdout.log').open('w') as log:
  p=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  (L/'unreal'/f'{cid}-render-job.json').write_text(json.dumps({'pid':p.pid,'args':args,'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'controlSha256':hashlib.sha256(control.read_bytes()).hexdigest()},indent=2))
  code=p.wait()
 count=len(list(dest.glob('*.png')))
 print('MRQ exit',code,'frames',count,'expected',j['frames'],flush=True)
 if code!=0 or count!=j['frames']:raise RuntimeError('Incomplete MRQ render; inspect owned log')
if __name__=='__main__':main()
