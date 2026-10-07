"""Render unchanged production ASS onto authored sparse preflight frames using their actual final PTS."""
from pathlib import Path
import json,hashlib,subprocess,sys,datetime
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1];revision=sys.argv[2] if len(sys.argv)>2 else 'v2';folder=ROOT/'projects'/slug/'production/visual-depth-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=folder/f'white-preflight-{revision}-local';dest=folder/f'white-caption-preflight-{revision}-local'
resume='--resume-observed-expression-failure' in sys.argv
if dest.exists() and not (resume and not (dest/'index.json').exists() and not list(dest.glob('frame-*.png'))):raise RuntimeError('Preserve existing captioned preflight')
plan=read(ROOT/'motion-canvas/src/projects'/slug/'depth-reel-plan-v1.json');rows={r['id']:r for r in plan['rows']}
execution=read(folder/f'white-lookdev-execution-{revision}.json');files=list(raw.glob('*.png'))
source=ROOT/'motion-canvas/src/projects'/slug/'depth-explanations-v1.tsx'
if any(r['sourceSha256']!=sha(source) for r in execution['completed']):raise RuntimeError('Source changed')
version='measured-edit-v3' if slug=='game-reward-planning' else 'final-v2' if slug=='making-game-sequels' else 'final-v1';ass=ROOT/'projects'/slug/'production'/version/'captions.ko.ass'
if not ass.is_file():raise RuntimeError('Inspect actual caption source before creating state')
globalFrame=lambda p:rows[p.stem.rsplit('-',1)[0]]['startFrame']+int(p.stem.rsplit('-',1)[1])
files.sort(key=globalFrame)
points=[]
for p in files:
 id,f=p.stem.rsplit('-',1);r=rows[id];points.append(r['startFrame']+int(f))
dest.mkdir(exist_ok=resume)
state=dict(slug=slug,revision=revision,status='running',sourceSha256=sha(source),completed=[],allFinalPixelsReviewed=False,chunkSize=24)
if resume:
 old=dest/'execution.json'
 if old.exists():
  history=dest/'execution-missing-ass-failure.json'
  if history.exists():raise RuntimeError('Inspect preserved failure before another retry')
  history.write_bytes(old.read_bytes())
  (dest/'chunk-00.log').rename(dest/'chunk-00-missing-ass.log')
 state['previousObservedFailure']=dict(exitCode=4294967274,imagesCreated=0,preservedConcat='preflight-concat.txt',actualCause='Reward production uses measured-edit-v3/captions.ko.ass; final-v1/captions.ko.ass does not exist. Actual libass missing-track error preserved.',inferredLongExpressionCauseRejected=True,noPriorPixelsOverwritten=True)
def save(): (dest/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
save()
for start in range(0,len(files),24):
 batch=files[start:start+24];pts=points[start:start+24];concat=dest/f'preflight-concat-{start//24:02}.txt'
 concat.write_text('\n'.join("file '"+p.as_posix()+"'\nduration 0.0166666667" for p in batch)+'\n','utf-8')
 expr=str(pts[-1])
 for i in reversed(range(len(pts)-1)):expr=f'if(eq(N,{i}),{pts[i]},{expr})'
 filters="settb=1/60,setpts='"+expr+"',ass='"+ass.relative_to(ROOT).as_posix()+"'"
 cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-v','error','-threads','2','-reinit_filter','0','-f','concat','-safe','0','-i',str(concat),'-vf',filters,'-fps_mode','passthrough','-threads','1','-start_number',str(start+1),str(dest/'frame-%04d.png')]
 with (dest/f'chunk-{start//24:02}.log').open('w',encoding='utf-8') as log:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000);state.update(activePid=p.pid,command=cmd);save();code=p.wait()
 state['completed'].append(dict(start=start,frames=len(batch),exitCode=code));save()
 if code:state.update(status='failed',error='Bounded caption overlay failed');save();raise RuntimeError('Inspect exact chunk log')
rendered=sorted(dest.glob('frame-*.png'))
if len(rendered)!=len(files):raise RuntimeError('Caption preflight count mismatch')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22);boards=[]
for start in range(0,len(files),6):
 board=Image.new('RGB',(1920,1722),'#edf0f2');d=ImageDraw.Draw(board);entries=[]
 for i,j in enumerate(range(start,min(start+6,len(files)))):
  x=i%2*960;y=i//2*574;d.text((x+10,y+3),files[j].stem+' | final '+str(points[j]),font=font,fill='black');board.paste(Image.open(rendered[j]).convert('RGB').resize((960,540)),(x,y+34));entries.append(dict(raw=files[j].relative_to(ROOT).as_posix(),rawSha256=sha(files[j]),frame=points[j],file=rendered[j].relative_to(ROOT).as_posix(),sha256=sha(rendered[j])))
 p=dest/f'board-{start//6+1:02}.jpg';board.save(p,quality=94);boards.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),frames=entries))
(dest/'index.json').write_text(json.dumps(dict(slug=slug,status='actual-ass-preflight-awaiting-direct-reading',sourceSha256=sha(source),ass=ass.relative_to(ROOT).as_posix(),assSha256=sha(ass),frames=len(files),boards=boards,allFinalPixelsReviewed=False),ensure_ascii=False,indent=2)+'\n','utf-8')
state.update(status='actual-ass-preflight-awaiting-direct-reading',activePid=None);save()
print(json.dumps(dict(slug=slug,frames=len(files),boards=len(boards),allFinalPixelsReviewed=False)))
