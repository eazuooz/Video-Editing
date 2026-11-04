"""M25 full semantic sentence groups, after reading all 39 bilingual paragraphs."""
from pathlib import Path
import importlib.util,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
ko=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
M.GROUPS={int(k['id']):[O]*len(re.split(r'(?<=[.!?])\s+',k['lines'][0].strip())) for k in ko}
M.GROUPS.update({1:[O,O,(2,1),O,O],2:[(2,1),O,(1,2)],3:[O,O,O,(2,1),O],4:[O,O,(2,1),O,O],6:[(2,1),O,O,O],7:[O,O,(1,2),O,O],11:[O,O,(2,1),(1,2)],14:[(2,1),O,(2,2),O],15:[O,O,(2,2),O],16:[(2,1),O,O,O,O],19:[O,O,(1,2),O],24:[O,(2,1),O,O],27:[O,O,O,(2,2)],30:[O,O,(2,1),(1,2)],33:[O,(2,1),O],35:[(1,2),O,O,O,O],36:[(2,2),O,O,O],37:[O,O,O,(1,2),O]})
if __name__=='__main__':M.main()
