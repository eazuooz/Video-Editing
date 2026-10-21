"""Current numeric-polygon font states with fixed captions; never auto-pass."""
import sys,datetime,math
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode(sys.argv[1]);assert e.id in ['M13','M14'];e.authorized()
out=e.O/'polygon-legibility-preflight';out.mkdir(exist_ok=True)
lesson=read(R/'production/batches/game-math-part2-full-series/lessons/game-math-polygons-triangulation.json')
records=[];tiles=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for slot in e.T['scenes']:
 if slot['classification']!='explanation' or not slot['id'].isdigit():continue
 s=next(s for s in lesson['scenes'] if s['id']==slot['id'])
 for i in sorted({0,len(s['beats'])//2,len(s['beats'])-1}):
  env=dict(os.environ,PYTHONUTF8='1',POLISH_SLUG=e.slug,POLYGON_PREVIEW_SID=s['id'],POLYGON_PREVIEW_STATE_COUNT=str(i+1),OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
  e.run([R/'manim/.venv/Scripts/python.exe','-m','manim','-s','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',out/'manim',B/'polygon-legibility-preview.py','Preview'],'polygon-font-still.log',env=env)
  raw=next((out/'manim/images/polygon-legibility-preview').glob('Preview_*.png'))
  t=slot['start']+min(slot['lineStarts'][i]+1.5,slot['seconds']-.1);dst=out/f'{s["id"]}-{i}.png'
  e.ff(['-i',raw,'-vf',f'setpts=PTS+{t}/TB,ass=captions.ko.ass','-frames:v','1','-threads','1',dst],'polygon-font-caption.log',e.O)
  records.append({'scene':s['id'],'mode':s['mode'],'state':i,'globalSeconds':t,'image':rel(dst),'imageSha256':sha(dst)})
  tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS),(0,29));ImageDraw.Draw(tile).text((5,3),f'{e.id} {s["id"]} {s["mode"]} #{i}',font=font,fill='white');tiles.append(tile)
 print(e.id,s['id'],'font states generated',flush=True)
for i in range(0,len(tiles),8):
 sheet=Image.new('RGB',(1500,480),'#222222')
 for j,tile in enumerate(tiles[i:i+8]):sheet.paste(tile,(j%4*375,j//4*240))
 sheet.save(out/f'sheet-{i//8+1:02d}.jpg',quality=94)
code=[B/'polygon-legibility-scenes.py',B/'polygon-legibility-preview.py',B/'polygon-scenes.py',R/'manim/projects/game-math-part2-full-series/geometry_polygons.py',R/'manim/projects/game-math-part2-full-series/lesson.py']
save(e.H/'polygon-legibility-preflight.json',{'status':'await-direct-inspection','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceCode':{rel(p):sha(p) for p in code},'timelineSha256':sha(e.P/'production/timeline.json'),'samples':records,'sheets':math.ceil(len(tiles)/8),'finalMovingReview':'pending','changes':'Existing undersized vertex/center labels, formulas and notes enlarged. Circumcenter diagram uniformly scaled .6 to .48; L-shaped diagram screen origin shifted down .25 to clear subtitle/rule. Original logical model, palette, indices, calculations, source strings, timings and animations retained.'})
