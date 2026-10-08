"""Use directly inspected additional real gameplay for the measured lecture."""
from pathlib import Path
import json, hashlib, datetime, shutil
from production_control import require_current_authorization

ROOT = Path(__file__).resolve().parents[3]
slug = 'game-math-planes-barycentric'
require_current_authorization(slug, 'measured real-footage coverage')
base = ROOT / 'projects' / slug
lesson_path = Path(__file__).parent / 'lessons' / (slug + '.json')
cuts_path = base / 'sources/gameplay-cuts.json'

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def write(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
lesson, cuts = read(lesson_path), read(cuts_path)
author_path = Path(__file__).parent / 'author-geometry-planes.py'
author = author_path.read_text(encoding='utf-8')
changes = [
    ('05', [(96, 126), (404, 423), (515, 521)], '[(96,122),(404,423)]', '[(96,126),(404,423),(515,521)]',
     ['planes-extra-noita-20261008/window-01-1.jpg', 'planes-extra-noita-20261008/window-02-1.jpg', 'planes-extra-noita-tail-20261008/window-01-1.jpg'],
     'Character crossing reference heights and moving along bounded layered terrain. Retain96–122/404–423; add122–126 and515–521. Exclude the513-second explosion from the additional cut.'),
    ('08', [(1320, 1374)], '[(1320,1366)]', '[(1320,1374)]',
     ['planes-extra-uncle-20261008/window-01-1.jpg'],
     'First-person grappling toward cyan surface symbols with changing camera direction. Retain1320–1366; add1366–1374. The visible marker motivates a defined triangle, not a claim about internal mesh topology.'),
]
backup = ROOT / 'shared/output' / slug / 'footage-extension-20261008'
backup.mkdir(exist_ok=True)
assert not (backup / lesson_path.name).exists(), 'Do not apply the measured extension twice'
for p in (lesson_path, cuts_path, author_path):
    shutil.copy2(p, backup / p.name)
proof = []
for sid, intervals, old, new, sheets, visible in changes:
    scene = next(s for s in lesson['scenes'] if s['id'] == sid)
    cut = next(s for s in cuts['cuts'] if s['scene'] == sid)
    source = cuts['sources'][cut['sourceId']]
    assert all(any(a <= start < end <= b for a, b in source['approvedIntervals']) for start, end in intervals)
    evidence = []
    for sheet in sheets:
        p = ROOT / 'shared/output/game-math-part2-full-series/inspection' / sheet
        assert p.exists()
        evidence.append(dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), directPixelReview='passed'))
    assert author.count(old) == 1
    author = author.replace(old, new)
    segments = [dict(**{'in': a}, maxSeconds=b-a) for a, b in intervals]
    for target in (scene, cut):
        target['sourceSegments'] = segments
        target['maxSeconds'] = sum(b-a for a, b in intervals)
    cut['additionalMeasuredFootageReview'] = dict(visibleAction=visible, sheets=evidence, sourceAudioUsed=False, sourceSpeed=1, freezeOrLoop=False)
    proof.append(dict(scene=sid, sourceId=cut['sourceId'], sourceSegments=segments, maxSeconds=cut['maxSeconds'], visibleAction=visible, sheets=evidence))
write(lesson_path, lesson)
write(cuts_path, cuts)
author_path.write_text(author, encoding='utf-8')
review_path = base / 'production/script-review.json'
review = read(review_path)
review.update(lessonSha256=sha(lesson_path), actualCapacitySeconds=sum(s.get('maxSeconds', 0) for s in lesson['scenes']),
              additionalFootageReview=proof, narrationUnchangedByFootageExtension=True)
write(review_path, review)
write(base / 'production/measured-footage-extension.json', dict(
    status='direct-extra-pixels-reviewed-before-retiming', reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    purpose='Keep complete narration and exactly40% real gameplay without freezing, slowing or looping.',
    preservedBaseline=backup.relative_to(ROOT).as_posix(), scenes=proof, publicGameIpReview='pending', humanListening='pending'))
print('Reviewed capacities05=55s /08=54s; retained all narration and original source segments.')
