"""Contact sheets for the actual encoded native studies, with source identities."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;L=H.parent/'local/real-clips-v2';font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for ep in sys.argv[1:]:
    rows=[]
    for p in sorted((L/'studies').glob(ep+'-*.json')):
        d=json.loads(p.read_text('utf-8'));files=sorted((L/'study-frames'/p.stem).glob('*.png'))
        if len(files)!=d['frames']:continue
        rows.append((p.stem,d,files))
    if not rows:continue
    canvas=Image.new('RGB',(1600,265*len(rows)),'#15221c');pen=ImageDraw.Draw(canvas)
    for row,(key,d,files) in enumerate(rows):
        pen.text((8,row*265+6),key+' | '+str(d['sourceClip']).split('/')[-1],font=font,fill='white')
        frames=d.get('inspectionFrames',[12,42,84,min(140,d['frames']-1)])
        for column,k in enumerate(frames):
            im=Image.open(files[min(k,len(files)-1)]).convert('RGB').resize((400,225),Image.Resampling.LANCZOS)
            ImageDraw.Draw(im).text((8,6),str(k),font=font,fill='#c23d30');canvas.paste(im,(column*400,row*265+40))
    canvas.save(L/(ep+'-native-inspection.jpg'),quality=90)
    print(ep,len(rows),'studies')
