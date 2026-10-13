"""Recreate the two editable screen-space UI annotations when restoring local assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

def ensure_annotations(directory):
 directory=Path(directory);directory.mkdir(exist_ok=True)
 font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',29)
 for kind in ['parent','children']:
  target=directory/f'sound-{kind}.png'
  if target.exists():continue
  im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
  if kind=='parent':d.line([(309,81),(583,81)],fill='#d93b38',width=6)
  else:
   d.line([(1491,155),(1512,155),(1512,472),(1491,472)],fill='#0b8c86',width=6)
   d.rounded_rectangle((1744,174,1904,310),radius=12,fill='#111820de')
   d.multiline_text((1824,242),'소리 아래\n세부 항목',font=font,fill='white',anchor='mm',align='center',spacing=8)
  im.save(target)
