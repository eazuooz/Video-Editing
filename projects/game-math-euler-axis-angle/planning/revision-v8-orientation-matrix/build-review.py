"""Build a script-only local review. Does not generate audio/video or publish."""
from pathlib import Path
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'projects/game-math-euler-axis-angle'
SCRIPT = BASE / 'script/revision-v8-orientation-matrix'
PLAN = Path(__file__).parent
OUT = ROOT / 'output/game-math-euler-axis-angle/script-review-v8'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    data = json.loads((SCRIPT / 'narration.ko.json').read_text(encoding='utf8'))
    narration = '\n\n'.join(p for s in data['scenes'] for p in s['paragraphs']) + '\n'
    (SCRIPT / 'narration.ko.txt').write_text(narration, encoding='utf8')
    chapter_names = {
        '8.1': '‘자세’란 정확히 무엇인가?',
        '8.2': '행렬 표현',
        '8.2.1': '어느 행렬을 써야 할까?',
        '8.2.2': '방향코사인 행렬',
        '8.2.3': '행렬 표현의 장점',
        '8.2.4': '행렬 표현의 단점',
        '8.2.5': '행렬 표현 정리',
    }
    chunks = []
    previous = None
    for scene in data['scenes']:
        if scene['section'] != previous:
            chunks.append(f'<h2 id="section-{scene["section"]}">{scene["section"]} {chapter_names[scene["section"]]}</h2>')
            previous = scene['section']
        paragraphs = ''.join(f'<p id="{scene["id"]}-p{i}">{html.escape(p)}</p>' for i, p in enumerate(scene['paragraphs'], 1))
        chunks.append(f'<article><h3>{html.escape(scene["title"])}</h3><div class="pair"><div class="speech">{paragraphs}</div><aside><b>화면 설계 메모</b><p>{html.escape(scene["visual"])}</p><small>아직 제작하지 않은 설계입니다. 숫자는 자체 설명 모형의 예시이며 게임 내부 측정값이 아닙니다.</small></aside></div></article>')
    nav = ''.join(f'<a href="#section-{k}">{k} {v}</a>' for k, v in chapter_names.items())
    page = '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>자세와 회전행렬 · 전체 대본 검수</title><style>
:root{color-scheme:dark;--bg:#111315;--text:#f4f4ee;--muted:#b8bdc4;--accent:#f3d273;--line:#42464e}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:20px/1.9 "Malgun Gothic",sans-serif}header,main,footer{max-width:1020px;margin:auto;padding:40px 32px}header{border-bottom:1px solid var(--line)}h1{font-size:36px;line-height:1.4;margin:14px 0}h2{font-size:28px;color:var(--accent);margin:60px 0 18px;scroll-margin-top:30px}h3{font-size:21px;color:var(--muted);margin:28px 0 12px}p{margin:0 0 25px}a{color:var(--accent);text-underline-offset:5px}nav{display:grid;grid-template-columns:1fr 1fr;gap:8px 20px;font-size:17px;margin:24px 0}.label{color:var(--accent);font-size:16px;letter-spacing:.08em}.summary{font-size:18px;color:var(--muted)}.tools{display:flex;gap:16px;align-items:center;flex-wrap:wrap}button{background:none;border:1px solid var(--line);color:var(--text);padding:10px 14px;border-radius:5px;font:inherit;font-size:16px;cursor:pointer}button[aria-pressed=true]{border-color:var(--accent);color:var(--accent)}aside{display:none;background:#1b1e22;padding:22px;font-size:16px;line-height:1.8;color:var(--muted);align-self:start;border-left:3px solid var(--accent)}aside b{color:var(--accent)}small{font-size:14px}.show-plan main{max-width:1500px}.show-plan .pair{display:grid;grid-template-columns:minmax(0,2.2fr) minmax(270px,1fr);gap:40px}.show-plan aside{display:block}.continuous h2,.continuous h3{display:none}footer{border-top:1px solid var(--line);font-size:16px;color:var(--muted)}@media(max-width:700px){body{font-size:18px}header,main,footer{padding:25px 20px}h1{font-size:28px}h2{font-size:24px}nav{grid-template-columns:1fr}.show-plan .pair{display:block}.show-plan aside{margin:15px 0 30px}}
</style></head><body><header><div class="label">얌얌코딩 · 게임 수학 PART2 · 대본 검수</div><h1>게임은 물체의 기울기를<br>어떻게 기억할까?</h1><p class="summary">이번 강의는 <strong>8.1 자세부터 8.2.5 행렬 표현 정리까지</strong>입니다.<br>오일러 각·짐벌 락·축–각의 상세 설명은 포함하지 않습니다. 새 음성·영상은 제작하지 않았습니다.</p><div class="tools"><a href="narration.ko.txt" download>전체 대본 TXT</a><button id="plan" aria-pressed="false">화면 메모 보기</button><button id="flow" aria-pressed="false">소제목 없이 읽기</button></div><nav>''' + nav + '''</nav></header><main>''' + ''.join(chunks) + '''</main><footer><p>검수 범위: 문장 흐름·선택한 글의 내용 대응·행렬 방향·숫자 계산. 말속도와 실제 화면의 이해도는 아직 검수 대상 영상이 없습니다.</p><p>학습 기준: <a href="https://app.notion.com/p/3e10b1ffa61e81d289e1da0dd7584a13">게임 수학 PART2 · 3차원 회전 8.1–8.2.5</a>. 글 안의 정정 사항을 반영하고 설명 문장은 새로 작성했습니다.</p></footer><script>
for(const [id,cls] of [['plan','show-plan'],['flow','continuous']]){document.getElementById(id).addEventListener('click',function(){const on=document.body.classList.toggle(cls);this.setAttribute('aria-pressed',String(on))})}
</script></body></html>'''
    (PLAN / 'review.html').write_text(page, encoding='utf8')
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PLAN / 'review.html', OUT / 'index.html')
    shutil.copyfile(SCRIPT / 'narration.ko.txt', OUT / 'narration.ko.txt')
    # Keep the tracked review link self-contained beside its HTML as well.
    (PLAN / 'narration.ko.txt').write_text(narration, encoding='utf8')
    validation = {
        'status': 'script-structure-valid',
        'scope': list(chapter_names),
        'scenes': len(data['scenes']),
        'paragraphs': sum(len(s['paragraphs']) for s in data['scenes']),
        'narrationCharacters': len(narration.strip()),
        'scriptSha256': sha(SCRIPT / 'narration.ko.json'),
        'textSha256': sha(SCRIPT / 'narration.ko.txt'),
        'reviewSha256': sha(PLAN / 'review.html'),
        'sourceCoverage': 'source-inventory.json',
        'technicalReview': 'technical-audit.json',
        'tts': 'not-started-not-authorized',
        'render': 'not-started-not-authorized',
        'runtimeSeconds': None,
        'actualAudioPaceReview': 'not-applicable-no-new-audio',
        'humanScriptReview': 'pending',
        'priorVideoApproval': False,
    }
    assert list(dict.fromkeys(s['section'] for s in data['scenes'])) == list(chapter_names)
    assert all(s['paragraphs'] and s['visual'] for s in data['scenes'])
    forbidden = ['원영상', '사쿠라이', '원작자', '제공된 자막']
    assert not any(x in narration for x in forbidden)
    (PLAN / 'validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == '__main__':
    build()
