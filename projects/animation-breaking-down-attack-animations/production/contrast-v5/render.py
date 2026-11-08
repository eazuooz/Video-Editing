"""Sequential CPU-only render. Reuse unchanged AAC packets and SRT bytes."""
from pathlib import Path
import json,subprocess,hashlib,sys,shutil,os,time
import visual
from prepare import H,P,R,B,L,read,save,sha
ENC=['-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-x264-params','scenecut=0','-bf','0','-g','120','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
def ff(args,log):
 with log.open('wb') as f:subprocess.run(['ffmpeg','-nostdin','-hide_banner','-v','error','-y',*map(str,args)],stdout=f,stderr=f,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def valid(p,n):
 if not p.exists():return False
 try:v=next(x for x in probe(p)['streams'] if x['codec_type']=='video');return int(v['nb_frames'])==n and (v['width'],v['height'])==(1920,1080)
 except Exception:return False
def changed(row,dest):
 if valid(dest,row['frames']):return
 log=dest.with_suffix('.log')
 with log.open('wb') as f:
  proc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0','-an',*ENC,str(dest)],stdin=subprocess.PIPE,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   previous=None;raw=None
   for i in range(row['frames']):
    # Exact source frames repeat in slow analysis; cache identical visual states.
    im=visual.frame(row,i);proc.stdin.write(im.tobytes())
  finally:proc.stdin.close()
  assert proc.wait()==0,dest
def run():
 c=read(R/'shared/publishing/video-production-control.json')['a03ContrastRevision20261108'];assert c['fullLocalRevisionAuthorized']
 plan=read(H/'edit-plan.json');V=L/'rendered';parts=L/'parts';V.mkdir(parents=True,exist_ok=True);parts.mkdir(exist_ok=True)
 base=R/next(x['path'] for x in plan['baseline']['files'] if x['kind']=='clean.mp4');assert sha(base)==next(x['sha256'] for x in plan['baseline']['files'] if x['kind']=='clean.mp4')
 for row in plan['rows']:
  print('render',row['key'],row['frames'],flush=True);changed(row,parts/(row['key']+'.mp4'))
  save(H/'checkpoint.json',{'revision':'contrast-v5','stage':'rendering-changed-visuals','lastCompleted':row['key'],'baselinePreserved':True,'humanReview':False})
 sequence=[];cursor=0
 for i,row in enumerate(plan['rows']):
  if row['start']>cursor:
   dest=parts/f'base-{i:02d}.mp4';n=row['start']-cursor
   if not valid(dest,n):ff(['-threads','2','-filter_threads','2','-ss',cursor/60,'-i',base,'-vf','settb=1/60,setpts=N','-frames:v',n,'-an',*ENC,dest],dest.with_suffix('.log'))
   sequence.append(dest)
  sequence.append(parts/(row['key']+'.mp4'));cursor=row['end'];print('sequence',row['key'],flush=True)
 if cursor<plan['totalFrames']:
  dest=parts/'base-end.mp4';n=plan['totalFrames']-cursor
  if not valid(dest,n):ff(['-threads','2','-filter_threads','2','-ss',cursor/60,'-i',base,'-vf','settb=1/60,setpts=N','-frames:v',n,'-an',*ENC,dest],dest.with_suffix('.log'))
  sequence.append(dest)
 assert sum(int(next(x for x in probe(p)['streams'] if x['codec_type']=='video')['nb_frames']) for p in sequence)==plan['totalFrames']
 concat=L/'concat.txt';concat.write_text(''.join("file '"+str(p).replace('\\','/')+"'\n" for p in sequence),'utf-8')
 pic=L/'picture.mp4'
 if not valid(pic,plan['totalFrames']):ff(['-f','concat','-safe','0','-i',concat,'-c','copy',pic],L/'concat.log')
 clean=V/(P.name+'.clean.mp4')
 if not valid(clean,plan['totalFrames']):ff(['-i',pic,'-i',base,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',clean],L/'clean.log')
 cap=V/(P.name+'.captioned.mp4');ass=P/'production/local/relations-v4/captions.ass';escape=str(ass).replace('\\','/').replace(':','\\:')
 if not valid(cap,plan['totalFrames']):ff(['-threads','2','-filter_threads','2','-i',clean,'-vf',f"ass='{escape}'",'-map','0:v:0','-map','0:a:0',*ENC,'-c:a','copy','-movflags','+faststart',cap],L/'captioned.log')
 for lang in ['ko','en']:
  src=R/next(x['path'] for x in plan['baseline']['files'] if x['kind']==lang+'.srt');shutil.copy2(src,V/(P.name+'.'+lang+'.srt'))
 save(H/'checkpoint.json',{'revision':'contrast-v5','stage':'rendered-awaiting-current-encoded-qa','frames':plan['totalFrames'],'directory':str(V),'baselinePreserved':True,'humanReview':False})
 print('four files rendered',flush=True)
if __name__=='__main__':run()
