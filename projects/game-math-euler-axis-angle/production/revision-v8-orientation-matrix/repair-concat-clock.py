"""Lossless frame-clock repair after observed concat duration rounding.

Reuse all encoded paragraph bytes; exact clip durations plus timestamp-only
bitstream filtering restore60Hz. Original failed-clock masters stay archived.
"""
from pathlib import Path
import importlib.util,json,subprocess,argparse,shutil
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_clock_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
D=c.O/'edit/clock-repair';D.mkdir(exist_ok=True);E=c.O/'edit'
FILTER='setts=pts=round(PTS/1000)*1000:dts=round(DTS/1000)*1000:duration=1000:time_base=1/60000:prescale=1'
def run(args):
 r=subprocess.run(['ffmpeg','-v','warning','-nostdin','-n',*map(str,args)],capture_output=True,cwd=c.R,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 assert r.returncode==0,r.stderr.decode(errors='replace')[-1800:]
def payload(file,stream):
 r=subprocess.run(['ffmpeg','-v','error','-nostdin','-i',str(file),'-map',stream,'-c','copy','-f','hash','-hash','sha256','-'],capture_output=True);assert r.returncode==0,r.stderr
 return r.stdout.decode().strip()
def build():
 c.authorized();t=c.read(H/'timeline.json');v=c.read(E/'visual-build.json');master=c.read(E/'master-build.json');rows=[]
 for kind in ['clean','captioned']:
  old=c.O/('orientation-matrix.'+kind+'.mp4');original=next(x for x in master['outputs']if x['kind']==kind);assert c.sha(old)==original['sha256']
  files=[(c.R/t['branding']['intro']['file'],120),*[(c.R/next(o['file']for o in row['outputs']if o['kind']==kind),row['frames'])for row in v['paragraphs']],(c.R/t['branding']['membership']['file'],600)]
  listing=D/(kind+'.ffconcat');listing.write_text('ffconcat version1.0\n'.replace('version1','version 1')+''.join("file '"+str(f.resolve()).replace('\\','/')+"'\nduration "+f'{frames/60:.12f}\n'for f,frames in files),encoding='utf8')
  visual=D/(kind+'-visual.mp4');new=D/('orientation-matrix.'+kind+'.mp4')
  run(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-c:v','copy','-bsf:v',FILTER,'-video_track_timescale','60000','-movflags','+faststart',visual])
  run(['-i',visual,'-i',c.O/'mix/final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','60000','-t',f'{t["duration"]:.9f}','-movflags','+faststart',new])
  oldv=payload(old,'0:v:0');newv=payload(new,'0:v:0');olda=payload(old,'0:a:0');newa=payload(new,'0:a:0');assert oldv==newv and olda==newa,'No compressed picture or AAC byte may change'
  probe=c.probe(new);stream=next(x for x in probe['streams']if x['codec_type']=='video');assert(stream['width'],stream['height'],stream['avg_frame_rate'],int(stream['nb_frames']))==(1920,1080,'60/1',t['totalFrames']),stream
  assert abs(float(stream['duration'])-t['duration'])<1e-7
  rows.append(dict(kind=kind,original=dict(original),repaired=dict(file=c.rel(new),sha256=c.sha(new),bytes=new.stat().st_size),visual=dict(file=c.rel(visual),sha256=c.sha(visual)),videoPacketPayload=oldv,audioPacketPayload=olda,compressedPayloadsUnchanged=True,videoStream=stream))
 c.save(D/'repair.json',dict(reason='Actual complete decode found concat format-duration rounding: first offset -20/60000s atF1127; cumulative24ms at end.',method='Explicit frames/60 duration perclip; timestamp-only setts quantization onto60000/60 clock; H264 and AAC payload hashes identical',filter=FILTER,rows=rows,frames=t['totalFrames'],duration=t['duration'],pixelReencode=False,audioReencode=False,installed=False,fullCorrectedFrameDecode='pending'))
 print('Built exact60Hz packet-clock copies; compressed pictures and audio unchanged')
def install():
 c.authorized();r=c.read(D/'repair.json');assert not r['installed'];master=c.read(E/'master-build.json');visual=c.read(E/'visual-build.json');history=E/'clock-history'/master['outputs'][1]['sha256'][:12];history.mkdir(parents=True,exist_ok=False)
 for path in [E/'master-build.json',E/'visual-build.json']:
  shutil.copy2(path,history/path.name)
 for row in r['rows']:
  kind=row['kind'];old=c.O/('orientation-matrix.'+kind+'.mp4');new=c.R/row['repaired']['file'];ov=E/(kind+'-visual.mp4');nv=c.R/row['visual']['file']
  assert c.sha(old)==row['original']['sha256']and c.sha(new)==row['repaired']['sha256']and c.sha(nv)==row['visual']['sha256']
  for src,dst in [(old,history/old.name),(ov,history/ov.name),(new,old),(nv,ov)]:
   src.resolve().relative_to(c.O.resolve());dst.resolve().relative_to(c.O.resolve());assert not dst.exists();src.rename(dst)
  item=next(x for x in master['outputs']if x['kind']==kind);item.update(file=c.rel(old),sha256=c.sha(old),bytes=old.stat().st_size)
  item=next(x for x in visual['versions']if x['kind']==kind);item.update(file=c.rel(ov),sha256=c.sha(ov))
  row['installedMaster']=c.rel(old);row['installedVisual']=c.rel(ov)
 r.update(installed=True,history=c.rel(history));c.save(D/'repair.json',r)
 for path,data in [(E/'master-build.json',master),(E/'visual-build.json',visual)]:data['frameClockRepair']=dict(file=c.rel(D/'repair.json'),sha256=c.sha(D/'repair.json'));c.save(path,data)
 print('Installed corrected current master; original failed-clock files preserved')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--install',action='store_true');a=p.parse_args()
 if a.build:build()
 if a.install:install()
