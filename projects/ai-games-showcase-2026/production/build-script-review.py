"""Build a readable complete script with the six rendered tool-summary slides."""
from pathlib import Path
import json,html,re,shutil
R=Path(__file__).resolve().parents[3];P=R/'projects/ai-games-showcase-2026';O=R/'output/ai-games-showcase-2026/planning'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
ko=read(P/'script/narration.ko.json');plan=read(P/'planning/production-plan.json');aliases=read(P/'script/pronunciation.json')['aliases']
def display(text):
 for canonical,spoken in sorted(aliases.items(),key=lambda x:len(x[1]),reverse=True):text=re.sub(r'(?<![가-힣A-Za-z0-9])'+re.escape(spoken),lambda _:canonical,text)
 return html.escape(text)
body=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI 게임 제작 근황 · 전체 대본</title>',
 '<style>body{margin:0;background:#111;color:#eee;font:18px/1.8 "Malgun Gothic",sans-serif}main{max-width:1000px;margin:auto;padding:36px 22px}h1,h2{color:#e8cf83;line-height:1.4}h2{margin-top:56px}p{max-width:920px}a{color:#e8cf83}video,img{width:100%;height:auto;display:block}nav{display:flex;gap:10px 24px;flex-wrap:wrap}aside{color:#b8c0bd}figure{margin:30px 0}figcaption{font-size:15px;color:#b8c0bd}.notice{border-left:4px solid #e8cf83;padding-left:18px}</style><main>',
 '<h1>AI로 만든 여섯 게임<br>전체 대본과 화면 구성</h1>',
 '<p class="notice">긴 AI 설명 영상은 제외했습니다. 각 게임마다 개발 환경·도구 PPT를 한 번, 5초씩 보여 줍니다. 아래 영상은 여섯 장의 화면을 확인하는 <strong>30초 무음 미리보기</strong>이며 완성 영상이 아닙니다. 새 음성은 게임·Unity 사용 종료 확인을 기다리고 있습니다.</p>',
 '<video controls preload="metadata" src="tool-summary-30s-silent.mp4"></video>',
 '<p><a href="ai-games-development-tools-v2.pptx">편집 가능한 PPT 6장</a> · 1920×1080 · 60fps · 각 5초</p>',
 '<nav>'+''.join(f'<a href="#s{s["id"]}">{html.escape(s["title"])}</a>' for s in ko['scenes'])+'</nav>']
slide=0
for scene,n in zip(plan['scenes'],ko['scenes']):
 body+= [f'<section id="s{n["id"]}"><h2>{html.escape(n["title"])}</h2>']
 card=scene.get('developmentSummary')
 for number,paragraph in enumerate(n['lines'],1):
  if card and number==card['paragraph']:
   slide+=1;name=f'tools-{slide:02d}.png';shutil.copy2(P/f'production/local/tool-slides/slide-{slide:02d}.png',O/name)
   body += [f'<figure><img loading="lazy" src="{name}" alt="{html.escape(card["title"])} 개발 환경 요약"><figcaption>이 문장 시작에 PPT 5초 → 같은 게임 화면으로 복귀. 문장은 자연스럽게 이어집니다.</figcaption></figure>']
  body += [f'<p>{display(paragraph)}</p>']
 body += ['</section>']
body+=['<aside>출처·개발 기간·모델의 확인 범위는 프로젝트 조사 기록에 보관했습니다. 미확인 정보는 내레이션에서도 구분했습니다. 최종 영상과 음성 검수는 별도 진행 단계입니다.</aside></main></html>']
(O/'index.html').write_text('\n'.join(body),encoding='utf-8')
print(json.dumps({'scenes':len(ko['scenes']),'paragraphs':sum(len(s['lines']) for s in ko['scenes']),'slides':slide,'reviewPage':str(O/'index.html')},ensure_ascii=False))
