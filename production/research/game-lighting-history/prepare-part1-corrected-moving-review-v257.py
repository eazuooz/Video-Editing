"""Bind a normal-speed review page to the five actually rendered corrections."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BP=P/'part1-final-visual-build-v250.json';build=read(BP)
SP=P/'part1-native-pixels-execution-v250.json';state=read(SP)
assert state['status']=='complete-awaiting-direct-pixels' and state['exitCode']==0 and build['wholeDecodeExitCode']==0
PP=P/'part1-final-input-plan-v240.json';plan=read(PP)
assert build['planSha256']==sha(PP) and len(build['repairs'])==5
rows=[]
for r in build['repairs']:
 assert sha(ROOT/r['path'])==r['sha256']
 c=next(c for c in build['effectiveCuts'] if c['id']==r['id'])
 rows.append({'id':r['id'],'path':r['path'],'sha256':r['sha256'],'ranges':[[0,r['frames']/60]],
 'ko':next(p['ko'] for p in plan['paragraphs'] if p['id']==c['paragraphId'])})
template=ROOT/'production/research/game-lighting-history/local/part1-moving-input-review-v247.html'
html=template.read_text('utf8');a=html.index('const rows=');b=html.index('];const pick',a)
html=html[:a]+'const rows='+json.dumps(rows,ensure_ascii=False)+html[b+1:]
html=html.replace('④-1 현재 입력의 정상 속도 검수','④-1 수정된 합성 입력의 정상 속도 검수')
dest=ROOT/'production/research/game-lighting-history/local/part1-corrected-moving-review-v257.html';dest.write_text(html,'utf8')
request={'preparedAt':datetime.now(timezone.utc).isoformat(),'visualBuildSha256':sha(BP),'planSha256':sha(PP),'rows':rows,
 'html':dest.relative_to(ROOT).as_posix(),'htmlSha256':sha(dest),'allCorrectedEncodedMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'qaApproved':False,'newGitImages':0}
(P/'part1-corrected-moving-review-request-v257.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'renderedInputsBound':len(rows),'movingApproved':False}))
