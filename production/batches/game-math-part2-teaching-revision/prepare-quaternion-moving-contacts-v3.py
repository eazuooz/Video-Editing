"""Current narrated/captioned moving-frame samples, with source SHA binding."""
from pathlib import Path
import json,hashlib,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/narrated-scene-review'
rows=json.loads((O/'index.json').read_text(encoding='utf8'));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
for ident,row in rows.items():
    source=O/row['file'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
    cap=cv2.VideoCapture(str(source));fps=cap.get(cv2.CAP_PROP_FPS);count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));assert fps==60 and count==row['frames']
    P=ROOT/'projects'/row['slug'];t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'));slot=next(s for s in t['scenes'] if s['id']==ident)
    if slot['classification']=='actual':
        times=[i/3 for i in range(1,int(row['seconds']*3))]
    else:
        times=sorted({.25,*[min(row['seconds']-.2,x+.25) for x in slot['lineStarts']],*[min(row['seconds']-.2,x+.75) for x in slot['fragmentCues'].values()],row['seconds']*.35,row['seconds']*.65,row['seconds']-.7})
    for page,start in enumerate(range(0,len(times),8),1):
        sheet=Image.new('RGB',(1920,2304),'#efefef');draw=ImageDraw.Draw(sheet)
        for i,at in enumerate(times[start:start+8]):
            cap.set(cv2.CAP_PROP_POS_MSEC,at*1000);ok,frame=cap.read();assert ok
            im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).resize((960,540));x=i%2*960;y=i//2*576
            sheet.paste(im,(x,y+32));draw.text((x+8,y+6),f'{ident} actual-timed voice/caption {at:.3f}s',font=font,fill='black')
        sheet.save(O/f'{ident}-moving-{page:02}.jpg',quality=94)
    cap.release()
    print(ident,len(times),'current moving/caption frames extracted; direct review pending',flush=True)
(O/'moving-contact-index.json').write_text(json.dumps({'currentFiles':rows,'directMovingPixelsApproved':False,'allImagesLocalOnly':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
