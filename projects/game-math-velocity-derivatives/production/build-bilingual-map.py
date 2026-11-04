"""M24 semantic sentence groups after full side-by-side source-order review."""
from pathlib import Path
import importlib.util,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
ko=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
M.GROUPS={int(k['id']):[O]*len(re.split(r'(?<=[.!?])\s+',k['lines'][0])) for k in ko}
M.GROUPS.update({0:[O,O,(2,1),O],6:[O]*3+[(2,1),O],7:[O,O,(2,1),O,O],10:[O,O,(2,1),O,O],12:[(3,2),(2,1),O],13:[O]*3+[(2,1)],14:[(2,1)]+[O]*4,16:[O]*3+[(2,1),O],19:[O]*3+[(2,1),O],22:[O,(2,1),O,O,O],23:[O,O,O,(2,1),O],24:[O,(2,1),O,O,(1,2)],25:[(2,1)]+[O]*4,26:[O]*4+[(2,1)],27:[(2,1),(2,1),O,O],28:[O]*3+[(2,1),O],32:[O]*6+[(2,1),O],34:[(2,1),O,O,O],36:[O]*3+[(2,1),O],38:[O,(1,2)]+[O]*4,41:[O,(2,1),(2,1),O,O],42:[O,O,(2,1),O,O,O],44:[(2,1),(2,2),O,O],45:[(2,1),O,(1,2),O]})
if __name__=='__main__':M.main()
