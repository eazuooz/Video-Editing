"""Render a local, truthful index of the second editorial pass."""
from pathlib import Path
from html import escape as h
import json
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'progress.json').read_text(encoding='utf8'))
s=data['summary']
rows=[]
for x in data['rows']:
    done=x['status']=='column-saved-and-readback-verified'
    local=f'articles/{x["id"]}.saved.md' if done else '../articles/'+x['id']+'.md'
    rows.append('<tr><td>'+h(x['id'])+'</td><td><a href="'+h(x['notionUrl'])+'">'+h(x['title'])+'</a></td><td>'+('보강 저장·내부 검수 / 사용자 검수 대기' if done else '기존 글 있음 / 칼럼 보강 대기')+'</td><td>'+str(x.get('imageCount',x.get('images',0)))+'</td><td><a href="'+local+'">본문</a></td></tr>')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>위키 칼럼 보강 검수표</title><style>body{font:17px/1.7 system-ui,sans-serif;color:#19352c;background:#fffef9;max-width:1150px;margin:40px auto;padding:0 22px}a{color:#176eaa}table{border-collapse:collapse;width:100%;font-size:15px}td,th{text-align:left;border-bottom:1px solid #d9e2dc;padding:14px 10px;vertical-align:top}th{background:#eef3ec}td:nth-child(1){white-space:nowrap}p{max-width:850px}</style><h1>위키 칼럼 보강 검수표</h1>'''
html+=f'<p>전체 {data["scope"]}장 중 <b>{s["savedAndInternallyReviewed"]}장 보강 저장·내부 검수</b>, {s["pending"]}장 보강 대기. 사용자 검수는 대기 중입니다.</p>'
html+='<p>영상 요약을 독립적인 개발 방법론 칼럼으로 보강합니다. 구체적인 상황에서 출발해 상태·조건·구현 순서·실패 진단을 설명하고, 글을 위한 과정 그림을 추가합니다. 기존 영상 링크와 유용한 이미지·앞뒤 장 연결은 유지합니다. 공개 웹의 캐시 반영과 Notion 원문 저장은 별도로 확인합니다.</p>'
html+='<table><thead><tr><th>ID</th><th>글</th><th>현재 상태</th><th>이미지</th><th>로컬</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></html>'
(ROOT/'index.html').write_text(html,encoding='utf8')
historical=ROOT.parent/'index-baseline.html'
old_index=ROOT.parent/'index.html'
if not historical.exists() and old_index.exists():
    historical.write_text(old_index.read_text(encoding='utf8'),encoding='utf8')
root_html=html.replace('href="articles/','href="revision-column-v2/articles/')
root_html=root_html.replace('<h1>위키 칼럼 보강 검수표</h1>','<h1>위키 칼럼 보강 검수표</h1><p><a href="revision-column-v2/final-qa.json">전체 검수 기록</a> · <a href="index-baseline.html">초기판 기록</a></p>')
old_index.write_text(root_html,encoding='utf8')
print(s)
