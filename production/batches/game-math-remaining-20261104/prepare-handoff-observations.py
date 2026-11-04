"""Additive CPU source frames for precise gameplay-to-explanation handoffs."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
sys.path.insert(0,str(R/'projects/game-math-euler-axis-angle/production/local/revision-v3/deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
out=B/'local/handoff-observations-v1';out.mkdir(parents=True,exist_ok=True)
assert not (out/'manifest.json').exists(),'Preserve existing sampled evidence'
choices=[('M32-loop','game-math-bezier-subdivision','000',238,247),
         ('M31-rail','game-math-parametric-hermite','027',270,282),
         ('M31-flight','game-math-parametric-hermite','012',93,104)]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21);records=[]
for name,slug,sid,start,end in choices:
 assert c['productionAllowedNow'] and slug in c['projectSlugs']
 s=next(s for s in read(R/'projects'/slug/'planning/scene-bindings.json')['scenes'] if s['id']==sid)
 g=s['actualGamePart'];cap=cv2.VideoCapture(str(R/g['sourceFile']));fps=cap.get(cv2.CAP_PROP_FPS)
 assert cap.isOpened();tiles=[];samples=[];folder=out/name;folder.mkdir(exist_ok=True)
 for i in range(16):
  frame=round((start+(end-start-.1)*i/15)*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,decoded=cap.read();assert ok
  im=Image.fromarray(cv2.cvtColor(decoded,cv2.COLOR_BGR2RGB));path=folder/f'{i:02}.jpg';im.save(path,quality=96)
  tile=im.resize((480,270));d=ImageDraw.Draw(tile);d.rectangle((0,0,480,27),fill='black');d.text((7,0),f'{name} | {frame/fps:.3f}s',font=font,fill='white');tiles.append(tile)
  samples.append(dict(time=frame/fps,file=path.relative_to(R).as_posix()))
 cap.release();board=Image.new('RGB',(1920,1080))
 for i,im in enumerate(tiles):board.paste(im,(i%4*480,i//4*270))
 bf=out/(name+'.jpg');board.save(bf,quality=96)
 records.append(dict(id=name,sourceFile=g['sourceFile'],sourceSha256=g['sourceSha256'],sourceId=g['sourceId'],start=start,end=end,samples=samples,board=bf.relative_to(R).as_posix(),viewed=False))
(out/'manifest.json').write_text(json.dumps(dict(status='sampled-not-yet-inspected',records=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Three native source handoff boards saved; not automatic content approval.')
