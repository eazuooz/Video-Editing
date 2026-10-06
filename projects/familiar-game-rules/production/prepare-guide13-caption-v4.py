"""Correct one six-frame anticipatory caption; preserve the completed source review."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = datetime.now(timezone.utc).isoformat()
old_path = BASE / 'word-caption-candidate-v3/captions.json'
source_path = BASE / 'word-action-source-candidate-v6.json'
review_path = PROOF / 'moving-source-direct-review-v6.json'
old, source, review = read(old_path), read(source_path), read(review_path)
assert review['sourceCandidateSha256'] == sha(source_path)
assert review['captionCandidateSha256'] == sha(old_path)
assert review['directlyReviewedCuts'] == 85 and review['allSourceMotionReviewed'] and review['allWordActionAligned']
caption = copy.deepcopy(old)
row = caption['ko'][62]
assert row['index'] == 63 and row['ko'] == '방에서는 총을 겨눕니다.'
assert abs(row['startSeconds'] * 60 - 5871) < 1e-6
original_row = copy.deepcopy(row)
row.update(startSeconds=5877/60, displayDelaySeconds=0.1,
           sourceSpeechStartPreserved=True, cueDisplayBoundaryBasis='First native held-gun target frame816 at output5877; CUA boundary264/269/816 directly read.')
assert caption['en'] == old['en'] and caption['paragraphs'] == old['paragraphs']
assert all(a == b for a,b in zip(caption['ko'],old['ko']) if a['index'] != 63)
assert row['sourceSpeechStart'] == 1.4 and row['endSeconds'] == original_row['endSeconds']
caption.update(preparedAt=now, status='single-six-frame-display-start-correction-input-review-pending',
               baselineCaption=rel(old_path), baselineCaptionSha256=sha(old_path), audioChanged=False,
               sourceActionAlignmentApproved=False, allCuePixelsReviewed=False, finalTimingApproved=False,
               finalTimelineAdopted=False,
               scope='Only KO cue63 display start5871->5877; actual speech anchor remains1.4s. English paragraph covers both kick and aim and stays byte-identical. No PCM, scene, chapter, ending or runtime retiming.')
caption['corrections'].append(dict(cue=63, oldDisplayStartFrame=5871, newDisplayStartFrame=5877,
                                  sourceSpeechUnchanged=True, humanListeningPronunciation='pending', encodedInputPixelsPending=True))
target = BASE / 'word-caption-candidate-v4'
assert not target.exists()
target.mkdir()
def stamp(t):
    n = round(t*1000)
    return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
(target/'candidate.ko.srt').write_text('\n\n'.join(f'{q["index"]}\n{stamp(q["startSeconds"])} --> {stamp(q["endSeconds"])}\n{q["ko"]}' for q in caption['ko'])+'\n','utf-8')
(target/'candidate.en.srt').write_bytes((old_path.parent/'candidate.en.srt').read_bytes())
(target/'captions.json').write_text(json.dumps(caption,ensure_ascii=False,indent=2)+'\n','utf-8')
proof = dict(schemaVersion=1,createdAt=now,sourceCandidate=rel(source_path),sourceCandidateSha256=sha(source_path),
             sourceReview=rel(review_path),sourceReviewSha256=sha(review_path),sourceCutsReviewed=85,
             oldCaption=rel(old_path),oldCaptionSha256=sha(old_path),currentCaption=rel(target/'captions.json'),
             currentCaptionSha256=sha(target/'captions.json'),originalCue=original_row,currentCue=row,
             currentDirectBoundaryObservation=[dict(sourceFrame=264,outputFrame=5871,action='corridor after door kick; no aimed gun'),
               dict(sourceFrame=269,outputFrame=5876,action='corridor; no aimed gun'),
               dict(sourceFrame=816,outputFrame=5877,action='held gun toward red-clothed room target')],
             correctedEarlierClaim='Earlier notes incorrectly said cue63 begins5877/one-frame transition; actual v3 start5871 anticipates by6frames. Preserve earlier reviews as historical observations.',
             additionalMetadataCorrections=[dict(cutId='10-part3-cut01',actualAction='Vertical-shaft wall jumps and upper red-target aiming, then cage approach; no train-crate sequence.'),
               dict(cutId='10-part3-cut02',actualAction='Train-crate climb with upper black-clad targets; not the same vertical room interval.')],
             allOtherCaptionObjectsUnchanged=True,englishSrtByteIdentical=sha(target/'candidate.en.srt')==sha(old_path.parent/'candidate.en.srt'),
             sourceIntervalsAudioAndTimelineUnchanged=True,allFinalCaptionPixelsReviewed=False,encodedInputPixelsPending=True,newGitImages=0,newGitMedia=0)
(PROOF/'guide13-six-frame-caption-boundary-correction-v4.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(ko=253,en=118,oldFrame=5871,newFrame=5877,captionSha256=sha(target/'captions.json'),finalApproved=False)))
