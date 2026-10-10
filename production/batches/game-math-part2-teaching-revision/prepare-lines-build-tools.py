"""Derive the scoped lines delivery tool from the already reviewed pair builder."""
from pathlib import Path
import ast
B=Path(__file__).parent
s=(B/'build-interpolation-episodes.py').read_text(encoding='utf8')
replacements={
 "game-math-interpolation-paths-v2":"game-math-lines-circles-v2",
 "game-math-rotation-conversions-v2":"game-math-bounds-transform-v2",
 "game-math-rotation-interpolation":"game-math-lines-bounds",
 "/interpolation'":"/lines'",
 "create-interpolation-overlay.py":"create-lines-overlay.py",
 "interpolation-annotation-tracks.json":"lines-annotation-tracks.json",
 "interpolation_additions":"lines_additions",
 "track.get('landmarkSources',[track.get('landmarks')])+track.get('blueLandmarkSources',[])":"track['landmarkSources']",
 "if ident in ['IP04','IP08']:":"if not slot['preservedOriginal']:",
}
for old,new in replacements.items():
 assert old in s,old
 s=s.replace(old,new)
ast.parse(s);(B/'build-lines-episodes.py').write_text(s,encoding='utf8')
print('Scoped lines build tools parsed; source tracks/render/pixels still required.')
