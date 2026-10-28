from pathlib import Path
from datetime import datetime, timezone
import hashlib
import html
import json
import shutil

task = Path(__file__).resolve().parent
repo = Path('D:/Github/VideoEditing')
batch = repo / 'production/batches/shorts-title-readability-20261028'
load = lambda name: json.loads((task / name).read_text(encoding='utf-8-sig'))
covers = load('covermap.json')['covers']
receipts = {x['videoId']: x for x in load('platform-receipts.json')}
after = load('studio-after.json')
assert len(covers) == len(receipts) == 14
assert after['allFourteenTitlesMatch'] and after['allFourteenVisibilityAndDatesPreserved']
esc = html.escape
cards = []
for c in covers:
    r = receipts[c['videoId']]
    assert r['thumbnailSHA256'] == c['jpgSHA256']
    assert hashlib.sha256(Path(c['jpgPath']).read_bytes()).hexdigest() == c['jpgSHA256']
    status = (r['dateKst'] + ' 17:00 KST 예약 유지') if r['dateKst'] else '비공개 유지 · 기존 권리 검토 보류'
    cards.append('<article><h2>' + esc(r['title']) + '</h2><p>' + esc(status) + '</p><div class="pair">'
        + '<figure><img src="' + Path(c['priorCoverPath']).as_uri() + '"><figcaption>이전</figcaption></figure>'
        + '<figure><img src="' + Path(c['jpgPath']).as_uri() + '"><figcaption>적용 완료</figcaption></figure></div>'
        + '<p class="old">이전 제목: ' + esc(r['previousTitle']) + '</p><a href="https://studio.youtube.com/video/'
        + c['videoId'] + '/edit">Studio에서 확인</a></article>')
page = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>얌얌코딩 쇼츠 14편 · 제목과 썸네일 개선</title><style>
*{box-sizing:border-box}body{margin:0;background:#0b0b0b;color:white;font:17px/1.65 system-ui,sans-serif;padding:24px}
main{max-width:1400px;margin:auto}h1{color:#ffdb62;font-size:28px}h2{font-size:21px;line-height:1.45;margin:0}p{color:#c8c8c8}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:32px}article{padding:16px;border:1px solid #444}
.pair{display:flex;gap:12px}.pair figure{width:50%;margin:0}img{width:100%;display:block}figcaption{padding:6px 0;font-weight:700}
a{color:#73dce5}.old{font-size:14px}header{margin-bottom:30px}footer{margin:32px 0}footer img{max-width:100%}
@media(max-width:420px){body{padding:14px}.grid{grid-template-columns:1fr}article{padding:12px}}
</style><main><header><h1>쇼츠 14편 · 제목과 썸네일 개선 완료</h1>
<p>실제 게임 이미지와 핵심 문구 두 줄. 제목 글씨 146–190px. 180px·375px 화면에서 가독성 확인.</p>
<p>Studio 저장 후 다시 열어 14편 제목·표지를 확인했습니다. 예약 13편과 비공개 1편은 유지했습니다.</p>
<p>제목과 썸네일을 함께 바꾼 작업이며 조회수 상승을 확인한 실험 결과는 아닙니다.</p></header><section class="grid">'''
page += ''.join(cards) + '</section><footer><h2>실제 Studio 적용 화면</h2><img src="studio-readability-complete.png"></footer></main></html>'
(task / 'index.html').write_text(page, encoding='utf-8')
completion = {
    'status': 'fourteen-titles-and-covers-applied-and-reopened',
    'completedAt': datetime.now(timezone.utc).isoformat(),
    'userRequest': '썸네일 글씨 잘보이게해줘~ 사람들이 잘 안봐 조회수가 제목도 조회수잘나오게~',
    'count': 14, 'scheduledUnchanged': 13, 'privateRightsHoldUnchanged': 'QlIwFupj9Dk',
    'scope': 'Same recent fourteen; old Bloom and other videos excluded.',
    'titleLanguage': 'ko', 'descriptionAndEnglishMetadataChanged': False,
    'videoBytesChanged': False, 'newUploadDeletionOrScheduleChanges': False,
    'userFullWatchingOrListeningInferred': False,
    'design': {'fontPxRange': [146, 190], 'headlineLines': 2, 'portraitDimensions': [1080, 1920],
               'actualGameplayBitmapPreserved': True, 'mobileWidthsInspected': [180, 375]},
    'reviewPage': str(task / 'index.html'), 'proof': str(task / 'studio-readability-complete.png'),
    'performance': {'improvementClaimed': False, 'singleVariableABTest': False,
                    'baseline': 'All fourteen were not public at the time of this change; small baseline counts are not public audience performance.'},
    'officialGuidance': [
        'https://support.google.com/youtube/answer/141805/discovery-optimisation-tips',
        'https://support.google.com/youtube/answer/12942217?co=YOUTUBE._YTVideoType%3Dshorts&hl=en'],
    'verification': {'titleAfterReload': 14, 'thumbnailAfterReload': 14, 'visibilityAndDatePreserved': 14,
                     'scheduledTimeAndTimezonePreserved': 13, 'metadataOnlyTask': True},
    'records': ['platform-receipts.json', 'studio-before.json', 'studio-after.json', 'covermap.json',
                'title-proposals.json', 'readability-qa.json'],
}
(task / 'completion.json').write_bytes((json.dumps(completion, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
batch.mkdir(parents=True, exist_ok=True)
names = ['completion.json', 'platform-receipts.json', 'studio-before.json', 'studio-after.json', 'covermap.json',
         'title-proposals.json', 'readability-qa.json', 'assets-audit.json', 'schedule-plan.json',
         'build-readable-covers.cjs', 'build-title-proposals.py', 'merge-readability-records.py',
         'commit-own-publishing-records.py', 'prepare-delivery.py']
for name in names:
    src, dst = task / name, batch / name
    assert src.is_file() and src.stat().st_size < 2_000_000
    src.read_text(encoding='utf-8-sig')
    assert not dst.exists(), f'Unexpected preexisting output {dst}'
    shutil.copyfile(src, dst)
print(json.dumps({'reviewPage': str(task / 'index.html'), 'batch': str(batch), 'textRecords': len(names)}))
