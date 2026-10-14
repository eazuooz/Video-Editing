"""Fresh read-only ownership check and narrow motion checkpoint update."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
B=ROOT/'production/batches/cross-game-example-coverage-review'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'resource-and-annotation-handoff-v16.json'
assert not out.exists()
prior=read(R/'resource-and-annotation-handoff-v15.json')
status_path=Path(prior['currentResearchStatusPath']);status=read(status_path)
assert status['status']=='complete_pending_visual_review' and status['completed']==status['total']==1088
assert not (ROOT/'shared/output/GPU_HANDOFF.json').exists()
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']
assert len(protected)==71
for row in protected: assert sha(ROOT/row['path'])==row['sha256'],row['path']
ident=prior['currentOriginalResearchIdentity']
try:
    p=psutil.Process(ident['pid']); assert abs(p.create_time()-ident['createTime'])>=.01
except psutil.NoSuchProcess: pass
for f in ['narration-timed-comparisons-render-execution-v1.json','extra-native-execution-v1.json','extra-native-execution-v2.json']:
    e=read(R/f)
    assert e['actualOuterExitCode']==0
    if 'pid' in e:
        try:
            p=psutil.Process(e['pid']); assert abs(p.create_time()-e['createTime'])>=.01
        except psutil.NoSuchProcess: pass
evidence=['narration-timed-comparisons-sampled-direct-review-v1.json',
    'narration-timed-comparisons-normal-playback-observation-v1.json',
    'extra-native-direct-review-v1.json','additional-gameplay-candidate-normal-comparison-v2.json',
    'narration-led-cut-allocation-proposal-v2.json']
stamp=datetime.now(timezone.utc).isoformat()
next_step='Preserve completed3currentPCM/repair/ASR, summary1997f and five narration-timed explanation renders2400f with50encoded samples13boards/normal1x start-end. Preserve55newnative samples14boards, exclude233menu and101+Portalpromotional material. Fine-anchor the conditional Portal1289-1739/PWash14040-14821 cuts, then derive paragraph-led unique actual/meaningful observations. Conditional4397ex/6596actual replaces held narrow3234ex/4851actual proposal; capacity alone is not approval. Review tracked narration-timed gameplay, mix/KOEN/chapters/end/currentmixedASR/allcuecutpixels/two decodes/four outputs/private/settings/selectGit/current09reservation before matchingobsolete deletion. Stop and pause after normal-transform-UV boundary; no six Sakurai starts.'
proof=dict(schemaVersion=1,recordedAt=stamp,previousHandoff='resource-and-annotation-handoff-v15.json',
    evidence=[dict(path=f,sha256=sha(R/f)) for f in evidence],
    activeOwnedWorkers=0,all71ProtectedHashesMatched=True,
    currentOriginalResearchIdentity=ident,currentOriginalResearchAlive=False,
    currentResearchStatus=status,currentResearchStatusPath=str(status_path),
    currentResearchStatusSha256=sha(status_path),currentForeignLease=None,
    researchControlMutations=0,ownResearchResumeClaimThisStep=False,
    currentResearchInterpretation='Previously restored original queue has completed1088/1088 and exited; visual review pending. No restart or optimizer/RNG approval.',
    comparisonRender=dict(session=27660,completion='259ed5',exitCode=0,scenes=5,frames=2400),
    comparisonQa=dict(completion='0e812a',exitCode=0,samples=50,boards=13,wholeDecodes=5),
    extraNativeV1=dict(session=65250,completion='8cae06',exitCode=0,samples=36,boards=9),
    extraNativeV2=dict(session=None,completion='3f5bd3',exitCode=0,samples=19,boards=5),
    conditionalNewExplanationFrames=4397,conditionalNewActualFrames=6596,
    conditionalAdditionalCandidateFrames=1681,nativeCutAndNarrationAllocationApproved=False,
    currentMixedAudioApproved=False,allFinalPixelsApproved=False,finalRatioMeasured=False,
    fourOutputsCollected=False,actualReplacementVideoId=None,privateSettingsVerified=False,
    gitDelivered=False,scheduleReplacementVerified=False,oldUploadDeleted=False,
    stopAfter='game-math-normal-transform-uv',startRemainingSixSakurai=False,next=next_step)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
cp_path=R/'latest-checkpoint.json';cp=read(cp_path)
cp.update(recordedAt=stamp,currentHandoff=out.name,
    stage='measured-comparisons-and-native-samples-reviewed-fine-tracking-and-final-cut-mapping-pending',
    ownedJob=dict(status='completed',active=False,sessionId=65250,exitCode=0,completion='8cae06'),
    activeOwnedWorkers=0,comparisonRenderCompleted=True,comparisonRenderSession=27660,
    comparisonSampledReview=evidence[0],comparisonNormalPlayback=evidence[1],extraNativeDirectReview=evidence[2],
    narrationLedCutAllocationProposal=evidence[4],conditionalNewExplanationFrames=4397,
    conditionalNewUniqueActualFrames=6596,currentOriginalResearchAlive=False,
    currentOriginalResearchStatus=status,next=next_step)
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
queue_path=B/'queue.json';queue=read(queue_path)
matches=[v for v in queue.values() if isinstance(v,dict) and v.get('currentCheckpoint','').endswith('revision-cross-game-four-v1/latest-checkpoint.json')]
assert len(matches)==1
matches[0].update(currentHandoff=out.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,
                  conditionalNewExplanationFrames=4397,conditionalNewActualFrames=6596)
queue.update(status='active',recordedAt=stamp,next=next_step)
queue_path.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(handoff=out.name,protected=71,activeOwnedWorkers=0,researchStatus=status['status'])))
