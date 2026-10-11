"""Native frames for manual landmark selection; no track/pixel approval."""
from pathlib import Path
import cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/cross-game-review-20261011/landmarks';O.mkdir(parents=True,exist_ok=True)
cv2.setNumThreads(1);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
plans=[('dorf','shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm',[98.5,99,99.5,100,100.5,101,117,118,119,120]),('shapez','shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/shapez2-257312662.mp4',[42.7,43,43.2,43.4,43.6,43.8,44,44.2,44.4,44.6])]
for ident,file,times in plans:
 cap=cv2.VideoCapture(str(ROOT/file));pictures=[]
 for t in times:
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=cap.read();assert ok
  im=Image.fromarray(cv2.cvtColor(cv2.resize(frame,(800,450)),cv2.COLOR_BGR2RGB));im.save(O/f'{ident}-{t:.2f}.jpg',quality=96);pictures.append((t,im))
 cap.release()
 for page in range((len(pictures)+5)//6):
  sheet=Image.new('RGB',(1600,1410),'white');d=ImageDraw.Draw(sheet)
  for cell,(t,im) in enumerate(pictures[page*6:page*6+6]):
   x=cell%2*800;y=cell//2*470;sheet.paste(im,(x,y+20));d.text((x+4,y),f'{ident} source{t:.2f}',font=font,fill='black')
  sheet.save(O/f'{ident}-page-{page+1}.jpg',quality=96)
print('Native samples prepared; select only visible mathematical objects.')
