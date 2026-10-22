"""Retain prior cue review for unchanged composites; inspect every changed-panel cue."""
from common import *
from PIL import Image,ImageDraw,ImageFont
P=R/'projects/game-math-quaternion-foundations-v3';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';Q=O/'qa-crop-delta';Q.mkdir(exist_ok=True)
old=read(O/'before-panel-crop-fix/caption-pixel-coverage.json');qa=read(H/'qa.json');out=read(H/'outputs.json');master=next(x for x in out['outputs'] if x['path'].endswith('.captioned.mp4'))
previous=read(O/'before-panel-crop-fix/composition.json');current=read(H/'composition.json')
changed=[x['id'] for x in current['scenes'] if x['sha256']!=next(y['sha256'] for y in previous['scenes'] if y['id']==x['id'])]
assert set(changed)=={'02','GA01','QF30'}
frames=[]
for cue in read(H/'captions.json')['cues']:
 if cue['scene'] not in changed:continue
 tm=(cue['start']+cue['end'])/2;p=Q/f'{tm:09.3f}.png'
 subprocess.run(['ffmpeg','-v','error','-ss',str(tm),'-i',str(R/master['path']),'-frames:v','1','-y',str(p)],capture_output=True,check=True)
 frames.append(dict(cue=cue['id'],scene=cue['scene'],time=tm,path=rel(p)))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);sheets=[]
for start in range(0,len(frames),12):
 im=Image.new('RGB',(1920,1560),'#111');dr=ImageDraw.Draw(im)
 for n,f in enumerate(frames[start:start+12]):
  l=n%3*640;t=n//3*390;im.paste(Image.open(R/f['path']).resize((640,360)),(l,t+30));dr.text((l+5,t+4),f['cue']+' '+str(f['time']),font=font,fill='white')
 p=Q/f'sheet-{start//12+1:02}.jpg';im.save(p,quality=92);sheets.append(rel(p))
old.update(masterSha256=master['sha256'],priorMasterSha256=old['masterSha256'],reusedReview='Prior15 full QA sheets and15 caption sheets directly viewed before crop-only repair.47 composite hashes unchanged; preserved narration/timing/ASS.',changedComposites=changed,deltaFrames=frames,deltaSheets=sheets,deltaDirectReview='pending',directReview='Prior cue review retained for47 unchanged composites; new three-panel evidence pending',checkedAt=now())
save(H/'caption-pixel-coverage.json',old)
print(len(frames),'affected cue images;',len(sheets),'delta sheets')
