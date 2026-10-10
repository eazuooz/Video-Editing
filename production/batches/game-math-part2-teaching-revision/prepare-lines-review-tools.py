"""Adapt reviewed tools only to this chapter; never alter completed interpolation."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
for original,target in [('extract-interpolation-moving-pixels.py','extract-lines-moving-pixels.py'),('prepare-interpolation-editor.py','prepare-lines-editor.py')]:
 text=(B/original).read_text(encoding='utf8').replace('game-math-interpolation-paths-v2','game-math-lines-circles-v2').replace('game-math-rotation-conversions-v2','game-math-bounds-transform-v2').replace('interpolation-annotation-tracks.json','lines-annotation-tracks.json')
 (B/target).write_text(text,encoding='utf8')
print('Line/bounds dense moving-pixel and independent editor tools prepared.')
