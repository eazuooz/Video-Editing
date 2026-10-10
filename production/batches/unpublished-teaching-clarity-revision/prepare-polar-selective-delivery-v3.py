"""Prepare a reviewable explicit selection; this does not stage or commit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[3]
git = Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
revision = 'projects/game-math-polar-3d/revision-teaching-clarity-v1'
batch = 'production/batches/unpublished-teaching-clarity-revision'
destination = root / revision / 'publishing/git-source-selection-v3.json'
assert not destination.exists(), 'Read the existing prepared selection before changing it'
receipt = json.loads((root / revision / 'publishing/youtube-upload-v3.json').read_text('utf-8-sig'))
assert receipt['actualVideoId'] == '2kNMDlrwdU8'
allowed_extensions = {'.json', '.md', '.py', '.cjs', '.ts', '.tsx', '.meta', '.srt', '.ass', '.csv', '.html'}
excluded_parts = {'__pycache__', 'raw', 'assets', 'frames', 'boards', 'delivery-history', 'node_modules', '.git'}
selected, excluded = [], []
for directory in [revision, batch]:
    for file in (root / directory).rglob('*'):
        if not file.is_file() or file.is_symlink():
            continue
        relative = file.relative_to(root).as_posix()
        forbidden = any(part in excluded_parts for part in file.relative_to(root / directory).parts)
        text_description = file.name in {'upload-description.ko.txt', 'upload-description.en.txt'}
        if forbidden or file.name.endswith(('.ax.txt', '.info.json')) or (file.suffix not in allowed_extensions and not text_description):
            excluded.append(relative)
            continue
        selected.append(relative)
selected.extend([
    'projects/game-math-polar-3d/project.json',
    'projects/game-math-polar-3d/planning/outline.md',
    'projects/game-math-polar-3d/production/timeline.json',
    'projects/game-math-polar-3d/production/qa.json',
    'projects/game-math-polar-3d/production/delivery-output.json',
    'projects/game-math-polar-3d/sources/game-candidates.json',
    'projects/game-math-polar-3d/sources/gameplay-cuts.json',
    'projects/game-math-polar-3d/rebuild.json',
    'templates/video-project/planning/outline.md',
    'templates/video-project/checklist.md',
])
selected = sorted(set(selected))
shared = {
    'AGENTS.md': ['- Opening, coherent examples and unpublished revisions,', '- Clear gameplay selection and on-footage math,'],
    'docs/VIDEO_WORKFLOW.md': ['## 개론·이해하기 쉬운 사례·유기적 연결, 공개 전 영상에도 적용', '## 실제 게임 자료의 이해도 비교와 수학 오버레이'],
    'docs/VIDEO_GAME_FOOTAGE_POLICY.md': ['## 이해가 잘되는 실제 장면 비교와 화면 위 수학 해설', '## 처음 보는 사람의 이해도와 참고 게임 선택'],
    'docs/VIDEO_VISUAL_STYLE.md': ['2026-10-10 최신 적용 범위:', '## 실제 게임 화면 위에 수학 표시와 비교를 그리기'],
}
def run(*args):
    return subprocess.check_output([str(git), *args], cwd=root).decode('utf-8').strip()
head = run('rev-parse', 'HEAD')
external_index = Path(run('rev-parse', '--git-path', 'index'))
if not external_index.is_absolute():
    external_index = root / external_index
record = {
    'schemaVersion': 1, 'slug': 'game-math-polar-3d', 'actualVideoId': receipt['actualVideoId'],
    'preparedAt': datetime.now(timezone.utc).isoformat(), 'actualHeadAtPreparation': head,
    'status': 'prepared-selection-only-awaiting-complete-private-settings',
    'selectedSourcePaths': selected,
    'sourceSha256AtPreparation': {file: hashlib.sha256((root / file).read_bytes()).hexdigest() for file in selected},
    'additionalSelectionRecordPath': destination.relative_to(root).as_posix(),
    'sharedFilesRequireOwnedOnlyMergeFromActualHead': shared,
    'excludedLocalPaths': sorted(excluded),
    'oldBaselineUploadReceiptExcluded': 'projects/game-math-polar-3d/publishing/youtube-upload.json',
    'oldReceiptReason': 'Unrelated historical Git receipt differs from HEAD; preserved locally and in the baseline snapshot, not silently delivered as this revision.',
    'rasterAutomaticallySelected': [], 'newRasterMustBeIndividuallyReviewedRegisteredAndExactIgnored': True,
    'externalIndexSha256AtPreparation': hashlib.sha256(external_index.read_bytes()).hexdigest(),
    'externalIndexMustStayByteAndEntryIdentical': True,
    'staged': False, 'committed': False, 'pushed': False,
}
destination.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'explicitTextPaths': len(selected), 'sharedOwnedOnlyFiles': len(shared), 'raster': 0, 'staged': False, 'committed': False}))
