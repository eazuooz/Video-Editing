from pathlib import Path
import urllib.request,subprocess,json,hashlib
R=Path('D:/Github/VideoEditing')
for slug in ['limited-color-world','computer-controlled-players']:
 a=R/'projects'/slug/'production/local/batch-v1/visual-assets';a.mkdir(exist_ok=True)
 if slug=='limited-color-world':
  for i in [10,11,12,13,14]:
   p=a/f'puyo-filter-{i}.jpg'
   if not p.exists():urllib.request.urlretrieve(f'https://puyo.sega.jp/puyopuyotetris2/images/info/210204/upd02-img{i}.jpg',p)
 shots=[('puyo', 'puyo-intro-ot4gqysX29c.mp4',1107),('mario','wonder-before.mp4',9),('flower','wonder-after.mp4',1.5)] if slug=='limited-color-world' else [('smash','smash-cpu-I3LV8o_xhR8-section.mp4',150),('dice','dicey-reunion-fVsWXAAccVg.mp4',10),('mario','smash-mario-INk1W8OujQI.mp4',4.6)]
 for key,fn,t in shots:
  p=a/(key+'.jpg')
  if not p.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(a.parent/'sources'/fn),'-frames:v','1','-q:v','2',str(p)],check=True)
  if key=='mario' and slug=='limited-color-world':
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(p),'-vf','hue=s=0','-frames:v','1','-q:v','2',str(a/'mario-gray.jpg')],check=True)
 print(slug,[(p.name,p.stat().st_size) for p in a.iterdir()])
