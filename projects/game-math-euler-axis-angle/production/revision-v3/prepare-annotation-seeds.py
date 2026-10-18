"""Extract real source frames for hand selection; never infer a target from a title."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3';sys.path.insert(0,str(O/'deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
src=json.loads((P/'sources/cut-plan-v3.json').read_text(encoding='utf8'))['sources']
rows=[('02-kart','dbA2StfJhqw',3),('02-bank','dbA2StfJhqw',12),('02-glide','dbA2StfJhqw',27),('05-kart','dbA2StfJhqw',111),('05-glide','dbA2StfJhqw',180),('08-hook','YNQ20CKbY8U',237),('08-logs','YNQ20CKbY8U',416),('11-bank','dbA2StfJhqw',243),('11-wall','dbA2StfJhqw',285),('14-mario','_wH_-1saHnw',1099),('14-turn','_wH_-1saHnw',1113),('17-jump','_wH_-1saHnw',1330),('17-air','_wH_-1saHnw',1346),('17-run','_wH_-1saHnw',1402),('20-log','YNQ20CKbY8U',399),('20-raftlog','YNQ20CKbY8U',990),('20-mast','YNQ20CKbY8U',1000),('20-raft','YNQ20CKbY8U',1014),('20-platform','YNQ20CKbY8U',264),('23-bank','dbA2StfJhqw',378),('23-glide','dbA2StfJhqw',387)]
out=O/'annotation-seeds';out.mkdir(exist_ok=True);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25);pages={}
for i,(name,source,t) in enumerate(rows):
 cap=cv2.VideoCapture(str(R/src[source]['file']));cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=cap.read();assert ok;(out/(name+'.json')).write_text(json.dumps(dict(name=name,source=source,sourceTime=t,decodedFrame=cap.get(cv2.CAP_PROP_POS_FRAMES)-1)));cap.release()
 im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));im.save(out/(name+'.jpg'),quality=90)
 thumb=im.resize((480,270));d=ImageDraw.Draw(thumb);d.rectangle([0,0,460,32],fill='black');d.text((4,2),f'{name}  {t}s',font=font,fill='yellow')
 page=pages.setdefault(i//12,Image.new('RGB',(1920,810)));page.paste(thumb,((i%4)*480,(i%12//4)*270))
for n,page in pages.items():page.save(out/f'contact-{n+1}.jpg',quality=92)
print('Source target frames extracted',len(rows))
