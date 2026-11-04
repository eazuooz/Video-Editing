"""Semantic pairing after all 43 KO/EN paragraphs were read in source order."""
from pathlib import Path
import importlib.util,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
ko=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
M.GROUPS={int(k['id']):[O]*len(re.split(r'(?<=[.!?])\s+',k['lines'][0].strip())) for k in ko}
M.GROUPS.update({3:[O,O,(2,1)],6:[(2,1),O,O],9:[O,(1,3),O,O],10:[O,O,(2,1),O],11:[(2,1),O,O,O],12:[O,(1,2),O,O],14:[O,(2,1),O,O],21:[O,(2,2),O,O],25:[O,O,(2,1)],26:[O,(2,1),O],28:[O,(2,1),(1,2),O],32:[O,(2,1),O],33:[O,O,(2,2)],36:[O,(1,2),O,O],37:[O,O,(2,1)],42:[(2,1),O,O,O,O,O]})
if __name__=='__main__':M.main()
