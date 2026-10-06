"""Reassign already selected native frames to the unchanged guide12 sentences.

Direct UI observations found native boundaries at F540/541 and F1238/1239.
This prepares a candidate, never approves its motion or final pixels.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import copy
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = datetime.now(timezone.utc).isoformat()
source_path = BASE / 'word-action-source-candidate-v4.json'
caption_path = BASE / 'word-caption-candidate-v3/captions.json'
assert sha(source_path) == 'c09c7b80680501208efc596f7d1c56a3da48621e9b14dc8cff4d515e190d776f'
assert sha(caption_path) == '588476e5471b153912138b1b07dc923a593e9686d722fd6c6042f26f732dc5e0'
source = read(source_path)
candidate = copy.deepcopy(source)
oldcuts = [c for p in source['pieces'] for c in p['selectedSourceCuts']]
old_by_id = {c['id']: c for c in oldcuts}
specs = {
    '12-cut02': [(480, 541), (1090, 1111)],
    '12-cut03': [(1239, 1362), (960, 1035)],
    '12-cut04': [(1035, 1090), (541, 562), (1111, 1152), (1164, 1239)],
}
connections = {
    '12-cut02': 'Two explicitly separate pink-room excerpts retain visible target aiming throughout the pink-room sentence; the native grey-room transition is moved to the later general direction comparison.',
    '12-cut03': 'The stairway sentence begins on the actual dark stairway/high window target, then shows a separate escalator stairway shot turning aim from a close low target to upper landing targets. No continuous route or exact key binding is claimed.',
    '12-cut04': 'The general height/direction invitation continues upper landing aim, then explicitly separate grey and pink corridor aiming/kick excerpts. The original native transitions remain visible; no single continuous location is claimed.',
}
new_ids = {}
for p in candidate['pieces']:
    replacement = []
    for c in p['selectedSourceCuts']:
        if c['id'] not in specs:
            replacement.append(c)
            continue
        cursor = c['startFrame']
        ids = []
        for index, (a, z) in enumerate(specs[c['id']], 1):
            row = copy.deepcopy(c)
            row['id'] = f"{c['id']}-v5-{index:02}"
            ids.append(row['id'])
            parents = [o for o in oldcuts if o['sourceVideoId'] == c['sourceVideoId']
                       and max(a, o['inFrameInclusive']) < min(z, o['outFrameExclusive'])]
            assert sum(min(z, o['outFrameExclusive']) - max(a, o['inFrameInclusive']) for o in parents) == z-a
            for field in ['previouslyBankedSourceFrames', 'newSourceBoundaryFrames']:
                row.pop(field, None)
            row.update(inFrameInclusive=a, outFrameExclusive=z, inSeconds=a/60,
                       outSeconds=z/60, sourceIntervalSeconds=(z-a)/60,
                       startFrame=cursor, endFrame=cursor+z-a, durationFrames=z-a,
                       bankCutIds=sorted({b for o in parents for b in o['bankCutIds']}),
                       previousCandidateCutIds=[o['id'] for o in parents],
                       previouslySelectedCandidateFrames=z-a,
                       sourceAndCaptionPixelsReviewed=False, completeMotionReviewed=False,
                       exactNewEdgesApproved=False, wordActionAlignmentApproved=False,
                       visibleActionConnection=connections[c['id']],
                       correction='Directly observed native location boundary; candidate needs current normal-speed playback and ordered pixel review.')
            replacement.append(row)
            cursor = row['endFrame']
        assert cursor == c['endFrame']
        new_ids[c['id']] = ids
    p['selectedSourceCuts'] = replacement

newcuts = [c for p in candidate['pieces'] for c in p['selectedSourceCuts']]
def frame_sets(cuts):
    result = defaultdict(set)
    for c in cuts:
        values = set(range(c['inFrameInclusive'], c['outFrameExclusive']))
        assert not result[c['sourceVideoId']].intersection(values), c['id']
        result[c['sourceVideoId']].update(values)
    return dict(result)
assert frame_sets(oldcuts) == frame_sets(newcuts)
assert len(newcuts) == 83
assert sum(c['durationFrames'] for c in newcuts) == source['actualFrameBudget'] == 13710
for oldp, newp in zip(source['pieces'], candidate['pieces']):
    assert {k:v for k,v in oldp.items() if k != 'selectedSourceCuts'} == {k:v for k,v in newp.items() if k != 'selectedSourceCuts'}
    selected = newp['selectedSourceCuts']
    if selected:
        assert all(a['endFrame'] == z['startFrame'] for a,z in zip(selected, selected[1:]))
for paragraph in candidate['paragraphs']:
    if paragraph['scene'] == '12':
        a, z = paragraph['startSeconds']*60, paragraph['endSeconds']*60
        paragraph['proposedSourceCutIds'] = [c['id'] for c in newcuts if c['pieceId'] == '12'
                                            and max(a,c['startFrame']) < min(z,c['endFrame'])]
        paragraph['visibleActionConnection'] = connections['12-cut02' if paragraph['paragraph']==1 else '12-cut03' if paragraph['paragraph']==2 else '12-cut04']
candidate.update(preparedAt=now, status='guide12-native-boundary-source-reassignment-candidate-only',
                 baselineCandidate=rel(source_path), baselineCandidateSha256=sha(source_path),
                 sourceCutCount=83, allUniqueSourceFrameIntervals=True,
                 finalTimingApproved=False, bodyRatioApproved=False, finalTimelineAdopted=False,
                 finalWordActionAlignment=False, allSourceMotionReviewed=False,
                 allSourceSegmentPixelsReviewed=False, allFinalCaptionPixelsReviewed=False,
                 finalMixedAsrApproved=False, newGitImages=0,
                 scope='Only the three guide12 source selections are split/reassigned. The union of every native source frame is exactly unchanged and unique. All PCM, captions, piece timing, white input and 23570-frame candidate duration are unchanged. New current source-motion/pixel review remains required.')
candidate['unresolved'] = [x for x in candidate['unresolved'] if x != 'Guide12 old trailer pink/sewer internal boundary']
candidate['unresolved'].append('Guide12 v5 reassignment requires all eight changed-cut normal-speed direct reviews and current sentence connections; all final gates remain false.')
dest = BASE / 'word-action-source-candidate-v5.json'
assert not dest.exists()
dest.write_text(json.dumps(candidate, ensure_ascii=False, indent=2)+'\n', 'utf-8')

old_review_path = PROOF / 'moving-source-direct-review-v4.json'
old_review = read(old_review_path)
assert old_review['sourceCandidateSha256'] == sha(source_path)
assert old_review['captionCandidateSha256'] == sha(caption_path)
new_by_id = {c['id']:c for c in newcuts}
carried = []
for row in old_review['cuts']:
    cut_id = row['cutId']
    if cut_id not in new_by_id:
        continue
    assert old_by_id[cut_id] == new_by_id[cut_id]
    assert row['decision'] == 'aligned'
    item = copy.deepcopy(row)
    item['unchangedCutEvidence'] = dict(previousReview=rel(old_review_path), previousReviewSha256=sha(old_review_path),
                                      previousSourceCandidateSha256=sha(source_path),
                                      canonicalCutSha256=hashlib.sha256(json.dumps(new_by_id[cut_id],ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
                                      completeCutObjectByteEquivalent=True, pieceAudioAndTimingUnchanged=True,
                                      allCaptionBytesUnchanged=True, inheritedObservationOnly=True)
    carried.append(item)
assert len(carried) == 26
proof = dict(schemaVersion=1, slug='familiar-game-rules', preparedAt=now,
             previousCandidate=rel(source_path), previousCandidateSha256=sha(source_path),
             currentCandidate=rel(dest), currentCandidateSha256=sha(dest),
             captionCandidate=rel(caption_path), captionCandidateSha256=sha(caption_path),
             nativeBoundaryDirectObservations=[dict(source='FVkDc6u_4GQ',lastPinkFrame=540,firstGreyFrame=541),
                                               dict(source='FVkDc6u_4GQ',lastPinkHallFrame=1238,firstDarkStairFrame=1239)],
             selectedPinkReplacementDirectEdges=[1090,1110], reassignedCutIds=new_ids,
             sourceFrameUnionByteEquivalent=True, nativeSourceFramesAdded=0, nativeSourceFramesRemoved=0,
             sourceFrameReuse=0, sourceAudio=False, loops=False, slowdown=False,
             allPieceAudioAndTimingUnchanged=True, allCaptionsByteUnchanged=True,
             originalExplanationFramesUnchanged=True, whiteInputUnchanged=True,
             candidateFinalFrames=23570, candidateActualFrames=13710,candidateExplanationFrames=9140,
             candidateBodyRatio=[60,40], candidateRoundingErrorFrames=0,
             currentMotionReviewRequired=True, allChangedCutPixelsReviewed=False,
             finalTimelineAdopted=False, allFinalCaptionPixelsReviewed=False, newGitImages=0,newGitMedia=0,
             humanListeningPronunciation='pending',
             scope='Exact source-only reassignment candidate after direct CUA boundary observations; no new media, speech or caption synthesis and no final approval.')
proof_path = PROOF / 'native-guide12-boundary-reassignment-v5.json'
assert not proof_path.exists()
proof_path.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
record = copy.deepcopy(old_review)
record.update(sourceCandidate=rel(dest), sourceCandidateSha256=sha(dest),
              previousReview=rel(old_review_path), previousReviewSha256=sha(old_review_path),
              expectedCuts=83, cuts=carried, directlyReviewedCuts=len(carried),
              allSourceMotionReviewed=False, allWordActionAligned=False, updatedAt=now,
              browserServer=None, unchangedCutInheritanceAudit=rel(proof_path),
              unchangedCutInheritanceAuditSha256=sha(proof_path),
              scope='Current v5 source-motion review. Exactly26 previous directly read observations are carried only for complete identical cut objects, piece PCM/timing and caption bytes. Eight reassigned cuts and all previously unread cuts require current direct playback/gallery review; final pixels and human listening remain pending.')
record_path = PROOF / 'moving-source-direct-review-v5.json'
assert not record_path.exists()
record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(currentCandidateSha256=sha(dest), cuts=83, inheritedUnchangedDirectReviews=26,
                      changedCuts=8, allSourceFramesUnchanged=True, currentMotionApproval=False)))
