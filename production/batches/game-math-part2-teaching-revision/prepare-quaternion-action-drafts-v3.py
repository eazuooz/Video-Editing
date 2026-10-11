"""Silent local source crops for tracking review, never a lecture delivery."""
from pathlib import Path
import cv2,hashlib,json,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
rows=json.loads((R/'additions.json').read_text(encoding='utf8'))['scenes']
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);cv2.setNumThreads(2)
jobs=[('trail', 'QF10',(360,340,1200,674)),('gear-v3','QF20',(480,320,960,540)),('besiege','QF30',(320,90,1440,810))]
(O/'action-drafts').mkdir(exist_ok=True);receipts=[]
for name,ident,crop in jobs:
 s=next(x for x in rows if x['id']==ident);lo=s['intervals'][0][0];hi=s['intervals'][-1][1]
 segments=s['sourceSegments'];frames=sum(round(x['maxSeconds']*60) for x in segments)
 dst=O/f'action-drafts/{name}-unannotated.mp4';receipt=dst.with_suffix('.json')
 stamp=dict(sourceFile=s['sourceFile'],sourceSha256=s['sourceSha256'],sourceIn=lo,sourceOut=hi,segments=segments,frames=frames,crop=list(crop),fps=60)
 old=json.loads(receipt.read_text(encoding='utf8')) if receipt.exists() else {}
 digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 if not dst.exists() or old.get('recipe')!=stamp or old.get('videoSha256')!=digest(dst):
  parts=[]
  for number,segment in enumerate(segments,1):
   x,y,w,h=segment.get('crop',crop);part=dst if len(segments)==1 else dst.with_name(f'{name}-part-{number}.mp4');parts.append(part)
   args=[str(FF),'-hide_banner','-loglevel','error','-y','-ss',str(segment['in']),'-i',str(ROOT/segment['sourceFile']),'-vf',f'crop={w}:{h}:{x}:{y},scale=1920:1080:flags=lanczos,setsar=1,fps=60','-frames:v',str(round(segment['maxSeconds']*60)),'-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(part)]
   subprocess.run(args,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  if len(parts)>1:
   listing=dst.with_suffix('.concat.txt');listing.write_text('\n'.join("file '"+str(p.as_posix())+"'" for p in parts)+'\n',encoding='utf8')
   subprocess.run([str(FF),'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-an','-movflags','+faststart',str(dst)],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 c=cv2.VideoCapture(str(dst));assert round(c.get(cv2.CAP_PROP_FRAME_COUNT))==frames and c.get(cv2.CAP_PROP_FPS)==60
 times=list(range(0,frames,120));pages=[]
 for page,i in enumerate(range(0,len(times),8),1):
  sheet=Image.new('RGB',(1280,1568),'white');draw=ImageDraw.Draw(sheet)
  for k,frame in enumerate(times[i:i+8]):
   c.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,img=c.read();assert ok
   remain=frame
   for segment in segments:
    length=round(segment['maxSeconds']*60)
    if remain<length:source_at=segment['in']+remain/60;break
    remain-=length
   x=k%2*640;y=k//2*392;sheet.paste(Image.fromarray(cv2.cvtColor(cv2.resize(img,(640,360)),cv2.COLOR_BGR2RGB)),(x,y+32));draw.text((x+4,y+4),f'{name} output {frame/60:g}s / source {source_at:g}s',font=font,fill='black')
  file=O/f'action-drafts/{name}-page-{page}.jpg';sheet.save(file,quality=95);pages.append(file.relative_to(ROOT).as_posix())
 c.release();record=dict(recipe=stamp,videoSha256=digest(dst),silentLocalTrackingDraft=True,narratedLectureComplete=False,cropAndLandmarkReview=False,pages=pages)
 receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');receipts.append(record)
 print(name,frames,'frames; direct crop/landmark review pending',flush=True)
(R/'action-draft-recipes.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
