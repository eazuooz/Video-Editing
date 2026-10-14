"""Record actual v1 review and prepare unique conservative recuts, not adoption."""
from pathlib import Path
import datetime, hashlib, json, subprocess, os
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
B=ROOT/'production/batches/unpublished-teaching-clarity-revision'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
ex=read(R/'observation-pilot-execution-v1.json')
assert ex['workerExitCode']==0 and ex['wholeDecodeExitCode']==0 and len(ex['samples'])==25 and len(ex['boards'])==5
assert all(sha(ROOT/x['path'])==x['sha256'] for x in ex['samples']+ex['boards'])
base=read(R/'baseline-preservation-v1.json');assert all(sha(ROOT/x['path'])==x['sha256'] for x in base['protectedFiles'])
live=subprocess.check_output(['powershell','-NoProfile','-Command','Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(82556,81540,38588) } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],text=True,encoding='utf8').strip()
assert not live,'Check PID creation and command before treating it as this worker'
target=R/'observation-pilot-direct-review-v1.json';assert not target.exists()
review=dict(observedAt=stamp,actualSessionId=4690,actualOuterExitCode=0,outerExitObservedChunk='d4015f',workerGenerationTerminated=True,
    all25ListedEncodedSamplesDirectlyRead=True,all5BoardsDirectlyRead=True,allHashesMatched=True,
    retainedSourcePixelAnchorsMatched=True,wholeDecodeExitCode=0,baseline38Unchanged=True,
    observations=['Bright gray/white flight makes the moving character more readable than the older green opening.',
        'Golden image-up arrows stay image-vertical and do not claim game-world up.',
        'Labels and geometry stay above910; no narration box is burned in this silent pilot.',
        'f120/135/150/165 hide the body guide on rejected segmentation. The mask loses a visible small body for60frames, so a complete position-vs-tilt illustration is not approved.',
        'f240/255/270 and359 capture only a connected portion of the articulated silhouette. Whole-body envelope wording is too broad. Principal line also changes with limb silhouette; it is not a torso/forward/roll axis.'],
    unresolved=['Improve silhouette grouping and small-body detection; hide uncertain lines.',
        'Use explicit screen centroid/displacement geometry and label the observed silhouette, rather than teaching an unverified anatomical or engine axis.'],
    prototypeApproved=False,allMovingPixelsApproved=False,sourceAdoptionApproved=False,
    timedNarrationApproved=False,finalCaptionUiApproved=False,publicRightsApproved=False,
    samples=ex['samples'],boards=ex['boards'])
write(target,review);ex.update(actualOuterExitCode=0,outerExitObservedChunk='d4015f',sessionId=4690,status='completed-direct-reviewed-held-for-tracking-repair',directReview=rel(target));write(R/'observation-pilot-execution-v1.json',ex)
cuts=read(ROOT/'projects/game-math-orientation-matrices/sources/gameplay-cuts.json')['cuts']
replacement={'02':[(822*60,861*60)],'11':[(350*60,364*60),(370*60,397*60)],
    '14':[(433*60,447*60),(891*60,908*60),(123*60,131*60),(137*60,143*60),(407*60,407*60+146)],
    '23':[(861*60,884*60),(22*60,22*60+1611)]}
windows=[]
for cut in cuts:
    pairs=replacement.get(cut['scene'],[(round(x['in']*60),round(x['in']*60)+x['frames']) for x in cut['segments']])
    assert sum(b-a for a,b in pairs)==sum(x['frames'] for x in cut['segments'])
    for index,(a,b) in enumerate(pairs):
        windows.append(dict(scene=cut['scene'],segment=index,firstNativeFrame=a,endExclusiveNativeFrame=b,frames=b-a,
            seconds=(b-a)/60,sourcePtsIn=a*256,sourcePtsOutExclusive=b*256,focus=cut['focus'],
            nativeListedSamplePreflightRead=True,normalPlaybackCompared=False,sourceAdopted=False,
            entireFrameAndCaptionUiApproved=False,claimsOneContinuousEventAcrossCuts=False))
assert sum(x['frames'] for x in windows)==21370
ordered=sorted(windows,key=lambda x:x['firstNativeFrame'])
assert all(a['endExclusiveNativeFrame']<=b['firstNativeFrame'] for a,b in zip(ordered,ordered[1:])), 'Do not reuse frames'
candidate=R/'conservative-source-recut-proposal-v1.json';assert not candidate.exists()
plan=dict(preparedAt=stamp,status='candidate-prepared-normal-playback-and-tracking-pending',
    source='shared/output/game-math-part2-full-series/sources/-Hpr1dqRzIk.mp4',sourceSha256='469df1da0e7fce4b5480064e43a2982e1121f9e1adb899acdbbd8f464371fd66',
    sourceTimebase='1/15360',nativePtsStep=256,normalSpeed=1,loop=False,sourceAudio=False,
    preservesOriginalActualFrames=21370,preservesOriginal24ApprovedPcm=True,windows=windows,
    firstExampleReason='822–861 gray/white background provides a larger, readable silhouette; screen motion is distinct from world rotation.',
    repairedScenes=['02 excludes51–54 collision/menu;39seconds reassigned to distinct bright flight.',
        '11 shifts351–365 to350–364 and retains370–397, excluding364.3 impact and364.8 menu.',
        '14 replaces the unsplit three-crash/reset sequence with five explicitly separate normal-flight examples.',
        '23 reuses the viewer question using distinct861–884 and22–48.85 frames rather than replaying the opening.'],
    scene14CutsAreSeparateExamples=True,extraBridgeActualSecondsMeasured=None,
    sourceAdoptionApproved=False,allFinalPixelsApproved=False,newTtsStarted=False)
write(candidate,plan)
cp=read(R/'latest-checkpoint.json');cp.update(observedAt=stamp,stage='conservative-recut-prepared-observation-pilot-v1-held-for-repair',
    observationPilot=rel(target),conservativeRecut=rel(candidate),next='Repair silhouette grouping and use explicit image geometry; compare each conservative cut at1x, then adopt only the checked scope before measuring new bridge voice.')
write(R/'latest-checkpoint.json',cp)
q=read(B/'queue.json');q['ownedJob']=None;q['updatedAt']=stamp
q.setdefault('completedJobs',[]).append(dict(slug='game-math-orientation-matrices',kind='silent-observation-pilot',sessionId=4690,actualOuterExitCode=0,observedChunk='d4015f',review=rel(target),approved=False))
write(B/'queue.json',q)
print(json.dumps({'pilotSamplesRead':25,'boardsRead':5,'actualOuterExitCode':0,'pilotApproved':False,'recutFrames':21370,'windows':len(windows),'baselineUnchanged':38},ensure_ascii=False))
