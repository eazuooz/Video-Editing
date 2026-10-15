"""Add editorial guides only in selected closed GOPs of the immutable v3 pair."""
import pathlib,json,hashlib,subprocess,shutil,runpy,datetime,sys
from fractions import Fraction
import av
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01'
H=pathlib.Path(__file__).parent;O=P/'production/local/review-v4';B=P/'production/local/review-v3';D=O/'pair';FF=shutil.which('ffmpeg')
rd=lambda p:json.loads(p.read_text('utf8'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def frames(path,start,count):
 with av.open(str(path)) as c:
  s=c.streams.video[0];s.thread_type='SLICE';s.codec_context.thread_count=2;c.seek(int(Fraction(start,60)/s.time_base),stream=s,backward=True);n=0
  for f in c.decode(s):
   if f.pts*s.time_base<Fraction(start,60):continue
   assert f.pts*s.time_base==Fraction(start+n,60)
   yield f.to_ndarray(format='yuv420p').tobytes();n+=1
   if n==count:break
  assert n==count
def main():
 control=runpy.run_path(str(H.parent/'beginner-revision-v1/production-authority.py'))['require_selected_production']()
 assert control['selectedVideoRevision']['id']=='review-v4'
 handoff=R/'shared/output/GPU_HANDOFF.json'
 assert not handoff.exists(), 'Inspect any new GPU handoff before proceeding'
 D.mkdir(exist_ok=True);design=rd(H/'annotations.json');plan=rd(B/'plan.json');total=plan['frames'];assert total==153402
 source=B/'pair';keys=None;extra=None
 for kind in ['clean','captioned']:
  with av.open(str(source/(kind+'.mp4'))) as c:
   s=c.streams.video[0];assert s.time_base==Fraction(1,90000) and s.average_rate==60
   if extra is None:extra=s.codec_context.extradata
   assert s.codec_context.extradata==extra
   k={p.pts//1500 for p in c.demux(s) if p.pts is not None and p.is_keyframe}|{total}
   keys=k if keys is None else keys&k
 keys=sorted(keys);windows=[]
 for w in sorted((w for w in design['windows'] if w['status']!='omitted'),key=lambda w:w['startFrame']):
  lo=max(k for k in keys if k<=w['startFrame']);hi=min(k for k in keys if k>=w['endFrame'])
  if windows and lo<=windows[-1][1]:windows[-1][1]=max(hi,windows[-1][1])
  else:windows.append([lo,hi])
 statepath=D/'visual-execution.json';fingerprint=dict(annotationSha256=sha(H/'annotations.json'),assSha256=sha(O/'annotations.ass'),styleSha256=sha(R/'shared/publishing/footage-annotation-style.json'),baselinePlanSha256=sha(B/'plan.json'))
 state=dict(status='encoding-selected-ranges',inputs=fingerprint,windows=windows,completed=[],outputs={},retainedPackets={},startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
 if statepath.exists():state=rd(statepath);assert state['inputs']==fingerprint and state['windows']==windows
 wr(statepath,state)
 codec=['-an','-fps_mode','passthrough','-c:v','h264_nvenc','-preset','p7','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-multipass','fullres','-spatial-aq','1','-temporal-aq','1','-rc-lookahead','32','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart']
 ass=(O/'annotations.ass').relative_to(R).as_posix()
 for i,(lo,hi) in enumerate(windows):
  for kind in ['clean','captioned']:
   key=f'{i}-{kind}'
   if key in state['completed']:continue
   path=D/f'patch-{key}.mp4';vf=f"settb=1/60,setpts=N+{lo},ass='{ass}',setpts=PTS-{lo}"
   cmd=[FF,'-v','error','-nostdin','-n','-f','rawvideo','-pixel_format','yuv420p','-video_size','1920x1080','-framerate','60','-i','pipe:0','-filter_threads','2','-vf',vf,*codec,str(path)]
   with (D/f'patch-{key}.log').open('w') as log:
    enc=subprocess.Popen(cmd,cwd=R,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
     for raw in frames(source/(kind+'.mp4'),lo,hi-lo):enc.stdin.write(raw)
    finally:enc.stdin.close()
    assert enc.wait()==0,key
   with av.open(str(path)) as c:
    s=c.streams.video[0];assert s.frames==hi-lo and s.codec_context.extradata==extra,(key,'codec mismatch')
   state['completed'].append(key);wr(statepath,state);print('PATCH',key,hi-lo,flush=True)
  if '--sample-only' in sys.argv:return
 for kind,name in [('clean','visual.mp4'),('captioned','captioned-video.mp4')]:
  outpath=D/name
  if name in state['outputs']:assert sha(outpath)==state['outputs'][name];continue
  retained=hashlib.sha256();count=0;written=0;last=-99999;inserted=set()
  with av.open(str(source/(kind+'.mp4'))) as c,av.open(str(outpath),'w',options={'movflags':'+faststart','video_track_timescale':'90000'}) as out:
   s=c.streams.video[0];target=out.add_stream_from_template(s)
   for p in c.demux(s):
    if p.pts is None:continue
    f=p.pts//1500;wi=next((i for i,(a,b) in enumerate(windows) if a<=f<b),None)
    if wi is not None:
     if wi not in inserted:
      lo,hi=windows[wi];assert p.is_keyframe and f==lo
      with av.open(str(D/f'patch-{wi}-{kind}.mp4')) as patch:
       for q in patch.demux(patch.streams.video[0]):
        if q.pts is None:continue
        q.pts+=lo*1500;q.dts+=lo*1500;assert q.dts>last;last=q.dts;q.stream=target;out.mux(q);written+=1
      inserted.add(wi)
     continue
    retained.update(bytes(p));count+=1;assert p.dts>last;last=p.dts;p.stream=target;out.mux(p);written+=1
  assert written==total and len(inserted)==len(windows)
  check=hashlib.sha256();n=0;pts=[]
  with av.open(str(outpath)) as c:
   for p in c.demux(c.streams.video[0]):
    if p.pts is None:continue
    pts.append(p.pts);f=p.pts//1500
    if not any(a<=f<b for a,b in windows):check.update(bytes(p));n+=1
  assert sorted(pts)==list(range(0,total*1500,1500)) and n==count and check.hexdigest()==retained.hexdigest()
  state['outputs'][name]=sha(outpath);state['retainedPackets'][name]=dict(frames=n,sha256=check.hexdigest(),unchangedBytes=True,unchangedTiming=True);wr(statepath,state)
 state.update(status='complete-awaiting-mix-and-pixel-review',exitCode=0);wr(statepath,state)
 print('Joined pair; retained packets identical',flush=True)
if __name__=='__main__':main()
