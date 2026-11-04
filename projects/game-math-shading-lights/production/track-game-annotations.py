"""CPU track visible editorial targets. Every track still needs visual review."""
from pathlib import Path
import sys,json,hashlib,math
P=Path(__file__).resolve().parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'projects/game-math-euler-axis-angle/production/local/revision-v3/deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
sources={s['id']:s for s in read(P/'planning/footage-audit.json')['sources']}
windows=[
 dict(id='abstract-rock',sourceId='dYyWmhVuc3w',start=248,end=250,bbox=[720,370,400,155],label='빛이 닿는 면',shape='open-ellipse',purpose='Highlight the illuminated rock without drawing across its texture.'),
 dict(id='matte-wall',sourceId='FRfnXAIbA-M',start=417,end=420,bbox=[1080,250,380,395],label='넓은 벽면의 밝기',shape='corner-bracket',purpose='The round tower remains unchanged while the camera moves; no inferred engine model.'),
 dict(id='bonnet',sourceId='X9UdRR_4Rog',start=56,end=57.2,bbox=[590,395,550,250],label='보닛에 비친 창문',shape='open-ellipse',purpose='Point at the actual bonnet window reflection, not the moving car door.'),
 dict(id='bloom',sourceId='pM6hIROLoyw',start=486.5,end=488,bbox=[870,575,130,150],label='스스로 밝은 식물',shape='ellipse',purpose='Brightbloom itself; following broad rock result remains unpainted.'),
 dict(id='ceiling',sourceId='dYyWmhVuc3w',start=771,end=772.3,bbox=[370,340,950,290],label='추가한 천장등',shape='corner-bracket',purpose='Installed light; hide before the fast turn. Then show the lit room unobstructed.'),
 dict(id='doom-surface',sourceId='Hu94MHBQCis',start=100,end=101.5,bbox=[855,405,285,225],label='표면에 맺힌 빛',shape='open-ellipse',purpose='A visible illuminated surface; no volumetric-fog or measured buffer claim.'),
]
out=P/'production/local/annotation-tracking';out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
results=[]
for w in windows:
 cap=cv2.VideoCapture(str(R/sources[w['sourceId']]['file']));assert cap.isOpened();fps=cap.get(cv2.CAP_PROP_FPS)
 start=round(w['start']*fps);end=round(w['end']*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,start)
 tracker=cv2.TrackerCSRT_create();keys=[];images=[]
 for f in range(start,end):
  ok,frame=cap.read();assert ok
  small=cv2.resize(frame,(960,540))
  if f==start:tracker.init(small,tuple(round(v/2) for v in w['bbox']));good=True;box=w['bbox']
  else:good,b=tracker.update(small);box=[2*float(v) for v in b]
  x,y,width,height=box
  visible=bool(good and x>=15 and y>=120 and x+width<=1905 and y+height<=870)
  keys.append(dict(time=f/fps,bbox=[round(v,2) for v in box],visible=visible))
  if (f-start)%max(1,round(fps/4))==0:
   im=Image.fromarray(cv2.cvtColor(small,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(im)
   if visible:d.rectangle([x/2,y/2,(x+width)/2,(y+height)/2],outline='#F4D557',width=4)
   d.text((8,8),f"{w['id']} {f/fps:.2f}s "+('' if visible else 'HIDDEN'),font=font,fill='yellow',stroke_width=2,stroke_fill='black')
   images.append(im.resize((480,270)))
 cap.release()
 data=dict(**w,sourceSha256=sources[w['sourceId']]['sha256'],coordinates='1920x1080 display, original aspect preserved',fps=fps,method='Actual CPU-decoded source and OpenCV CSRT at source fps; editorial guide only',keyframes=keys,visualQa='pending',failedSamples=sum(not k['visible'] for k in keys))
 (out/(w['id']+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for n in range(0,len(images),16):
  board=Image.new('RGB',(1920,math.ceil(len(images[n:n+16])/4)*270))
  for j,im in enumerate(images[n:n+16]):board.paste(im,((j%4)*480,(j//4)*270))
  board.save(out/f"{w['id']}-{n//16+1}.jpg",quality=95)
 results.append({k:v for k,v in data.items() if k!='keyframes'});print(w['id'],len(keys),'native frames',flush=True)
(P/'planning/game-annotation-tracks.json').write_text(json.dumps(dict(status='draft-tracks-awaiting-visual-QA-and-speech-cues',windows=results,finalCompositeViewed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
