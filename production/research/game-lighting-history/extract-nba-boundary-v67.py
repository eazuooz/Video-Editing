"""Inspect a new, complete NBA source. Sampling does not approve final motion."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, psutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'production/research/game-lighting-history/local/nba-boundary-v67'
SOURCE=ROOT/'production/research/game-lighting-history/local/nba2k27-dlss5-official-2026.mp4'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
stamp=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
assert sha(SOURCE)=='102800354e8af924023cca9a8df7fb8a08903e77e7c1bd1826ea4e556cf80a9a'
assert not OUT.exists(),'Preserve completed extraction'
resources=[]
for p in psutil.process_iter(['pid','name','cmdline','create_time']):
 try:
  d=p.info;cmd=' '.join(d['cmdline'] or [])
  if 'ffmpeg' in (d['name'] or '').lower() and 'game-lighting-history' in cmd:raise RuntimeError('Own media slot busy')
  if (d['name'] or '').lower().startswith(('python','ffmpeg')):resources.append(d)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip()
OUT.mkdir();me=psutil.Process()
state=dict(startedAt=stamp(),status='running',worker=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=str(ROOT)),source=dict(id='LHUzFnq70b8',path=rel(SOURCE),sha256=sha(SOURCE)),resources=resources,gpuObservation=gpu,cpuThreads=2,gpuJobs=0,active=None,samples=[],boards=[],allSamplesDirectlyRead=False,finalUseApproved=False,newGitImages=0)
def save():
 (OUT/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
 cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=json.loads(cp.read_text('utf-8-sig'))
 c['episode04NbaBoundaryV67']=dict(execution=rel(OUT/'execution.json'),status=state['status'],worker=state['worker'],active=state['active'],cpuThreads=2,gpuJobs=0,finalUseApproved=False)
 c['updatedAt']=stamp();tmp=cp.with_suffix('.nba67.tmp');tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
cmd=[str(FF),'-n','-v','error','-threads','2','-ss','19','-i',str(SOURCE),'-t','6','-filter_threads','2','-vf','fps=2','-frames:v','12','-threads','2',str(OUT/'frame-%02d.png')]
try:
 with (OUT/'extract.log').open('w',encoding='utf-8') as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW);obs=psutil.Process(p.pid)
  state['active']=dict(pid=p.pid,createTime=obs.create_time(),commandLine=cmd,log=rel(OUT/'extract.log'));save();code=p.wait()
 state['command']={**state['active'],'exitCode':code};state['active']=None;assert code==0
 files=sorted(OUT.glob('frame-*.png'));assert len(files)==12
 for i,file in enumerate(files):state['samples'].append(dict(path=rel(file),sha256=sha(file),seconds=19+i*.5,sourceFrame=1140+i*30,directlyRead=False,localOnly=True))
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
 for start in range(0,12,4):
  board=Image.new('RGB',(1920,1160),'#111111');d=ImageDraw.Draw(board)
  for k,item in enumerate(state['samples'][start:start+4]):
   x=k%2*960;y=k//2*580;d.text((x+12,y+8),f"NBA2K27 native {item['seconds']}s",font=font,fill='white')
   with Image.open(ROOT/item['path']) as im:board.paste(im.resize((960,540)),(x,y+40))
  file=OUT/f'board-{start//4+1:02d}.jpg';board.save(file,quality=94)
  state['boards'].append(dict(path=rel(file),sha256=sha(file),directlyRead=False,localOnly=True))
 state.update(status='selection-samples-ready',endedAt=stamp());save();print(json.dumps(dict(samples=12,boards=3,finalUseApproved=False)))
except BaseException as e:
 state.update(status='failed-preserve-existing',error=str(e),endedAt=stamp());save();raise
