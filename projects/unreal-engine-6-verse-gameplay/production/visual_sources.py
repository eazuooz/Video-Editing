"""Select primary documentation images and inspect the installed engine's example images."""
from pathlib import Path
from PIL import Image,ImageDraw
from bs4 import BeautifulSoup
import json,re,requests,hashlib
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1]
A=P/'research/local/evidence';A.mkdir(parents=True,exist_ok=True)
E=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Content/Tutorial')
records=[]
for index,(width,asset) in enumerate([(1920,'cmq9rh3jx2gic07o8rotnzq7f'),(1200,'cms7ijbgj1dmo07n4ybiz7bmv')]):
    url=f'https://cms-assets.unrealengine.com/AiKUh5PQCTaOFnmJDZJBfz/resize=width:{width}/quality=value:90/auto_image/{asset}'
    dest=A/f'road-{index}.jpg'
    if not dest.exists():
        data=requests.get(url,timeout=20);data.raise_for_status()
        from io import BytesIO
        Image.open(BytesIO(data.content)).convert('RGB').save(dest)
def add(p,src,page):
    try: im=Image.open(p); im.verify(); im=Image.open(p); im.thumbnail((330,160))
    except OSError:return
    records.append((p,src,page,im.copy()))
for p in sorted(E.rglob('*.png')):
    if ('Blueprint' in str(p) or 'Blueprint' in p.name) and Image.open(p).width>=270:
        add(p,str(p),'UE 5.8 installed editor tutorial')
urls=['https://dev.epicgames.com/documentation/en-us/fortnite/working-with-entities-and-components-in-unreal-editor-for-fortnite','https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-framework-in-unreal-engine']
for i,url in enumerate(urls):
    page=requests.get(url,timeout=20).text
    discovered=list(dict.fromkeys(re.findall(r'"original_url":"(https[^"]+)"',page)))
    for j,src in enumerate(discovered[:8]):
        if not src.startswith('https://') or 'cloudfront.net/documentation/images/' not in src:continue
        p=A/f'original-{i}-{j}.png'
        try:
            response=requests.get(src,timeout=15);response.raise_for_status();p.write_bytes(response.content)
            add(p,src,url)
        except requests.RequestException:pass
for index,(p,src,page,im) in enumerate(records):print(index, p.name,Image.open(p).size)
(A/'usable-images.json').write_text(json.dumps([dict(id=n,file=str(p),source=src,page=page) for n,(p,src,page,_) in enumerate(records)],indent=2),encoding='utf-8')
for start in range(0,len(records),20):
    sheet=Image.new('RGB',(1400,5*190),'#141916');d=ImageDraw.Draw(sheet)
    for j,(p,src,page,im) in enumerate(records[start:start+20]):
        x=j%4*350;y=j//4*190;sheet.paste(im,(x,y));d.text((x,y+161),f'{start+j}  {p.stem[:30]}',fill='white')
    sheet.save(A/f'available-{start//20}.jpg')
