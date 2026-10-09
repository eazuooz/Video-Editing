"""Current mesh delivery change; preserve the sealed prior full-content review."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'production/batches/sakurai-planning-game-design/proof-similar-game-design'
REPORT = ROOT / 'production/batches/sakurai-planning-game-design/preflight/similar-game-design.json'
read = lambda path: json.loads(path.read_text('utf-8-sig'))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')


current = read(REPORT)
old = read(B / 'inventory-prior-v15.json')
old_map = {row['path']: row['sha256'] for row in old['inputFiles']}
changed = [row for row in current['inputFiles'] if old_map.get(row['path']) != row['sha256']]
assert current['inputsDigest'] == '63e3a22e94f91179c3f5bda95e98e7d22749df88c9563f713913f1af8a392fa2'
assert len(current['existingProjects']) == 50 and len(current['inputFiles']) == 352
expected = {
    'projects/game-math-mesh-uv/project.json': '8d250017739c19fd45b65029ebfe0c2b66bf4d68961c1648a002b3043933ede7',
    'projects/game-math-mesh-uv/publishing/youtube-upload.json': 'e3346891059c36f997fde4928e0f8971f5af50f16e99f19b9ddbe22c0acde40a',
}
assert {row['path']: row['sha256'] for row in changed} == expected
for row in current['inputFiles']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
receipt = read(ROOT / 'projects/game-math-mesh-uv/publishing/youtube-upload.json')
assert receipt['videoId'] == 'xnIA0EAJtiA' and receipt['status'] == 'actual-upload-in-progress;private-default-observed;settings-pending'
studio_path = ROOT / 'shared/output/similar-game-design/preflight/studio-current-mesh-v17.ax.txt'
studio = studio_path.read_text('utf-8')
assert '메시·법선 만들기' in studio and '43% 업로드 중' in studio and '곧 검토가 시작됨' in studio
comparison = '정점 공유·인덱스 메모리·면/정점 법선·누적·날카로운 모서리·각도 가중을 끝까지 설명하고 검산하는 수학 강의다. 친숙한 장르의 행동에 목적·공간·함께하는 방식의 조합을 더해 새 작품을 선택할 이유를 만드는 질문과 다르다. 현재 전체16장/100문단 KOEN은 v15에서 직접 읽은 바이트 그대로이며, 이번 두 변경 파일의 전체 본문과 실측 챕터/설명/계약을 직접 읽었다.'
proof = dict(schemaVersion=1, reviewedAt=now(), candidate='similar-game-design', inventoryProjects=50,
             inputFiles=352, inputsDigest=current['inputsDigest'], changedFilesCount=2,
             previousReview=dict(path='production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v15.json', sha256=sha(B / 'content-review-v15.json')),
             changedFiles=[dict(**row, previousSha256=old_map.get(row['path']), entireCurrentContentDirectlyRead=True,
                                comparison=comparison, foreignFileModified=False) for row in changed],
             currentStudio=dict(path=studio_path.relative_to(ROOT).as_posix(), sha256=sha(studio_path), uiOnly=True,
                                approximateTotal=487, visibleRows=30, currentChangedMeshRowDirectlyRead=True,
                                meshUploadObserved='43% upload; checks not started', meshActualIdFromCurrentReceipt='xnIA0EAJtiA', meshIdObservedInListRow=False,
                                priorV15RelatedFullContentAndStudioReviewsPreserved=True, clippedListDescriptionsNotFullMetadata=True,
                                existingPublishedAndScheduledRowsPreserved=True, foreignUploadModified=False, uiWrites=0),
             localInProgressReceiptNotClaimedAsPrivateSave=True, decision='distinct', emptyExactMatchesUsedAsDecision=False,
             mathematical40_60AndNoBgmExceptionCopied=False, foreignFilesModified=0)
save(B / 'current-mesh-delivery-change-review-v17.json', proof)
review = copy.deepcopy(read(B / 'content-review-v15.json'))
review.update(reviewedAt=now(), previousReview=proof['previousReview'],
              addedWholeScriptReview='production/batches/sakurai-planning-game-design/proof-similar-game-design/current-mesh-delivery-change-review-v17.json',
              currentForeignChangeReview=proof['changedFiles'], gateStatus='awaiting-current-check')
review['inventory'].update(projectCount=50, inputsDigest=current['inputsDigest'])
review['currentStudio']['currentList'] = proof['currentStudio']
review['scope'] += ' v17: current50-project/352-file inventory, two changed mesh manifest/actual in-progress publishing files fully read. Current Studio mesh upload is43% and checks pending, not a verified private delivery. Prior sealed full KOEN content and related Studio reviews remain evidence; this is not a fresh reread of all50 full scripts.'
review.pop('gate', None)
save(B / 'content-review-v17.json', review)
reason = comparison + ' 근거: production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v17.json'
subprocess.run(['node', 'scripts/review-video-duplicates.cjs', 'similar-game-design', '--decision', 'distinct', '--reason', reason,
                '--studio-evidence', 'production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v17.json'], cwd=ROOT, check=True)
subprocess.run(['node', 'scripts/review-video-duplicates.cjs', 'similar-game-design', '--check'], cwd=ROOT, check=True)
checked = read(REPORT)
assert checked['inputsDigest'] == current['inputsDigest']
review.update(gateStatus='current-distinct-check-passed', gate=dict(command='node scripts/review-video-duplicates.cjs similar-game-design --check', exitCode=0, checkedAt=now(), inputsDigest=checked['inputsDigest']))
save(B / 'content-review-v17.json', review)
save(B / 'inventory-prior-v17.json', checked)
cp_path = ROOT / 'projects/similar-game-design/production/latest-checkpoint.json'
cp = read(cp_path)
cp.update(currentDuplicateReview='production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v17.json', duplicateInputsDigest=checked['inputsDigest'], updatedAt=now())
save(cp_path, cp)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
queue = read(qp)
item = next(row for row in queue['items'] if row['slug'] == 'similar-game-design')
item.update(currentDuplicateReview=cp['currentDuplicateReview'], duplicateInputsDigest=checked['inputsDigest'])
queue['updatedAt'] = now()
save(qp, queue)
print(json.dumps(dict(currentDistinctPassed=True, projects=50, changedWholeContentFiles=2, foreignFilesModified=0)))
