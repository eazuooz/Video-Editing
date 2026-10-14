"""Seal actual endpoint observations for five new precise source intervals."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=V/'candidate-normal-playback-observation-v2.json';assert not out.exists()
previous=V/'candidate-normal-playback-observation-v1.json';prior=read(previous)
observations=[]
detail=[]
manor_index=read(V/'native-candidate-pixels-v1/manor-overview/index.json')
for number,expected_pts in [(16,30),(42,82)]:
    sample=manor_index['samples'][number-1]
    assert sample['actualDecodedSourcePtsSeconds']==expected_pts and sha(ROOT/sample['path'])==sample['sha256']
    detail.append(dict(**sample,fullResolutionDirectlyViewed=True,wholeMovingSceneApproved=False))
for name,sid,a,b in [('storm-housing','qaK2FWQB7DE',2930,2970),('storm-mine','qaK2FWQB7DE',2990,3018),
    ('storm-fishing','qaK2FWQB7DE',3080,3116),('manor-placement','gVkhhrLARU8',18,34),('manor-market','gVkhhrLARU8',80,91)]:
    pair=[]
    for point in ['start','end']:
        p=V/'ui-proof-v1'/(name+'-normal-'+point+'-v1.ax.txt')
        text=p.read_text('utf8')
        records=[]
        for line in text.splitlines():
            if 'text {"source"' in line:
                records.append(json.loads(line[line.index('{'):]))
        assert records, p
        state=records[-1]
        assert sid in state['source'] and state['intervalStart']==a and state['intervalEnd']==b
        assert state['muted'] and state['playbackRate']==1 and state['videoWidth']==1920 and state['videoHeight']==1080
        if point=='start':assert not state['paused'] and a<=state['currentTime']<a+1
        else:assert state['paused'] and b<=state['currentTime']<b+1
        pair.append(dict(point=point,evidence=p.relative_to(ROOT).as_posix(),sha256=sha(p),state=state))
    observations.append(dict(name=name,sourceId=sid,actualCuaTab=127,requestedInterval=[a,b],observedEndpoints=pair,
        originalSourceVersionPreserved=True,allContinuousFramesDirectlyViewed=False,
        preciselyNarratedFinalCutApproved=False,sourceNormalRateOnly=True))
proof=dict(recordedAt=datetime.now(timezone.utc).isoformat(),previousReview=dict(path=previous.relative_to(ROOT).as_posix(),sha256=sha(previous)),
    previousWholeCandidatePlaybackRepeated=False,actualNewPreciseIntervalCount=5,newNormalObservations=observations,
    newRepresentativeFullResolutionReads=detail,
    timberbornAdditionalStreamObservations=dict(videoId='6TNjosDftog',actualCuaTab=124,
        firstObservedStartSeconds=2307.991951,firstPausedEndSeconds=2571.413646,
        firstPausedEndReplacesCoarse2551Estimate=True,continuedFromSamePausedPosition=True,
        nextObservedSeconds=2601.333961,secondPausedEndSeconds=2611.651166,
        muted=True,playbackRate=1,width=1920,height=1080,
        nativeExactActionSelectionPending=True,allContinuousFramesDirectlyViewed=False),
    findings=[
        'Storm housing sequence includes a source-game pause for a housing tooltip; actual placement and later construction completion must be allocated separately from this paused explanation.',
        'Storm Mine endpoint3018 has construction progress31percent and selected recipes/storage panel. It does not prove finished extraction or collected output.',
        'Storm Fishing endpoint3116 has panned back to the settlement. Final fishing cut must end while its own placement/configuration remains visible; do not imply this separate housing view is its completed result.',
        'Manor2022 pre-alpha placement, worker-management and market dropdown are independently edited shots, not one continuous completed build. Requested endpoint34.218714s is a source black transition, so the final worker-control cut must end before that fade. Source1x is not proof that all source-game time/simulation rates are1x.',
        'Two newly read full-resolution native images verify Carpenter camp People worker slots2/3 at30s and Market stall SELLING dropdown/worker slots0/2 at82s. These are readable specific UI observations; no current-version capacity/price or completed sale is inferred. The screenshot result does not approve all between-frame pixels.',
        'Manor requested market endpoint91.191252s is a distinct cinematic horse/cart shot, rather than the market configuration result. Select the actual dropdown/worker-change window before this source cut; do not narrate the cart as a demonstrated completed sale or use unrelated cinematic time for quota.'
    ],fullFourGameTeachingApproved=False,humanWholeListeningApproved=False,publicRightsApproved=False,
    finalCaptionPixelsApproved=False,noFinalGameTimeAllocatedYet=True,
    next='Directly read only newly planned fine-action pixels and additional Timberborn native points after the single current source/extraction closes. Then choose exact useful input/result intervals and write causal narration; no repeated whole-source playback.')
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(normalIntervalsSealed=5,previousWholePlaybackRepeated=False,allContinuousFramesApproved=False)))
