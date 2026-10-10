"""Only add visible contours at their narrated comparison points."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
observed={
'o17bike-landmarks.json':{853:[[132,311],[229,239]],854:[[143,308],[251,238]],855:[[143,311],[241,240]]},
'o20-landmarks.json':{1038:[[347,285],[378,361]],1039:[[289,298],[303,364]],1040:[[368,283],[391,355]],1041:[[365,290],[381,366]],1042:[[325,292],[326,370]],1043:[[363,319],[392,385]],1044:[[317,325],[339,395]],1045:[[300,300],[313,360]],1046:[[293,315],[306,389]]},
'o23-landmarks.json':{1095:[[344,295],[361,357]],1096:[[325,303],[334,385]],1098:[[291,223],[298,284]],1101:[[304,321],[304,386]],1102:[[299,342],[267,407]],1103:[[299,300],[292,364]],1104:[[314,346],[311,412]],1105:[[358,342],[384,407]]}
}
for file,points in observed.items():
 p=B/file;v=read(p)
 for row in v['keyframes']:
  if row['t'] in points:row['wheel']=points[row['t']]
 write(p,v)
reg=read(B/'quaternion-annotation-tracks.json')
for ident,line in [('17',5),('20',5),('23',1)]:reg['scenes'][ident].update(showWheel=True,blueAtLine=line,blueLabel='보이는 바퀴 선')
write(B/'quaternion-annotation-tracks.json',reg)
print('Three narrated projected-wheel comparisons; moving review pending')
