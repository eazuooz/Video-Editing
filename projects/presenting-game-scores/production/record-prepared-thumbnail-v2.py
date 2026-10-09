"""Preserve and record the directly reviewed generated thumbnail; no pixel edits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
source = Path('C:/Users/eazuo/.codex/generated_images/01a0f1af-3710-7742-b7c9-87594dc45400/exec-6881dc7e-ae9d-49f1-bc12-a82e7e6cb2c6.png')
target = ROOT / 'projects/presenting-game-scores/publishing/thumbnail-v2.png'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if target.exists():
    assert sha(target) == sha(source), 'Preserve an existing different version'
else:
    shutil.copy2(source, target)
with Image.open(target) as im:
    dimensions = list(im.size)
assert target.stat().st_size < 2 * 1024 * 1024, 'Prepare a platform-sized asset before upload'
assert abs(dimensions[0] / dimensions[1] - 16 / 9) < .01
v1 = target.with_name('thumbnail-v1.png')
proof = dict(
    schemaVersion=1, slug='presenting-game-scores', reviewedAt=datetime.now(timezone.utc).isoformat(),
    generationMethod='built-in image_gen; targeted edit of preserved v1',
    sourceGeneratedPath=str(source), path=target.relative_to(ROOT).as_posix(), sha256=sha(target),
    bytes=target.stat().st_size, dimensions=dimensions, originalGeneratedFilePreserved=True,
    promptSummary='Keep the illustrated yellow header, white ground, natural calico cat with green scarf and all Korean typography. Correct only the left stack so three teal blocks are visible, matching the right stack; keep the quantity and score labels clear.',
    exactTexts=['얌얌코딩 | 게임 기획·디자인', '점수는 커졌는데', '뭘 잘한 걸까?', '이름 · 단위 · 비교 기준', '3개', '100점'],
    directVisualReview=dict(entireImageRead=True, brandingRead=True, headlineRead=True,
        quantityIllustrationThreeBlocksOnEachSide=True, naturalCatConceptIllustration=True,
        yellowHeaderWhiteGroundBlackRedHeadline=True, videoInset=False, pptOrFlowchartPaste=False,
        explanationBlackPaletteDoesNotChangeThumbnail=True),
    preservedRejectedCandidate=dict(path=v1.relative_to(ROOT).as_posix(), sha256=sha(v1),
        reason='The first candidate showed two visible left blocks beneath a 3개 label; corrected in v2.'),
    thumbnailPreparedVisualReviewApproved=True, essentialGitRegistryAdded=False, imagesGitAdded=0,
    actualVideoId=None, uploaded=False, savedPlatformThumbnailVerified=False, fullSettingsVerified=False,
    stage='prepared-only; final narrated video QA and private upload remain pending')
(BASE / 'prepared-thumbnail-direct-review-v2.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({k: proof[k] for k in ['path', 'sha256', 'bytes', 'dimensions', 'uploaded', 'imagesGitAdded']}, ensure_ascii=False))
