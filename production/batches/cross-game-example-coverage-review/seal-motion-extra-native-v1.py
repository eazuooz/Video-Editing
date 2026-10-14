"""Record already-read native pixels and conditional cuts; never approve a final mix."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, psutil

ROOT = Path(__file__).resolve().parents[3]
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stamp = datetime.now(timezone.utc).isoformat()
out = R/'extra-native-direct-review-v1.json'
assert not out.exists(), 'Do not overwrite completed direct review.'
executions = []
checked = {}
for version, session, completion in [(1,65250,'8cae06'),(2,None,'3f5bd3')]:
    p = R/f'extra-native-execution-v{version}.json'
    e = read(p)
    try:
        proc = psutil.Process(e['pid'])
        assert abs(proc.create_time()-e['createTime']) >= .01, 'Original worker still alive.'
    except psutil.NoSuchProcess:
        pass
    assert all(x['exitCode'] == 0 for x in e['results'])
    for x in e['samples']+e['boards']:
        assert sha(ROOT/x['path']) == x['sha256'], x['path']
        checked[x['path']] = x['sha256']
    e.update(actualOuterSession=session, actualOuterExitCode=0,
             actualOuterCompletion=completion, originalWorkerAlive=False,
             status='completed-native-samples-directly-reviewed-bounded')
    p.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n','utf-8')
    executions.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),
                           samples=e['sampleCount'],boards=e['boardCount'],session=session,
                           actualExitCode=0,actualCompletion=completion))
assert sum(x['samples'] for x in executions)==55
assert sum(x['boards'] for x in executions)==14
proof=dict(schemaVersion=1,reviewedAt=stamp,executionEvidence=executions,
    directlyReadNativeSamples=55,directlyReadBoards=14,sha256RecheckedFiles=checked,
    observations={
      'PowerWash227-251':'227 spray/dirty roundabout;229-232 tool/view changes;233 central radial menu excluded.234-249 nozzle changes direction over mostly stable playground.243-244 brief similar state must not be stretched.250-251 upward view excluded from independent-aim comparison.',
      'Portal99-109':'98.999 held cube on button/yellow dots;100 exit/check indicators.101 onward promotional transition/logos/platform text excluded. Full browser window held.',
      'Portal40-58':'40-42 held red cube/beam;43-45 changed room view with held cube;46-48 cube on floor;49-50 white panels/blue indicator;50.984 orange portal;51.985 unlit cube;52.986-53.987 held lit cube/beam through portal;54.988-55.989 placed cube/beam;56.990-57.991 farther room view.'},
    nativeSampledSourcePlanningApproved=True,allIntermediateFramesRead=False,
    exactFirstTransitionsMeasured=False,engineWorldMeasurementApproved=False,
    comfortEffectApproved=False,finalNativeCutApproved=False,
    finalNarrationTimedAnnotationApproved=False,finalRatioApproved=False,localOnly=True)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
normal=read(R/'additional-gameplay-candidate-normal-comparison-v1.json')
normal.update(schemaVersion=2,recordedAt=stamp,previousEvidence='additional-gameplay-candidate-normal-comparison-v1.json')
normal['observations'].append(dict(id='Portal40.006633-58.024633',preparedStart=40.006633,
    startRunningTime=40.008352,pausedEndTime=58.071581,proposedEnd=58.024633,
    decision='sampled-native-planning-approved-full-final-cut-pending',
    observations='Held red reflector cube/laser at start; placed cube/beam/portal and room at endpoint. All19 native samples directly compared. Selected subcut excludes long held lead-in; no portal-traversal, activation or discomfort causality claim.'))
(R/'additional-gameplay-candidate-normal-comparison-v2.json').write_text(json.dumps(normal,ensure_ascii=False,indent=2)+'\n','utf-8')
cuts=[dict(id='portal-held-putdown-portal-beam',game='Portal2',
    path='shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4',
    sha256='0d233cfcc3eb86b1e7722d257512ed6cfcc2b6276eac0b349fded54c516843bb',
    nativeInFrame=1289,nativeOutFrameExclusive=1739,timeBase='1/30000',ptsStep=1001,
    inSeconds=1289*1001/30000,outSecondsExclusive=1739*1001/30000,
    normalSpeedOutputFrames=900,
    connection='07b manipulation/view relationship: held cube with changed room cues, then putdown/portal-placement/beam redirection. Reuse in08b explicit cube/hand comparison only with announced transition.',
    excluded='40-42 static held lead-in;101+ promotional material',
    annotationRule='Red cube/held-object role; blue room/wall reference. Hide role markers during uncertain occlusion or pickup/drop transition. No fake trajectory or world-axis measurement.'),
  dict(id='powerwash-independent-nozzle-aim',game='PowerWashSimulator',
    path='shared/assets/game-footage/motion-sickness-games/PF5L_2g9UVQ.mp4',
    sha256='d2fff989d106762f66971c6e85172f79ce0bb6782c75f318d348447e11161612',
    nativeInFrame=14040,nativeOutFrameExclusive=14821,timeBase='1/15360',ptsStep=256,
    inSeconds=234,outSecondsExclusive=14821/60,normalSpeedOutputFrames=781,
    connection='07b comparison and08b cleaning/cube/hand connection: nozzle moves across target while playground reference is mostly stable. Observable aim direction, not measured cleaning percentage or comfort effect.',
    excluded='233 radial menu;250+ upward camera;69-90.5 insufficient action;115-132 central alert',
    annotationRule='Red nozzle tip/aim direction and blue stable visible background cue. Interpolate only between observed screen points within continuous shots; do not infer engine/world coordinates.')]
assert sum(x['normalSpeedOutputFrames'] for x in cuts)==1681
for c in cuts: assert sha(ROOT/c['path'])==c['sha256']
plan=dict(schemaVersion=2,preparedAt=stamp,status='conditional-narration-led-plan-needs-fine-anchors-and-continuous-cuts',
    replacesHeldNarrowProposal='narration-led-cut-allocation-proposal-v1.json',
    explanationEvidence='narration-timed-comparisons-sampled-direct-review-v1.json',
    explanationNormalPlayback='narration-timed-comparisons-normal-playback-observation-v1.json',
    measuredCurrentPcmSeconds=122.2175,newExplanationFrames=4397,newUniqueActualFramesRequired=6596,
    baselineBodyFrames=39473,baselineActualFrames=23684,baselineExplanationFrames=15789,
    conditionalNewBodyFrames=10993,conditionalTotalBodyFrames=50466,
    conditionalTotalActualFrames=30280,conditionalRatioErrorFrames=.2,
    existingCandidateBankCapacityFrames=4915,additionalCandidateFrames=1681,cuts=cuts,
    narrativeObservationConstraint='Approximately61 seconds beyond current PCM must serve unique visible before/action/result observations and role comparisons. Capacity alone cannot approve a cut; remove idle candidates, obtain clearer related sources if needed. Never trim useful explanation, loop or slow footage to fit.',
    exactFinalAllocationApproved=False,allNarrationTimedMovingPixelsApproved=False,
    finalRatioMeasured=False,currentMixedAudioApproved=False,newTtsRequired=False)
(R/'narration-led-cut-allocation-proposal-v2.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(samples=55,boards=14,hashChecks=len(checked),conditionalAdditionalFrames=1681,allFinalApproved=False)))
