"""Only two directly reviewed texture inputs replace v332; other92 inputs exact."""
from pathlib import Path
import importlib.util,copy,json
spec=importlib.util.spec_from_file_location('m',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
stackp=P/'part1-texture-stack-preview-execution-v343d.json';stack=m.read(stackp)
tilep=P/'part1-texture-preview-execution-v343.json';tile=m.read(tilep)
partialp=P/'part1-texture-preview-partial-direct-review-v343c.json';partial=m.read(partialp)
cuep=P/'part1-texture-stack-cues-execution-v343e.json';cues=m.read(cuep)
assert stack['status']==tile['status']=='complete-awaiting-direct-review' and stack['exitCode']==tile['exitCode']==0
assert cues['status']=='complete' and len(cues['boards'])==5 and len(cues['images'])==30
assert partial['textureTile']['approvedInputPixels'] and partial['all9BoardsDirectlyRead'] and partial['all50ImagesDirectlyRead']
proposalp=P/'part1-texture-source-order-proposal-v343c.json';proposal=m.read(proposalp)
assert proposal['allTwoSourceIntervalsActuallyPlayed'] and proposal['inputs'][0]['sourceReview']['fullCandidateActuallyPlayed']
assert stack['proposalSha256']==m.sha(proposalp)
records=[]
for e,ex in [(stack,stackp),(tile,tilep)]:
    rr=e['results'][0] if e is stack else next(x for x in e['results'] if x['id']=='texture-project-tile-settings:native')
    r=copy.deepcopy(rr)
    for key in ['native','preview']:assert m.sha(R/r[key]['path'])==r[key]['sha256']
    r.update(fullSelectedIntervalActuallyPlayed=True,playbackRate=1,normalSpeedInputPixelsApproved=True,selectedForCurrentPrivateTechnicalPair=True,
        actualPlaybackEnd=26.116666666666667 if e is stack else 24.283333333333335,
        allFiveCueImagesDirectlyRead=True,
        observation='All4 source pieces appear at1x; state labels distinguish shared coordinates/changed connections/returned before comparison/changed result. Stack1→3 now appears during cue84. Entire Stats panel is above880; fixed caption centered960,970. Five cues readable. No invented stack number or frame-time measurement.' if e is stack else partial['textureTile']['observations'],
        execution=dict(path=m.rel(ex),sha256=m.sha(ex)))
    records.append(r)
rp=P/'part1-texture-native-input-direct-review-v344.json'
assert not rp.exists()
review=dict(reviewedAt=m.stamp(),planSha256=proposal['planSha256'],allTwoFullInputIntervalsActuallyPlayed=True,allTwoSelectedForCurrentPrivateTechnicalPair=True,records=records,
    partialReview=dict(path=m.rel(partialp),sha256=m.sha(partialp)),stackCueExecution=dict(path=m.rel(cuep),sha256=m.sha(cuep)),
    all5StackBoardsDirectlyRead=True,all30StackImagesDirectlyRead=True,
    boards=[dict(b,directlyRead=True) for b in cues['boards']],
    resolvedIssues=['Cue84 count obscured by caption in333','Cue93 virtual texture settings displayed too late in333','Rejected343 stack result displayed later than cue84'],
    comparisonSourceFramesPartitionedOnce=True,all77PcmPreserved=True,allCaptionsPreserved=True,
    finalCueBoundaryPixelsPending=True,allFinalPixelsReviewed=False,qaApproved=False,collected=False,uploaded=False,newGitImages=0,humanListeningPending=True)
m.save(rp,review)
pp=P/'part1-final-input-plan-v309.json';plan=m.read(pp);assert m.sha(pp)==review['planSha256']
priorp=P/'part1-final-visual-build-v332.json';prior=m.read(priorp)
assert prior['planSha256']==m.sha(pp) and prior['wholeDecodeExitCode']==0 and prior['all89148PtsExact1500']
assert m.sha(R/prior['path'])==prior['sha256']
resources=m.resources();out=R/'production/research/game-lighting-history/local/part1-texture-repaired-visual-v344';sp=P/'part1-texture-repaired-visual-execution-v344.json'
assert not out.exists() and not sp.exists();out.mkdir()
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,commands=[],results=[],resources=resources,cpuThreads=2,gpuJobs=0,newTts=0,newAudioMix=0,newGitImages=0,allFinalPixelsReviewed=False,uploaded=False)
def checkpoint():
    cp=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
    j['episode04Part1TextureVisualV344']=dict(execution=m.rel(sp),status=state['status'],worker=state['worker'],active=state['active'],finalApproved=False)
    j['ownedActiveWork']=dict(type='one-reviewed-two-texture-master-assembly',execution=m.rel(sp),worker=state['worker'],active=state['active'],cpuThreads=2,gpuJobs=0,next='Current pair345 then changed final cue-edge/moving QA') if state['status']=='running' else dict(status='no-active-owned-media-worker',execution=m.rel(sp),next='Current pair345 then changed final cue-edge/moving QA')
    m.save(cp,j)
m.save(sp,state);checkpoint()
try:
    selected={r['id']:r for r in records};cuts=copy.deepcopy(prior['cuts']);files=[R/plan['branding']['path']];changed=[]
    for c in cuts:
        assert m.sha(R/c['path'])==c['sha256']
        if c['id'] in selected:
            r=selected[c['id']];assert(c['frames'],c['fromFrame'],c['toFrame'])==(r['frames'],r['fromFrame'],r['toFrame'])
            for key in list(c):
                if key.startswith('retainedByteIdentical') or key in ['technicalProofs','technical','inputDirectReview']:c.pop(key)
            c.update(path=r['native']['path'],sha256=r['native']['sha256'],sourceCuts=r['sourcePieces'],technical=r['technical'],inputDirectReview=dict(path=m.rel(rp),sha256=m.sha(rp)),retainedByteIdenticalToV332=False)
            changed.append(c['id'])
        else:c['retainedByteIdenticalToV332']=True
        files.append(R/c['path'])
    assert len(cuts)==94 and set(changed)==set(selected);files.append(R/plan['membership']['path'])
    concat=out/'master.concat.txt';concat.write_text('\n'.join("file '"+str(f).replace('\\','/')+"'" for f in files)+'\n','utf8')
    visual=out/'silent-visual.mp4'
    m.run([m.FF,'-n','-hide_banner','-nostdin','-threads','2','-f','concat','-safe','0','-i',concat,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart',visual],'master-concat',state,sp,out)
    technical=m.verify_video(visual,plan['finalFrames'],state,sp,out,'verify-master')
    proof=copy.deepcopy(prior)
    proof.update(builtAt=m.stamp(),path=m.rel(visual),sha256=m.sha(visual),cuts=cuts,technical=technical,previousVisual=dict(path=m.rel(priorp),sha256=m.sha(priorp)),
        retainedOther92InputsByteIdenticalToV332=True,retainedOther93InputsByteIdenticalToV322=False,sourceModelsRerendered=0,nativeCutsReframed=2,newTts=0,newAudioMix=0,
        allFinalPixelsReviewed=False,allMovingPixelsReviewed=False,qaApproved=False,uploaded=False,newGitImages=0)
    proof['inputOverrides'].update(textureReview=dict(path=m.rel(rp),sha256=m.sha(rp)),textureChangedInputs=changed,other92InputsExactV332=True,other93InputsExactV322=False)
    m.save(P/'part1-final-visual-build-v344.json',proof)
    state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None);m.save(sp,state);checkpoint()
    print(json.dumps(dict(frames=89148,changedInputs=2,retainedInputs=92,pixelsApproved=False)))
except BaseException as e:
    state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(sp,state);checkpoint();raise
