"""Bind the eight already-inspected encoded clips; never manufacture review."""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parents[1]
U = P / 'production/local/unity-v5'


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    build = read(U / 'build.json')
    sources = {}
    for entry in read(P / 'production/unity-workflow-v5-cues.json')['entries']:
        ident = entry['id']
        directory = U / ident / 'render'
        video = directory / 'unity.mp4'
        digest = sha(video)
        receipt_path = directory / 'producer-receipt.json'
        receipt = read(receipt_path)
        evidence = directory / 'review' / digest[:12] / 'motion-review.json'
        review = read(evidence)
        success = read(directory / 'render-success.json')
        assert success['status'] == 'complete'
        assert success['fingerprint'] == receipt['fingerprint'] == build['fingerprint']
        assert success['completed'] == receipt['actualFrames'] == entry['frames']
        assert receipt['sha256'] == review['sha256'] == digest
        assert review['fingerprint'] == build['fingerprint']
        assert review.get('passed') is True and review.get('motionReviewed') is True
        assert review.get('allContactPagesInspected') is True and review.get('reviewedFrameCount', 0) > 0
        assert not review.get('defects') and not review.get('blockingFindings')
        assert review.get('humanViewing') is False
        sources[ident] = {
            'sha256': digest,
            'motionReviewed': True,
            'evidence': evidence.relative_to(P).as_posix(),
            'evidenceSha256': sha(evidence),
            'producerReceipt': receipt_path.relative_to(P).as_posix(),
            'producerReceiptSha256': sha(receipt_path),
        }
    assert len(sources) == 8
    result = {
        'fingerprint': build['fingerprint'],
        'sources': sources,
        'scope': 'Actual encoded cue-sequence samples inspected by the named reviewers; not continuous full playback or human approval. Final integrated captioned master has separate review.',
        'humanViewing': False,
        'humanListening': False,
    }
    target = U / 'source-review.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'sources': len(sources), 'path': str(target), 'sha256': sha(target)}))


if __name__ == '__main__':
    main()
