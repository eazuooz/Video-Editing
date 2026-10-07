from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,sys
ROOT=Path(__file__).resolve().parents[3]
slug=sys.argv[1] if len(sys.argv)>1 else 'picking-sides'
revision=sys.argv[2] if len(sys.argv)>2 else 'v1'
folder=ROOT/'projects'/slug/'production/visual-depth-v1'/(f'white-preflight-{revision}-local' if '--preflight' in sys.argv else 'white-lookdev-local' if revision=='v1' else f'white-lookdev-{revision}-local')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
files=sorted(folder.glob('*.png'));boards=[]
for start in range(0,len(files),6):
 batch=files[start:start+6];out=folder/f'board-{start//6+1:02}.jpg'
 board=Image.new('RGB',(1920,3*574),'#edf0f2');d=ImageDraw.Draw(board)
 for i,p in enumerate(batch):
  x=i%2*960;y=i//2*574;im=Image.open(p).convert('RGB');im.thumbnail((960,540));board.paste(im,(x,y+34));d.text((x+12,y+3),p.stem,font=font,fill='#202020')
 board.save(out,quality=94);boards.append(dict(path=out.relative_to(ROOT).as_posix(),frames=[p.name for p in batch]))
(folder/'index.json').write_text(json.dumps(dict(status='prepared-local-only-not-reviewed',frames=len(files),boards=boards),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(frames=len(files),boards=len(boards))))
