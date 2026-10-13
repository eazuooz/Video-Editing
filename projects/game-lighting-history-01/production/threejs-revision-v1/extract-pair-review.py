"""One changed-encoded-pixel pass; unchanged closed GOP evidence is reused."""
import pathlib,json,hashlib,datetime,math,os,sys
import av,psutil
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/threejs-revision-v1/pair-caption-decoder-v3';D=O/'encoded-review';BASE=P/'production/local/final-edit-v1'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 plan=rd(O/'plan.json');exe=rd(O/'execution.json');caps=rd(BASE/'captions.json')['cues']['ko'];points={}
 def add(f,reason):
  if 0<=f<plan['frames']:points.setdefault(f,[]).append(reason)
 def edge(t):return math.ceil(math.floor(t*100+1e-7)*.6-1e-7)
 for a,z in exe['captionPatchRanges']:
  for f in [a-1,a,z-1,z]:add(f,'closed-GOP-join')
  for n in plan['nodes']:
   lo,hi=max(a,n['startFrame']),min(z,n['endFrame'])
   if hi<=lo:continue
   add(lo,'cut-first:'+n['id']);add(hi-1,'cut-last:'+n['id'])
   for c in caps:
    ca,cz=max(lo,edge(c['startSeconds'])),min(hi,edge(c['endSeconds']))
    if cz>ca:add((ca+cz-1)//2,'cue:'+str(c['index']))
   off=n['startFrame']
   for part in n.get('rendererRevisionParts',[]):
    if part['changed']:
     for f in [off,off+part['frames']//2,off+part['frames']-1]:add(f,'asset:'+part['key'])
    off+=part['frames']
 rows=[]
 for f,reasons in sorted(points.items()):
  n=next(n for n in plan['nodes'] if n['startFrame']<=f<n['endFrame']);rows.append(dict(frame=f,reasons=reasons,node=n['id'],role=n['role'],cueIds=[c['index'] for c in caps if edge(c['startSeconds'])<=f<edge(c['endSeconds'])]))
 request=dict(points=rows,changedRanges=exe['captionPatchRanges'],planSha256=sha(O/'plan.json'),assSha256=sha(BASE/'captions.ko.ass'),reusedUnchangedEvidence='production/local/final-edit-v1/repair-v2/combined-review.json',allImagesLocalOnly=True)
 if '--plan-only' in sys.argv:wr(O/'encoded-review-request.json',request);print(len(rows),'planned frames');return
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert exe['status']=='complete-awaiting-changed-encoded-pixels'
 src=O/'captioned.mp4';assert sha(src)==exe['outputs']['captioned']['sha256']
 assert not D.exists();D.mkdir()
 state=dict(status='extracting',pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,sourceSha256=sha(src),request=request,images=[],boards=[],allFinalPixelsApproved=False);wr(D/'execution.json',state)
 # Seek to the preceding keyframe and decode actual encoded frame; no re-encoding.
 with av.open(str(src)) as c:
  s=c.streams.video[0];s.thread_type='SLICE';s.codec_context.thread_count=2
  for i,row in enumerate(rows):
   c.seek(row['frame']*1500,stream=s,backward=True,any_frame=False)
   frame=next(f for f in c.decode(s) if f.pts>=row['frame']*1500);assert frame.pts==row['frame']*1500
   p=D/f'frame-{i+1:04}.png';frame.to_image().save(p);state['images'].append(dict(row,path=p.relative_to(R).as_posix(),sha256=sha(p),directlyReviewed=False))
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
 for b in range(0,len(rows),6):
  board=Image.new('RGB',(1920,1740),'#141414');draw=ImageDraw.Draw(board)
  for j,row in enumerate(state['images'][b:b+6]):
   x=j%2*960;y=j//2*580
   with Image.open(R/row['path']) as im:board.paste(im.convert('RGB').resize((960,540)),(x,y+40))
   draw.text((x+8,y+7),f"{b+j+1:04} f{row['frame']} {row['node']} cue{row['cueIds']}",font=font,fill='white')
  p=D/f'board-{b//6+1:03}.jpg';board.save(p,quality=94);state['boards'].append(dict(path=p.relative_to(R).as_posix(),sha256=sha(p),directlyReviewed=False))
 state.update(status='complete-awaiting-direct-review',exitCode=0,endedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());wr(D/'execution.json',state);print(len(rows),'frames',len(state['boards']),'boards')
if __name__=='__main__':main()
