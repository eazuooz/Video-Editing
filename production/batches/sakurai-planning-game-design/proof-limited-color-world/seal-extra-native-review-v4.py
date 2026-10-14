"""Seal the actually read 27 boards; retain unresolved cuts as held."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[4]
P=Path(__file__).resolve().parent
BASE=ROOT/'projects/limited-color-world/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4194304),b''):h.update(b)
    return h.hexdigest()
def save(p,d):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
sp=P/'extra-native-action-execution-v4.json';d=read(sp)
assert d['actualExitObserved'] and d['actualOuterExitCode']==0 and d['actualOuterExitToolObservation']=='4f0029'
out=P/'extra-native-action-direct-review-v4.json';assert not out.exists()
observations={
 'room-door-approach':('Player walks toward upper-left door in an outlined furnished room. Last included f6119 already has a right-side wipe; the proposed 102s end is not clean.','trim-end',6090),
 'portrait-corridor-travel':('Player walks left through a portrait corridor to the central carpet. Portrait interaction bubble stays above the fixed test caption. The last half-second is a short stand; propose end110.5s. This is a corridor rather than house painting.','trim-end',6630),
 'town-outline-route':('Monochrome town navigation down the stone route, with outlined houses and sign prompt. The coloured Luncheon heading is not evidence of an action rule. Up120 preserves player/path above the test box.','bounded-samples-clear',10620),
 'flower-before-paint':('Player approaches the first flower/path/ledge before painting. Outlines and destination are clear above the test box. Normal navigation establishes the before state; no permanent unlocking claim.','bounded-samples-clear',32100),
 'four-mushroom-ledged-arrival':('Already at the right ledge over four mushrooms. Most of110–111 is a short stand; only111–111.5 shows an exit movement. Do not claim another win or unlock.','trim-start',6690),
 'tree-outline-paint':('Tree is painted green, erased to outlines and painted coral. Leaf/branch/trunk boundaries remain. New tree example must be named in its on-screen observation and paired with a generic outline claim, never a house-specific line.','bounded-samples-clear',35880),
 'portrait-corridor-continuation':('Separate leftward corridor traversal across carpets, with portrait bubble above. Omitted dialogue separates it from108–110.5. Use only with an explicit corridor label and a navigation/shape observation; no continuous action claim across the omitted gap.','bounded-samples-clear',7500),
 'town-path-first-part':('Cyan-filled town retains dark stone-path and house edges while player walks down/right. Compare shape cues with the earlier monochrome view without claiming uninterrupted painting between the two cuts.','bounded-samples-clear',12600),
 'town-path-second-part':('After a source transition, player follows a path toward another house/NPC. Pickle prompt is above the test caption.211s transition is excluded; separate shot, not one uninterrupted route.','bounded-samples-clear',12900),
 'fence-route-part1':('Editorial name is inaccurate: this is a multicoloured house and Lemon NPC, not a fence.357–358 mostly stationary, then a short downward move; f21569 is already heavily wiped. Reject the full2.5s candidate.','held-rejected',None),
 'fence-route-part2':('Different house/fence area, player walks left along the outlined stone path. Fence and tree borders remain clear with up120. Name the changed object and do not imply continuity with the rejected Lemon shot.','bounded-samples-clear',21900),
 'mushroom-other-hues-comparison':('Orange, yellow and dark-rose mushrooms rise; player hops across and caps compress after contact. Separate normal-speed example supports height/motion despite different hues. Gift39–43 is excluded; no correct-colour, victory or collection assertion.','bounded-samples-clear',2280)
}
verified=[]
for c in d['cuts']:
    assert c['key'] in observations
    for s in c['samples']:
        assert s['pts']==s['nativeFrame']*256
        assert sha(ROOT/s['path'])==s['sha256'] and sha(ROOT/s['captionTestPath'])==s['captionTestSha256']
    for b in c['boards']:assert sha(ROOT/b['path'])==b['sha256']
    note,decision,newend=observations[c['key']]
    verified.append(dict(key=c['key'],source=c['source'],proposedStartFrame=c['startFrame'],proposedEndFrameExclusive=c['endFrameExclusive'],
      directlyReadSampleCount=len(c['samples']),directlyReadBoards=c['boards'],observed=note,decision=decision,
      proposedRevisedStartFrame=6660 if c['key']=='four-mushroom-ledged-arrival' else c['startFrame'],
      proposedRevisedEndFrameExclusive=newend,exactRevisedBoundaryApproved=False if decision.startswith('trim') else decision=='bounded-samples-clear',
      fixedPlaceholderSamplesClear=decision=='bounded-samples-clear',adopted=False,finalCueUiApproved=False))
assert sum(len(c['boards']) for c in d['cuts'])==27 and sum(len(c['samples']) for c in d['cuts'])==134
assert all(sha(ROOT/p)==h for p,h in d['protectedInputs'].items())
assert all(sha(ROOT/p)==h for p,h in d['protectedOriginal8Pcm'].items())
review=dict(schemaVersion=4,slug='limited-color-world',recordedAt=now(),execution=rel(sp),executionSha256=sha(sp),
 actualOuterSession=19362,actualOuterExitCode=0,actualExitTool='4f0029',all27BoardsAnd134SamplesDirectlyRead=True,
 allRawCaptionAndBoardHashesVerified=True,actualAbsolutePtsEqualNativeFrameTimes256=True,verifiedCuts=verified,
 scope='Complete direct reading of selected native samples and two-line placeholder pixels. Not all intermediate native frames, whole continuous playback, actual final cues, timing, narration or public-rights approval.',
 captionTest=d['captionTest'],original8PcmAndProtectedInputsUnchanged=True,initial37SecondsAdopted=False,
 unresolved=['room-door end must exclude wipe','portrait-corridor short standing tail trimmed','mushroom-arrival short stand excluded','Lemon shot rejected','new tree/corridor/route objects require accurate contextual labels and claim mapping'],
 proposedCleanAdditionalMaximumSeconds=32.5,proposedTotalWithOriginalBankSeconds=134.0,
 bridge3PcmMeasured=False,finalRatioApproved=False,sourceAdoptionApproved=False,allFinalCueUiApproved=False,
 allIntermediateNativeFramesViewed=False,continuousPlaybackApproved=False,publicRightsApproved=False,
 researchManipulated=False,ownResearchResumeClaim=False,gitImagesOrMediaAdded=0)
save(out,review)
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='extra-native-v4-direct-review-needs-boundary-trims',
 voiceMeasured=True,original8VoiceSeconds=199.52004166666666,currentWhole8AndIndependent24TextReviewComplete=True,
 extraNativeReview=rel(out),extraNativeBoardsDirectlyRead=27,extraNativeSamplesDirectlyRead=134,
 maximumUniqueActionSeconds=101.5,conditionalAdditionalAfterTrimsSeconds=32.5,
 nextAction='Reuse all v4 pixels; inspect only missing exact revised endpoints and fresh useful plant actions. Preserve original8PCM and32ASR; then measure additive3bridges and allocate unique actual60/explanation40. No stand/menu/transition/loop/slowdown quota.')
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(10):
    raw=qp.read_bytes();q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='limited-color-world');assert item['videoId'] is None
    item.update(stage=cp['stage'],nextAction=cp['nextAction'],extraNativeReview=rel(out))
    q['updatedAt']=q['lastProgressAt']=now()
    if qp.read_bytes()==raw:save(qp,q);break
else:raise RuntimeError('Preserve concurrent queue change')
print(json.dumps(dict(review=rel(out),sha256=sha(out),boards=27,samples=134,adoption=False,needsTrims=True),ensure_ascii=False))
