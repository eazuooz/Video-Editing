"""Extract actual native game frames for explicitly inspected annotation seeds."""
from pathlib import Path
import json,sys
P=Path(__file__).resolve().parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'projects/game-math-euler-axis-angle/production/local/revision-v3/deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
sources={s['id']:s for s in json.loads((P/'planning/footage-audit.json').read_text(encoding='utf-8'))['sources']}
rows=[('abstract-rock','dYyWmhVuc3w',248),('matte-wall','FRfnXAIbA-M',417),('bonnet','X9UdRR_4Rog',54),('bloom','pM6hIROLoyw',486.5),('ceiling','dYyWmhVuc3w',771),('doom-door','Hu94MHBQCis',100)]
out=P/'production/local/annotation-seeds';out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24);evidence=[]
for name,sid,t in rows:
 cap=cv2.VideoCapture(str(R/sources[sid]['file']));assert cap.isOpened();cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=cap.read();assert ok
 frame_number=int(cap.get(cv2.CAP_PROP_POS_FRAMES))-1;fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
 h,w=frame.shape[:2];assert w>=1920 and h>=1080
 im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));im.save(out/(name+'.png'))
 preview=im.resize((960,540));ImageDraw.Draw(preview).text((12,12),f'{name} | {t}s | native {w}x{h}',font=font,fill='yellow',stroke_width=2,stroke_fill='black');preview.save(out/(name+'.jpg'),quality=95)
 evidence.append(dict(id=name,sourceId=sid,sourceTime=t,frame=frame_number,fps=fps,dimensions=[w,h],image=str(out/(name+'.png')),review='awaiting direct inspection'))
(out/'frames.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Extracted',len(evidence),'actual native source frames; no annotation approval claimed')
