"""Resume pixel sampling after completed cached decode/PTS/audio checks."""
from pathlib import Path
import subprocess,json,math
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent;O=R/'projects/avoid-game-comparisons/production/local/reference-preserving-v2/edit';Q=O/'qa'
plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));layout=json.loads((O/'caption-layout.json').read_text(encoding='utf8'));rows=json.loads((Q/'pixel-sample-index.json').read_text(encoding='utf8'))
for f,label in [(60,'original branding'),(plan['totalFrames']-300,'original membership identities')]:
 if not any(r['frame']==f for r in rows):rows.append({'frame':f,'time':f/60,'labels':[label]})
rows.sort(key=lambda r:r['frame']);(Q/'pixel-sample-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def balanced(terms):
 if len(terms)==1:return terms[0]
 mid=len(terms)//2;return '('+balanced(terms[:mid])+'+'+balanced(terms[mid:])+')'
selection=balanced(['eq(n,'+str(r['frame'])+')' for r in rows]);vf="select='"+selection+"',scale=480:270:flags=lanczos"
with (Q/'pixel-extract.log').open('w',encoding='utf8') as f:r=subprocess.run(['ffmpeg','-v','error','-i',str(O/'avoid-game-comparisons-v2-captioned.mp4'),'-an','-vf',vf,'-fps_mode','vfr','-c:v','mjpeg','-threads','1','-q:v','3','-y',str(Q/'frame-%04d.jpg')],cwd=R,stdout=f,stderr=subprocess.STDOUT)
if r.returncode:raise RuntimeError((Q/'pixel-extract.log').read_text(encoding='utf8',errors='replace'))
for page in range(math.ceil(len(rows)/12)):
 chunk=rows[page*12:(page+1)*12];sheet=Image.new('RGB',(1440,310*math.ceil(len(chunk)/3)),(22,22,22));draw=ImageDraw.Draw(sheet)
 for k,row in enumerate(chunk):
  im=Image.open(Q/f'frame-{page*12+k+1:04}.jpg');x=k%3*480;y=k//3*310;sheet.paste(im,(x,y));draw.text((x+5,y+274),f"{row['time']:.2f}s | "+' / '.join(row['labels'])[:65],fill='white')
 sheet.save(Q/f'contact-{page:02}.jpg')
results=[json.loads((Q/(kind+'-integrity.json')).read_text()) for kind in ['clean','captioned']];actual=sum(c['frames'] for c in plan['cuts'] if c['kind']=='independent-gameplay')
report={'outputs':results,'bodyFrames':plan['bodyFrames'],'actualFrames':actual,'explanationFrames':plan['bodyFrames']-actual,'ratioRoundingErrorFrames':actual-plan['bodyFrames']*.6,'noSourceLoopsOrSpeedChanges':all(c.get('playbackSpeed',1)==1 and not c.get('loop') for c in plan['cuts']),'captionPairs':len(layout['rows']),'pixelSamples':len(rows),'contactSheets':math.ceil(len(rows)/12),'actualPixelsReview':'pending direct review','fullAsrReview':'complete; direct text comparison done, ambiguous spelling contexts pending','humanWholeListening':'pending','platformMutation':False}
(Q/'integrity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='outputs'}))
