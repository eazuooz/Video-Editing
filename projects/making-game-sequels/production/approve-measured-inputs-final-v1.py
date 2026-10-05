"""Freeze reviewed timing and inputs; final mixed/composite QA stays pending."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
WORK = BASE / 'measured-edit-v4'
FINAL = BASE / 'final-v1'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
def write(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
stamp = datetime.now(timezone.utc).isoformat()
assert not FINAL.exists(), 'Do not repeat an existing final preparation.'
edge = read(WORK / 'overhead-caption-edge-cropped-local-v6/execution.json')
assert edge['exitCode'] == 0 and len(edge['images']) == 14 and len(edge['sheets']) == 3
for r in edge['images'] + edge['sheets']:
    assert sha(ROOT / r['path']) == r['sha256']
edge_review = dict(schemaVersion=1, reviewedAt=stamp,
    images=[{**r, 'directlyRead': True} for r in edge['images']],
    boards=[{**r, 'directlyRead': True} for r in edge['sheets']],
    all14ImagesAnd3BoardsDirectlyRead=True, intendedCrop=[0,0,1472,828],
    observation='The presenter/hotbar are excluded by the intended crop. The overhead cue is absent on wall32174–32176 and visible from the first overhead32177; previous wall wording persists on32173 at the ASS centisecond edge. Overhead previews and adjustments stay above the fixed box. Sell/ReadyUp are not sale or combat evidence.',
    targetInputPixelsReviewed=True, finalCompositeApproved=False,
    historicalRawTrial='projects/making-game-sequels/production/overhead-caption-raw-edge-direct-review-v5.json',
    allRasterLocalOnly=True, newGitImages=0)
write(BASE / 'overhead-caption-cropped-direct-review-v6.json', edge_review)
plan = read(WORK / 'plan.json')
assert not plan['finalTimingApproved'] and plan['finalFrames'] == 35583
assert plan['actualFrames'] == 20918 and plan['explanationFrames'] == 13945
assert abs(plan['actualFrames'] - plan['bodyFrames']*.6) <= 1
assert plan['introFrames'] == 120 and plan['outroFrames'] == 600
compiled = read(WORK / 'native-review-v4/compiled.json')
white = read(WORK / 'timed-white-cues-local-v4/execution.json')
assert len(compiled['cuts']) == 85 and len(white['cuts']) == 7
assert read(BASE / 'timed-white-caption-direct-review-v4.json')['allImagesDirectlyRead']
assert read(BASE / 'wall-guide-target-direct-review-v4.json')['changedWordSourceAlignmentTechnicallySupported']
assert read(BASE / 'guided-joins-byte-preservation-review-v4.json')['allSixContextsSampleIdentical']
placed = read(WORK / 'inspection-pcm-index-v4.json')
assert len(placed['scenes']) == 13 and all(s['allComponentsSampleIdentical'] for s in placed['scenes'])
reviews = [
    WORK.parent/'measured-edit-v2/all-cue-framing-direct-review-v2.json',
    WORK.parent/'measured-edit-v2/targeted-framing-direct-review-v2.json',
    WORK.parent/'measured-edit-v2/caption-and-tail-direct-review-v3.json',
    BASE/'guided-native-caption-direct-review-v3.json',
    BASE/'wall-guide-target-direct-review-v4.json',
    BASE/'timed-white-caption-direct-review-v4.json',
    BASE/'overhead-caption-cropped-direct-review-v6.json',
    BASE/'guided-joins-byte-preservation-review-v4.json']
FINAL.mkdir()
intervals = {}
position = 120
original_white = 0
for s in plan['scenes']:
    assert s['startFrame'] == position
    assert sha(ROOT / s['audio']) == s['audioSha256']
    p = next(p for p in placed['scenes'] if p['scene'] == s['id'])
    assert p['samples'] == s['frames']*400 and sha(ROOT / p['audio']) == p['sha256']
    s.update(seconds=s['frames']/60, placedVoice=p['audio'], placedVoiceSha256=p['sha256'])
    for c in s['segments']:
        assert c['startFrame'] == position
        if c['classification'] == 'actual-existing-game':
            r = next(r for r in compiled['cuts'] if r['id'] == c['id'])
            assert sha(ROOT / r['video']) == r['sha256']
            a,z = c['sourceStartFrame'], c['sourceEndFrameExclusive']
            for old_a,old_z in intervals.setdefault(c['assetId'], []):
                assert a >= old_z or z <= old_a, c['id']
            intervals[c['assetId']].append((a,z))
            c.update(rawCompiledVideo=r['video'], rawCompiledSha256=r['sha256'],
                sourceFraming=r['composition']['proposedCrop'],
                video=rel(FINAL/'framed-native'/f"{c['id']}.mp4"), videoSha256=None,
                inputSamplePixelsReviewed=True, encodedFramingReviewed=False,
                finalApproved=False, captionPixelsApproved=False)
        else:
            r = next(r for r in white['cuts'] if r['id'] == c['id'])
            assert r['frames'] == c['frames'] and sha(ROOT/r['video']) == r['sha256']
            c.update(video=r['video'], videoSha256=r['sha256'],
                inputSamplePixelsReviewed=True, finalApproved=False, captionPixelsApproved=False)
            if s['id'] != '04': original_white += c['frames']
        position += c['frames']
    assert position == s['endFrameExclusive']
assert position+600 == plan['finalFrames'] and original_white >= plan['originalSixMinimumFrames']
plan.update(status='measured-input-timing-approved-final-mix-and-composite-QA-pending',
    createdAt=stamp, candidatePlan=rel(WORK/'plan.json'), candidatePlanSha256=sha(WORK/'plan.json'),
    finalTimingApproved=True, bodyRatioApproved=True,
    allInputSegmentCaptionPixelsReviewed=True, allFinalPixelsApproved=False,
    body60_40ErrorFrames=abs(plan['actualFrames']-plan['bodyFrames']*.6),
    currentPcmComponentsSeconds=554.584, allCurrentPcmSamplesPreserved=True,
    inputReviewEvidence=[dict(path=rel(p), sha256=sha(p)) for p in reviews],
    framingEncodingPending=True, finalMixBuilt=False, finalMixAsrApproved=False,
    sourceAudioStreams=0, selfCreatedGames=0, loop=0, slowdown=0,
    humanWholeListening='pending', humanPronunciation='pending')
write(FINAL/'plan.json', plan)
tracks=read(WORK/'caption-tracks-v5.json')
assert len(tracks['koRows']) == 308 and len(tracks['enRows']) == 173
write(FINAL/'caption-tracks.json', tracks)
for src,dst in [('captions.ko.candidate.v5.srt','captions.ko.srt'),
                ('captions.en.candidate.v5.srt','captions.en.srt'),
                ('captions.ko.candidate.v5.ass','captions.ko.ass')]:
    shutil.copyfile(WORK/src, FINAL/dst)
write(FINAL/'input-timing-approval.json', dict(schemaVersion=1, reviewedAt=stamp,
    planSha256=sha(FINAL/'plan.json'), candidatePlanSha256=sha(WORK/'plan.json'),
    actualFrames=20918, explanationFrames=13945, finalFrames=35583,
    ratioErrorFrames=.2, nativeCuts=85, whiteSegments=7,
    originalSixWhiteFrames=original_white, originalSixMinimumFrames=13350,
    currentPcmSeconds=554.584, original52AndEightNewParagraphsPreserved=True,
    longTailsGuided=True, nativeIntervalsUnique=True, sourceAudioStreams=0,
    classificationBasis='Visible existing-game placement/aiming/combat vs original white diagrams; normal-speed brief followthrough after matching guidance. No menu-only tests, loops, slowdowns or unrelated idle quota.',
    unresolvedHumanReview='Listening/pronunciation/rights/originalNimbus/truncatedhandles/externalbackup remain pending.',
    allInputSamplePixelsReviewed=True, finalEncodedCompositeReviewed=False,
    finalTimingApproved=True, bodyRatioApproved=True, finalMixBuilt=False,
    captionTracksSha256=sha(FINAL/'caption-tracks.json'), newGitImages=0))

# Synchronize all timing consumers; do not open the final-pixel factory gate.
m=read(PROJECT/'project.json')
m['status']='current13-guided60-final-input-timing-approved-mix-and-composite-pending'
e=m['editing'];e.update(actualGameplaySeconds=20918/60, actualExplanationSeconds=13945/60,
    actualGameplayShare=20918/34863, bodyRatioApproved=True,
    timingStatus='35583 frames/593.05s;85 unique native cuts and7 independent white segments,60:40 error0.2frame. Input samples reviewed; final composite/mix pending.')
e['exampleInterleaving']['reviewStatus']='Original/changed native cue trials and measured white literal cues directly reviewed; final encoded composite pending.'
e['measuredCandidate'].update(finalPlan=rel(FINAL/'plan.json'),status='input-timing-approved-final-media-pending',
    captionTracks=rel(FINAL/'caption-tracks.json'), finalTimingApproved=True,bodyRatioApproved=True,
    allInputPixelsReviewed=True, allFinalPixelsReviewed=False)
m['paths'].update(timeline=rel(FINAL/'plan.json'),candidateTimeline=rel(WORK/'plan.json'),
    captionsKo=rel(FINAL/'captions.ko.srt'),captionsEn=rel(FINAL/'captions.en.srt'),
    videoClean=rel(FINAL/'making-game-sequels.clean.review.mp4'),
    videoBurnedCaptions=rel(FINAL/'making-game-sequels.captioned.review.mp4'))
m['video']['durationSeconds']=593.05
m['audio']['mixStatus']='All554.584s current component PCM and six byte-identical unmixed contexts technically reviewed; final continuous approvedNimbus mix pending.'
write(PROJECT/'project.json',m)
for p in [PROJECT/'planning/chapter-plan.json',PROJECT/'sources/action-map.json']:
    d=read(p);d.update(updatedAt=stamp,currentFinalPlan=rel(FINAL/'plan.json'),
        finalTimingApproved=True,bodyRatioApproved=True,allInputSamplePixelsReviewed=True,
        finalCompositeApproved=False,finalMixBuilt=False)
    write(p,d)
mcpath=ROOT/'motion-canvas/src/projects/making-game-sequels/scene-plan.json';mc=read(mcpath)
mc.update(finalTimingApproved=True,bodyRatioApproved=True,finalPlan=rel(FINAL/'plan.json'),
    allFinalCaptionPixelsReviewed=False,allSourceSegmentPixelsReviewed=False,
    approvalScope='Measured input samples only; final-pixel production gate remains closed.')
write(mcpath,mc)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp)
i=next(i for i in q['items'] if i['slug']=='making-game-sequels')
i.update(stage=m['status'],updatedAt=stamp,nextAction='Build lossless current placed voice and approved continuousNimbus mix, frame85 native inputs with reviewed crops, assemble exact35583PTS frames, compare final mixed13chapters/joins and every final caption/cut, then QA/collect/private/Git.')
i['execution'].update(status='all-input-pixel-workers-closed',observedAt=stamp,pid=None,sessionId=None,
    alive=False,activeTasks=[],cpuProductionJobs=0,primaryCpuProductionJobs=0,
    gpuSynthesisJobs=0,renderJobs=0,uploads=0)
i['measuredEditCandidate'].update(finalPlan=rel(FINAL/'plan.json'),finalTimingApproved=True,
    bodyRatioApproved=True,allInputSamplePixelsReviewed=True,allFinalPixelsReviewed=False,
    koCues=308,enCues=173)
i['measuredWhiteReview']=dict(path=rel(BASE/'timed-white-caption-direct-review-v4.json'),images=173,boards=29,
    frames=13945,allDirectlyRead=True,finalCompositeApproved=False)
i['overheadCaptionReview']=dict(path=rel(BASE/'overhead-caption-cropped-direct-review-v6.json'),
    rawHistoricalTrial=rel(BASE/'overhead-caption-raw-edge-direct-review-v5.json'),
    correctedTargetImages=14,correctedBoards=3,allDirectlyRead=True,captionShiftFrames=4)
q['updatedAt']=stamp;write(qp,q)
proof=ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
for p in [BASE/'latest-checkpoint.json',proof/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','nextAction','execution','measuredEditCandidate','measuredWhiteReview','overheadCaptionReview']:d[k]=i[k]
    d.update(finalTimingApproved=True,bodyRatioApproved=True,finalPlan=rel(FINAL/'plan.json'),
        allInputSamplePixelsReviewed=True,allFinalPixelsApproved=False,finalMixBuilt=False,
        finalMixAsrApproved=False,rendered=False,qaApproved=False,collected=False,privateUploaded=False)
    write(p,d)
print(json.dumps(dict(frames=35583,seconds=593.05,ratioErrorFrames=.2,
    nativeCuts=85,whiteSegments=7,currentPcmSeconds=554.584,finalCompositeApproved=False)))
