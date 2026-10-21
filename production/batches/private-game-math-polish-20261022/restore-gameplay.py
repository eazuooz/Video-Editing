"""Restore original FHD cut slots. New annotations and actual pixel QA are separate."""
import sys,shutil
from polish_common import *
results={}
for ident in sys.argv[1:]:
 try:
  e=Episode(ident);e.authorized();assert ident not in ['M05','M06']
  folder=e.O/'gameplay';folder.mkdir(exist_ok=True);(e.O/'clips').mkdir(exist_ok=True)
  target=e.H/'gameplay-restoration.json';records=read(target) if target.exists() else {'scenes':{}}
  for s in e.T['scenes']:
   if s['classification']!='actual':continue
   e.authorized();sid=s['id'];cut=s['cut'];sources=[];parts=[]
   for j,seg in enumerate(cut['segments']):
    src=R/seg.get('sourceFile',cut['sourceFile']);v=video(src)
    assert v['width']>=1920 and v['height']>=1080,(sid,'FHD original required',str(src))
    assert seg['in']+seg['frames']/60<=float(probe(src)['format']['duration'])+.03
    assert cut.get('sourceSpeed',1)==1
    vf='scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1'
    if cut.get('sourceFraming'):
     # Retained framing was authored in the original FHD coordinate canvas.
     vf+=','+cut['sourceFraming']['filter']
    vf+=',fps=60'
    part=folder/f'{sid}-{j+1}.mp4';sig={'sourceSha256':sha(src),'source':rel(src),'sourceIn':seg['in'],'frames':seg['frames'],'vf':vf};receipt=part.with_suffix('.json')
    if not(part.exists() and receipt.exists() and read(receipt)==sig):
     e.ff(['-ss',seg['in'],'-i',src,'-vf',vf,'-frames:v',seg['frames'],'-an',*ENC,part],f'gameplay-{sid}-{j+1}.log');save(receipt,sig)
    e.verify(part,seg['frames']);parts.append(part);sources.append(sig)
   dst=e.O/f'clips/{sid}.mp4';listing=folder/f'{sid}-concat.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts)+'\n',encoding='utf8')
   e.ff(['-f','concat','-safe','0','-i',listing,'-c','copy','-an','-video_track_timescale','60000',dst],f'gameplay-{sid}-concat.log');e.verify(dst,s['frames'])
   records['scenes'][sid]={'path':rel(dst),'sha256':sha(dst),'sources':sources,'frames':s['frames'],'speed':1,'originalCutOrderAndDuration':True,'currentMovingPixelReview':'pending','annotationPolish':'pending: inspect actual target before authoring or restoring guides','sourceAudio':'unchanged original narration-only upload retained'};save(target,records)
   print(ident,sid,'original FHD cut restored; annotation and current pixels pending',flush=True)
  results[ident]={'status':'original-gameplay-restored','annotationPolish':'pending'}
 except Exception as error:
  results[ident]={'status':'needs-source-repair','error':str(error)[-1500:]};print(ident,'source repair needed',str(error)[-500:],flush=True)
 save(B/'gameplay-restoration-status.json',results)
