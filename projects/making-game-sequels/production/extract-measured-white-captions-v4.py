"""Review every measured white caption intersection and paragraph transition locally."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,subprocess,time,traceback
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v4'
DEST=WORK/'timed-white-cues-local-v4';assert not DEST.exists();DEST.mkdir()
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
layout=read(WORK/'caption-layout-v4.json');white=read(ROOT/'motion-canvas/src/projects/making-game-sequels/timed-white-reel-plan-v4.json')
state=dict(schemaVersion=1,startedAt=now(),pid=os.getpid(),sessionId=None,status='CPU-measured-white-cuts-and-literal-caption-pixels',threads=2,activeTasks=[],cuts=[],images=[],sheets=[],newGitImages=0,finalVideoApproved=False)
def write(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(30):
  try:t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p);return
  except OSError:
   if n==29:raise
   time.sleep(.1)
def save():
 if (DEST/'session.json').exists():state['sessionId']=read(DEST/'session.json')['sessionId']
 write(DEST/'execution.json',state)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='making-game-sequels')
 i.update(stage='current13-guided60-measured-white-caption-pixels-preparing',updatedAt=now())
 i['execution'].update(observedAt=i['updatedAt'],status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],activeTasks=state['activeTasks'],cpuProductionJobs=0 if 'endedAt' in state else 1,gpuSynthesisJobs=0,renderJobs=0,uploads=0,state=rel(DEST/'execution.json'))
 q['updatedAt']=i['updatedAt'];write(qp,q)
 for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels/latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','execution','updatedAt']:d[k]=i[k]
  write(p,d)
def run(args,log,kind):
 with log.open('wb') as fh:
  c=subprocess.Popen(args,cwd=WORK,stdout=fh,stderr=fh,creationflags=subprocess.CREATE_NO_WINDOW)
  state['activeTasks']=[dict(kind=kind,pid=c.pid,log=rel(log),command=args)];save();code=c.wait()
 state['activeTasks']=[];assert code==0,(code,log)
 assert not log.read_text().strip(),log
def probe(p):
 d=json.loads(subprocess.check_output([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
 v=d['streams'][0];assert len(d['streams'])==1 and v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='60/1'
 return int(v['nb_read_frames']),d
try:
 save();reel=ROOT/'shared/output/motion-canvas/making-game-sequels-timed-white-v4.mp4';count,pr=probe(reel);assert count==white['totalFrames']==13945
 state['reel']=dict(path=rel(reel),sha256=sha(reel),frames=count,probe=pr,sourceAudioStreams=0)
 run([FF,'-v','error','-nostdin','-threads','2','-i',str(reel),'-f','null','-'],DEST/'reel.decode.log','CPU-whole-white-decode')
 for row in white['rows']:
  folder=DEST/row['id'];folder.mkdir();out=folder/'clean-white.mp4';a=row['reelStartFrame'];z=a+row['frames']
  run([FF,'-v','error','-nostdin','-threads','2','-i',str(reel),'-an','-vf',f'trim=start_frame={a}:end_frame={z},setpts=PTS-STARTPTS','-frames:v',str(row['frames']),'-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p',str(out)],folder/'encode.log','CPU-exact-white-split')
  n,p=probe(out);assert n==row['frames']
  run([FF,'-v','error','-nostdin','-threads','2','-i',str(out),'-f','null','-'],folder/'decode.log','CPU-white-cut-decode')
  state['cuts'].append(dict(row,video=rel(out),sha256=sha(out),probe=p,wholeDecodeExitCode=0,audioStreams=0,finalPixelsApproved=False))
  points={0:dict(anchors=['first'],cues=[]),row['frames']//2:dict(anchors=['middle'],cues=[]),row['frames']-1:dict(anchors=['last'],cues=[])}
  for r in layout['rows']:
   if r['segment']==row['id']:points.setdefault(r['localFrame'],dict(anchors=[],cues=[]))['cues'].append(r['cue'])
  for t in row['paragraphEnds']:
   for n in [round(t*60)-1,round(t*60),round(t*60)+1]:
    if 0<=n<row['frames']:points.setdefault(n,dict(anchors=[],cues=[]))['anchors'].append('PCM-paragraph-edge')
  select='+'.join(f'eq(n\\,{n})' for n in sorted(points))
  vf=f"setpts=PTS+{row['finalStartFrame']/60:.9f}/TB,subtitles=captions.ko.candidate.v4.ass,select='{select}'"
  run([FF,'-v','error','-nostdin','-threads','2','-filter_threads','1','-i',str(out),'-vf',vf,'-fps_mode','passthrough','-frames:v',str(len(points)),str(folder/'pixel-%03d.png')],folder/'pixels.log','CPU-literal-white-caption-pixels')
  files=sorted(folder.glob('pixel-*.png'));assert len(files)==len(points)
  for f,n in zip(files,sorted(points)):state['images'].append(dict(path=rel(f),sha256=sha(f),segment=row['id'],localFrame=n,globalFrame=row['finalStartFrame']+n,cueIds=points[n]['cues'],anchors=points[n]['anchors'],directlyRead=False))
  save();print('White cuts '+str(len(state['cuts']))+'/7',flush=True)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 for off in range(0,len(state['images']),6):
  subset=state['images'][off:off+6];im=Image.new('RGB',(1920,1740),'white');draw=ImageDraw.Draw(im)
  for k,r in enumerate(subset):
   x,y=k%2*960,k//2*580
   with Image.open(ROOT/r['path']) as raw:im.paste(raw.resize((960,540)),(x,y+40))
   draw.text((x+7,y+7),f'{off+k+1:03d} {r["segment"]} n{r["localFrame"]} cue{r["cueIds"]}',font=font,fill='black')
  p=DEST/f'white-sheet-{off//6+1:03d}.jpg';im.save(p,quality=94);state['sheets'].append(dict(path=rel(p),sha256=sha(p),imageIndices=list(range(off+1,off+len(subset)+1)),directlyRead=False))
 state.update(endedAt=now(),exitCode=0,status='closed-measured-white-pixels-awaiting-direct-review',activeTasks=[]);save()
 print(json.dumps(dict(cuts=len(state['cuts']),images=len(state['images']),sheets=len(state['sheets']),newGitImages=0)))
except BaseException:
 state.update(endedAt=now(),exitCode=1,status='closed-measured-white-pixel-preparation-failed',error=traceback.format_exc(),activeTasks=[]);save();raise
