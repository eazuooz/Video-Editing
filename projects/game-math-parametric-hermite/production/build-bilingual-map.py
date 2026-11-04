"""Semantic pairing after reading all 37 Korean/English paragraphs in order."""
from pathlib import Path
import importlib.util,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
ko=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
M.GROUPS={int(k['id']):[O]*len(re.split(r'(?<=[.!?])\s+',k['lines'][0].strip())) for k in ko}
M.GROUPS.update({2:[O,O,(2,2)],13:[O,(2,1),O,O],19:[(2,2),O,O],21:[O,O,(1,2),O],22:[(2,1),O,O],25:[(2,1),O,(1,2)],26:[O,(2,1),O,O],28:[O,(2,1),O,O],30:[(1,2),O,O,O],32:[(2,2),O,O],34:[O,O,(2,1)]})
if __name__=='__main__':M.main()
