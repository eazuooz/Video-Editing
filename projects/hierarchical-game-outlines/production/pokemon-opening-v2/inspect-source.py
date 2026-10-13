from pathlib import Path
import json,sys,subprocess,hashlib,datetime,psutil
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parent;R=P.parents[3]
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
S=P/'source-inspection.json';assert not S.exists()
src=R/'shared/assets/game-footage/hierarchical-pokemon/D1SrSFZrV7A-480-1500.mp4'
a=json.loads((P/'source-acquisition.json').read_text(encoding='utf-8'));assert a['exitCode']==0 and sha(src)==a['files'][0]['sha256']
c=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf-8'));assert c['selectedVideo']=='hierarchical-game-outlines' and c['newProductionAuthorization']['fullProductionAuthorized']
p=psutil.Process();state=dict(startedAt=now(),status='extracting',worker=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd()),resource=dict(cpu=psutil.cpu_percent(interval=1),ram=psutil.virtual_memory().available,gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)),sourceSha256=sha(src),samples=[],boards=[])
assert state['resource']['cpu']<85 and state['resource']['ram']>8e9
def save():S.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save();d=P/'source-contact-local';d.mkdir()
times=sorted(set(list(range(900,1001,10))+list(range(1008,1189,6))+[720,830,835,1250,1300,1350,1400,1450]))
frames=[round((t-480)*60000/1001) for t in times]
flt=d/'selection.txt';flt.write_text("select='"+'+'.join('eq(n,%d)'%f for f in frames)+"'",encoding='utf-8')
args=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-hide_banner','-loglevel','error','-threads','2','-i',str(src),'-filter_script:v',str(flt),'-fps_mode','vfr','-frames:v',str(len(frames)),str(d/'frame-%03d.png')]
state['command']=args;save();subprocess.run(args,check=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
for i,(t,f) in enumerate(zip(times,frames),1):
 path=d/f'frame-{i:03d}.png';state['samples'].append(dict(index=i,originalSecondsApprox=t,localFrame=f,localPts=f*1001,file=path.relative_to(R).as_posix(),sha256=sha(path)))
for start in range(0,len(times),12):
 rows=state['samples'][start:start+12];im=Image.new('RGB',(1600,1170),'#dddddd');dr=ImageDraw.Draw(im)
 for j,row in enumerate(rows):
  x=j%4*400;y=j//4*390;fr=Image.open(R/row['file']);fr.thumbnail((400,360));im.paste(fr,(x,y+30));dr.text((x+4,y+2),f"{row['index']:02d} source {row['originalSecondsApprox']}s",font=font,fill='black')
 path=d/f'board-{start//12+1:02d}.jpg';im.save(path,quality=92);state['boards'].append(dict(file=path.relative_to(R).as_posix(),sha256=sha(path)))
state.update(status='samples-awaiting-direct-reading',endedAt=now(),exitCode=0);save();print(json.dumps(dict(samples=len(times),boards=len(state['boards']))))
