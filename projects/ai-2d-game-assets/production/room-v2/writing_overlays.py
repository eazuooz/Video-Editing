"""Non-generative layer extraction from actual native sprite outputs."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw
H=Path(__file__).resolve().parent; P=H.parents[1]; L=P/'production/local/room-v3'; O=L/'writing-overlays'; O.mkdir(exist_ok=True)
# Keep the nib and both forearms above a fixed book, without the abdomen.
# The same source coordinates are retained; this is a draw-order mask, not new art.
polygons=[[(26,73),(32,70),(39,74),(48,75),(49,82),(37,83),(28,80)],
          [(30,59),(36,59),(44,69),(48,79),(42,82),(37,73),(31,67)],
          [(49,76),(56,72),(64,71),(70,75),(71,80),(62,82),(51,82)]]
mask=Image.new('L',(96,132));d=ImageDraw.Draw(mask)
for polygon in polygons:d.polygon(polygon,fill=255)
records=[]
for source in sorted((L/'codixel-writing').glob('write-loop-[0-9][0-9].png')):
 im=Image.open(source).convert('RGBA'); a=im.getchannel('A'); a=Image.composite(a,Image.new('L',im.size),mask);im.putalpha(a)
 out=O/source.name;im.save(out)
 records.append({'file':out.name,'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'outputSha256':hashlib.sha256(out.read_bytes()).hexdigest()})
for i in range(8):
 source=L/'pixel-clean/96x132/writing'/f'write-{i:02}.png'; im=Image.open(source).convert('RGBA')
 # Before the arms arrive over the desk, the whole actor stays behind the prop.
 # From phase 4 onward the final shared hand region is already appropriate.
 if i<4:im=Image.new('RGBA',im.size)
 else:im.putalpha(Image.composite(im.getchannel('A'),Image.new('L',im.size),mask))
 out=O/source.name;im.save(out);records.append({'file':out.name,'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'outputSha256':hashlib.sha256(out.read_bytes()).hexdigest()})
preview=Image.new('RGBA',(96,132),(40,42,47,255));preview.alpha_composite(Image.open(O/'write-loop-00.png'))
preview.resize((576,792),Image.Resampling.NEAREST).save(O/'mask-preview.png')
(H/'writing-overlay-execution.json').write_text(json.dumps({'kind':'lossless pixel mask extraction from actual Codixel/PixelOE outputs','canvas':[96,132],'anchor':[48,125],'gameScale':1,'polygons':polygons,'drawOrder':['base actor','ledger prop','masked hands and quill','table front'],'records':records},ensure_ascii=False,indent=2),'utf8')
print(O, len(records))
