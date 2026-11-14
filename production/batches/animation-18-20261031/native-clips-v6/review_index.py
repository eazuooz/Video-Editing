"""Publish only the exact completed local masters in the finite selected revision."""
from html import escape
from pathlib import Path

from prepare import HERE, OUTPUT, read


def shell(title, content):
    return ('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + escape(title) + '</title><style>body{background:#080c0a;color:#f3f5ef;font:17px/1.7 system-ui;margin:0}'
            'main{max-width:1100px;margin:auto;padding:24px}h1{font-size:clamp(23px,4vw,36px);color:#f2d787}'
            'a{color:#94d8c9}video{width:100%;background:black}nav{display:flex;gap:20px;flex-wrap:wrap;margin:18px 0}'
            'td,th{padding:12px;text-align:left;border-bottom:1px solid #34463b}table{border-collapse:collapse;width:100%}'
            'small{color:#b5c4b8}</style><main>' + content + '</main></html>')


def main():
    plan = read(HERE / 'plan.json')
    rows, complete = [], 0
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for row in plan['episodes']:
        ep = row['id']
        receipt = OUTPUT / ep / 'delivery.json'
        if not receipt.is_file() or read(receipt).get('visualReviewPending', True):
            rows.append('<tr><td>' + ep + '</td><td>' + escape(row['title'].split('|')[0]) + '</td><td>수정 중</td></tr>')
            continue
        result = read(receipt)
        complete += 1
        links = {file['kind']: Path(file['path']).name for file in result['files']}
        controls = ''.join('<a href="' + escape(name) + '" download>' + label + '</a>' for kind, label in (
            ('clean.mp4', '무자막 영상'), ('captioned.mp4', '자막 영상'), ('ko.srt', '한국어 자막'), ('en.srt', '영어 자막'))
                           for name in [links[kind]])
        seconds = int(result['durationSeconds'])
        text = ('<nav><a href="../index.html">전체 검수표</a></nav><h1>' + escape(row['title']) + '</h1>'
                '<p>1080p 60fps · ' + f'{seconds // 60}:{seconds % 60:02}' + ' · 사용자 검수 대기</p>'
                '<video controls playsinline preload="metadata" src="' + links['captioned.mp4'] + '"></video>'
                '<nav>' + controls + '</nav><p>' + escape(result.get('revisionDescription', '')) + '</p>'
                '<a href="' + links['captioned.mp4'] + '#t=' + str(result['summaryAt']) + '">10초 요약 바로 보기</a>')
        (OUTPUT / ep / 'index.html').write_text(shell(row['title'], text), encoding='utf-8')
        rows.append('<tr><td>' + ep + '</td><td><a href="' + ep + '/index.html">' + escape(row['title'].split('|')[0])
                    + '</a></td><td>수정본 검수 가능</td></tr>')
    page = ('<h1>애니메이션 수정 검수</h1><p>수정본 ' + str(complete) + ' / 16편 준비</p>'
            '<p>A03–A18 · 기존 애니메이션 활용 비교와 편별 10초 요약</p>'
            '<table><tr><th>편</th><th>주제</th><th>상태</th></tr>' + ''.join(rows) + '</table>'
            '<p><small>A01과 A02는 Studio에서 공개를 확인해 이번 수정 대상에서 제외했습니다.</small></p>')
    (OUTPUT / 'index.html').write_text(shell('애니메이션 수정 검수표', page), encoding='utf-8')
    print(OUTPUT / 'index.html')


if __name__ == '__main__':
    main()
