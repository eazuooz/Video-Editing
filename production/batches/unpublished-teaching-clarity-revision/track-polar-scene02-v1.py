"""Track a visible helmet in the selected cut; no inferred world coordinates."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, os
os.environ['OMP_NUM_THREADS']='2'
os.environ['OPENBLAS_NUM_THREADS']='2'
import psutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def main():
 source=LOCAL/'selected-scene02-v1/scene02.source-selected.mp4'
 statefile=OUT/'scene02-visible-track-execution-v1.json';assert not statefile.exists()
 selected=json.loads((OUT/'selected-scene02-execution-v1.json').read_text(encoding='utf-8'))
 assert selected['exitCode']==0 and sha(source)==selected['sourceCandidateSha256']
 folder=LOCAL/'scene02-track-v1';folder.mkdir(exist_ok=True)
 state={'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'createTime':psutil.Process().create_time(),'commandLine':psutil.Process().cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'status':'running','sourceSha256':sha(source),'worldCoordinateMeasurement':False,'currentMovingTrackApproved':False}
 def save():statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 save();print(json.dumps({'pid':state['pid'],'createTime':state['createTime']}),flush=True)
 command=[FF,'-hide_banner','-nostdin','-loglevel','error','-threads','2','-filter_threads','1','-i',str(source),'-vf','scale=640:360','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
 reset={0:(915/3,474/3),660:(968/3,483/3),2087:(940/3,479/3),2777:(1020/3,480/3)}
 try:
  points=[];previous=np.array(reset[0]);sampleFrames={r['frame'] for r in selected['samples']}
  log=folder/'decode.log'
  with log.open('wb') as err:
   proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=err)
   for frame in range(3403):
    raw=proc.stdout.read(640*360*3);assert len(raw)==640*360*3,(frame,len(raw))
    im=Image.frombytes('RGB',(640,360),raw)
    if frame in reset:previous=np.array(reset[frame])
    px,py=previous;left=max(215,int(px)-48);right=min(430,int(px)+48);top=max(72,int(py)-54);bottom=min(285,int(py)+54)
    a=np.array(im.crop((left,top,right,bottom)).convert('HSV'))
    mask=(a[:,:,0]>154)&(a[:,:,0]<211)&(a[:,:,1]>65)&(a[:,:,2]>32)
    lab,n=ndimage.label(mask);sizes=np.bincount(lab.ravel());objects=ndimage.find_objects(lab)
    candidates=[]
    for j,box in enumerate(objects,1):
     if box is None or not 4<=sizes[j]<=450:continue
     yy,xx=np.nonzero(lab[box]==j);x=float(xx.mean()+box[1].start+left);y=float(yy.mean()+box[0].start+top)
     distance=float(np.hypot(x-px,y-py))
     if distance<43:candidates.append((distance,x,y,int(sizes[j])))
    if candidates:
     distance,x,y,size=min(candidates)
     previous=np.array([x,y]);mode='detected'
    else:distance=None;size=0;mode='held-for-review'
    point={'frame':frame,'pts':frame*1500,'xy':[round(float(previous[0])*3,2),round(float(previous[1])*3,2)],'mode':mode,'pixels':size,'screenOnly':True}
    points.append(point)
    if frame in sampleFrames:
     out=im.resize((1920,1080));d=ImageDraw.Draw(out);x,y=point['xy'];d.ellipse((x-32,y-32,x+32,y+32),outline='#ff4444',width=5);d.line((x-45,y,x+45,y),fill='#ffd56a',width=3);d.line((x,y-45,x,y+45),fill='#ffd56a',width=3)
     out.save(folder/f"track-f{frame:04d}.png")
   assert proc.stdout.read(1)==b'';exitcode=proc.wait();assert exitcode==0
  trackfile=OUT/'scene02-visible-track-v1.json';assert not trackfile.exists()
  track={'source':rel(source),'sourceSha256':sha(source),'fps':60,'timebase':'1/90000','points':points,'target':'Visible helmet only; image pixels, not game-world position','detector':'Purple HSV component selected by proximity; held points require review','automaticTrackIsApproval':False}
  trackfile.write_text(json.dumps(track,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
  records=[{'frame':f,'path':rel(folder/f'track-f{f:04d}.png'),'sha256':sha(folder/f'track-f{f:04d}.png')} for f in sorted(sampleFrames)]
  boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
  for n in range(0,len(records),6):
   board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
   for j,r in enumerate(records[n:n+6]):
    x=j%3*640;y=j//3*390
    with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
    d.text((x+8,y+5),f"f{r['frame']} helmet screen point",font=font,fill='white')
   path=folder/f'board-{n//6+1:02d}.png';board.save(path);boards.append({'path':rel(path),'sha256':sha(path)})
  snapshot=json.loads((OUT/'baseline-protected-sha-v1.json').read_text(encoding='utf-8'));assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
  state.update(status='completed',exitCode=0,decodeExitCode=exitcode,finishedAt=datetime.now(timezone.utc).isoformat(),frames=len(points),heldFrames=sum(p['mode']!='detected' for p in points),track=rel(trackfile),trackSha256=sha(trackfile),samples=records,boards=boards,baselineUnchanged=True)
  save();print(json.dumps({'frames':len(points),'heldFrames':state['heldFrames'],'samples':len(records),'boards':len(boards),'exitCode':0}),flush=True)
 except Exception as e:state.update(status='failed',exitCode=1,exception=str(e));save();raise
if __name__=='__main__':main()
