"""Extract current encoded replacement joins; never change production media."""
from pathlib import Path
import hashlib,json,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v5';Q=O/'join-review'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
plan=read(H/'assembly-plan.json');pair=read(O/'pair-source.json');master=R/pair['outputs']['captioned']['file'];mastersha=sha(master)
assert mastersha==pair['outputs']['captioned']['sha256'];Q.mkdir(exist_ok=True)
samples=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
for r in plan['replacements']:
 start=r['globalStartFrame'];end=start+r['frames'];board=Image.new('RGB',(1500,239),'#151515');draw=ImageDraw.Draw(board)
 for i,(phase,n) in enumerate([('before',start-1),('reveal',start+30),('last',end-1),('after',end)]):
  path=Q/f"{r['id']}-{phase}.png";stamp=path.with_suffix('.json');key=dict(masterSha256=mastersha,frame=n)
  if not(path.exists() and stamp.exists() and read(stamp)==key):
   subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{n/60:.12f}','-i',str(master),'-an','-frames:v','1','-update','1',str(path)],check=True);save(stamp,key)
  im=Image.open(path);assert im.size==(1920,1080)
  board.paste(im.resize((375,211),Image.Resampling.LANCZOS),(i*375,28));draw.text((i*375+4,4),f'{phase} frame{n}',font=font,fill='white')
  samples.append(dict(id=r['id'],phase=phase,frame=n,file=rel(path),sha256=sha(path)))
 b=Q/f"{r['id']}-board.jpg";board.save(b,quality=97)
save(H/'join-review.json',dict(revision=plan['revision'],masterSha256=mastersha,scope='24 current final-master frames at six replacement in/out boundaries; unchanged complete captions are encoded in these pixels.',samples=samples,boards=[rel(Q/f"{r['id']}-board.jpg") for r in plan['replacements']],directPixelReview='pending',humanListening='pending; audio reused unchanged'))
print('Prepared24 current-master join frames.')
