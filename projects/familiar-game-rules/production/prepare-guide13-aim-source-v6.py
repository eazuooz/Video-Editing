"""Prepare source-only correction of the directly rejected guide13 aiming cut."""
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
previous_path = BASE / 'word-action-source-candidate-v5.json'
caption_path = BASE / 'word-caption-candidate-v3/captions.json'
review_path = PROOF / 'moving-source-direct-review-v5.json'
assert sha(previous_path) == 'da41dbf3b3922bb0a4a7850c3fb1855c0a5c5e0fac0864e17d8447f8f08f1f84'
assert sha(caption_path) == '588476e5471b153912138b1b07dc923a593e9686d722fd6c6042f26f732dc5e0'
source, review = read(previous_path), read(review_path)
assert review['sourceCandidateSha256'] == sha(previous_path)
rejected = next(r for r in review['cuts'] if r['cutId'] == '13-cut02')
assert rejected['decision'] == 'needs-correction'
candidate = copy.deepcopy(source)
oldcuts = [c for p in source['pieces'] for c in p['selectedSourceCuts']]
old_by_id = {c['id']: c for c in oldcuts}
old = old_by_id['13-cut02']
specs = [(816, 870), (1591, 1680), (753, 790)]
connection = ('Separate purple-room held-gun target aiming, then an explicitly separate tiled-room '
              'held-gun/near-target excerpt, then a door kick. The unchanged narration compares aiming '
              'with a kick and asks separating direction from the new action. Exact keys, a continuous '
              'route and game implementation are not inferred. Current normal-speed review remains required.')
for p in candidate['pieces']:
    replaced = []
    for c in p['selectedSourceCuts']:
        if c['id'] != '13-cut02':
            replaced.append(c)
            continue
        cursor = c['startFrame']
        for index, (a, z) in enumerate(specs, 1):
            row = copy.deepcopy(c)
            for field in ['previouslyBankedSourceFrames', 'newSourceBoundaryFrames']:
                row.pop(field, None)
            row.update(id=f'13-cut02-v6-{index:02}', inFrameInclusive=a, outFrameExclusive=z,
                       inSeconds=a/60, outSeconds=z/60, sourceIntervalSeconds=(z-a)/60,
                       startFrame=cursor, endFrame=cursor+z-a, durationFrames=z-a,
                       previousCandidateCutIds=['13-cut02'] if index != 2 else [],
                       bankCutIds=c['bankCutIds'] if index != 2 else [],
                       newlySelectedSourceFrames=z-a if index == 2 else 0,
                       previouslySelectedCandidateFrames=0 if index == 2 else z-a,
                       visibleActionConnection=connection,
                       sourceAndCaptionPixelsReviewed=False, completeMotionReviewed=False,
                       exactNewEdgesApproved=False, wordActionAlignmentApproved=False,
                       correction='Rejected v5 floating-debris cue63 replaced by active aiming; candidate only.')
            replaced.append(row)
            cursor = row['endFrame']
        assert cursor == c['endFrame'] == 6057
    p['selectedSourceCuts'] = replaced
newcuts = [c for p in candidate['pieces'] for c in p['selectedSourceCuts']]
def frames(cuts):
    result = defaultdict(set)
    for c in cuts:
        selected = set(range(c['inFrameInclusive'], c['outFrameExclusive']))
        assert not result[c['sourceVideoId']].intersection(selected), c['id']
        result[c['sourceVideoId']].update(selected)
    return dict(result)
oldframes, newframes = frames(oldcuts), frames(newcuts)
added = sorted(newframes['FVkDc6u_4GQ'] - oldframes['FVkDc6u_4GQ'])
removed = sorted(oldframes['FVkDc6u_4GQ'] - newframes['FVkDc6u_4GQ'])
assert added == list(range(1591, 1680))
assert removed == list(range(690, 753)) + list(range(790, 816))
assert all(oldframes[k] == newframes[k] for k in oldframes if k != 'FVkDc6u_4GQ')
assert len(newcuts) == 85
assert sum(c['durationFrames'] for c in newcuts) == source['actualFrameBudget'] == 13710
for oldp, newp in zip(source['pieces'], candidate['pieces']):
    assert {k:v for k,v in oldp.items() if k != 'selectedSourceCuts'} == {k:v for k,v in newp.items() if k != 'selectedSourceCuts'}
    cuts = newp['selectedSourceCuts']
    assert all(a['endFrame'] == z['startFrame'] for a,z in zip(cuts,cuts[1:]))
for p in candidate['paragraphs']:
    if p['scene'] == '13':
        a,z = p['startSeconds']*60,p['endSeconds']*60
        p['proposedSourceCutIds'] = [c['id'] for c in newcuts if c['pieceId'] == '13' and max(a,c['startFrame']) < min(z,c['endFrame'])]
        p['visibleActionConnection'] = connection
candidate.update(preparedAt=now, status='guide13-aim-source-correction-candidate-only',
                 baselineCandidate=rel(previous_path), baselineCandidateSha256=sha(previous_path),
                 sourceCutCount=85, allUniqueSourceFrameIntervals=True,
                 finalTimingApproved=False, bodyRatioApproved=False, finalTimelineAdopted=False,
                 finalWordActionAlignment=False, allSourceMotionReviewed=False,
                 allSourceSegmentPixelsReviewed=False, allFinalCaptionPixelsReviewed=False,
                 finalMixedAsrApproved=False, newGitImages=0,
                 scope='Only guide13-cut02 is replaced/split into three normal-speed excerpts. Exactly89 new native frames replace89 rejected frames. All other complete cuts, PCM, caption bytes, piece timing, white input and23570 total remain unchanged; current review required.')
candidate['unresolved'].append('Guide13 v6 source correction requires direct playback/gallery of all3changed cuts; new89native frames require encoded input/final pixel checks.')
dest = BASE / 'word-action-source-candidate-v6.json'
assert not dest.exists()
dest.write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n','utf-8')
new_by_id = {c['id']:c for c in newcuts}
carried = []
for row in review['cuts']:
    cut_id = row['cutId']
    if cut_id not in new_by_id:
        continue
    assert old_by_id[cut_id] == new_by_id[cut_id]
    assert row['decision'] == 'aligned'
    item = copy.deepcopy(row)
    item.setdefault('priorInheritanceHistory', []).append(item.get('unchangedCutEvidence'))
    item['unchangedCutEvidence'] = dict(previousReview=rel(review_path),previousReviewSha256=sha(review_path),
                                      previousSourceCandidateSha256=sha(previous_path),
                                      canonicalCutSha256=hashlib.sha256(json.dumps(new_by_id[cut_id],ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
                                      completeCutObjectByteEquivalent=True,pieceAudioAndTimingUnchanged=True,
                                      allCaptionBytesUnchanged=True,inheritedObservationOnly=True)
    carried.append(item)
assert len(carried) == 47
proof = dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=now,
             previousCandidate=rel(previous_path),previousCandidateSha256=sha(previous_path),
             currentCandidate=rel(dest),currentCandidateSha256=sha(dest),
             captionCandidateSha256=sha(caption_path),rejectedDirectReview=rel(review_path),
             rejectedDirectReviewSha256=sha(review_path),rejectedCut=rejected,
             newCuts=[c for c in newcuts if c['id'].startswith('13-cut02-v6-')],
             directlyObservedFreeFrameResearch=[1591,1630,1679],
             freeFrameScope='CUA native main-stage observation only; no normal-speed/current-caption approval inferred.',
             nativeSourceFramesAdded=added,nativeSourceFramesRemoved=removed,
             sourceFrameReuse=0,sourceAudio=False,loops=False,slowdown=False,
             allOtherCutObjectsUnchanged=True,allPieceAudioAndTimingUnchanged=True,
             allCaptionsByteUnchanged=True,whiteInputUnchanged=True,
             candidateFinalFrames=23570,candidateActualFrames=13710,candidateExplanationFrames=9140,
             candidateBodyRatio=[60,40],candidateRoundingErrorFrames=0,
             inheritedAlignedReviews=47,currentChangedCutMotionReviewRequired=True,
             newNativeEncodedInputPixelReviewRequired=True,allChangedCutPixelsReviewed=False,
             finalTimelineAdopted=False,allFinalCaptionPixelsReviewed=False,newGitImages=0,newGitMedia=0,
             humanListeningPronunciation='pending')
proof_path = PROOF / 'native-guide13-aim-reassignment-v6.json'
assert not proof_path.exists()
proof_path.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
record = copy.deepcopy(review)
record.update(sourceCandidate=rel(dest),sourceCandidateSha256=sha(dest),
              previousReview=rel(review_path),previousReviewSha256=sha(review_path),
              expectedCuts=85,cuts=carried,directlyReviewedCuts=47,
              allSourceMotionReviewed=False,allWordActionAligned=False,updatedAt=now,
              browserServer=None,unchangedCutInheritanceAudit=rel(proof_path),
              unchangedCutInheritanceAuditSha256=sha(proof_path),
              scope='Exactly47 aligned whole-identical cut observations carried from v5;3changed cuts and35unread cuts require current direct playback/gallery. Rejected v5cut preserved separately; final/human gates pending.')
out = PROOF / 'moving-source-direct-review-v6.json'
assert not out.exists()
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
candidates_path = ROOT/'projects/familiar-game-rules/sources/game-candidates.json'
games = read(candidates_path)
games['guide13SourceCorrectionV6'] = dict(candidate=rel(dest),candidateSha256=sha(dest),
    evidence=rel(proof_path),evidenceSha256=sha(proof_path),sourceVideoId='FVkDc6u_4GQ',
    newIntervalFrames=[1591,1680],newIntervalSeconds=[1591/60,1680/60],
    oldSelectedFramesRemoved=[[690,753],[790,816]],insertionPiece='13',
    visibleAction='Native main-stage research at1591/1630 shows held gun toward nearby tiled-room targets;1679shows closekick with gun. Full current1x interval remains pending.',
    diagramConnection='Separate target-direction function from new kick action; no exact key binding inferred.',
    recentUse='Exact new89frames are disjoint from all85current selected native intervals; same official trailer is already used in this project.',
    rights='Existing SHA/full-decode0/official Devolver source and personalized commercial permission retained; final public rights pending.',
    sourceAudio=False,loops=False,editorSlowdown=False,exactCutApproval=False,
    normalSpeedReviewPending=True,newNativeEncodedPixelsPending=True,reviewedAt=now)
games['updatedAt'] = now
candidates_path.write_text(json.dumps(games,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(cuts=85,currentCandidateSha256=sha(dest),inheritedAligned=47,newNativeFrames=89,removedNativeFrames=89,finalApproved=False)))
