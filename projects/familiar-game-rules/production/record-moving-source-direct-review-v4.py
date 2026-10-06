"""Record explicit direct source-motion observations; never infer review from playback alone."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
SOURCE = ROOT / 'projects/familiar-game-rules/production/word-action-source-candidate-v4.json'
CAPTION = ROOT / 'projects/familiar-game-rules/production/word-caption-candidate-v3/captions.json'
OUT = PROOF / 'moving-source-direct-review-v4.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cut', required=True)
    parser.add_argument('--pages', type=int, required=True)
    parser.add_argument('--notes', required=True)
    parser.add_argument('--decision', choices=['aligned', 'needs-correction'], required=True)
    parser.add_argument('--source', default=SOURCE.name)
    parser.add_argument('--output', default=OUT.name)
    args = parser.parse_args()
    source_path = SOURCE.parent / args.source
    out_path = PROOF / args.output
    assert source_path.parent == SOURCE.parent and out_path.parent == PROOF
    source = json.loads(source_path.read_text(encoding='utf-8-sig'))
    cuts = [c for p in source['pieces'] for c in p.get('selectedSourceCuts', [])]
    cut = next(c for c in cuts if c['id'] == args.cut)
    server = json.loads((PROOF / 'browser-word-action-review-server-v1.json').read_text(encoding='utf-8-sig'))
    assert server['sourceCandidateSha256'] == sha(source_path)
    assert server['captionCandidateSha256'] == sha(CAPTION)
    event_path = PROOF / 'browser-word-action-playback-events-v1.jsonl'
    event_bytes = event_path.read_bytes()
    events, malformed = [], []
    for number, line in enumerate(event_bytes.decode('utf-8').splitlines(), 1):
        try:
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError('Event is not an object')
            events.append(value)
        except (json.JSONDecodeError, ValueError) as error:
            malformed.append(dict(lineNumber=number, raw=line, error=str(error)))
    if malformed:
        # Keep the source log intact. A damaged fragment cannot count as evidence.
        audit_path = PROOF / 'browser-playback-log-malformed-lines-v1.json'
        audit = dict(source=str(event_path.relative_to(ROOT)).replace('\\', '/'),
                     sourceSha256=hashlib.sha256(event_bytes).hexdigest(),
                     observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     malformedLines=malformed, sourceLogPreserved=True,
                     malformedEventsUsedForApproval=False)
        audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    ends = [e for e in events if e.get('cutId') == args.cut and e.get('kind') == 'play-end'
            and e.get('mode') == 'candidate' and e.get('completeSourceIntervalTraversed') is True
            and e['serverObservedAt'] >= server['startedAt']]
    assert ends, 'No current full candidate playback observation'
    event = ends[-1]
    assert abs(event['sourceFrame'] - (cut['outFrameExclusive'] - 1)) <= 1
    assert args.pages == (event['samples'] + 5) // 6, 'Explicitly inspect every gallery page before recording'
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if out_path.exists():
        record = json.loads(out_path.read_text(encoding='utf-8-sig'))
        assert record['sourceCandidateSha256'] == sha(source_path)
        assert record['captionCandidateSha256'] == sha(CAPTION)
        if record.get('browserServer') is None:
            record['browserServer'] = server
    else:
        record = dict(schemaVersion=1, slug='familiar-game-rules', sourceCandidate=str(source_path.relative_to(ROOT)).replace('\\', '/'),
                      sourceCandidateSha256=sha(source_path), captionCandidateSha256=sha(CAPTION),
                      browserServer=server, expectedCuts=len(cuts), cuts=[],
                      scope='Direct visual review of full normal-speed browser source playback and every ordered observation gallery; decoded input trials are separate. Human audio listening remains pending.',
                      allFinalCaptionPixelsReviewed=False, finalTimelineAdopted=False,
                      humanListeningPronunciation='pending', newGitImages=0, newGitMedia=0)
    assert args.cut not in [c['cutId'] for c in record['cuts']], 'Already recorded; use explicit correction evidence for a changed verdict'
    record['cuts'].append(dict(cutId=args.cut, sourceVideoId=cut['sourceVideoId'], sourceSha256=cut['sourceSha256'],
                              inFrameInclusive=cut['inFrameInclusive'], outFrameExclusive=cut['outFrameExclusive'],
                              startFrame=cut['startFrame'], endFrame=cut['endFrame'], crop=cut['sourceCrop'],
                              directVisualReviewed=True, normalSpeedPlaybackEvent=event, observationPagesDirectlyRead=args.pages,
                              notes=args.notes, decision=args.decision, reviewedAt=now))
    record['directlyReviewedCuts'] = len(record['cuts'])
    record['allSourceMotionReviewed'] = len(record['cuts']) == len(cuts)
    record['allWordActionAligned'] = record['allSourceMotionReviewed'] and all(c['decision'] == 'aligned' for c in record['cuts'])
    record['updatedAt'] = now
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(cut=args.cut, decision=args.decision, reviewed=record['directlyReviewedCuts'], expected=len(cuts), allWordActionAligned=record['allWordActionAligned'])))

if __name__ == '__main__':
    main()
