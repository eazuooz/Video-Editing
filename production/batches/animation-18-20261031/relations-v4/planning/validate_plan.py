"""Validate authored relationship-map contracts; this is not rendered-video QA."""
from pathlib import Path
import hashlib, json, re

P = Path(__file__).resolve().parent
R = P.parents[4]
B = R / 'production/batches/animation-18-20261031'
plan = json.loads((P / 'relations-plan.json').read_text('utf-8'))
layout = json.loads((P / 'opening-layout.json').read_text('utf-8'))
assert [x['id'] for x in plan['episodes']] == [f'A{x:02}' for x in range(1, 19)]
rows = []
for ep in plan['episodes']:
    text = (B / 'review-20261108' / (ep['id'] + '-comparison.txt')).read_text('utf-8-sig').split('\nCURRENT ', 1)[1]
    found = re.search(r'\[(\d\d):(\d\d):(\d\d),(\d{3})\] ' + re.escape(ep['insertion']['beforeSentence']), text)
    assert found, ep['id']
    at = sum(int(v) * mult for v, mult in zip(found.groups(), [3600, 60, 1, .001]))
    assert abs(at - ep['insertion']['atSeconds']) < .0011
    assert 4 <= len(ep['sentences']) <= 7
    bids = {b['id'] for b in ep['beats']}
    assert len(bids) == len(ep['beats'])
    for s in ep['sentences']:
        assert s['ko'].strip() and s['en'].strip() and s['beat'] in bids
        assert not any(term in s['ko'] for term in ('원영상', '사쿠라이', '원작자', '마사히로'))
    for beat in ep['beats']:
        ids = {n['id'] for n in beat['nodes']}
        assert len(ids) == len(beat['nodes'])
        assert all(x in ids for x in beat['focus'])
        assert all(e['from'] in ids and e['to'] in ids for e in beat['edges'])
    opening = next(x for x in layout['episodes'] if x['id'] == ep['id'])
    for move in opening['moves']:
        p0, p1 = move['originalPictureRangeFrames']
        a0, a1 = move['originalMusicOnlyRangeSamples']
        assert p1 > p0 and a1 > a0 and a1 - a0 == (p1 - p0) * 800
        assert move['newInsertedPassCount'] == 3 or move['thirdPassFromUnchangedBodyAtAnchor']
    rows.append({
        'id': ep['id'],
        'sentences': len(ep['sentences']),
        'beatCount': len(ep['beats']),
        'exactCurrentSentenceBoundaryVerified': True,
        'nodeEdgeAndSentenceBeatReferencesValid': True,
        'sourcePath': ep['source']['path'],
        'sourceClassification': ep['source']['classification'],
        'headingFreeKoreanReadThrough': 'Reviewed for continuous independent explanation and return to the original next sentence.',
        'preMapRepeatSetsToRelocate': len(opening['moves']),
        'bodyVisualRepairCount': len(ep['bodyVisualRepairs']),
        'renderedMotionAndAudioQA': 'pending; no listening or encoded-video review claimed by this planning pass',
    })
report = {
    'schemaVersion': 1,
    'status': 'planning-checks-passed',
    'planSha256': hashlib.sha256((P / 'relations-plan.json').read_bytes()).hexdigest(),
    'openingLayoutSha256': hashlib.sha256((P / 'opening-layout.json').read_bytes()).hexdigest(),
    'coverage': 'A01–A18 source/current comparison text, existing review audit, and pacing-v3 event mappings. Independently phrased added maps preserve the existing source-order body; no full reference narration is reproduced.',
    'criticalDistinctions': [
        'A03 visual idle/lead-in/attack/follow-through versus active collision; hit-stop is conditional on contact; control recovery is a separate track.',
        'A06 three attack time rows; A08 persistent cumulative changes to the same pose; A14 two real clip tracks, overlap, playhead and independent weight.',
        'All pre-map complete repeated explanation sets are relocated behind the map per opening-layout.json; baseline brief previews may remain.',
    ],
    'episodes': rows,
}
(P / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('Planning checks passed:', len(rows), 'episodes;', sum(x['sentences'] for x in rows), 'bilingual sentence pairs.')
