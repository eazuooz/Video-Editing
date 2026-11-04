"""CPU-only source boards for selecting actual on-screen annotation targets."""
from pathlib import Path
import hashlib,json,math,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
sys.path.insert(0,str(R/'projects/game-math-euler-axis-angle/production/local/revision-v3/deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
out=B/'local/annotation-targets-v1';out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
unique={};records=[]
for item in read(B/'batch.json')['items'][3:]:
 P=R/'projects'/item['slug'];plan=read(P/'planning/production-plan.json')
 for g in plan['nativeGameCueBindings']:
  key=(g['sourceFile'],g['sourceIn'],g['sourceOut'])
  if key in unique:
   unique[key]['uses'].append(dict(episode=item['id'],scene=g['sceneId'],project=item['slug']));continue
  name=item['id']+'-'+g['sceneId'];folder=out/name;folder.mkdir(exist_ok=True)
  record=dict(id=name,sourceFile=g['sourceFile'],sourceSha256=g['sourceSha256'],sourceId=g['sourceId'],game=g['game'],start=g['sourceIn'],end=g['sourceOut'],uses=[dict(episode=item['id'],scene=g['sceneId'],project=item['slug'])],samples=[],viewed=False)
  cap=cv2.VideoCapture(str(R/g['sourceFile']));assert cap.isOpened();fps=cap.get(cv2.CAP_PROP_FPS);tiles=[]
  for i in range(9):
   t=g['sourceIn']+(g['sourceOut']-g['sourceIn']-.1)*i/8;frame_number=round(t*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,frame_number);ok,f=cap.read();assert ok
   im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB));original=folder/f'{i:02}.jpg';im.save(original,quality=96)
   tile=im.resize((640,360));d=ImageDraw.Draw(tile);d.rectangle((0,0,640,30),fill='black');d.text((8,1),f'{name} | {frame_number/fps:.3f}s',font=font,fill='white');tiles.append(tile)
   record['samples'].append(dict(time=frame_number/fps,file=original.relative_to(R).as_posix()))
  cap.release();board=Image.new('RGB',(1920,1080))
  for i,im in enumerate(tiles):board.paste(im,((i%3)*640,(i//3)*360))
  boardfile=out/(name+'.jpg');board.save(boardfile,quality=96);record['board']=boardfile.relative_to(R).as_posix();records.append(record);unique[key]=record
  print(name,g['game'],flush=True)
(out/'manifest.json').write_text(json.dumps(dict(status='actual-source-boards-awaiting-target-review',records=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
