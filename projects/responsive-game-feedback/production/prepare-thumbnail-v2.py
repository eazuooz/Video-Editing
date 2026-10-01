"""Prepare the approved generated thumbnail at the YouTube upload size."""
import json
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[3]
source = Path('C:/Users/eazuo/.codex/generated_images/01a0f1af-3710-7742-b7c9-87594dc45400/exec-1240aad3-670d-4ed6-82c7-b21ec2749b34.png')
destination = root / 'projects/responsive-game-feedback/publishing/thumbnail-v2.png'
destination.parent.mkdir(parents=True, exist_ok=True)
with Image.open(source) as image:
    image.convert('RGB').resize((1280, 720), Image.Resampling.LANCZOS).save(destination)
record = {
    'method': 'built-in image_gen',
    'revision': 'final-v2',
    'concept': 'Yellow strip, white background, large black Korean title and original coding cat. Selection, unavailable action and processing states illustrate input feedback; no official game character or logo copied.',
    'referenceStyle': 'docs/references/youtube-thumbnail-20261001.png',
    'generatedSource': source.as_posix(),
    'uploadImage': destination.relative_to(root).as_posix(),
    'dimensions': [1280, 720],
    'visualReview': 'Generated source directly inspected: 버튼 눌렀는데 / 왜 무반응?; label 게임 입력 피드백; selection, unavailable and processing states legible, no duration badge or false game screenshot.'
}
destination.with_name('thumbnail-v2-generation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(destination)
