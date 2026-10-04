"""Normalize inherited rollup labels; preserve measured audio and pending gates."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;PROJECT=BASE.parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat();p=BASE/'narration-expanded15-index.json';d=read(p)
assert len(d['measurements'])==15
for m in d['measurements']:assert sha(ROOT/m['path'])==m['sha256']
total=sum(m['seconds'] for m in d['measurements']);assert abs(total-475.26016666666663)<1e-8
if 'historicalInherited14Rollup' not in d:d['historicalInherited14Rollup']={k:d[k] for k in ['status','paragraphs','speechSeconds','technicalScope']}
d.update(speechSeconds=total,totalSeconds=total,paragraphs=60,paragraphCount=60,status='current15-scene-technical-ASR-reviewed-final-timing-pending',technicalScope='Current15 scenes/60 independent paired paragraphs: preserved14 full/context technical reviews plus new15 whole and3 contexts. Human listening/pronunciation and final mixed-audio review remain pending.',reviewEvidence=[rel(BASE/'narration-current-full-review.json'),rel(BASE/'additive-narration-direct-review.json'),rel(BASE/'native-cue-narration-direct-review.json')],updatedAt=now)
save(p,d)
planPath=ROOT/'motion-canvas/src/projects/avoid-game-comparisons/production-plan.json';plan=read(planPath)
plan.update(status='15-independent-scenes-mixed-cue-code-final-frames-pixels-pending',currentFinalTimingApproved=False,bodyRatioApproved=False,nativeCueProposal=rel(BASE/'native-cue-proposal-v3.json'))
for s in plan['scenes']:
 if s['id'] in ['06','10','12','13','14','15']:
  s.update(role='mixed-actual-explanation',segments=[],actualFrames=0,diagramFrames=0,diagramPixelsReviewed=False)
  if s['id']=='15':s.update(paragraphs=4,paragraphEnds=[])
  if s['id']=='14':s.update(diagramParagraphs=[2,3],actualParagraphs=[1],note='The current native chest-card prefix covers9.55955s; the remaining fact/condition/listener-check narration is a white comparison, not held gameplay.')
save(planPath,plan)
proposal=read(BASE/'native-cue-proposal-v3.json')
p=BASE/'script-source-review.json';review=read(p)
review.update(currentNarrationIndex=rel(BASE/'narration-expanded15-index.json'),nativeCueProposal=rel(BASE/'native-cue-proposal-v3.json'),nativeSourceContextReview=rel(PROOF/'source-research/direct-native-accessibility-actions-review.json'),updatedAt=now,finalCutAndCaptionApproval=False,bodyRatioApproved=False,sourceCueChangeReview='Directly read corrected WFI edges, excluded flashes, Mine/Pepper separation and two distinct option-context actions. All15 KO/EN scripts and PCM are unchanged. Proposed diagrams clarify caveats; final cue pixels and timing remain pending.')
for x in review['inputs']:x['sha256']=sha(ROOT/x['path'])
for path in [BASE/'native-cue-proposal-v3.json',PROOF/'source-research/direct-native-accessibility-actions-review.json']:
 if not any(x['path']==rel(path) for x in review['inputs']):review['inputs'].append(dict(path=rel(path),sha256=sha(path)))
save(p,review)
for p in [PROJECT/'planning/chapter-plan.json',PROJECT/'sources/action-map.json']:
 d=read(p);d.update(nativeCueProposal=rel(BASE/'native-cue-proposal-v3.json'),updatedAt=now)
 for c in d['chapters']:
  groups=[g for g in proposal['groups'] if g['sceneId']==c['id']]
  if groups:c['currentProposedSourceActionIds']=[a['id'] for g in groups for a in g['sourceCuts']]
  if c['id'] in ['06','10','12','13','14','15']:c.update(visualRole='mixed-actual-explanation',finalTimingApproved=False,diagramPixelReview=False)
 save(p,d)
# action-map bytes changed above; record their read, measured proposal and hash.
review=read(BASE/'script-source-review.json')
for x in review['inputs']:x['sha256']=sha(ROOT/x['path'])
save(BASE/'script-source-review.json',review)
qpath=PROOF.parent/'queue.json';q=read(qpath);task=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
task['nativeCueNarration'].update(speechSeconds=total,scriptScenes=15,paragraphs=60,current15Index=rel(BASE/'narration-expanded15-index.json'))
task.update(stage='current15-native-context-and-mixed-code-reviewed-final-cues-pending',updatedAt=now,nextAction='Compile current15 PCM with exact native action and word timing, meaningful white comparisons and fixed960,970 captions; correct pending short group coverage. Directly inspect new13/14/cue diagrams before approving final frames60:40. Final mix ASR, render/QA/collection/private save remain pending.')
task['nativeCuePlanning']=dict(proposal=rel(BASE/'native-cue-proposal-v3.json'),bankCandidates=93,projectCutCandidates=105,candidateActualSeconds=proposal['sourceUniqueSeconds'],proposedWhiteSeconds=proposal['proposedExplanationSeconds'],currentSpeechSeconds=total,bodyRatioApproved=False,allCaptionPixelsReviewed=False,newDiagramPixelsReviewed=False)
task['execution'].update(nextAction=task['nextAction'],cpuProductionJobs=0,primaryCpuProductionJobs=0,gpuSynthesisJobs=0,renderJobs=0,uploads=0,alive=False,activeTasks=[],observedAt=now)
q.update(updatedAt=now,lastProgressAt=now);save(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
 d=read(p)
 for k in ['stage','updatedAt','nextAction','execution','nativeCueNarration','nativeCuePlanning']:d[k]=task[k]
 d.update(current15TechnicalNarrationApproved=True,bodyRatioApproved=False,rendered=False,privateUploadSaved=False);save(p,d)
print(json.dumps(dict(currentScenes=15,paragraphs=60,currentSpeechSeconds=total,old14RollupPreserved=True,finalApproved=False)))
