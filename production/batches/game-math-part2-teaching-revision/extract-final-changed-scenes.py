"""Bounded final-pixel review after a selective scene edit; never approves it."""
from pathlib import Path
import argparse,json,hashlib,subprocess,concurrent.futures,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
a=argparse.ArgumentParser();a.add_argument('slug');a.add_argument('--scenes',required=True);args=a.parse_args()
P=ROOT/'projects'/args.slug;m=json.loads((P/'project.json').read_text(encoding='utf8'));t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'))
src=ROOT/m['paths']['videoBurnedCaptions'];digest=hashlib.file_digest(src.open('rb'),'sha256').hexdigest()
D=ROOT/'shared/output'/args.slug/'changed-final-pixel-review'/digest[:16];D.mkdir(parents=True,exist_ok=True)
ids=set(args.scenes.split(','));chosen=[s for s in t['scenes'] if s['id'] in ids];assert len(chosen)==len(ids)
jobs=[]
for s in chosen:
 for n,fraction in enumerate([.3,.6,.9],1):jobs.append({'kind':'motion','scene':s['id'],'time':s['start']+s['seconds']*fraction,'file':D/f'{s["id"]}-motion-{n}.jpg'})
for n,c in enumerate(t['koCaptions'],1):
 if c['scene'] in ids:jobs.append({'kind':'cue','scene':c['scene'],'cue':n,'time':(c['start']+c['end'])/2,'file':D/f'cue-{n:03}.jpg'})
def extract(j):
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-ss',str(j['time']),'-i',str(src),'-frames:v','1','-q:v','2',str(j['file'])],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(extract,jobs))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
for kind,page_count,height in [('motion',6,560),('cue',24,130)]:
 data=[j for j in jobs if j['kind']==kind]
 for start in range(0,len(data),page_count):
  portion=data[start:start+page_count];sheet=Image.new('RGB',(1920,math.ceil(len(portion)/2)*height),'#e9ecee');draw=ImageDraw.Draw(sheet)
  for k,j in enumerate(portion):
   im=Image.open(j['file']);x=k%2*960;y=k//2*height
   if kind=='cue':im=im.crop((0,880,1920,1080)).resize((960,100));offset=25
   else:im=im.resize((960,540));offset=20
   sheet.paste(im,(x,y+offset));draw.text((x+8,y),f'{j["scene"]} {kind} {j.get("cue","")} | final {j["time"]:.3f}s',font=font,fill='#202020')
  sheet.save(D/f'{kind}-sheet-{start//page_count+1:02}.jpg',quality=95)
record={'slug':args.slug,'source':m['paths']['videoBurnedCaptions'],'sha256':digest,'scenes':[s['id'] for s in chosen],'motionSamples':sum(j['kind']=='motion' for j in jobs),'cueSamples':sum(j['kind']=='cue' for j in jobs),'humanListening':'pending','pixelApproval':False,'imagesLocalOnly':True}
(D/'extraction.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(record),flush=True)
