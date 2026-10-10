"""Compare two previously observed official moving-surface demonstrations."""
from pathlib import Path
import shutil
B=Path(__file__).parent;ROOT=B.parents[2]
O=ROOT/'shared/output/game-math-part2-teaching-revision/planes-moving-surfaces';O.mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'shared/output/game-math-part2-teaching-revision/planes-source-candidates/portal2-official-movies.json',O/'portal2-official-movies.json')
source=(B/'prepare-planes-portal-secondary.py').read_text(encoding='utf8')
assert '[5926,5786]' in source
source=source.replace('planes-portal-secondary','planes-moving-surfaces').replace('[5926,5786]','[80739,5790]')
exec(compile(source,str(B/'prepare-planes-portal-secondary.py'),'exec'))
