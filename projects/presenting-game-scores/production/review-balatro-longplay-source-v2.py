"""One CPU2/GPU0 read-only source job; acquisition is not footage adoption."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent/'revision-balatro60-v2'
RAW=ROOT/'shared/assets/presenting-game-scores/revision-balatro60-v2/longplay-c1WD4x9Dyg0.mp4'
OUT=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/source-review/longplay-c1WD4x9Dyg0'
STATE=BASE/'longplay-source-execution.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
YTPY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
NODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
stamp=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def run(cmd,log):
 with log.open('w',encoding='utf-8') as f:p=subprocess.run([str(x) for x in cmd],cwd=ROOT,stdout=f,stderr=f)
 if p.returncode:raise RuntimeError(f'exit {p.returncode}: {log}')
 return p.returncode
if STATE.exists() or RAW.exists() or OUT.exists():raise RuntimeError('Read existing checkpoint; duplicate work refused.')
rights=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/rights/c1WD4x9Dyg0-license-description.ax.txt'
text=rights.read_text('utf-8')
if 'Feel free to use this footage' not in text or 'Creative' not in text and '크리에이티브 커먼즈' not in text:raise RuntimeError('Actual source permission evidence required.')
inventory=[]
for p in psutil.process_iter(['pid','name','create_time','cmdline']):
 try:
  d=p.info;cmd=' '.join(d['cmdline'] or [])
  if any(n in (d['name'] or '').lower() for n in ['python','ffmpeg','node']):inventory.append(d)
  if 'presenting-game-scores' in cmd and not any(n in cmd for n in ['serve-native-review-v1.py','vite.presenting-game-scores.black-preflight-v1.config.ts','review-balatro-longplay-source-v2.py']):raise RuntimeError('Other own job needs inspection: '+cmd)
 except psutil.AccessDenied:pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
resource={'observedAt':stamp(),'processInventory':inventory,'gpuCsv':gpu.stdout.strip(),'cpuLoadPercent':psutil.cpu_percent(interval=1),'freePhysicalMemoryBytes':psutil.virtual_memory().available,'cpuThreads':2,'gpuJobs':0,'researchProcessChanges':0}
save(BASE/'resources-before-longplay-review.json',resource)
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='2'
os.environ['PATH']=str(NODE.parent)+os.pathsep+os.environ['PATH']
me=psutil.Process();OUT.mkdir(parents=True)
state={'schemaVersion':1,'slug':'presenting-game-scores','revision':'balatro60-tetris40-v2','startedAt':stamp(),'actualPid':me.pid,'createTime':me.create_time(),'command':me.cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpu':0,'stage':'longplay-acquisition','exitCode':None,'directReviewApproved':False,'footageAdopted':False,'attributionExceptionUserAnswer':'pending','finalPublicRightsApproved':False,'sourceAudioSelected':False,'newGitImages':0,'rightsEvidence':str(rights),'rightsEvidenceSha256':sha(rights)};save(STATE,state)
try:
 run([YTPY,'-X','utf8','-m','yt_dlp','--no-playlist','--no-progress','--no-overwrites','--js-runtimes','node','--write-info-json','-f','299','-o',RAW,'https://www.youtube.com/watch?v=c1WD4x9Dyg0'],OUT/'download.log')
 meta=json.loads(RAW.with_suffix('.info.json').read_text('utf-8'))
 if meta.get('channel')!='Squeaky Whale Gameplay Archive' or 'Creative Commons' not in (meta.get('license') or ''):raise RuntimeError('Recording provenance/license mismatch')
 probe=subprocess.run([str(FP),'-v','error','-show_streams','-show_format','-of','json',str(RAW)],capture_output=True,text=True,check=True);p=json.loads(probe.stdout);save(OUT/'probe.json',p)
 state.update(stage='longplay-whole-decode',sourcePath=str(RAW),sha256=sha(RAW),bytes=RAW.stat().st_size,title=meta['title'],channelId=meta.get('channel_id'),license=meta.get('license'),durationSeconds=float(p['format']['duration']));save(STATE,state)
 run([FF,'-nostdin','-v','error','-threads','2','-i',RAW,'-map','0:v:0','-an','-f','null','-'],OUT/'whole-decode.log');state.update(wholeDecodeExit=0,stage='first480seconds-coarse-review-extraction');save(STATE,state)
 frames=OUT/'frames';frames.mkdir()
 run([FF,'-nostdin','-v','error','-threads','2','-i',RAW,'-t','480','-an','-vf','fps=1/2,scale=948:533:force_original_aspect_ratio=decrease','-threads','2','-q:v','2',frames/'frame-%04d.jpg'],OUT/'sampling.log')
 images=sorted(frames.glob('*.jpg'));boards=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',24)
 for first in range(0,len(images),6):
  board=Image.new('RGB',(1920,1683),'#171717');draw=ImageDraw.Draw(board);entries=[]
  for n,ip in enumerate(images[first:first+6]):
   im=Image.open(ip).convert('RGB');x=6+(n%2)*960;y=28+(n//2)*561;board.paste(im,(x,y));nominal=(first+n)*2+1
   draw.text((x,y-27),f'longplay #{first+n+1:03d} nominal {nominal:.0f}s',font=font,fill='white');entries.append({'index':first+n+1,'nominalSeconds':nominal,'path':str(ip),'sha256':sha(ip)})
  bp=OUT/f'board-{first//6+1:03d}.jpg';board.save(bp,quality=94);boards.append({'path':str(bp),'sha256':sha(bp),'entries':entries})
 state.update(stage='longplay-technical-preflight-complete-direct-review-pending',sampleExtractionExit=0,samples=len(images),boards=boards,samplesAreNominalNotNativePts=True,reviewWindowSeconds=[0,480],finishedAt=stamp(),exitCode=0);save(STATE,state)
 print(json.dumps({k:state[k] for k in ['stage','actualPid','durationSeconds','sha256','samples','exitCode']},ensure_ascii=False),flush=True)
except BaseException as e:
 state.update(stage='longplay-source-failed-preserve-files',error=repr(e),finishedAt=stamp(),exitCode=1);save(STATE,state);raise
