"""Create local-only source contact sheets before dependent narration is written."""
from pathlib import Path
import argparse,json,hashlib,subprocess
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--windows',required=True);p.add_argument('--tag',required=True);p.add_argument('--interval',type=float,default=3);a=p.parse_args()
source=root/a.source;windows=json.loads((root/a.windows).read_text(encoding='utf-8'));work=root/'shared/output/game-math-part2-full-series/inspection'/a.tag;work.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);records=[]
for wi,w in enumerate(windows,1):
 start,end=w['in'],w['out'];ts=[];t=start
 while t<end-.1:ts.append(round(t,3));t+=a.interval
 ts.append(end-.1);frames=[]
 for t in ts:
  f=work/f'{wi:02}-{t:g}.jpg';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=384:216',str(f)],check=True);frames.append((t,f))
 for offset in range(0,len(frames),20):
  group=frames[offset:offset+20];sheet=Image.new('RGB',(1536,245*((len(group)+3)//4)),'white');draw=ImageDraw.Draw(sheet)
  for j,(t,f) in enumerate(group):
   x=(j%4)*384;y=(j//4)*245;sheet.paste(Image.open(f),(x,y));draw.text((x+6,y+216),f'{wi}: {t:g}s',font=font,fill='black')
  out=work/f'window-{wi:02}-{offset//20+1}.jpg';sheet.save(out,quality=94);print(out.relative_to(root),flush=True)
  records.append({'window':wi,'in':start,'out':end,'sampleIntervalSeconds':a.interval,'sheet':out.relative_to(root).as_posix(),'sampleTimes':[t for t,_ in group]})
(work/'generated-samples.json').write_text(json.dumps({'source':a.source,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'records':records,'humanVisualReview':'pending; generated sheets alone do not confirm valid footage'},indent=2)+'\n',encoding='utf8')
