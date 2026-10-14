"""Isolated decoder per source; exactly one input frame per planned output frame.

Avoid concat demuxer timestamp selection across heterogeneous H264 GOPs.
Encode the clean/captioned pair together; no duplicate visual decoding.
"""
import pathlib,json,hashlib,datetime,subprocess,shutil,runpy,os
import av,psutil
from fractions import Fraction
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/continuity-v2';D=O/'pair-exact-v2';FF=shutil.which('ffmpeg')
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 runpy.run_path(str(pathlib.Path(__file__).with_name('production-authority.py')))['require_selected_production']()
 plan=rd(O/'plan.json');cap=rd(O/'captions.json');assert plan['finalTimingApproved'] and cap['planSha256']==sha(O/'plan.json')
 assert not D.exists();D.mkdir()
 old=rd(O/'pair/visual-execution.json');assert old['status']=='failed'
 state=dict(status='running',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),planSha256=sha(O/'plan.json'),captionSha256=sha(O/'captions.ko.ass'),method='Independent PyAV decoder per planned source interval, exact integer source PTS, raw yuv420p pipe, dual NVENC outputs.',priorFailedPair='pair',priorObservedFrames=143488,expectedFrames=plan['frames'],allFinalPixelsApproved=False,sourceIntervals=[],framesWritten=0,introNoteRemoval=dict(box=[800,819,320,45],startFrame=120,endFrame=438,text='질문을 먼저 제시'),outputs={})
 def save():wr(D/'visual-execution.json',state)
 ass=(O/'captions.ko.ass').relative_to(R).as_posix();fonts=(P/'production/local/final-edit-v1/fonts').relative_to(R).as_posix()
 graph=f"[0:v]drawbox=x=800:y=819:w=320:h=45:color=black:t=fill:enable='gte(n,120)*lt(n,438)',split=2[clean][text];[text]ass='{ass}':fontsdir='{fonts}'[captioned]"
 codec=['-an','-fps_mode','passthrough','-c:v','h264_nvenc','-preset','p7','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-multipass','fullres','-spatial-aq','1','-temporal-aq','1','-rc-lookahead','32','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart']
 cmd=[FF,'-hide_banner','-nostdin','-n','-threads','2','-f','rawvideo','-pix_fmt','yuv420p','-video_size','1920x1080','-framerate','60','-i','pipe:0','-filter_complex_threads','2','-filter_complex',graph,'-map','[clean]',*codec,str(D/'visual.mp4'),'-map','[captioned]',*codec,str(D/'captioned-video.mp4')]
 state['encoderCommand']=cmd;save()
 try:
  with (D/'dual-encode.log').open('w') as log:
   encoder=subprocess.Popen(cmd,cwd=R,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state['encoderPid']=encoder.pid;save()
   try:
    for index,n in enumerate(plan['nodes']):
     assert state['framesWritten']==n['startFrame'];count=0;sourceHash=hashlib.sha256()
     with av.open(str(R/n['framedPath'])) as c:
      s=c.streams.video[0];s.thread_type='SLICE';s.codec_context.thread_count=2
      assert s.width==1920 and s.height==1080 and s.average_rate==60
      start=n['framedStartFrame'];target=Fraction(start,60)/s.time_base;assert target.denominator==1
      c.seek(int(target),stream=s,backward=True,any_frame=False)
      for frame in c.decode(s):
       if frame.pts*s.time_base<Fraction(start,60):continue
       assert frame.pts*s.time_base==Fraction(start+count,60),(n['id'],count,frame.pts,s.time_base)
       raw=frame.to_ndarray(format='yuv420p').tobytes();assert len(raw)==1920*1080*3//2
       sourceHash.update(raw);encoder.stdin.write(raw);count+=1;state['framesWritten']+=1
       if count==n['frames']:break
     assert count==n['frames'],(n['id'],count,n['frames'])
     state['sourceIntervals'].append(dict(index=index,node=n['id'],startFrame=n['startFrame'],frames=count,sourceStartFrame=start,sourcePath=n['framedPath'],decodedYuv420pSha256=sourceHash.hexdigest(),exactSourcePts=True));save()
     if index%15==0:print('ENCODED',state['framesWritten'],'/',plan['frames'],flush=True)
   finally:encoder.stdin.close()
   rc=encoder.wait();assert rc==0,rc
  assert state['framesWritten']==plan['frames']
  for name in ['visual.mp4','captioned-video.mp4']:
   with av.open(str(D/name)) as c:
    s=c.streams.video[0];assert s.frames==plan['frames'] and s.time_base==Fraction(1,90000) and s.average_rate==60
    pts=sorted(p.pts for p in c.demux(s) if p.pts is not None);assert pts==list(range(0,plan['frames']*1500,1500))
   state['outputs'][name]=sha(D/name)
  state.update(status='complete-awaiting-mix-and-pixel-review',exitCode=0,endedAt=now());save()
 except BaseException as e:
  state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()
