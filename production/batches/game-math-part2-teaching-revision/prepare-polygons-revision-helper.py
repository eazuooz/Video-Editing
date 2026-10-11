"""Derive a polygon-specific freeze/voice guard from the reviewed additive workflow."""
from pathlib import Path
B=Path(__file__).parent
s=(B/'prepare-planes-revision.py').read_text(encoding='utf8')
s=s.replace('game-math-planes-barycentric','game-math-polygons-triangulation')
s=s.replace('game-math-planes-teaching-additions-v2','game-math-polygons-teaching-additions-v2')
s=s.replace('planes-','polygons-').replace('planes_additions.py','polygons_additions.py')
s=s.replace('wsxSYEEj8aQ','L7SXFwn4i2k').replace("'PF01' if number==1 else 'PF03'","'QF01' if number==1 else 'QF03'")
s=s.replace("s['id'].startswith('PF')","s['id'].startswith('QF')").replace("len(checks)==21","len(checks)==25")
s=s.replace('평면과 삼각형: 새 기초 설명과 유기적 연결','다각형: 중심·경계·분할의 기초와 유기적 연결')
s=s.replace('Lines/bounds second private upload active; plane/triangle compared gameplay and preserved scripts/math ready, current research boundary required before new TTS',
 'Both plane private episodes complete; polygon compared gameplay and preserved scripts/math ready; current research boundary required before new-only TTS')
(B/'prepare-polygons-revision.py').write_text(s,encoding='utf8')
s=(B/'render-planes-narration.py').read_text(encoding='utf8').replace('game-math-planes-teaching-additions-v2','game-math-polygons-teaching-additions-v2').replace('planes-','polygons-')
(B/'render-polygons-narration.py').write_text(s,encoding='utf8')
print('Prepared polygon-specific new-only script and narration guards.')
