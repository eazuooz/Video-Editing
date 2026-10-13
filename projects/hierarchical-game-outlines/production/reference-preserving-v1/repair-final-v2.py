"""Repair one late annotation and filter-reinitialization caption loss; retain all source/voice/PPT."""
from pathlib import Path
import os,json,hashlib,datetime,subprocess,traceback
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='2'
import psutil,numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[3];STATE=P/'final-repair-execution-v2.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rel=lambda p:p.relative_to(ROOT).as_posix()
assert not STATE.exists(),'Inspect actual state; no duplicate repair.'
control=read(ROOT/'shared/publishing/video-production-control.json')
assert control['selectedVideo']=='hierarchical-game-outlines' and control['newProductionAuthorization']['fullProductionAuthorized']
assert sha(ROOT/'projects/hierarchical-game-outlines/project.json')=='575c807611d8c60040db51764cd805cf712fae48fd0037525f8591c753f50070'
assert read(P/'qa-execution-v1.json')['exitCode']==0 and read(P/'caption-boundary-diagnosis-v1.json')['allExact']
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS);ancestors={p.pid for p in me.parents()}
active=[]
for pr in psutil.process_iter(['pid','create_time','cmdline'],ad_value=None):
 cmd=' '.join(pr.info['cmdline'] or []).replace('\\','/')
 if pr.pid in ancestors|{me.pid} or 'powershell' in cmd.lower() or 'pwsh' in cmd.lower():continue
 if 'reference-preserving-v1/' in cmd and any(k in cmd for k in ['render-reference.cjs','review-audio-v1.py','build-current-v1.py','repair-final-v2.py','review-mix-contexts-v1.py']):active.append(pr.info)
state=dict(status='running',startedAt=now(),worker=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),resource=dict(cpu=psutil.cpu_percent(interval=1),availableMemoryBytes=psutil.virtual_memory().available,gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout,otherOwnedHeavy=active),completed=[],exitCode=None)
assert not active and state['resource']['cpu']<85 and state['resource']['availableMemoryBytes']>8e9
def save():state['updatedAt']=now();write(STATE,state)
def done(x):state['completed'].append(x);save();print(json.dumps(x,ensure_ascii=False),flush=True)
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def run(args):
 r=subprocess.run(args,capture_output=True,creationflags=0x08000000)
 if r.returncode:raise RuntimeError(r.stderr.decode('utf-8','replace')[-6000:])
 return r.stdout
def ff(args):return run([FF,'-hide_banner','-loglevel','warning','-nostdin','-n',*args])
plan=read(P/'final-timeline-v1.json');old=read(P/'final-pixel-plan-v1.json');save()
try:
 # Same original source/crop/duration/quality; annotation stops at the final spoken cue end.
 cut=next(c for c in plan['pieces'] if c['startFrame']==5576)
 end=6118-cut['startFrame'];assert end==542
 fixed=P/'pieces-local/08-03-menu-v2.mp4'
 filt="[0:v]split=2[bg][fg];[bg]scale=1920:1080:flags=lanczos,boxblur=22:2[blur];[fg]scale=1536:864:flags=lanczos[front];[blur][front]overlay=192:12,setsar=1,fps=60[base];[base][1:v]overlay=0:0:enable='lt(n,542)'[a];[a][2:v]overlay=0:0:enable='gte(n,60)*lt(n,542)'[v]"
 ff(['-threads','2','-ss','512','-i',str(ROOT/cut['path']),'-i',str(P/'annotations-local/sound-parent.png'),'-i',str(P/'annotations-local/sound-children.png'),'-filter_complex_threads','1','-filter_complex',filt,'-map','[v]','-frames:v','1171','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(fixed)])
 done(dict(stage='one-cut-repaired',path=rel(fixed),sha256=sha(fixed),frames=1171,annotationEndExclusive=6118))
 original=(P/'silent-concat-local.txt').read_text(encoding='utf-8');target=original.replace("08-03-menu.mp4'","08-03-menu-v2.mp4'");assert original!=target
 concat=P/'silent-concat-v2-local.txt';concat.write_text(target,encoding='utf-8');silent=P/'current-silent-v2.mp4'
 ff(['-f','concat','-safe','0','-i',str(concat),'-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(silent)])
 mix=read(P/'mix-final-inputs-v1.json');audio=ROOT/mix['audio'];assert sha(audio)==mix['sha256']
 clean=P/'hierarchical-game-outlines.clean.v2.review.mp4';cap=P/'hierarchical-game-outlines.captioned.v2.review.mp4'
 ff(['-i',str(silent),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(clean)])
 # All base pieces are 1920x1080/yuv420p/60. Their SAR/color metadata varies.
 # A filter reinitialization at such joins discarded the queued alpha frame in V1.
 # Keep one continuous frame synchronizer; retain original source pixel values.
 ff(['-threads','2','-reinit_filter','0','-i',str(silent),'-i',str(P/'captions-alpha-local.mov'),'-i',str(audio),'-filter_complex_threads','1','-filter_complex','[0:v]setsar=1[base];[base][1:v]overlay=0:0:shortest=1[v]','-map','[v]','-map','2:a:0','-frames:v',str(plan['totalFrames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',str(cap)])
 packet=[]
 for p in [clean,cap]:
  probe=json.loads(run([FP,'-v','error','-show_streams','-of','json',str(p)]));v=next(s for s in probe['streams'] if s['codec_type']=='video')
  assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',17140)
  ff(['-threads','2','-i',str(p),'-map','0:v','-map','0:a','-f','null','-'])
  pts=sorted(int(n) for n in run([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','csv=p=0',str(p)]).decode().splitlines() if n.strip());assert pts==list(range(0,17140*1500,1500))
  packet.append(hashlib.sha256(ff(['-i',str(p),'-map','0:a','-c:a','copy','-f','adts','pipe:1'])).hexdigest())
  done(dict(stage='current-technical',path=rel(p),sha256=sha(p),bytes=p.stat().st_size,decodeExit=0,frames=len(pts),ptsStep=1500,aacPacketSha256=packet[-1]))
 assert packet==['bcdf218b4b4b1c5da4624f6ea839938d77cb8d0cb14e8064f5701805d37ba2cd']*2
 samples={s['frame'] for s in old['samples']}|{6117,6118,6119,540,541,542,2687,2688,2700,2707,2708}
 samples.update(c['startFrame']+1 for c in plan['pieces']);samples=sorted(samples)
 dest=P/'final-qa-v2-local';dest.mkdir(exist_ok=False);selection=dest/'select.txt';selection.write_text('select='+ '+'.join(f'eq(n\\,{i})' for i in samples),encoding='utf-8')
 ff(['-threads','2','-i',str(cap),'-filter_script:v',str(selection),'-fps_mode','vfr','-threads','2',str(dest/'frame-%04d.png')])
 oldmap={s['frame']:s for s in old['samples']};rows=[];changed=[]
 for i,n in enumerate(samples):
  p=dest/f'frame-{i+1:04d}.png';im=Image.open(p).convert('RGB');row=dict(frame=n,seconds=n/60,path=rel(p),sha256=sha(p),rgbSha256=hashlib.sha256(im.tobytes()).hexdigest(),inherited=False)
  if n in oldmap:
   oldp=ROOT/oldmap[n]['path'];assert sha(oldp)==oldmap[n]['sha256'];prior=Image.open(oldp).convert('RGB')
   row['priorPath']=oldmap[n]['path'];row['inherited']=im.tobytes()==prior.tobytes()
   if not row['inherited']:
    diff=np.abs(np.asarray(im,dtype=np.int16)-np.asarray(prior,dtype=np.int16));row['meanAbsoluteRgbDifference']=float(diff.mean())
  rows.append(row)
  if not row['inherited']:changed.append(row)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21);boards=[]
 for k in range(0,len(changed),4):
  board=Image.new('RGB',(1920,1136),'#192126');draw=ImageDraw.Draw(board)
  for j,row in enumerate(changed[k:k+4]):
   x=j%2*960;y=j//2*568;board.paste(Image.open(ROOT/row['path']).convert('RGB').resize((960,540)),(x,y));draw.text((x+8,y+542),f"{k+j+1:03} | f{row['frame']} | {row['seconds']:.3f}s",font=font,fill='white')
  p=dest/f'changed-board-{k//4+1:03d}.jpg';board.save(p,quality=95);boards.append(dict(path=rel(p),sha256=sha(p),frames=[r['frame'] for r in changed[k:k+4]]))
 write(P/'final-pixel-plan-v2.json',dict(at=now(),captionedSha256=sha(cap),priorReview='final-direct-review-v1-held.json',samples=rows,boards=boards,exactRgbInherited=sum(r['inherited'] for r in rows),newDirectSamples=len(changed),allCurrentCues=48,allCurrentCuts=21,directPixelsApproved=False))
 done(dict(stage='new-pixels-extracted',samples=len(rows),exactRgbInherited=sum(r['inherited'] for r in rows),newDirectSamples=len(changed),boards=len(boards)))
 state.update(status='complete-pending-changed-pixels',exitCode=0,finishedAt=now());save()
except BaseException:
 state.update(status='failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
