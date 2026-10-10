from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
q=read(R/'additive-mc-qa-v2.json')
assert q['actualDecodeExitCode']==0 and q['sampleCount']==74 and q['boardCount']==13
for x in q['samples']+q['boards']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
review=dict(recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceSha256=q['sourceSha256'],
    all74SamplesAnd13BoardsDirectlyRead=True,allFramePtsExact=True,wholeDecodeExitCode=0,
    maxNonWhitePixelsBelow910=0,openingSelectedSamplesApproved=True,goalSelectedSamplesApproved=False,
    resolved=['Gold floor target stays separate from blue post.','Wall/floor/goal labels now use separate leaders.'],
    remaining=['At later goal rotation, projected front/right floor faces touch the direction-change footer.'],
    rawFrames=886,rawOpeningInclusive=[0,480],rawGoalInclusive=[481,885],
    selectedOpeningInclusive=[0,479],plannedSelectedGoalFrames=403,
    v3Target='Only goal frames481..883; reduce projection to.9 and originY55.',
    renderedFfmpegExitCode=None,finalCaptionedPixelsApproved=False,wholeContinuousAnimationApproved=False,
    v1AndV2Preserved=True,newImageGitAdded=0)
assert not (R/'additive-mc-direct-review-v2.json').exists();save(R/'additive-mc-direct-review-v2.json',review)
e=read(R/'additive-mc-execution-v2.json');e.update(actualRenderComplete=True,
    completionEvidence='CUA tab59 Render enabled after rendering; actual886-frame output wholedecode0.',
    qaSessionId=62757,actualQaOuterExitCode=0,actualFfmpegExitCode=None)
save(R/'additive-mc-execution-v2.json',e)
e3=dict(recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),serverPid=77444,
    serverCreate='2026-10-11T02:34:49.455401+09:00',sessionId=70827,cwd='D:/Github/Video-Editing/motion-canvas',
    actualRenderStartedInCUA=True,rangeUiInclusive=[481,883],expectedSelectedFrames=403,
    actualRenderComplete=False,actualFfmpegExitCode=None,cpuThreads=2,gpuJobs=0,
    resource='projects/motion-sickness-games/production/revision-teaching-clarity-v1/additive-mc-render-resource-v3.json',
    outputDirectory='shared/output/unpublished-teaching-clarity-revision/motion/explanation-additions-v3',
    originalScenesRerendered=0,originalMemberRender=0,foreignProcessesChanged=0)
assert not (R/'additive-mc-execution-v3.json').exists();save(R/'additive-mc-execution-v3.json',e3)
print(json.dumps({'v2OpeningSamplesApproved':True,'v2GoalHeld':True,'v3TargetFrames':403}))
