"""Create audition links into the actual v6 master; does not claim listening."""
from pathlib import Path
import html, json, os
from urllib.parse import quote

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
OUT = P / 'production/local/final-qa-v6/listening'
MASTER = ROOT / f'output/{P.name}-v6/{P.name}.captioned.mp4'

def main():
    if not MASTER.is_file():
        raise FileNotFoundError(MASTER)
    timing = json.loads((P / 'production/local/audio-v4/narration.timing.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True, exist_ok=True)
    url = quote(os.path.relpath(MASTER, OUT).replace('\\', '/'), safe='/:.-_')
    rows = [('2배속 실제 플레이와 음악', 2, 32, '장전 → 사격 → 수갑 → 톱 → 강화 사격')]
    rows += [(f'{i + 1}. {e["scene_id"]}', float(e['start']) + 32,
              float(e['end']) + 32, e['text']) for i, e in enumerate(timing['entries'])]
    sections = []
    for title, start, end, text in rows:
        sections.append(f'<section><h2>{html.escape(title)}</h2>'
                        f'<p>{html.escape(text)}</p>'
                        f'<video controls preload="none" playsinline src="{url}#t={start:.3f},{end:.3f}"></video>'
                        f'<p>{start:.2f}–{end:.2f}초 · 현재 최종본의 소리와 화면</p></section>')
    page = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    page += '<title>REA v6 문단별 시청·청취</title><style>body{background:#090b0c;color:#f4f5f0;font:17px/1.7 "Malgun Gothic",sans-serif;max-width:920px;margin:auto;padding:24px}h1,h2{color:#f4cf77}section{border-top:1px solid #303a38;margin-top:28px}video{width:100%}</style>'
    page += '<h1>v6 문단별 시청·청취</h1><p>실제 최종 자막 영상의 구간별 재생 링크입니다. 배경음악·게임 효과음·말소리의 균형을 확인할 수 있습니다. 이 페이지 생성은 실제 청취 완료를 의미하지 않습니다.</p>'
    page += ''.join(sections) + '</html>'
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    print(str(OUT / 'index.html'))

if __name__ == '__main__':
    main()
