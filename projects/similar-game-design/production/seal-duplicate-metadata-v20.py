"""Seal a fully read foreign normal/UV manifest and fresh Studio comparison."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'production/batches/sakurai-planning-game-design/proof-similar-game-design'
R=ROOT/'production/batches/sakurai-planning-game-design/preflight/similar-game-design.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
cur=read(R);old=read(B/'inventory-prior-v19.json')
m={x['path']:x['sha256'] for x in old['inputFiles']}
delta=[x for x in cur['inputFiles'] if m.get(x['path'])!=x['sha256']]
expected={'projects/game-math-normal-transform-uv/project.json':'0cff1169bb9d4102dbe55470185e58c60ffd40663cef2523d3f867ac565f55f3'}
assert {x['path']:x['sha256'] for x in delta}==expected
assert len(cur['existingProjects'])==51 and len(cur['inputFiles'])==358
for x in cur['inputFiles']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
studio=ROOT/'shared/output/similar-game-design/preflight/studio-current-v20.ax.txt'
t=studio.read_text('utf-8')
for value in ['_p1IqDeg6YE','xnIA0EAJtiA','비슷한 게임','비공개']:assert value in t
reason='변경된 법선 변환/UV manifest 전체를 직접 읽었다. inverse-transpose 수직 조건, UV 대응과 보간 후 주소 조회, 표면/무늬 예시 및734초 본편17616:26424프레임40:60 강의 배정의 실측 갱신이다. 해당13장 KO81문단/EN 전체 검토와 발음 명료화는 v19까지 보존됐다. 렌더링 수학의 계산 질문은 친숙한 장르 행동에 목적·공간·협력의 새 선택 이유를 연결하는 현재 게임설계 주장과 다르다. 수학의40:60/noBGM/검정 예외는 이 이미 시작한 흰60:40/Nimbus 영상에 복사하지 않는다. 새 실제 Studio의 동일 단일 비공개/기존 수학 행과 사용자 예약·공개 상태도 직접 비교했다. 외부 파일 수정0, 제목/ID/emptyExactMatches 단독 판정0.'
proof=dict(schemaVersion=1,reviewedAt=now,decision='distinct',inventoryProjects=51,inputsDigest=cur['inputsDigest'],
 changedFiles=[dict(**x,previousSha256=m[x['path']],entireCurrentContentDirectlyRead=True,comparison=reason,foreignFileModified=False) for x in delta],
 currentStudio=dict(path=studio.relative_to(ROOT).as_posix(),sha256=sha(studio),uiOnly=True,foreignUiWrites=0,clippedDescriptionsNotFullContent=True),
 previousReview=dict(path=(B/'content-review-v19.json').relative_to(ROOT).as_posix(),sha256=sha(B/'content-review-v19.json')),
 emptyExactMatchesUsedAsDecision=False,foreignFilesModified=0)
save(B/'current-normal-uv-manifest-review-v20.json',proof)
review=copy.deepcopy(read(B/'content-review-v19.json'))
review.update(reviewedAt=now,previousReview=proof['previousReview'],currentForeignChangeReview=proof['changedFiles'],addedWholeManifestReview=(B/'current-normal-uv-manifest-review-v20.json').relative_to(ROOT).as_posix(),gateStatus='awaiting-current-check')
review['inventory'].update(projectCount=51,inputsDigest=cur['inputsDigest'])
review['scope']+=' v20: entire changed normal/UV manifest and fresh actual current Studio rows directly compared.'
review['currentStudio']['currentList']=proof['currentStudio'];review.pop('gate',None)
save(B/'content-review-v20.json',review)
subprocess.run(['node','scripts/review-video-duplicates.cjs','similar-game-design','--decision','distinct','--reason',reason+' '+(B/'content-review-v20.json').relative_to(ROOT).as_posix(),'--studio-evidence',(B/'content-review-v20.json').relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
subprocess.run(['node','scripts/review-video-duplicates.cjs','similar-game-design','--check'],cwd=ROOT,check=True)
checked=read(R);assert checked['inputsDigest']==cur['inputsDigest']
review.update(gateStatus='current-distinct-check-passed',gate=dict(command='node scripts/review-video-duplicates.cjs similar-game-design --check',exitCode=0,checkedAt=now,inputsDigest=checked['inputsDigest']))
save(B/'content-review-v20.json',review);save(B/'inventory-prior-v20.json',checked)
cp=ROOT/'projects/similar-game-design/production/latest-checkpoint.json';c=read(cp)
c.update(currentDuplicateReview=(B/'content-review-v20.json').relative_to(ROOT).as_posix(),duplicateInputsDigest=checked['inputsDigest'],updatedAt=now);save(cp,c)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='similar-game-design')
i.update(currentDuplicateReview=c['currentDuplicateReview'],duplicateInputsDigest=checked['inputsDigest']);q['updatedAt']=now;save(qp,q)
print(json.dumps(dict(distinctPassed=True,projects=51,changedWholeManifest=1,foreignFilesModified=0)))
