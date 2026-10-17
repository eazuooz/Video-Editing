"""Reproducible stills from the already rights-reviewed independent FHD recordings."""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[4]; V=Path(__file__).parent
L=R/'projects/avoid-game-comparisons/production/local/reference-preserving-v2'
O=L/'screenshots-v1/assets';O.mkdir(parents=True,exist_ok=True)
specs=[('side-jump','nes-gameplay-project',172.2),('flag','nes-gameplay-project',195.4),('frog','odyssey-switch2-360-440',23.4),('capture','odyssey-switch2-555-705',94.2),('pull','odyssey-switch2-555-705',96.0),('break','odyssey-switch2-555-705',97.7),('moon','odyssey-switch2-555-705',99.5),('collected','odyssey-switch2-555-705',108.0)]
records=[];hashes={}
for ident,source,sec in specs:
 p=L/(source+'.mp4');out=O/(ident+'.png')
 if source not in hashes:hashes[source]=hashlib.sha256(p.read_bytes()).hexdigest()
 if not out.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(sec),'-i',str(p),'-frames:v','1','-update','1',str(out)],check=True)
 with Image.open(out) as im:assert im.size==(1920,1080)
 nes=source.startswith('nes')
 records.append({'id':ident,'sourceFile':p.relative_to(R).as_posix(),'sourceSha256':hashes[source],'sourceTimeSeconds':sec,'sourceUrl':'https://www.youtube.com/watch?v='+('HGmyQS09VGQ' if nes else 'FJgSiI-Fols'),'credit':'Gameplay Project · CC BY' if nes else 'LongplayArchive / Spazbo4','output':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'size':[1920,1080],'sourceClassification':'independent-gameplay','screenRole':'explanation-still','crop':None,'aspectRatioPreserved':True})
(V/'screenshot-assets.json').write_text(json.dumps({'revision':'screenshots-v1','recipe':__file__,'rightsRecord':'projects/avoid-game-comparisons/planning/chapter-plan.json#currentRevision','records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sheet=Image.new('RGB',(1280,4*390),'#151515');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for i,r in enumerate(records):
 x=(i%2)*640;y=(i//2)*390
 with Image.open(R/r['output']) as im:sheet.paste(im.resize((640,360)),(x,y+30))
 d.text((x+8,y+2),f"{r['id']}  {r['sourceTimeSeconds']}s",font=font,fill='white')
sheet.save(O/'contact.jpg');print(O/'contact.jpg')
