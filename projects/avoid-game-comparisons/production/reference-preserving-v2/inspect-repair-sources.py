from pathlib import Path
import subprocess,json
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent;L=R/'projects/avoid-game-comparisons/production/local/reference-preserving-v2';src=L/'nes-gameplay-project.mp4'
sheet=Image.new('RGB',(1440,600));draw=ImageDraw.Draw(sheet)
for i,t in enumerate([43,45,47,49,51,53,169,171,173,175]):
 raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=360:203','-f','rawvideo','-pix_fmt','rgb24','-']);im=Image.frombytes('RGB',(360,203),raw);x=i%4*360;y=i//4*200;sheet.paste(im.resize((350,180)),(x,y));draw.text((x+4,y+183),str(t),fill='white')
sheet.save(L/'repair-sources.jpg')
keys=[]
for k in range(26):
 t=194+k*.1;raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']);im=np.frombuffer(raw,dtype=np.uint8).reshape(1080,1920,3);roi=im[180:830,800:1300].astype(float);mask=(roi[:,:,1]>roi[:,:,0]*1.15)&(roi[:,:,1]>roi[:,:,2]*1.1)&(roi[:,:,1]>140);counts=mask.sum(axis=0);assert counts.max()>400,(t,counts.max());x=800+float(np.mean(np.flatnonzero(counts>counts.max()*.97)));keys.append([round(t,1),round(x-50,1),140,100,770])
(V/'flag-track.json').write_text(json.dumps({'source':'nes-gameplay-project.mp4','target':'tall green flagpole, restricted verified source region','measurement':'editorial screen coordinate tracking only; no game world data','keyframes':keys},indent=2)+'\n');print(keys[:8])
