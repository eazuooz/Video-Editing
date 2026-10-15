"""Replace only closed-GOP review ranges; keep all other H.264 packets intact."""
import pathlib,json,hashlib,subprocess,shutil,runpy,datetime
from fractions import Fraction
import av
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/review-v3';B=P/'production/local/continuity-v2';D=O/'pair';FF=shutil.which('ffmpeg')
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def frames(path,start,count):
 with av.open(str(path)) as c:
  s=c.streams.video[0];s.thread_type='SLICE';s.codec_context.thread_count=2;c.seek(int(Fraction(start,60)/s.time_base),stream=s,backward=True)
  n=0
  for f in c.decode(s):
   if f.pts*s.time_base<Fraction(start,60):continue
   assert f.pts*s.time_base==Fraction(start+n,60),(path,start,n,f.pts,s.time_base)
   yield f.to_ndarray(format='yuv420p').tobytes();n+=1
   if n==count:break
  assert n==count
def main():
 runpy.run_path(str(H.parent/'beginner-revision-v1/production-authority.py'))['require_selected_production']()
 assert not (R/'shared/output/GPU_HANDOFF.json').exists()
 plan=rd(O/'plan.json');assert plan['finalTimingApproved'];D.mkdir(exist_ok=True)
 source=B/'pair-exact-v2';base=source/'visual.mp4';total=145768
 with av.open(str(base)) as c:
  s=c.streams.video[0];extra=s.codec_context.extradata;keys=[p.pts//1500 for p in c.demux(s) if p.pts is not None and p.is_keyframe]+[total]
 windows=[]
 for a,b in plan['changedBaselineRanges']:
  lo=max(k for k in keys if k<=a);hi=min(k for k in keys if k>=b)
  if windows and lo<=windows[-1][1]:windows[-1][1]=max(hi,windows[-1][1])
  else:windows.append([lo,hi])
 delta=plan['frames']-total;mapf=lambda f:f if f<=64119 else f+delta if f>=67924 else (_ for _ in []).throw(ValueError('boundary inside replacement'))
 state=dict(status='encoding-selected-ranges',planSha256=sha(O/'plan.json'),windows=windows,completed=[],retainedPackets={},outputs={},startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
 statepath=D/'visual-execution.json'
 if statepath.exists():state=rd(statepath);assert state['planSha256']==sha(O/'plan.json')
 codec=['-an','-fps_mode','passthrough','-c:v','h264_nvenc','-preset','p7','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-multipass','fullres','-spatial-aq','1','-temporal-aq','1','-rc-lookahead','32','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart']
 ass=(O/'captions.ko.ass').relative_to(R).as_posix();fonts=(P/'production/local/final-edit-v1/fonts').relative_to(R).as_posix()
 for i,(lo,hi) in enumerate(windows):
  if i in state['completed']:continue
  start,end=mapf(lo),mapf(hi);overlays=[]
  for h in plan['termHeaders']:
   a,b=h['startFrame'],h['endFrame']
   if start<=a and b<=end:
    enabled=f'gte(n,{a-start})*lt(n,{b-start})';overlays.append(f"drawbox=x=0:y=0:w=1920:h=133:color=black:t=fill:enable='{enabled}'")
    for j,key in enumerate(['titleFile','subtitleFile']):
     overlays.append(f"drawtext=fontfile='{fonts}/YamYamCaptionMedium.ttf':textfile='{h[key]}':fontcolor={'0xe8cf83' if j==0 else '0xb9bcbc'}:fontsize={44 if j==0 else 30}:x=(w-tw)/2:y={35 if j==0 else 93}:enable='{enabled}'")
  initial=','.join(overlays)+',' if overlays else ''
  graph=f"[0:v]{initial}split=2[clean][text];[text]settb=1/60,setpts=N+{start},ass='{ass}':fontsdir='{fonts}',setpts=PTS-{start}[captioned]"
  outs=[D/f'patch-{i}-{n}.mp4' for n in ['clean','captioned']]
  cmd=[FF,'-v','error','-nostdin','-n','-f','rawvideo','-pixel_format','yuv420p','-video_size','1920x1080','-framerate','60','-i','pipe:0','-filter_complex_threads','2','-filter_complex',graph,'-map','[clean]',*codec,str(outs[0]),'-map','[captioned]',*codec,str(outs[1])]
  with (D/f'patch-{i}.log').open('w') as log:
   enc=subprocess.Popen(cmd,cwd=R,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);written=0
   try:
    for n in plan['nodes']:
     a,b=max(start,n['startFrame']),min(end,n['endFrame'])
     if b<=a:continue
     for raw in frames(R/n['framedPath'],n['framedStartFrame']+a-n['startFrame'],b-a):enc.stdin.write(raw);written+=1
   finally:enc.stdin.close()
   assert enc.wait()==0 and written==end-start
  for file in outs:
   with av.open(str(file)) as c:
    s=c.streams.video[0];assert s.frames==end-start and s.codec_context.extradata==extra,(str(file),'SPS mismatch')
  state['completed'].append(i);wr(statepath,state);print('PATCH',i,written,flush=True)
 # Join packet sequences at verified closed GOP boundaries, resetting time only.
 for kind,name in [('clean','visual.mp4'),('captioned','captioned-video.mp4')]:
  outpath=D/name
  if name in state['outputs']:assert sha(outpath)==state['outputs'][name];continue
  retained=hashlib.sha256();retainedCount=0;written=0;last=-999999
  with av.open(str(source/name)) as c,av.open(str(outpath),'w',options={'movflags':'+faststart','video_track_timescale':'90000'}) as out:
   s=c.streams.video[0];target=out.add_stream_from_template(s);i=0
   for p in c.demux(s):
    if p.pts is None:continue
    f=p.pts//1500
    if i<len(windows) and p.is_keyframe and f==windows[i][0]:
     lo,hi=windows[i];offset=mapf(lo)*1500
     with av.open(str(D/f'patch-{i}-{kind}.mp4')) as patch:
      for q in patch.demux(patch.streams.video[0]):
       if q.pts is None:continue
       q.pts+=offset;q.dts+=offset;assert q.dts>last;last=q.dts;q.stream=target;out.mux(q);written+=1
    if any(a<=f<b for a,b in windows):continue
    while i<len(windows) and f>=windows[i][1]:i+=1
    retained.update(bytes(p));retainedCount+=1;offset=(mapf(f)-f)*1500;p.pts+=offset;p.dts+=offset;assert p.dts>last;last=p.dts;p.stream=target;out.mux(p);written+=1
  assert written==plan['frames']
  check=hashlib.sha256();count=0;pts=[]
  nw=[(mapf(a),mapf(b)) for a,b in windows]
  with av.open(str(outpath)) as c:
   s=c.streams.video[0];assert s.frames==plan['frames'] and s.average_rate==60
   for p in c.demux(s):
    if p.pts is None:continue
    pts.append(p.pts);f=p.pts//1500
    if not any(a<=f<b for a,b in nw):check.update(bytes(p));count+=1
  assert sorted(pts)==list(range(0,plan['frames']*1500,1500)) and count==retainedCount and check.hexdigest()==retained.hexdigest()
  state['outputs'][name]=sha(outpath);state['retainedPackets'][name]=dict(frames=count,sha256=check.hexdigest(),unchangedBytes=True);wr(statepath,state)
 state.update(status='complete-awaiting-mix-and-pixel-review',exitCode=0);wr(statepath,state)
if __name__=='__main__':main()
