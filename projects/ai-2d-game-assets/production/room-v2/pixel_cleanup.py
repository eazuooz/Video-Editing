"""Actual PixelOE contour-aware reduction + one shared final palette and binary alpha.
Keeps every existing pose unchanged in its original source path.
"""
from pathlib import Path
import json,hashlib,sys
import numpy as np,cv2,torch
torch.set_num_threads(2)
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
from pixeloe.legacy.pixelize import pixelize
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];SITE=R/'sites/yamyam-cartographers-room/dist';OUT=P/'production/local/room-v3/pixel-clean';OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((SITE/'assets/motions.json').read_text('utf8'));sources=sorted(set(f for c in manifest['clips'].values() for f in c['frames']))
# Include idle fallback so switching between current states never changes palette/grid.
sources+=['sprite-gen/hero-idle.png']
pixels=[]
for name in sources:
 a=np.array(Image.open(SITE/'assets'/name).convert('RGBA'));pixels.append(a[:,:,:3][a[:,:,3]>=128])
opaque=np.concatenate(pixels);swatch=Image.fromarray(opaque.reshape(-1,1,3),'RGB');pal=swatch.quantize(colors=32,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
palette=pal.getpalette()[:96];palette+=palette[-3:]*(256-32);palimg=Image.new('P',(1,1));palimg.putpalette(palette)
def process(name,size):
 f=SITE/'assets'/name;im=Image.open(f).convert('RGBA');a=np.array(im);mask=a[:,:,3]>=128
 # Extend real edge colors into transparent pixels before filtering; no white matte.
 _,indices=distance_transform_edt(~mask,return_indices=True);rgb=a[:,:,:3].copy();rgb[~mask]=rgb[indices[0][~mask],indices[1][~mask]]
 params={'mode':'contrast','target_size':list(size),'patch_size':4,'thickness':1,'colors':None,'color_matching':False,'no_upscale':True}
 bgr=pixelize(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),**params);result=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB));assert result.size==size,result.size
 result=result.quantize(palette=palimg,dither=Image.Dither.NONE).convert('RGBA');alpha=Image.fromarray((mask*255).astype(np.uint8)).resize(size,Image.Resampling.NEAREST);result.putalpha(alpha)
 arr=np.array(result);arr[arr[:,:,3]==0,:3]=0;result=Image.fromarray(arr,'RGBA')
 dest=OUT/f'{size[0]}x{size[1]}'/name;dest.parent.mkdir(parents=True,exist_ok=True);result.save(dest)
 used={tuple(v) for v in arr[:,:,:3][arr[:,:,3]==255]};assert len(used)<=32 and set(np.unique(arr[:,:,3]))<={0,255}
 return {'file':name,'sourceSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'output':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'width':size[0],'height':size[1],'opaqueColors':len(used),'alpha':[0,255],'parameters':params}
sample=['motions/walk-00.png','motions/walk-02.png','motions/sit-07.png','motions/book-07.png','motions/look-07.png','2dimg2motion/map_05.png'];full='--all' in sys.argv
records=[]
for size in ([(96,132)] if full else [(128,176),(96,132),(64,88)]):
 for name in (sources if full else sample):
  rec=process(name,size);records.append(rec);print(size,name,flush=True)
report={'tool':'PixelOE 1.0.0 legacy.pixelize','actualExecution':True,'operation':'contour-aware downsample then shared exact32 palette; no dithering; nearest binary alpha','originalPreserved':True,'paletteRGB':[palette[i:i+3] for i in range(0,96,3)],'sourceCanvas':[128,176],'recommendedCanvas':[96,132],'recommendedAnchor':[48,125],'recommendedGameScale':1,'worldSizePreserved':'original .75 ×128/176 equals new96/132 ×1; anchor124.5 rounded125 is0.5 game-pixel offset','records':records,'humanReview':False}
(OUT/('full-execution.json' if full else 'sample-execution.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
if not full:
 sheet=Image.new('RGB',(1536,6*440),(14,19,20));d=ImageDraw.Draw(sheet)
 for y,name in enumerate(sample):
  for x,size in enumerate([(128,176),(96,132),(64,88)]):
   im=Image.open(OUT/f'{size[0]}x{size[1]}'/name);im=im.resize((288,396),Image.Resampling.NEAREST);sheet.paste(im,(x*512+112,y*440+32),im);d.text((x*512+20,y*440+8),f'{name} / {size[0]}x{size[1]} / fixed32 / alpha01',fill='white')
 sheet.save(OUT/'candidates.png')
