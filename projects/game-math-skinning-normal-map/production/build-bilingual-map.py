"""M22 corresponding sentence groups, directly checked in both languages."""
from pathlib import Path
import importlib.util
P=Path(__file__).resolve().parents[1];R=P.parents[1]
spec=importlib.util.spec_from_file_location('checked_bilingual_groups',R/'projects/game-math-shading-lights/production/build-bilingual-map.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M);M.P=P
O=(1,1)
M.GROUPS={
0:[O]*4,1:[(2,1),O,(2,1)],2:[O]*6,3:[O]*5,4:[O]*3+[(2,1)],5:[(3,1),O,O],
6:[O,O,(2,1),O],7:[O,(2,1),O,O],8:[(2,1),(2,1),(1,2)],9:[(3,1),O,O],
10:[O]*3,11:[O]*3+[(2,1)],12:[(2,1),O,O],13:[O,O,(2,1)],14:[O]*3+[(2,1)],
15:[O]*4+[(2,1),(2,1)],16:[O,(2,1),O],17:[O,O,(2,1),O],18:[(2,1),(2,1),O],
19:[(2,1),O,O,O],20:[O,O,(2,2)],21:[(2,1),O,(2,1)],22:[O,(2,1),O],23:[O]*4,
24:[(2,1),(3,1),(2,1)],25:[(2,1),O,O,O],26:[(2,1),O,O,O],27:[O]*4,
28:[(2,1),O,(2,1),O],29:[(2,2),O,(2,1)],30:[O,(2,1),(2,1)],31:[O,(2,1),O,O],
32:[(3,1),O,O],33:[O]*3+[(2,1)],34:[O]*3,35:[O]*3}
if __name__=='__main__':M.main()
