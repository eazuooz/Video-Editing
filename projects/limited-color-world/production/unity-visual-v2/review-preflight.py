from pathlib import Path
import argparse,json,math
from PIL import Image,ImageDraw,ImageFont
M=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
ap=argparse.ArgumentParser();ap.add_argument('--slug',required=True);ap.add_argument('--revision',default='v2');a=ap.parse_args()
root=M/a.slug/'preflight'/a.revision
out=M/a.slug/'qa'/('preflight-'+a.revision);out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
done=[]
for cut in sorted(root.glob('cut*')):
 if not (cut/'preflight-success.json').exists():continue
 frames=sorted(cut.glob('frame-*.png'))
 for width in (375,640):
  height=round(width*1080/1920);board=Image.new('RGB',(width*2,(height+30)*math.ceil(len(frames)/2)),(20,20,20));d=ImageDraw.Draw(board)
  for i,p in enumerate(frames):
   im=Image.open(p).convert('RGB').resize((width,height),Image.Resampling.LANCZOS);x=i%2*width;y=i//2*(height+30);board.paste(im,(x,y));d.text((x+6,y+height+2),cut.name+' '+p.stem.split('-')[-1]+'f',font=font,fill='white')
  file=out/(cut.name+'-'+str(width)+'.jpg');board.save(file,quality=95)
 done.append(cut.name)
(out/'sheet-index.json').write_text(json.dumps({'slug':a.slug,'revision':a.revision,'cuts':done,'scope':'All7native temporal states per completedcut;375and640 resized sheets. Native PNG preserved.'},indent=2)+'\n','utf-8')
print(out);print(done)
