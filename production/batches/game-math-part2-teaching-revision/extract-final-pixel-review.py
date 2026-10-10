"""Extract every burned cue and composition from actual final pixels.

Local reproducible QA images stay outside Git. Extraction never grants approval.
"""
from pathlib import Path
import json,sys,subprocess,hashlib,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1];P=ROOT/'projects'/slug
m=json.loads((P/'project.json').read_text(encoding='utf8'))
t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'))
src=ROOT/m['paths']['videoBurnedCaptions'];D=ROOT/'shared/output'/slug/'final-pixel-review';D.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
jobs=[]
for i,c in enumerate(t['koCaptions'],1):
 jobs.append({'kind':'cue','index':i,'time':(c['start']+c['end'])/2,'scene':c['scene'],'file':D/f'cue-{i:03}.jpg'})
for i,(ident,time) in enumerate([('intro',.8),*[(s['id'],s['start']+s['seconds']*.55) for s in t['scenes']],('outro',t['seconds']-5)],1):
 jobs.append({'kind':'composition','index':i,'time':time,'scene':ident,'file':D/f'composition-{i:03}.jpg'})
def extract(j):
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-ss',str(j['time']),'-i',str(src),'-frames:v','1','-q:v','2',str(j['file'])],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 return j
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for n,j in enumerate(pool.map(extract,jobs),1):
  if n%40==0:print(f'Extracted {n}/{len(jobs)} actual final frames',flush=True)
for kind,size,page_count in [('cue',(1920,1560),24),('composition',(1920,1120),4)]:
 chosen=[j for j in jobs if j['kind']==kind]
 for start in range(0,len(chosen),page_count):
  page=Image.new('RGB',size,'#e9ecee');draw=ImageDraw.Draw(page)
  for k,j in enumerate(chosen[start:start+page_count]):
   im=Image.open(j['file']);x=(k%2)*960
   if kind=='cue':y=(k//2)*130;im=im.crop((0,880,1920,1080)).resize((960,100));offset=25
   else:y=(k//2)*560;im=im.resize((960,540));offset=20
   page.paste(im,(x,y+offset));draw.text((x+8,y),f'{kind} {j["index"]:03} | {j["time"]:.2f}s | {j["scene"]}',font=font,fill='#202020')
  page.save(D/f'{kind}-sheet-{start//page_count+1:02}.jpg',quality=95)
record={'source':m['paths']['videoBurnedCaptions'],'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'captionCueCount':len(t['koCaptions']),'compositionCount':sum(j['kind']=='composition' for j in jobs),'allCuePixelReview':False,'allCompositionReview':False,'movingReview':False,'humanListening':'pending','imagesLocalOnly':True}
(D/'extraction.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(record),flush=True)
