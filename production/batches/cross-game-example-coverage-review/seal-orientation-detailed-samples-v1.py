"""Bind all directly inspected current detail samples; normal playback is separate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
out=O/'current34-detailed-explanations-sampled-direct-review-v1.json'
assert not out.exists()
notes={
 '03':'Detailed aircraft canopy, wings, tail and engine intakes remain visible. Twist around forward preserves blue forward while body/up rotate. Stacked attitudes distinguish same direction from full orientation.',
 '04':'Aircraft and colored body axes rotate together; x cross y equals z is retained. Header rule and subtitle are separate.',
 '06':'Local-to-world matrix and aircraft use the retained right-handed convention and matching column colors.',
 '07':'Three retained columns reveal in order and the worked vector (2,1,0) becomes (-1,2,0). Aircraft shape and body axes agree.',
 '09':'Transpose/inverse is stated for pure rotation. Worked world vector (-1,2,0) recovers local (2,1,0).',
 '10':'Direction cosine rows/world and columns/local connect the highlighted first column to the aircraft body axis.',
 '13':'Length/orthogonality and positive determinant tests remain visible; detailed aircraft does not cover labels.',
 '15':'Scale expands the aircraft and axis, reflection has determinant -1, and diag(-1,-1,1) is the distinct 180-degree rotation. Intermediate transition is a reveal, with the final matrix/result checked.',
 '16':'Exaggerated creep is explicitly illustrative. Axis distortion and correction lead to identity; degenerate/intentional scaling cases remain qualified.',
 '21':'Detailed aircraft and two axes collapse under the elementwise midpoint diag(0,0,1); this deliberate mathematical failure is labelled, not a missing subject asset.',
 '22':'Retained worked answers (0,1,0), p-t=(1,2,0), inverse=(2,-1,0), and reconstruction=(4,5,0) remain clear.',
 '12':'Detailed parent aircraft and orange mounted camera/lens preserve child-to-parent B, parent-to-world A, rightmost-first ABv and the AB/BA comparison. Camera is a conceptual mounted object, not an engine measurement.',
 '06a':'The same detailed aircraft links body-attached rulers to world readings and matrix columns. No game-world measurement is claimed.',
 '09a':'Aircraft axes, projected vector and dot products explain transpose recovery under pure rotation, with the original numbers retained.',
 '13a':'Distorted detailed aircraft shows why unit length, right angles and handedness must be tested; it returns to a valid basis.',
 '16a':'Parallel component removal, normalization and fallback qualification preserve their order while aircraft and axes change together.',
 '21a':'Detailed aircraft deliberately collapses in the illustrative midpoint example; zero-length axes and non-rotation warning are visible.'}
rows=[];refs=[]
for name,ids in [('current34-detailed-header-repair-render-execution-v2.json',None),('current34-detailed-explanation-render-execution-v1.json',{'12','06a','09a','13a','16a','21a'})]:
 p=O/name;s=rd(p)
 assert s['actualOuterExitCode']==0 and s['actualExitObserved'] and s['workerDead']
 refs.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),actualSession=s['actualSession'],completion=s['completionChunk']))
 for x in s['scenes']:
  if ids is not None and x['id'] not in ids:continue
  assert x['renderExitCode']==x['wholeDecodeExitCode']==x['extractExitCode']==0
  assert sha(ROOT/x['output'])==x['outputSha256']
  for r in x['samples']+x['boards']:assert sha(ROOT/r['path'])==r['sha256']
  rows.append(dict(scene=x['id'],execution=name,video=x['output'],videoSha256=x['outputSha256'],samples=x['samples'],boards=x['boards'],allSamplesDirectlyRead=True,observation=notes[x['id']],captionReservedAreaClearInSamples=True))
assert len(rows)==17 and sum(len(x['samples']) for x in rows)==605 and sum(len(x['boards']) for x in rows)==109
proof=rd(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
data=dict(recordedAt=datetime.now(timezone.utc).isoformat(),executions=refs,rows=rows,all605SamplesDirectlyRead=True,all109BoardsDirectlyRead=True,readMethod='Direct original-resolution contact-board inspection, with earlier scene12 boards02/03 and full-resolution representative carried forward from actual prior direct reads.',recognizableDetailedSubjectsReviewed=True,narrationOrderedMotionSampled=True,allInterveningFramesReviewed=False,normalPlaybackReviewed=False,final244CaptionPixelsApproved=False,humanContinuousListeningApproved=False,all79ProtectedUnchanged=True,repairCandidateUnchanged=True,newTts=0,newAsr=0,newMix=0,newImageGit=0)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(scenes=17,samples=605,boards=109,normalPending=True,finalPixels=False)))
