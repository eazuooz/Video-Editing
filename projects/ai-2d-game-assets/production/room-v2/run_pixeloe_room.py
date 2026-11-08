from pathlib import Path
import cv2,numpy as np,json,hashlib
from PIL import Image,ImageDraw
from pixeloe.legacy.pixelize import pixelize
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'projects/ai-2d-game-assets';OUT=P/'production/local/room-v2/pixeloe';OUT.mkdir(parents=True,exist_ok=True)
src=P/'assets/local/workshop-generated-v1.png';img=cv2.imdecode(np.fromfile(str(src),dtype=np.uint8),cv2.IMREAD_COLOR)
args={'mode':'contrast','target_size':[426,240],'patch_size':4,'thickness':1,'colors':64,'color_matching':True,'no_upscale':True}
result=pixelize(img,**args);dest=OUT/'room-pixeloe.png';cv2.imencode('.png',result)[1].tofile(str(dest))
raw=Image.open(src).convert('RGB');final=Image.open(dest).convert('RGB')
preview=Image.new('RGB',(852,272),(21,25,28));preview.paste(raw.resize((426,240),Image.Resampling.LANCZOS),(0,32));preview.paste(final,(426,32));d=ImageDraw.Draw(preview);d.text((10,10),'Generated input / smooth resize',fill='white');d.text((436,10),'Actual PixelOE / 426 x 240',fill='white');preview.save(OUT/'comparison.png')
record={'tool':'PixelOE','actualExecution':True,'input':'workshop-generated-v1.png','inputSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'parameters':args,'outputSize':list(final.size),'actualColorCount':len(set(final.getdata())),'outputSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'purpose':'same workshop background pixel-grid comparison; original game background preserved'}
(P/'production/room-v2/pixeloe-execution.json').write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record))
