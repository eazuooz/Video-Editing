"""Explicit semantic groups after all 61 KO/EN paragraphs were read together."""
from pathlib import Path
import importlib.util,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
ko=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
M.GROUPS={int(k['id']):[O]*len(re.split(r'(?<=[.!?])\s+',k['lines'][0].strip())) for k in ko}
M.GROUPS.update({
2:[O,(2,1),O,O],3:[O,O,O,(2,1),O,O,O,O],4:[(2,1),O,O],5:[O,O,O,(2,1)],
6:[O,(2,1),O,(2,1)],7:[(2,1),O,O,O],8:[O,(2,1),O,O],10:[O,(2,1),O,O,O],
11:[O,(2,1),O,O],12:[(2,1),O,O],14:[O,(2,1),O,O],15:[(2,1),O,O,(2,1)],
17:[(2,1),O,O,O],19:[O,(2,1),O,O],21:[O,(1,2),O,O],22:[O,O,(2,1),O,O],
23:[(2,1),O,O],24:[O,O,O,(2,1)],27:[O,O,O,O,O,(2,1),(1,2),O],29:[(2,1),O,O],
30:[O,(2,1),(2,1),O],31:[(2,1),O,O,O],32:[O,O,(2,1),O],34:[O,(2,1),O],
35:[(2,1),(2,1),O,O],37:[O,(2,1),O,O],38:[(2,1),O,O,O],39:[O,O,(2,1),O],
40:[O,O,O,(2,1)],42:[(2,1),O,(2,1),O],43:[(2,1),O,O],44:[(2,1),(2,1),O],
45:[(2,1),O],48:[(2,1),O,O,O],49:[O,(2,1)],50:[O,O,O,(2,1)],51:[(2,1),O,O],
53:[(2,1),O,O],54:[O,O,O,(2,1)],56:[O,(2,1),O,O],57:[O,(2,1),O,O],
58:[(2,1),O,(2,1)],59:[(2,1),O,O,O],60:[(3,1),O,O]})
if __name__=='__main__':M.main()
