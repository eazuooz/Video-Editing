"""Make bounded local inspection boards from genuine source pixels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse, json, subprocess
R=Path(__file__).resolve().parents[4]
FF=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('name');ap.add_argument('--step',type=float,default=6);ap.add_argument('--start',type=float,default=0);ap.add_argument('--end',type=float,required=True);a=ap.parse_args()
source=Path(a.source);source=source if source.is_absolute() else R/source
out=R/'projects/familiar-game-rules/production/local/reference-preserving-v2/inspection'/a.name
out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
rows=[];t=a.start
while t<a.end:
 p=out/f'{t:09.3f}.jpg'
 if not p.exists():subprocess.run([str(FF),'-v','error','-threads','2','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2','-q:v','3',str(p)],check=True)
 rows.append({'seconds':t,'path':p.relative_to(R).as_posix()});t+=a.step
for n in range(0,len(rows),12):
 group=rows[n:n+12];board=Image.new('RGB',(1920,4*400),'#141714');draw=ImageDraw.Draw(board)
 for j,row in enumerate(group):
  x=(j%3)*640;y=(j//3)*400;board.paste(Image.open(R/row['path']),(x,y));draw.text((x+14,y+365),f'{a.name}  {row["seconds"]:.3f}s',font=font,fill='white')
 board.save(out/f'board-{n//12+1:02}.jpg',quality=92)
(out/'index.json').write_text(json.dumps({'source':str(source),'samples':rows,'directReview':'pending'},indent=2)+'\n',encoding='utf-8')
print('Prepared',len(rows),'source samples;',len(range(0,len(rows),12)),'boards for direct review')
