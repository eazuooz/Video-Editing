"""Source-faithful Korean/English sentence groups checked side by side."""
from pathlib import Path
import importlib.util
P=Path(__file__).resolve().parents[1];R=P.parents[1]
s=importlib.util.spec_from_file_location('groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M);M.P=P
O=(1,1)
M.GROUPS={0:[O]*4,1:[(2,1),O,O],2:[(2,1),O,O],3:[(3,1),(2,1),O],4:[O]*4,5:[O]*5,6:[O,(2,1),O],7:[O]*4,8:[O,O,(2,1),O],9:[O,O,(2,1),O,(2,1),O],10:[O]*5,11:[O,(2,1),O,O],12:[O,(2,2),O,O],13:[O,O,(2,1),O],14:[(2,1),O,O],15:[O]*4,16:[(3,1),O,O,O],17:[(2,1),O,O,O],18:[(2,1),O,O,O],19:[O]*4,20:[O,(3,1),O],21:[(2,1),O,O,O],22:[O]*4,23:[(3,1),O,(2,1)],24:[O,(2,1),O,O],25:[O,O,(2,1),O],26:[O]*3+[(2,1)],27:[O]*3+[(2,1)],28:[O]*6,29:[O,O,(2,1),O,O],30:[(2,1),O,O,O],31:[O,(2,1),O,O],32:[O]*4,33:[(2,1),O,O],34:[(2,1),O,O,O],35:[O,(2,1),O,O,O],36:[O,O,(2,1),O,O],37:[O,O,(2,1),O],38:[O]*4,39:[O,(2,1),O,O,O],40:[(2,1),O,(2,1),O],41:[O,(2,1),O,O],42:[O,(2,1),O,O],43:[O,(2,1),O],44:[(2,1),O,O],45:[O,(3,2),O],46:[(2,1),O,O],47:[O]*5,48:[O]*4,49:[O,(2,1),O],50:[O]*3,51:[(2,1),O,O]}
M.GROUPS[12]=[O,(2,2),(2,1)]
M.GROUPS.update({52:[(2,1),O,(2,1),O],53:[O]*5,54:[(2,1),(2,1),O,O],55:[O]*3+[(2,1)],56:[O]*5,57:[O,O,(2,1),O],58:[O]*4,59:[O]*6,60:[O]*5,61:[O,(2,1),O,O,O],62:[(3,1),O,O],63:[(3,1),(2,1)],64:[O]*4,65:[O]*5,66:[(2,1),(2,1),O],67:[O,O,(2,1)]})
if __name__=='__main__':M.main()
