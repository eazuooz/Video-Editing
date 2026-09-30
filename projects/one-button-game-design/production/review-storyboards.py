from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import io
from PIL import Image, ImageDraw
import requests
from yt_dlp import YoutubeDL

dest=Path(__file__).parent/'footage-review'
for video,name in [('GMjG70AHm00','super-star'),('rJXM4EPbPe0','adventure')]:
    data=YoutubeDL({'quiet':True,'no_warnings':True}).extract_info(f'https://www.youtube.com/watch?v={video}',download=False)
    format=next(x for x in data['formats'] if x['format_id']=='sb0')
    rows,cols= format['rows'],format['columns']
    def grab(item):
        i,fragment=item
        response=requests.get(fragment['url'],timeout=30);response.raise_for_status()
        grid=Image.open(io.BytesIO(response.content))
        n=(rows*cols)//2
        pic=grid.crop(((n%cols)*format['width'],(n//cols)*format['height'],(n%cols+1)*format['width'],(n//cols+1)*format['height']))
        pic.thumbnail((158,144))
        return i,round((i*rows*cols+n)/format['fps']),pic
    with ThreadPoolExecutor(max_workers=8) as pool:
        samples=list(pool.map(grab,enumerate(format['fragments'])))
    for page,start in enumerate(range(0,len(samples),72)):
        batch=samples[start:start+72];sheet=Image.new('RGB',(1920,((len(batch)+11)//12)*174),'white');draw=ImageDraw.Draw(sheet)
        for j,(_,seconds,pic) in enumerate(batch):
            x=j%12*160;y=j//12*174;sheet.paste(pic,(x,y));draw.text((x+4,y+147),f'{seconds}s',fill='black')
        sheet.save(dest/f'{name}-overview-{page+1}.jpg')
        print(f'{name}-overview-{page+1}.jpg',flush=True)
