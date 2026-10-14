"""Prepare a scoped extraction for the two v40 numeric repairs in encoded v41."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
source=ROOT/'production/research/game-lighting-history/extract-episode04-inspection-encoded-v38.py'
target=ROOT/'production/research/game-lighting-history/extract-episode04-inspection-numeric-v42.py'
assert not target.exists()
code=source.read_text('utf-8')
code=code.replace('episode04-inspection-encoded-v38','episode04-inspection-numeric-v42')
code=code.replace('inspection-chapter-review-build-v38','inspection-chapter-review-build-v41')
code=code.replace('inspection-chapter-review-execution-v38','inspection-chapter-review-execution-v41')
code=code.replace('episode04-inspection-chapter-v38','episode04-inspection-chapter-v41')
code=code.replace('episode04DlssEncodedExtractionV34','episode04InspectionNumericExtractionV42')
code=code.replace('CPU-inspection-encoded-extraction-v38','CPU-inspection-numeric-extraction-v42')
code=code.replace('.extract-inspection-v38.tmp','.extract-inspection-numeric-v42.tmp')
start=code.index('def points_for(captioned):')
end=code.index('\ntry:',start)
code=code[:start]+'''def points_for(captioned):
 points={}
 changed=[c for c in plan['cuts'] if c['id'] in ['original-22r-5','original-22rb-6']]
 assert len(changed)==2
 def inside(frame):return any(c['fromFrame']-1<=frame<=c['toFrame'] for c in changed)
 def add(frame,label):
  if 0<=frame<N and inside(frame):points.setdefault(frame,[]).append(label)
 for c in changed:
  for frame,name in [(c['fromFrame']-1,'previous cut last'),(c['fromFrame'],'first'),((c['fromFrame']+c['toFrame']-1)//2,'middle'),(c['toFrame']-1,'last'),(c['toFrame'],'next cut first')]:add(frame,c['id']+' '+name)
  for fraction in [.1,.25,.5,.75,.9]:add(c['fromFrame']+round((c['frames']-1)*fraction),c['id']+' progress '+str(fraction))
 if captioned:
  for c in metrics:
   first,last=c['firstFrame'],c['exclusiveEndFrame']
   for frame,name in [(first,'first'),((first+last-1)//2,'middle'),(last-1,'last'),(first-1,'before'),(last,'after')]:add(frame,f"cue{c['id']} {name}")
 return points
'''+code[end:]
code=code.replace('"""One CPU2 extraction of all69 current inspection chapter cue/cut/annotation samples."""','"""Only two changed numeric cuts, their captions and adjacent boundary pixels; unchanged v38 samples preserved."""')
target.write_text(code,'utf-8')
print(json.dumps({'prepared':target.relative_to(ROOT).as_posix(),'scope':'two changed cuts only','actualExtraction':False}))
