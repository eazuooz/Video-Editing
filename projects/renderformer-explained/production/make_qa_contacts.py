from pathlib import Path
from PIL import Image, ImageDraw

root=Path(__file__).parent/'layout-qa'
pages=sorted(root.glob('page-*.png'))
for start in range(0,len(pages),8):
    sheet=Image.new('RGB',(1600,1840),'#d3d6d8')
    draw=ImageDraw.Draw(sheet)
    for j,path in enumerate(pages[start:start+8]):
        im=Image.open(path).convert('RGB')
        # Discard only the outer narration-safe margin in this QA contact sheet.
        im=im.crop((215,10,1705,860));im.thumbnail((784,435))
        x,y=(j%2)*800+8,(j//2)*460+24
        sheet.paste(im,(x,y));draw.text((x,y-20),f'PAGE {start+j+1:02}',fill='black')
    sheet.save(root/f'contact-{start+1:02}.jpg',quality=93)
