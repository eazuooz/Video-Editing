from pathlib import Path
import sys, json, hashlib, subprocess, datetime, psutil
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(x): (P/'source-acquisition.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (P/'source-acquisition.json').exists(),'Resume existing acquisition'
control=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))
assert control['selectedVideo']=='hierarchical-game-outlines' and control['newProductionAuthorization']['fullProductionAuthorized']
pr=psutil.Process();state=dict(at=now(),status='starting',worker=dict(pid=pr.pid,createTime=pr.create_time(),command=pr.cmdline(),cwd=pr.cwd()),source='https://www.youtube.com/watch?v=D1SrSFZrV7A',sourceRole='independent-gameplay',window=[480,1500],resource=dict(cpu=psutil.cpu_percent(interval=1),ramAvailable=psutil.virtual_memory().available,gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)),exitCode=None)
state['processes']=[]
for p in psutil.process_iter(['pid','create_time','name','cmdline'],ad_value=None):
 if (p.info['name'] or '').lower() in ['python.exe','ffmpeg.exe','node.exe']:
  x=p.info
  try:x['cwd']=p.cwd()
  except(psutil.AccessDenied,psutil.NoSuchProcess):x['cwd']=None
  state['processes'].append(x)
assert state['resource']['cpu']<85 and state['resource']['ramAvailable']>8e9
save(state)
dst=ROOT/'shared/assets/game-footage/hierarchical-pokemon';dst.mkdir(exist_ok=True)
assert not list(dst.glob('D1SrSFZrV7A-480-1500.*'))
args=[sys.executable,'-X','utf8','-m','yt_dlp','--no-playlist','--no-overwrites','--ffmpeg-location','C:/ProgramData/HP/LCDDisplayHelper/bin','-f','best[height<=720][ext=mp4]/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]','--download-sections','*480-1500','--merge-output-format','mp4','-o',str(dst/'D1SrSFZrV7A-480-1500.%(ext)s'),state['source']]
with (P/'source-download-local.log').open('w',encoding='utf-8') as log:
 child=subprocess.Popen(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000)
 state.update(status='downloading',childPid=child.pid,command=args);save(state);code=child.wait()
state.update(exitCode=code,status='acquired-awaiting-source-review' if code==0 else 'failed',endedAt=now(),files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in dst.glob('D1SrSFZrV7A-480-1500.*') if p.suffix in ['.mp4','.mkv']]);save(state)
print(json.dumps({k:state[k] for k in ['status','exitCode','files']},ensure_ascii=False));raise SystemExit(code)
