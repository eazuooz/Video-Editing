"""Current retimed pair. Decode-select exact framed ranges; preserve one AAC."""
import pathlib,json,hashlib,datetime,subprocess,os,sys
import av,psutil
from fractions import Fraction
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/continuity-v2';D=O/'pair'
def ffmpeg_path():
 import shutil
 return os.environ.get('VIDEO_FFMPEG') or shutil.which('ffmpeg')
FF=ffmpeg_path()
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def concat_text(nodes):
 lines=['ffconcat version 1.0']
 for n in nodes:
  s=n['framedStartFrame'];count=n['frames'];shift=.25 if s else 0
  # Put a fractional-frame margin before nonzero boundaries; selection then
  # keeps exactly s..s+count-1 despite microsecond concat timestamps.
  lines += ["file '"+(R/n['framedPath']).as_posix()+"'",f'inpoint {(s-shift)/60:.9f}',f'outpoint {(s+count-shift)/60:.9f}',f'duration {count/60:.9f}']
 return '\n'.join(lines)+'\n'
def main():
 import runpy
 runpy.run_path(str(pathlib.Path(__file__).with_name('production-authority.py')))['require_selected_production']()
 plan=rd(O/'plan.json');assert plan['finalTimingApproved'];cap=rd(O/'captions.json');assert cap['planSha256']==sha(O/'plan.json') and cap['allCueTextDirectReview']
 D.mkdir(exist_ok=True)
 if '--verify-concat' in sys.argv:
  assert not (D/'concat-verification.json').exists()
  ns=[dict(n) for n in [next(n for n in plan['nodes'] if n.get('newExplanation')),next(n for n in plan['nodes'] if n.get('retained') and n['framedStartFrame']>0),next(n for n in plan['nodes'] if n.get('newNative'))]]
  for n in ns:n['framedStartFrame']+=7;n['frames']=37
  listing=D/'verify-concat.txt';listing.write_text(concat_text(ns),encoding='utf8')
  def md5(args):
   cmd=[FF,'-v','error','-nostdin','-threads','2',*args,'-filter_threads','2','-an','-fps_mode','passthrough','-f','framemd5','-'];r=subprocess.run(cmd,cwd=R,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);assert r.returncode==0,r.stderr
   return [l.split(',')[-1].strip() for l in r.stdout.splitlines() if l and not l.startswith('#')]
  got=md5(['-copyts','-segment_time_metadata','1','-f','concat','-safe','0','-i',str(listing),'-vf','select=concatdec_select,setpts=N/(60*TB),format=yuv420p'])
  wanted=[]
  for n in ns:wanted+=md5(['-ss',str(n['framedStartFrame']/60),'-i',str(R/n['framedPath']),'-vf',f"trim=end_frame={n['frames']},setpts=N/(60*TB),format=yuv420p"])
  assert len(wanted)==111 and wanted==got,(len(wanted),len(got),next((i for i,(a,b) in enumerate(zip(wanted,got)) if a!=b),None))
  wr(D/'concat-verification.json',dict(checkedAt=now(),method='Each decoded frame MD5 compared to independently seek/trimmed source; three codec/range cases,37 frames each.',frames=len(got),passed=True,framingCodeSha256=sha(pathlib.Path(__file__)),nodes=ns));print('concat exact111frames verified');return
 assert rd(D/'concat-verification.json')['passed']
 if '--visual-only' in sys.argv:
  # Independent visual preparation can overlap CPU ASR when measured host
  # capacity permits. No audio mux, collection or upload approval is granted.
  assert not (D/'visual-execution.json').exists() and not (D/'visual.mp4').exists()
  visualState=dict(status='running',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=1,planSha256=sha(O/'plan.json'),captionSha256=sha(O/'captions.ko.ass'),steps=[],finalPairApproved=False,allFinalPixelsApproved=False)
  def saveVisual():wr(D/'visual-execution.json',visualState)
  def runVisual(label,args):
   cmd=[FF,'-hide_banner','-nostdin','-n','-threads','2',*args];log=D/(label+'.log');visualState['active']=dict(label=label,command=cmd,log=log.relative_to(R).as_posix());saveVisual()
   with log.open('w') as f:
    ch=subprocess.Popen(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);visualState['active']['pid']=ch.pid;saveVisual();rc=ch.wait()
   visualState['steps'].append(dict(label=label,exitCode=rc));saveVisual();assert rc==0
  saveVisual()
  try:
   listing=D/'segments.txt';listing.write_text(concat_text(plan['nodes']),encoding='utf8')
   common=['-filter_threads','2','-an','-fps_mode','passthrough','-c:v','h264_nvenc','-preset','p7','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-multipass','fullres','-spatial-aq','1','-temporal-aq','1','-rc-lookahead','32','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart']
   runVisual('visual',['-copyts','-reinit_filter','0','-segment_time_metadata','1','-f','concat','-safe','0','-i',str(listing),'-vf','select=concatdec_select,setpts=N/(60*TB),setsar=1,format=yuv420p',*common,str(D/'visual.mp4')])
   ass=(O/'captions.ko.ass').relative_to(R).as_posix();fonts=(P/'production/local/final-edit-v1/fonts').relative_to(R).as_posix()
   runVisual('captioned-video',['-reinit_filter','0','-i',str(D/'visual.mp4'),'-vf',f"setpts=N/(60*TB),ass='{ass}':fontsdir='{fonts}',setsar=1",*common,str(D/'captioned-video.mp4')])
   for name in ['visual.mp4','captioned-video.mp4']:
    with av.open(str(D/name)) as c:
     s=c.streams.video[0];assert s.frames==plan['frames'] and s.time_base==Fraction(1,90000) and s.average_rate==60
   visualState.update(status='complete-awaiting-mix-and-pixel-review',endedAt=now(),exitCode=0,active=None,outputs={n:sha(D/n) for n in ['visual.mp4','captioned-video.mp4']});saveVisual();return
  except BaseException as e:visualState.update(status='failed',endedAt=now(),error=repr(e));saveVisual();raise
 mix=rd(O/'mix-execution.json');review=rd(O/'mixed-asr-direct-review.json');assert review['allCurrentMixedTextsDirectlyCompared'] and review['contentCoverageApproved'] and review['mixSha256']==sha(O/mix['currentWav'])
 assert not (D/'execution.json').exists(),'Inspect successful/running outputs; never restart.'
 state=dict(status='running',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=1,planSha256=sha(O/'plan.json'),captionSha256=sha(O/'captions.ko.ass'),steps=[],outputs={},allFinalPixelsApproved=False)
 def save():wr(D/'execution.json',state)
 def run(label,args):
  cmd=[FF,'-hide_banner','-nostdin','-n','-threads','2',*args];log=D/(label+'.log');state['active']=dict(label=label,command=cmd,log=log.relative_to(R).as_posix());save()
  with log.open('w') as f:child=subprocess.Popen(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state['active']['pid']=child.pid;save();rc=child.wait()
  state['steps'].append(dict(label=label,exitCode=rc));save();assert rc==0,(label,rc)
 def check_video(path):
  with av.open(str(path)) as c:
   s=c.streams.video[0];assert s.width==1920 and s.height==1080 and s.average_rate==60 and s.time_base==Fraction(1,90000) and s.frames==plan['frames'],(path.name,s.frames,s.time_base)
  run(path.stem+'-decode',['-i',str(path),'-map','0:v:0','-map','0:a:0','-f','null','-'])
  # Packet timestamps are exact; full decode above confirms actual data.
  with av.open(str(path)) as c:
   s=c.streams.video[0];pts=sorted(p.pts for p in c.demux(s) if p.pts is not None)
  assert pts==list(range(0,plan['frames']*1500,1500)),path
  extract=D/(path.stem+'-audio.m4a');run(path.stem+'-extract-aac',['-i',str(path),'-vn','-c:a','copy',str(extract)]);return dict(sha256=sha(path),videoFrames=len(pts),decodeExitCode=0,ptsStep=1500,aacSha256=sha(extract))
 save()
 try:
  listing=D/'segments.txt';listing.write_text(concat_text(plan['nodes']),encoding='utf8');aac=O/mix['currentAac']
  common=['-filter_threads','2','-an','-fps_mode','passthrough','-c:v','h264_nvenc','-preset','p7','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-multipass','fullres','-spatial-aq','1','-temporal-aq','1','-rc-lookahead','32','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart']
  prepared=rd(D/'visual-execution.json') if (D/'visual-execution.json').exists() else None
  if prepared:
   assert prepared['exitCode']==0 and prepared['planSha256']==state['planSha256'] and prepared['captionSha256']==state['captionSha256']
   for n in ['visual.mp4','captioned-video.mp4']:assert sha(D/n)==prepared['outputs'][n]
   state['reusedVisualPreparation']='visual-execution.json';save()
  else:run('visual',['-copyts','-reinit_filter','0','-segment_time_metadata','1','-f','concat','-safe','0','-i',str(listing),'-vf','select=concatdec_select,setpts=N/(60*TB),setsar=1,format=yuv420p',*common,str(D/'visual.mp4')])
  with av.open(str(D/'visual.mp4')) as c:assert c.streams.video[0].frames==plan['frames'],c.streams.video[0].frames
  run('clean',['-i',str(D/'visual.mp4'),'-i',str(aac),'-map','0:v','-map','1:a','-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(D/'clean.mp4')])
  ass=(O/'captions.ko.ass').relative_to(R).as_posix();fonts=(P/'production/local/final-edit-v1/fonts').relative_to(R).as_posix()
  if not prepared:run('captioned-video',['-reinit_filter','0','-i',str(D/'visual.mp4'),'-vf',f"setpts=N/(60*TB),ass='{ass}':fontsdir='{fonts}',setsar=1",*common,str(D/'captioned-video.mp4')])
  run('captioned',['-i',str(D/'captioned-video.mp4'),'-i',str(aac),'-map','0:v','-map','1:a','-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(D/'captioned.mp4')])
  for name in ['clean','captioned']:state['outputs'][name]=check_video(D/(name+'.mp4'));save()
  assert state['outputs']['clean']['aacSha256']==state['outputs']['captioned']['aacSha256']==sha(aac)
  state.update(status='complete-awaiting-encoded-pixels',endedAt=now(),exitCode=0,active=None);save()
 except BaseException as e:state.update(status='failed',endedAt=now(),error=repr(e));save();raise
if __name__=='__main__':main()
