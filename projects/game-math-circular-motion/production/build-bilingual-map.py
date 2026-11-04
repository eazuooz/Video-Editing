"""M26 semantic groups from direct full bilingual reading, 40 paragraphs."""
from pathlib import Path
import importlib.util,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
ko=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
M.GROUPS={int(k['id']):[O]*len(re.split(r'(?<=[.!?])\s+',k['lines'][0].strip())) for k in ko}
M.GROUPS.update({1:[(2,2),O,O,O],7:[O,(2,1),O,(2,2)],9:[O,(2,1),O,O],13:[O,(2,1),O,O],14:[(3,2),O,O],19:[(2,1),O,O],20:[O,O,(1,2),O,O],22:[O,O,O,(2,1)],23:[(2,1),O,O],26:[O,O,(1,2),O],29:[(2,1),O,O,O],31:[(2,1),O,O,O],33:[O,(2,2),(1,2)],35:[O,(2,1),O,O],36:[(2,1),O,(2,1),O],37:[(2,1),O,(2,1),(1,2)]})
if __name__=='__main__':M.main()
