"""Assemble QA contact sheets; never modifies source captures or artwork."""
from pathlib import Path
from PIL import Image,ImageDraw
base=Path(__file__).parent
sheet=Image.new('RGB',(1920,5*385),'white');draw=ImageDraw.Draw(sheet)
for row,mode in enumerate(['rate','interval','poses','pause','render']):
    draw.text((10,row*385+5),mode+' v2 / original captured frames 75, 90, 1650',fill='black')
    for col,frame in enumerate([75,90,1650]):
        image=Image.open(base/f'prototype-{mode}-v2-{frame}.jpg').convert('RGB')
        image.thumbnail((640,360));sheet.paste(image,(col*640,row*385+25))
sheet.save(base/'prototype-v2-contact.jpg',quality=95)
