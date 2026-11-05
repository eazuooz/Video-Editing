from pathlib import Path
import requests,json,hashlib,re
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[3];P=R/'projects/unreal-engine-6-verse-gameplay';L=P/'research/local';A=L/'evidence';A.mkdir(exist_ok=True)
def get(url,name):
 p=A/name
 if not p.exists():
  r=requests.get(url,timeout=60);r.raise_for_status();p.write_bytes(r.content)
 return p
records=[]
html=(L/'tokyo.html').read_text(encoding='utf-8');s=BeautifulSoup(html,'html.parser')
urls=[]
for i in s.select('img'):
 u=i.get('data-pagespeed-lazy-src') or i.get('src','')
 if '/cms/wp-content/uploads/2026/11/' in u and u not in urls:urls.append(u)
for n,u in enumerate(urls):
 try:
  p=get(u,f'conference-{n:02}.jpg');im=Image.open(p)
  records.append({'id':p.stem,'url':u,'page':'https://gamemakers.jp/article/2026_11_03_149187/','path':p.relative_to(R).as_posix(),'dimensions':im.size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'classification':'primary-conference-photograph'})
 except Exception as e:print(str(e),flush=True)
(A/'catalog.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
for batch in range(0,len(records),12):
 sheet=Image.new('RGB',(1440,4*235),'#1c1c1c');d=ImageDraw.Draw(sheet)
 for j,r in enumerate(records[batch:batch+12]):
  im=Image.open(R/r['path']).convert('RGB');im.thumbnail((470,207));x=(j%3)*480;y=(j//3)*235;sheet.paste(im,(x,y));d.text((x+6,y+210),r['id']+' '+str(r['dimensions']),fill='white')
 sheet.save(A/f'conference-contact-{batch//12}.jpg')
print('photos',len(records),flush=True)
