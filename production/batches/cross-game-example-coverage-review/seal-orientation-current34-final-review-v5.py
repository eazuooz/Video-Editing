"""Bind completed V5 pixel, playback, AAC and ratio evidence before promotion."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil
ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd = lambda p: json.loads(p.read_text('utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for buf in iter(lambda: f.read(1048576), b''): h.update(buf)
    return h.hexdigest()
def save(p, v):
    t = p.with_name(p.name + '.writing')
    t.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(t, p)
out = O / 'current34-final-technical-and-pixel-direct-review-v5.json'
assert not out.exists()
pairp = O / 'current34-final-pair-execution-v5.json'
pair = rd(pairp)
assert pair['workerDead'] and pair['actualOuterExitCode'] == 0 and pair['frames'] == 65917
pixelp = O / 'current34-pair-pixel-execution-v4.json'
pixel = rd(pixelp)
assert pixel['workerDead'] and pixel['actualOuterExitCode'] == 0
assert pixel['pairExecutionSha256'] == sha(pairp)
reviewp = O / 'current34-final-v5-pixels-partial-direct-review-v1.json'
review = rd(reviewp)
assert review['executionSha256'] == sha(pixelp)
assert review['allNewDirectPixelsRead'] and review['samplesDirectlyRead'] == 118 and review['boardsDirectlyRead'] == 30
x = pixel['results'][0]
assert len(x['samples']) == 3170 and len(x['inheritedExactPixelSamples']) == 3052
assert review['reviewedSamples'] == x['directReviewSamples'] and review['reviewedBoards'] == x['boards']
assert all(s['scene'] != '06a' and s['cachedPriorExactPixels'] for s in x['inheritedExactPixelSamples'])
for sample in x['samples']:
    assert sample['pts'] == sample['frame'] * 1500 and sha(ROOT/sample['path']) == sample['sha256']
for board in x['boards']: assert sha(ROOT/board['path']) == board['sha256']
normalp = O / 'current34-final-normal-direct-review-v5.json'
normal = rd(normalp)
assert normal['allNormalStartEndObserved'] and normal['normalPlaybackEndpointsReviewed']
assert normal['executionSha256'] == sha(pairp) and normal['captionedVideoSha256'] == pair['pair'][1]['sha256']
assert normal['start']['rate'] == normal['end']['rate'] == 1 and normal['end']['ended']
inputs = rd(ROOT/pair['assemblyInputs'])
assert sha(ROOT/pair['assemblyInputs']) == pair['assemblyInputsSha256']
assert inputs['changedPieceCount'] == pair['changedPieceCount'] == 1
assert inputs['reusedPreparedByteExactPieces'] == pair['reusedPreparedByteExactPieces'] == 36
for piece in pair['pieces']: assert sha(ROOT/piece['path']) == piece['sha256']
body = [p for p in pair['pieces'] if p['id'] not in ('intro','outro')]
counts = dict(bodyFrames=sum(p['frames'] for p in body),
              actualFrames=sum(p['actualFrames'] for p in body),
              explanationFrames=sum(p['explanationFrames'] for p in body))
assert counts == {k:pair['bodyMeasured'][k] for k in counts}
assert counts['bodyFrames'] == counts['actualFrames'] + counts['explanationFrames'] == 65197
error = counts['actualFrames'] - counts['bodyFrames'] * .4
assert abs(error) <= 1 and counts['actualFrames'] == 26078
assert pair['originalIntroFrames'] == 120 and pair['originalMemberFrames'] == 600
mixp = O / 'current34-mix-execution-v2.json'; mix = rd(mixp)
mixedp = O / 'current34-mixed-complete-direct-review-v1.json'; mixed = rd(mixedp)
assert mixed['currentMixedPlacementAndContentReviewPassed'] and mixed['all180ContextsDirectlyCompared'] and mixed['all34WholeTextsDirectlyCompared']
assert mixed['all34RawPcmPlacementsExact'] and mixed['all24BaselineDistributedPcmExact']
assert mixed['mixAacSha256'] == mix['mixAacSha256'] == sha(ROOT/mix['mixAac'])
assert mix['noBgm'] and mix['noSourceAudio'] and len(mix['placements']) == 76
for v in pair['pair']:
    assert sha(ROOT/v['path']) == v['sha256'] and v['wholeDecodeExitCode'] == 0
    assert v['allPts1500Verified'] and v['identicalReviewedWholeAacPackets']
    assert v['audioPacketProof'] == pair['currentAudioPacketProof']
    assert v['video']['width'] == 1920 and v['video']['height'] == 1080
    assert v['video']['time_base'] == '1/90000' and v['video']['avg_frame_rate'] == '60/1'
alignmentp = O / 'current34-caption-alignment-v1.json'; alignment = rd(alignmentp)
assert len(alignment['entries']) == 244 and alignment['retainedCueCount'] == 200 and alignment['newCueCount'] == 44
assert alignment['allOriginalCueTextWrapAndRelativeTimingPreserved'] and alignment['allNewCueTimingDirectlyReviewed']
selected = {p['frame'] for p in x['samples']}
for cue in alignment['entries']:
    first = int(cue['start']*60+.999999); last = int(cue['end']*60+.999999)-1
    assert {first,(first+last)//2,last} <= selected
off = 0
for piece in pair['pieces']:
    assert {max(0,off-1),off,off+piece['frames']-1,min(65916,off+piece['frames'])} <= selected
    off += piece['frames']
assert off == 65917
evidence = {}
for filename in ['current34-overview-direct-review-v5.json',
                 'current34-detailed-explanations-sampled-direct-review-v1.json',
                 'current34-detailed-explanations-normal-direct-review-v1.json',
                 'current34-mixed-detailed-direct-review-v1.json',
                 'current34-baseline-guides-direct-review-v1.json',
                 'current34-clearance-caption-pixels-partial-direct-review-v1.json',
                 'current34-caption-clearance-normal-direct-review-v2.json',
                 '07b-current-caption-clearance-normal-direct-review-v1.json',
                 'current34-06a-caption-clearance-sampled-direct-review-v1.json',
                 '06a-current-caption-clearance-normal-direct-review-v1.json',
                 'current34-final-v4-pixels-partial-direct-review-v1.json']:
    p = O/filename; evidence[filename] = dict(path=rel(p),sha256=sha(p))
assert rd(O/'current34-overview-direct-review-v5.json')['recognizableDetailedSubjectsReviewed']
assert rd(O/'current34-detailed-explanations-sampled-direct-review-v1.json')['recognizableDetailedSubjectsReviewed']
assert rd(O/'current34-clearance-caption-pixels-partial-direct-review-v1.json')['allSelectedPixelsDirectlyRead']
assert rd(O/'current34-06a-caption-clearance-sampled-direct-review-v1.json')['all32SamplesDirectlyRead']
protected = rd(O/'narration-07b-guide-repair-execution-v1.json')
for p in protected['protectedInputs']+protected['results']: assert sha(ROOT/p['path']) == p['sha256']
policy = ROOT/'shared/publishing/illustrative-subject-detail-policy.json'
policy_data = rd(policy)
assert policy_data['editableAssetsRequired'] and policy_data['movingPixelsAndCaptionClearanceReviewRequired']
assert policy_data['userReaffirmations'] and policy_data['newVisualApprovalRequiredForReplacedScenes']
record = dict(schemaVersion=1, reviewedAt=now(), pairExecution=rel(pairp), pairExecutionSha256=sha(pairp),
              pixelExecution=rel(pixelp), pixelExecutionSha256=sha(pixelp),
              directReview=rel(reviewp), directReviewSha256=sha(reviewp),
              normalReview=rel(normalp), normalReviewSha256=sha(normalp),
              all3170SelectedFinalSamplesReviewed=True,newDirectSamples=118,newDirectBoards=30,
              inheritedExactV4PixelSamples=3052,cachedPriorPixelsRedisplayed=False,
              all244CueFirstMidLastPixelsReviewed=True,all37PieceBoundariesReviewed=True,
              detailedPeopleAndObjectsReviewed=True,repairedCaptionClearanceReviewed=True,
              sourceReviewBindings=evidence,technicalQaPassed=True,finalRatioApproved=True,
              bodyMeasured=dict(**counts,ratioErrorFrames=error,contract='legacylecture40actual60explanation/noBGM'),
              mixedContentReview=rel(mixedp),mixedContentReviewSha256=sha(mixedp),
              current34PcmAnd76PlacementReviewPassed=True,identicalReviewedAacPackets=pair['currentAudioPacketProof'],
              normal1xMutedActualStartEndObserved=True,all79ProtectedInputsUnchanged=True,repairCandidateUnchanged=True,
              subjectPolicyAtAssemblySha256=inputs['subjectPolicySha256'],currentSubjectPolicySha256=sha(policy),
              subjectPolicyReaffirmation='Explicit repeated user directive recorded; substantive detailed-subject requirements retained.',
              claimScope='All planned final selected samples and current normal1x muted endpoints;not every intervening frame or continuous human listening.',
              allIntermediateFramesApproved=False,currentMixedAudioApproved=False,
              humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
              mainPromoted=False,fourOutputsCollected=False,newActualVideoId=None,settingsVerified=False,
              gitDelivered=False,scheduleReplacementVerified=False,obsoleteDeleted=False,
              newTts=0,newAsr=0,newMix=0,newImageGit=0,researchChanges=0)
save(out,record)
cp = rd(O/'latest-checkpoint.json')
cp.update(recordedAt=record['reviewedAt'],stage='current34-final-v5-bounded-pixels-technical-approved-delivery-pending',
          activeOwnedWorkers=0,ownedJob=None,allFinalPixelsApproved=True,finalPixelReview=rel(out),
          finalRatioApproved=True,qaApproved=True,detailedExplanationVisualApproved=True,
          currentMixedAudioApproved=False,next='Explicit root backup/promotion with78 others andcandidate preserved;collect4outputs;one privatecaptioned/settings;selectGit;actualStudio09slot savedreopen replacement.')
save(O/'latest-checkpoint.json',cp)
qp = B/'queue.json'; raw = qp.read_bytes(); q = rd(qp)
q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,
    allFinalPixelsApproved=True,finalRatioApproved=True,qaApproved=True,finalPixelReview=rel(out),next=cp['next'])
q['updatedAt']=record['reviewedAt'];assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(finalSelectedPixelsReviewed=3170,technicalQaPassed=True,ratioErrorFrames=error,review=rel(out),humanListeningApproved=False)))
