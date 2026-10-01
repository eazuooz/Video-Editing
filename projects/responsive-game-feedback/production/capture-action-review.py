"""Inspect recorded state responses at the actual event time in the final movie."""
from pathlib import Path
import json,subprocess,io
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];WORK=Path(__file__).parent/'final-v1'
m=json.loads((ROOT/'projects/responsive-game-feedback/project.json').read_text(encoding='utf-8'))
p=json.loads((WORK/'plan.json').read_text(encoding='utf-8'))
events=[(0,'receipt',3.35,'locked-door reason'),(1,'blocked',3.35,'occupied reason'),(1,'blocked',12.35,'material shortage'),(2,'menu',19.35,'both confirm'),(3,'cutscene',8.35,'partial hold'),(3,'cutscene',16.4,'confirmed skip'),(4,'pending',12.35,'duplicate pending'),(4,'pending',17.35,'confirmed completion'),(5,'context',15.35,'menu context')]
sheet=Image.new('RGB',(1920,1170),'white');points=[]
for i,(scene,key,t,label) in enumerate(events):
    cut=next(c for c in p['scenes'][scene]['cuts'] if c['key']==key)
    absolute=cut['timelineStart']+t-cut['sourceIn']
    assert cut['timelineStart']<=absolute<cut['timelineStart']+cut['seconds']
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(absolute),'-i',str(ROOT/m['paths']['videoBurnedCaptions']),'-frames:v','1','-vf','scale=630:354','-f','image2pipe','-c:v','mjpeg','-'])
    x=i%3*640;y=i//3*390;sheet.paste(Image.open(io.BytesIO(data)),(x,y));ImageDraw.Draw(sheet).text((x+8,y+358),f'{absolute:.3f}s / {label}',fill='black');points.append({'seconds':absolute,'label':label})
sheet.save(WORK/'action-response-review.jpg');(WORK/'action-response-points.json').write_text(json.dumps(points,indent=2)+'\n',encoding='utf-8')
