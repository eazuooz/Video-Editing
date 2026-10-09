import copy
import hashlib
import json
import pathlib
import subprocess
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[3]
B = ROOT / 'production/batches/sakurai-planning-game-design/proof-similar-game-design'
REPORT = ROOT / 'production/batches/sakurai-planning-game-design/preflight/similar-game-design.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


now = datetime.now(timezone.utc).isoformat()
current = read(REPORT)
previous_inventory = read(B / 'inventory-prior-v14.json')
previous_review = read(B / 'content-review-v14.json')
assert current['inputsDigest'] == 'dba505e07fdfd96966832067d62c2f6019762936d328b6af8f456b32c697430c'
assert len(current['existingProjects']) == 50
old = {row['path']: row['sha256'] for row in previous_inventory['inputFiles']}
changes = [row for row in current['inputFiles'] if old.get(row['path']) != row['sha256']]
assert len(changes) == 29
for row in current['inputFiles']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']

reasons = {
    'game-lighting-history-02': '포톤 매핑, 광원 목록, 선형/PBR, 노멀 매핑, 화면/프로브/평면 반사, LTC, 물과 볼륨의 저장·정보 손실을 설명한다. 친숙한 게임 행동의 목적·상황·조합으로 고유한 매력을 설계하는 질문과 다르다.',
    'game-lighting-history-03': 'SDF/복셀/BVH/BLAS/TLAS, 표본·PDF·히스토리, DDGI/ReSTIR, 컬링·메시 셰이더·나나이트·루멘의 계산과 재사용을 설명한다. 장르 작품의 선택 이유를 플레이 상황에서 비교하는 영상과 다르다.',
    'game-lighting-history-04': 'VSM/SMRT/TSR, 가시성 버퍼, 경로 표본과 레이 재구성, MegaLights, 투명도·후처리·프레임 자원 검사를 구분한다. 마지막 픽셀의 계산·복원 질문은 게임 목적과 경험의 조합 질문과 다르다.',
    'game-math-mesh-uv': '현재16장 전체는 정점·인덱스 메모리, 와인딩, 면/정점 법선, 법선 합산·날카로운 모서리·각도 가중과 연습문제이다. 노멀 변환과 UV는 다음 회차로 명시한다. 새 게임의 고유한 재미를 설계하는 질문과 다르다.',
    'game-math-camera-projection': '점→클립→화면 좌표 계산과 행렬·동차 나눗셈·연습문제를 완결한다. 실제 새 비공개 저장을 확인했으며 수학 설명과 게임의 목적·상황·매력 비교는 별개다.',
    'game-math-projection-depth': '투영 뒤 깊이, 보간, 시야/원근과 깊이 버퍼의 수학·연습문제이다. 실제 새 비공개 저장을 확인했으며 장르 작품의 행동·목적·경험 질문과 다르다.',
}
reviewed = []
for row in changes:
    slug = pathlib.PurePosixPath(row['path']).parts[1]
    item = dict(row, previousSha256=old.get(row['path']), entireCurrentContentDirectlyRead=True,
                foreignFileModified=False, comparison=reasons[slug])
    if row['path'].endswith('/sources/SOURCES.md') and slug in ['game-lighting-history-03', 'game-lighting-history-04']:
        item['readMethod'] = 'Byte-identical full-content reuse from the directly read game-lighting-history-02 SOURCES.md; SHA256 independently confirmed.'
        item['sameContentPath'] = 'projects/game-lighting-history-02/sources/SOURCES.md'
    if '/script/narration.' in row['path']:
        script = read(ROOT / row['path'])
        item['sceneCount'] = len(script['scenes'])
        item['paragraphCount'] = sum(len(scene['lines']) for scene in script['scenes'])
        item['allParagraphsDirectlyRead'] = True
    reviewed.append(item)

studio = ROOT / 'shared/output/similar-game-design/preflight/studio-current-v15.ax.txt'
assert studio.exists()
proof = {
    'schemaVersion': 1, 'reviewedAt': now, 'candidate': 'similar-game-design',
    'previousReview': {'path': 'production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v14.json', 'sha256': sha(B / 'content-review-v14.json')},
    'inventoryProjects': 50, 'inputsDigest': current['inputsDigest'], 'inputFiles': len(current['inputFiles']),
    'changedFilesCount': len(changes), 'changedFiles': reviewed,
    'wholeContentReviewMethod': 'Direct whole-text reads of current KO/EN paragraphs and changed manifest/outline/source/README/receipt content. Unchanged historical inventories and related full-script reviews retain their sealed prior evidence. This does not claim rereading every full script of all50 projects.',
    'actualCurrentStudio': {
        'uiOnly': True, 'path': studio.relative_to(ROOT).as_posix(), 'sha256': sha(studio),
        'all30VisibleRowsDirectlyRead': True, 'approximateTotal': 486,
        'cameraPrivateId': 'c96qTnlHBVU', 'projectionDepthPrivateId': 'PuXZUArWFko',
        'cameraCurrentReceiptWholeContentRead': True, 'projectionDepthCurrentReceiptWholeContentRead': True,
        'oldProjectionDepthToDoRowSupersededByObservedPrivateSave': True,
        'listDescriptionsAreTruncated': True,
        'priorFiveRelatedFullDescriptionsAndChapterListsRetained': True,
        'existingUserSchedulesPreserved': ['xtUVcAHtQzg', 'gSN8tbGkJ5E', '6-k orientation row', 'ZLO polar row'],
        'uiWrites': 0,
    },
    'decision': 'distinct', 'emptyExactMatchesUsedAsDecision': False,
    'mathematicalLectureRatioAndNoBgmExceptionCopied': False, 'foreignFilesModified': 0,
    'finalMixOrFinalPixelsApprovedByThisRecord': False,
}
write(B / 'current-foreign-delivery-change-review-v15.json', proof)
write(B / 'inventory-observed-v15.json', current)
review = copy.deepcopy(previous_review)
review.update(reviewedAt=now, previousReview=proof['previousReview'],
              addedWholeScriptReview='production/batches/sakurai-planning-game-design/proof-similar-game-design/current-foreign-delivery-change-review-v15.json',
              currentForeignChangeReview=reviewed, gateStatus='awaiting-current-check')
review['inventory']['projectCount'] = 50
review['inventory']['inputsDigest'] = current['inputsDigest']
review['scope'] += ' Latest v15 directly reviews29 changed/additional files against the46-project v14 inventory: lighting02/03/04 complete current KOEN and all companions, mesh16-scene100-paragraph KOEN and companions, and current camera/depth manifests and actual saved-private receipts. Current inventory is50 projects/351 input files. The two identical lighting source documents reuse the directly read identical02 content. Current Studio30 rows and actual private camera/depth delivery are observed; clipped list descriptions are not claimed as full metadata reads.'
review['currentStudio']['currentList'] = proof['actualCurrentStudio']
review.pop('gate', None)
write(B / 'content-review-v15.json', review)
reason = '기존 전체 개념과 관련 전체 KOEN에 더해 현재50프로젝트의29변경파일 전체본문 및 실제 Studio를 직접 비교. 조명·가시성·법선·투영/깊이 수학은 친숙한 행동의 목적·상황·조합으로 새 작품의 고유한 매력을 만드는 질문과 다름. 근거: production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v15.json'
subprocess.run(['node', 'scripts/review-video-duplicates.cjs', 'similar-game-design', '--decision', 'distinct', '--reason', reason, '--studio-evidence', 'production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v15.json'], cwd=ROOT, check=True)
subprocess.run(['node', 'scripts/review-video-duplicates.cjs', 'similar-game-design', '--check'], cwd=ROOT, check=True)
checked = read(REPORT)
assert checked['inputsDigest'] == current['inputsDigest']
review['gateStatus'] = 'current-distinct-check-passed'
review['gate'] = {'command': 'node scripts/review-video-duplicates.cjs similar-game-design --check', 'exitCode': 0, 'checkedAt': datetime.now(timezone.utc).isoformat(), 'inputsDigest': checked['inputsDigest']}
write(B / 'content-review-v15.json', review)
write(B / 'inventory-prior-v15.json', checked)
cp_path = ROOT / 'projects/similar-game-design/production/latest-checkpoint.json'
cp = read(cp_path)
cp['currentDuplicateReview'] = 'production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v15.json'
cp['duplicateInputsDigest'] = checked['inputsDigest']
cp['updatedAt'] = datetime.now(timezone.utc).isoformat()
write(cp_path, cp)
print(json.dumps({'currentDistinctPassed': True, 'projects': 50, 'changedWholeContentFiles': 29, 'inputsDigest': checked['inputsDigest']}))
