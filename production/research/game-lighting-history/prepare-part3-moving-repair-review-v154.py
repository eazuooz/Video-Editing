"""Local UI for direct normal-rate review of seven existing repaired inputs."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'production/research/game-lighting-history'
plan = json.loads((ROOT/'projects/game-lighting-history-04/production/part3-final-input-plan-v145.json').read_text('utf-8'))
proof = json.loads((ROOT/'projects/game-lighting-history-04/production/part3-annotated-visual-build-v148.json').read_text('utf-8'))
rows=[]
for r in proof['cuts']:
    if not r['repairedNative']: continue
    c=next(c for c in plan['cuts'] if c['id']==r['id'])
    related=[p for p in plan['paragraphs'] if any(max(q['fromFrame'],c['fromFrame']) < min(q['toFrame'],c['toFrame']) for q in p['koCues'])]
    rows.append({'id': r['id'], 'path':r['path'], 'ranges':[[0,c['frames']/60]], 'ko':' '.join(p['ko'] for p in related)})
assert len(rows)==7
source=(R/'local/part3-explanation-moving-input-review-v151.html').read_text('utf-8')
a=source.index('const rows=');b=source.index('];const pick',a)
source=source[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+source[b+1:]
source=source.replace('현재 2.5D 설명 입력의 정상 속도 검수','보정한 실제 입력의 표시·크롭 검수')
source=source.replace('입력의 움직임 확인 · 최종 자막 합성 픽셀 승인과 구별','일곱 보정 구간 · 원래 동작과 시각 표시를 비교 · 최종 자막 합성은 별도 검수')
(R/'local/part3-moving-repair-review-v154.html').write_text(source,'utf-8')
print(json.dumps({'preparedInputReviewRows':7,'newImages':0,'approved':False}))
