from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
W=Path(__file__).resolve().parent; R=W.parents[3]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
for key in ['captionImages','compositionImages']:
    points=json.loads((W/(key+'-changed.json')).read_text(encoding='utf8'))
    per=32 if key=='captionImages' else 8
    for start in range(0,len(points),per):
        page=Image.new('RGB',(1920,1760 if per==32 else 2320),'#dfe6ee')
        draw=ImageDraw.Draw(page)
        for i,p in enumerate(points[start:start+per]):
            im=Image.open(R/p['path'])
            if per==32: im=im.crop((0,875,1920,1055)).resize((960,90)); h=110
            else: im=im.resize((960,540)); h=580
            x=i%2*960;y=i//2*h
            page.paste(im,(x,y+20));draw.text((x+8,y),p['label']+' '+str(round(p['seconds'],3)),font=font,fill='#222222')
        page.save(W/f'cleanup-diff-{key}-{start//per+1:02d}.jpg',quality=95)
