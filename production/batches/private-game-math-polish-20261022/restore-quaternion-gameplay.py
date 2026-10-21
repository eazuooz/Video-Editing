"""Restore the approved real-time cuts and observed editorial tracks in FHD."""
import sys,shutil,types
from polish_common import *
e=Episode(sys.argv[1]);assert e.id in ['M05','M06'];e.authorized()
old=R/'production/batches/game-math-part2-teaching-revision'
tracked=module('polish_original_tracks',old/'create-game-overlay.py')
# The legacy contact-sheet helper imported OpenCV even for pure ASS writing.
# Load its existing vector functions without that unused optional dependency.
renderer=types.ModuleType('polish_cross_vector_writer');renderer.__file__=str(old/'render-quaternion-track-drafts-v3.py')
source=(old/'render-quaternion-track-drafts-v3.py').read_text(encoding='utf8').replace('import cv2,hashlib,json,subprocess,sys','import hashlib,json,subprocess,sys')
exec(compile(source,renderer.__file__,'exec'),renderer.__dict__)
cross=types.ModuleType('polish_cross_tracks');cross.__file__=str(old/'quaternion-final-overlays-v3.py')
cross.__dict__.update(Path=Path,hashlib=hashlib,read=read,ROOT=R,B=old,R=old/'cross-game-review-20261011/quaternion-four-game-v3',renderer=renderer)
source=(old/'quaternion-final-overlays-v3.py').read_text(encoding='utf8');exec(compile(source[source.index('def stem('):],cross.__file__,'exec'),cross.__dict__)
track_ids=set(read(old/'quaternion-annotation-tracks.json')['scenes'])
folder=e.O/'gameplay';folder.mkdir(exist_ok=True);(e.O/'clips').mkdir(exist_ok=True)
target=e.H/'gameplay-restoration.json';records=read(target) if target.exists() else {'scenes':{}}
for s in e.T['scenes']:
 if s['classification']!='actual':continue
 e.authorized();sid=s['id'];cut=s['cut'];parts=[];sources=[];ass=None
 if sid in track_ids:ass=tracked.write_overlay(e.slug,sid)
 elif sid.startswith(('QF','QC')):ass=cross.write_overlay(e.slug,sid)
 for j,seg in enumerate(cut['segments']):
  src=R/seg.get('sourceFile',cut['sourceFile']);v=video(src);assert v['width']>=1920 and v['height']>=1080,(sid,'FHD source required',str(src))
  assert seg['in']+seg['frames']/60<=float(probe(src)['format']['duration'])+.03
  vf='scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60'
  if sid.startswith(('QF','QC')):
   # Original tracked crop coordinates are a 1920x1080 canvas. The recovered
   # Besiege source is native 1440p; first downsample to that original canvas.
   vf='scale=1920:1080:flags=lanczos,'+cross.crop_filter(s,seg)
  elif cut.get('sourceFraming'):vf=cut['sourceFraming']['filter']+',fps=60'
  part=folder/f'{sid}-{j+1}.mp4';sig={'sourceSha256':sha(src),'sourceIn':seg['in'],'frames':seg['frames'],'vf':vf};receipt=part.with_suffix('.json')
  if not(part.exists() and receipt.exists() and read(receipt)==sig):
   e.ff(['-ss',seg['in'],'-i',src,'-vf',vf,'-frames:v',seg['frames'],'-an',*ENC,part],f'gameplay-{sid}-{j+1}.log');save(receipt,sig)
  e.verify(part,seg['frames']);parts.append(part);sources.append({'source':rel(src),**sig})
 raw=folder/f'{sid}-raw.mp4';listing=folder/f'{sid}-concat.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts)+'\n',encoding='utf8')
 e.ff(['-f','concat','-safe','0','-i',listing,'-c','copy','-an','-video_track_timescale','60000',raw],f'gameplay-{sid}-concat.log');e.verify(raw,s['frames'])
 dst=e.O/f'clips/{sid}.mp4'
 if ass:
  local_ass=folder/f'{sid}.ass';shutil.copy2(ass,local_ass);e.ff(['-i',raw,'-vf',f'ass={local_ass.name}','-frames:v',s['frames'],'-an',*ENC,dst],f'gameplay-{sid}-overlay.log',folder)
 else:shutil.copy2(raw,dst)
 e.verify(dst,s['frames']);records['scenes'][sid]={'path':rel(dst),'sha256':sha(dst),'sources':sources,'frames':s['frames'],'speed':1,'originalCutOrderAndDuration':True,'overlay':rel(ass) if ass else None,'overlaySha256':sha(ass) if ass else None,'screenSpaceEditorialGuidesOnly':True,'currentMovingPixelReview':'pending','sourceAudio':'existing narration-only upload preserved'};save(target,records)
 print(e.id,sid,'FHD cut restored; current visual review pending',flush=True)
