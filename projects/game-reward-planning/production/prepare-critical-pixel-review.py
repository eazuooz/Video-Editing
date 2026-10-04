from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parents[3];DEST=Path(__file__).resolve().parent/'final-v1/pixel-review-v1'
d=json.loads((DEST/'index.json').read_text(encoding='utf8')); rows=[]
for name in ['branding','explanation-01','ammo-08','ammo-04','ammo-10','potion-state-study','coop-fit-combat-01','ranch-02-pet-milk','ranch-03','ranch-05','appearance-01','appearance-03','explanation-03','explanation-05','explanation-07','explanation-09','explanation-11','explanation-13']:
 choices=[r for r in d['rows'] if r.get('cut')==name];assert choices,name
 candidates=[r for r in choices if r['kind']=='caption-intersection'] or choices
 r=candidates[min(len(candidates)-1,round((len(candidates)-1)*.72))];rows.append(r)
pages=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
for off in range(0,len(rows),6):
 page=Image.new('RGB',(1920,1740),'#eee');draw=ImageDraw.Draw(page)
 for k,r in enumerate(rows[off:off+6]):
  x=k%2*960;y=k//2*580;page.paste(Image.open(ROOT/r['image']).resize((960,540)),(x,y));draw.text((x+3,y+545),f"{r['cut']} f{r['frame']} cue{r.get('cue','-')}",fill='black',font=font)
 f=DEST/f'critical-page-{len(pages)+1:02d}.jpg';page.save(f,quality=97);pages.append(f.relative_to(ROOT).as_posix())
(DEST/'critical-index.json').write_text(json.dumps({'rows':rows,'pages':pages,'directlyRead':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
