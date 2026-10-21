"""Render inexpensive still states with actual captions; no visual autopass."""
import ast,shutil,datetime
from polish_common import *
from PIL import Image,ImageDraw
tree=ast.parse((B/'polygon-scenes.py').read_text('utf8'))
states=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='STATES' for t in n.targets)))
records=[]
for ident in ['M13','M14']:
 e=Episode(ident);e.authorized();out=e.O/'reconstruction-preflight';out.mkdir(exist_ok=True)
 for slot in e.T['scenes']:
  sid=slot['id']
  if sid not in states:continue
  selected=sorted({1,len(states[sid]),max(1,len(states[sid])//2)})
  for count in selected:
   state=states[sid][count-1];cue=slot['sentenceCues'][state[0]];time=slot['start']+min(cue['start']+1,slot['seconds']-.1)
   name=f'{sid}-{count}';target=out/(name+'.png')
   env=dict(os.environ,PYTHONUTF8='1',POLISH_SLUG=e.slug,POLYGON_PREVIEW_SID=sid,POLYGON_PREVIEW_STATE_COUNT=str(count),MATH_RENDER_TIMING=str(e.P/'production/timeline.json'),OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
   e.run([R/'manim/.venv/Scripts/python.exe','-m','manim','-s','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',out/'manim',B/'polygon-preview.py','Preview'],'polygon-still.log',env=env)
   raw=next((out/'manim/images/polygon-preview').glob('Preview_*.png'))
   ass=rel(e.O/'captions.ko.ass');e.ff(['-i',raw,'-vf',f"setpts=PTS+{time}/TB,ass='{ass}'",'-frames:v','1',target],'polygon-still-caption.log')
   mobile=Image.open(target);mobile.thumbnail((375,212));mobile.save(out/(name+'-375.png'))
   records.append({'id':ident,'scene':sid,'stateCount':count,'state':state[3],'sourceCue':cue,'representedGlobalSeconds':time,'native':rel(target),'mobile':rel(out/(name+'-375.png')),'directInspection':'pending'})
  print(ident,sid,'still preflight generated',flush=True)
 # Four 375px frames per row; these sheets are inspected, never an autopass.
 local=[r for r in records if r['id']==ident]
 for start in range(0,len(local),8):
  group=local[start:start+8];sheet=Image.new('RGB',(1500,480),'#eeeeee');draw=ImageDraw.Draw(sheet)
  for j,r in enumerate(group):
   x=j%4*375;y=j//4*240;sheet.paste(Image.open(R/r['mobile']),(x,y+27));draw.text((x+8,y+7),f'{ident} {r["scene"]} state {r["stateCount"]}: {r["state"]}',fill='black')
  sheet.save(out/f'sheet-{start//8+1:02d}.jpg',quality=94)
 save(e.H/'reconstruction-preflight.json',{'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceSha256':sha(B/'polygon-scenes.py'),'captionSha256':sha(e.O/'captions.ko.ass'),'states':local,'directInspection':'pending','movingOutputReview':'pending'})
