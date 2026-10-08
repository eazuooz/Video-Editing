"""Clarify ambiguous spoken values without changing Geometry2's mathematics."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
from production_control import require_current_authorization

ROOT = Path(__file__).resolve().parents[3]
SLUG = 'game-math-planes-barycentric'
require_current_authorization(SLUG, 'spoken value clarification')
lease = ROOT / 'shared/output/GPU_HANDOFF.json'
if lease.exists() and json.loads(lease.read_text(encoding='utf-8-sig')).get('project') == SLUG:
    raise SystemExit('Wait for the current full TTS handoff to finish before changing its script.')
base = ROOT / 'projects' / SLUG
lesson_path = Path(__file__).parent / 'lessons' / (SLUG + '.json')
author_path = Path(__file__).parent / 'author-geometry-planes.py'
lesson = json.loads(lesson_path.read_text(encoding='utf-8'))
ko_path, en_path = [base / 'script' / ('narration.' + lang + '.json') for lang in ('ko', 'en')]
scripts = [json.loads(p.read_text(encoding='utf-8')) for p in (ko_path, en_path)]
author = author_path.read_text(encoding='utf-8')
edits = [
    ('03', '법선이 영, 일, 영이고 디가 이라면 와이가 이인 모든 점이 평면 위에 있습니다.',
     '법선의 세 성분은 영, 일, 영입니다. 상수 디의 값은 이입니다. 이때 와이가 이인 모든 점이 평면 위에 있습니다.',
     'The normal has components zero, one, zero. Constant d equals two. Every point with y equal to two lies on this plane.'),
    ('04', '법선이 영, 이, 영이고 디가 사인 평면도 와이가 이인 평면입니다. 법선 길이는 이입니다.',
     '법선의 세 성분은 영, 이, 영입니다. 상수 디의 값은 사입니다. 이 평면에서도 와이가 이이고, 법선 길이는 이입니다.',
     'The normal has components zero, two, zero. Constant d equals four. This is still the y-equals-two plane, and the normal length is two.'),
    ('06', '삼각형이나 발판의 끝을 넘어가면 유한 표면의 가장 가까운 점은 다시 검사해야 합니다.',
     '삼각형이나 발판의 끝을 넘어가면, 가장자리가 있는 표면의 최근접점은 별도로 검사해야 합니다.',
     'This projection finds the nearest point on an infinite plane. Beyond a triangle or platform edge, the nearest point on that bounded surface needs a separate test.'),
    ('12', '절반을 취하면 삼각형 넓이가 되고, 이 예제에서는 십이를 이로 나눕니다.',
     '절반을 취하면 삼각형 넓이가 됩니다. 이 예제의 평행사변형 넓이는 십이입니다. 이를 이로 나누면 삼각형 넓이 육을 얻습니다.',
     'The cross-product length is the parallelogram area. Half gives the triangle area. Here the parallelogram area is twelve, and dividing by two gives a triangle area of six.'),
    ('14', '꼭짓점 하나를 향해 다가가면 그 꼭짓점의 가중치는 일을 향합니다.',
     '꼭짓점 하나에 가까워질수록, 그 꼭짓점의 가중치는 숫자 일에 가까워집니다.',
     'Approaching a vertex makes its weight approach the number one. A point on its opposite edge has zero weight for it.'),
    ('15', '음수 가중치를 무조건 잘못된 계산으로 버리면 바깥 위치 정보를 잃습니다.',
     '음수 가중치를 무조건 잘못된 계산으로 버리면, 바깥 위치를 설명하는 정보를 버리게 됩니다.',
     'Position has length units; weights are dimensionless ratios. Rejecting every negative weight discards information describing valid outside positions.'),
    ('22', '법선 영, 이, 영과 디 사인 평면에서 점 사, 오, 마이너스 삼까지의 거리는 얼마일까요?',
     '법선의 세 성분은 영, 이, 영이고, 상수 디의 값은 사입니다. 이 평면에서 점 사, 오, 마이너스 삼까지의 거리는 얼마일까요?',
     'First problem: the normal has components zero, two, zero, and constant d equals four. What is the distance from this plane to point four, five, minus three?'),
]
records = []
for sid, old, new, new_en in edits:
    scene = next(s for s in lesson['scenes'] if s['id'] == sid)
    indexes = [i for i, text in enumerate(scene['ko']) if old in text]
    assert len(indexes) == 1, (sid, 'Expected one original sentence; do not apply twice.')
    index = indexes[0]
    old_ko, old_en = scene['ko'][index], scene['en'][index]
    new_ko = old_ko.replace(old, new)
    assert author.count(old) == 1 and author.count(old_en) == 1
    author = author.replace(old, new).replace(old_en, new_en)
    scene['ko'][index], scene['en'][index] = new_ko, new_en
    for lang, replacement in zip(scripts, (new_ko, new_en)):
        target = next(s for s in lang['scenes'] if s['id'] == sid)
        assert target['lines'][index] in (old_ko, old_en)
        target['lines'][index] = replacement
    records.append(dict(scene=sid, line=index + 1, beforeKo=old_ko, afterKo=new_ko,
                        beforeEn=old_en, afterEn=new_en,
                        reason='Separate constants and area operands into complete statements; retain signed distance, projection and 12/2=6.'))

stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup = ROOT / 'shared/output' / SLUG / 'spoken-clarity' / stamp
backup.mkdir(parents=True)
for p in (lesson_path, author_path, ko_path, en_path):
    shutil.copy2(p, backup / p.name)

def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

write(lesson_path, lesson)
author_path.write_text(author, encoding='utf-8')
for path, script in zip((ko_path, en_path), scripts):
    write(path, script)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
review_path = base / 'production/script-review.json'
review = json.loads(review_path.read_text(encoding='utf-8'))
review.update(status='reviewed-before-current-value-clarification-TTS', reviewedAt=stamp,
              lessonSha256=sha(lesson_path), koChars=sum(len(x) for s in lesson['scenes'] for x in s['ko']),
              spokenValueClarification=records, mathematicalClaimsUnchanged=True)
write(review_path, review)
write(base / 'production/spoken-value-clarification.json', dict(status='script-reviewed-voice-pending',
      edits=records, preservedBaseline=backup.relative_to(ROOT).as_posix(),
      lessonSha256=sha(lesson_path), koScriptSha256=sha(ko_path), enScriptSha256=sha(en_path),
      currentVoiceReview='pending', humanListening='pending'))
print('Clarified ' + '/'.join(x[0] for x in edits) + '; preserved source baseline; current voice/read-back still required.')
