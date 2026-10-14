"""Timestamped source inspection, separate from publication assets."""
from pathlib import Path
import argparse,json,subprocess,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('--start',type=float,default=0);p.add_argument('--end',type=float);p.add_argument('--step',type=float,default=20);a=p.parse_args()
source=ROOT/'shared/sources'/SLUG/'actual-footage-v2'/(a.key+'.webm')
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(source)]))
end=min(a.end or float(info['format']['duration']),float(info['format']['duration']))
out=ROOT/'shared/output'/SLUG/'actual-footage-survey'/a.key;out.mkdir(parents=True,exist_ok=True)
rows=[]
for i in range(math.ceil((end-a.start)/a.step)):
 t=min(a.start+(i+.5)*a.step,end-.05);im=out/f'{t:010.3f}.jpg'
 if not im.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2','-q:v','3',str(im)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 rows.append({'time':t,'path':im.relative_to(ROOT).as_posix()})
prefix=f'survey-{a.start:g}-{end:g}-{a.step:g}'
for page in range(math.ceil(len(rows)/12)):
 canvas=Image.new('RGB',(1920,1560),'#151515');d=ImageDraw.Draw(canvas)
 for i,row in enumerate(rows[page*12:(page+1)*12]):
  x=i%3*640;y=i//3*390;canvas.paste(Image.open(ROOT/row['path']),(x,y));d.text((x+8,y+367),f'{a.key} source {row["time"]:.3f}s',fill='white')
 canvas.save(out/f'{prefix}-{page+1:02d}.jpg',quality=92)
(out/f'{prefix}.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'key':a.key,'frames':len(rows),'prefix':prefix}),flush=True)
