"""M29 semantic grouping after all 38 KO/EN paragraphs were read side by side."""
from pathlib import Path
import importlib.util,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
ko=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))['scenes']
M.GROUPS={int(k['id']):[O]*len(re.split(r'(?<=[.!?])\s+',k['lines'][0].strip())) for k in ko}
M.GROUPS.update({1:[O,(2,1),O,O],2:[(2,1),O,O,O],3:[O,(2,1),O,O],9:[O,(2,1),O,O],11:[(2,1),O,O],12:[O,(2,1),O,O],13:[O,O,(2,1),O],14:[O,O,O,O,O,(2,1),O],15:[O,O,O,(2,1)],18:[O,O,(2,1),O,(2,2)],19:[(2,1),O,O,O],21:[O,O,(2,1),O],23:[O,O,(2,1),O,O],24:[O,(2,1),O,O],26:[O,O,(2,1),O],27:[(2,1),O,O],28:[O,O,(2,1),O,O],30:[(2,2),O,O],34:[(2,1),O,O,O],36:[O,O,O,O,(2,1)],37:[(2,1),O,O]})
if __name__=='__main__':M.main()
