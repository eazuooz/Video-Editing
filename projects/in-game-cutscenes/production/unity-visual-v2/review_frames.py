"""Prepare evidence sheets at real375px and1080p for D27/D28 visual changes.

Extracts only changed explanation cuts and their adjacent joins. This does not
claim that generated sheets were looked at. Reviewed frames are recorded by the
agent separately after actual pixel inspection.
"""
from pathlib import Path
import argparse,json,subprocess
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[4]
MEDIA=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
SLUGS=('in-game-cutscenes','start-with-climax')
def read(p):return json.loads(p.read_text('utf-8-sig'))

def sheets(paths,out,prefix,width=375):
 h=round(width*1080/1920);cols=3;rows=3;limit=cols*rows
 for offset in range(0,len(paths),limit):
  group=paths[offset:offset+limit];im=Image.new('RGB',(cols*width,(h+28)*((len(group)+cols-1)//cols)),'#080808');draw=ImageDraw.Draw(im)
  for n,(path,label) in enumerate(group):
   x=n%cols*width;y=n//cols*(h+28)
   with Image.open(path) as original:im.paste(original.convert('RGB').resize((width,h),Image.Resampling.LANCZOS),(x,y))
   draw.text((x+5,y+h+4),label,fill='white')
  im.save(out/f'{prefix}-{offset//limit:02d}.jpg',quality=95)

def preflight(slug,version):
 base=MEDIA/slug/'preflight'/version;out=base/'review';out.mkdir(exist_ok=True)
 paths=[];cuts=[]
 for cut in sorted(base.glob('cut*')):
  if not(cut/'preflight-success.json').exists():continue
  current=[]
  for frame in sorted(cut.glob('frame-*.png')):
   p=(frame,cut.name+' '+frame.stem);paths.append(p);current.append(p)
  sheets(current,out,cut.name,375);cuts.append({'cut':cut.name,'frames':[str(p[0]) for p in current]})
 (out/'index.json').write_text(json.dumps({'scope':'Generated preflight sheets; direct viewing is recorded separately.','slug':slug,'cuts':cuts},ensure_ascii=False,indent=2)+'\n','utf-8')

def final(slug):
 plan=read(ROOT/'projects'/slug/'production/unity-visual-v2/plan.json');edit=MEDIA/slug/plan.get('mediaEditDirectory','edit');movie=edit/f'{slug}.captioned.mp4';out=edit/'review';out.mkdir(exist_ok=True)
 frames=set();labels={}
 for c in plan['cuts']:
  starts=c['globalStartFrame'];length=c['frames']
  samples={0, min(30,length-1),length//5,length*2//5,length*3//5,length*4//5,length-1}
  samples.update(min(length-1,max(0,round(t*60))) for t in c['speechCuesSeconds'])
  samples.update(min(length-1,max(0,round(t*60))) for t in c.get('motionCuesSeconds',[]))
  for f in samples:frames.add(starts+f);labels[starts+f]=c['id']+' local '+str(f)
  for f in (starts-1,c['globalEndFrame']):frames.add(f);labels[f]='join '+c['id']+' '+str(f)
 def balanced(terms):
  if len(terms)==1:return terms[0]
  middle=len(terms)//2
  return '('+balanced(terms[:middle])+'+'+balanced(terms[middle:])+')'
 expr=balanced([f'eq(n,{f})' for f in sorted(frames)])
 args=['ffmpeg','-hide_banner','-v','error','-n','-threads','2','-i',str(movie),'-vf',"select='"+expr+"'",'-fps_mode','passthrough',str(out/'frame-%04d.png')]
 subprocess.run(args,check=True,cwd=ROOT)
 paths=[];records=[]
 for n,f in enumerate(sorted(frames),1):
  path=out/f'frame-{n:04d}.png';assert path.exists();paths.append((path,labels[f]));records.append({'globalFrame':f,'seconds':f/60,'file':str(path),'label':labels[f]})
 sheets(paths,out,'final-375',375)
 (out/'index.json').write_text(json.dumps({'slug':slug,'movie':str(movie),'generatedFrames':records,'allFramesDirectlyViewed':False,'fullPlaybackClaimed':False},ensure_ascii=False,indent=2)+'\n','utf-8')

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('stage',choices=['preflight','final']);a.add_argument('slug',choices=SLUGS);a.add_argument('--version',default='v3');args=a.parse_args()
 if args.stage=='preflight':preflight(args.slug,args.version)
 else:final(args.slug)
