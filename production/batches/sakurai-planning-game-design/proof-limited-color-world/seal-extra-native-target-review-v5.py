from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent;BASE=ROOT/'projects/limited-color-world/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
def save(p,d):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
sp=P/'extra-native-targets-execution-v5.json';d=read(sp);out=P/'extra-native-target-direct-review-v5.json';assert not out.exists()
assert d['actualExitObserved'] and d['actualOuterExitCode']==0 and d['actualOuterExitToolObservation']=='dec20f'
notes={
 'room-door-clean-end':'First5940/last6089 are clean native room frames. Player moves toward left door; old wipe6119 excluded. Six new/reused endpoint samples plus v4 interiors support bounded2.5s.',
 'corridor-moving-clean-end':'First6480/last6629 are clean native corridor frames. Player reaches centre carpet, PortraitQ above fixed caption. Old half-second standing tail excluded; corridor-labelled generic shape/path observation only.',
 'mushroom-arrival-moving-only':'First6660/last6689 show actual movement from right ledge toward lower-right path; no dialogue/wipe. Original110–111 stationary portion excluded;0.5s only.',
 'tree-outline-step-away':'First35880/last35969 show walking beside the previously painted tree. Lostkid interaction bubble appears near end but not a dialogue modal. Outlines and player are clear above caption; no collectible found603s. Use tree/path label and generic contour check.',
 'mushroom-erase-shrink-and-return':'Editorial name erase is not proven by these pixels: orange ground persists. Cap is low, rises again at27.5, then compresses/lowers and player crosses left. Actual transient height/contact/movement only; do not claim erasing, permanent unlocking or an optimal return path. First1620/last1769 no wipe.',
 'branch-height-change-and-climb':'Held as proposed4s height/climb proof. At68.5 branches appear during brush action; growth is visible but a climb/raised platform is not established. GiftQ and letterbox near70.5–71 are unrelated to the planned height claim. Inspect only68.5–70.5 endpoints as a separate plant-contour observation, never call it a platform climb.',
 'flower-route-exit-before-wipe':'First5760/last5834 normal walking down/right along outlined stone path after the flowers. Up120 keeps player/destination path above fixed caption.98s source wipe excluded; no dialogue or stationary quota.'
}
verified=[]
for c in d['cuts']:
 for s in c['samples']:
  assert s['pts']==s['nativeFrame']*256 and sha(ROOT/s['path'])==s['sha256'] and sha(ROOT/s['captionTestPath'])==s['captionTestSha256']
 for b in c['boards']:assert sha(ROOT/b['path'])==b['sha256']
 held=c['key']=='branch-height-change-and-climb'
 verified.append(dict(key=c['key'],source=c['source'],startFrame=c['startFrame'],endFrameExclusive=c['endFrameExclusive'],sampleCount=len(c['samples']),boards=c['boards'],
 observed=notes[c['key']],boundedSelectedSamplesApproved=not held,exactSampleEndpointsApproved=not held,fixedPlaceholderSampleGapApproved=not held,
 editorialNameCorrected='mushroom-return-crossing' if c['key']=='mushroom-erase-shrink-and-return' else None,
 adopted=False,allContinuousNativeFramesApproved=False,finalCueUiApproved=False))
assert sum(len(c['boards']) for c in d['cuts'])==12 and sum(len(c['samples']) for c in d['cuts'])==57
assert all(sha(ROOT/p)==h for p,h in d['protectedInputs'].items()) and all(sha(ROOT/p)==h for p,h in d['protectedOriginal8Pcm'].items())
r=dict(schemaVersion=5,slug='limited-color-world',recordedAt=now(),execution=rel(sp),executionSha256=sha(sp),
 actualSession=66883,actualOuterExitCode=0,actualExitTool='dec20f',all12BoardsAnd57SamplesDirectlyRead=True,
 allSampleCaptionAndBoardHashesVerified=True,allSelectedPtsEqualFrameTimes256=True,verifiedCuts=verified,
 reusedV4Interiors='production/batches/sakurai-planning-game-design/proof-limited-color-world/extra-native-action-direct-review-v4.json',
 scope='Revised endpoint and new selected native sample review with two-line placeholder. Not every intermediate frame, continuous playback, final cue, final timing or public rights.',
 usefulAdditionalMaximumBeforePlantTrimSeconds=37.75,totalIncludingOriginal101_5Seconds=139.25,
 heldProposedBranch4Seconds=True,plantContour2SecondsPendingExactEndpoints=True,
 original8PcmAndProtectedInputsUnchanged=True,sourceAdoptionApproved=False,finalRatioApproved=False,publicRightsApproved=False,
 allFinalCueUiApproved=False,researchManipulated=False,ownResearchResumeClaim=False,gitImagesOrMediaAdded=0)
save(out,r)
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='extra-native-v5-reviewed-plant-trim-pending',extraNativeV5Review=rel(out),
 nextAction='Inspect only missing68.5–70.5 plant-contour endpoints; preserve all v4/v5 native pixels. Then protect/source-map three causal bridge paragraphs and measure them in one cooperative TTS batch. Original8 PCM/32ASR are complete; final gates remain false.')
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(10):
 raw=qp.read_bytes();q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='limited-color-world');assert item['videoId'] is None
 item.update(stage=cp['stage'],nextAction=cp['nextAction'],extraNativeV5Review=rel(out));q['updatedAt']=q['lastProgressAt']=now()
 if qp.read_bytes()==raw:save(qp,q);break
else:raise RuntimeError('Concurrent queue change')
print(json.dumps(dict(review=rel(out),sha256=sha(out),boards=12,samples=57,proposedBranchHeld=True)))
