"""New two-cut correction and measured white pixels; preserve completed media."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,subprocess,time,traceback,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v6'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
MODE=sys.argv[1];assert MODE in ['two','white']
DEST=WORK/('two-lower-crops-local' if MODE=='two' else 'timed-white-cues-local');assert not DEST.exists();DEST.mkdir()
plan=read(WORK/'plan.json');layout=read(WORK/'caption-layout-v1.json')
state=dict(startedAt=now(),pid=os.getpid(),sessionId=None,status='CPU-two-crops' if MODE=='two' else 'CPU-timed-white-split-and-pixels',
 activeTasks=[],cuts=[],images=[],sheets=[],planSha256=sha(WORK/'plan.json'),captionLayoutSha256=sha(WORK/'caption-layout-v1.json'),newGitImages=0,finalApproved=False)
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
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons')
 item.update(stage='current15-v6-timed-white-and-final-framing-review',updatedAt=now(),nextAction='Read the new two-cut framing and all measured white/caption pixels; preserve all current PCM and completed cuts before final synchronization and mix QA.')
 item['execution'].update(observedAt=now(),phase=item['stage'],status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive='endedAt' not in state,
  activeTasks=state['activeTasks'],cpuProductionJobs=0 if 'endedAt' in state else 1,gpuSynthesisJobs=0,renderJobs=0,uploads=0,state=rel(DEST/'execution.json'))
 q['updatedAt']=now();write(qp,q)
 for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','execution','updatedAt','nextAction']:d[k]=item[k]
  write(p,d)
def run(args,log,kind):
 with log.open('wb') as fh:
  c=subprocess.Popen(args,cwd=WORK,stdout=fh,stderr=fh,creationflags=subprocess.CREATE_NO_WINDOW)
  state['activeTasks']=[dict(kind=kind,pid=c.pid,log=rel(log))];save();code=c.wait()
 state['activeTasks']=[];assert code==0,(code,log)
 assert not log.read_text().strip(),log
def probe(file):
 d=json.loads(subprocess.check_output([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(file)]))
 v=d['streams'][0];assert v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='60/1' and len(d['streams'])==1
 return int(v['nb_read_frames']),d
def samples(row,file):
 points={0:dict(anchors=['first'],cues=[]),row['frames']//2:dict(anchors=['middle'],cues=[]),row['frames']-1:dict(anchors=['last'],cues=[])}
 for r in layout['rows']:
  if r['segment']==row['id']:points.setdefault(r['localFrame'],dict(anchors=[],cues=[]))['cues'].append(r['cue'])
 if MODE=='two':
  for n in range(0,row['frames'],15):points.setdefault(n,dict(anchors=['dense-lower-avatar'],cues=[]))
 else:
  for t in row['paragraphEnds']:
   for n in [round(t*60)-1,round(t*60),round(t*60)+30]:
    if 0<=n<row['frames']:points.setdefault(n,dict(anchors=['paragraph-transition'],cues=[]))
 folder=DEST/row['id'];folder.mkdir();select='+'.join(f'eq(n\\,{n})' for n in sorted(points))
 vf=f"setpts=PTS+{row['startFrame']/60:.9f}/TB,subtitles=captions.ko.candidate.ass,select='{select}'"
 run([FF,'-v','error','-nostdin','-threads','2','-i',str(file),'-vf',vf,'-fps_mode','passthrough','-frames:v',str(len(points)),str(folder/'sample-%03d.png')],folder/'pixels.log','CPU-new-pixels')
 files=sorted(folder.glob('sample-*.png'));assert len(files)==len(points)
 for f,n in zip(files,sorted(points)):
  state['images'].append(dict(path=rel(f),sha256=sha(f),cut=row['id'],localFrame=n,globalFrame=row['startFrame']+n,cueIds=points[n]['cues'],anchorRoles=points[n]['anchors'],directlyRead=False))
def sheets():
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 for off in range(0,len(state['images']),6):
  subset=state['images'][off:off+6];im=Image.new('RGB',(1920,1740),'white');draw=ImageDraw.Draw(im)
  for k,r in enumerate(subset):
   x,y=k%2*960,k//2*580
   with Image.open(ROOT/r['path']) as raw:im.paste(raw.resize((960,540)),(x,y+40))
   draw.text((x+7,y+7),f'{off+k+1:03d} {r["cut"]} n{r["localFrame"]} cue{r["cueIds"]}',font=font,fill='black')
  out=DEST/f'review-sheet-{off//6+1:03d}.jpg';im.save(out,quality=94)
  state['sheets'].append(dict(path=rel(out),sha256=sha(out),imageIndices=list(range(off+1,off+len(subset)+1)),directlyRead=False))
try:
 save()
 if MODE=='two':
  compiled=read(WORK/'native-review-v1/compiled.json')
  for cid in ['10-p1-action-40-2010-2130','10-p1-action-41-2160-2310']:
   c=next(x for x in compiled['cuts'] if x['id']==cid);assert sha(ROOT/c['video'])==c['sha256']
   out=DEST/f'{cid}.mp4';crop='crop=1440:810:240:270,scale=1920:1080,setsar=1'
   run([FF,'-v','error','-nostdin','-threads','2','-i',str(ROOT/c['video']),'-an','-vf',crop,'-frames:v',str(c['frames']),'-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p',str(out)],DEST/f'{cid}.encode.log','CPU-two-crop-encode')
   count,p=probe(out);assert count==c['frames'];run([FF,'-v','error','-nostdin','-threads','2','-i',str(out),'-f','null','-'],DEST/f'{cid}.decode.log','CPU-two-crop-decode')
   c=dict(c,video=rel(out),sha256=sha(out),cropFilter='crop=1440:810:240:270',filter=crop,wholeDecodeExitCode=0,audioStreams=0)
   state['cuts'].append(c);samples(c,out);save()
 else:
  reel=ROOT/'shared/output/motion-canvas/avoid-game-comparisons-timed-white-v6.mp4'
  count,p=probe(reel);assert count==12552
  state['reel']=dict(path=rel(reel),sha256=sha(reel),probe=p,frames=count,actualUiStatus='render-returned-verify-file',renderPid=17320,renderPidClosed=True)
  run([FF,'-v','error','-nostdin','-threads','2','-i',str(reel),'-f','null','-'],DEST/'reel.decode.log','CPU-white-full-decode')
  white=read(ROOT/'motion-canvas/src/projects/avoid-game-comparisons/timed-white-reel-plan-v6.json')
  for row in white['rows']:
   row=dict(row,startFrame=row['finalStartFrame']);out=DEST/f'{row["id"]}.mp4';start=row['reelStartFrame'];end=start+row['frames']
   run([FF,'-v','error','-nostdin','-threads','2','-i',str(reel),'-an','-vf',f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS','-frames:v',str(row['frames']),'-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p',str(out)],DEST/f'{row["id"]}.encode.log','CPU-white-exact-split')
   n,p=probe(out);assert n==row['frames']
   run([FF,'-v','error','-nostdin','-threads','2','-i',str(out),'-f','null','-'],DEST/f'{row["id"]}.decode.log','CPU-white-cut-decode')
   row.update(video=rel(out),sha256=sha(out),wholeDecodeExitCode=0,audioStreams=0,finalPixelsApproved=False)
   state['cuts'].append(row);samples(row,out);save();print(f'White cuts {len(state["cuts"])}/14',flush=True)
 sheets();state.update(endedAt=now(),exitCode=0,status='closed-new-pixels-awaiting-direct-read',activeTasks=[]);save()
 print(json.dumps(dict(cuts=len(state['cuts']),images=len(state['images']),sheets=len(state['sheets']))))
except BaseException:
 state.update(endedAt=now(),exitCode=1,status='closed-pixel-preparation-failed',error=traceback.format_exc(),activeTasks=[]);save();raise
