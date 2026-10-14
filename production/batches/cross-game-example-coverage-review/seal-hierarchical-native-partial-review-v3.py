"""Seal only36 newly read v2 boards; remaining51 must be read once later."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=V/'native-candidate-partial-direct-review-v3.json';assert not out.exists()
closed=read(V/'native-candidate-extraction-execution-v2.session.json')
assert closed['actualOuterExitCode']==0 and closed['exactWorkerDead'] and closed['exactChildrenDead']
groups=[]
for name,read_boards,read_samples in [('manor-placement-fine',6,32),('manor-market-fine',4,22),
    ('timber-early-settlement',18,104),('timber-automation',8,48)]:
    index_path=V/'native-candidate-pixels-v2'/name/'index.json';index=read(index_path)
    boards=index['boards'][:read_boards]
    indices={n for b in boards for n in b['sampleIndices']}
    assert len(indices)==read_samples
    shown_samples=[s for s in index['samples'] if s['index'] in indices]
    for item in boards+shown_samples:assert sha(ROOT/item['path'])==item['sha256'],item['path']
    groups.append(dict(group=name,indexPath=index_path.relative_to(ROOT).as_posix(),indexSha256=sha(index_path),
        sourceSha256=index['localSourceSha256'],viewedBoardCount=read_boards,viewedBoundSampleCount=read_samples,
        totalBoards=len(index['boards']),totalSamples=len(index['samples']),
        viewedBoards=boards,allShownSampleFileHashesMatched=True,allShownBoardsDirectlyRead=True,
        allFullResolutionFramesIndividuallyViewed=False,nextBoard=read_boards+1 if read_boards<len(index['boards']) else None))
record=dict(recordedAt=datetime.now(timezone.utc).isoformat(),nativeActualSession=23194,nativeActualExit=0,
    totalNew499Points=499,totalNewBoards=87,newBoardsViewed=36,newBoundSamplesViewed=206,
    remainingNewBoards=51,remainingNewSamples=293,previous371PointsAnd64BoardsRepeated=0,
    previousCompleteReview=dict(path='native-candidate-direct-review-v2.json',sha256=sha(V/'native-candidate-direct-review-v2.json')),
    groups=groups,findings=[
        'Manor18.25..22.25 building placement/blueprints;22.75..28.25 separate close worker carrying timber and construction. Carpenter camp People goes1/3 at28.75 to2/3 at29.25. Logging camp later is2/5, not another demonstrated allocation increase.33.25 fades and33.75 is black. Final cut must exclude fade/black and announce separate excerpts.',
        'Manor80.25..84.75 Market stall dropdown scrolls and selects Hide;85.25 closed dropdown shows Hide. Worker0/2 at85.75 becomes1/2 at86.25..86.75.87.75..89.25 zoomed market attractiveness tooltip is a separate shot;89.75 onward cinematic cart is excluded. Do not infer a completed sale or current price/capacity.',
        'Timber670..1082 native104samples/18boards all read. Visible candidate actions include Water Wheel/Power Wheel/Wind Turbine placement previews, Lodge row and path drawing746..758, cutting-area marks810, Lumber Mill placement862..874, Lodge occupancy panels894..914, Campfire placement1034..1038. Long ambient/night/day/panning sections do not fill quota. The ordinary source game uses accelerated simulation while video plays1x; no claim of1x simulation.',
        'TimberWaterWheel734/794 is still a construction site; later858 is visibly built. Lumber Mill red invalid placement864 becomes green adjacent preview866 and a foundation874. No completed plank output inferred from these views. Same-source Lodge or Campfire completion is not the mill result.',
        'Timber2306..2494 first48automation native samples/8boards read. Zipline Pylon Connections changes2306..2310; Double Floodgate OFF/ON heights are visible2366..2382. Lever Badside stateOff and usage12 at2418..2426, floodgate signal selection2430/2438, copy-configuration prompt2442, leverOn2450..2454. Contamination Sensor2 at2478..2494 shows measurement0percent/threshold5percent/usages3. These are source UI observations; exact between-frame inputs/final signal/flow causality await precise normal/native selection.',
        'Presenter overlays occupy both lower corners in the Timber stream. Source toolbar/tooltips may overlap these regions, so needed controls must be visible outside them. No hidden field recovered or blanket people-rights approval.'
    ],next='Only remaining v2 boards: timber-automation9..22(79samples14boards), storm-housing-fine1..14(82/14), storm-mine-fine1..10(58/10), storm-fishing-fine1..13(74/13). Then exact full-resolution UI/normal action cuts and current causal KOEN; do not read completed36boards/206points again.',
    allFourGameTeachingApproved=False,finalVoiceAllocationApproved=False,allContinuousFramesApproved=False,
    humanWholeListeningApproved=False,publicRightsApproved=False,newNarrationWritten=False,newTtsStarted=False,
    imagesLocalOnly=True)
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
cp_path=V/'latest-checkpoint.json';cp=read(cp_path)
cp.update(recordedAt=record['recordedAt'],additionalNativePartialReview=out.relative_to(ROOT).as_posix(),
    additionalCandidateBoardsViewed=36,additionalCandidateSamplesViewed=206,activeOwnedWorkers=0,next=record['next'])
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(newBoardsViewed=36,newPointsViewed=206,remainingBoards=51,remainingPoints=293,
    completedNativeOuterSession=23194,sourceAndNativeWorkersDead=True,newTtsStarted=False)))
