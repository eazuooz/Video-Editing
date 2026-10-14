"""Read uncertain source controls before binding new narration. Local-only images."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'production/research/game-lighting-history/local/guided-context-v70'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
stamp=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
sources={
 'capture':('production/research/game-lighting-history/local/episode04-native-v1/own-renderdoc-capture.mp4','4dd745b1f29bee29b351d9e1e605b9092215a1b4ffeeaecaa43206c4735c02c8'),
 'post':('production/research/game-lighting-history/local/epic-post-processing.mp4','d4c422af11f1242fb9d1ac8fd233ddd5638dbfc4be6a93417e50d826f92ea723')}
selections={'capture':[8,18,28,38,48,58,68,78,88,98,108], 'post':[1927,1935,1943,1953,1963,2465,2480,2495,2510,2525]}
assert not OUT.exists(),'Preserve completed source sampling'
for file,digest in sources.values():assert sha(ROOT/file)==digest
resources=[]
for proc in psutil.process_iter(['pid','create_time','name','cmdline']):
 try:
  d=proc.info;c=' '.join(d['cmdline'] or [])
  if 'ffmpeg' in (d['name'] or '').lower() and 'game-lighting-history' in c:raise RuntimeError('Own media slot busy')
  if (d['name'] or '').lower().startswith(('python','ffmpeg')):resources.append(d)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip()
OUT.mkdir();me=psutil.Process()
state=dict(status='extracting',startedAt=stamp(),worker=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=str(ROOT)),resources=resources,gpuObservation=gpu,cpuThreads=2,gpuJobs=0,active=None,samples=[],boards=[],finalApproved=False)
def save():
 (OUT/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
 cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=json.loads(cp.read_text('utf-8-sig'))
 c['episode04GuidedContextV70']=dict(execution=rel(OUT/'execution.json'),status=state['status'],worker=state['worker'],active=state['active'],cpuThreads=2 if state['active'] else 0,gpuJobs=0,finalApproved=False)
 tmp=cp.with_suffix('.context70.tmp');tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
try:
 for key,times in selections.items():
  for t in times:
   file=OUT/f'{key}-{t}.png';cmd=[str(FF),'-n','-v','error','-threads','2','-ss',str(t),'-i',str(ROOT/sources[key][0]),'-frames:v','1','-filter_threads','2','-threads','2',str(file)]
   log=OUT/f'{key}-{t}.log'
   with log.open('w',encoding='utf-8') as handle:
    p=subprocess.Popen(cmd,cwd=ROOT,stdout=handle,stderr=handle,creationflags=subprocess.CREATE_NO_WINDOW);obs=psutil.Process(p.pid)
    state['active']=dict(pid=p.pid,createTime=obs.create_time(),commandLine=cmd,log=rel(log));save();code=p.wait()
   assert code==0,f'{key}@{t}'
   state['samples'].append(dict(source=key,seconds=t,path=rel(file),sha256=sha(file),exitCode=code,directlyRead=False,localOnly=True));state['active']=None
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
 for key in selections:
  samples=[x for x in state['samples'] if x['source']==key]
  for start in range(0,len(samples),4):
   board=Image.new('RGB',(1920,1160),'#111111');draw=ImageDraw.Draw(board)
   for k,item in enumerate(samples[start:start+4]):
    x=k%2*960;y=k//2*580;draw.text((x+12,y+8),f"{key} native {item['seconds']}s",font=font,fill='white')
    with Image.open(ROOT/item['path']) as im:board.paste(im.resize((960,540)),(x,y+40))
   file=OUT/f'{key}-board-{start//4+1:02d}.jpg';board.save(file,quality=95)
   state['boards'].append(dict(path=rel(file),sha256=sha(file),directlyRead=False,localOnly=True))
 state.update(status='context-samples-ready',endedAt=stamp());save();print(json.dumps(dict(samples=len(state['samples']),boards=len(state['boards']),finalApproved=False)))
except BaseException as exc:
 state.update(status='failed-preserving-existing',error=repr(exc),endedAt=stamp());save();raise
