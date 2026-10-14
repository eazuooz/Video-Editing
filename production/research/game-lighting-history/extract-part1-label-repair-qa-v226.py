"""Offline ordered encoded pixels; no browser file-protocol workaround."""
from pathlib import Path
import json,hashlib,datetime,psutil,subprocess,os
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
bank=ROOT/'production/research/game-lighting-history/local/part1-label-repair-v225';qp=bank/'review-v226/plan.json';q=read(qp);source=ROOT/q['source']['path'];q['source']['sha256']=sha(source)
e=read(B/'part1-literal-onset-asr-execution-v220.json')
if e.get('exitCode')!=0 or len(e['completed'])!=5 or not e.get('endedAt'):raise RuntimeError('Close the one recognizer before this extraction')
assert sha(source)==q['source']['sha256']
out=bank/'qa-v226';out.mkdir(exist_ok=False);points={x['frame']:list(x['labels'])for x in q['points']}
for s in q['scenes']:
 for f in range(s['fromFrame'],s['toFrame'],30):points.setdefault(f,[]).append(s['id']+' ordered-motion-0.5s')
frames=sorted(points);me=psutil.Process();state=dict(startedAt=stamp(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),plan=dict(path=rel(qp),sha256=sha(qp)),source=q['source'],status='extracting-ordered-encoded-pixels',cpuThreads=2,gpuJobs=0,localOnly=True,newGitImages=0,items=[],boards=[],actualBrowserPlaybackObserved=False,allMovingPixelsReviewed=False,allFinalCaptionPixelsReviewed=False,browserRejection='The browser rejected file:// navigation. No alternative URL/surface was used to bypass that restriction. Review uses local ffmpeg pixel extraction and view_image, without browser execution.')
sp=out/'execution.json'
def save():
 t=sp.with_name(sp.name+'.writing');t.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,sp)
save();cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-n','-v','error','-threads','2','-reinit_filter','0','-i',str(source),'-filter_threads','2','-vf','select='+'+'.join(f'eq(n\\,{f})'for f in frames),'-fps_mode','vfr','-frames:v',str(len(frames)),'-threads','2',str(out/'frame-%04d.png')]
log=out/'extract.log'
with log.open('w',encoding='utf-8')as file:
 p=subprocess.Popen(cmd,cwd=ROOT,stdout=file,stderr=file);obs=psutil.Process(p.pid);state['active']=dict(pid=p.pid,createTime=obs.create_time(),command=cmd,log=rel(log));save();code=p.wait()
state['exitCode']=code;state['active']=None;save();assert code==0
images=sorted(out.glob('frame-*.png'));assert len(images)==len(frames);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for frame,path in zip(frames,images):
 with Image.open(path)as im:assert im.size==(1920,1080)
 state['items'].append(dict(frame=frame,seconds=frame/60,labels=points[frame],path=rel(path),sha256=sha(path),directlyViewed=False))
for offset in range(0,len(images),4):
 group=state['items'][offset:offset+4];board=Image.new('RGB',(1920,1180),(20,20,24));draw=ImageDraw.Draw(board)
 for i,item in enumerate(group):
  x=i%2*960;y=i//2*590
  with Image.open(ROOT/item['path'])as im:board.paste(im.convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(x,y+50))
  draw.text((x+8,y+8),f"f{item['frame']} {item['seconds']:.3f}s | {item['labels'][0]}",font=font,fill='white')
 p=out/f'board-{offset//4+1:03d}.png';board.save(p);state['boards'].append(dict(path=rel(p),sha256=sha(p),frames=[x['frame']for x in group],directlyViewed=False))
state.update(status='ordered-source-samples-ready',endedAt=stamp());save()
print(json.dumps(dict(images=len(images),boards=len(state['boards']),exitCode=code,actualPlaybackApproved=False,finalCaptionApproval=False)))
