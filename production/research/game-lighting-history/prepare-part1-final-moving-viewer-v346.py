"""Prepare a local UI for the four changed complete final intervals; no approval."""
from pathlib import Path
import json
root=Path('D:/Github/Video-Editing');r=root/'production/research/game-lighting-history';p=root/'projects/game-lighting-history-04/production'
cmp=json.loads((p/'part1-texture-current-decoded-comparison-v346.json').read_text('utf-8-sig'))
plan=json.loads((p/'part1-final-input-plan-v309.json').read_text('utf-8-sig'))
pair=json.loads((p/'part1-reviewed-pair-build-v345.json').read_text('utf-8-sig'))
rows=[]
for c in cmp['movingIntervals']:
 if c['needsFreshCurrentMovingReview']:
  relevant=[q for q in plan['paragraphs'] if any(c['rangeSeconds'][0]<=x['fromFrame']/60<c['rangeSeconds'][1] for x in q['koCues'])]
  rows.append(dict(id=c['id'],path=pair['captioned']['path'],ranges=[c['rangeSeconds']],ko=' '.join(q['ko'] for q in relevant)))
template=(r/'local/part1-texture-stack-preview-v343d/review.html').read_text('utf-8')
a=template.index('const rows=');b=template.index(';const pick=',a)
html=template[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+template[b:]
html=html.replace('실제 편집기 소스 · 수치 가독성 / 안내 시점 수정 후보','현재 최종 345 · 변경된 네 전체 구간 검수')
dest=r/'local/part1-texture-final-pixel-qa-v346/review.html';assert not dest.exists();dest.write_text(html,'utf-8')
print(json.dumps(dict(viewer=str(dest),intervals=len(rows),totalSeconds=sum(x['ranges'][0][1]-x['ranges'][0][0] for x in rows),approved=False)))
