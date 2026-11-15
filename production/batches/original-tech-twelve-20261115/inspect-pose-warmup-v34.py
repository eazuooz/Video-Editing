from pathlib import Path
import av,hashlib,json,numpy as np
from PIL import Image,ImageDraw
ROOT=Path('D:/Github/VideoEditing');M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');R=M/'production-resume-20261115T055255Z';B=ROOT/'shared/output/original-tech-twelve-20261115/remaining-seven/native-pose-warmup-v30';cap=B/'attempts/20261115T181242Z-639bc9f2/capture'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
old=read(M/'remaining-seven/native-stream-v2/accepted-smoke.json');rows=[];thumbs=[]
for c in old['clips']:
 if c['camera']!=('overview'if c['topic']in['spiderman','ratchet']else'detail'):continue
 p=cap/c['topic']/c['mode']/c['camera'];a=read(Path(c['frameRgbManifest']['path']))['frames'];b=read(p/'streamed-capture.json')['frames'];bad=[i for i in range(32)if a[i]!=b[i]];rows.append(dict(topic=c['topic'],mode=c['mode'],differentFrames=bad))
 if c['topic']=='doom':
  for label,path in [('old',c['video']['path']),('new30',p/'frames-lossless-rgb.mp4')]:
   with av.open(str(path))as ct:
    for i,f in enumerate(ct.decode(video=0)):
     if i in[0,1,2,31]:thumbs.append((c['mode']+' '+label+' '+str(i),f.to_image().resize((360,360))))
out=R/'pose-warmup-raster-observation-v34.json';assert not out.exists();out.write_text(json.dumps(dict(rows=rows),indent=2)+'\n','utf8');im=Image.new('RGB',(1440,4*390),'#12221a');d=ImageDraw.Draw(im)
for i,(label,pic)in enumerate(thumbs):x=i%4*360;y=i//4*390;im.paste(pic,(x,y+30));d.text((x+5,y+5),label,fill='white')
im.save(R/'doom-first-animation-frames-v34.jpg',quality=94);print(json.dumps(rows))
