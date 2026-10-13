"""One encoded-pixel pass covering each cue/cut intersection and every cut edge."""
import pathlib,json,hashlib,datetime,subprocess,os,math,sys
import psutil
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1';D=O/'encoded-qa'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sh(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 plan=rd(O/'plan.json');caps=rd(O/'captions.json');points={}
 def add(f,reason):
  if 0<=f<plan['frames']:points.setdefault(f,[]).append(reason)
 for n in plan['nodes']:
  a,z=n['startFrame'],n['endFrame'];add(a,'first:'+n['id']);add(z-1,'last:'+n['id'])
  for c in caps['cues']['ko']:
   ca=math.ceil(math.floor(c['startSeconds']*100+1e-7)*.6-1e-7);cz=math.ceil(math.floor(c['endSeconds']*100+1e-7)*.6-1e-7)
   first,end=max(a,ca),min(z,cz)
   if end>first:add((first+end-1)//2,'cue:'+str(c['index']))
 for v in plan['voice']:add(v['startFrame'],'voice:'+v['key'])
 for a in rd(O/'retained-motion-points.json'):
  for f in [a['fromFrame'],(a['fromFrame']+a['toFrame'])//2,a['toFrame']]:add(f,'motion:'+a['key'])
 # Exact console input, unlike its earlier autocomplete and later closed state.
 add(115159,'actual-console-input')
 rows=[]
 for f,reasons in sorted(points.items()):
  n=next(n for n in plan['nodes'] if n['startFrame']<=f<n['endFrame'])
  rows.append(dict(frame=f,reasons=reasons,node=n['id'],role=n['role'],cueIds=[c['index'] for c in caps['cues']['ko'] if math.floor(c['startSeconds']*100+1e-7)/100<=f/60<math.floor(c['endSeconds']*100+1e-7)/100]))
 assert set(c['index'] for c in caps['cues']['ko'])==set(k for r in rows for k in r['cueIds'])
 request=dict(createdAt=now(),planSha256=sh(O/'plan.json'),assSha256=sh(O/'captions.ko.ass'),cueCount=len(caps['cues']['ko']),nodes=len(plan['nodes']),points=rows,allImagesLocalOnly=True,allDirectlyReviewed=False)
 if '--plan-only' in sys.argv:
  wr(O/'encoded-qa-request.json',request);print(len(rows),'planned frames; no extraction');return
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 pair=rd(O/'pair-execution.json');assert pair['status']=='complete-awaiting-current-encoded-pixel-review'
 source=O/'captioned.mp4';assert pair['outputs']['captioned']['sha256']==sh(source)
 assert not D.exists();D.mkdir()
 state=dict(status='extracting',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,sourceSha256=sh(source),request=request,images=[],boards=[],allFinalPixelsApproved=False)
 wr(D/'execution.json',state)
 expression='+'.join(f'eq(n\\,{r["frame"]})' for r in rows)
 cmd=[FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(source),'-an','-filter_threads','1','-vf',f"select='{expression}'",'-fps_mode','passthrough','-threads','2','-frames:v',str(len(rows)),str(D/'frame-%04d.png')]
 with (D/'extract.log').open('w') as log:rc=subprocess.call(cmd,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 assert rc==0 and len(list(D.glob('frame-*.png')))==len(rows)
 for i,r in enumerate(rows):
  f=D/f'frame-{i+1:04}.png';state['images'].append(dict(r,path=f.relative_to(R).as_posix(),sha256=sh(f),directlyReviewed=False))
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
 for b in range(0,len(rows),6):
  board=Image.new('RGB',(1920,1740),'#141414');draw=ImageDraw.Draw(board)
  for j,r in enumerate(state['images'][b:b+6]):
   x=j%2*960;y=j//2*580
   with Image.open(R/r['path']) as im:board.paste(im.convert('RGB').resize((960,540)),(x,y+40))
   draw.text((x+8,y+7),f"{b+j+1:04} f{r['frame']} {r['node']} {r['role']} cue{r['cueIds']}",font=font,fill='white')
  f=D/f'board-{b//6+1:03}.jpg';board.save(f,quality=94);state['boards'].append(dict(path=f.relative_to(R).as_posix(),sha256=sh(f),imageIndices=list(range(b+1,min(b+7,len(rows)+1))),directlyReviewed=False))
 state.update(status='complete-awaiting-direct-review',exitCode=0,endedAt=now());wr(D/'execution.json',state);print('Extracted',len(rows),'frames',len(state['boards']),'boards')
if __name__=='__main__':main()
