"""Save directly inspected, distinct actions from an already acquired source.
This is a candidate/cue proposal. It does not render or approve a final timeline.
"""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROJECT=BASE.parent;PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons';SR=PROOF/'source-research'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat();reviewPath=SR/'direct-native-accessibility-actions-review.json'
assert not reviewPath.exists(),'Read saved direct review instead of repeating it.'
state=read(BASE/'native-accessibility-actions-execution.json');assert state['exitCode']==0 and state['cpuJobs']==0
index=read(BASE/'narration-expanded15-index.json')
for m in index['measurements']:assert sha(ROOT/m['path'])==m['sha256'],m['scene']
review=dict(schemaVersion=1,reviewedAt=now,status='direct-native-actions-and-duplicates-reviewed-planning-only',sourceVideoId='JdNZo7E_hXU',sourceSha256=state['sourceSha256'],sheetsRead=state['sheets'],nativeSamplesRead=len(state['frames']),sourceAudioUsed=False,newGitImages=0,allCurrent15PcmPreserved=True,
 observations=[
  dict(region='62–65.38s',finding='The page avatar strikes purple foes beside a long horizontal pond and a lower pool with wooden posts, then moves toward another foe. Native3922 still shows the hit/knockback; the later standing tail and orange settings are excluded.',proposedNativeInterval=[3720,3923],claimLimit='No default difficulty, button mapping or universal combat rule is inferred.'),
  dict(region='65.86–69.52s',finding='The settings pixels show Invincibility OFF first, ON at67s; One Hit Kill OFF at68s and ON at69s. Both are ON before the subsequent desk fight.',decision='Menus are excluded from actual-action quota. Preserve context for the desk action.'),
  dict(region='69.7–72.6667s',finding='The avatar moves and strikes near stepping stones, frogs, yellow blocks and thread spools. Native4359 is still the fight;4360 cuts to a different desk path.',proposedNativeInterval=[4182,4360],requiredContextLabel='접근기능 시연 · 무적/한방처치 ON',claimLimit='This is the official assist-options demonstration, not evidence of default difficulty or hidden-portal rules.'),
 ],duplicateComparisons=[
  dict(existingAction='action-47/48',images=['research-local/native-review-v1/JdNZo7E_hXU/action-sheet-01.jpg','research-local/native-review-v1/JdNZo7E_hXU/action-sheet-02.jpg'],finding='The early fight has a central elongated pond and stumps beside a right stone wall. The new fight has a long upper horizontal pond, lower water with wooden posts and a green opening on the right; it is a different route/action sequence.'),
  dict(existingAction='action-54',images=['research-local/native-review-v1/JdNZo7E_hXU/action-sheet-05.jpg'],finding='The existing upper tan path/tree/stump scene is distinct from the new post-filled lower pond scene.'),
  dict(existingAction='action-59/71',images=['research-local/native-review-rocket-v1/h27ZF-hKKYM/action-sheet-01.jpg','research-local/native-review-rocket-v1/h27ZF-hKKYM/action-sheet-02.jpg','research-local/native-review-rocket-v1/h27ZF-hKKYM/action-sheet-13.jpg'],finding='The earlier purple raised platform route and the green Machines of M desk with stars differ from the new yellow-block/spool/stepping-stone fight. No repeated cross-trailer shot is counted.'),
 ],rightsEvidence=rel(PROJECT/'sources/game-candidates.json'),exactFinalCutBoundaryApproval=False,finalCaptionFramingApproved=False,bodyRatioApproved=False,humanContinuousSourcePlayback='pending')
save(reviewPath,review)
def clip(i,start,end,action,focus,scene,paragraph,context=None):
 d=dict(id=f'action-{i}',sourceVideoId='JdNZo7E_hXU',sourceUrl='https://www.youtube.com/watch?v=JdNZo7E_hXU',sourceSha256=state['sourceSha256'],nativeFrameRate='60/1',nativeFps=60,startFrame=start,endFrameExclusive=end,inSeconds=start/60,outSeconds=end/60,seconds=(end-start)/60,visibleAction=action,planningClaim='Describe the observed setting, verb and target; distinguish shown action from an undecided game rule.',viewerFocus=focus,diagramConnection='Observed action → setting/target → unverified condition',insertionPoint=f'{scene} paragraph{paragraph}',caution='Normal-speed native gameplay only; no source audio, replay, idle/menu quota or default-rule inference.',status='unique-native-reviewed-planning-candidate',finalCaptionFramingApproved=False,directReview=rel(reviewPath))
 if context:d['requiredContextLabel']=context
 return d
new=[clip(99,3720,3923,'Move and strike enemies on the bright page beside ponds and wooden posts','Avatar, enemy and printed route','15',1),clip(100,4182,4360,'Move and strike beside virtual-desk stepping stones and spools','Desk surface, target and enabled assist context','10',4,review['observations'][2]['requiredContextLabel'])]
bank=copy.deepcopy(read(SR/'source-action-bank-v4.json'))
bank.update(createdAt=now,status='93-native-planning-candidates-including-two-context-reviewed-actions',previousBank=rel(SR/'source-action-bank-v4.json'),bodyRatioApproved=False,finalCutAndCaptionApproval=False,measuredNarration=True,nextAction='Compile current15 sentence/cut timing and mixed white diagrams. Select exact final native cuts and fixed-caption framing; do not repeat closed synthesis or source workers.')
excluded={'action-08','action-55','action-14','action-23','action-17','action-12','action-13'}
bank['excludedMicroCuts']=read(BASE/'native-cue-proposal-v2.json')['excludedMicroCuts']
bank['clips']=[c for c in bank['clips'] if c['id'] not in excluded]+new
for c in bank['clips']:
 if c['id']=='action-35':c['endFrameExclusive']=827
 if c['id']=='action-36':c['startFrame']=827;c['endFrameExclusive']=961
 c.update(inSeconds=c['startFrame']/c['nativeFps'],outSeconds=c['endFrameExclusive']/c['nativeFps'],seconds=(c['endFrameExclusive']-c['startFrame'])/c['nativeFps'])
bank['directReview']+=[rel(BASE/'native-cue-boundary-direct-review.json'),rel(reviewPath)];bank['uniqueSourceSeconds']=sum(c['seconds'] for c in bank['clips'])
bank['bySourceSeconds']={sid:sum(c['seconds'] for c in bank['clips'] if c['sourceVideoId']==sid) for sid in {c['sourceVideoId'] for c in bank['clips']}}
for sid in {c['sourceVideoId'] for c in bank['clips']}:
 ordered=sorted([c for c in bank['clips'] if c['sourceVideoId']==sid],key=lambda c:c['startFrame'])
 for a,b in zip(ordered,ordered[1:]):assert a['endFrameExclusive']<=b['startFrame'],(sid,a['id'],b['id'])
save(SR/'source-action-bank-v5.json',bank)
proposal=copy.deepcopy(read(BASE/'native-cue-proposal-v2.json'))
proposal.update(schemaVersion=3,createdAt=now,supersedes=rel(BASE/'native-cue-proposal-v2.json'),status='current15-native-context-candidate-proposal-awaiting-final-timeline',sourceActionBank=rel(SR/'source-action-bank-v5.json'),additionalDirectReview=rel(reviewPath))
for c,scene,paragraph in [(new[0],'15',1),(new[1],'10',4)]:
 g=next(g for g in proposal['groups'] if g['sceneId']==scene and g['paragraph']==paragraph)
 c=copy.deepcopy(c);c.update(sceneId=scene,paragraph=paragraph);g['sourceCuts'].append(c)
for g in proposal['groups']:
 g['sourceSeconds']=sum(c['seconds'] for c in g['sourceCuts']);voice=g['voiceSeconds']
 g['minimumActionObservationExtraSeconds']=max(0,g['sourceSeconds']-voice)
 g['unresolvedVoiceCoverageSeconds']=0 if g['whiteExplanationTail'] else max(0,voice-g['sourceSeconds'])
 g['proposedExplanationSeconds']=max(0,voice-g['sourceSeconds']) if g['whiteExplanationTail'] else 0
cuts=[c for g in proposal['groups'] for c in g['sourceCuts']]
for sid in {c['sourceVideoId'] for c in cuts}:
 ordered=sorted([c for c in cuts if c['sourceVideoId']==sid],key=lambda c:c['startFrame'])
 for a,b in zip(ordered,ordered[1:]):assert a['endFrameExclusive']<=b['startFrame'],(sid,a['id'],b['id'])
proposal['sourceUniqueSeconds']=sum(c['seconds'] for c in cuts)
proposal['proposedExplanationSeconds']-=new[1]['seconds']
proposal['minimumRelatedAdditionalActualSeconds']=max(0,1.5*proposal['proposedExplanationSeconds']-proposal['sourceUniqueSeconds'])
proposal['planningActualSurplusSeconds']=max(0,proposal['sourceUniqueSeconds']-1.5*proposal['proposedExplanationSeconds'])
proposal['pendingCoverageNotes']=['02p4 is short by0.333s and04p1 by0.0467s at proposed per-paragraph boundaries. Align preserved continuous PCM using adjacent relevant shots and actual word times; do not insert flashes, slow down or fill with idle.','Short proposed white tails are not pixel-approved. Use meaningful comparison timing and adjust related actual actions while preserving original explanation PCM.','All source cuts remain candidates; final frame/caption/ratio approvals are false.']
save(BASE/'native-cue-proposal-v3.json',proposal)
state.update(status='closed-direct-native-and-duplicate-context-reviewed',directPixelReview=True,uniqueSecondsApproved=True,approvalScope='two native planning candidates only; final cuts/captions/body ratio remain false',directReview=rel(reviewPath),updatedAt=now)
save(BASE/'native-accessibility-actions-execution.json',state)
for p in [PROJECT/'sources/game-candidates.json',PROJECT/'sources/action-map.json']:
 d=read(p);d.update(updatedAt=now,status='current15-native-cue-context-planning',sourceActionBank=rel(SR/'source-action-bank-v5.json'),nativeCueProposal=rel(BASE/'native-cue-proposal-v3.json'),nativeAccessibilityDirectReview=rel(reviewPath),bodyRatioApproved=False,finalCutAndCaptionApproval=False)
 if p.name=='game-candidates.json':
  d.update(selectedPlanningIntervals=len(bank['clips']),selectedPlanningSeconds=bank['uniqueSourceSeconds'],planningIntervals=len(bank['clips']),planningUniqueSeconds=bank['uniqueSourceSeconds'],projectAssignedIntervals=len(cuts),projectAssignedSeconds=proposal['sourceUniqueSeconds'],actionBank=rel(SR/'source-action-bank-v5.json'),stage='current15-native-context-cues-pending',nextAction=bank['nextAction'])
  d['additionalSourceReviews'].append(dict(sourceId='JdNZo7E_hXU',selectedActionIds=['action-99','action-100'],selected='Two normal-speed unique actions6.35seconds with assist-option context; final frame/caption timing pending.',directReview=rel(reviewPath),rights='Already read official Devolver posting/monetization permission; no new agreement; source audio excluded; final public rights pending.',recentUse='Same source already reviewed for this project; these two disjoint routes/actions directly compared against prior shots.',rejected='Menu transition, standing tail, later unrelated desk cut; no default difficulty claim.'))
 save(p,d)
p=PROJECT/'project.json';d=read(p);d['status']='current15-native-context-and-mixed-cue-planning';d['production'].update(currentVoiceApproved=True,current15TechnicalAsrApproved=True,nativeCueProposal=rel(BASE/'native-cue-proposal-v3.json'),finalTimingApproved=False);save(p,d)
qpath=PROOF.parent/'queue.json';q=read(qpath);task=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
task.update(stage='current15-native-context-reviewed-final-cue-timing-pending',updatedAt=now,nextAction=bank['nextAction'])
task['nativeAccessibilityActionReview'].update(status=state['status'],directPixelReview=True,uniqueSecondsApproved=True,directReview=rel(reviewPath),newCandidateSeconds=sum(c['seconds'] for c in new),bodyRatioApproved=False)
task['execution'].update(status='closed-current15-and-context-native-review',phase='final-native-cue-timing-planning',alive=False,cpuProductionJobs=0,primaryCpuProductionJobs=0,gpuSynthesisJobs=0,renderJobs=0,uploads=0,activeTasks=[],observedAt=now,nextAction=task['nextAction'])
task['nativeCueProposal']=rel(BASE/'native-cue-proposal-v3.json');q.update(updatedAt=now,lastProgressAt=now);save(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
 d=read(p)
 for k in ['stage','updatedAt','nextAction','execution','nativeAccessibilityActionReview','nativeCueProposal']:d[k]=task[k]
 d.update(current15TechnicalNarrationApproved=True,bodyRatioApproved=False,rendered=False,privateUploadSaved=False);save(p,d)
p=PROJECT/'planning/outline.md'
with p.open('a',encoding='utf-8') as f:f.write('\n\n## '+now+' native cue/context correction\n\nPreserve all15 current PCM and the original six explanations. The corrected proposal rejects seven subsecond flashes, fixes WFI music/gap native edits and separates Mine combat from the Pepper-device sentence. Two distinct official accessibility-source actions add6.35seconds: bright-page combat at62–65.3833s and desk combat at69.7–72.6667s after Invincibility/One Hit Kill ON. Carry that context into10p4; do not describe default difficulty. These are planning candidates, with final word/cut framing, meaningful white tails, fixed-caption pixels and exact60:40 still pending. Source audio and new Git images remain0.\n')
print(json.dumps(dict(bankCandidates=len(bank['clips']),bankSeconds=bank['uniqueSourceSeconds'],assignedCandidates=len(cuts),assignedActualSeconds=proposal['sourceUniqueSeconds'],proposedWhiteSeconds=proposal['proposedExplanationSeconds'],currentVoiceSeconds=sum(m['seconds'] for m in index['measurements']),bodyRatioApproved=False,newGitImages=0)))
