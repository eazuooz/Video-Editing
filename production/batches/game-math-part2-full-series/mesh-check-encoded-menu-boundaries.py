from pathlib import Path
import subprocess,hashlib,json
from PIL import Image,ImageDraw,ImageFont
R=Path('D:/Github/Video-Editing');W=R/'shared/output/game-math-mesh-uv';v=W/'clips/07.mp4'
samples=[(24.9833333333,46.9833333333),(43.8,108.8),(43.9833333333,108.9833333333),(62.9833333333,150.9833333333),(80.25,173.25),(80.4,173.4)]
sheet=Image.new('RGB',(1920,1740),'#e9edf0');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for i,(t,s) in enumerate(samples):
 p=W/f'qa/menu-boundary-{i+1:02}.jpg';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(v),'-frames:v','1','-vf','scale=960:540','-threads','4',str(p)],check=True)
 x=i%2*960;y=i//2*580;d.text((x+8,y+4),f'Encoded scene07 {t:.5f}s / source {s:.5f}s',font=font,fill='black');sheet.paste(Image.open(p),(x,y+30))
p=W/'qa/menu-boundary-sheet.jpg';sheet.save(p,quality=95)
proof=dict(clipPath=v.relative_to(R).as_posix(),clipSha256=hashlib.sha256(v.read_bytes()).hexdigest(),sheet=dict(path=p.relative_to(R).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),samples=samples,status='generated-direct-view-pending')
(W/'qa/menu-boundary-samples.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
print(str(p))
