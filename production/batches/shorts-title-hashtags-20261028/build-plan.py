from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re, shutil

TASK = Path(__file__).resolve().parent
PRIOR = TASK.parent / 'shorts-title-readability-20261028'
REPO = Path('D:/Github/VideoEditing')
load = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
tags = {
    'ULUDi4gKgzw': ['#게임개발', '#노이타', '#물리시뮬레이션'],
    'X27rK3qlrto': ['#게임개발', '#뷰파인더', '#메시절단'],
    'pT9UgRewqxw': ['#게임개발', '#레인월드', '#절차적애니메이션'],
    'QlIwFupj9Dk': ['#게임개발', '#아우터와일즈', '#게임물리'],
    'NwgrLJhu1UI': ['#게임개발', '#오브라딘', '#디더링'],
    'ijGOYaPZi3c': ['#게임개발', '#디아블로2', '#울트라와이드'],
    'qpoUJd_S0LA': ['#게임개발', '#디아블로2', '#게임그래픽'],
    'KcnUqy8tcfI': ['#게임개발', '#디아블로2', '#스프라이트'],
    'IaU43puuLuI': ['#게임개발', '#디아블로2', '#렌더링'],
    'tocRD4fGhJ0': ['#게임개발', '#디아블로2', '#게임패드'],
    'Tt7hCWPjcpc': ['#게임개발', '#컵헤드', '#애니메이션'],
    'utm0fy9Smyc': ['#게임개발', '#티어다운', '#복셀'],
    '5-QZzmXlTLM': ['#게임개발', '#스플래툰2', '#게임그래픽'],
    'RYjQZiKtU30': ['#게임개발', '#스플래툰', '#텍스처'],
}
items = []
for p in load(PRIOR / 'title-proposals.json')['items']:
    path = REPO / 'projects' / p['slug'] / 'publishing/youtube-upload.json'
    receipt = load(path)
    previous = receipt.get('title') or receipt.get('metadata', {}).get('title')
    assert previous == p['proposedTitle'], (p['videoId'], previous)
    ht = tags[p['videoId']]
    assert len(ht) == len(set(ht)) == 3
    assert all(re.fullmatch(r'#[^\s#]+', tag) for tag in ht)
    title = previous + ' ' + ' '.join(ht)
    assert len(title) <= 100
    source = Path(p['evidence']['path'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == p['evidence']['sha256']
    items.append({'videoId': p['videoId'], 'slug': p['slug'], 'previousTitle': previous,
                  'title': title, 'hashtags': ht, 'titleLength': len(title),
                  'rationale': '기존 제목 문장을 유지하고 채널 주제·해당 게임·본문에서 설명하는 기술을 각각 연결한다.',
                  'sourceEvidencePath': str(source), 'sourceEvidenceSHA256': p['evidence']['sha256'],
                  'sourceEvidenceSnippet': p['evidence']['snippet'],
                  'receiptPath': str(path), 'thumbnailSHA256': receipt['thumbnail']['sha256'],
                  'masterSHA256': receipt.get('masterSha256') or receipt.get('captionedSha256') or receipt.get('uploadedFile', {}).get('sha256')})
plan = {'createdAt': datetime.now(timezone.utc).isoformat(), 'scope': 'Same recent fourteen Shorts; titles only',
        'request': '그리고 우리 쇼츠영상에도 각 #게임 개발 같은 해쉬태그 제목뒤에 붙여서 잘나오게 해줘',
        'status': 'prepared-for-root-review', 'publicRightsHoldPreserved': 'QlIwFupj9Dk',
        'baseTitleChanged': False, 'hashtagCount': 3, 'viewIncreaseGuaranteed': False,
        'officialGuidance': 'https://support.google.com/youtube/answer/6390658?hl=ko',
        'guidanceSummary': 'Use no spaces inside a hashtag and only directly related topics; no invented ranking benefit.',
        'items': items}
TASK.mkdir(parents=True, exist_ok=True)
(TASK / 'plan.json').write_bytes((json.dumps(plan, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
for name in ('assets-audit.json', 'schedule-plan.json'):
    shutil.copyfile(PRIOR / name, TASK / name)
print(json.dumps({'plan': str(TASK/'plan.json'), 'count': len(items), 'maxTitleLength': max(x['titleLength'] for x in items)}))
