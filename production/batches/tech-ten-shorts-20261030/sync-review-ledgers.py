"""Reflect verified current files in the ten ledgers without inventing human review."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('review_index', HERE/'build-review-overview.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def sync(write=False):
    _, overview = review.collect()
    changed = []
    for row in overview['projects']:
        if not row['generated']:
            continue
        path = Path(row['reviewLedger'])
        original = path.read_bytes()
        ledger = json.loads(original.decode('utf-8-sig'))
        final = Path(row['finalDirectory'])
        integrity = review.read(final/'integrity.json')
        if integrity.get('status') != 'pass' or not integrity.get('identicalAac') or not integrity.get('allCaptionTimesInsideVideo'):
            raise RuntimeError('Incomplete current integrity evidence: '+row['slug'])
        videos = {v['name']: v for v in integrity['outputs']}
        for name in ('clean', 'captioned'):
            data = videos[name]
            if not data.get('decoded') or not data.get('ptsRegular60') or data['sha256'] != review.sha(final/(name+'.mp4')):
                raise RuntimeError('Current integrity file binding differs: '+row['slug'])
        samples = ledger.get('sampleVisualReviews', [])
        exact_sample_pass = any(s.get('masterSHA256') == row['masterSha256'] and
                                s.get('status') == 'passed-sampled-visual-review' for s in samples)
        sc_sample = ledger.get('sampledVisualReview', {})
        exact_sample_pass |= (sc_sample.get('captionedSHA256') == row['masterSha256'] and
                              sc_sample.get('status') == 'pass-at-sampled-times')
        evidence = {
            'masterSHA256': row['masterSha256'], 'finalDirectory': str(final),
            'deliveryPath': str(final/'delivery.json'), 'deliverySHA256': review.sha(final/'delivery.json'),
            'integrityPath': str(final/'integrity.json'), 'integritySHA256': review.sha(final/'integrity.json'),
            'fourOutputsHashVerified': True, 'decodedBothVideos': True, 'regular60FpsPTS': True,
            'identicalAacBetweenCleanAndCaptioned': True, 'captionTimesInsideVideo': True,
            'matchingRecordedSampleVisualPass': bool(exact_sample_pass),
            'scope': 'Current file/integrity checks and existing exact-master sampled review records. No new listening, real-time playback, user approval or platform action.',
        }
        ledger['technicalChecks'] = 'pass'
        ledger['currentTechnicalReview'] = evidence
        # Human-approved records retain their status; only generated-file state
        # replaces the old pre-generation label for the still-unreviewed batch.
        if ledger.get('humanFinalReview') in (None, False, 'pending', 'not-reviewed'):
            ledger['status'] = ('local-files-generated-sampled-visual-pass' if exact_sample_pass else
                                'local-files-generated-sampled-review-pending')
        encoded = (json.dumps(ledger, ensure_ascii=False, indent=2)+'\n').encode('utf8')
        if write and encoded != original:
            if path.read_bytes() != original:
                raise RuntimeError('Ledger changed during verification; retry: '+row['slug'])
            path.write_bytes(encoded)
        changed.append({'slug':row['slug'], 'masterSHA256':row['masterSha256'],
                        'sampledVisualPass':bool(exact_sample_pass), 'changed':encoded != original})
    return {'written':write, 'verifiedFinalCount':len(changed), 'projects':changed}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    print(json.dumps(sync(parser.parse_args().write), ensure_ascii=False, indent=2))
