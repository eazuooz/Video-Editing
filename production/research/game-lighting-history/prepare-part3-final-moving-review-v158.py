"""Prepare local review controls over the actual final captioned encode, no approval."""
from pathlib import Path
import json, hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'production/research/game-lighting-history'
P=ROOT/'projects/game-lighting-history-04/production'
plan=json.loads((P/'part3-final-input-plan-v145.json').read_text('utf-8'))
pair=json.loads((P/'part3-reviewed-pair-build-v149.json').read_text('utf-8'))
rows=[dict(id='original-branding',path=pair['captioned']['path'],ranges=[[0,2]],ko='원래 고양이 로고 2초')]
for c in plan['inputs'] if 'inputs' in plan else plan['cuts']:
    related=[p for p in plan['paragraphs'] if any(max(q['fromFrame'],c['fromFrame'])<min(q['toFrame'],c['toFrame']) for q in p['koCues'])]
    rows.append(dict(id=c['id'],path=pair['captioned']['path'],ranges=[[c['fromFrame']/60,c['toFrame']/60]],ko=' '.join(p['ko'] for p in related)))
rows.append(dict(id='original-membership',path=pair['captioned']['path'],ranges=[[(plan['finalFrames']-600)/60,plan['finalFrames']/60]],ko='원래 12행 프로필·이름·배지와 정확한 멤버쉽가입 감사드립니다. 제목·과외 링크'))
assert len(rows)==95
source=(R/'local/part3-explanation-moving-input-review-v151.html').read_text('utf-8')
a=source.index('const rows=');b=source.index('];const pick',a)
source=source[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+source[b+1:]
source=source.replace('현재 2.5D 설명 입력의 정상 속도 검수','현재 최종 자막 영상의 이동 검수')
source=source.replace('입력의 움직임 확인 · 최종 자막 합성 픽셀 승인과 구별','최종 92038프레임 · 실제 합성 자막·도식·표시선 검수')
out=R/'local/part3-final-moving-review-v158.html';out.write_text(source,'utf-8')
proof=dict(preparedAt=datetime.now(timezone.utc).isoformat(),source=pair['captioned']['path'],sourceSha256=pair['captioned']['sha256'],rows=rows,approved=False)
(P/'part3-final-moving-review-request-v158.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(rows=len(rows),sourceSha256=proof['sourceSha256'],approved=False)))
