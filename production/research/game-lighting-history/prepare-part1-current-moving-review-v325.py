"""Bind the current final pair's 96 cuts to normal-speed UI without marking approval."""
from pathlib import Path
import json, hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'production/research/game-lighting-history';P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BP=P/'part1-reviewed-pair-build-v323.json';pair=read(BP)
plan=read(P/'part1-final-input-plan-v309.json');visual=read(P/'part1-final-visual-build-v322.json')
assert pair['planSha256']==visual['planSha256']==sha(P/'part1-final-input-plan-v309.json') and pair['captioned']['wholeDecode']['exitCode']==0
assert sha(ROOT/pair['captioned']['path'])==pair['captioned']['sha256']
old=read(P/'part1-final-moving-review-request-v295.json')
rows=[dict(r,path=pair['captioned']['path']) for r in old['rows']]
assert len(rows)==96
for r,c in zip(rows[1:-1],visual['cuts']):
 assert r['id']==c['id'] and r['ranges'][0]==[c['fromFrame']/60,c['toFrame']/60]
 related=[p for p in plan['paragraphs'] if any(max(q['fromFrame'],c['fromFrame'])<min(q['toFrame'],c['toFrame']) for q in p['koCues'])]
 r['ko']=' '.join(p['ko'] for p in related)
rows.insert(0,dict(id='whole-current-captioned-final',path=pair['captioned']['path'],ranges=[[0,1485.8]],ko='현재323 최종본 정상 속도 연속 검수. 기존 검수의 픽셀 동일성은 별도324로 확인합니다.'))
source=(R/'local/part1-final-continuous-review-v304.html').read_text('utf8');a=source.index('const rows=');b=source.index('];const pick',a)
source=source[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+source[b+1:]
dest=R/'local/part1-current-moving-review-v325.html';assert not dest.exists();dest.write_text(source,'utf8')
request=dict(preparedAt=datetime.now(timezone.utc).isoformat(),source=pair['captioned']['path'],sourceSha256=pair['captioned']['sha256'],pairBuildSha256=sha(BP),planSha256=pair['planSha256'],rows=rows,html=dest.relative_to(ROOT).as_posix(),htmlSha256=sha(dest),allFinalMovingPixelsReviewed=False,newGitImages=0)
(P/'part1-current-moving-review-request-v325.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(cuts=96,normalSpeed=1,approved=False)))
