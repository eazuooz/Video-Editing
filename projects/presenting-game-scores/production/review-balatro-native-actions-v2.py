"""Preflight exact source PTS around observed actions; never adopts source or creates narration."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import argparse,hashlib,json,os,re,subprocess
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent/'revision-balatro60-v2'
parser=argparse.ArgumentParser();parser.add_argument('--recover-v3',action='store_true');args=parser.parse_args()
VERSION='v3' if args.recover_v3 else 'v2'
OUT=ROOT/f'shared/output/presenting-game-scores/revision-balatro60-v2/native-actions-preflight-{VERSION}'
STATE=BASE/f'native-actions-preflight-execution-{VERSION}.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FP=FF.with_name('ffprobe.exe')
stamp=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
if STATE.exists() or OUT.exists():raise RuntimeError('Read existing native preflight; duplicate extraction refused')
if args.recover_v3:
 failed=json.loads((BASE/'native-actions-preflight-execution-v2.json').read_text('utf-8'))
 if failed['exitCode']!=1 or failed['intervals'] or failed['error']!="RuntimeError('Extracted source PTS mismatch: pair')":raise RuntimeError('Inspect changed failed state before recovery')
 if list((ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/native-actions-preflight-v2').rglob('frame-*.jpg')):raise RuntimeError('Existing extracted images require explicit resume')
prior=json.loads((BASE/'longplay-source-execution.json').read_text('utf-8'))
for name in ['longplay-first480-direct-review-v2.json','longplay-second480-direct-review-v2.json','longplay-third480-direct-review-v2.json']:
 p=json.loads((BASE/name).read_text('utf-8'))
 if not p['allListedCoarsePixelsDirectlyRead']:raise RuntimeError('Coarse direct review required')
RAW=Path(prior['sourcePath'])
if sha(RAW)!=prior['sha256']:raise RuntimeError('Source changed')
inventory=[]
for proc in psutil.process_iter(['pid','name','create_time','cmdline']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline'] or [])
  if any(n in (d['name'] or '').lower() for n in ['python','ffmpeg','node']):inventory.append(d)
  if 'presenting-game-scores' in cmd and not any(n in cmd for n in ['serve-native-review-v1.py','vite.presenting-game-scores.black-preflight-v1.config.ts','review-balatro-native-actions-v2.py']):raise RuntimeError('Inspect other own job: '+cmd)
 except psutil.AccessDenied:pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
cim=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|ffmpeg|node' } | Select-Object ProcessId,ParentProcessId,Name,CreationDate,CommandLine | ConvertTo-Json -Depth 4 -Compress"],capture_output=True,text=True,check=True)
save(BASE/f'resources-before-native-actions-preflight-{VERSION}.json',{'observedAt':stamp(),'processInventory':inventory,'cimInventory':json.loads(cim.stdout.lstrip('\ufeff')),'gpuCsv':gpu.stdout.strip(),'cpuLoadPercent':psutil.cpu_percent(interval=1),'freePhysicalMemoryBytes':psutil.virtual_memory().available,'cpuThreads':2,'gpuJobs':0,'researchProcessChanges':0})
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='2'
me=psutil.Process();OUT.mkdir(parents=True)
s={'schemaVersion':1,'slug':'presenting-game-scores','revision':'balatro60-tetris40-v2','startedAt':stamp(),'actualPid':me.pid,'createTime':me.create_time(),'command':me.cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpu':0,'sourcePath':str(RAW),'sourceSha256':prior['sha256'],'stage':'native-pts-action-preflight','exitCode':None,'footageAdopted':False,'attributionExceptionUserAnswer':'pending','finalPublicRightsApproved':False,'newImagesGitAdded':0,'intervals':[]};save(STATE,s)
if args.recover_v3:
 s['recoveryOf']='native-actions-preflight-execution-v2.json';s['historicalFailureActualOuterExitObserved']=1;s['historicalExtractedImages']=0;s['repair']='Move duration bound to input before -i; output -t with absolute copied PTS rejected all encoded frames. Source PTS/probe and failed log preserved.';save(STATE,s)
windows=[('pair',240,247),('three-kind-extra-card',351,365),('full-house',392,414),('enhanced-two-pair',660,684),('hook-two-pair',904,927),('diamond-full-house',995,1011),('round-accumulate',1097,1115),('enhanced-704',1203,1225),('straight-400',1251,1267),('decimal-mult',1283,1297),('debuff-diamond',1397,1411)]
try:
 stream=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,time_base,start_time,duration','-of','json',str(RAW)],capture_output=True,text=True,check=True).stdout)['streams'][0]
 tb=Fraction(stream['time_base']);step=int(Fraction(1,60)/tb)
 if tb!=Fraction(1,15360) or step!=256:raise RuntimeError('Unexpected source timing; inspect before extracting')
 s['stream']=stream;s['sourceFrameStepPts']=step;save(STATE,s)
 entries=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
 for key,start,end in windows:
  directory=OUT/key;directory.mkdir()
  pf=directory/'native-source-frames.json'
  oldprobe=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/native-actions-preflight-v2/pair/native-source-frames.json'
  if args.recover_v3 and key=='pair':pf.write_bytes(oldprobe.read_bytes())
  else:
   pr=subprocess.run([str(FP),'-v','error','-threads','2','-select_streams','v:0','-read_intervals',f'{start-2}%{end+2}','-show_frames','-show_entries','frame=best_effort_timestamp,best_effort_timestamp_time,pict_type','-of','json',str(RAW)],capture_output=True,text=True,check=True)
   pf.write_text(pr.stdout,'utf-8')
  frames=json.loads(pf.read_text('utf-8'))['frames'];lo=int(Fraction(start)/tb);hi=int(Fraction(end)/tb)
  chosen=[f for f in frames if lo<=int(f['best_effort_timestamp'])<hi]
  pts=[int(f['best_effort_timestamp']) for f in chosen]
  if not pts or pts[0]!=lo or pts[-1]!=hi-step or any(b-a!=step for a,b in zip(pts,pts[1:])) or len(pts)!=(end-start)*60:raise RuntimeError('Native PTS continuity mismatch: '+key)
  selected=[lo+i*15360 for i in range(end-start)]+[hi-step]
  expression='+'.join('eq(pts,'+str(p)+')' for p in selected)
  log=directory/'sampling.log'
  with log.open('w',encoding='utf-8') as f:
   rc=subprocess.run([str(FF),'-nostdin','-v','info','-threads','2','-copyts','-ss',str(start-2),'-t',str(end-start+4),'-i',str(RAW),'-an','-vf',f"select='{expression}',scale=948:533:force_original_aspect_ratio=decrease,showinfo",'-fps_mode','passthrough','-threads','2','-q:v','2',str(directory/'frame-%04d.jpg')],cwd=ROOT,stdout=f,stderr=f).returncode
  if rc:raise RuntimeError('Native extraction exit'+str(rc))
  shown=[int(p) for p in re.findall(r'\bn:\s*\d+\s+pts:\s*(-?\d+)',log.read_text('utf-8'))]
  images=sorted(directory.glob('frame-*.jpg'))
  if shown!=selected or len(images)!=len(selected):raise RuntimeError('Extracted source PTS mismatch: '+key)
  cut={'id':key,'preflightStartSeconds':start,'preflightEndSecondsExclusive':end,'sourceFirstPts':lo,'sourceLastPts':hi-step,'sourceEndPtsExclusive':hi,'sourceTimeBase':str(tb),'sourceFrames':len(pts),'sourceFrameContinuityVerified':True,'ptsRecord':str(pf),'ptsRecordSha256':sha(pf),'sampleExtractionExit':0,'samples':[],'nativePixelReviewApproved':False,'adopted':False}
  for p,ip in zip(selected,images):
   e={'interval':key,'sourcePts':p,'sourceTimeBase':str(tb),'sourceSeconds':float(p*tb),'sourceFrame':p//step,'path':str(ip),'sha256':sha(ip)};cut['samples'].append(e);entries.append(e)
  s['intervals'].append(cut);save(STATE,s)
 boards=[]
 for first in range(0,len(entries),6):
  board=Image.new('RGB',(1920,1683),'#171717');draw=ImageDraw.Draw(board)
  for n,e in enumerate(entries[first:first+6]):
   im=Image.open(e['path']).convert('RGB');x=6+(n%2)*960;y=28+(n//2)*561;board.paste(im,(x,y));draw.text((x,y-27),f"{e['interval']} f{e['sourceFrame']} PTS{e['sourcePts']}",font=font,fill='white')
  bp=OUT/f'board-{first//6+1:03d}.jpg';board.save(bp,quality=94);boards.append({'path':str(bp),'sha256':sha(bp),'entries':entries[first:first+6]})
 s.update(stage='native-actions-extraction-exit0-direct-review-pending',sampleCount=len(entries),boardCount=len(boards),boards=boards,totalPreflightUniqueSeconds=sum(b-a for _,a,b in windows),allNativeFramesReviewed=False,continuousPlaybackApproved=False,nativeCutBoundariesApproved=False,finishedAt=stamp(),exitCode=0);save(STATE,s)
 print(json.dumps({k:s[k] for k in ['stage','actualPid','sampleCount','boardCount','totalPreflightUniqueSeconds','exitCode']},ensure_ascii=False),flush=True)
except BaseException as e:
 s.update(stage='native-preflight-failed-preserve-files',error=repr(e),finishedAt=stamp(),exitCode=1);save(STATE,s);raise
