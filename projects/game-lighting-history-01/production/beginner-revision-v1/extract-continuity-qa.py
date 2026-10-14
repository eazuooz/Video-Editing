"""One current encoded-pixel pass: every cue/cut plus changed motion phases."""
import pathlib,json,hashlib,datetime,math,os,sys
import av,psutil
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/continuity-v2';D=O/'pair/encoded-review'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 plan=rd(O/'plan.json');caps=rd(O/'captions.json')['cues']['ko'];scenes={s['key']:s for s in rd(H/'measured-scene-plan.json')['scenes']};points={}
 def add(f,reason):
  if 0<=f<plan['frames']:points.setdefault(f,[]).append(reason)
 def edge(t):return math.ceil(math.floor(t*100+1e-7)*.6-1e-7)
 for n in plan['nodes']:
  a,z=n['startFrame'],n['endFrame'];add(a,'cut-first:'+n['id']);add(z-1,'cut-last:'+n['id'])
  for c in caps:
   lo,hi=max(a,edge(c['startSeconds'])),min(z,edge(c['endSeconds']))
   if hi>lo:add((lo+hi-1)//2,'cue:'+str(c['index']))
  if n.get('newExplanation'):
   b=scenes[n['anchor']];lo,hi=b['actionStartFrame'],b['actionEndFrame']
   if n['anchor']=='02-p4':lo,hi=678,743
   for f in [lo,(lo+hi)//2,hi]:add(a+min(f,n['frames']-1),'motion:'+n['anchor'])
  if n.get('newNative'):add((a+z-1)//2,'new-native-action:'+n['id'])
 for v in plan['voice']:add(v['startFrame'],'voice-onset:'+v['key'])
 rows=[]
 for f,reasons in sorted(points.items()):
  n=next(n for n in plan['nodes'] if n['startFrame']<=f<n['endFrame']);rows.append(dict(frame=f,reasons=reasons,node=n['id'],role=n['role'],cueIds=[c['index'] for c in caps if edge(c['startSeconds'])<=f<edge(c['endSeconds'])]))
 assert set(c['index'] for c in caps)==set(k for r in rows for k in r['cueIds'])
 request=dict(createdAt=now(),points=rows,planSha256=sha(O/'plan.json'),assSha256=sha(O/'captions.ko.ass'),cueCount=len(caps),nodeCount=len(plan['nodes']),allImagesLocalOnly=True,allDirectlyReviewed=False)
 if '--plan-only' in sys.argv:wr(O/'encoded-review-request.json',request);print(len(rows),'planned frames; no images');return
 import runpy
 runpy.run_path(str(pathlib.Path(__file__).with_name('production-authority.py')))['require_selected_production']()
 exe=rd(O/'pair/visual-execution.json');assert exe['status']=='complete-awaiting-mix-and-pixel-review'
 src=O/'pair/captioned-video.mp4';assert sha(src)==exe['outputs']['captioned-video.mp4'];assert not D.exists();D.mkdir()
 state=dict(status='extracting',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,sourceSha256=sha(src),request=request,images=[],boards=[],allFinalPixelsApproved=False)
 wr(D/'execution.json',state)
 with av.open(str(src)) as c:
  s=c.streams.video[0];s.thread_type='SLICE';s.codec_context.thread_count=2
  for i,row in enumerate(rows):
   c.seek(row['frame']*1500,stream=s,backward=True,any_frame=False);frame=next(f for f in c.decode(s) if f.pts>=row['frame']*1500);assert frame.pts==row['frame']*1500
   p=D/f'frame-{i+1:04}.png';frame.to_image().save(p);state['images'].append(dict(row,path=p.relative_to(R).as_posix(),sha256=sha(p),directlyReviewed=False))
   if i%60==59:wr(D/'execution.json',state)
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
 for b in range(0,len(rows),6):
  board=Image.new('RGB',(1920,1740),'#141414');draw=ImageDraw.Draw(board)
  for j,row in enumerate(state['images'][b:b+6]):
   x=j%2*960;y=j//2*580
   with Image.open(R/row['path']) as im:board.paste(im.convert('RGB').resize((960,540)),(x,y+40))
   draw.text((x+8,y+7),f"{b+j+1:04} f{row['frame']} {row['node']} cue{row['cueIds']}",font=font,fill='white')
  p=D/f'board-{b//6+1:03}.jpg';board.save(p,quality=94);state['boards'].append(dict(path=p.relative_to(R).as_posix(),sha256=sha(p),imageIndices=list(range(b+1,min(b+7,len(rows)+1))),directlyReviewed=False))
 state.update(status='complete-awaiting-direct-review',exitCode=0,endedAt=now());wr(D/'execution.json',state);print(len(rows),'frames',len(state['boards']),'boards')
if __name__=='__main__':main()
