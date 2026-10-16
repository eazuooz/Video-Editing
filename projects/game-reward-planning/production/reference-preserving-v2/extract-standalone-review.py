"""Changed caption cues and their neighboring boundaries, at native/mobile scale."""
from pathlib import Path
import subprocess,json,math
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];O=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit/standalone-v3';Q=O/'qa';Q.mkdir(exist_ok=True)
rows=json.loads((O/'caption-tracks.json').read_text(encoding='utf8'));patches=json.loads((O/'patch-evidence.json').read_text(encoding='utf8'))['patches'];keys={(x['scene'],x['line']) for x in patches};indexes=[i for i,r in enumerate(rows) if (r['scene'],r['line']) in keys];points=[]
for i in indexes:
 r=rows[i];points.append({'type':'changed-cue','cue':i+1,'time':(r['start']+r['end'])/2,'text':r['ko']})
for x in patches:
 selected=[r for r in rows if r['scene']==x['scene'] and r['line']==x['line']]
 for label,t in [('before',selected[0]['start']-.05),('after',selected[-1]['end']+.05)]:points.append({'type':label,'scene':x['scene'],'time':t})
for i,p in enumerate(points):
 dst=Q/f'{i:02}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(p['time']),'-i',str(O/'game-reward-planning-v2-captioned.mp4'),'-frames:v','1',str(dst)],check=True);p['frame']=dst.relative_to(R).as_posix()
for page in range(math.ceil(len(points)/6)):
 group=points[page*6:(page+1)*6];sheet=Image.new('RGB',(1920,3*590),(235,235,235));draw=ImageDraw.Draw(sheet)
 for n,p in enumerate(group):
  im=Image.open(R/p['frame']);im.thumbnail((960,540));x=n%2*960;y=n//2*590;sheet.paste(im,(x,y));draw.text((x+10,y+545),f"{page*6+n:02}  {p['type']}  t={p['time']:.3f}",fill='black')
 sheet.save(Q/f'contact-{page:02}.jpg',quality=92)
mobile=Image.new('RGB',(375*len(indexes),240),(220,220,220))
for n,p in enumerate(points[:len(indexes)]):
 im=Image.open(R/p['frame']).resize((375,211),Image.Resampling.LANCZOS);mobile.paste(im,(375*n,0));ImageDraw.Draw(mobile).text((375*n+5,215),f"cue {p['cue']}",fill='black')
mobile.save(Q/'mobile.jpg',quality=94)
(O/'changed-caption-review.json').write_text(json.dumps({'changedCues':[i+1 for i in indexes],'samples':points,'unchangedLayoutEvidence':'../caption-layout.json and prior ledger; same font/ASS renderer/clean video stream/retained timing','directPixelReview':'pending','humanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(len(points),'review samples prepared')
