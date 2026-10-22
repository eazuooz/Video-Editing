"""Every final caption, scene/cut joins and repaired movement; never auto-pass."""
import sys,math
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();movie=e.D/f'{e.slug}.captioned.mp4';digest=sha(movie)
technical=read(e.H/'technical-qa.json');assert next(x for x in technical['outputs'] if x['kind']=='captioned')['sha256']==digest
out=e.O/'final-pixel-review';out.mkdir(exist_ok=True);points={}
replacement=read(e.H/'fhd-replacement-cuts.json') if (e.H/'fhd-replacement-cuts.json').exists() else None
if replacement:
 assert replacement['status']=='approved-source-cuts'
 assert replacement['originalTimelineSha256']==sha(e.P/'production/timeline.json')
def add(t,reason):
 t=round(min(e.T['seconds']-.02,max(.02,t))*60)/60;points.setdefault(t,[]).append(reason)
for i,cue in enumerate(e.T['koCaptions']):add((cue['start']+cue['end'])/2,f'caption-{i+1}')
for slot in e.T['scenes']:
 for offset in [-1/60,1/60,.25]:add(slot['start']+offset,'scene-join-'+slot['id'])
 for fraction in [.15,.5,.85]:add(slot['start']+slot['seconds']*fraction,'scene-state-'+slot['id'])
 boundary=slot['start']
 current_cut=replacement['scenes'].get(slot['id'],slot.get('cut',{})) if replacement else slot.get('cut',{})
 for segment in current_cut.get('segments',[])[:-1]:
  boundary+=segment['frames']/60
  for offset in [-1/60,1/60,.25]:add(boundary+offset,'source-cut-'+slot['id'])
 if slot['id']=='GA06':
  for k in range(min(66,math.floor(slot['seconds']/.2))):add(slot['start']+k*.2,'repaired-body-guide-GA06')
 if slot['id'] in ['QF20','QC20']:
  for k in range(15):add(slot['start']+.5+k*.4,'caption-ui-clearance-'+slot['id'])
if (e.H/'observed-guides.json').exists():
 for guide in read(e.H/'observed-guides.json')['guides']:
  slot=next(x for x in e.T['scenes'] if x['id']==guide['scene'])
  a,z=guide['keyframes'][0][0],guide['keyframes'][-1][0]
  for frame in range(round(a*60),round(z*60)+1,6):add(slot['start']+frame/60,'observed-guide-'+guide['scene'])
  for t in [a-1/60,z-1/60,z+1/60]:add(slot['start']+t,'guide-boundary-'+guide['scene'])
add(.5,'branding');add(e.T['seconds']-8,'membership');add(e.T['seconds']-.2,'ending')
if (e.H/'restored-polygon-guides.json').exists():
 for run in read(e.H/'restored-polygon-guides.json')['visibleIntervals']:
  slot=next(x for x in e.T['scenes'] if x['id']==run['scene'])
  for frame in range(round(run['start']*60),round(run['end']*60)+1,6):add(slot['start']+frame/60,'restored-polygon-guide-'+slot['id'])
  for t in [run['start']-1/60,run['end']+1/60]:add(slot['start']+t,'restored-guide-boundary-'+slot['id'])
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15);tiles=[];records=[]
for i,(t,reasons) in enumerate(sorted(points.items())):
 dst=out/f'{i:04d}.png';receipt=dst.with_suffix('.json');sig={'masterSha256':digest,'seconds':t,'reasons':reasons}
 if not(dst.exists() and receipt.exists() and read(receipt)==sig):
  e.ff(['-ss',t,'-i',movie,'-frames:v','1','-threads','1',dst],'final-pixel-sampling.log');save(receipt,sig)
 records.append({**sig,'image':rel(dst)})
 im=Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS);tile=Image.new('RGB',(375,240),'#222222');tile.paste(im,(0,29));ImageDraw.Draw(tile).text((5,3),f'{i:03d} {t:.2f}s {reasons[0]}',font=font,fill='white');tiles.append(tile)
 if i%100==0:print(e.id,i,'final encoded samples',flush=True)
for i in range(0,len(tiles),12):
 sheet=Image.new('RGB',(1500,720),'#222222')
 for j,tile in enumerate(tiles[i:i+12]):sheet.paste(tile,((j%4)*375,(j//4)*240))
 sheet.save(out/f'sheet-{i//12+1:03d}.jpg',quality=94)
save(e.H/'final-pixel-samples.json',{'status':'await-direct-inspection','captionedMasterSha256':digest,'samples':records,'sheets':math.ceil(len(tiles)/12),'captionCueCoverage':len(e.T['koCaptions']),'limitations':'Discrete current encoded pixels and dense repaired-motion samples; not a claim of every-frame human viewing or human listening.'})
print(e.id,len(records),'final-pixel samples generated; review pending',flush=True)
