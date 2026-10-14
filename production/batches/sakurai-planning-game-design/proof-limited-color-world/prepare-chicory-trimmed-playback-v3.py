"""Preserve v2; independent timeupdate end guard and explicit local page width."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
raw=ROOT/'shared/assets/presenting-game-scores/raw'
out=raw/'limited-chicory-trimmed-framing-v3.html';assert not out.exists()
s=(raw/'limited-chicory-trimmed-framing-v2.html').read_text(encoding='utf-8')
s=s.replace('Chicory trimmed framing review v2','Chicory trimmed framing review v3')
s=s.replace('body{margin:16px;','body{width:1264px;min-height:900px;margin:16px;')
s=s.replace('width:min(1920px,100%);','width:1264px;')
s=s.replace("document.getElementById('prepare').onclick", "v.addEventListener('timeupdate',()=>{if(active&&current&&v.currentTime>=current.sourceEndSecondsExclusive){active=false;v.pause();draw();status.textContent='수정 컷 재생 완료 (timeupdate guard)';log('end-timeupdate')}else{draw();show()}});\ndocument.getElementById('prepare').onclick")
out.write_text(s,encoding='utf-8')
print('Preserved v2; v3 local page prepared. Existing9250 and original media reused. No source decode/render.')
