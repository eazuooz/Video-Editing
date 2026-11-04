from pathlib import Path
import json,sys,math
P=Path(__file__).resolve().parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'projects/game-math-euler-axis-angle/production/local/revision-v3/deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
sources={s['id']:s for s in json.loads((P/'planning/footage-audit.json').read_text(encoding='utf-8'))['sources']}
out=P/'production/local/annotation-inspection';out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
for name,sid,times in [('doom','Hu94MHBQCis',[91,92,93,94,95,96,97,98]),('spot','dYyWmhVuc3w',list(range(378,392))),('ceiling','dYyWmhVuc3w',[768,768.5,769,769.5,770,770.5,771,771.5])]:
 cap=cv2.VideoCapture(str(R/sources[sid]['file']));board=Image.new('RGB',(1920,math.ceil(len(times)/4)*270))
 for i,t in enumerate(times):
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=cap.read();assert ok
  im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)).resize((960,540));ImageDraw.Draw(im).text((10,10),f'{name} {t}s',font=font,fill='yellow',stroke_width=2,stroke_fill='black');board.paste(im.resize((480,270)),((i%4)*480,(i//4)*270))
 cap.release();board.save(out/(name+'.jpg'),quality=96)
