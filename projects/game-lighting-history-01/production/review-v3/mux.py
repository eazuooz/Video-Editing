"""Mux the reviewed current AAC once; verify both full outputs and packet timing."""
import pathlib,json,hashlib,datetime,subprocess,shutil,runpy,concurrent.futures
import av
from fractions import Fraction
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/review-v3';D=O/'pair';FF=shutil.which('ffmpeg')
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def audio_packets(path):
 h=hashlib.sha256();n=0;times=[]
 with av.open(str(path)) as c:
  s=c.streams.audio[0]
  for p in c.demux(s):
   if p.pts is None:continue
   h.update(bytes(p));n+=1;times.append([p.pts,p.dts,p.duration])
 return dict(sha256=h.hexdigest(),packets=n,timeBase=str(s.time_base),timesSha256=hashlib.sha256(json.dumps(times).encode()).hexdigest())
def main():
 runpy.run_path(str(P/'production/beginner-revision-v1/production-authority.py'))['require_selected_production']()
 visual=rd(D/'visual-execution.json');plan=rd(O/'plan.json');mix=rd(O/'mix-execution.json');review=rd(O/'mixed-asr-direct-review.json')
 assert visual['status']=='complete-awaiting-mix-and-pixel-review' and review['allCurrentMixedTextsDirectlyCompared'] and review['contentCoverageApproved'];assert review['mixSha256']==mix['outputs'][mix['currentAsrWav']]
 assert not (D/'execution.json').exists();aac=O/mix['currentAac'];audio=audio_packets(aac)
 state=dict(status='running',startedAt=now(),planSha256=sha(O/'plan.json'),captionSha256=sha(O/'captions.ko.ass'),sourceAacSha256=sha(aac),sourceAacPackets=audio,outputs={},allFinalPixelsApproved=False,humanListening='pending')
 wr(D/'execution.json',state)
 for name,source in [('clean','visual.mp4'),('captioned','captioned-video.mp4')]:
  assert sha(D/source)==visual['outputs'][source]
  with (D/(name+'-mux.log')).open('w') as log:subprocess.run([FF,'-hide_banner','-nostdin','-n','-i',str(D/source),'-i',str(aac),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',str(D/(name+'.mp4'))],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 def verify(name):
  path=D/(name+'.mp4')
  with av.open(str(path)) as c:
   s=c.streams.video[0];assert s.frames==plan['frames'] and s.width==1920 and s.height==1080 and s.average_rate==60 and s.time_base==Fraction(1,90000)
   pts=sorted(p.pts for p in c.demux(s) if p.pts is not None);assert pts==list(range(0,plan['frames']*1500,1500))
  packets=audio_packets(path);assert packets==audio
  with (D/(name+'-decode.log')).open('w') as log:subprocess.run([FF,'-v','error','-xerror','-nostdin','-threads','2','-i',str(path),'-map','0:v:0','-map','0:a:0','-f','null','-'],stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  return name,dict(path=path.relative_to(R).as_posix(),sha256=sha(path),bytes=path.stat().st_size,videoFrames=len(pts),width=1920,height=1080,fps='60/1',timeBase='1/90000',ptsStep=1500,fullVideoAudioDecodeExitCode=0,sourceAacPacketMatch=True,aacPackets=packets)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for name,result in pool.map(verify,['clean','captioned']):state['outputs'][name]=result;wr(D/'execution.json',state)
 state.update(status='complete-awaiting-encoded-pixels',exitCode=0,endedAt=now());wr(D/'execution.json',state);print('Both1080p60 outputs fully decoded; measured frames and identical AAC packets')
if __name__=='__main__':main()
