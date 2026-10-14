"""Seal the remaining51 actually viewed boards; inherit the prior36 exactly."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=V/'native-candidate-direct-review-v4.json';assert not out.exists()
partial_path=V/'native-candidate-partial-direct-review-v3.json';partial=read(partial_path)
closed=read(V/'native-candidate-extraction-execution-v2.session.json')
source_closed=read(V/'source-acquisition-execution-v2.session.json')
assert closed['actualOuterExitCode']==0 and closed['exactWorkerDead'] and closed['exactChildrenDead']
assert source_closed['actualOuterExitCode']==0 and source_closed['exactWorkerDead']
previous={g['group']:g for g in partial['groups']}
groups=[];new_boards=0;new_samples=0
for name in ['manor-placement-fine','manor-market-fine','storm-housing-fine','storm-mine-fine',
             'storm-fishing-fine','timber-early-settlement','timber-automation']:
    p=V/'native-candidate-pixels-v2'/name/'index.json';index=read(p)
    prior=previous.get(name);count=prior['viewedBoardCount'] if prior else 0
    if prior:
        assert sha(p)==prior['indexSha256']
        assert index['boards'][:count]==prior['viewedBoards']
    boards=index['boards'][count:]
    indices={n for b in boards for n in b['sampleIndices']}
    samples=[s for s in index['samples'] if s['index'] in indices]
    for item in boards+samples:assert sha(ROOT/item['path'])==item['sha256'],item['path']
    new_boards+=len(boards);new_samples+=len(samples)
    groups.append(dict(group=name,indexPath=p.relative_to(ROOT).as_posix(),indexSha256=sha(p),
        sourceSha256=index['localSourceSha256'],totalBoards=len(index['boards']),totalSamples=len(index['samples']),
        inheritedExactBoardCount=count,newlyDirectlyReadBoards=boards,
        allBoardsDirectlyRead=True,allBoundSampleFileHashesMatched=True,allFullResolutionFramesIndividuallyViewed=False))
assert (new_boards,new_samples)==(51,293)
details=[]
for group,numbers in [('manor-placement-fine',[22,23]),('manor-market-fine',[11,12,13]),
                      ('storm-fishing-fine',[8,30]),('timber-automation',[32,37,44])]:
    index=read(V/'native-candidate-pixels-v2'/group/'index.json')
    for n in numbers:
        sample=index['samples'][n-1];assert sample['index']==n and sha(ROOT/sample['path'])==sample['sha256']
        details.append(dict(group=group,**sample,fullResolutionDirectlyViewed=True))
findings=[
 'All499 new native points87boards are directly read.36boards206points inherit the exact partialV3; remaining51boards293points were read once. Previous371points64boards remain exact inherited research evidence, without re-extraction or repeated review.',
 'Manor:18.25..22.25 placement previews/foundations;22.75..28.25 separate worker carrying timber/construction. Carpenter camp People1/3 at28.75 becomes2/3 at29.25. Later Logging camp2/5 is a different panel. Exclude33.25fade/33.75black. Market80.25..84.75 dropdown selection,85.25Hide,85.75worker0/2 and86.25worker1/2.87.75..89.25 attractiveness is a separate edited shot; exclude89.75cinematic cart. Full-resolution readings confirm these fields. Disclose2022pre-alpha, no current-version capacity/economy or completed sale.',
 'Storm housing:2930.75menu;2931.25..2935.25moving/rotating Shelter previews and three foundations.2937.25..2957.75 PRESS SPACE paused explanation is not action quota.2958.25resume and builders/dust/roofs;2967.75one Shelter visibly complete, other sites incomplete.2968.75..2970.25HousingStatus shows homeless8/free0+6;2970.75paused. Do not claim all residents housed or all three complete.',
 'Storm Mine:2990.25..2991.75red placement preview;2992.25foundation;2992.75construction/recipes.2993.25Salttooltip. Mostly static subsequent UI is explanation, not idle quota.3008.25StoneNodeLARGE is a different gathering rule;3012.75tree tooltip unrelated.3014.75world pan/builders;3018.25Mine31percent construction. No finished extraction/storage output. Console injection windows are excluded.',
 'Storm Fishing:3080.25..3083.25moving hut ghost;3083.75foundation,3084.25selected Small Fishing Hut panel.3087.25GroundBait and3087.75PackOfCrops tooltips.3093.25..3094.25bait-mode tooltip states Never/Optional/OnlyWithBait;3094.75Optional field becomes readable after source presenter layout moves to lower-left. No observed mode change is asserted.3095..3104recipe/bait hovering;3105.25camera pans;3115.75panel closes. This window remains construction0percent, not completed fishing/output. Use placement action and readable rules for a branch comparison; static tooltip/diagram analysis is explanation. Do not use settlement pan as fishing result.',
 'Timber early:670..1082 contains Water/PowerWheel/WindTurbine previews, Lodge row/path746..758, cutting-area810, LumberMill862..874red invalid to green adjacent preview/foundation, Lodge occupancy894..914, Campfire1034..1038. Long ambient/night/panning is excluded. Wheel734/794 is construction,858built; later Lodge/Campfire is not the mill result. No plank output or completed power claim. Source simulation accelerates independently of video1x.',
 'Timber automation:2306..2310Zipline Pylon Connections;2366..2382Double Floodgate Off1m/On2m.2418..2426lever Off/Usages12,2430/2438signal field Badtide,2442copy-target prompt,2450..2454lever On. Full-resolution field is BADTIDE, correcting prior coarse Badside transcription. Native white zipline wires are not our automation annotation or an inferred signal graph.2478ContaminationSensor2 measurement0percent/threshold5percent/usages3/Off is only source UI observation.2498..2526night pan and2530crossfade to another map are excluded as a supposed lever result.2734unlockGeothermalEngine/2738preview/2742foundation;2802PowerShaft/2806Platform previews show no completed power output.',
 'All new subject/UI fields must stay clear of fixed bottom-center captions and existing presenter overlays. Hidden UI is not recovered by masking. Version-specific official previews are labelled; no world measurements, engine document tree, causality, safety result or blanket public/person rights approval is inferred.'
]
record=dict(recordedAt=datetime.now(timezone.utc).isoformat(),nativeActualSession=23194,nativeActualExit=0,
    nativeWorkerDead=True,nativeChildrenDead=True,additionalSourceActualSession=36150,additionalSourceExit=0,
    additionalSourceWorkerDead=True,additionalSourceDecodeComplete=True,
    inheritedPartial=dict(path=partial_path.relative_to(ROOT).as_posix(),sha256=sha(partial_path),boards=36,samples=206),
    newlyDirectlyReadBoards=51,newlyBoundSamples=293,totalNewDirectlyReadBoards=87,totalNewBoundSamples=499,
    priorComplete=dict(path='native-candidate-direct-review-v2.json',sha256=sha(V/'native-candidate-direct-review-v2.json'),boards=64,samples=371),
    totalCandidateResearchBoards=151,totalCandidateResearchPoints=870,completedViewsRepeated=0,
    groups=groups,newFullResolutionDirectReads=details,findings=findings,
    allFourGameTeachingApproved=False,finalVoiceAllocationApproved=False,allContinuousFramesApproved=False,
    humanWholeListeningApproved=False,publicRightsApproved=False,finalCaptionPixelsApproved=False,
    imagesLocalOnly=True,newTtsStarted=False,
    next='Choose exact meaningful cuts and causal independent KOEN/retained insertion mapping; preserve12PCM/60paragraphs/white/Nimbus/49inputs. No source acquisition/native extraction/completed board playback repeats. Fresh duplicate gate and resource before one new narration batch.')
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
cp_path=V/'latest-checkpoint.json';cp=read(cp_path)
cp.update(recordedAt=record['recordedAt'],stage='native-candidates-directly-reviewed;causal-script-and-cut-selection-next',
    additionalNativeDirectReview=out.relative_to(ROOT).as_posix(),additionalCandidateBoardsViewed=87,
    additionalCandidateSamplesViewed=499,activeOwnedWorkers=0,additionalSourceWorkerDead=True,
    additionalNativeWorkerDead=True,next=record['next'])
if 'actualAdditionalSourceWorker' in cp:cp['actualAdditionalSourceWorker']['alive']=False
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(newBoards=51,newPoints=293,totalV2Boards=87,totalV2Points=499,totalResearchPoints=870,
    sourceWorkerDead=True,nativeWorkerDead=True,newTtsStarted=False)))
