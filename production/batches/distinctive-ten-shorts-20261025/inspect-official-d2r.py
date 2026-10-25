"""Read sparse exact-time frames from public publisher B-roll for source selection."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,subprocess,json
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw
B=Path(__file__).parent;L=B/'local/d2r-official';Q=L/'survey';Q.mkdir(parents=True,exist_ok=True)
page='https://blizzard.gamespress.com/en/Kit/Details/Diablo-II-Resurrected-Launch-Press-Kit'
s=BeautifulSoup(requests.get(page,timeout=30).text,'html.parser')
url=s.find('input',{'data-filename':'D2R_Launch_Broll_.mp4'}).find_parent('div',class_='tn-inner').find('i',attrs={'data-preview':True})['data-preview']
times=list(range(5,1066,30))
def get(t):
    p=Q/f'{t:04}.jpg'
    if not p.exists():
        r=subprocess.run(['ffmpeg','-v','error','-n','-threads','1','-ss',str(t),'-i',url,'-frames:v','1','-vf','scale=768:432','-q:v','3','-threads','1',str(p)],capture_output=True,timeout=80)
        if r.returncode:raise RuntimeError('Source frame failed '+str(t))
    return t
with ThreadPoolExecutor(max_workers=2) as pool:
    for t in pool.map(get,times):print('sample',t,flush=True)
for base in range(0,len(times),12):
    im=Image.new('RGB',(1536,1416),'#101010');d=ImageDraw.Draw(im)
    for j,t in enumerate(times[base:base+12]):
        thumb=Image.open(Q/f'{t:04}.jpg');thumb.thumbnail((512,288))
        x=j%3*512;y=j//3*354
        im.paste(thumb,(x,y));d.text((x+10,y+300),f'original {t}s',fill='white')
    im.save(Q/f'sheet-{base//12+1}.jpg',quality=93)
(Q/'index.json').write_text(json.dumps({'sourceUrl':page,'sampleTimes':times,'method':'Sparse source selection frames; not continuous playback review'},indent=2),encoding='utf8')
