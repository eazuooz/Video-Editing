"""CPU-only preservation and source-selection checkpoint for the next two owned lectures."""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).parent/'cross-game-review-20261011/interpolation-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
episodes=[]
for slug,new,video,date in [('game-math-interpolation-paths-v2','game-math-interpolation-paths-v3','_SzbJR4R6OI','2026-10-21'),('game-math-rotation-conversions-v2','game-math-rotation-conversions-v3','n-k7zwaSum0','2026-10-23')]:
 p=ROOT/'projects'/slug;m=read(p/'project.json');t=read(ROOT/m['paths']['timeline'])
 files=[p/'project.json',p/'production/qa.json']+[ROOT/m['paths'][key] for key in ['script','scriptEn','timeline','captionsKo','captionsEn','narration']]
 assert t['actualShare']==.4 and t['explanationShare']==.6 and t['ratioErrorFrames']==0
 ids=[s['id'] for s in t['scenes']]
 assert [s['id'] for s in read(ROOT/m['paths']['script'])['scenes']]==ids
 assert [s['id'] for s in read(ROOT/m['paths']['scriptEn'])['scenes']]==ids
 ep=dict(slug=slug,newSlug=new,videoId=video,sceneIds=ids,frames=t['frames'],bodyFrames=t['bodyFrames'],
  actualFrames=t['actualFrames'],explanationFrames=t['explanationFrames'],
  files=[dict(path=f.relative_to(ROOT).as_posix(),sha256=sha(f)) for f in files],
  games=['Forza Horizon 4','Riders Republic','Skate 3'],minimumDistinctGames=4,additionalDistinctGamesNeeded=1,
  sourceFields=list(t['scenes'][0]),newSchedule=dict(date=date,time='09:00',timezone='Asia/Seoul',actualReservation=False))
 episodes.append(ep)
 for f in files:
  if f.suffix in ['.json','.srt']:
   dest=R/'baseline-snapshots'/slug/f.relative_to(p) if f.is_relative_to(p) else R/'baseline-snapshots'/slug/f.name
   dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes())
write(R/'baseline.json',dict(recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),episodes=episodes,
 preserveAllExistingScriptsOrderExplanationFramesClipsAndPcm=True,baselineProjectsChanged=False,
 actualShare=.4,explanationShare=.6,backgroundMusic=False,sourceAudio=False,palette='preserve existing white Manim',
 humanListeningComplete=False,rightsHumanReviewComplete=False,newTtsStarted=False))
proofs=[read(R/('native-candidate-'+i+'.json')) for i in ['A','B','C']]
assert all(p['completed'] and p['rate']==1 for p in proofs)
write(R/'candidate-comparison.json',dict(recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 game='Trailmakers',sourceId='JvTCVUEc1ZE',
 sourceFile='shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/sources/trailmakers-JvTCVUEc1ZE.mp4',
 sourceSha256='3b88e252e1f4d0afbc08d2a92c218c7ff34d5bd1c2356466c1e1e04e223c083d',
 nativeProofs=proofs,
 candidates=[
  dict(id='A',interval=[592,622],decision='rejected',before='Construction view with component-selection UI',
   action='Building view followed by a flight cut',after='Gray aircraft beside a cliff',
   reason='An editing cut separates construction from flight; this interval does not show one continuous orientation transition.'),
  dict(id='B',interval=[632,657],decision='rejected',before='Gray aircraft near the ground',
   action='Camera views and a change to a yellow/blue craft',after='Close low angle of the yellow/blue craft',
   reason='Craft changes and close camera framing make before/after wing-axis comparison harder.'),
  dict(id='C',interval=[665,700],decision='selected-candidate-for-bounded-additions',
   before='Yellow/blue aircraft with visible body and paired wings',
   action='Continuous flight; body/wing screen directions change; camera movement must be separated',
   after='Same yellow/blue aircraft remains visible in flight',
   reason='The same rigid craft remains recognizable, with longer opportunities to follow body and wings than the rejected cuts.',
   annotationUnreliableLocalSeconds=[[2.82,3.2],[9.5,10],[18.7,28],[30.8,31.4],[34,35]],
   cameraAndOcclusion='Hide inferred body/wing lines at abrupt camera motion or poor endpoint visibility; state that screen inclination is not a measured game-world angle.',
   overlay='Retain red body/nose and blue wing semantic colors. Narrated reveals need new alignment and actual moving-pixel review.',
   fixedCaptionClearance='Keep overlays above the fixed bottom caption box; verify every rendered cue.',
   history='Source and interval already used in quaternion v3. Reuse is explicit: transfer to interpolation/representation questions; new title relative to these two three-game episodes. Do not count familiarity alone as teaching approval.')],
 claims=dict(interpolation='Follow visible orientation changes, then construct intermediate poses from explicitly chosen fixed endpoint models; no claim about the game using SLERP.',
  conversions='Compare body and wing directions, then verify representation changes with model basis vectors; no game-engine matrix/quaternion readout is available.'),
 modeledValuesNotMeasured=True,rightsHumanReviewComplete=False,narratedAdditionsCreated=False,finalMovingReviewComplete=False))
print(json.dumps(dict(episodes=len(episodes),retainedScenes=sum(len(e['sceneIds']) for e in episodes),cpuOnly=True,newTtsStarted=False)))
