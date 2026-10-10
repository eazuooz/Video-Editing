from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision';SRC=O/'sources/_dw9jjRpanA.mp4';assert SRC.exists()
times=list(range(0,713,15));per=24;names=[]
for group in range((len(times)+per-1)//per):
 groupTimes=times[group*per:(group+1)*per];sheet=Image.new('RGB',(1600,((len(groupTimes)+3)//4)*245),'white');draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(groupTimes):
  p=O/f'new-riders-inspection/{t:04d}.png';p.parent.mkdir(exist_ok=True)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(t),'-i',str(SRC),'-frames:v','1','-vf','scale=400:225',str(p)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  x=i%4*400;y=i//4*245;sheet.paste(Image.open(p),(x,y));draw.text((x+5,y+228),f'_dw9jjRpanA / {t}s',fill='black')
 target=O/f'new-riders-inspection/coarse-{group+1}.jpg';sheet.save(target);names.append(str(target))
print(json.dumps({'coarseSheets':names,'finalPlaybackSelectionComplete':False}))
