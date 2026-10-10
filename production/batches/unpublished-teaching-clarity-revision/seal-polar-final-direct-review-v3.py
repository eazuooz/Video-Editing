"""Seal the actual completed direct review, without claiming human listening."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
MEDIA=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/final-pair-v3'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p): return p.relative_to(ROOT).as_posix()

state=read(OUT/'final-pixel-extraction-execution-v2.json')
assert state['exitCode']==0 and state['boardsCount']==386 and state['samplesCount']==2262
assert all(sha(ROOT/b['path'])==b['sha256'] for b in state['boards'])
pair=read(OUT/'final-pair-execution-v3.json')
source=pair['pair'][1]['sha256']
assert source=='8b1aacd54034faca55809702ab332e08b80403d32a113b2834e7fa7af867d372'
assert pair['exitCode']==0 and pair['currentAudioComparisonPreservedByIdenticalAacAndPcm']
assert read(OUT/'current-aac-complete-comparison-v2.json')['all44CompleteContextsDirectlyCompared']
for name in ['final-pixel-direct-review-v2.json','final-flow-playback-direct-review-v3.json']:
    assert not (OUT/name).exists(), name
observations={
 'intro':'Original cat/logo/name fade and exact120frames retained.',
 '01':'All12boards: four natural sentences and eight fixed cues promise cylinder, sphere and camera in their actual order; header/body/footer/caption gaps clear.',
 '02':'All28boards: normal bicycle jumps/landings, tracked rider and red horizontal/green height/blue hypotenuse marked illustrative; three ride boundaries explicitly distinguished; score/speed/sourcecredit and fixed captions clear.',
 '03':'All19boards: cylinder z-up and x-y floor explicitly introduced; fixed radius/angle and signed-radius distinction readable with moving point.',
 '04':'All17boards: cylinder forward/inverse equations and (5,0degrees,3) versus sqrt34 whole length distinguish projected radius from total distance; short math crossfades resolve.',
 '05':'All17boards: actual ramp/jump/landing action remains visible; annotated projection is a chosen coordinate plane, not distance to sloping ground or reconstructed world measurement.',
 '06':'All28boards: zenith phi zero/top and90/horizontal versus latitude90-phi; point moves, forward/inverse formulas and origin/pole rules readable above the fixed caption.',
 '07':'All19boards: book convention +xright/+yup/+zforward and positive pitch down announced; heading, pitch and roll separated rather than attributed universally to engines.',
 '08':'All28boards: normal spins/jumps/turns show direction, attitude and viewing roles; world up and screen vertical explicitly separated; different rides marked at exact cuts and overlays do not cover UI.',
 '09':'All19boards: x=r*cos(p)*sin(h), y=-r*sin(p), z=r*cos(p)*cos(h), axis tests and radians versus distance units match narration; minus glyph readable.',
 '10':'All17boards: hypot3 versus horizontal hypot, atan2(x,z), atan2(-y,q), origin/pole policies and stored heading versus retained control heading distinguished; no layout overlap.',
 '11':'All25boards: camera-target placement and opposite look direction have distinct role colors; actual ride and relational/numeric model clearly distinguished; exactengine coordinates not inferred. New ride and overlay removal correctly precede following model.',
 '12':'All18boards: same-position angular aliases and negative radius identity readable; diagram keeps the same point and directs Cartesian comparison.',
 '13':'All19boards: canonical range and undefined pole heading distinguished from full orientation/gimbal lock; stored h0 versus controls/nearpole snap policy separated.',
 '14':'All18boards: regular ride is explicitly not a pole experiment or proprietary implementation evidence; numerical representation versus pitch limits/smoothtracking are separate choices; annotations/captions/UI clear.',
 '15':'All17boards: centre(0,1,0), r5/h60/p-30 yields offset(3.75,2.5,2.165) and camera(3.75,3.5,2.165); placement and centre-camera view vector separated with readable minus.',
 '16':'All27boards: blue target-to-camera placement and red camera-to-target look are opposite; actual ride versus relational model labeled; second ride marked, rider/score/speed/sourcecredit/caption spacing retained.',
 '17':'All20boards: component addition(1,0,0)+(0,2,0)=(1,2,0), clamp1.0000001 to1, origin/pole policy and lost precision at huge angles distinguished. Summary leaves caption gap; unit/axis/rounding checks lead to application.',
 '18':'All14boards: normal turning/jumps/doublebackflip/landing show yellow position, red attitude and blue view roles. Text says illustrative role model and formula needs separate collision/rotation/tracking rules; rider/UI remain visible. Short natural foliage overlap is gameplay and not hidden by added annotation.',
 '19':'All20boards: (r2,h0,p0)=(0,0,2), h90=(2,0,0), p-90=(0,2,0) animated axis tests match positivepitchdown convention; residual floating components/poleheading policy stated; conclusion returns to height/distance/two angles and applying to camera.',
 'member':'All3boards/14samples: original12profile/name/badge rows, channel logo, exact membership title and coaching URL preserved; title fade at both ends is original; no generated identity substitutes.'
}
now=datetime.now(timezone.utc).isoformat()
pixels={'schemaVersion':1,'reviewedAt':now,'sourceSha256':source,
 'extractionState':rel(OUT/'final-pixel-extraction-execution-v2.json'),
 'actualOuterExitCode':0,'exitObservedChunk':'0a51b9','processAbsenceObservedChunk':'c558f2',
 'boardsDirectlyRead':386,'samplesDirectlyRead':2262,'reviewedBoards':state['boards'],
 'coverage':'Every listed whole1second, KO/ENcue start/end +/-1 and mid, scene/nativecut and annotationstage +/-1 plus intro/member boundary sample.',
 'observationsByScene':observations,'allListedSamplesDirectlyRead':True,
 'allFinalCueCutPixelsApproved':True,'unresolved':[],
 'all54115FramesHumanViewed':False,'humanWholeListeningApproved':False,
 'pronunciationApproved':False,'publicRightsApproved':False,
 'reviewScope':'Direct pixel approval covers all2262 planned samples. Whole decoded media and every PTS are machine verified; human complete listening/each intervening frame is not asserted.'}
write(OUT/'final-pixel-direct-review-v2.json',pixels)
playback=read(MEDIA/'playback-whole-ended-status.json')
events=playback['events'];assert events[-1]['kind']=='whole-ended'
assert playback['paused'] and playback['playbackRate']==1 and not playback['muted']
assert abs(playback['currentTime']-54115/60)<0.00001
assert [e['scene'] for e in events if e['kind']=='scene-enter']==['intro']+[f'{i:02}' for i in range(1,20)]+['member']
assert all(e['playbackRate']==1 and not e['muted'] for e in events)
assert [e['kind'] for e in events if e['kind']!='scene-enter']==['whole-start','whole-ended']
proofs=[]
for name in ['playback-whole-ended-status.json','playback-whole-ended-ax.txt','playback-whole-ended.png']:
    p=MEDIA/name;assert p.exists();proofs.append({'path':rel(p),'sha256':sha(p)})
flow={'schemaVersion':1,'reviewedAt':now,'sourceSha256':source,
 'wholeNormalSpeedPlaybackReachedEnd':True,'sampledContinuousFlowApproved':True,
 'browser':'3','tab':'51','url':'http://127.0.0.1:9250/polar-3d-final-flow-v3.html',
 'startAt':'2026-10-10T12:55:50.364Z','endedAt':'2026-10-10T13:10:52.355Z',
 'durationSeconds':54115/60,'wholePlaybackEvents':events,'savedUiProof':proofs,
 'pixelReview':rel(OUT/'final-pixel-direct-review-v2.json'),
 'fullChapterConnectionReview':rel(OUT/'causal-flow-and-primary-reference-review-v1.json'),
 'currentWholeMixedAudioReview':rel(OUT/'current-aac-complete-comparison-v2.json'),
 'observedFlow':'Preserved question/overview -> actual height/position observations -> cylinder/sphere conventions and conversion -> undefined directions and policies -> placement versus view -> vector/numeric limits -> actual application -> three axis tests and conclusion.',
 'unresolved':[],'allIntermediateFramesDirectlyViewed':False,
 'humanWholeListeningApproved':False,'pronunciationApproved':False,'publicRightsApproved':False,
 'reviewScope':'Actual whole1x unmuted player completion,21scene entries and directly read2262samples plus previously observed live action/moving pilots; this is not a claim of human continuous complete listening.'}
write(OUT/'final-flow-playback-direct-review-v3.json',flow)
progress=OUT/'final-pixel-direct-review-progress-v2.json'
if progress.exists():
    p=read(progress);p.update(reviewedAt=now,boardsDirectlyRead=386,reviewedBoards=state['boards'],
       allListedSamplesDirectlyRead=True,allFinalCueCutPixelsApproved=True,finalEvidence=rel(OUT/'final-pixel-direct-review-v2.json'))
    write(progress,p)
qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qpath)
q['execution'].update(stage='polar-local-final-reviewed-adoption-collection-pending',
 finalPixelReviewProgress={'path':rel(OUT/'final-pixel-direct-review-v2.json'),'boardsRead':386,'boardsTotal':386,'finalApproval':True},
 next='Adopt reviewed pair and collect four exact files once; then single private replacement upload/settings and selective Git, followed by actual schedule swap after new ID verification.')
write(qpath,q)
print(json.dumps({'boardsRead':386,'samplesRead':2262,'pixelApproved':True,'wholePlaybackReachedEnd':True,'humanListeningApproved':False,'actualId':None}))
