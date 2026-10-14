"""Inspect unused secured editor actions before authoring any added narration."""
from pathlib import Path
import json,hashlib,subprocess,datetime,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'production/research/game-lighting-history/local/part1-added-action-candidates-v228'
OUT.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
jobs=[('nanite',ROOT/'production/research/game-lighting-history/local/episode04-additional-action-v44/nanite-editor-goldcoast2024.mp4',218,280),
 ('virtual-texture',ROOT/'production/research/game-lighting-history/local/episode04-additional-action-v47/virtual-texture-editor-goldcoast2024.mp4',130,175)]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
me=psutil.Process();state=dict(startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),identity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline()),cpuThreads=2,gpuJobs=0,localOnly=True,rows=[],approved=False)
for name,source,start,end in jobs:
 d=OUT/name;d.mkdir();cmd=[FF,'-n','-v','error','-threads','2','-ss',str(start),'-t',str(end-start),'-i',str(source),'-filter_threads','2','-vf','crop=1520:854:60:114,fps=1,scale=960:540','-threads','2',str(d/'frame-%03d.png')]
 with (d/'extract.log').open('w')as log:
  p=subprocess.Popen(cmd,stdout=log,stderr=log);obs=psutil.Process(p.pid);state['active']=dict(pid=p.pid,createTime=obs.create_time(),command=cmd);(OUT/'execution.json').write_text(json.dumps(state,indent=2)+'\n');code=p.wait()
 assert code==0
 files=sorted(d.glob('frame-*.png'));assert len(files)==end-start
 row=dict(name=name,source=dict(path=rel(source),sha256=sha(source)),range=[start,end],crop=[60,114,1520,854],items=[],boards=[])
 for i,p in enumerate(files):row['items'].append(dict(path=rel(p),sha256=sha(p),sourceTime=start+i,directlyViewed=False))
 for off in range(0,len(files),4):
  board=Image.new('RGB',(1920,1180),(20,20,24));draw=ImageDraw.Draw(board)
  for j,item in enumerate(row['items'][off:off+4]):
   x=j%2*960;y=j//2*590
   with Image.open(ROOT/item['path'])as im:board.paste(im,(x,y+50))
   draw.text((x+8,y+8),f"{name} source {item['sourceTime']}s",font=font,fill='white')
  p=d/f'board-{off//4+1:03d}.png';board.save(p);row['boards'].append(dict(path=rel(p),sha256=sha(p),directlyViewed=False))
 state['rows'].append(row)
state.update(active=None,endedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),exitCode=0)
(OUT/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(images=107,boards=sum(len(r['boards'])for r in state['rows']),exitCode=0,approved=False)))
