"""Readable contact sheets of every final burned caption, retaining nearby UI."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
WORK=Path(__file__).parent/'final-v1';qa=json.loads((WORK/'qa.json').read_text(encoding='utf8'));points=qa['captionImages']['images'];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);pages=[]
for i,p in enumerate(points):
    page=i//32
    if page==len(pages):pages.append(Image.new('RGB',(1920,1760),'#dfe6ee'))
    native=Path(__file__).resolve().parents[3]/p['path'];im=Image.open(native).crop((0,875,1920,1055)).resize((960,90));x=i%2*960;y=i//2%16*110;pages[page].paste(im,(x,y+20));ImageDraw.Draw(pages[page]).text((x+8,y),f"Cue {i+1:03d} / {p['seconds']:.3f}s",font=font,fill='#222222')
for i,p in enumerate(pages):p.save(WORK/f'caption-strips-{i+1:02d}.jpg',quality=95)
(WORK/'caption-strip-index.json').write_text(json.dumps({'count':len(points),'pages':len(pages),'crop':[0,875,1920,1055],'source':'qa.json captionImages current final output native frames','directReview':'pending'},indent=2)+'\n',encoding='utf8');print(len(points),'current burned captions on',len(pages),'readable sheets')
