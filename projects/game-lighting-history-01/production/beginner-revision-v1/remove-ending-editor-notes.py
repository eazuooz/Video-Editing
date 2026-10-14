"""Remove two production notes, retaining all earlier H264 packets unchanged."""
import pathlib,json,hashlib,datetime,subprocess,shutil,runpy
import av
from fractions import Fraction
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/continuity-v2';D=O/'pair-exact-v2';FF=shutil.which('ffmpeg')
BOX=[600,858,720,42]
RANGES=[(142577,143201),(143766,144448)]
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 runpy.run_path(str(pathlib.Path(__file__).with_name('production-authority.py')))['require_selected_production']()
 state=rd(D/'visual-execution.json');assert state['status']=='complete-awaiting-mix-and-pixel-review'
 assert not (D/'ending-note-removal.json').exists()
 total=rd(O/'plan.json')['frames'];report=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),box=BOX,ranges=RANGES,reason='Remove production-only notes 이미 설명한 답을 연결 and 다음 편 내용 예고; 새 사례로 이번 비율 채우지 않음. Preserve teaching text and captions.',outputs={})
 for name in ['visual.mp4','captioned-video.mp4']:
  original=D/name;assert sha(original)==state['outputs'][name]
  with av.open(str(original)) as c:
   s=c.streams.video[0];extra=s.codec_context.extradata;keys=[p.pts//1500 for p in c.demux(s) if p.pts is not None and p.is_keyframe and p.pts<=RANGES[0][0]*1500]
  cut=max(keys);assert 0<=RANGES[0][0]-cut<300
  tail=D/(original.stem+'-ending-tail.mp4');patched=D/(original.stem+'-ending-corrected.mp4');assert not tail.exists() and not patched.exists()
  enable='+'.join(f'gte(n,{a-cut})*lt(n,{b-cut})' for a,b in RANGES)
  vf=f"drawbox=x=600:y=858:w=720:h=42:color=black:t=fill:enable='{enable}',setsar=1"
  cmd=[FF,'-hide_banner','-v','error','-nostdin','-n','-threads','2','-ss',f'{cut/60:.9f}','-i',str(original),'-vf',vf,'-filter_threads','2','-frames:v',str(total-cut),'-an','-fps_mode','passthrough','-c:v','h264_nvenc','-preset','p7','-tune','hq','-rc','vbr','-cq','18','-b:v','0','-multipass','fullres','-spatial-aq','1','-temporal-aq','1','-rc-lookahead','32','-pix_fmt','yuv420p','-video_track_timescale','90000',str(tail)]
  subprocess.run(cmd,cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  with av.open(str(tail)) as c:
   s=c.streams.video[0];assert s.codec_context.extradata==extra and s.frames==total-cut and s.time_base==Fraction(1,90000)
  retained=hashlib.sha256();count=0;lastDts=None
  with av.open(str(original)) as base,av.open(str(tail)) as end,av.open(str(patched),'w',options={'movflags':'+faststart','video_track_timescale':'90000'}) as out:
   target=out.add_stream_from_template(base.streams.video[0])
   for p in base.demux(base.streams.video[0]):
    if p.pts is None:continue
    if p.is_keyframe and p.pts==cut*1500:break
    assert p.pts<cut*1500
    retained.update(bytes(p));count+=1;lastDts=p.dts;p.stream=target;out.mux(p)
   assert count==cut
   for p in end.demux(end.streams.video[0]):
    if p.pts is None:continue
    p.pts+=cut*1500;p.dts+=cut*1500;assert p.dts>lastDts;lastDts=p.dts;count+=1;p.stream=target;out.mux(p)
  assert count==total
  check=hashlib.sha256();pts=[];prefix=0
  with av.open(str(patched)) as c:
   s=c.streams.video[0];assert s.frames==total and s.average_rate==60
   for p in c.demux(s):
    if p.pts is None:continue
    pts.append(p.pts)
    if p.pts<cut*1500:check.update(bytes(p));prefix+=1
  assert sorted(pts)==list(range(0,total*1500,1500)) and prefix==cut and check.hexdigest()==retained.hexdigest()
  saved=D/(original.stem+'-before-ending-note-removal.mp4');assert not saved.exists();original.rename(saved);patched.rename(original)
  report['outputs'][name]=dict(priorFile=saved.name,priorSha256=state['outputs'][name],sha256=sha(original),retainedPrefixFrames=cut,retainedPrefixPacketSha256=retained.hexdigest(),reencodedTailFrames=total-cut,allPtsVerified=True)
  state['outputs'][name]=report['outputs'][name]['sha256']
 state['endingNoteRemoval']='ending-note-removal.json';wr(D/'visual-execution.json',state);wr(D/'ending-note-removal.json',report)
 print('Ending notes removed; prefix packets retained; every frame PTS verified')
if __name__=='__main__':main()
