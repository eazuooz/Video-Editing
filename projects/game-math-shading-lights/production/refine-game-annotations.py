"""Replace visually rejected tracking and preserve native action in QA frames."""
from pathlib import Path
import json,sys,math
P=Path(__file__).resolve().parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'projects/game-math-euler-axis-angle/production/local/revision-v3/deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources={s['id']:s for s in read(P/'planning/footage-audit.json')['sources']}
original=P/'production/local/annotation-tracking';out=P/'production/local/annotation-refined-v2';out.mkdir(parents=True,exist_ok=True)
tracks=[]
for name in ['abstract-rock','matte-wall','bloom']:
 d=read(original/(name+'.json'))
 # Original video is fit into 1632x918; captions remain at 960,970.
 # This corrects the old mistaken native-y caption gate, not tracker failures.
 for k in d['keyframes']:
  x,y,w,h=k['bbox'];k['visible']=bool(w>0 and h>0 and x>=15 and y>=75 and x+w<=1905 and y+h<=975)
 d['revisionReason']='Native target remained visible; revised caption-safe fit removes false hide/show. Source fps and speed remain unchanged.'
 d['visualQa']='revised composite needs direct review';tracks.append(d)
d=read(original/'bonnet.json');d['start']=56;d['end']=57
d['shape']='contour';d['method']='Manual image-verified bonnet contour; rejected drifting CSRT preserved in prior revision.'
points=[(56,[(360,215),(535,213),(561,301),(353,302)]),(56.25,[(337,184),(548,193),(477,264),(300,261)]),(56.5,[(352,165),(540,176),(475,233),(300,229)]),(56.75,[(360,166),(540,174),(480,235),(295,228)]),(57,[(375,169),(560,180),(430,243),(290,227)])]
d['keyframes']=[{'time':t,'points':[[x*2,y*2] for x,y in p],'visible':True} for t,p in points];d['visualQa']='manual correction needs composite review';tracks.append(d)
for name,sid,label,keys in [
 ('ceiling','dYyWmhVuc3w','천장등 추가',[(768,[510,420,850,270]),(768.5,[550,465,800,225]),(769,[535,390,820,270]),(769.25,[535,390,820,270])]),
 ('doom-surface','Hu94MHBQCis','빛이 닿는 표면',[(91,[900,370,360,350]),(92,[930,435,330,300]),(93,[900,395,360,315]),(94,[900,410,360,320])]),
 ('spot-surface','dYyWmhVuc3w','빛이 닿는 앞쪽 바닥',[(386,[110,560,1320,145]),(387,[100,630,1430,165]),(388,[160,595,1260,250])]),
]:
 tracks.append(dict(id=name,sourceId=sid,start=keys[0][0],end=keys[-1][0],shape='corner-bracket',label=label,method='Manual visible-region keyframes inspected in original native frames; editorial guide, not exact detector/measurement',sourceSha256=sources[sid]['sha256'],keyframes=[dict(time=t,bbox=b,visible=True) for t,b in keys],visualQa='manual region guide needs composite review'))
font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',45)
smallfont=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
def sample(track,t):
 keys=track['keyframes'];a=keys[0];b=keys[-1]
 for i in range(1,len(keys)):
  if keys[i]['time']>=t:a,b=keys[i-1:i+1];break
 u=max(0,min(1,(t-a['time'])/max(.00001,b['time']-a['time'])))
 if 'points' in a: pts=[(x+(xx-x)*u,y+(yy-y)*u) for (x,y),(xx,yy) in zip(a['points'],b['points'])]
 else:
  x,y,w,h=[x+(xx-x)*u for x,xx in zip(a['bbox'],b['bbox'])];pts=[(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
 return pts,a['visible'] and b['visible']
for d in tracks:
 cap=cv2.VideoCapture(str(R/sources[d['sourceId']]['file']));frames=[]
 for t in [d['start']+i*.25 for i in range(round((d['end']-d['start'])*4))]:
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=cap.read();assert ok
  im=Image.new('RGB',(1920,1080));im.paste(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).resize((1632,918)),(144,0));draw=ImageDraw.Draw(im)
  pts,visible=sample(d,t);q=[(144+x*.85,y*.85) for x,y in pts]
  if visible:
   if d['shape']=='contour':draw.line(q+[q[0]],fill='#F4D557',width=8,joint='curve')
   elif d['shape']=='ellipse':draw.ellipse((q[0],q[2]),outline='#71D6DF',width=8)
   else:
    x,y=q[0];xx,yy=q[2];n=min(38,(xx-x)*.2,(yy-y)*.2)
    for ax,ay,sx,sy in [(x,y,1,1),(xx,y,-1,1),(xx,yy,-1,-1),(x,yy,1,-1)]:draw.line([(ax,ay+sy*n),(ax,ay),(ax+sx*n,ay)],fill='#F4D557',width=8)
  # Real final captions will replace this clearance-only sample.
  label=d['label'];w=draw.textbbox((0,0),label,font=font)[2];draw.rounded_rectangle((960-w/2-24,938,960+w/2+24,1008),radius=8,fill='white');draw.text((960-w/2,940),label,font=font,fill='#173B2B')
  draw.text((8,1020),f"{d['id']} | native t={t:.2f}s | QA only",font=smallfont,fill='white')
  frames.append(im.resize((480,270)))
 cap.release()
 board=Image.new('RGB',(1920,math.ceil(len(frames)/4)*270))
 for j,f in enumerate(frames):board.paste(f,((j%4)*480,(j//4)*270))
 board.save(out/(d['id']+'.jpg'),quality=95);save(out/(d['id']+'.json'),d)
save(P/'planning/game-annotation-revision-v2.json',{'status':'seven-tracks-awaiting-complete-composite-review','frameFit':{'width':1632,'height':918,'x':144,'y':0,'aspectPreserved':True},'captionCenter':[960,970],'captionTextInSamples':'target label for clearance check only, not final timed narration','tracks':[{'id':d['id'],'path':str(out/(d['id']+'.json'))} for d in tracks],'unresolved':['verify new manually placed regions at all sampled frames and final moving overlay'], 'finalCompositeViewed':False})
print('Seven annotation contact sheets; no final QA claim')
