"""Add only unrepresented caption cues to the current actual-file QA evidence."""
from common import *
import sys,math
from PIL import Image,ImageDraw,ImageFont
slug=sys.argv[1];H=R/'projects'/slug/'production/concept-fit-v2';O=R/'projects'/slug/'production/local/concept-fit-v2';Q=O/'qa-captions';Q.mkdir(exist_ok=True)
qa=read(H/'qa.json');cues=read(H/'captions.json')['cues'];master=next(x for x in qa['technical'] if x['kind']=='captioned');assert sha(R/master['path'])==master['sha256']
rows=[];added=[]
for cue in cues:
 candidates=[f for f in qa['frames'] if cue['start']+.03<=f['time']<=cue['end']-.03]
 if candidates:frame=candidates[len(candidates)//2];origin='existing current-master QA frame'
 else:
  t=(cue['start']+cue['end'])/2;p=Q/f'{t:09.3f}.png'
  subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(R/master['path']),'-frames:v','1','-y',str(p)],capture_output=True,check=True)
  frame=dict(scene=cue['scene'],time=t,path=rel(p));added.append(dict(**frame,cue=cue['id']));origin='additional cue midpoint'
 rows.append(dict(cue=cue['id'],frame=frame['path'],time=frame['time'],origin=origin))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);sheets=[]
for start in range(0,len(added),12):
 im=Image.new('RGB',(1920,1560),'#111');dr=ImageDraw.Draw(im)
 for n,f in enumerate(added[start:start+12]):
  l=n%3*640;t=n//3*390;im.paste(Image.open(R/f['path']).resize((640,360)),(l,t+30));dr.text((l+5,t+4),f['cue']+' '+f'{f["time"]:.2f}s',font=font,fill='white')
 p=Q/f'sheet-{start//12+1:02}.jpg';im.save(p,quality=92);sheets.append(rel(p))
save(H/'caption-pixel-coverage.json',dict(masterSha256=master['sha256'],cues=len(cues),addedFrames=len(added),mapping=rows,sheets=sheets,directReview='pending',checkedAt=now()))
print(len(cues),'cues covered;',len(added),'new frames;',len(sheets),'sheets')
