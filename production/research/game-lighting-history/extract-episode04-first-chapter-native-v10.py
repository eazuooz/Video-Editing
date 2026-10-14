"""Single CPU2 native crop samples for a first-chapter review; no final approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,os,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'production/research/game-lighting-history/local/episode04-first-chapter-native-v10'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
stamp=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
resources=[]
for p in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  d=p.info;cmd=' '.join(d['cmdline']or[])
  if d['name']and any(n in d['name'].lower()for n in ['ffmpeg','python','node']):resources.append(d)
  if d['name']and 'ffmpeg' in d['name'].lower()and 'game-lighting-history' in cmd:raise RuntimeError('Owned media slot busy')
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
assert not OUT.exists(),'Preserve earlier samples'
specs=[('vsm','production/research/game-lighting-history/local/episode04-native-v1/virtual-shadow-editor-2024.mp4','b6dbe8fe584e3b9401b98b7d50bdbd35dc38a611a6aedddee7341c7069bb8d32',(64,122,1536,864),[0,3.2,4,7.64,16.24,56,61.88,74,79,83.54,92.86]),('cyber','production/research/game-lighting-history/local/episode04-native-v1/cyberpunk-ray-reconstruction.mp4','25a4f9f3d7c2cd335df4128687582e444b61c7d119b2af5493b80003b49ac2da',None,[39,42.0]),('post','production/research/game-lighting-history/local/epic-post-processing.mp4','d4c422af11f1242fb9d1ac8fd233ddd5638dbfc4be6a93417e50d826f92ea723',None,[1580,1582.2]),('renderdoc','production/research/game-lighting-history/local/episode04-native-v1/own-renderdoc-capture.mp4','4dd745b1f29bee29b351d9e1e605b9092215a1b4ffeeaecaa43206c4735c02c8',(244,123,1570,923),[125,131.95])]
for _,path,digest,_,_ in specs:assert sha(ROOT/path)==digest,path
OUT.mkdir()
me=psutil.Process();state={'startedAt':stamp(),'status':'running','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'resourceObservation':{'processes':resources,'gpu':gpu},'cpuThreads':2,'gpuJobs':0,'active':None,'completed':[],'commands':[],'allFinalPixelsReviewed':False,'localOnly':True}
sp=OUT/'execution.json'
def save():sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
save()
try:
 for slug,path,digest,crop,times in specs:
  points=[]
  for t in times:
   raw=OUT/f'{slug}-{t:g}-raw.png';cmd=[str(FF),'-n','-v','error','-threads','2','-ss',str(t),'-i',str(ROOT/path),'-frames:v','1','-threads','2',str(raw)]
   log=OUT/f'{slug}-{t:g}.log'
   with log.open('w',encoding='utf-8')as f:
    p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f);proc=psutil.Process(p.pid)
    state['active']={'pid':p.pid,'createTime':proc.create_time(),'commandLine':cmd,'startedAt':stamp(),'log':rel(log)};save();code=p.wait()
   record={**state['active'],'exitCode':code,'endedAt':stamp()};state['commands'].append(record);state['active']=None;save();assert code==0,record
   im=Image.open(raw).convert('RGB');assert im.size==(1920,1080)if slug!='post'else im.size==(1280,720)
   cp=OUT/f'{slug}-{t:g}-crop.png'
   if crop:
    x,y,w,h=crop;im=im.crop((x,y,x+w,y+h));im.resize((1920,1080),Image.Resampling.LANCZOS).save(cp)
   else:im.resize((1920,1080),Image.Resampling.LANCZOS).save(cp)
   point={'slug':slug,'nativeSeconds':t,'source':path,'sourceSha256':digest,'raw':{'path':rel(raw),'sha256':sha(raw)},'crop':crop,'cropImage':{'path':rel(cp),'sha256':sha(cp)},'directlyViewed':False,'fullMovingApproval':False}
   state['completed'].append(point);points.append(point);save()
  for offset in range(0,len(points),6):
   group=points[offset:offset+6];board=Image.new('RGB',(1920,2*400),(17,20,24));draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
   for i,item in enumerate(group):
    x=i%3*640;y=i//3*400;tile=Image.open(ROOT/item['cropImage']['path']).resize((640,360),Image.Resampling.LANCZOS);board.paste(tile,(x,y+36));draw.text((x+8,y+7),f"{slug} native {item['nativeSeconds']:g}s crop",font=font,fill='white')
   bp=OUT/f'{slug}-board-{offset//6+1:02}.png';board.save(bp);state.setdefault('boards',[]).append({'path':rel(bp),'sha256':sha(bp),'directlyViewed':False});save()
  print(json.dumps({'source':slug,'points':len(points),'status':'samples-ready'}),flush=True)
 state['status']='samples-ready';state['endedAt']=stamp();save()
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();raise
