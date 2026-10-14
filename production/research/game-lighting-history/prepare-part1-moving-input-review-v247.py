"""Expose the thirteen current repaired inputs for direct, normal-rate UI review."""
from pathlib import Path
import json, hashlib
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'production/research/game-lighting-history'
P = ROOT / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan_path = P / 'part1-final-input-plan-v240.json'
plan = read(plan_path)
state = read(P / 'part1-input-repair-execution-v245.json')
assert len(state['results']) == 94
assert state['planSha256'] == sha(plan_path)
result = {r['id']:r for r in state['results']}
rows = []
for c in plan['cuts']:
    selected = c['id'] == 'first:original-overview-1' or 'part1-label-repair-v225' in c['video']['path'] or 'part1-observation-bridge-v236' in c['video']['path'] or c['id'] in read(P/'part1-visual-layers-v244.json')['layers']
    if not selected: continue
    r = result[c['id']]
    assert sha(ROOT/r['path']) == r['sha256']
    related = [p for p in plan['paragraphs'] if any(max(q['fromFrame'],c['fromFrame']) < min(q['toFrame'],c['toFrame']) for q in p['koCues'])]
    rows.append({'id':c['id'],'path':r['path'],'sha256':r['sha256'],'ranges':[[0,c['frames']/60]],'ko':' '.join(p['ko'] for p in related)})
assert len(rows) == 13
source = (R/'local/part3-explanation-moving-input-review-v151.html').read_text('utf-8')
a = source.index('const rows=');b = source.index('];const pick',a)
source = source[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+source[b+1:]
source = source.replace('현재 2.5D 설명 입력의 정상 속도 검수','④-1 수정 입력의 정상 속도 검수')
source = source.replace('입력의 움직임 확인 · 최종 자막 합성 픽셀 승인과 구별','정확한 컷 길이·원본 조건·실제 움직임·공간 도식 확인 · 최종 자막 픽셀은 별도 검수')
html = R/'local/part1-moving-input-review-v247.html'
assert not html.exists()
html.write_text(source,'utf-8')
manifest = {'preparedOnly':True,'planSha256':sha(plan_path),'rows':rows,'html':html.relative_to(ROOT).as_posix(),'htmlSha256':sha(html),'normalMovingPlaybackObserved':False,'allMovingPixelsReviewed':False,'finalPixelsApproved':False,'newGitImages':0}
(P/'part1-moving-input-request-v247.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'preparedRows':len(rows),'normalPlaybackApproved':False}))
