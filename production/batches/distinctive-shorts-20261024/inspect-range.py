import subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3]
slug,start,duration=sys.argv[1],float(sys.argv[2]),int(sys.argv[3]);p=R/'projects'/slug/'production/local'
out=p/f'inspection-{start:g}-{duration}';out.mkdir(exist_ok=True)
sheet=Image.new('RGB',(1280,204*((duration+3)//4)),(10,10,10));d=ImageDraw.Draw(sheet)
for i in range(duration):
 target=out/f'{i:02}.jpg';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start+i),'-i',str(p/'gameplay.mp4'),'-frames:v','1','-vf','scale=320:180','-threads','2',str(target)],check=True)
 sheet.paste(Image.open(target),((i%4)*320,(i//4)*204));d.text(((i%4)*320+5,(i//4)*204+181),str(start+i)+'s',fill='white')
sheet.save(out/'sequence.jpg',quality=95);print(out/'sequence.jpg')
