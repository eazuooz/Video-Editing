"""Remove one editorial note; encode only the first closed GOP range.

The remainder is copied as original H264 packets with unchanged timestamps.
Preserve pre-correction files and prove packet equivalence for the retained tail.
"""
import pathlib,json,subprocess,shutil,hashlib,datetime,runpy
import av
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/continuity-v2';D=O/'pair';FF=shutil.which('ffmpeg')
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 runpy.run_path(str(pathlib.Path(__file__).with_name('production-authority.py')))['require_selected_production']()
 state=rd(D/'visual-execution.json');assert state['status']=='complete-awaiting-mix-and-pixel-review'
 report=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='Remove production-only note 질문을 먼저 제시 from intro. Keep teaching labels, geometry and fixed captions.',box=[800,819,320,45],startFrame=120,endFrame=438,tailBitstreamUnchanged=True,outputs={})
 assert not (D/'intro-note-removal.json').exists()
 for name in ['visual.mp4','captioned-video.mp4']:
  original=D/name;assert sha(original)==state['outputs'][name]
  with av.open(str(original)) as src:
   stream=src.streams.video[0];key=next(p for p in src.demux(stream) if p.is_keyframe and p.pts is not None and p.pts>=438*1500);cut=key.pts//1500;oldExtra=stream.codec_context.extradata
  assert cut==438,'Inspect unexpected GOP boundary before patching.'
  head=D/(original.stem+'-intro-head.mp4');patched=D/(original.stem+'-intro-corrected.mp4');assert not head.exists() and not patched.exists()
  vf="drawbox=x=800:y=819:w=320:h=45:color=black:t=fill:enable='gte(n,120)*lt(n,438)',setsar=1"
  cmd=[FF,'-hide_banner','-v','error','-nostdin','-n','-threads','2','-i',str(original),'-vf',vf,'-filter_threads','2','-frames:v',str(cut),'-an','-fps_mode','passthrough','-c:v','h264_nvenc','-preset','p7','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-multipass','fullres','-spatial-aq','1','-temporal-aq','1','-rc-lookahead','32','-pix_fmt','yuv420p','-video_track_timescale','90000',str(head)]
  subprocess.run(cmd,cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  with av.open(str(head)) as h:assert h.streams.video[0].codec_context.extradata==oldExtra,'SPS/PPS differ: do not concatenate incompatible encoding.'
  tailHash=hashlib.sha256();tailCount=0
  with av.open(str(original)) as base,av.open(str(head)) as first,av.open(str(patched),'w',options={'movflags':'+faststart','video_track_timescale':'90000'}) as out:
   target=out.add_stream_from_template(base.streams.video[0]);lastDts=None;count=0
   for packet in first.demux(first.streams.video[0]):
    if packet.pts is None:continue
    lastDts=packet.dts;packet.stream=target;out.mux(packet);count+=1
   assert count==cut
   started=False
   for packet in base.demux(base.streams.video[0]):
    if packet.pts is None:continue
    if not started:
     if packet.is_keyframe and packet.pts==cut*1500:started=True
     else:continue
    assert packet.dts>lastDts;lastDts=packet.dts
    tailHash.update(bytes(packet));tailCount+=1;packet.stream=target;out.mux(packet)
  expected=rd(O/'plan.json')['frames'];assert cut+tailCount==expected
  check=hashlib.sha256();pts=[];started=False
  with av.open(str(patched)) as c:
   s=c.streams.video[0];assert s.frames==expected and s.width==1920 and s.height==1080 and s.average_rate==60
   for packet in c.demux(s):
    if packet.pts is None:continue
    pts.append(packet.pts)
    if packet.is_keyframe and packet.pts==cut*1500:started=True
    if started:check.update(bytes(packet))
  assert sorted(pts)==list(range(0,expected*1500,1500)) and check.hexdigest()==tailHash.hexdigest()
  saved=D/(original.stem+'-before-intro-note-removal.mp4');assert not saved.exists();original.rename(saved);patched.rename(original)
  report['outputs'][name]=dict(priorFile=saved.name,priorSha256=state['outputs'][name],sha256=sha(original),reencodedFrames=cut,retainedPackets=tailCount,retainedPacketSha256=tailHash.hexdigest(),ptsVerifiedEveryFrame=True)
  state['outputs'][name]=report['outputs'][name]['sha256']
 state['introNoteRemoval']='intro-note-removal.json';wr(D/'visual-execution.json',state);wr(D/'intro-note-removal.json',report)
 print('Removed intro production note; all tail packets/PTS preserved for both files')
if __name__=='__main__':main()
