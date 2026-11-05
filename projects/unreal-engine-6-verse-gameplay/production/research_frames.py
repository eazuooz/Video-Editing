from pathlib import Path
import io,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];L=R/'projects/unreal-engine-6-verse-gameplay/research/local';O=L/'frames';O.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for page in range(5):
 sheet=Image.new('RGB',(1920,4*296),'#131713');d=ImageDraw.Draw(sheet)
 for j in range(12):
  t=5+(page*12+j)*10
  if t>590:break
  raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(L/'reference.mp4'),'-frames:v','1','-vf','scale=640:360','-f','image2pipe','-vcodec','png','-threads','1','-'])
  im=Image.open(io.BytesIO(raw)).convert('RGB').resize((640,270));x=j%3*640;y=j//3*296;sheet.paste(im,(x,y));d.text((x+8,y+270),f'{t}s',font=font,fill='white')
 sheet.save(O/f'reference-{page+1}.jpg',quality=88)
print('Source contact sheets extracted')
