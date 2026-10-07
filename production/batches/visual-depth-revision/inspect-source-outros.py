from pathlib import Path
import json,subprocess,re,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
names={'motion-sickness-games':'final-concat.txt','hierarchical-game-outlines':'final-concat.txt','game-reward-planning':'visual-concat.txt','avoid-game-comparisons':'visual-concat.txt','making-game-sequels':'visual-concat.txt','familiar-game-rules':'visual-concat.txt'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for slug,name in names.items():
 version='final-v2' if slug=='making-game-sequels' else 'final-v1';concat=ROOT/'projects'/slug/'production'/version/name
 line=concat.read_text('utf-8-sig').strip().splitlines()[-1];match=re.fullmatch(r"file '(.*)'",line)
 if not match:raise RuntimeError('Inspect exact concat')
 src=Path(match[1]);src=src.resolve() if src.is_absolute() else (concat.parent/src).resolve()
 folder=ROOT/'projects'/slug/'production/visual-depth-v1/source-outro-preflight-local'
 if folder.exists():raise RuntimeError('Preserve prior source inspection')
 folder.mkdir();frames=[0,1,2,15,30,60]
 subprocess.run(['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-v','error','-threads','2','-i',str(src),'-vf','select='+ '+'.join(f'eq(n\\,{n})' for n in frames),'-fps_mode','vfr','-frames:v','6','-threads','1',str(folder/'frame-%02d.png')],check=True,creationflags=0x08000000)
 board=Image.new('RGB',(1920,1722),'#e8edef');d=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
 for i,n in enumerate(frames):
  x=i%2*960;y=i//2*574;d.text((x+10,y+3),slug+' | source frame '+str(n),font=font,fill='black');board.paste(Image.open(folder/f'frame-{i+1:02d}.png').resize((960,540)),(x,y+34))
 p=folder/'boundary.jpg';board.save(p,quality=95)
 (folder/'index.json').write_text(json.dumps(dict(source=src.relative_to(ROOT).as_posix(),sourceSha256=sha(src),frames=frames,board=p.relative_to(ROOT).as_posix(),boardSha256=sha(p),directlyRead=False,allFinalPixelsReviewed=False),ensure_ascii=False,indent=2)+'\n','utf-8');print(slug+' source boundary ready')
