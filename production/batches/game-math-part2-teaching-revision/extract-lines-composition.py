"""One composition sample per scene, complementing every-cue/motion reviews."""
from pathlib import Path
import sys,json,hashlib,subprocess,concurrent.futures,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1];assert slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']
P=ROOT/'projects'/slug;m=json.loads((P/'project.json').read_text(encoding='utf8'));t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'));src=ROOT/m['paths']['videoBurnedCaptions'];D=ROOT/'shared/output'/slug/'composition-review';D.mkdir(parents=True,exist_ok=True)
rows=[('intro',.8),*[(s['id'],s['start']+s['seconds']*.55) for s in t['scenes']],('outro',t['seconds']-5)]
def extract(item):
 i,(ident,at)=item;path=D/f'{i+1:02}-{ident}.jpg'
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-ss',str(at),'-i',str(src),'-frames:v','1','-vf','scale=960:540','-q:v','2',str(path)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 return {'scene':ident,'finalTime':at,'file':path.name}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(extract,enumerate(rows)))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);sheets=[]
for page in range(math.ceil(len(records)/4)):
 sheet=Image.new('RGB',(1920,1120),'white');draw=ImageDraw.Draw(sheet)
 for j,row in enumerate(records[page*4:page*4+4]):
  x=j%2*960;y=j//2*560;sheet.paste(Image.open(D/row['file']),(x,y+20));draw.text((x+5,y),f'{row["scene"]} final{row["finalTime"]:.3f}',font=font,fill='black')
 name=f'composition-sheet-{page+1:02}.jpg';sheet.save(D/name,quality=95);sheets.append(name)
(D/'index.json').write_text(json.dumps({'source':m['paths']['videoBurnedCaptions'],'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'records':records,'sheets':sheets,'directReviewPassed':False,'imagesLocalOnly':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Current composition samples:',len(records))
