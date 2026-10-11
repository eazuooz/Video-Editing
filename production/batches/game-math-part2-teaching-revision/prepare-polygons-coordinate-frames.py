"""Visible coordinate grids for manual source-edge authoring, local QA only."""
from pathlib import Path
import cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-coordinate-frames';O.mkdir(parents=True,exist_ok=True)
base='shared/output/game-math-polygons-triangulation/clips/'
fresh='shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/'
frames=[('11',base+'11.mp4',27),('14',base+'14.mp4',7),('19',base+'19.mp4',18),('21',base+'21.mp4',12),('QG01-rotate',fresh+'tiny-glade/tiny-glade-256965562.mp4',42),('QG02-arch',fresh+'tiny-glade/tiny-glade-257046593.mp4',7.5),('QG02-gameplay',fresh+'tiny-glade/tiny-glade-256965562.mp4',9.8)]
frames.extend([('QG02-arch-6.5',fresh+'tiny-glade/tiny-glade-257046593.mp4',6.5),('QG03-height',fresh+'tiny-glade/tiny-glade-256965562.mp4',27),('QG06-square',fresh+'shapez2-257312662.mp4',43),('QG07-passage','shared/output/game-math-part2-full-series/sources/igcymdI4XYM.mp4',262)])
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',11);cv2.setNumThreads(2)
frames.extend([(f'QG03-opening-{at}','shared/output/game-math-part2-full-series/sources/igcymdI4XYM.mp4',at) for at in [90.6,91.6,94]])
for ident,file,t in frames:
 c=cv2.VideoCapture(str(ROOT/file));c.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=c.read();assert ok;c.release()
 im=Image.fromarray(cv2.cvtColor(cv2.resize(f,(800,450)),cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(im)
 for x in range(0,800,50):
  d.line([(x,0),(x,450)],fill='#888888',width=1)
  for y in range(50,450,50):d.text((x+2,y+2),f'{x},{y}',font=font,fill='white',stroke_width=1,stroke_fill='black')
 for y in range(50,450,50):d.line([(0,y),(800,y)],fill='#888888',width=1)
 im.save(O/f'{ident}.jpg',quality=97)
print(len(frames),'coordinate reference frames')
