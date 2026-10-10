"""Small native-frame coordinate references for the remaining actual shots."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[3];script=Path(__file__).with_name('prepare-landmark-frames.py')
windows=[('GB03','_dw9jjRpanA',558,575),('GB04','_dw9jjRpanA',651,668),('O02','4Odvp_TIeQU',3,20),('O05','4Odvp_TIeQU',51,68),('O08','4Odvp_TIeQU',99,116),('O11ski','4Odvp_TIeQU',195,206),('O11wing','4Odvp_TIeQU',552,569),('O14','4Odvp_TIeQU',734,751),('O17board','4Odvp_TIeQU',782,794),('O17bike','4Odvp_TIeQU',838,855),('O20','4Odvp_TIeQU',1038,1055),('O23','4Odvp_TIeQU',1088,1105)]
for ident,source,a,b in windows:
 folder=ROOT/'shared/output/game-math-part2-teaching-revision/landmark-authoring'/ident
 if (folder/'frames.json').exists():continue
 subprocess.run([sys.executable,'-X','utf8',str(script),ident,source,str(a),str(b),'--step','1'],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
