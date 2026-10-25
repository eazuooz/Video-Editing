"""Inspect only the publisher's separately offered gameplay B-roll.

This is unrelated to the rejected YouTube search command. No YouTube access,
credentials, authentication, uploader material or game captures are requested.
"""
from pathlib import Path
import requests, subprocess, json
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
P=Path(__file__).resolve().parents[1]
Q=P/'production/local/source-review';Q.mkdir(parents=True,exist_ok=True)
PAGE='https://blizzard.gamespress.com/en/Kit/Details/Diablo-II-Resurrected-Launch-Press-Kit'
s=BeautifulSoup(requests.get(PAGE,timeout=30).text,'html.parser')
entry=s.find('input',{'data-filename':'D2R_Launch_Broll_.mp4'})
assert entry
url=entry.find_parent('div',class_='tn-inner').find('i',attrs={'data-preview':True})['data-preview']
start=12;length=72;fps=2
if not (Q/'frame-00144.jpg').exists():
    subprocess.run(['ffmpeg','-v','error','-n','-threads','2','-ss',str(start),'-i',url,'-t',str(length),'-vf',f'fps={fps},scale=960:540','-q:v','2','-threads','1',str(Q/'frame-%05d.jpg')],check=True)
rows=[]
for n,file in enumerate(sorted(Q.glob('frame-*.jpg'))):rows.append(dict(path=file.name,originalTime=start+n/fps))
for base in range(0,len(rows),12):
    canvas=Image.new('RGB',(1920,1160),'#101010');d=ImageDraw.Draw(canvas)
    for i,row in enumerate(rows[base:base+12]):
        im=Image.open(Q/row['path']);im.thumbnail((480,270));x=i%4*480;y=i//4*386
        canvas.paste(im,(x,y));d.text((x+8,y+280),f'original {row["originalTime"]:.1f} s',fill='white')
    canvas.save(Q/f'sheet-{base//12+1:02}.jpg',quality=94)
(Q/'index.json').write_text(json.dumps(dict(sourceUrl=PAGE,fileName=entry['data-filename'],originalStart=start,originalEnd=start+length,reviewSamplingFps=fps,rows=rows,scope='Sequential 2fps source selection images; not full-speed playback or audio listening'),indent=2),encoding='utf8')
print(json.dumps(dict(frames=len(rows),sheets=(len(rows)+11)//12,sourceRange=[start,start+length])))
