"""Finite final pair, subtitle-aware preflight and current-output integrity checks."""
from pathlib import Path
import argparse,json,subprocess,hashlib,math
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]; R=P.parents[1]; L=P/'production/local'
BIN=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
FF=str(BIN/'ffmpeg.exe');FP=str(BIN/'ffprobe.exe')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def run(args):
 a=subprocess.run(args,capture_output=True)
 if a.returncode:raise RuntimeError(a.stderr.decode(errors='replace')[-4000:])
 return a.stdout
def guard():
 a=read(R/'shared/publishing/video-production-control.json')['shortsRecurringAuthorization']
 assert a['selectedShort']==P.name and a['latestSelection']['selectedRevision']=='zombie-quiet-v1'
def ass_filter():return 'ass='+str((L/'captions.ko.ass').relative_to(R)).replace('\\','/')
def preflight():
 guard();src=R/'shared/output/motion-canvas/shorts-zombie-quiet-director-preflight-pacing.mp4'
 out=L/'preflight-captioned.mp4'
 if not out.exists():run([FF,'-v','error','-n','-i',str(src),'-vf','setpts=PTS+13/TB,'+ass_filter()+',setpts=PTS-STARTPTS','-an','-c:v','libx264','-preset','fast','-crf','18',str(out)])
 for t in [.2,1.2,2.5]:
  target=L/f'preflight-{t}.png'
  if not target.exists():run([FF,'-v','error','-n','-ss',str(t),'-i',str(out),'-frames:v','1',str(target)])
def pair():
 guard();c=read(P/'script/captions.json');visual=R/'shared/output/motion-canvas/shorts-zombie-quiet-director-full-v2.mp4';mix=L/'final-mix.m4a'
 clean=L/'clean.mp4';captioned=L/'captioned.mp4'
 assert not clean.exists() and not captioned.exists(),'Preserve completed pair'
 run([FF,'-v','warning','-n','-i',str(visual),'-i',str(mix),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(clean)])
 run([FF,'-v','warning','-n','-i',str(clean),'-vf',ass_filter(),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(captioned)])
 save(L/'pair-build.json',dict(frames=c['frames'],durationSeconds=c['durationSeconds'],visual=sha(visual),audio=sha(mix),ass=sha(L/'captions.ko.ass'),clean=sha(clean),captioned=sha(captioned),speechSpeed=1))
def integrity():
 guard();c=read(P/'script/captions.json');reports=[];audio=[]
 for name in ['clean','captioned']:
  f=L/(name+'.mp4');run([FF,'-v','error','-xerror','-i',str(f),'-f','null','-'])
  info=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(f)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
  assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'60/1',c['frames'])
  stamps=json.loads(run([FP,'-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(f)]))['frames']
  pts=[float(x['best_effort_timestamp_time']) for x in stamps];assert len(pts)==c['frames'] and all(abs(t-i/60)<2e-6 for i,t in enumerate(pts))
  raw=run([FF,'-v','error','-i',str(f),'-map','0:a:0','-c','copy','-f','adts','pipe:1']);audio.append(hashlib.sha256(raw).hexdigest())
  reports.append(dict(name=name,sha256=sha(f),bytes=f.stat().st_size,format=info['format'],video=v,audio=a,decoded=True,ptsRegular60=True,frames=len(pts)))
 assert audio[0]==audio[1]
 save(L/'integrity.json',dict(status='pass',outputs=reports,identicalAac=True,aacHash=audio[0],all26KoEnCaptionTimesInsideVideo=True))
def qa():
 c=read(P/'script/captions.json');timing=read(L/'visual-timing.json');folder=L/'qa';folder.mkdir(exist_ok=True)
 times=sorted(set([round((x['start']+x['end'])/2,3) for x in c['cues']]+[.1,1.69,1.72,11.5,12.4,13.5,14.6,20.62,23.77,27.5,28.5,29.9,30.5,31.3,32.3,33.5,35.88,37.65,40.8,43.7]))
 rows=[]
 for i,t in enumerate(times):
  f=folder/f'frame-{i:03}.png'
  if not f.exists():run([FF,'-v','error','-n','-ss',str(t),'-i',str(L/'captioned.mp4'),'-frames:v','1',str(f)])
  rows.append(dict(id=i,seconds=t,path=str(f.relative_to(R)).replace('\\','/')))
 # Contact sheets are QA artifacts, never production assets.
 for start in range(0,len(rows),12):
  subset=rows[start:start+12];sheet=Image.new('RGB',(375*4,700*3),'#252525');draw=ImageDraw.Draw(sheet)
  for j,row in enumerate(subset):
   im=Image.open(R/row['path']).convert('RGB');im.thumbnail((375,666));x=j%4*375;y=j//4*700;sheet.paste(im,(x,y));draw.text((x+5,y+672),str(row['seconds'])+'s',fill='white')
  sheet.save(folder/f'sheet-{start//12+1:02}.jpg',quality=92)
 save(folder/'index.json',dict(captionMidpoints=26,rows=rows,scope='all26captioncues plus cuts/diagrambeforeactionresult/reactions; direct-moving-playback still required'))
 mobile=L/'mobile-review.mp4'
 if not mobile.exists():run([FF,'-v','error','-n','-i',str(L/'captioned.mp4'),'-vf','scale=374:666','-c:v','libx264','-crf','22','-preset','fast','-c:a','copy','-movflags','+faststart',str(mobile)])
def main():
 a=argparse.ArgumentParser();a.add_argument('command',choices=['preflight','pair','integrity','qa']);args=a.parse_args();globals()[args.command]()
if __name__=='__main__':main()
