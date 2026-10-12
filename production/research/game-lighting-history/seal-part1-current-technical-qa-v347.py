"""Seal only explicit final pixel/moving observations plus decoded-identical review reuse."""
from pathlib import Path
import importlib.util,json,sys,copy
spec=importlib.util.spec_from_file_location('m',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production';data=json.load(sys.stdin)
ep=P/'part1-texture-final-pixel-qa-execution-v346.json';ex=m.read(ep);assert ex['status']=='complete' and ex['exitCode']==0
bp=P/'part1-reviewed-pair-build-v345.json';pair=m.read(bp)
pp=P/'part1-final-input-plan-v309.json';plan=m.read(pp)
rp=P/'part1-texture-final-pixel-qa-request-v346.json';request=m.read(rp)
cmp=m.read(P/'part1-texture-current-decoded-comparison-v346.json')
assert ex['sourceSha256']==request['sourceSha256']==cmp['sourceSha256']==pair['captioned']['sha256']
assert ex['pairBuildSha256']==request['pairBuildSha256']==m.sha(bp)
assert request['allHistoricalQaFramesCovered'] and request['all335ActualAssCueBoundariesAnd94CutEdgesCovered']
obs={r['board']:r for r in data['boards']};assert set(obs)=={r['board'] for r in ex['boards']}
boards=[]
for b in ex['boards']:
    o=obs[b['board']];assert o['allConstituentFramesDirectlyRead'] and o['actualObservation'].strip() and not o['issues']
    assert m.sha(R/b['path'])==b['sha256'];boards.append(dict(b,**o,directlyRead=True,reviewedAt=m.stamp()))
fresh={o['id']:o for o in data['motion']}
needs={r['id'] for r in cmp['movingIntervals'] if r['needsFreshCurrentMovingReview']};assert set(fresh)==needs
for r in cmp['movingIntervals']:
    if r['id'] in fresh:
        o=fresh[r['id']];assert o['rangeSeconds']==r['rangeSeconds'] and o['fullSelectedIntervalActuallyPlayed'] and o['playbackRate']==1
        assert o['normalSpeedPixelsApproved'] and o['actualObservation'].strip() and not o['issues']
oldp=P/'part1-final-moving-direct-progress-v298.json';curp=P/'part1-current-moving-direct-progress-v325.json';roadp=P/'part1-road-final-direct-review-v337.json'
maps={'293':{r['id']:r for r in m.read(oldp)['records']},'323':{r['id']:r for r in m.read(curp)['records']},'333':{r['id']:r for r in m.read(roadp)['motion']}}
paths={'293':oldp,'323':curp,'333':roadp};motion=[]
for r in cmp['movingIntervals']:
    if r['id'] in fresh:
        motion.append(dict(fresh[r['id']],sourceSha256=ex['sourceSha256'],currentDirectlyPlayed=True));continue
    candidates=[(v,maps[v][r['id']]) for v in r['fullIntervalExactVersions'] if r['id'] in maps[v] and maps[v][r['id']]['normalSpeedPixelsApproved'] and not maps[v][r['id']]['issues']]
    assert candidates,('No complete approved moving evidence',r['id'],r['fullIntervalExactVersions'])
    v,o=candidates[0];assert o['rangeSeconds']==r['rangeSeconds'] and o['fullSelectedIntervalActuallyPlayed'] and o['playbackRate']==1
    assert o['actualObservation'].strip()
    motion.append(dict(o,currentSourceSha256=ex['sourceSha256'],entireCurrentDecodedIntervalIdentical=True,reviewVersion=v,directEvidence=dict(path=m.rel(paths[v]),sha256=m.sha(paths[v]))))
assert len(motion)==96 and len({r['id'] for r in motion})==96
rivalryp=P/'part1-rivalry-rate-aligned-direct-resolution-v338d.json';rv=m.read(rivalryp)
assert rv['allSixConstituentImagesRead'] and rv['wrongRate338b339Superseded'] and rv['failedV340Unused'] and rv['current333Unmodified']
texp=P/'part1-texture-native-input-direct-review-v344.json';tex=m.read(texp)
assert tex['allTwoSelectedForCurrentPrivateTechnicalPair'] and tex['all77PcmPreserved'] and tex['allCaptionsPreserved']
audioP=P/'part1-final-current-mixed-asr-direct-review-v312.json';audio=m.read(audioP);settings=m.read(P/'part1-final-mix-settings-v310.json')
assert audio['finalMixedAsrApproved'] and audio['allWholeAndIndependentTextsDirectlyCompared'] and audio['allWordEndingsAndTimestampsCompared']
assert audio['noRemainingContentFailures'] and audio['allObservedRecognitionConcernsResolved'] and len(audio['records'])==37
assert audio['currentMixSha256']==settings['wavSha256']==m.sha(R/settings['wav'])
semp=P/'part1-semantic-caption-review-v312.json';sem=m.read(semp)
assert sem['approved'] and sem['manualSemanticReview'] and sem['unchanged76ParagraphsExact'] and sem['paragraphCount']==77
assert sem['planSha256']==audio['planSha256']==pair['planSha256']==m.sha(pp)
for k in ['clean','captioned']:
    assert pair[k]['wholeDecode']['exitCode']==0 and pair[k]['frames']==89148 and pair[k]['allPresentationPtsContinuous']
    assert m.sha(R/pair[k]['path'])==pair[k]['sha256']
assert pair['identicalAacPayloadPtsDuration'] and abs(pair['ratioErrorFrames'])<=1
assert (pair['actualFrames'],pair['explanationFrames'],pair['bodyFrames'])==(53057,35371,88428)
records={r['id']:r for r in motion}
games=['Horizon Forbidden West','The Outer Worlds 2','Cyberpunk 2077','Fortnite']
gameIds=['horizon-detail-motion:native','outer-displayed-frames:native','cyber-light-reconstruction:native','cyber-surface-observation:native','fortnite-mobile-test:native','fortnite-normal-material:native']
assert all(records[i]['normalSpeedPixelsApproved'] for i in gameIds)
assert records['four-game-transfer-conclusion:model']['normalSpeedPixelsApproved']
assert records['original-branding']['normalSpeedPixelsApproved'] and records['original-membership']['normalSpeedPixelsApproved']
pixelp=P/'part1-current-final-pixel-review-direct-v347.json';motionp=P/'part1-current-final-moving-review-direct-v347.json';qap=P/'part1-final-qa-v347.json'
assert not pixelp.exists() and not motionp.exists() and not qap.exists()
pixel=dict(reviewedAt=m.stamp(),sourceSha256=ex['sourceSha256'],boards=boards,extraction=dict(path=m.rel(ep),sha256=m.sha(ep)),request=dict(path=m.rel(rp),sha256=m.sha(rp)),
    allChangedFinalBoardsDirectlyRead=True,allHistoricalQaFramesCovered=True,all335ActualAssCueBoundariesAnd94CutEdgesCovered=True,
    exactReviewedPixelReuse=request['exactReviewedPixelReuse'],historicalBoardReviews=request['historicalBoardReviews'],allFinalPixelsReviewed=True,
    knownHistoricalFailuresResolved=[dict(issue='VT conversion direction/dependency timing',evidence='part1-vt-direction-direct-review-v309.json'),dict(issue='Cyber promotional card',evidence='part1-current-board-direct-progress-v325.json'),dict(issue='Mobile loading/presenter/HQ-LQ timing',evidence='part1-current-board-direct-progress-v325.json'),dict(issue='Road green mask',evidence='part1-road-final-direct-review-v337.json'),dict(issue='Rivalry30fps fade',evidence=m.rel(rivalryp)),dict(issue='Texture Stats/Tile UI timing',evidence=m.rel(texp))],unresolvedIssues=[],newGitImages=0,humanWholeListening='pending')
moving=dict(reviewedAt=m.stamp(),sourceSha256=ex['sourceSha256'],records=motion,all96MovingIntervalsCovered=True,allFinalMovingPixelsReviewed=True,unresolvedIssues=[],
    decodedComparison=dict(path=m.rel(P/'part1-texture-current-decoded-comparison-v346.json'),sha256=m.sha(P/'part1-texture-current-decoded-comparison-v346.json')),rivalryResolution=dict(path=m.rel(rivalryp),sha256=m.sha(rivalryp)),newGitImages=0,humanWholeListening='pending')
m.save(pixelp,pixel);m.save(motionp,moving)
qa=dict(reviewedAt=m.stamp(),status='approved-current-technical-production-qa',slug=plan['slug'],planSha256=m.sha(pp),cleanSha256=pair['clean']['sha256'],captionedSha256=pair['captioned']['sha256'],
    reviewPair=dict(path=m.rel(bp),sha256=m.sha(bp)),pixels=dict(path=m.rel(pixelp),sha256=m.sha(pixelp)),motion=dict(path=m.rel(motionp),sha256=m.sha(motionp)),mixedAudio=dict(path=m.rel(audioP),sha256=m.sha(audioP)),semanticCaptions=dict(path=m.rel(semp),sha256=m.sha(semp)),
    fourGameTeachingReview=dict(reviewed=True,currentCaptionedSha256=pair['captioned']['sha256'],fourTitles=games,records=[records[i] for i in gameIds],transferConclusion=records['four-game-transfer-conclusion:model'],method='Complete normal-speed final footage/diagram review; current decoded-identical interval reuse only. Four different titles and meaningful differences; Rivalry2014 is additional engine demonstration, not a fifth game.',publicRightsApproved=False),
    finalFrames=89148,actualFrames=53057,explanationFrames=35371,bodyFrames=88428,ratioErrorFrames=pair['ratioErrorFrames'],loudness=pair['loudness'],
    identicalAacPayloadPtsDuration=True,twoWholeDecodesPassed=True,allPresentationPtsContinuous=True,allFinalPixelsReviewed=True,allMovingPixelsReviewed=True,captionTimingApproved=True,finalTimingApproved=True,bodyRatioApproved=True,qaApproved=True,
    originalIntroAnd10SecondMembershipPreserved=True,sourceAudio=0,loop=0,slowdown=0,newGitImages=0,collected=False,uploaded=False,humanWholeListening='pending',humanPronunciation='pending',publicRightsApproved=False,originalNimbusFileVerified=False,externalMediaBackup='pending',
    sourceFramePartitionScope='Texture stack uses each selected normalized60fps source position exactly once; original60000/1001fps is normalized at1x, without intentional loops or slowdown.')
m.save(qap,qa)
cp=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j.update(updatedAt=m.stamp(),episode04Part1LatestReality=dict(stage='current-technical-QA-approved-awaiting-four-file-collection-private-settings',qa=dict(path=m.rel(qap),sha256=m.sha(qap)),qaApproved=True,collected=False,uploaded=False),ownedActiveWork=dict(status='no-active-owned-media-worker',next='Create reviewed physical adapter, collect four files, privately upload captioned master and verify settings'))
m.save(cp,j)
print(json.dumps(dict(qaApproved=True,boards=len(boards),movingIntervals=96,uploaded=False)))
