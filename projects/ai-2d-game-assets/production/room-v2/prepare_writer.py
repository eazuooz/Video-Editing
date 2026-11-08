"""Register actual sprite-gen writing cuts; reuse the approved PixelOE palette."""
from pathlib import Path
import json,hashlib
import numpy as np,cv2,torch
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
from pixeloe.legacy.pixelize import pixelize
torch.set_num_threads(2)
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v3';base=L/'write-entry-sprite-gen';SOURCE=P/'assets/local/room-v3/write-entry-source.png';sheet=Image.open(SOURCE).convert('RGBA');report=json.loads((base/'write-slice-sheet.json').read_text('utf8'));factor=report['factor'];common=(192,493)
out128=L/'writer-registered128';out128.mkdir(exist_ok=True);OUT=L/'pixel-clean/96x132/writing';OUT.mkdir(exist_ok=True)
palette=json.loads((L/'pixel-clean/full-execution.json').read_text('utf8'))['paletteRGB'];flat=[x for rgb in palette for x in rgb];flat+=flat[-3:]*(256-len(palette));pal=Image.new('P',(1,1));pal.putpalette(flat);records=[]
for i in range(8):
 cell=sheet.crop((i%4*384,i//4*512,(i%4+1)*384,(i//4+1)*512));bb=cell.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();dx=round(((bb[0]+bb[2])/2-common[0])*factor);dy=round((bb[3]-common[1])*factor)
 registered=Image.new('RGBA',(128,176));registered.alpha_composite(Image.open(base/f'write-{i:02}.png').convert('RGBA'),(dx,dy));registered.save(out128/f'write-{i:02}.png')
 a=np.array(registered);mask=a[:,:,3]>=128;_,nearest=distance_transform_edt(~mask,return_indices=True);rgb=a[:,:,:3].copy();rgb[~mask]=rgb[nearest[0][~mask],nearest[1][~mask]]
 args={'mode':'contrast','target_size':[96,132],'patch_size':4,'thickness':1,'colors':None,'color_matching':False,'no_upscale':True};bgr=pixelize(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),**args)
 result=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');alpha=Image.fromarray((mask*255).astype('uint8')).resize((96,132),Image.Resampling.NEAREST);result.putalpha(alpha);z=np.array(result);z[z[:,:,3]==0,:3]=0;result=Image.fromarray(z);dest=OUT/f'write-{i:02}.png';result.save(dest)
 records.append({'frame':i,'sourceBox':bb,'registrationShift':[dx,dy],'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'opaqueColors':len({tuple(v) for v in z[:,:,:3][z[:,:,3]>0]}),'alphaBinary':set(np.unique(z[:,:,3]))<={0,255}})
canvas=Image.new('RGB',(1536,1104),'#111a1b');d=ImageDraw.Draw(canvas)
for i in range(8):
 im=Image.open(OUT/f'write-{i:02}.png').resize((384,528),Image.Resampling.NEAREST);canvas.paste(im,((i%4)*384,(i//4)*552+24),im);d.text(((i%4)*384+12,(i//4)*552+6),f'write-{i:02} / shared32 / native96x132',fill='white')
canvas.save(L/'pixel-clean/writer-contact.png')
record={'toolSequence':['sprite-gen slice-sheet','shared source-cell registration','PixelOE contour-aware reduction','shared32 palette/no-dither/binaryalpha'],'source':str(SOURCE),'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'sourceCellAnchor':common,'reason':'Observed source feet baseline492-494 instead of requested480; one common493 origin, no per-frame rescale','factor':factor,'canvas':[96,132],'anchor':[48,125],'gameScale':1,'paletteReused':'pixel-clean/full-execution.json paletteRGB unchanged','clip':{'frames':[f'pixel-native/writing/write-{i:02}.png' for i in range(8)],'canvas':[96,132],'anchor':[48,125],'gameScale':1,'fps':4,'loop':False},'records':records}
(H/'write-entry-execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');print(OUT)
