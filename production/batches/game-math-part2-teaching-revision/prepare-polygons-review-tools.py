"""Adapt pure editor authoring/extraction helpers without granting approvals."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
names=['editor','composition-review','final-caption-review','detail-review','explanation-review']
for name in names:
 text=(B/f'prepare-planes-{name}.py').read_text(encoding='utf8')
 for old,new in [('game-math-plane-distances-v2','game-math-polygon-centers-v2'),('game-math-triangle-addresses-v2','game-math-polygon-partition-v2'),('planes-annotation-tracks','polygons-annotation-tracks'),('planes_additions','polygons_additions'),('teaching-revision/planes','teaching-revision/polygons'),('평면·삼각형 좌표','다각형 중심·경계·분할'),('평면·삼각형','다각형')]:text=text.replace(old,new)
 (B/f'prepare-polygons-{name}.py').write_text(text,encoding='utf8')
text=(B/'audit-planes-preservation.py').read_text(encoding='utf8')
for old,new in [('game-math-planes-barycentric','game-math-polygons-triangulation'),('game-math-plane-distances-v2','game-math-polygon-centers-v2'),('game-math-triangle-addresses-v2','game-math-polygon-partition-v2'),('planes-preservation-audit','polygons-preservation-audit')]:text=text.replace(old,new)
(B/'audit-polygons-preservation.py').write_text(text,encoding='utf8')
print('Independent editable scenes and current-pixel extraction helpers prepared; approval unchanged.')
