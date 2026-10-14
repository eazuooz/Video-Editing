"""Seal only the31 actually viewed candidate boards; never infer final teaching approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=V/'native-candidate-partial-direct-review-v1.json'
assert not out.exists(), 'Continue the remaining boards without repeating completed ones'
groups=[]
for name,expected_boards,expected_samples in [('manor-overview',22,127),('timber-short',9,54)]:
    index_path=V/'native-candidate-pixels-v1'/name/'index.json'
    index=read(index_path)
    assert len(index['boards'])==expected_boards and len(index['samples'])==expected_samples
    for item in index['boards']+index['samples']:
        assert sha(ROOT/item['path'])==item['sha256'],item['path']
    groups.append(dict(group=name,indexPath=index_path.relative_to(ROOT).as_posix(),indexSha256=sha(index_path),
        sourceSha256=index['localSourceSha256'],boardCount=expected_boards,sampleCount=expected_samples,
        allBoardsDirectlyViewed=True,allBoundSampleFileHashesMatched=True,
        allFullResolutionSourceFramesIndividuallyViewed=False,finalCutApproval=False,
        viewedBoards=[dict(path=b['path'],sha256=b['sha256'],sampleIndices=b['sampleIndices']) for b in index['boards']]))
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),viewedBoardCount=31,
    reviewedBoundNativeSampleCount=181,totalPlannedBoards=64,totalPlannedSamples=371,groups=groups,
    findings=[
        'ManorLords0..252s all127planned native samples on22boards read. The official2022 pre-alpha preview visibly distinguishes building placement, carpenter/logging worker slots, market item/worker selection, taxation controls, diplomacy, recruitment and military equipment. Candidate useful windows are18..33 and82..89; precise in/out, full-resolution UI and action alignment remain pending. Do not present the2022 controls as a verified current version.',
        'ManorLords46..50 construction/season changes are condensed presentation; do not count them as normal-action quota or claim an exact uninterrupted upgrade result. Static region/tech/diplomacy/catalogue screens are explanation-led. Unrelated military/cinematic/promotional sections are not a substitute for document-organization teaching.',
        'Timberborn0..53s all54planned native samples on9boards read. Indicator lights, pumps/silos/gates, storage examples and terrain/water changes are visible. But the short promotional edit hides all control/configuration UI, includes fast weather/water transitions and independent shots, and has no demonstrated user input binding. Keep this candidate held for complete fourth-game/action teaching; no quota allocation, no threshold/world-state or causal guarantee inferred.',
        'An outline in this lesson remains our written design proposal. Building hierarchy, game world positions, input signal wiring and time order are not automatically the same structure. Do not infer a developer document or engine hierarchy from the game footage.'
    ],next='Continue only storm-conditions boards1..7 and storm-building-ui boards1..26 after current actual extraction exit/closure. Find a clearer official Timberborn configuration-and-action source before its narration. Completed31boards/source downloads/whole decodes and recorded normal playback are not repeated.',
    fourGameTeachingApproved=False,allSourceIntermediateFramesApproved=False,newNarrationWritten=False,
    humanWholeListeningApproved=False,publicRightsApproved=False,imagesLocalOnly=True)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
playback=dict(recordedAt=proof['reviewedAt'],candidateOnly=True,normalObservations=[
    dict(game='Manor Lords',sourceId='gVkhhrLARU8',actualCuaTab=127,
        actualObservedStartSeconds=23.002772,actualObservedMidSeconds=51.440594,actualObservedPausedEndSeconds=156.119003,
        requestedStartSeconds=23,requestedEndSeconds=156,playbackRate=1,muted=True,width=1920,height=1080,
        startEvidence='ui-proof-v1/manor-candidate-normal-start-v1.ax.txt',endEvidence='ui-proof-v1/manor-candidate-normal-end-v1.ax.txt',
        allContinuousFramesDirectlyViewed=False,finalCutPlaybackApproval=False),
    dict(game='Timberborn',sourceId='Jsc7003gSu0',actualCuaTab=124,
        actualInitialUiSeconds=0,actualObservedMidSeconds=[9.630248,29.574129],actualObservedEndSeconds=53.781,
        ended=True,playbackRate=1,muted=True,width=1920,height=1080,
        endEvidence='ui-proof-v1/timberborn-candidate-normal-end-v1.ax.txt',
        sourceFileVideoDurationMayDifferFromYouTubeAvMux=True,
        allContinuousFramesDirectlyViewed=False,finalCutPlaybackApproval=False)],
    wholeHumanListeningApproved=False,finalCaptionPixelsApproved=False,newPlaybackRequiredOnlyForNewSelectedIntervals=True)
(V/'candidate-normal-playback-observation-v1.json').write_text(json.dumps(playback,ensure_ascii=False,indent=2)+'\n','utf-8')
cp_path=V/'latest-checkpoint.json';cp=read(cp_path)
cp.update(recordedAt=proof['reviewedAt'],nativeCandidatePartialReview=out.relative_to(ROOT).as_posix(),
    candidateBoardsViewed=31,candidateNativeSamplesBound=181,timberbornShortHeld=True,fourGameTeachingApproved=False,
    next=proof['next'])
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(boardsViewed=31,nativeSamples=181,timberbornShortHeld=True,narrationWritten=False)))
