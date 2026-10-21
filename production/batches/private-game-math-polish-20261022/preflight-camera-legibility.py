"""Review targeted original camera diagram states; does not grant final QA."""
import datetime,math
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M16');e.authorized();out=e.O/'camera-legibility-preflight';out.mkdir(exist_ok=True)
lesson=read(R/f'production/batches/game-math-part2-full-series/lessons/{e.slug}.json')
records=[];tiles=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for s in lesson['scenes']:
 if s['kind']!='explanation':continue
 slot=next(x for x in e.T['scenes'] if x['id']==s['id'])
 states=sorted({0,len(s['beats'])//2,len(s['beats'])-1})
 for i in states:
  env=dict(os.environ,PYTHONUTF8='1',CAMERA_PREVIEW_SCENE=s['id'],CAMERA_PREVIEW_STATE=str(i),OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
  e.run([R/'manim/.venv/Scripts/python.exe','-m','manim','-s','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',out/'manim',B/'camera-polish-preview.py','Preview'],'camera-still.log',env=env)
  raw=next((out/'manim/images/camera-polish-preview').glob('Preview_*.png'))
  t=slot['start']+min(slot['lineStarts'][i]+1.5,slot['seconds']-.1);dst=out/f'{s["id"]}-{i}.png'
  e.ff(['-i',raw,'-vf',f'setpts=PTS+{t}/TB,ass=captions.ko.ass','-frames:v','1','-threads','1',dst],'camera-still-caption.log',e.O)
  records.append({'scene':s['id'],'mode':s['mode'],'state':i,'globalSeconds':t,'image':rel(dst),'imageSha256':sha(dst)})
  tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS),(0,29));ImageDraw.Draw(tile).text((5,3),f'M16 {s["id"]} {s["mode"]} #{i}',font=font,fill='white');tiles.append(tile)
 print('M16',s['id'],'legibility states generated',flush=True)
for i in range(0,len(tiles),8):
 sheet=Image.new('RGB',(1500,480),'#222222')
 for j,tile in enumerate(tiles[i:i+8]):sheet.paste(tile,(j%4*375,j//4*240))
 sheet.save(out/f'sheet-{i//8+1:02d}.jpg',quality=94)
save(e.H/'camera-legibility-preflight.json',{'status':'await-direct-inspection','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceCode':{rel(p):sha(p) for p in [B/'camera-polish-scenes.py',B/'camera-polish-preview.py',R/'manim/projects/game-math-part2-full-series/camera_frustum.py']},'timelineSha256':sha(e.P/'production/timeline.json'),'samples':records,'sheets':math.ceil(len(tiles)/8),'finalMovingReview':'pending','changes':'Original camera geometry/common state transforms and all narration preserved; guide strokes and post-transform label size only'})
