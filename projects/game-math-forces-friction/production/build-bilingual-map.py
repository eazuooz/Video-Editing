"""M27 full 32-paragraph bilingual semantic reading, with exact meaning groups."""
from pathlib import Path
import importlib.util,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
ko=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
M.GROUPS={int(k['id']):[O]*len(re.split(r'(?<=[.!?])\s+',k['lines'][0].strip())) for k in ko}
M.GROUPS.update({0:[O,O,O,(2,1)],2:[(2,1),O,O,O],3:[O,O,(2,1),O],4:[(2,1),O,O,O,O],6:[(2,1),O,O,O],7:[O,(3,3),O],8:[O,O,(2,1),O],11:[O,O,O,(2,1)],12:[O,O,O,O,O,(2,1)],13:[(2,1),O,O,O],15:[(3,2),O,O],21:[(2,1),O,O,O],22:[O,(2,1),O,O],23:[(2,1),O,(2,1),O],24:[O,O,(2,1),O],28:[(2,1),O,O,O],29:[O,O,O,(2,1)],30:[O,O,(2,1),(2,1)],31:[O,(2,1),O,O]})
if __name__=='__main__':M.main()
