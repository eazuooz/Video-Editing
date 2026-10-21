"""Improve existing screen-space guides without changing any source cut/audio."""
import sys,types,re
from polish_common import *

e=Episode(sys.argv[1]);e.authorized();assert e.id in ['M05','M06']
old=R/'production/batches/game-math-part2-teaching-revision'
registry=read(old/'quaternion-annotation-tracks.json')
for spec in registry['scenes'].values():spec['labelOutline']=1.8
if e.id=='M05':
 registry['scenes']['GA06']['landmarks']=rel(B/'ga06-observed-repair.json')
local_registry=e.H/'annotation-registry.json';save(local_registry,registry)
source=(old/'create-game-overlay.py').read_text(encoding='utf8')
source=source.replace("read(B/'quaternion-annotation-tracks.json')",f'read(Path({str(local_registry)!r}))')
source=source.replace("out=ROOT/'shared/output'/slug/'overlays'",f'out=Path({str(e.O / "polished-overlay-authoring")!r})')
source=source.replace("  x,y=np.array(p)*[sx,sy]","  size=max(size,17)\n  x,y=np.array(p)*[sx,sy]")
source=source.replace("spec.get('mathNotePosition',[407,124])","spec.get('mathNotePosition',[450,124])")
box=" polygon(note_start,slot['seconds'],[[note_x,note_y],[note_x+378,note_y],[note_x+378,note_y+65],[note_x,note_y+65]],'#171717',0)"
assert box in source
source=source.replace(box,'')
source=source.replace('round(15*sy)','round(20*sy)').replace('>880','>748')
source=source.replace(" words='\\n'.join(wrapped)"," words='\\n'.join(wrapped)\n note_h=66 if len(wrapped)==1 else 90\n polygon(note_start,slot['seconds'],[[note_x,note_y],[note_x+330,note_y],[note_x+330,note_y+note_h],[note_x,note_y+note_h]],'#171717',0)")
source=source.replace("size=13)\n text(note_start", "size=18)\n text(note_start")
source=source.replace('[note_x+9,note_y+27]','[note_x+9,note_y+36]').replace("words,'#ffe082',size=15)","words,'#ffe082',size=20)")
m=types.ModuleType('private_polish_overlay');m.__file__=str(old/'create-game-overlay.py');exec(compile(source,m.__file__,'exec'),m.__dict__)
records=read(e.H/'gameplay-restoration.json');changes={}
selected=set(sys.argv[2:]) - {'--apply'}
for s in e.T['scenes']:
 sid=s['id']
 if s['classification']!='actual' or sid not in registry['scenes'] or (selected and sid not in selected):continue
 # Keep original authoring output untouched; direct the existing writer locally.
 generated=m.write_overlay(e.slug,sid)
 ass=e.O/f'gameplay/{sid}-polished.ass';ass.write_bytes(generated.read_bytes())
 changes[sid]={'ass':rel(ass),'sha256':sha(ass),'basis':'observed projected screen landmarks; not engine/world measurement','captionClearance':'fixed caption band below y880; current pixels require review','fontMinimumPx':41,'mathBodyPx':48,'mathHeadingPx':43}
 if '--apply' in sys.argv:
  e.authorized();raw=e.O/f'gameplay/{sid}-raw.mp4';dst=e.O/f'clips/{sid}.mp4';e.verify(raw,s['frames'])
  if records['scenes'][sid].get('polishedOverlaySha256')!=sha(ass):
   e.ff(['-i',raw,'-vf',f'ass={ass.name}','-frames:v',s['frames'],'-an',*ENC,dst],f'polished-overlay-{sid}.log',ass.parent)
   e.verify(dst,s['frames']);records['scenes'][sid].update(sha256=sha(dst),polishedOverlay=rel(ass),polishedOverlaySha256=sha(ass),currentMovingPixelReview='pending');save(e.H/'gameplay-restoration.json',records)
  print(e.id,sid,'overlay typography/target repair rendered; review pending',flush=True)
save(e.H/'annotation-polish.json',{'script':rel(Path(__file__)),'scriptSha256':sha(Path(__file__)),'scenes':changes,'sourceAndTimingUnchanged':True,'review':'pending'})
