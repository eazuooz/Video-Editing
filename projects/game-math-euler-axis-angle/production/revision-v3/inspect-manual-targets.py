"""Exact source frames for correcting fast rotations and traced road boundaries."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3';sys.path.insert(0,str(O/'deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
src=json.loads((P/'sources/cut-plan-v3.json').read_text(encoding='utf8'))['sources'];out=O/'manual-frames';out.mkdir(exist_ok=True)
groups={
 'raft-trace':('YNQ20CKbY8U',[1026,1027,1028,1029,1030,1031,1032,1033,1034]),
 'hook':('YNQ20CKbY8U',[240.5,241,241.5,242,242.5,243]),
 'logs':('YNQ20CKbY8U',[418.5,419,419.5,420,420.5,421]),
 'mast':('YNQ20CKbY8U',[1000,1000.5,1001,1001.5,1002,1002.5,1003,1003.5,1004,1004.5,1005,1005.5,1006,1006.5,1007]),
 'road05':('dbA2StfJhqw',[115,115.5,116,116.5,117,117.5,118,118.5,119,119.5]),
 'road11':('dbA2StfJhqw',[244,244.5,245,245.5,246,246.5,247,247.5]),
 'road23':('dbA2StfJhqw',[379.5,380,380.5,381,381.5,382,382.5,383]),
 'glider05':('dbA2StfJhqw',[220,220.5,221,221.5,222,222.5,223])}
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',24)
for name,(sid,times) in groups.items():
 if len(sys.argv)>1 and name not in sys.argv[1:]:continue
 cap=cv2.VideoCapture(str(R/src[sid]['file']));ims=[]
 for t in times:
  cap.set(cv2.CAP_PROP_POS_FRAMES,round(t*60));ok,f=cap.read();assert ok
  im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB));im.save(out/f'{name}-{t:.1f}.jpg',quality=94)
  im=im.resize((640,360));d=ImageDraw.Draw(im);d.rectangle([0,0,190,30],fill='black');d.text((3,2),str(t),font=font,fill='yellow');ims.append(im)
 cap.release()
 for offset in range(0,len(ims),12):
  part=ims[offset:offset+12];board=Image.new('RGB',(1920,360*((len(part)+2)//3)))
  for j,im in enumerate(part):board.paste(im,((j%3)*640,(j//3)*360))
  board.save(out/f'{name}-board-{offset//12+1}.jpg',quality=92)
 print(name,flush=True)
