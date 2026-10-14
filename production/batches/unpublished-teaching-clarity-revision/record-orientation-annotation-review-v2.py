"""Seal only the directly read, bounded silent annotation sample review."""
from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,o:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
state=read(R/'annotation-prototype-execution-v2.json')
target=R/'annotation-prototype-direct-review-v2.json'
assert not target.exists()
assert state['actualOuterExitCode']==state['workerExitCode']==0 and state['sessionId']==68087
notes={
 '05':'All25 samples: helper labels moved to370/420, clearing multiplier UI seen covered in v1; cyan torso point and red image displacement remain readable.',
 '08':'All25 samples: left multiplier UI is clear after helper relocation; screen-up is labelled as an image convention, not a recovered world axis.',
 '11':'All25 samples: ambiguous occlusions suppress current/previous points; visible sampled positions stay on the torso.',
 '14':'All25 samples: wall-occlusion interval is hidden; visible point follows the sampled body without interpreting screen size as world-basis length.',
 '17':'All25 samples: sampled point follows the visible turn; red line describes image displacement only.',
 '20':'All25 samples: visible points remain on the torso through285; tiny subject at300 onward is hidden rather than inventing an anchor.',
 '23':'All25 samples:90–165 hidden,180 onward visible; sampled torso point/red displacement and score UI remain clear.'}
rows=[]
for w in state['windows']:
 assert w['wholeDecodeExitCode']==w['extractionExitCode']==0 and len(w['samples'])==25 and len(w['boards'])==5
 assert sha(ROOT/w['output'])==w['outputSha256']
 for x in w['samples']+w['boards']:assert sha(ROOT/x['path'])==x['sha256']
 rows.append(dict(scene=w['scene'],samplesRead=25,boardsRead=w['boards'],output=w['output'],outputSha256=w['outputSha256'],observation=notes[w['scene']]))
b=read(R/'baseline-preservation-v1.json')
assert len(b['protectedFiles'])==38 and all(sha(ROOT/x['path'])==x['sha256'] for x in b['protectedFiles'])
save(target,dict(reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),execution='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/annotation-prototype-execution-v2.json',actualOuterSessionId=68087,actualOuterExitCode=0,all175SamplesAnd35BoardsDirectlyRead=True,allRecordedHashesMatched=True,windows=rows,status='sampled-annotation-layout-approved-awaiting-normal-playback-and-narration-timing',sampledTorsoTrackingPassed=True,sampledUiClearancePassed=True,screenGeometryOnly=True,unresolved=[],allIntermediateFramesDirectlyRead=False,normalPlaybackExecuted=False,allMovingPixelsApproved=False,narrationTimed=False,finalCueApproved=False,finalVideoApproved=False,baseline38Unchanged=True,researchManipulations=0,newImageGitAdded=0))
s=read(R/'structural-prototype-execution-v1.json')
assert s['workerExitCode']==0
s.update(sessionId=89216,actualOuterExitCode=0,actualOuterExitObservedChunk='c65797')
save(R/'structural-prototype-execution-v1.json',s)
print(json.dumps(dict(annotationSamples=175,boards=35,boundedReview=True,structuralActualExit=0,structuralSession=89216)))
