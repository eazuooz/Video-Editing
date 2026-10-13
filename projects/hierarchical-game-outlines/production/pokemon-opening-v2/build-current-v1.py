"""Current independent-footage edit. Stages are single-run and never mutate baselines."""
from pathlib import Path
import os,sys,json,hashlib,datetime,subprocess,traceback,math,re
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
import numpy as np,soundfile as sf,psutil
from PIL import Image
from captions import image as caption_image
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
sys.stdout.reconfigure(encoding='utf-8')
mode=sys.argv[1];assert mode in ['preflight','visuals','mix','pair','qa']
version=sys.argv[2] if len(sys.argv)>2 else 'v1';assert re.fullmatch(r'v[1-9][0-9]*',version)
STATE=P/f'{mode}-execution-{version}.json';assert not STATE.exists(),'Inspect current state, never duplicate the stage'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def run(args):
 r=subprocess.run(args,capture_output=True,windowsHide=True) if False else subprocess.run(args,capture_output=True,creationflags=0x08000000)
 if r.returncode:raise RuntimeError(r.stderr.decode('utf-8','replace')[-5000:])
 return r.stdout,r.stderr.decode('utf-8','replace')
def ff(args):return run([FF,'-hide_banner','-loglevel','warning','-nostdin','-n',*args])
def probe(p):return json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)])[0])
control=read(ROOT/'shared/publishing/video-production-control.json')
assert control['selectedVideo']=='hierarchical-game-outlines' and control['newProductionAuthorization']['fullProductionAuthorized']
plan=read(P/'final-timeline-v1.json');baseline=ROOT/'projects/hierarchical-game-outlines/production/visual-depth-v1/hierarchical-game-outlines.clean.review.mp4'
assert sha(ROOT/'projects/hierarchical-game-outlines/project.json')=='45bae8b008d8f34e562bd868e3a71f1220a61338b18e433d19be6c1adb1c8c5b'
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
active=[]
for pr in psutil.process_iter(['pid','create_time','cmdline'],ad_value=None):
 a=pr.info;cmd=' '.join(a['cmdline'] or []).replace('\\','/')
 if a['pid'] in [me.pid,me.ppid()] or any(z in cmd.lower() for z in ['pwsh.exe','powershell.exe']):continue
 if 'pokemon-opening-v2/' in cmd and any(z in cmd for z in ['render-pokemon.cjs','review-audio-v1.py','review-audio-v2.py','review-voice-contexts-v1.py','review-mix-contexts.py','review-mix-contexts-v2.py','build-current-v1.py','render-voice-v1.py']):
  # Windows venv launcher and its exact base-Python child are one request.
  if pr.pid in [x.pid for x in me.parents()] and 'build-current-v1.py' in cmd:continue
  active.append(a)
state=dict(mode=mode,status='running',startedAt=now(),worker=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),
 resource=dict(cpu=psutil.cpu_percent(interval=1),availableMemoryBytes=psutil.virtual_memory().available,gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout,ownedOtherHeavy=active),
 timelineSha256=sha(P/'final-timeline-v1.json'),completed=[],exitCode=None)
assert not active and state['resource']['cpu']<85 and state['resource']['availableMemoryBytes']>8e9,state['resource']
def save():state['updatedAt']=now();write(STATE,state)
def done(row):state['completed'].append(row);save();print(json.dumps(row,ensure_ascii=False),flush=True)
save()
gamefilter='[0:v]split=2[bg][fg];[bg]scale=1920:1080:flags=lanczos,boxblur=22:2[blur];[fg]scale=1536:864:flags=lanczos[front];[blur][front]overlay=192:12,setsar=1,fps=60'
enc=['-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart']
try:
 if mode=='visuals':
  ppt=read(P/'white-cpu-execution.json');assert ppt['status']=='rendered-pending-direct-pixels-and-full-decode' and len(ppt['completed'])==2
  dest=P/'pieces-local';dest.mkdir(exist_ok=True)
  prev=ROOT/'projects/hierarchical-game-outlines/production/reference-preserving-v1'
  pieces=[prev/'pieces-local/intro.mp4']
  for i,cut in enumerate(plan['pieces']):
   if cut.get('reuseVisual'):
    target=ROOT/cut['reuseVisual'];assert sha(target)==cut['reuseVisualSha256'];pieces.append(target);continue
   target=dest/f'{i:02}-{cut["scene"]}-{cut["kind"]}.mp4'
   if cut['kind'].startswith('ex'):
    ff(['-threads','2','-ss',str(cut.get('sourceStart',0)),'-i',str(ROOT/cut['path']),'-vf','setpts=PTS-STARTPTS,setsar=1','-frames:v',str(cut['frames']),*enc,str(target)])
   elif cut['kind']=='pokemon':
    # Preserve the complete 10:9 original and all English game UI above fixed captions.
    f='[0:v]split=2[bg][fg];[bg]scale=1920:1080:flags=neighbor,boxblur=32:2[blur];[fg]scale=960:864:flags=neighbor[front];[blur][front]overlay=480:12,setsar=1,fps=60[v]'
    ff(['-threads','2','-ss',str(cut['sourceStart']),'-i',str(ROOT/cut['path']),'-filter_complex_threads','1','-filter_complex',f,'-map','[v]','-frames:v',str(cut['frames']),*enc,str(target)])
   else:raise AssertionError('Unexpected new cut '+str(cut))
   v=next(x for x in probe(target)['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==cut['frames']
   pieces.append(target);done(dict(cut=i,frames=cut['frames'],path=target.relative_to(ROOT).as_posix(),sha256=sha(target)))
  pieces.append(prev/'pieces-local/outro.mp4')
  concat=P/'silent-concat-local.txt';concat.write_text('\n'.join("file '"+p.as_posix()+"'" for p in pieces)+'\n',encoding='utf-8')
  target=P/'current-silent-v1.mp4';ff(['-f','concat','-safe','0','-i',str(concat),'-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(target)])
  v=next(x for x in probe(target)['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==plan['totalFrames']
  done(dict(path=target.relative_to(ROOT).as_posix(),frames=int(v['nb_frames']),sha256=sha(target)))
 if mode=='mix':
  from scipy.signal import resample_poly
  sr=48000;count=plan['totalFrames']*800;voice=np.zeros((count,2),np.float32);native=voice.copy();music=voice.copy()
  for sc in plan['scenes']:
   x,rate=sf.read(ROOT/sc['voicePath'],dtype='float32');assert rate==24000 and len(x)==sc['voiceSamples'] and sha(ROOT/sc['voicePath'])==sc['voiceSha256']
   placed=np.zeros(round(sc['frames']/60*24000),np.float32);covered=[]
   for a in sc['placements']:
    z=x[a['sourceStartSample']:a['sourceEndSample']];k=a['outputStartSample'];placed[k:k+len(z)]=z;covered.append(z)
   assert np.array_equal(np.concatenate(covered),x)
   yy=resample_poly(placed,2,1).astype(np.float32);k=sc['startFrame']*800;voice[k:k+len(yy)]=yy[:,None]
  def decode(src,start,duration):
   b,_=ff(['-threads','2','-ss',str(start),'-i',str(src),'-t',str(duration),'-vn','-ac','2','-ar','48000','-f','f32le','pipe:1']);return np.frombuffer(b,dtype='<f4').reshape(-1,2).copy()
  for cut in plan['pieces']:
   if cut['kind'].startswith('ex'):continue
   x=decode(ROOT/cut['path'],cut['sourceStart'],cut['frames']/60);n=cut['frames']*800;x=x[:n];k=cut['startFrame']*800
   fade1=min(len(x),5760);fade2=min(len(x),14400);x[:fade1]*=np.linspace(0,1,fade1,dtype=np.float32)[:,None];x[-fade2:]*=np.linspace(1,0,fade2,dtype=np.float32)[:,None]
   native[k:k+len(x)]+=x
  # The independently selected licensed track spans the body; original branding/member
  # audio is retained at its own boundaries rather than layered with a second song.
  bg=decode(ROOT/'projects/hierarchical-game-outlines/production/manual-preflight-v1/Late-Night-Radio.mp3',0,10000);originalBg=bg.copy();joins=[]
  while len(bg)<plan['bodyFrames']*800:
   join=len(bg)-sr;joins.append(join/sr);ramp=np.linspace(0,1,sr,dtype=np.float32)[:,None]
   bg=np.concatenate([bg[:-sr],bg[-sr:]*(1-ramp)+originalBg[:sr]*ramp,originalBg[sr:]])
  state['musicContinuation']=dict(originalSeconds=len(originalBg)/sr,oneSecondCrossfadeBodyTimes=joins,scope='licensed background music only; gameplay never loops or slows');save()
  music[120*800:(120+plan['bodyFrames'])*800]=bg[:plan['bodyFrames']*800]
  logs={}
  def level(arr,name,target):
   tmp=P/f'{name}-stem-local.wav';sf.write(tmp,arr,sr,subtype='FLOAT')
   _,stderr=run([FF,'-hide_banner','-nostdin','-i',str(tmp),'-af',f'loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
   obj=json.loads(stderr[stderr.rfind('{'):stderr.rfind('}')+1]);gain=10**((target-float(obj['input_i']))/20);logs[name]=dict(measured=obj,gainDb=20*math.log10(gain),target=target);return arr*gain
  voice=level(voice,'narration',-16);native=level(native,'native',-29);music=level(music,'lofi',-31)
  attenuation=np.ones(count,np.float32)
  for cut in plan['pieces']:
   if not cut['kind'].startswith('ex'):attenuation[cut['startFrame']*800:(cut['startFrame']+cut['frames'])*800]=10**(-3/20)
  # Smooth abrupt section transitions without changing audio duration.
  from scipy.ndimage import uniform_filter1d
  attenuation=uniform_filter1d(attenuation,size=21600,mode='nearest');music*=attenuation[:,None]
  bodya=120*800;bodyb=(120+plan['bodyFrames'])*800;fad=21600;music[bodya:bodya+fad]*=np.linspace(0,1,fad)[:,None];music[bodyb-fad:bodyb]*=np.linspace(1,0,fad)[:,None]
  mix=voice+native+music
  for start,n,k in [(0,2,0),(576.75,10,bodyb)]:
   a=decode(baseline,start,n);mix[k:k+len(a)]=a[:min(len(a),count-k)]
  mix*=10**(-1.05/20)
  state['finalHeadroomDb']=-1.05
  sf.write(P/'current-mix-prelimit-local.wav',mix,sr,subtype='FLOAT')
  ff(['-i',str(P/'current-mix-prelimit-local.wav'),'-af','alimiter=limit=0.794328:attack=5:release=50:level=false:latency=true','-c:a','pcm_s24le',str(P/'current-mix-v1.wav')])
  ff(['-i',str(P/'current-mix-v1.wav'),'-c:a','aac','-b:a','192k','-ar','48000','-ac','2',str(P/'current-mix-v1.m4a')])
  decoded=decode(P/'current-mix-v1.m4a',0,count/sr);assert abs(len(decoded)-count)<=1024
  # ASR reads the actual final AAC decoded scene intervals, including observations/music.
  d=P/'mix-review-local';d.mkdir(exist_ok=True)
  for sc in plan['scenes']:
   a=sc['startFrame']*800;b=(sc['startFrame']+sc['frames'])*800;sf.write(d/f'{sc["id"]}.wav',decoded[a:b],sr,subtype='PCM_16')
  _,loud=run([FF,'-hide_banner','-nostdin','-i',str(P/'current-mix-v1.m4a'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);measure=json.loads(loud[loud.rfind('{'):loud.rfind('}')+1]);assert float(measure['input_tp'])<=-1.5
  write(P/'mix-final-inputs-v1.json',dict(audio=(P/'current-mix-v1.m4a').relative_to(ROOT).as_posix(),sha256=sha(P/'current-mix-v1.m4a'),scenes=[dict(id=sc['id'],path=(d/f'{sc["id"]}.wav').relative_to(ROOT).as_posix(),sha256=sha(d/f'{sc["id"]}.wav')) for sc in plan['scenes']]))
  done(dict(path=(P/'current-mix-v1.m4a').relative_to(ROOT).as_posix(),sha256=sha(P/'current-mix-v1.m4a'),layers=logs,decodedAAC=measure,originalVoiceSamplesPreservedBeforeGain=True,gameAudio='original mixed game audio retained quietly; not isolated SFX',humanListening=False))
 if mode=='pair':
  assert read(P/'visuals-execution-v1.json')['exitCode']==0 and read(P/'mix-direct-review-v1.json')['approvedForEditing']
  d=P/'captions-local';d.mkdir(exist_ok=True);blank=d/'blank.png';Image.new('RGBA',(1920,1080)).save(blank)
  concat=['ffconcat version 1.0'];cursor=0
  def add(img,n):
   if n>0:concat.extend(["file '"+img.as_posix()+"'",'option framerate 60',f'duration {n/60:.12f}'])
  for i,c in enumerate(plan['captionsKo']):
   add(blank,c['startFrame']-cursor);im=d/f'{i+1:03}.png';caption_image(c['text']).save(im);add(im,c['endFrame']-c['startFrame']);cursor=c['endFrame']
  add(blank,plan['totalFrames']-cursor);concat.extend(["file '"+blank.as_posix()+"'",'option framerate 60'])
  f=d/'concat.txt';f.write_text('\n'.join(concat)+'\n',encoding='utf-8')
  ff(['-f','concat','-safe','0','-i',str(f),'-frames:v',str(plan['totalFrames']),'-vf','fps=60','-c:v','qtrle','-threads','2','-pix_fmt','argb',str(P/'captions-alpha-local.mov')])
  clean=P/'hierarchical-game-outlines.clean.review.mp4';cap=P/'hierarchical-game-outlines.captioned.review.mp4';currentAudio=read(P/'mix-final-inputs-v1.json');mix=ROOT/currentAudio['audio'];assert sha(mix)==currentAudio['sha256']
  ff(['-i',str(P/'current-silent-v1.mp4'),'-i',str(mix),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(clean)])
  ff(['-threads','2','-reinit_filter','0','-i',str(P/'current-silent-v1.mp4'),'-i',str(P/'captions-alpha-local.mov'),'-i',str(mix),'-filter_complex_threads','1','-filter_complex','[0:v]setsar=1[base];[base][1:v]overlay=0:0:shortest=1[v]','-map','[v]','-map','2:a:0','-frames:v',str(plan['totalFrames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',str(cap)])
  for path in [clean,cap]:done(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size))
 if mode=='qa':
  files=[P/f'hierarchical-game-outlines.{s}.review.mp4' for s in ['clean','captioned']];audio=[]
  for p in files:
   inf=probe(p);v=next(s for s in inf['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',plan['totalFrames'])
   ff(['-threads','2','-i',str(p),'-map','0:v','-map','0:a','-f','null','-'])
   pts=run([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','csv=p=0',str(p)])[0].decode().splitlines();pts=sorted(int(x) for x in pts if x.strip());assert pts==list(range(0,plan['totalFrames']*1500,1500))
   adts=ff(['-i',str(p),'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])[0];audio.append(hashlib.sha256(adts).hexdigest());done(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),decodeExit=0,frames=len(pts),allPtsStep=1500,aacPacketSha256=audio[-1]))
  sourceAudio=ROOT/read(P/'mix-final-inputs-v1.json')['audio']
  sourceAac=hashlib.sha256(ff(['-i',str(sourceAudio),'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])[0]).hexdigest()
  assert audio[0]==audio[1]==sourceAac
  samples={0,60,119,120,plan['totalFrames']-601,plan['totalFrames']-600,plan['totalFrames']-300,plan['totalFrames']-1}
  for c in plan['captionsKo']:samples.update([c['startFrame'],(c['startFrame']+c['endFrame']-1)//2,c['endFrame']-1])
  for cut in plan['pieces']:
   samples.update([max(0,cut['startFrame']-1),cut['startFrame'],cut['startFrame']+cut['frames']-1])
   if cut['scene'] in ['01','01a'] and cut['kind']=='ex':samples.update(range(cut['startFrame'],cut['startFrame']+cut['frames'],90))
   if cut['scene']=='03' and cut['kind']=='menu':samples.update(range(cut['startFrame'],cut['startFrame']+cut['frames'],120))
  samples=sorted(samples);d=P/'final-qa-local';d.mkdir(exist_ok=True);select=d/'select.txt';select.write_text('select='+ '+'.join(f'eq(n\\,{i})' for i in samples),encoding='utf-8')
  ff(['-threads','2','-i',str(files[1]),'-filter_script:v',str(select),'-fps_mode','vfr','-threads','2',str(d/'frame-%04d.png')])
  rows=[]
  for i,n in enumerate(samples):
   p=d/f'frame-{i+1:04d}.png';assert p.exists();rows.append(dict(frame=n,seconds=n/60,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
  from PIL import ImageDraw,ImageFont
  font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21);boards=[]
  for k in range(0,len(rows),4):
   board=Image.new('RGB',(1920,1136),'#192126');draw=ImageDraw.Draw(board)
   for j,row in enumerate(rows[k:k+4]):
    x=(j%2)*960;y=(j//2)*568;im=Image.open(ROOT/row['path']).convert('RGB').resize((960,540));board.paste(im,(x,y));draw.text((x+8,y+542),f"{k+j+1:03} | f{row['frame']} | {row['seconds']:.3f}s",font=font,fill='white')
   path=d/f'board-{k//4+1:03d}.jpg';board.save(path,quality=95);boards.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),samples=list(range(k+1,min(k+5,len(rows)+1)))))
  write(P/'final-pixel-plan-v1.json',dict(at=now(),captionedSha256=sha(files[1]),samples=rows,boards=boards,allCurrentCues=len(plan['captionsKo']),allCurrentCuts=len(plan['pieces']),directPixelsApproved=False))
  done(dict(samples=len(rows),boards=len(boards),pixelsApproved=False))
 state.update(status='complete-pending-relevant-direct-review',exitCode=0,finishedAt=now());save()
except BaseException:
 state.update(status='failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
