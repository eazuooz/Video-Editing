"""M28 all 25 bilingual paragraphs reviewed; preserve matching meaning groups."""
from pathlib import Path
import importlib.util,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
ko=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
M.GROUPS={int(k['id']):[O]*len(re.split(r'(?<=[.!?])\s+',k['lines'][0].strip())) for k in ko}
M.GROUPS.update({1:[O,O,O,O,O,(2,1)],2:[O,O,O,(2,2)],4:[(2,1),O,O,O],6:[(2,1),(1,2),O,O],8:[O,(2,1),O,O,O],9:[(2,1),O,O,(2,1)],10:[O,O,O,(2,1),O],11:[O,(2,1),O,(2,1)],13:[(2,1),O,O,O,O],14:[(2,1),(2,1),O,O,O],16:[O,O,(3,1),(2,1),O],17:[O,O,(2,1),O,O],19:[O,(2,1),O],21:[O,O,O,(2,1)],24:[(2,1),O,(2,1)]})
if __name__=='__main__':M.main()
