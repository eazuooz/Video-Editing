from pathlib import Path
import cv2, numpy as np, json, hashlib
from PIL import Image
from pixeloe.legacy.pixelize import pixelize

P=Path(__file__).resolve().parents[2]
src=P/'assets/local/room-v3/room-centered-source.png'
out=P/'production/local/room-v3/background'
out.mkdir(parents=True,exist_ok=True)
img=cv2.imdecode(np.fromfile(str(src),dtype=np.uint8),cv2.IMREAD_COLOR)
args={'mode':'contrast','target_size':[426,240],'patch_size':4,'thickness':1,'colors':96,'color_matching':False,'no_upscale':True}
result=pixelize(img,**args)
dest=out/'room.png'
cv2.imencode('.png',result)[1].tofile(str(dest))
im=Image.open(dest).convert('RGB')
assert im.size==(426,240)
im=im.quantize(colors=96,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
im.save(dest)
record={'tool':'PixelOE','input':str(src.relative_to(P)),'inputSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'parameters':args,'outputSize':list(im.size),'actualColors':len(set(im.getdata())),'outputSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'purpose':'Centered desk, unlit lantern/candle, native426x240 room grid for new writing interaction'}
record['postprocess']={'paletteQuantization':96,'dither':False,'reason':'PixelOE legacy output retained intermediate colours; explicit final palette keeps native clusters.'}
(P/'production/room-v3/background-execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
