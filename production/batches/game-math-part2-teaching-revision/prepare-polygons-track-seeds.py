"""Local observed-frame references, never upload or commit these reproducible images."""
from pathlib import Path
import cv2,json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-track-seeds';O.mkdir(parents=True,exist_ok=True)
cv2.setNumThreads(2)
base='shared/output/game-math-polygons-triangulation/clips/'
tiny='shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/'
fresh='shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/'
noita='shared/output/game-math-part2-full-series/sources/igcymdI4XYM.mp4'
seeds=[('02',base+'02.mp4',11),('05',base+'05.mp4',12),('08',base+'08.mp4',24),('11',base+'11.mp4',27),('14',base+'14.mp4',7),('17',base+'17.mp4',24),('19',base+'19.mp4',18),('21',base+'21.mp4',10),
 ('QG01-reference',tiny+'tiny-glade-257046593.mp4',18),('QG01-rotate',tiny+'tiny-glade-256965562.mp4',42),('QG02-arch',tiny+'tiny-glade-257046593.mp4',6),('QG02-path',tiny+'tiny-glade-256965562.mp4',13),
 ('QG03-height',tiny+'tiny-glade-256965562.mp4',27),('QG03-opening',noita,86),('QG04-lake',tiny+'tiny-glade-257046593.mp4',34),('QG04-notch',noita,457),('QG05-opening',noita,794),
 ('QG06-circle',fresh+'shapez2-257294952.mp4',1),('QG06-square',fresh+'shapez2-257312662.mp4',43),('QG07-passage',noita,262),('QG07-return',noita,274),('QG07-path',fresh+'shapez2-257312662.mp4',33),('17-return',base+'17.mp4',26),('QG06-square-after-cut',fresh+'shapez2-257312662.mp4',45),('05-night',base+'05.mp4',46),('05-night-later',base+'05.mp4',48)]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
records=[]
for ident,file,time in seeds:
 cap=cv2.VideoCapture(str(ROOT/file));cap.set(cv2.CAP_PROP_POS_MSEC,time*1000);ok,frame=cap.read();assert ok,(ident,time);cap.release()
 im=Image.fromarray(cv2.cvtColor(cv2.resize(frame,(800,450)),cv2.COLOR_BGR2RGB));im.save(O/f'{ident}.jpg',quality=97)
 records.append({'id':ident,'file':file,'time':time})
for page in range((len(records)+3)//4):
 sheet=Image.new('RGB',(1600,944),'white');draw=ImageDraw.Draw(sheet)
 for cell,row in enumerate(records[page*4:page*4+4]):
  x=cell%2*800;y=cell//2*472;sheet.paste(Image.open(O/f'{row["id"]}.jpg'),(x,y+22));draw.text((x+5,y),f'{row["id"]} native {row["time"]}s · 800x450',font=font,fill='black')
 sheet.save(O/f'seeds-{page+1:02}.jpg',quality=97)
(O/'inputs.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
print(len(records),'frames extracted; observations pending.')
