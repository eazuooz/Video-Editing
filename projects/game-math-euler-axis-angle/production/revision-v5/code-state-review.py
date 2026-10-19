"""Current encoded captions/text samples at all twelve revised state cues."""
from pathlib import Path
import json,hashlib,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v5/code-color'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18);samples=[];boards=[]
for sid in ['15','25']:
 clip=O/f'{sid}-captioned.mp4';receipt=read(O/f'{sid}.json');cs=sha(clip);board=Image.new('RGB',(1125,482),'#151515');draw=ImageDraw.Draw(board)
 for i,start in enumerate(receipt['stateBoundaries'][:-1]):
  n=start+72;path=O/f'final-state-{sid}-{i}.png';stamp=path.with_suffix('.json');key=dict(clipSha256=cs,frame=n)
  if not(path.exists() and stamp.exists() and read(stamp)==key):
   subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{n/60:.12f}','-i',str(clip),'-an','-frames:v','1','-update','1',str(path)],check=True);save(stamp,key)
  im=Image.open(path);assert im.size==(1920,1080);x=i%3*375;y=i//3*241
  board.paste(im.resize((375,211),Image.Resampling.LANCZOS),(x,y+28));draw.text((x+4,y+4),f'{sid} state{i+1} frame{n}',font=font,fill='white')
  samples.append(dict(scene=sid,state=i,file=rel(path),sha256=sha(path),clipSha256=cs,localFrame=n))
 b=O/f'final-states-{sid}.jpg';board.save(b,quality=97);boards.append(rel(b))
save(H/'code-state-review.json',dict(samples=samples,boards=boards,scope='12 actual encoded captioned state samples, native1080 and375px derivatives',directPixelReview='pending'))
print('Prepared12 code/text states with actual encoded captions.')
