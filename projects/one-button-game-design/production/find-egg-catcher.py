from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image,ImageDraw
from yt_dlp import YoutubeDL
import requests,io,numpy as np
dest=Path(__file__).parent/'footage-review'
d=YoutubeDL({'quiet':True,'no_warnings':True}).extract_info('https://www.youtube.com/watch?v=rJXM4EPbPe0',download=False)
f=next(x for x in d['formats'] if x['format_id']=='sb0');per=f['rows']*f['columns'];w,h=f['width'],f['height']
def grab(item):
 i,z=item;r=requests.get(z['url'],timeout=30);r.raise_for_status();grid=Image.open(io.BytesIO(r.content))
 return [((i*per+n)/f['fps'],grid.crop((n%f['columns']*w,n//f['columns']*h,(n%f['columns']+1)*w,(n//f['columns']+1)*h)).convert('RGB')) for n in range(per)]
with ThreadPoolExecutor(max_workers=8) as pool:frames=[x for batch in pool.map(grab,enumerate(f['fragments'])) for x in batch]
def descriptor(pic):
 pixels=np.array(pic.resize((24,24))).reshape(-1,3);return np.histogramdd(pixels,bins=6,range=[(0,256)]*3)[0].flatten()/len(pixels)
reference=min(frames,key=lambda row:abs(row[0]-858));hist=descriptor(reference[1])
ranked=sorted(frames,key=lambda row:float(np.abs(descriptor(row[1])-hist).sum()))[:60]
sheet=Image.new('RGB',(2000,1200),'white');draw=ImageDraw.Draw(sheet)
for k,(t,p) in enumerate(ranked):
 x=k%10*200;y=k//10*200;sheet.paste(p.resize((196,180)),(x,y));draw.text((x+5,y+184),str(round(t))+'s',fill='black')
sheet.save(dest/'egg-catcher-candidates.jpg')
