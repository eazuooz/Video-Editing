"""Inspect missing-code scenes in the retained baseline; never production pixels."""
from polish_common import *
from PIL import Image, ImageDraw
for ident in ['M13','M14']:
 e=Episode(ident); e.authorized()
 source=e.O/'baseline-upload-review.mp4'; out=e.O/'missing-code-reference';out.mkdir(exist_ok=True)
 records=[]
 for s in e.T['scenes']:
  if s['classification']!='explanation' or s['id'].isdigit():continue
  sheet=Image.new('RGB',(1280,768),'#eeeeee');draw=ImageDraw.Draw(sheet);samples=[]
  for j,f in enumerate([.12,.38,.64,.9]):
   t=s['start']+s['seconds']*f;dst=out/f'{s["id"]}-{j}.png'
   if not dst.exists():e.ff(['-ss',str(t),'-i',source,'-frames:v','1',dst],'polygon-reference-extract.log')
   im=Image.open(dst).convert('RGB');im.thumbnail((640,360));x=(j%2)*640;y=(j//2)*384
   sheet.paste(im,(x,y+24));draw.text((x+12,y+5),f'{ident} {s["id"]} / baseline {t:.3f}s / local {t-s["start"]:.3f}s',fill='black')
   samples.append({'path':rel(dst),'globalSeconds':t,'localSeconds':t-s['start']})
  path=out/f'{s["id"]}-sheet.jpg';sheet.save(path,quality=92)
  records.append({'id':s['id'],'sheet':rel(path),'samples':samples})
 save(e.H/'missing-code-reference.json',{'source':rel(source),'sourceSha256':sha(source),'purpose':'baseline low-resolution pixel reference only, never production footage','scenes':records,'directInspection':'pending'})
 print(ident,len(records),'reference sheets',flush=True)
