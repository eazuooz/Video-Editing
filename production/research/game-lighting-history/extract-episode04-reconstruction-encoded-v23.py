"""One CPU2 extraction of all26 current chapter cue/cut/annotation samples."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, psutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
OUT=ROOT/'production/research/game-lighting-history/local/episode04-reconstruction-encoded-v23'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
buildPath=P/'reconstruction-chapter-review-build-v23.json';build=read(buildPath)
assert read(P/'reconstruction-chapter-review-execution-v23.json')['status']=='technical-review-pair-ready'
assert build['identicalAacPayloadAndPtsAndDuration'] and all(x['wholeDecode']['exitCode']==0 for x in build['outputs'])
plan=read(ROOT/build['plan']['path']);assert sha(ROOT/build['plan']['path'])==build['plan']['sha256']
N=plan['totals']['frames'];assert N==7301
metrics=read(ROOT/'production/research/game-lighting-history/local/episode04-reconstruction-chapter-v23/caption-layout.json')['metrics']
assert len(metrics)==26
for ref in build['outputs']:assert sha(ROOT/ref['path'])==ref['sha256']
assert not OUT.exists()
resources=[]
for proc in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline']or[])
  if d['name'] and any(n in d['name'].lower() for n in ['ffmpeg','python']):resources.append(d)
  if d['name'] and 'ffmpeg' in d['name'].lower() and 'game-lighting-history' in cmd:raise RuntimeError('Owned media slot busy')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
OUT.mkdir();me=psutil.Process();SP=OUT/'execution.json'
state={'status':'running','startedAt':stamp(),'worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'resourceObservation':{'processes':resources,'gpu':gpu},'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'items':[],'boards':[],'build':{'path':rel(buildPath),'sha256':sha(buildPath)},'localOnly':True,'newGitImages':0,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False}
def save():SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
 p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(p)
 j['episode04ReconstructionEncodedExtractionV23']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'images':len(state['items']),'boards':len(state['boards']),'allFinalPixelsReviewed':False}
 j['ownedActiveWork']=({'type':'CPU-reconstruction-encoded-extraction-v23','execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Read all26 cues and every cut/annotation board; then remaining55 paragraphs'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct encoded chapter sample review; all moving/final approvals pending'})
 j['updatedAt']=stamp();tmp=p.with_suffix('.extract-reconstruction-v23.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
 log=OUT/(label+'.log')
 with log.open('w',encoding='utf-8') as f:
  proc=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f);obs=psutil.Process(proc.pid)
  state['active']={'pid':proc.pid,'createTime':obs.create_time(),'commandLine':cmd,'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()};save();checkpoint();code=proc.wait()
 state['commands'].append({**state['active'],'exitCode':code,'endedAt':stamp()});state['active']=None;save();assert code==0,label
def points_for(captioned):
 points={}
 def add(frame,label):
  if 0<=frame<N:points.setdefault(frame,[]).append(label)
 if captioned:
  for c in metrics:
   first,last=c['firstFrame'],c['exclusiveEndFrame']
   for frame,name in [(first,'first'),((first+last-1)//2,'middle'),(last-1,'last'),(first-1,'before'),(last,'after')]:add(frame,f"cue{c['id']} {name}")
 for c in plan['cuts']:
  for frame,name in [(c['fromFrame'],'first'),((c['fromFrame']+c['toFrame']-1)//2,'middle'),(c['toFrame']-1,'last')]:add(frame,c['id']+' '+name)
  add(c['fromFrame']-1,c['id']+' previous cut last')
 # Both disjoint source intervals: preserve feature tags, inspect cut clearance.
 for native in [c for c in plan['cuts'] if c['kind']=='actual']:
  for localSeconds in [0,.1,.5,1,1.5,2,2.5,163/60,164/60,165/60,3,4,(native['frames']-1)/60]:
   frame=native['fromFrame']+round(localSeconds*60)
   if frame<native['toFrame']:add(frame,f"reconstruction native source{native['sourceStart']+localSeconds:.3f}s")
 return points
try:
 save();checkpoint();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
 for ref in build['outputs']:
  slug='captioned' if 'captioned.mp4' in ref['path'] else 'clean';points=points_for(slug=='captioned');frames=sorted(points)
  dest=OUT/slug;dest.mkdir();vf='select='+'+'.join(f'eq(n\\,{n})' for n in frames)
  cmd=[str(FF),'-n','-v','error','-threads','2','-reinit_filter','0','-i',str(ROOT/ref['path']),'-filter_threads','2','-vf',vf,'-fps_mode','vfr','-frames:v',str(len(frames)),'-threads','2',str(dest/'frame-%04d.png')]
  run(cmd,slug+'-extract');images=sorted(dest.glob('frame-*.png'));assert len(images)==len(frames)
  groupItems=[]
  for frame,reconstruction in zip(frames,images):
   with Image.open(reconstruction) as im:assert im.size==(1920,1080)
   item={'source':slug,'frame':frame,'seconds':frame/60,'labels':points[frame],'path':rel(reconstruction),'sha256':sha(reconstruction),'directlyViewed':False};state['items'].append(item);groupItems.append(item)
  for offset in range(0,len(groupItems),4):
   group=groupItems[offset:offset+4];board=Image.new('RGB',(1920,1180),(20,20,24));draw=ImageDraw.Draw(board)
   for i,item in enumerate(group):
    x=i%2*960;y=i//2*590
    with Image.open(ROOT/item['path']) as im:tile=im.convert('RGB').resize((960,540),Image.Resampling.LANCZOS)
    board.paste(tile,(x,y+50));draw.text((x+8,y+8),f"{slug} f{item['frame']} {item['seconds']:.3f}s | {item['labels'][0]}",font=font,fill='white')
   reconstruction=dest/f'board-{offset//4+1:03d}.png';board.save(reconstruction);state['boards'].append({'source':slug,'path':rel(reconstruction),'sha256':sha(reconstruction),'frames':[x['frame'] for x in group],'directlyViewed':False});save()
  print(json.dumps({'source':slug,'images':len(images),'boards':(len(images)+3)//4}),flush=True)
 state['status']='encoded-samples-ready';state['endedAt']=stamp();save();checkpoint();print(json.dumps({'status':state['status'],'images':len(state['items']),'boards':len(state['boards']),'allFinalPixelsReviewed':False}),flush=True)
except Exception as e:
 state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise
