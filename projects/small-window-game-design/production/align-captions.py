"""Use the shared word alignment with narrower, HUD-safe Korean captions."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'qwen3-tts'))
import align_project_subtitles as align

normalize = align.normalized
def normalized_terms(text):
    # Whisper writes spoken ratios and abbreviations as digits/Latin letters.
    return normalize(text.lower().replace('16', '십육').replace('21', '이십일').replace('9', '구').replace('fov', '에프오브이'))
align.normalized = normalized_terms

split, partition, wrap = align.split_caption, align.partition_fixed, align.wrapped_lines
align.split_caption = lambda text, width: split(text, 24 if width == 32 else width)
align.partition_fixed = lambda text, width, count: partition(text, 24 if width == 32 else width, count)
align.wrapped_lines = lambda text, width: wrap(text, 24 if width == 32 else width)
sys.argv = [sys.argv[0], '--project', 'small-window-game-design']
align.main()
