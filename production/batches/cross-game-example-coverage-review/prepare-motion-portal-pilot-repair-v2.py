"""Seal the directly observed v1 defect and prepare one bounded v2 repair."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
S=ROOT/'production/batches/cross-game-example-coverage-review'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    assert not p.exists(),p
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
state=read(R/'portal-annotation-pilot-execution-v1.json')
assert state['actualOuterExitCode']==0 and state['sessionId']==5691
assert len(state['samples'])==12
for row in state['samples']:
    assert sha(ROOT/row['path'])==row['sha256']
assert sha(ROOT/state['path'])==state['sha256']
review=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),
    actualSession=5691,actualOuterExitCode=0,all12EncodedSamplesDirectlyRead=True,
    encodedSamples=state['samples'],videoPath=state['path'],videoSha256=state['sha256'],
    status='held-cyan-wall-target-crosses-cube-during-interpolation',
    findings=[dict(frames=[15,30],role='cyan room-wall clue',
        observation='Cyan endpoint falls on the cube left face/upper-left edge rather than a visible room wall.',
        cause='Interpolation between left-wall and right-wall observations crosses the foreground cube.',
        repair='Hide the wall label, leader and endpoint until native frame1139; retain the observed cube marker.'),
        dict(frames=[0,1,15,30,45,60,75,90,105,120,150,179],
             observation='Red cube endpoint remains on its visible upper face; role labels, source credit and fixed mock caption remain readable.')],
    staticApprovalDoesNotApproveInterpolation=True,normalSpeedPlaybackReviewed=False,
    movingAnnotationApproved=False,narrationTimed=False,finalCueApproval=False,
    allFinalPixelsApproved=False,sourceAudioAdopted=False,gitImagesAdded=0)
save(R/'portal-annotation-pilot-direct-review-v1.json',review)
plan=read(R/'portal-annotation-observation-plan-v1.json')
plan.update(preparedAt=datetime.now(timezone.utc).isoformat(),
    priorPlan='portal-annotation-observation-plan-v1.json',priorPlanSha256=sha(R/'portal-annotation-observation-plan-v1.json'),
    priorEncodedReview='portal-annotation-pilot-direct-review-v1.json',
    wallMarkerVisibleFromNativeFrame=1139,
    interpolation='Hide cyan wall annotation before native1139. Later screen-space interpolation remains subject to encoded moving review; no world tracking claim.')
save(R/'portal-annotation-observation-plan-v2.json',plan)
source=(S/'render-motion-portal-annotation-pilot-v1.py').read_text('utf-8-sig')
source=source.replace('portal-annotation-pilot-v1','portal-annotation-pilot-v2').replace('portal-annotation-observation-plan-v1','portal-annotation-observation-plan-v2').replace('portal-annotation-pilot-execution-v1','portal-annotation-pilot-execution-v2')
old="            d.rectangle((80,175,580,232),fill='white',outline='#087ca6',width=3);d.text((100,183),'방의 단서: 벽',font=font,fill='#066685')\n            d.line([(580,232),(610,270),tuple(b)],fill='#1bb3d0',width=5);d.ellipse((b[0]-11,b[1]-11,b[0]+11,b[1]+11),outline='#1bb3d0',width=4)"
assert source.count(old)==1
source=source.replace(old,"            if native>=plan['wallMarkerVisibleFromNativeFrame']:\n"+'\n'.join('    '+line for line in old.splitlines()))
target=S/'render-motion-portal-annotation-pilot-v2.py'
assert not target.exists()
target.write_text(source,'utf-8')
print('V1 all12 direct-review defect sealed; v2 visibility repair prepared. No render/GPU/voice approval.')
