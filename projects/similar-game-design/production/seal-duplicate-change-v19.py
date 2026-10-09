"""Seal one directly reread pronunciation clarification and current Studio rows."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'production/batches/sakurai-planning-game-design/proof-similar-game-design'
REPORT=ROOT/'production/batches/sakurai-planning-game-design/preflight/similar-game-design.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
cur=read(REPORT);old=read(B/'inventory-prior-v18.json')
oldmap={x['path']:x['sha256'] for x in old['inputFiles']}
changes=[x for x in cur['inputFiles'] if oldmap.get(x['path'])!=x['sha256']]
expected={'projects/game-math-normal-transform-uv/script/narration.ko.json':'9f5739fbd27ebe3497a6dc9b5023247c1f24062e8817b92c5c674f66bd64433c'}
assert {x['path']:x['sha256'] for x in changes}==expected
assert len(cur['existingProjects'])==51 and len(cur['inputFiles'])==358
for x in cur['inputFiles']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
ko=read(ROOT/next(iter(expected)))
assert len(ko['scenes'])==13 and sum(len(s['lines']) for s in ko['scenes'])==81
sp=ROOT/'shared/output/similar-game-design/preflight/studio-current-v19.ax.txt'
studio=sp.read_text('utf-8')
assert '_p1IqDeg6YE' in studio and '비슷한 게임' in studio and 'xnIA0EAJtiA' in studio
reason='법선/UV의 변경 KO13장81문단 전체를 직접 다시 읽었다. 11장의 영에서 숫자 이까지 UV, 정점 단계의 먼저 반복 오류와 보간 후 조회를 명료하게 발음하는 수정이다. 접선-법선 수직/역전치/정규화, UV 대응 및 범위 밖 주소 규칙은 여전히 렌더링 수학이다. 현재 영상의 친숙한 장르 행동에 목적·공간·협력을 연결하여 새 작품을 고를 이유를 만드는 질문/주장과 다르다. EN과 나머지 동료 파일은 v18의 전체 직접 검토를 보존했다. 새 현재 Studio 목록은 자신의 단일 새 비공개와 기존 수학 비공개 및 사용자 예약/공개 행을 보존한다.'
proof=dict(schemaVersion=1,reviewedAt=now,decision='distinct',inventoryProjects=51,inputsDigest=cur['inputsDigest'],
 changedFiles=[dict(**x,previousSha256=oldmap[x['path']],entireCurrentContentDirectlyRead=True,comparison=reason,foreignFileModified=False) for x in changes],
 wholeKoreanScript=dict(scenes=13,paragraphs=81),currentStudio=dict(path=sp.relative_to(ROOT).as_posix(),sha256=sha(sp),uiOnly=True,uiWritesToForeignRows=0,clippedDescriptionsNotFullContent=True),
 previousReview=dict(path=(B/'content-review-v18.json').relative_to(ROOT).as_posix(),sha256=sha(B/'content-review-v18.json')),
 emptyExactMatchesUsedAsDecision=False,foreignFilesModified=0)
save(B/'current-normal-uv-pronunciation-review-v19.json',proof)
review=copy.deepcopy(read(B/'content-review-v18.json'))
review.update(reviewedAt=now,previousReview=proof['previousReview'],currentForeignChangeReview=proof['changedFiles'],addedWholeScriptReview=(B/'current-normal-uv-pronunciation-review-v19.json').relative_to(ROOT).as_posix(),gateStatus='awaiting-current-check')
review['inventory'].update(projectCount=51,inputsDigest=cur['inputsDigest'])
review['scope']+=' v19: one changed KO13/81 complete reread and actual current Studio rows; unchanged inputs preserve prior content review.'
review['currentStudio']['currentList']=proof['currentStudio'];review.pop('gate',None)
save(B/'content-review-v19.json',review)
subprocess.run(['node','scripts/review-video-duplicates.cjs','similar-game-design','--decision','distinct','--reason',reason+' '+(B/'content-review-v19.json').relative_to(ROOT).as_posix(),'--studio-evidence',(B/'content-review-v19.json').relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
subprocess.run(['node','scripts/review-video-duplicates.cjs','similar-game-design','--check'],cwd=ROOT,check=True)
checked=read(REPORT);assert checked['inputsDigest']==cur['inputsDigest']
review.update(gateStatus='current-distinct-check-passed',gate=dict(command='node scripts/review-video-duplicates.cjs similar-game-design --check',exitCode=0,checkedAt=now,inputsDigest=checked['inputsDigest']))
save(B/'content-review-v19.json',review);save(B/'inventory-prior-v19.json',checked)
cp_path=ROOT/'projects/similar-game-design/production/latest-checkpoint.json';cp=read(cp_path)
cp.update(currentDuplicateReview=(B/'content-review-v19.json').relative_to(ROOT).as_posix(),duplicateInputsDigest=checked['inputsDigest'],updatedAt=now);save(cp_path,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='similar-game-design')
item.update(currentDuplicateReview=cp['currentDuplicateReview'],duplicateInputsDigest=checked['inputsDigest']);q['updatedAt']=now;save(qp,q)
print(json.dumps(dict(distinctPassed=True,projects=51,changedWholeKoParagraphs=81,foreignFilesModified=0)))
