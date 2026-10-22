"""Read-only media inspection; contact sheets retain exact source timestamps."""
import argparse, json, subprocess, math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]
a=argparse.ArgumentParser();a.add_argument('name');a.add_argument('source');a.add_argument('--start',type=float,default=0);a.add_argument('--end',type=float);a.add_argument('--step',type=float,default=15);args=a.parse_args()
p=R/args.source;o=R/'shared/output/private-math-concept-fit-20261023/candidates'/args.name;o.mkdir(parents=True,exist_ok=True)
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],text=True,encoding='utf8'))
v=next(x for x in meta['streams'] if x['codec_type']=='video');duration=float(meta['format']['duration']);end=min(args.end or duration,duration)
items=[]
for i in range(math.ceil((end-args.start)/args.step)):
 t=args.start+i*args.step;dst=o/f'{t:09.3f}.jpg'
 if not dst.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=640:360','-q:v','3','-y',str(dst)],check=True,capture_output=True)
 items.append({'path':dst.relative_to(R).as_posix(),'time':t})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);sheets=[]
for ix in range(0,len(items),12):
 group=items[ix:ix+12];im=Image.new('RGB',(1920,1560),'#111');dr=ImageDraw.Draw(im)
 for n,x in enumerate(group):
  left=n%3*640;top=n//3*390;im.paste(Image.open(R/x['path']),(left,top+30));dr.text((left+6,top+3),f'{args.name} {x["time"]:.2f}s',fill='white',font=font)
 dest=o/f'sheet-{args.start:g}-{ix//12+1:02}.jpg';im.save(dest,quality=88);sheets.append(dest.relative_to(R).as_posix())
report={'source':args.source,'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'duration':duration,'start':args.start,'end':end,'step':args.step,'samples':items,'sheets':sheets,'review':'pending'}
(o/f'samples-{args.start:g}-{end:g}-{args.step:g}.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ['source','width','height','fps','duration','sheets']}))
