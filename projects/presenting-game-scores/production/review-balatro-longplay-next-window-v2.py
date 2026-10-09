"""Inspect another unique source window; never adopts footage or starts TTS."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent/'revision-balatro60-v2'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,required=True);args=parser.parse_args()
START=args.start;END=START+480
if START not in (960,1440):raise RuntimeError('Only untouched later windows may be inspected')
OUT=ROOT/f'shared/output/presenting-game-scores/revision-balatro60-v2/source-review/longplay-c1WD4x9Dyg0-window{START}-{END}'
STATE=BASE/f'longplay-window{START}-{END}-execution.json'
stamp=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
if STATE.exists() or OUT.exists():raise RuntimeError('Read existing window; repeat extraction refused')
previous=json.loads((BASE/'longplay-source-execution.json').read_text('utf-8'))
if previous['exitCode']!=0 or not (BASE/'longplay-second480-direct-review-v2.json').exists():raise RuntimeError('Completed earlier direct reviews required')
RAW=Path(previous['sourcePath'])
if sha(RAW)!=previous['sha256']:raise RuntimeError('Source changed')
inventory=[]
for proc in psutil.process_iter(['pid','name','create_time','cmdline']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline'] or [])
  if any(n in (d['name'] or '').lower() for n in ['python','ffmpeg','node']):inventory.append(d)
  if 'presenting-game-scores' in cmd and not any(n in cmd for n in ['serve-native-review-v1.py','vite.presenting-game-scores.black-preflight-v1.config.ts','review-balatro-longplay-next-window-v2.py']):raise RuntimeError('Inspect other own job: '+cmd)
 except psutil.AccessDenied:pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
cim=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|ffmpeg|node' } | Select-Object ProcessId,ParentProcessId,Name,CreationDate,CommandLine | ConvertTo-Json -Depth 4 -Compress"],capture_output=True,text=True,check=True)
save(BASE/f'resources-before-longplay-window{START}-{END}.json',{'observedAt':stamp(),'processInventory':inventory,'cimInventory':json.loads(cim.stdout.lstrip('\ufeff')),'gpuCsv':gpu.stdout.strip(),'cpuLoadPercent':psutil.cpu_percent(interval=1),'freePhysicalMemoryBytes':psutil.virtual_memory().available,'cpuThreads':2,'gpuJobs':0,'researchProcessChanges':0})
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='2'
me=psutil.Process();OUT.mkdir(parents=True);frames=OUT/'frames';frames.mkdir()
s={'schemaVersion':1,'slug':'presenting-game-scores','revision':'balatro60-tetris40-v2','startedAt':stamp(),'actualPid':me.pid,'createTime':me.create_time(),'command':me.cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpu':0,'sourcePath':str(RAW),'sourceSha256':previous['sha256'],'reviewWindowSeconds':[START,END],'stage':'later-window-coarse-extraction','exitCode':None,'footageAdopted':False,'attributionExceptionUserAnswer':'pending','finalPublicRightsApproved':False,'newImagesGitAdded':0};save(STATE,s)
try:
 with (OUT/'sampling.log').open('w',encoding='utf-8') as log:
  result=subprocess.run([str(FF),'-nostdin','-v','error','-threads','2','-ss',str(START),'-i',str(RAW),'-t','480','-an','-vf','fps=1/2,scale=948:533:force_original_aspect_ratio=decrease','-threads','2','-q:v','2',str(frames/'frame-%04d.jpg')],cwd=ROOT,stdout=log,stderr=log)
 if result.returncode:raise RuntimeError(f'Extraction exit{result.returncode}')
 images=sorted(frames.glob('*.jpg'));boards=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',24)
 if len(images)!=240:raise RuntimeError('Unexpected sample count')
 for first in range(0,len(images),6):
  board=Image.new('RGB',(1920,1683),'#171717');draw=ImageDraw.Draw(board);entries=[]
  for n,ip in enumerate(images[first:first+6]):
   im=Image.open(ip).convert('RGB');x=6+(n%2)*960;y=28+(n//2)*561;board.paste(im,(x,y));nominal=START+(first+n)*2+1;index=START//2+first+n+1
   draw.text((x,y-27),f'longplay #{index:03d} nominal {nominal:.0f}s',font=font,fill='white');entries.append({'index':index,'nominalSeconds':nominal,'path':str(ip),'sha256':sha(ip)})
  bp=OUT/f'board-{first//6+1:03d}.jpg';board.save(bp,quality=94);boards.append({'path':str(bp),'sha256':sha(bp),'entries':entries})
 s.update(stage='later-window-extraction-complete-direct-review-pending',sampleExtractionExit=0,samples=len(images),boards=boards,samplesAreNominalNotNativePts=True,finishedAt=stamp(),exitCode=0);save(STATE,s)
 print(json.dumps({k:s[k] for k in ['stage','actualPid','samples','exitCode']},ensure_ascii=False),flush=True)
except BaseException as e:
 s.update(stage='later-window-failed-preserve-files',error=repr(e),finishedAt=stamp(),exitCode=1);save(STATE,s);raise
