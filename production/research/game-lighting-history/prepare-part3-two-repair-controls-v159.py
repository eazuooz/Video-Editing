"""Prepare two local review controls, without recording approval."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'production/research/game-lighting-history';P=ROOT/'projects/game-lighting-history-04/production'
plan=json.loads((P/'part3-final-input-plan-v145.json').read_text('utf-8'))
rows=[]
for i,c in enumerate(plan['cuts']):
 if c['id'] not in ['hogwarts-courtyard-ui','grade-shared-reference']:continue
 path=f'production/research/game-lighting-history/local/part3-annotations-v159/cut-{i+1:03d}-annotated.mp4'
 assert (ROOT/path).exists()
 related=[p for p in plan['paragraphs'] if any(max(q['fromFrame'],c['fromFrame'])<min(q['toFrame'],c['toFrame']) for q in p['koCues'])]
 rows.append(dict(id=c['id'],path=path,ranges=[[0,c['frames']/60]],ko=' '.join(p['ko'] for p in related)))
assert len(rows)==2
source=(R/'local/part3-explanation-moving-input-review-v151.html').read_text('utf-8')
a=source.index('const rows=');b=source.index('];const pick',a)
source=source[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+source[b+1:]
source=source.replace('현재 2.5D 설명 입력의 정상 속도 검수','관찰된 두 표시 오류 수정 검수')
(R/'local/part3-two-repair-controls-v159.html').write_text(source,'utf-8')
print(json.dumps(dict(preparedRows=len(rows),approved=False)))
