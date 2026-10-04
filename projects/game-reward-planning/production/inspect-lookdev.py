from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,re,os
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
version=sys.argv[1] if len(sys.argv)>1 else 'v1'
assert re.fullmatch(r'v\d+',version)
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
source=ROOT/f'shared/output/motion-canvas/game-reward-planning-lookdev-{version}.mp4'
dest=ROOT/f'projects/game-reward-planning/production/lookdev-{version}'
if (dest/'inspection.json').exists():raise RuntimeError('Preserve existing inspection')
requests=[]
for i,sid in enumerate(['01','03','05','07','09','11','13']):
 for phase,offset in [('early',1.5),('middle',4.7),('late',7.3),('transition',5.65 if i else 4.15)]:
  seconds=8*i+offset;file=dest/f'{sid}-{phase}.png'
  subprocess.run([str(FF),'-v','error','-ss',str(seconds),'-i',str(source),'-frames:v','1',str(file)],check=True)
  requests.append({'scene':sid,'phase':phase,'seconds':seconds,'path':file.relative_to(ROOT).as_posix()})
for page in range(4):
 chunk=requests[page*7:(page+1)*7]
 canvas=Image.new('RGB',(1920,4*564),'#e8ece9');draw=ImageDraw.Draw(canvas)
 for n,item in enumerate(chunk):
  x=n%2*960;y=n//2*564
  canvas.paste(Image.open(ROOT/item['path']).convert('RGB').resize((960,540)),(x,y+24))
  draw.text((x+12,y+5),f"Scene {item['scene']} | {item['phase']} | {item['seconds']:.2f}s",fill='black')
 canvas.save(dest/f'contact-{page+1}.png')
probe=json.loads(subprocess.check_output([str(FP),'-v','error','-show_streams','-show_format','-of','json',str(source)],text=True))
result=subprocess.run([str(FF),'-hide_banner','-v','error','-threads','2','-i',str(source),'-f','null','-'],capture_output=True,text=True)
(dest/'full-decode.log').write_text(result.stderr,encoding='utf-8')
record={'pid':os.getpid(),'inspectedAt':datetime.now(timezone.utc).isoformat(),'source':source.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frames':requests,'streamProbe':probe,'fullDecodeExitCode':result.returncode,'fullDecodeLog':(dest/'full-decode.log').relative_to(ROOT).as_posix(),'silentLookdev':True,'finalNarratedVideo':False,'directVisualReview':'pending','finalCaptionApproval':False}
(dest/'inspection.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if result.returncode or result.stderr:raise RuntimeError('Lookdev decode errors require review')
print('28 layout/transition frames extracted; silent layout approval pending.',flush=True)
