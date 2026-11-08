from pathlib import Path
from PIL import Image,ImageDraw
import json,shutil,hashlib,sys
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'projects/ai-2d-game-assets'
OUT=P/'production/local/room-v2/2dimg2motion/map-loop'
for sub in ['keyframe','fullframe']: (OUT/sub).mkdir(parents=True,exist_ok=True)
base=P/'production/local/room-v2/sprite-gen/hero-read-a.png'
shutil.copy2(base,OUT/'baseline.png')
baseim=Image.open(base).convert('RGBA');basebox=baseim.getbbox();floor=basebox[3]
sources=[('map-keyposes-source.png',[2,5,8,11]),('map-inbetweens-a-source.png',[1,3,4,6]),('map-inbetweens-b-source.png',[7,9,10,12])]
# One physical scale for all generated full-body poses. Translation only aligns the planted feet.
SCALE=150/459
records=[]
for name,ids in sources:
 im=Image.open(P/'assets/local/room-v2'/name).convert('RGBA')
 for j,idx in enumerate(ids):
  cell=im.crop((j%2*768,j//2*512,(j%2+1)*768,(j//2+1)*512))
  alpha=cell.getchannel('A').point(lambda a:255 if a>=128 else 0);cell.putalpha(alpha)
  bb=alpha.getbbox();cut=cell.crop(bb)
  sz=(round(cut.width*SCALE),round(cut.height*SCALE));cut=cut.resize(sz,Image.Resampling.NEAREST)
  frame=Image.new('RGBA',(128,176))
  x=round(64+(bb[0]-384)*SCALE);y=floor-cut.height
  frame.alpha_composite(cut,(x,y))
  dest=OUT/'fullframe'/f'map_{idx:02}.png';frame.save(dest)
  if idx in [2,5,8,11]:shutil.copy2(dest,OUT/'keyframe'/dest.name)
  records.append({'frame':idx,'source':name,'sourceCell':j,'sourceBox':bb,'commonScale':SCALE,'translation':[x,y]})
for idx in [0,13]:shutil.copy2(base,OUT/'fullframe'/f'map_{idx:02}.png')
sys.path.insert(0,str(P/'production/room-v2/research/2dimg2motion/scripts'))
from fullframes_to_gif import write_gif
from validate_14frame_pattern import validate_pattern
write_gif(fullframes_dir=OUT/'fullframe',output=OUT/'preview.gif',duration_ms=160,loop=0,background=(255,255,255),pattern='*.png')
errors=validate_pattern(baseline=OUT/'baseline.png',keyframes_dir=OUT/'keyframe',fullframes_dir=OUT/'fullframe',preview=OUT/'preview.gif',prefix='map')
if errors:raise RuntimeError(errors)
dest=ROOT/'sites/yamyam-cartographers-room/dist/assets/2dimg2motion';dest.mkdir(parents=True,exist_ok=True)
for f in (OUT/'fullframe').glob('*.png'):shutil.copy2(f,dest/f.name)
preview=Image.new('RGB',(7*256,2*376),(21,25,28));d=ImageDraw.Draw(preview)
for i in range(14):
 f=Image.open(OUT/'fullframe'/f'map_{i:02}.png').convert('RGBA').resize((256,352),Image.Resampling.NEAREST)
 preview.paste(f,(i%7*256,i//7*376+24),f);d.text((i%7*256+8,i//7*376+6),str(i).zfill(2),fill='white')
preview.save(OUT/'contact.png')
clip={'frames':[f'2dimg2motion/map_{i:02}.png' for i in range(14)],'canvas':[128,176],'anchor':[64,166],'gameScale':.75,'fps':6.25,'loop':True}
manifest=ROOT/'sites/yamyam-cartographers-room/dist/assets/motions.json';data=json.loads(manifest.read_text(encoding='utf8'));data['clips']['map-read']=clip
data['clips']['book-read']={'frames':[f'codixel/read-{i:02}.png' for i in range(24)],'canvas':[128,176],'anchor':[64,166],'gameScale':.75,'fps':8,'loop':True}
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
record={'tool':'2dimg2motion','actualExecution':True,'method':'image-generated whole-character keyposes and inbetweens; local helper assembly/validation; no procedural pose synthesis','activeHand':'screen-left; accepted visual matches original identity reference, correcting the initial prompt-side mistake','toolValidator':'OK','firstLastByteIdentical':True,'keyframeIndices':[2,5,8,11],'frameCount':14,'clip':clip,'records':records}
(P/'production/room-v2/map-loop-execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8');(dest/'map-loop.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'result':'OK','frames':14,'output':str(dest)}))
