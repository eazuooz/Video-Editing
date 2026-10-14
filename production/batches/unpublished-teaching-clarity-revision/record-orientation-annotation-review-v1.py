"""Record the completed direct review and prepare only the held-label repair."""
from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
state=read(R/'annotation-prototype-execution-v1.json')
assert state['actualOuterExitCode']==state['workerExitCode']==0 and state['sessionId']==7723
review=R/'annotation-prototype-direct-review-v1.json'
assert not review.exists(),'Preserve already recorded review'
notes={
 '05':'Torso point follows the visible body at the sampled frames; lower helper text covers the x2 multiplier around frames135/165. Hold layout.',
 '08':'Sampled point follows the torso while gold arrow names screen-up; lower helper text covers the left x2 UI. Hold layout.',
 '11':'Hide ranges suppress ambiguous occluded points and previous-point displacement; visible samples remain on the body.',
 '14':'Sampled point follows the visible torso; wall-occlusion range is hidden. Screen size is not a measured basis length.',
 '17':'Point and red screen displacement are readable in the sampled smooth turn; no matrix interpolation or world-axis recovery is claimed.',
 '20':'Visible samples stay on the body; tiny subject at frames300 onward is hidden. Screen-left and body-left remain distinct.',
 '23':'All25 samples read: early point remains on torso,90–165 hidden and180 onward visible; red displacement describes image motion, not physical velocity.'}
rows=[]
for w in state['windows']:
 assert w['wholeDecodeExitCode']==w['extractionExitCode']==0 and len(w['samples'])==25 and len(w['boards'])==5
 for item in w['samples']+w['boards']:assert sha(ROOT/item['path'])==item['sha256']
 assert sha(ROOT/w['output'])==w['outputSha256']
 rows.append(dict(scene=w['scene'],samplesRead=25,boardsRead=w['boards'],output=w['output'],outputSha256=w['outputSha256'],observation=notes[w['scene']]))
baseline=read(R/'baseline-preservation-v1.json')
assert len(baseline['protectedFiles'])==38 and all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
save(review,dict(reviewedAt=now,execution=str((R/'annotation-prototype-execution-v1.json').relative_to(ROOT)).replace('\\','/'),actualOuterSessionId=7723,actualOuterExitCode=0,all175SamplesAnd35BoardsDirectlyRead=True,allRecordedHashesMatched=True,windows=rows,status='held-helper-text-over-game-score-ui',sampledTorsoTrackingPassed=True,screenGeometryOnly=True,unresolved=['scene05 multiplier UI beneath lower helper labels','scene08 left multiplier UI beneath lower helper labels'],repair='Move both helper labels above the body/action region and reread all changed boards.',allIntermediateFramesDirectlyRead=False,allMovingPixelsApproved=False,narrationTimed=False,finalCueApproved=False,finalVideoApproved=False,baseline38Unchanged=True,researchManipulations=0,newImageGitAdded=0))
source=Path(__file__).with_name('render-orientation-annotation-prototypes-v1.py')
target=source.with_name('render-orientation-annotation-prototypes-v2.py')
assert not target.exists()
code=source.read_text(encoding='utf-8').replace('annotation-prototypes-v1','annotation-prototypes-v2').replace('annotation-prototype-execution-v1.json','annotation-prototype-execution-v2.json').replace('(64,810)','(64,370)').replace('(64,855)','(64,420)')
assert '(64,810)' not in code and '(64,855)' not in code
target.write_text(code,encoding='utf-8')
checkpoint=read(R/'latest-checkpoint.json')
checkpoint.update(observedAt=now,stage='annotation-v1-ui-hold-v2-repair-prepared-and-existing-single-tts-wait',actualGameplayComparisonApproved=True,dependentNewScriptPrepared=True,dependentNarrationApproved=True,sourcePlanning='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/source-selection-preflight-v2.json',annotationPrototypeDirectReview='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/annotation-prototype-direct-review-v1.json',conservativeRecut='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/conservative-source-recut-proposal-v2.json',newFinalMediaApproved=False,next='Run one CPU2 annotation-label repair if own GPU TTS is still waiting; keep existing TTS54946 and then verify actual own research restoration before ASR.')
save(R/'latest-checkpoint.json',checkpoint)
qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qpath)
q['execution']['stage']=checkpoint['stage']
q['execution']['completedJobs'].append(dict(sessionId=7723,pid=82792,createTime=1791677843.1560252,state='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/annotation-prototype-execution-v1.json',actualOuterExitCode=0,exitObservedChunk='63006d',all175SamplesAnd35BoardsRead=True,approved=False,reason='Lower helper text covers multiplier UI in05/08.'))
q['updatedAt']=now
save(qpath,q)
print(json.dumps({'review':'v1-held-ui','samples':175,'boards':35,'v2Prepared':True,'baseline38':True}))
