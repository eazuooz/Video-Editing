"""Preserve forty KO/EN paragraphs and prepare fixed-caption editorial units."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = O / 'current34-caption-editorial-groups-v1.json'
assert not out.exists()
plan = read(O / 'current34-measured-timing-plan-v1.json')
ko = {s['id']: s['lines'] for s in read(O / 'script/current34-combined-v1.ko.json')['scenes']}
en = {s['id']: s['lines'] for s in read(O / 'script/current34-combined-v1.en.json')['scenes']}
splits = {
    ('02a', 3): (
        ['몸통에 표시한 관찰점이 화면에서 어디로 움직이는지,', '몸이 어떻게 기울어지는지 따로 보겠습니다.'],
        ['We will separately observe where the marked torso point moves on screen', 'and how the body tilts.']),
    ('07b', 6): (
        ['카메라도 움직이니까, 화면에 그린 선은 관찰용 표시입니다.', '앞서 계산한 구십 도는 따로 정한 수학 예입니다.'],
        ['The camera also moves, so the lines drawn on the screen are observation guides.', 'The ninety-degree calculation shown earlier is a separately defined mathematical example.']),
    ('10b', 4): (
        ['작은 부품을 세로와 가로로 돌려 보는 장면과,', '골라 놓은 자세로 실제 부품을 배치하는 장면을 비교하세요.'],
        ['Compare the shot of the small component turning upright and sideways', 'with the shot of a solid component placed in the chosen orientation.']),
    ('10b', 6): (
        ['비행 중인 기체와 달리 배치 자세를 고르는 상황이지만,', '물체의 축을 같은 기준에서 기록한다는 원리는 같습니다.'],
        ['Here we choose a placement orientation rather than fly an aircraft,', 'but the shared principle is to record the object axes in one reference frame.'])
}
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)
def wrap(text):
    if font.getlength(text) <= 1050:
        return [text]
    words = text.split(); choices = []
    for n in range(1, len(words)):
        lines = [' '.join(words[:n]), ' '.join(words[n:])]
        widths = [font.getlength(x) for x in lines]
        if max(widths) <= 1083:
            choices.append((abs(widths[0]-widths[1]), lines))
    assert choices, ('Needs editorial split', text)
    return min(choices, key=lambda x: x[0])[1]
groups = []
for s in plan['scenes']:
    if s['baseline']:
        continue
    sid = s['id']
    for p, (k, e) in enumerate(zip(ko[sid], en[sid]), 1):
        ks, es = splits.get((sid, p), ([k], [e]))
        assert ' '.join(ks) == k and ' '.join(es) == e
        for u, (kt, et) in enumerate(zip(ks, es), 1):
            lines = wrap(kt)
            groups.append(dict(id=f'{sid}-p{p:02d}-u{u:02d}', scene=sid, paragraph=p,
                ko=kt, en=et, lines=lines, boxWidth=math.ceil(max(font.getlength(x) for x in lines))+44,
                fixedCenter=[960, 970], fontSize=48, maximumTwoLines=True, timingPrepared=False,
                finalPixelReviewed=False))
assert len(groups) == 44
baseline = read(ROOT / plan['sourceBaselineTimeline'])
assert len(baseline['koCaptions']) == len(baseline['enCaptions']) == 200
out.write_text(json.dumps(dict(preparedAt=datetime.now(timezone.utc).isoformat(), groups=groups,
    koScriptSha256=sha(O / 'script/current34-combined-v1.ko.json'),
    enScriptSha256=sha(O / 'script/current34-combined-v1.en.json'),
    originalBaselineCuesRetained=200, addedParagraphs=40, addedEditorialCues=44, totalPlannedCues=244,
    all40AddedKoEnParagraphsExactlyPreserved=True, allAddedFontFitMeasured=True,
    currentWordTimingApproved=False, finalPixelsApproved=False, newImageGit=0), ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(preparedNewCues=44, baselineCues=200, plannedTotal=244, exact40KoEn=True, finalPixels=False)))
