import json, hashlib, subprocess, os, psutil, time
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('D:/Github/Video-Editing');R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1';OUT=ROOT/'shared/output/cross-game-example-coverage/motion/extra-native-v2'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
assert not (R/'extra-native-execution-v2.json').exists()
cpu=psutil.cpu_percent(interval=1); ram=psutil.virtual_memory().available//1024
assert cpu<85 and ram>8000000,(cpu,ram)
busy=[]
for p in psutil.process_iter(['pid','name','cmdline','create_time']):
 c=' '.join(p.info.get('cmdline') or []).lower()
 if p.pid!=os.getpid() and ('render-motion-narration-timed-comparisons-v1.cjs' in c or 'qa-motion-narration-timed-comparisons-v1.py' in c or 'render-motion-four-additions-v7.py' in c): busy.append(p.info)
assert not busy,busy
protected=json.loads((R/'narration-first-paragraph-repair-execution-v1.json').read_text('utf-8-sig'))['protectedInputs']
assert len(protected)==71
for x in protected: assert sha(ROOT/x['path'])==x['sha256'],x['path']
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip()
sources=[dict(id='portal40-58',path='shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4',sha256='0d233cfcc3eb86b1e7722d257512ed6cfcc2b6276eac0b349fded54c516843bb',frames=[1199]+[round(t*30000/1001) for t in range(41,59)],ptsStep=1001,timeBase='1/30000',fps=30000/1001)]
state=dict(schemaVersion=1,startedAt=stamp(),pid=os.getpid(),createTime=psutil.Process().create_time(),resource=dict(cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,gpuRaw=gpu,ownedHeavyOtherJobs=0),sources=sources,cpuThreads=2,gpuJobs=0,protected71ShaMatched=True,sourcePlanningOnly=True,status='running',actualOuterExitCode=None,results=[],samples=[],boards=[])
def save(): (R/'extra-native-execution-v2.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
OUT.mkdir(parents=True,exist_ok=True); save()
for row in sources:
 src=ROOT/row['path'];assert sha(src)==row['sha256']
 folder=OUT/row['id'];folder.mkdir(exist_ok=True)
 select='+'.join('eq(n\\,%d)'%n for n in row['frames'])
 cmd=[FF,'-hide_banner','-loglevel','error','-threads','2','-filter_threads','2','-i',str(src),'-vf',f'select={select},scale=1280:720','-fps_mode','passthrough','-an',str(folder/'sample-%02d.png')]
 run=subprocess.run(cmd,capture_output=True,text=True)
 state['results'].append(dict(id=row['id'],exitCode=run.returncode,stderr=run.stderr[-3000:]));save();assert run.returncode==0,run.stderr
 for i,n in enumerate(row['frames'],1):
  p=folder/f'sample-{i:02d}.png';assert p.exists()
  state['samples'].append(dict(id=row['id'],frame=n,pts=n*row['ptsStep'],timeBase=row['timeBase'],seconds=n/row['fps'],path=p.relative_to(ROOT).as_posix(),sha256=sha(p),source=row['path']))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for start in range(0,len(state['samples']),4):
 chunk=state['samples'][start:start+4];board=Image.new('RGB',(1920,1160),'#e4e7ec');d=ImageDraw.Draw(board)
 for k,s in enumerate(chunk):
  x=(k%2)*960;y=(k//2)*580
  im=Image.open(ROOT/s['path']).resize((960,540));board.paste(im,(x,y+40));d.text((x+8,y+5),f"{s['id']} native{ s['frame']} PTS{s['pts']} {s['seconds']:.3f}s",font=font,fill='black')
 p=OUT/f'board-{len(state["boards"])+1:02d}.png';board.save(p)
 state['boards'].append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),samples=chunk))
state.update(status='extracted-awaiting-direct-review',finishedAt=stamp(),sampleCount=len(state['samples']),boardCount=len(state['boards']),sourceFramesReextractedFromCompletedQa=0,directPixelReview=False,finalCutAllocationApproved=False)
save();print(json.dumps(dict(samples=len(state['samples']),boards=len(state['boards']),cpuThreads=2,gpuJobs=0,allExtractionExitCodes=[x['exitCode'] for x in state['results']])))
