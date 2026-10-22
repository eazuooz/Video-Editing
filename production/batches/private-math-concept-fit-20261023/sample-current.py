"""Sample current encoded gameplay for direct conceptual review; no auto approvals."""
from pathlib import Path
import collections, concurrent.futures, datetime, io, json, subprocess
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=R/'shared/output/private-math-concept-fit-20261023'
O.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d=read(B/'scene-audit.json');entries={e['id']:e for e in d['entries']}
def job(row):
 e=entries[row['episode']];p=R/'projects'/e['slug'];h=p/'production/private-polish-v1'
 rec=read(h/'gameplay-restoration.json').get('scenes',{}).get(row['scene']) if (h/'gameplay-restoration.json').exists() else None
 if rec:
  row['currentParts']=[dict(source=x['source'],sourceIn=x['sourceIn'],seconds=x['frames']/60,exists=(R/x['source']).exists()) for x in rec['sources']]
 else:row['currentParts']=row['parts']
 master=R/'output'/(e['slug']+'-private-polish')/(e['slug']+'.captioned.mp4')
 if not master.exists():row['sampleStatus']='original-master-not-local';return row
 folder=O/'current-samples'/e['id'];folder.mkdir(parents=True,exist_ok=True)
 paths=[]
 for n,fraction in enumerate([.08,.33,.66,.92]):
  sec=row['start']+row['seconds']*fraction;dst=folder/f'{row["scene"]}-{n}.jpg'
  if not dst.exists():
   subprocess.run(['ffmpeg','-v','error','-ss',str(sec),'-i',str(master),'-vf','scale=640:360','-frames:v','1','-q:v','3','-y',str(dst)],check=True,capture_output=True)
  paths.append(dict(path=dst.relative_to(R).as_posix(),masterSeconds=sec,localSeconds=row['seconds']*fraction))
 row['samples']=paths;row['sampledMaster']=master.relative_to(R).as_posix();row['sampleStatus']='sampled-not-reviewed';return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 rows=list(pool.map(job,d['scenes']))
d['scenes']=rows
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
sheets=[]
for e in entries.values():
 items=[(r,x) for r in rows if r['episode']==e['id'] for x in r.get('samples',[])]
 for idx in range(0,len(items),12):
  group=items[idx:idx+12];im=Image.new('RGB',(1920,1560),'#121512');draw=ImageDraw.Draw(im)
  for j,(row,x) in enumerate(group):
   left=(j%3)*640;top=(j//3)*390;im.paste(Image.open(R/x['path']),(left,top+30));draw.text((left+6,top+4),f'{e["id"]}/{row["scene"]} +{x["localSeconds"]:.1f}s  {row["title"][:30]}',font=font,fill='white')
  dest=O/f'current-{e["id"]}-{idx//12+1:02}.jpg';im.save(dest,quality=88)
  sheets.append(dict(episode=e['id'],path=dest.relative_to(R).as_posix(),items=[dict(scene=r['scene'],**x) for r,x in group]))
d['currentSampleSheets']=sheets;save(B/'scene-audit.json',d)
print(json.dumps(dict(status='sampled-not-reviewed',sceneCount=len(rows),samples=sum(len(r.get('samples',[])) for r in rows),sheets=len(sheets),missing=[r['episode']+'/'+r['scene'] for r in rows if r['sampleStatus']=='original-master-not-local']),ensure_ascii=False))
