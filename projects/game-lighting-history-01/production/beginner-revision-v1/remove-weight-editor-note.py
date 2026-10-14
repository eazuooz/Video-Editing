"""Remove the remaining weight-example production note within closed GOPs only."""
import pathlib, json, hashlib, datetime, subprocess, shutil, runpy
import av
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/continuity-v2';D=O/'pair-exact-v2';FF=shutil.which('ffmpeg')
A,Z=40805,41643
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 runpy.run_path(str(pathlib.Path(__file__).with_name('production-authority.py')))['require_selected_production']()
 state=rd(D/'visual-execution.json');total=rd(O/'plan.json')['frames'];assert not (D/'weight-note-removal.json').exists()
 report=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),range=[A,Z],box=[600,850,720,50],reason='Remove internal note 정확한 예제 비중을 유지; retain formula, weights and narration.',outputs={})
 for name in ['visual.mp4','captioned-video.mp4']:
  src=D/name;assert sha(src)==state['outputs'][name]
  with av.open(str(src)) as c:
   s=c.streams.video[0];extra=s.codec_context.extradata;keys=[p.pts//1500 for p in c.demux(s) if p.pts is not None and p.is_keyframe]
  lo=max(k for k in keys if k<=A);hi=min(k for k in keys if k>=Z);assert A-lo<300 and hi-Z<300
  patch=D/(src.stem+'-weight-gop.mp4');dest=D/(src.stem+'-weight-corrected.mp4')
  vf=f"drawbox=x=600:y=850:w=720:h=50:color=black:t=fill:enable='gte(n,{A-lo})*lt(n,{Z-lo})',setsar=1"
  args=[FF,'-hide_banner','-v','error','-nostdin','-n','-threads','2','-ss',f'{lo/60:.9f}','-i',str(src),'-vf',vf,'-filter_threads','2','-frames:v',str(hi-lo),'-an','-fps_mode','passthrough','-c:v','h264_nvenc','-preset','p7','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-multipass','fullres','-spatial-aq','1','-temporal-aq','1','-rc-lookahead','32','-pix_fmt','yuv420p','-video_track_timescale','90000',str(patch)]
  subprocess.run(args,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  with av.open(str(patch)) as c:assert c.streams.video[0].codec_context.extradata==extra and c.streams.video[0].frames==hi-lo
  retained=hashlib.sha256();count=0;lastDts=None;inserted=False
  with av.open(str(src)) as base,av.open(str(patch)) as replacement,av.open(str(dest),'w',options={'movflags':'+faststart','video_track_timescale':'90000'}) as out:
   target=out.add_stream_from_template(base.streams.video[0])
   for p in base.demux(base.streams.video[0]):
    if p.pts is None:continue
    if lo*1500<=p.pts<hi*1500:
     if not inserted:
      assert p.is_keyframe and p.pts==lo*1500
      for q in replacement.demux(replacement.streams.video[0]):
       if q.pts is None:continue
       q.pts+=lo*1500;q.dts+=lo*1500;assert lastDts is None or q.dts>lastDts;lastDts=q.dts;q.stream=target;out.mux(q);count+=1
      inserted=True
     continue
    assert lastDts is None or p.dts>lastDts;lastDts=p.dts;retained.update(bytes(p));p.stream=target;out.mux(p);count+=1
  assert inserted and count==total
  check=hashlib.sha256();pts=[]
  with av.open(str(dest)) as c:
   s=c.streams.video[0];assert s.frames==total and s.average_rate==60
   for p in c.demux(s):
    if p.pts is None:continue
    pts.append(p.pts)
    if not lo*1500<=p.pts<hi*1500:check.update(bytes(p))
  assert sorted(pts)==list(range(0,total*1500,1500)) and check.hexdigest()==retained.hexdigest()
  old=D/(src.stem+'-before-weight-note-removal.mp4');src.rename(old);dest.rename(src)
  report['outputs'][name]=dict(priorFile=old.name,priorSha256=state['outputs'][name],sha256=sha(src),reencodedFrameRange=[lo,hi],retainedFrames=total-(hi-lo),retainedPacketSha256=retained.hexdigest(),allPtsVerified=True)
  state['outputs'][name]=report['outputs'][name]['sha256']
 state['weightNoteRemoval']='weight-note-removal.json';wr(D/'visual-execution.json',state);wr(D/'weight-note-removal.json',report)
 # Preserve the earlier master, its completed integrity check and visual evidence.
 for name in ['clean.mp4','captioned.mp4','execution.json']:(D/name).rename(D/('before-weight-note-'+name))
 print(json.dumps(report))
if __name__=='__main__':main()
