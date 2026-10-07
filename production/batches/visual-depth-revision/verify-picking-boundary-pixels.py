"""Compare decoded body pixels to the already directly read pair, then extract every changed body sample and outro checkpoints."""
from pathlib import Path
import json,hashlib,subprocess,datetime,os
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];slug='picking-sides';folder=ROOT/'projects'/slug/'production/visual-depth-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
qa=read(folder/'pair-technical-qa.json');oldqa=read(folder/'pair-technical-qa-pre-outro-fix.json')
reject=read(folder/'encoded-pixel-direct-review-pre-outro-fix.json')
if reject['requiredFix']!='outro-source-frame-0-old-PPT-flash' or reject['boardsRead']!=100:raise RuntimeError('Exact completed earlier direct review required')
new=folder/(slug+'.captioned.review.mp4');old=folder/(slug+'.captioned.pre-outro-fix.review.mp4')
if sha(new)!=next(o['sha256'] for o in qa['outputs'] if o['variant']=='captioned') or sha(old)!=reject['videoSha256']:raise RuntimeError('Pair identity changed')
body=qa['expectedFrames']-600; statepath=folder/'boundary-pixel-execution.json'
if statepath.exists():raise RuntimeError('Inspect existing boundary comparison; do not repeat')
state=dict(status='running',pid=os.getpid(),threads=2,gpu=0,allFinalPixelsReviewed=False)
write(statepath,state)
hashes=[]
for label,p in [('before',old),('after',new)]:
 dest=folder/(label+'-boundary-body.framemd5')
 cmd=[FF,'-v','error','-threads','2','-i',str(p),'-map','0:v:0','-an','-frames:v',str(body),'-f','framemd5',str(dest)]
 proc=subprocess.Popen(cmd,creationflags=0x08000000);state.update(stage='decoded-body-'+label,activePid=proc.pid,activeCommand=cmd);write(statepath,state)
 if proc.wait()!=0:raise RuntimeError('Decoded body hash failed')
 hashes.append([line.split(',')[-1].strip() for line in dest.read_text().splitlines() if line and not line.startswith('#')])
if any(len(h)!=body for h in hashes):raise RuntimeError('Decoded comparison body frame count mismatch')
changed=[i for i,(a,b) in enumerate(zip(*hashes)) if a!=b]
if any(f<body-8 for f in changed):raise RuntimeError('Unexpected earlier-body pixel change requires full fresh extraction')
frames=sorted(set(changed+[body-2,body-1,body,body+1,body+2,body+15,body+30,body+60,body+300,body+599]))
dest=folder/'boundary-pixels-local';dest.mkdir(exist_ok=True)
cmd=[FF,'-v','error','-threads','2','-i',str(new),'-vf','select='+ '+'.join('eq(n\\,'+str(f)+')' for f in frames),'-fps_mode','vfr',str(dest/'frame-%03d.png')]
proc=subprocess.Popen(cmd,creationflags=0x08000000);state.update(stage='new-boundary-extraction',activePid=proc.pid,activeCommand=cmd);write(statepath,state)
if proc.wait()!=0:raise RuntimeError('Boundary extraction failed')
files=sorted(dest.glob('frame-*.png'))
if len(files)!=len(frames):raise RuntimeError('Boundary sample count mismatch')
records=[];boards=[]
for i,(f,p) in enumerate(zip(frames,files)):
 records.append(dict(frame=f,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
for start in range(0,len(records),6):
 batch=records[start:start+6];im=Image.new('RGB',(1920,1722),'#eee');d=ImageDraw.Draw(im)
 for i,r in enumerate(batch):
  tile=Image.open(ROOT/r['path']).convert('RGB');tile.thumbnail((960,540));x=(i%2)*960;y=(i//2)*574;im.paste(tile,(x,y));d.text((x+10,y+548),f"frame {r['frame']} | outro-relative {r['frame']-body}",fill='#111')
 p=dest/f'board-{start//6+1:02}.jpg';im.save(p,quality=92);boards.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),frames=batch))
result=dict(status='compared-extracted-awaiting-direct-reading',videoSha256=sha(new),previousVideoSha256=sha(old),bodyFramesCompared=body,decodedBodyIdentical=not changed,changedBodyFrames=changed,previousDirectReview='encoded-pixel-direct-review-pre-outro-fix.json',sampledFrames=records,boards=boards,outroFix='outro-boundary-fix.json',allFinalPixelsReviewed=False)
write(folder/'boundary-pixel-comparison.json',result);state.update(status=result['status'],activePid=None,endedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());write(statepath,state)
print(json.dumps(dict(bodyFramesCompared=body,changedBodyFrames=changed,boards=len(boards),allFinalPixelsReviewed=False)))
