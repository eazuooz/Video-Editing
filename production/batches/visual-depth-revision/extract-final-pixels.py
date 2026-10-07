"""CPU-only sparse extraction of every cue and cut from the actual encoded pair."""
from pathlib import Path
import json,sys,hashlib,math,re,subprocess,datetime,os
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1];folder=ROOT/'projects'/slug/'production/visual-depth-v1'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
baseline=read(folder/'baseline.json');depth=read(ROOT/'motion-canvas/src/projects'/slug/'depth-reel-plan-v1.json');plan=read(ROOT/(depth.get('sourcePlan') or baseline['manifest']['editing'].get('scenePlan') or baseline['manifest']['paths']['timeline']))
srt=ROOT/next(f['path'] for f in baseline['files'] if f['role']=='captionsKo');points={};cues=[]
total=depth.get('finalFrames') or baseline['manifest']['finalRender']['frames']
def add(f,role):
 f=max(0,min(total-1,int(f)));points.setdefault(f,[]).append(role)
def stamp(s):
 h,m,sec,ms=map(int,re.split('[:,]',s));return h*3600+m*60+sec+ms/1000
for block in re.split(r'\r?\n\s*\r?\n',srt.read_text('utf-8-sig').strip()):
 lines=block.splitlines();a,b=lines[1].split(' --> ');start,end=stamp(a),stamp(b);cue=dict(id=int(lines[0]),start=start,end=end,text='\n'.join(lines[2:]));cues.append(cue)
 for label,f in [('start',math.ceil(start*60)),('middle',round((start+end)*30)),('end',math.ceil(end*60)-1)]:add(f,dict(kind='cue-'+label,**cue))
cuts=plan.get('cuts')
if not isinstance(cuts,list):cuts=plan.get('nativeCuts')
if not isinstance(cuts,list):cuts=[segment for scene in plan.get('scenes',[]) for segment in scene.get('segments',[]) if segment.get('classification','').startswith('actual')]
if not cuts:raise RuntimeError('Actual game cut coverage required; inspect the exact source-plan schema')
for c in cuts:
 start=c.get('startFrame',c.get('finalStartFrame'))
 if start is None and 'timelineStart' in c:start=round(c['timelineStart']*60)
 end=c.get('endFrameExclusive',c.get('endFrame',c.get('finalEndFrame')))
 if end is None:end=start+c.get('frames',c.get('durationFrames'))
 if not(120<=start<end<=total-600):raise RuntimeError('Actual cut timing outside current body '+c['id'])
 for label,f in [('start',start),('end',end-1)]:add(f,dict(kind='cut-'+label,id=c['id']))
for r in depth['rows']:
 for f in [0,r['frames']-1,*[min(r['frames']-1,s+d) for s in r['paragraphStarts'] for d in [60,150]]]:add(r.get('startFrame',r.get('finalStartFrame'))+f,dict(kind='depth-motion',id=r['id'],localFrame=f))
for f in [0,119,total-601,total-600,total-300,total-1]:add(f,dict(kind='branding-or-outro'))
frames=sorted(points);dest=folder/'encoded-pixels-local';dest.mkdir(exist_ok=True)
out=dict(status='plan-only',slug=slug,cueCount=len(cues),cutCount=len(cuts),uniqueFrames=len(frames),totalFrames=total,srtSha256=sha(srt),frames=[dict(frame=f,roles=points[f]) for f in frames],allFinalPixelsReviewed=False)
write(folder/'encoded-pixel-plan.json',out)
if '--plan-only' in sys.argv:print(json.dumps(dict(cues=len(cues),cuts=len(cuts),frames=len(frames))));sys.exit()
qa=read(folder/'pair-technical-qa.json');pair=next(o for o in qa['outputs'] if o['variant']=='captioned');video=ROOT/pair['path']
if sha(video)!=pair['sha256']:raise RuntimeError('Encoded pair hash changed')
if (dest/'index.json').exists() or list(dest.glob('frame-*.png')):raise RuntimeError('Inspect existing extraction instead of repeating')
state=dict(status='running',pid=os.getpid(),threads=2,gpu=0,videoSha256=pair['sha256'],allFinalPixelsReviewed=False);write(folder/'encoded-pixel-execution.json',state)
ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';selection='+'.join(f'eq(n,{f})' for f in frames)
cmd=[ff,'-hide_banner','-loglevel','warning','-threads','2','-i',str(video),'-vf',"select='"+selection+"'",'-vsync','0','-threads','1',str(dest/'frame-%05d.png')]
with open(folder/'encoded-pixel-extraction.log','w',encoding='utf-8') as log:
 p=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000);state.update(activePid=p.pid,command=cmd);write(folder/'encoded-pixel-execution.json',state);code=p.wait()
if code:raise RuntimeError('Extraction failed; preserve outputs and log')
files=sorted(dest.glob('frame-*.png'))
if len(files)!=len(frames):raise RuntimeError('Sparse extraction count differs')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21);boards=[]
for start in range(0,len(frames),6):
 board=Image.new('RGB',(1920,1722),'#e8edf0');d=ImageDraw.Draw(board);rows=[]
 for i,j in enumerate(range(start,min(start+6,len(frames)))):
  x=i%2*960;y=i//2*574;im=Image.open(files[j]).convert('RGB');im.thumbnail((960,540));board.paste(im,(x,y+34));label=f"{j+1:03} | frame {frames[j]} | "+','.join(str(r.get('id','')) for r in points[frames[j]]);d.text((x+12,y+3),label,font=font,fill='#202020');rows.append(dict(frame=frames[j],file=files[j].relative_to(ROOT).as_posix(),sha256=sha(files[j]),roles=points[frames[j]]))
 path=dest/f'board-{start//6+1:03}.jpg';board.save(path,quality=94);boards.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),frames=rows))
write(dest/'index.json',dict(status='extracted-awaiting-direct-reading',videoSha256=pair['sha256'],srtSha256=out['srtSha256'],uniqueFrames=len(frames),cueCount=len(cues),boards=boards,allFinalPixelsReviewed=False));state.update(status='extracted-awaiting-direct-reading',frames=len(frames),boards=len(boards));write(folder/'encoded-pixel-execution.json',state);print(json.dumps(dict(frames=len(frames),boards=len(boards))))
