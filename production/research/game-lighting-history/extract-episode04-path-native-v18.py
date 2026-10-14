"""One CPU2 native pixel batch for the next chapter; does not approve motion."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, psutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'production/research/game-lighting-history/local/episode04-path-native-v18'
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
stamp = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
sources = {
 'cyberpunk': ('production/research/game-lighting-history/local/episode04-native-v1/cyberpunk-ray-reconstruction.mp4', '25a4f9f3d7c2cd335df4128687582e444b61c7d119b2af5493b80003b49ac2da', None, [8,8.5,9,9.5,11.966666667,27,27.5,28,28.933333333]),
}
for path,digest,crop,times in sources.values(): assert sha(ROOT/path)==digest
assert not OUT.exists(), 'Preserve earlier media'
resources=[]
for p in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  d=p.info; cmd=' '.join(d['cmdline'] or [])
  if 'python' in (d['name'] or '').lower() or 'ffmpeg' in (d['name'] or '').lower(): resources.append(d)
  if 'ffmpeg' in (d['name'] or '').lower() and 'game-lighting-history' in cmd: raise RuntimeError('Owned media slot busy')
 except (psutil.AccessDenied,psutil.NoSuchProcess): pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
OUT.mkdir(); me=psutil.Process()
state={'startedAt':stamp(),'status':'running','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'resources':resources,'gpuObservation':gpu,'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'samples':[],'boards':[],'allSamplesRead':False,'allMovingFramesReviewed':False,'newGitImages':0}
SP=OUT/'execution.json'
def save(): SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json'; j=json.loads(p.read_text('utf-8-sig'))
 j['episode04PathNativeV17']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'samples':len(state['samples']),'cpuThreads':2,'gpuJobs':0,'allMovingFramesReviewed':False}
 j['ownedActiveWork']=({'type':'CPU-path-native-v18','execution':rel(SP),'worker':state['worker'],'active':state['active'],'next':'Read native windows/crop before next chapter composition'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Read9 supplementary Cyberpunk8-12s and27-28.933s samples; exclude13-15s title card before path chapter composition'})
 j['updatedAt']=stamp(); tmp=p.with_suffix('.path-native-v18.tmp'); tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
try:
 save();checkpoint()
 for name,(path,digest,crop,times) in sources.items():
  samples=[]
  for index,time in enumerate(times):
   dest=OUT/f'{name}-{index+1:02d}.png'; log=OUT/f'{name}-{index+1:02d}.log'
   vf=[]
   if crop:
    x,y,w,h=crop;vf.append(f'crop={w}:{h}:{x}:{y}')
   vf+=['scale=1920:1080:force_original_aspect_ratio=decrease','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black','setsar=1']
   cmd=[str(FF),'-n','-v','error','-threads','2','-ss',str(time),'-i',str(ROOT/path),'-filter_threads','2','-vf',','.join(vf),'-frames:v','1',str(dest)]
   with log.open('w',encoding='utf-8') as f:
    proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f); observed=psutil.Process(proc.pid)
    state['active']={'pid':proc.pid,'createTime':observed.create_time(),'commandLine':cmd,'log':rel(log),'startedAt':stamp()};save();checkpoint();code=proc.wait()
   state['commands'].append({**state['active'],'exitCode':code,'endedAt':stamp()});state['active']=None;assert code==0
   item={'source':name,'path':rel(dest),'sha256':sha(dest),'localSeconds':time,'sourcePath':path,'sourceSha256':digest,'crop':crop,'directlyRead':False,'localOnly':True};state['samples'].append(item);samples.append(item);save()
  for start in range(0,len(samples),4):
   group=samples[start:start+4]; board=Image.new('RGB',(1920,1160),'#111111');draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
   for k,item in enumerate(group):
    x=(k%2)*960;y=(k//2)*580
    draw.text((x+12,y+8),f"{name} · local {item['localSeconds']}s",font=font,fill='white')
    with Image.open(ROOT/item['path']) as im: board.paste(im.resize((960,540)),(x,y+40))
   file=OUT/f'{name}-board-{start//4+1:02d}.jpg';board.save(file,quality=94)
   state['boards'].append({'path':rel(file),'sha256':sha(file),'samples':[x['path'] for x in group],'directlyRead':False,'localOnly':True});save()
 state['status']='samples-ready';state['endedAt']=stamp();save();checkpoint();print(json.dumps({'samples':len(state['samples']),'boards':len(state['boards']),'newGitImages':0}))
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise
