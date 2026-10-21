"""Scoped baseline-preserving batch primitives; no publication or TTS."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,data):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def video(p):return next(s for s in probe(p)['streams'] if s['codec_type']=='video')
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
ENC=['-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-enc_time_base','1:60','-video_track_timescale','60000','-movflags','+faststart']
class Episode:
 def __init__(self,ident):
  self.entry=next(x for x in read(B/'queue.json')['entries'] if x['id']==ident);self.id=ident;self.slug=self.entry['slug']
  self.P=R/'projects'/self.slug;self.O=self.P/'production/local/private-polish-v1';self.H=self.P/'production/private-polish-v1';self.D=R/'output'/(self.slug+'-private-polish')
  self.O.mkdir(parents=True,exist_ok=True);self.H.mkdir(parents=True,exist_ok=True);self.T=read(self.P/'production/timeline.json')
 def authorized(self):
  key=read(B/'authorization.json')['id'];a=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations'][key]
  assert a['status']=='active' and a['fullProductionAuthorized'] and self.id in a['ids'] and not a['newTtsAuthorized']
  assert sha(self.P/'production/timeline.json')==self.entry['originalTimelineSha256']
 def run(self,args,log,cwd=None,env=None):
  with (self.O/log).open('w',encoding='utf8') as f:p=subprocess.run([str(a) for a in args],cwd=cwd or R,env=env,stdout=f,stderr=subprocess.STDOUT)
  if p.returncode:raise RuntimeError((self.O/log).read_text(encoding='utf8',errors='replace')[-2500:])
 def ff(self,args,log,cwd=None):self.run(['ffmpeg','-hide_banner','-loglevel','warning','-y',*args],log,cwd)
 def verify(self,path,frames):
  v=video(path);assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',frames),(str(path),v)
  return v
