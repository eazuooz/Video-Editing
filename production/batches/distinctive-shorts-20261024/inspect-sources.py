"""Decode native gameplay samples for editorial inspection; never upscale a source."""
import json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3]
B=Path(__file__).parent
for row in json.loads((B/'batch.json').read_text(encoding='utf8'))['projects']:
 p=R/'projects'/row['slug']; src=p/'production/local/gameplay.mp4'
 if not src.exists():continue
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)]))
 v=next(s for s in probe['streams'] if s['codec_type']=='video'); assert v['width']>=1920 and v['height']>=1080
 out=p/'production/local/source-inspection';out.mkdir(exist_ok=True)
 (out/'probe.json').write_text(json.dumps(probe,indent=2),encoding='utf8')
 if (out/'overview.jpg').exists():continue
 duration=float(probe['format']['duration']); points=[round(1+i*(duration-3)/19,2) for i in range(20)]
 sheet=Image.new('RGB',(1280,5*204),(16,20,22));d=ImageDraw.Draw(sheet)
 for i,t in enumerate(points):
  target=out/f'{i:02}.jpg'
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=320:180','-threads','2',str(target)],check=True)
  sheet.paste(Image.open(target),((i%4)*320,(i//4)*204));d.text(((i%4)*320+5,(i//4)*204+181),str(t)+'s',fill='white')
 sheet.save(out/'overview.jpg',quality=95)
 print(row['slug'],v['width'],v['height'],v['r_frame_rate'],duration,flush=True)
