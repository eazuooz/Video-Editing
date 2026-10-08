"""Generate current final game-subject, quiet-seam and source-boundary pixels.

Generation does not approve the footage; review the sheets directly afterward.
"""
from pathlib import Path
import hashlib,json,math,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
from production_control import require_current_authorization

R=Path(__file__).resolve().parents[3]; slug=sys.argv[1]
require_current_authorization(slug,'final game observation inspection')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=R/f'projects/{slug}/production'; Q=R/f'shared/output/{slug}/qa'
t=read(P/'timeline.json'); qa=read(P/'qa.json')
v=R/qa['videos']['videoBurnedCaptions']['path']
assert qa['fullDecodePassed'] and sha(v)==qa['videos']['videoBurnedCaptions']['sha256']
times=[]
for s in t['scenes']:
 if s['classification']!='actual':continue
 assert s['observationReview']['rawSamplesPreserved'] and s['observationReview']['maximumPauseSeconds']<=6
 for i,start in enumerate(s['lineStarts']):
  end=s['lineStarts'][i+1] if i+1<len(s['lineStarts']) else s['seconds']-.6
  times.append(dict(scene=s['id'],time=s['start']+start+min(1.5,max(.08,(end-start)*.6)),kind='narrated subject',line=i+1))
 accumulated=0
 for p in s['observationPauses']:
  times.append(dict(scene=s['id'],time=s['start']+p['rawAt']+accumulated+p['seconds']/2,kind='quiet observation seam',afterLine=p['afterLine']))
  accumulated+=p['seconds']
 for cut in s['cuts']:
  for offset,label in [(.15,'source start'),(max(.15,cut['durationSeconds']-.15),'source end')]:
   times.append(dict(scene=s['id'],time=cut['outputStart']+offset,kind=label,sourceTime=cut['sourceIn']+offset))
times.sort(key=lambda x:x['time'])
assert all(2<=x['time']<t['seconds']-10 for x in times)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18); sheets=[]
for page in range(math.ceil(len(times)/4)):
 group=times[page*4:(page+1)*4]; sheet=Image.new('RGB',(1920,1160),'#e9edf0'); draw=ImageDraw.Draw(sheet)
 for j,x in enumerate(group):
  frame=Q/f'observation-{page*4+j+1:03}.jpg'
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(x['time']),'-threads','4','-i',str(v),'-frames:v','1','-vf','scale=960:540','-threads','4',str(frame)],check=True)
  left=(j%2)*960; top=(j//2)*580
  draw.text((left+8,top+6),f"{x['scene']} / {x['kind']} / {x['time']:.2f}s",fill='black',font=font)
  sheet.paste(Image.open(frame),(left,top+30))
 path=Q/f'observation-sheet-{page+1:02}.jpg';sheet.save(path,quality=95)
 sheets.append(dict(path=path.relative_to(R).as_posix(),sha256=sha(path)))
proof=dict(status='generated-pending-direct-view',videoSha256=sha(v),samples=times,sheets=sheets,scenes=[dict(scene=s['id'],observationReview=s['observationReview'],cuts=s['cuts']) for s in t['scenes'] if s['classification']=='actual'])
(Q/'observation-samples.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Generated',len(times),'current encoded game-subject/seam/boundary samples on',len(sheets),'sheets; direct review pending.')
