"""Expose normal-speed controls for every actual final encoded cut, without approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'production/research/game-lighting-history';P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PP=P/'part1-final-input-plan-v240.json';OP=P/'part1-input-overrides-v249.json';BP=P/'part1-reviewed-pair-build-v252.json'
plan,overrides,pair=read(PP),read(OP),read(BP)
assert pair['planSha256']==sha(PP) and pair['inputOverrides']['sha256']==sha(OP) and pair['captioned']['wholeDecode']['exitCode']==0
assert sha(ROOT/pair['captioned']['path'])==pair['captioned']['sha256']
rows=[{'id':'original-branding','path':pair['captioned']['path'],'ranges':[[0,2]],'ko':'원래 고양이 로고 2초'}]
for c in overrides['effectiveCuts']:
 related=[p for p in plan['paragraphs'] if any(max(q['fromFrame'],c['fromFrame'])<min(q['toFrame'],c['toFrame']) for q in p['koCues'])]
 rows.append({'id':c['id'],'path':pair['captioned']['path'],'ranges':[[c['fromFrame']/60,c['toFrame']/60]],'ko':' '.join(p['ko'] for p in related)})
rows.append({'id':'original-membership','path':pair['captioned']['path'],'ranges':[[(plan['finalFrames']-600)/60,plan['finalFrames']/60]],'ko':'원래12행 프로필·이름·배지·로고와 정확한 멤버쉽가입 감사드립니다. 제목·과외 링크'})
assert len(rows)==96
source=(R/'local/part1-moving-input-review-v247.html').read_text('utf8');a=source.index('const rows=');b=source.index('];const pick',a)
source=source[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+source[b+1:]
source=source.replace('④-1 현재 입력의 정상 속도 검수','④-1 최종 자막 영상의 정상 속도 검수')
source=source.replace('현재 2.5D 설명 입력의 정상 속도 검수','④-1 최종 자막 영상의 정상 속도 검수')
dest=R/'local/part1-final-moving-review-v261.html';dest.write_text(source,'utf8')
request={'preparedAt':datetime.now(timezone.utc).isoformat(),'source':pair['captioned']['path'],'sourceSha256':pair['captioned']['sha256'],
 'pairBuildSha256':sha(BP),'planSha256':sha(PP),'inputOverridesSha256':sha(OP),'rows':rows,'html':dest.relative_to(ROOT).as_posix(),'htmlSha256':sha(dest),
 'allFinalMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'qaApproved':False,'newGitImages':0}
(P/'part1-final-moving-review-request-v261.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'allFinalCutsBound':96,'normalSpeed':1,'approved':False}))
