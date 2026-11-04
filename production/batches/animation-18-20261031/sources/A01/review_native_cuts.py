from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,math
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
core=json.loads((P/'selected-footage.json').read_text(encoding='utf-8'))['sources']
extra=json.loads((P/'additional-fighters-inventory.json').read_text(encoding='utf-8'))
items={**core,**extra}
cuts=json.loads((P/'native-cut-detector.json').read_text(encoding='utf-8'))
def run(key):
 s=items[key];fps=eval(next(x['r_frame_rate'] for x in s['decoded']['streams'] if x['codec_type']=='video'))
 ts=[]
 for t in cuts[key]['candidates']:
  if not ts or t-ts[-1]>.25:ts.append(t)
 indices=sorted(set(int(max(0,t-.1)*fps) for t in ts)|set(int((t+.1)*fps) for t in ts))
 filt='scale=320:180,select='+repr('+'.join('eq(n,%d)'%n for n in indices))
 p=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',s['path'],'-vf',filt,'-fps_mode','vfr','-an','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 frames={}
 for i in indices:
  b=p.stdout.read(320*180*3)
  if len(b)==320*180*3:frames[i]=Image.frombytes('RGB',(320,180),b)
 p.communicate()
 for offset in range(0,len(ts),8):
  page=Image.new('RGB',(1280,840),'#111111');d=ImageDraw.Draw(page)
  for j,t in enumerate(ts[offset:offset+8]):
   x=(j%2)*640;y=(j//2)*210
   for k,n in enumerate([int(max(0,t-.1)*fps),int((t+.1)*fps)]):
    if n in frames:page.paste(frames[n],(x+k*320,y+25))
   d.text((x+5,y+5),f'{key} cut candidate {t:.6f}   -0.1s | +0.1s',fill='white')
  page.save(P/f'cut-pairs-{key}-{offset//8+1:02d}.jpg',quality=90)
 print(key,len(ts),flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,items))
