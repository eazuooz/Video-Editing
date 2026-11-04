"""Candidate open guide for the complete native track-edit result, CPU only."""
from pathlib import Path
import json,sys,math
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
sys.path.insert(0,str(R/'projects/game-math-euler-axis-angle/production/local/revision-v3/deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
manifest=read(B/'local/handoff-observations-v1/manifest.json')
g=next(r for r in manifest['records'] if r['id']=='M32-loop')
out=B/'local/handoff-observations-v1/loop-guide-v2';out.mkdir(exist_ok=True)
assert not (out/'track.json').exists(),'Preserve candidate and review evidence'
start,end=240.2,242.3
points=[[544,415],[544,495],[714,672]]
cap=cv2.VideoCapture(str(R/g['sourceFile']));fps=cap.get(cv2.CAP_PROP_FPS)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);tiles=[];kfs=[]
for i in range(math.ceil((end-start)*8)+1):
 t=min(end,start+i/8);fr=round(t*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,fr);ok,frame=cap.read();assert ok
 im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(im)
 d.line([tuple(p) for p in points],fill='#101010',width=16);d.line([tuple(p) for p in points],fill='#73c7c2',width=10)
 tile=im.resize((480,270));d=ImageDraw.Draw(tile);d.rectangle((0,0,480,28),fill='black');d.text((6,0),f'Native guide | {t:.3f}s',font=font,fill='white');tiles.append(tile)
 kfs.append(dict(time=t,points=points,visible=True))
cap.release()
board=Image.new('RGB',(1920,math.ceil(len(tiles)/4)*270))
for i,tile in enumerate(tiles):board.paste(tile,(i%4*480,i//4*270))
board.save(out/'board.jpg',quality=96)
record=dict(id='M32-loop-corner',sourceId=g['sourceId'],sourceSha256=g['sourceSha256'],start=start,end=end,
 label='각진 모서리를 둥글게',shape='open-contour',coordinates='1920x1080 native decoded source',
 fps=fps,method='Manually drawn open contour; stationary edit corner, sampled at8fps; editorial guide only',
 keyframes=kfs,visualQa=dict(status='candidate-not-reviewed',evidence=(out/'board.jpg').relative_to(R).as_posix()))
(out/'track.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('18 sampled overlay frames prepared; inspect before binding.')
