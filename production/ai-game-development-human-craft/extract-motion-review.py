"""Decode current encoded motion/contact evidence once, with exact frame mapping.

These pages are evidence for direct visual review, not automatic motion approval.
Caption pixels are checked independently for every cue and neighboring boundary.
"""
from pathlib import Path
import json, hashlib, subprocess, math, sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
OUT=ROOT/f'shared/output/{SLUG}/encoded-motion-review';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def select_expr(indices):
 if len(indices)==1:return f'eq(round(t*60),{indices[0]})'
 mid=len(indices)//2
 return '('+select_expr(indices[:mid])+'+'+select_expr(indices[mid:])+')'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
 return h.hexdigest()
m=read(ROOT/f'projects/{SLUG}/project.json');data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json')
actual=read(ROOT/f'projects/{SLUG}/planning/actual-footage-plan.json')
movie=ROOT/m['paths']['videoBurnedCaptions'];movie_sha=sha(movie);mapping=[]
for s in data['scenes']:
 sid=s['id'];count=round(s['duration']*60);times={0,(count-1)/60}
 for p in s['paragraphs']:times.add(min(s['duration']-1/60,p['start']+.6))
 for c in actual['cuts']:
  if c['scene']==sid:times.update([max(0,(c['startFrame']-1)/60),c['startFrame']/60,(c['startFrame']+c['endFrame'])/120,(c['endFrame']-1)/60,min(s['duration']-1/60,c['endFrame']/60)])
 if s['mode'] in ['flow','branch','cycle']:
  duration=8;n=len(s['labels'])
  for edge in range(1,n):
   for fraction in [.08,.5,.92]:times.add((edge-1+fraction)*duration/n)
 if s['mode']=='compare':times.update([2,3,4,5,6,10,11,12,13])
 if sid=='02':times.update(s['paragraphs'][2]['start']+v for v in [0,1.98,2.02,6.98,7.02,10.98,11.02,12])
 if sid in ['04','10']:
  a=0 if sid=='04' else s['paragraphs'][1]['start'];times.update([a+.2,a+7.8,a+8.1])
 if sid=='09':
  a=max(0,s['paragraphs'][5]['end']-20.5);times.update(a+v for v in [0,3.7,4,9.8,10.1,13.7,14,16,19.8])
 if sid=='17':
  for p in [2,3,5,6]:times.update(s['paragraphs'][p]['start']+v for v in [0,4.3,4.5,6])
  times.update([s['paragraphs'][2]['start']-2/60,s['paragraphs'][3]['start']+12+2/60])
 if sid=='18':times.update([0,4.3,4.5,5.8,6,6.95,7.05,11.3,11.5,12.8,13,13.95,14.5])
 if sid=='20':times.update(s['paragraphs'][4]['start']+v for v in [0,2.98,3.02,3.15,3.28,3.32,3.6,4,5])
 if sid=='23':times.update(s['paragraphs'][1]['start']+v for v in [0,6.9,7.1,8,13.8])
 if sid=='26':times.update(s['paragraphs'][1]['start']+v for v in [0,.9,1.5,3,4.9,5.1,7])
 for f in sorted({max(0,min(count-1,round(t*60))) for t in times}):mapping.append({'scene':sid,'localFrame':f,'frame':120+round(s['start']*60)+f})
total=120+sum(round(s['duration']*60) for s in data['scenes'])+600
mapping=[{'scene':'intro','localFrame':f,'frame':f} for f in [0,60,119]]+mapping+[{'scene':'members','localFrame':f,'frame':total-600+f} for f in [0,300,599]]
mapping.sort(key=lambda x:x['frame']);stamp={'sourceSha256':movie_sha,'mapping':mapping,'size':[640,360]}
receipt=OUT/'input.json';frames=OUT/'frames';frames.mkdir(exist_ok=True)
reviewFile=OUT/'review.json'
if receipt.exists() and read(receipt)==stamp and reviewFile.exists():
 previous=read(reviewFile)
 if (previous['movieSha256']==movie_sha and previous['frames']==len(mapping)
     and all((ROOT/p['path']).exists() for p in previous['pages'])):
  print('Reusing identical current motion evidence and its scoped review status.')
  sys.exit(0)
if receipt.exists():assert read(receipt)==stamp,'Changed output requires explicit new evidence version'
else:
 assert not list(frames.glob('*.png')),'Interrupted extraction must be inspected'
 vf=OUT/'filter.txt';vf.write_text("select='"+select_expr([r['frame'] for r in mapping])+"',scale=640:360",encoding='ascii')
 subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-/filter:v',str(vf),'-fps_mode','passthrough','-compression_level','2',str(frames/'%06d.png')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 assert len(list(frames.glob('*.png')))==len(mapping)
 receipt.write_text(json.dumps(stamp,indent=2)+'\n',encoding='utf-8')
for i,row in enumerate(mapping):row['image']=str((frames/f'{i+1:06d}.png').relative_to(ROOT)).replace('\\','/')
pages=[]
for sid in dict.fromkeys(r['scene'] for r in mapping):
 rows=[r for r in mapping if r['scene']==sid]
 for page in range(math.ceil(len(rows)/12)):
  subset=rows[page*12:(page+1)*12];canvas=Image.new('RGB',(1920,392*math.ceil(len(subset)/3)),'#242424');draw=ImageDraw.Draw(canvas)
  for i,row in enumerate(subset):
   x=(i%3)*640;y=(i//3)*392;canvas.paste(Image.open(ROOT/row['image']).convert('RGB'),(x,y));draw.text((x+10,y+365),f"Scene {sid} | local f{row['localFrame']} | final {row['frame']/60:.3f}s",fill='white')
  dest=OUT/f'{sid}-{page+1}.jpg';canvas.save(dest,quality=90);pages.append({'scene':sid,'page':page+1,'path':str(dest.relative_to(ROOT)).replace('\\','/'),'review':'pending'})
(OUT/'review.json').write_text(json.dumps({'movieSha256':movie_sha,'status':'pending-direct-visual-review','frames':len(mapping),'pages':pages},indent=2)+'\n')
print(json.dumps({'frames':len(mapping),'pages':len(pages),'review':'pending'}))
