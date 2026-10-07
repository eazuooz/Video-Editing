"""Single CPU composition. Exact reviewed white replacements; preserve baseline PCM/SRT/media."""
from pathlib import Path
import sys,json,hashlib,subprocess,datetime,os
ROOT=Path(__file__).resolve().parents[3]
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
PROBE=FF.with_name('ffprobe.exe')
slug=sys.argv[1];folder=ROOT/'projects'/slug/'production/visual-depth-v1'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
baseline=read(folder/'baseline.json');review=read(folder/'white-direct-review.json')
if not review.get('selectedWhitePixelsApproved'):raise RuntimeError('Direct white review required before state creation')
for f in baseline['files']:
 if f['role'] in ['script','scriptEn','audioMix','captionsKo','captionsEn'] and sha(ROOT/f['path'])!=f['sha256']:raise RuntimeError('Baseline changed '+f['role'])
if (folder/'guide-preservation.json').exists():
 for f in read(folder/'guide-preservation.json')['files']:
  if sha(ROOT/f['path'])!=f['sha256']:raise RuntimeError('Preserved additional guide script changed')
for r in review['selected']:
 if sha(ROOT/r['file'])!=r['sha256']:raise RuntimeError('Reviewed white hash changed')
for s in read(folder/'assembly-inputs.json')['segments']:
 if s.get('sha256') and sha(ROOT/s['file'])!=s['sha256']:raise RuntimeError('Assembly input changed '+s['file'])
resume='--resume-composition' in sys.argv
clock_resume='--resume-clock' in sys.argv
pixel_resume='--resume-pixel-fix' in sys.argv
caption_resume='--resume-caption-safe' in sys.argv
previous=read(folder/'pair-execution.json') if (folder/'pair-execution.json').exists() else None
if previous and not((resume and previous['status']=='failed' and previous.get('stage')=='compose-clean-captioned') or (clock_resume and previous['status']=='failed' and previous.get('error')=='Exact frame/PTS gate failed clean') or ((pixel_resume or caption_resume) and previous['status']=='encoded-technical-passed-awaiting-final-pixels')):raise RuntimeError('Inspect existing execution; do not repeat')
if caption_resume:
 request=read(folder/'caption-safe-repair-request.json');source=ROOT/request['source'];oldqa=read(folder/'pair-technical-qa.json');preflight=read(folder/'white-preflight-direct-review.json')
 expected=next(r['sha256'] for r in request['retainedV1Records'] if r['path'].endswith('/pair-technical-qa.json'))
 if sha(folder/'pair-technical-qa.json')!=expected or request['sourceSha256']!=sha(source) or review.get('revision')!=request['revision'] or preflight.get('revision')!=request['revision']:raise RuntimeError('Exact prepared correction and current directly reviewed source required')
 for o in oldqa['outputs']:
  if sha(ROOT/o['path'])!=o['sha256']:raise RuntimeError('Previous encoded pair changed')
 for variant in ['clean','captioned']:
  old=folder/(slug+'.'+variant+'.review.mp4');target=folder/(slug+'.'+variant+'.pre-caption-safe.review.mp4')
  if target.exists():raise RuntimeError('Preserve previous pair')
  if not target.resolve().is_relative_to(ROOT.resolve()):raise RuntimeError('Archive outside workspace')
  old.rename(target)
 for name in ['pair-execution.json','pair-technical-qa.json','white-technical-qa.json','compose-clean-captioned.log','encoded-pixel-execution.json','encoded-pixel-plan.json','encoded-pixel-direct-progress.json','encoded-pixel-extraction.log']:
  old=folder/name
  if old.exists():
   target=folder/(Path(name).stem+'-pre-caption-safe'+Path(name).suffix)
   if target.exists():raise RuntimeError('Preserve earlier record '+name)
   old.rename(target)
 old=folder/'encoded-pixels-local'
 if old.exists():
  target=folder/'encoded-pixels-pre-caption-safe-local'
  if target.exists() or not old.resolve().is_relative_to(ROOT.resolve()) or not target.resolve().is_relative_to(ROOT.resolve()):raise RuntimeError('Inspect extraction archive targets')
  old.rename(target)
if pixel_resume:
 rejection=read(folder/'encoded-pixel-direct-review-pre-outro-fix.json')
 oldqa=read(folder/'pair-technical-qa.json')
 if rejection.get('allFinalPixelsReviewed') or rejection.get('requiredFix')!='outro-source-frame-0-old-PPT-flash' or rejection['videoSha256']!=next(o['sha256'] for o in oldqa['outputs'] if o['variant']=='captioned'):raise RuntimeError('Observed exact-pair pixel rejection required')
 fix=read(folder/'outro-boundary-fix.json')
 if fix['fullDecodeExitCode']!=0 or sha(ROOT/fix['path'])!=fix['sha256'] or fix['frames']!=600:raise RuntimeError('Boundary fix QA required')
 for variant in ['clean','captioned']:
  old=folder/(slug+'.'+variant+'.review.mp4');target=folder/(slug+'.'+variant+'.pre-outro-fix.review.mp4')
  if target.exists():raise RuntimeError('Preserve previous pair')
  old.rename(target)
 for name in ['pair-execution.json','pair-technical-qa.json','compose-clean-captioned.log']:
  (folder/name).rename(folder/(Path(name).stem+'-pre-outro-fix'+Path(name).suffix))
if resume:
 if not previous:raise RuntimeError('No observed failure to resume')
 for f in folder.glob('*.review.mp4'):
  if f.stat().st_size:raise RuntimeError('Existing nonempty pair output must be inspected')
 write(folder/'pair-execution-first-failure.json',previous)
 (folder/'compose-clean-captioned.log').rename(folder/'compose-clean-captioned-first-failure.log')
if clock_resume:
 if not read(folder/'encoder-clock-fixed-120-verification.json')['exact']:raise RuntimeError('Observed fixed clock diagnostic required')
 archive=[]
 for variant in ['clean','captioned']:
  old=folder/(slug+'.'+variant+'.review.mp4');target=folder/(slug+'.'+variant+'.failed-clock.mp4')
  if target.exists():raise RuntimeError('Preserve earlier failed clock evidence')
  archive.append(dict(file=old.relative_to(ROOT).as_posix(),sha256=sha(old),preservedAs=target.relative_to(ROOT).as_posix()));old.rename(target)
 write(folder/'pair-execution-clock-failure.json',dict(**previous,preservedFailedOutputs=archive,cause='Filter reinitialization at differing input color metadata reset setpts N; explicit disabled reinitialization and encoder 1/60 clock diagnostic passed'))
 (folder/'compose-clean-captioned.log').rename(folder/'compose-clean-captioned-clock-failure.log')
state=dict(status='running',slug=slug,pid=os.getpid(),startedAt=now(),threadsTotal=2,gpu=0,completed=[],allFinalPixelsReviewed=False,uploaded=False)
def save():write(folder/'pair-execution.json',state)
def run(args,label):
 state['stage']=label;save();log=folder/(label+'.log')
 with open(log,'w',encoding='utf-8') as f:
  p=subprocess.Popen([str(x) for x in args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
  state['activePid']=p.pid;state['activeCommand']=[str(x) for x in args];save();code=p.wait()
 state['completed'].append(dict(stage=label,exitCode=code,log=log.relative_to(ROOT).as_posix(),endedAt=now()));save()
 if code:raise RuntimeError(label+' failed; preserved log '+str(log))
def probe(p):
 return json.loads(subprocess.check_output([str(PROBE),'-v','error','-show_streams','-show_format','-of','json',str(p)],text=True))
def packet_hash(p):
 return subprocess.check_output([str(FF),'-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
try:
 save();white_qa=[]
 if resume or clock_resume or pixel_resume:
  qa=read(folder/'white-technical-qa.json')
  if qa['status']!='passed' or [r['sha256'] for r in qa['inputs']]!=[r['sha256'] for r in review['selected']]:raise RuntimeError('Preserved white QA hash mismatch')
  state['preservedWhiteQa']='white-technical-qa.json'
 else:
  for r in review['selected']:
   path=ROOT/r['file'];p=probe(path);v=p['streams'][0]
   if int(v['nb_frames'])!=r['frames'] or v['time_base']!='1/90000' or v['r_frame_rate']!='60/1':raise RuntimeError('White timing mismatch')
   run([FF,'-hide_banner','-v','error','-threads','2','-i',path,'-map','0:v:0','-f','null','-'],'decode-white-'+r['id'])
   white_qa.append(dict(**r,fullDecodeExitCode=0,probe=v))
  write(folder/'white-technical-qa.json',dict(status='passed',checkedAt=now(),inputs=white_qa))
 # The reviewed assembly list names every preserved actual/branding/member input.
 inputs=read(folder/'assembly-inputs.json');lines=[]
 for s in inputs['segments']:
  p=ROOT/s['file'];lines.append("file '"+p.as_posix().replace("'","'\\''")+"'")
 concat=folder/'revised-concat.txt';concat.write_text('\n'.join(lines)+'\n','utf-8')
 audio=ROOT/next(f['path'] for f in baseline['files'] if f['role']=='audioMix')
 clean=folder/(slug+'.clean.review.mp4');captioned=folder/(slug+'.captioned.review.mp4')
 ass=ROOT/inputs['captionAss'];assrel=ass.relative_to(ROOT).as_posix().replace(':','\\:')
 filters="[0:v]settb=expr=1/60,setpts=N,split=2[clean][raw];[raw]ass='"+assrel+"'[captioned]"
 cmd=[FF,'-hide_banner','-y','-loglevel','warning','-filter_complex_threads','1','-reinit_filter','0','-threads','2','-f','concat','-safe','0','-i',concat,'-i',audio,'-filter_complex',filters]
 for label,path in [('clean',clean),('captioned',captioned)]:
  cmd+=['-map','['+label+']','-map','1:a:0','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-enc_time_base','1:60','-fps_mode','passthrough','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',path]
 run(cmd,'compose-clean-captioned')
 results=[];expected=inputs['totalFrames'];audio_hash=packet_hash(audio)
 for name,path in [('clean',clean),('captioned',captioned)]:
  run([FF,'-hide_banner','-v','error','-threads','2','-i',path,'-f','null','-'],'decode-'+name)
  p=probe(path);v=next(s for s in p['streams'] if s['codec_type']=='video')
  timestamps=subprocess.check_output([str(PROBE),'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(path)],text=True)
  pts=[int(f['best_effort_timestamp']) for f in json.loads(timestamps)['frames']]
  if v['time_base']!='1/90000' or len(pts)!=expected or any(t!=i*1500 for i,t in enumerate(pts)):raise RuntimeError('Exact frame/PTS gate failed '+name)
  ah=packet_hash(path)
  if ah!=audio_hash:raise RuntimeError('AAC packet bytes changed '+name)
  results.append(dict(variant=name,path=path.relative_to(ROOT).as_posix(),sha256=sha(path),frames=len(pts),timeBase=v['time_base'],firstPts=pts[0],lastPts=pts[-1],ptsStep=1500,fullDecodeExitCode=0,aacPacketHash=ah,probe=p))
 write(folder/'pair-technical-qa.json',dict(status='passed-awaiting-every-final-pixel',checkedAt=now(),expectedFrames=expected,allFinalPixelsReviewed=False,audioIdentity=audio_hash,preservedSrt=True,outputs=results))
 state['status']='encoded-technical-passed-awaiting-final-pixels';state['endedAt']=now();save()
 print('Pair built with exact frame clocks, two full decodes and identical AAC. Final pixel review remains pending.',flush=True)
except Exception as e:
 state['status']='failed';state['error']=str(e);state['endedAt']=now();save();raise
