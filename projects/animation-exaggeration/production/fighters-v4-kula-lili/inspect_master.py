"""Sample actual encoded pixels at each cut/cue, selected motion poses and mobile size."""
from pipeline import *
import av, numpy as np,soundfile as sf
from PIL import Image, ImageDraw, ImageFont
def extract():
 p=read(H/'edit-plan.json');cues=read(L/'edit/captions.json')['cues'];q=L/'qa/final';q.mkdir(parents=True,exist_ok=True)
 f=L/'edit/animation-exaggeration-captioned.mp4'
 groups={'cuts':[],'motion':[],'captions':[],'mobile':[]}; targets={}
 def mark(g,name,frame):targets.setdefault(int(frame),[]).append((g,name))
 for c in p['cuts']:
  mid=c['startFrame']+c['frames']//2;mark('cuts',c['id'],mid)
  if c.get('playbackSpeed')==.25 or c['id'] in ('A02-E015','A02-E011'):
   for j,r in enumerate((.06,.18,.32,.46,.59,.73,.87,.96)):mark('motion',c['id']+' '+str(j+1),c['startFrame']+int(c['frames']*r))
   for r in ((.15,.32,.65) if c['id']=='A02-E011' else (.32,.65)):mark('mobile',c['id']+' @'+str(r),c['startFrame']+int(c['frames']*r))
 for c in cues:mark('captions','cue '+str(c['cue']),round((c['start']+c['end'])*30))
 todo=set(targets);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
 with av.open(str(f)) as container:
  stream=container.streams.video[0];stream.thread_type='AUTO';stream.codec_context.thread_count=4
  for i,frame in enumerate(container.decode(stream)):
   if i not in todo:continue
   im=frame.to_image()
   for g,name in targets[i]:
    if g=='captions':pic=im.crop((115,880,1805,1080)).resize((590,70),Image.Resampling.LANCZOS)
    else:
     w=375 if g=='mobile' else (480 if g=='motion' else 405);pic=im.resize((w,round(w*9/16)),Image.Resampling.LANCZOS)
    groups[g].append((name+' / %.2fs'%(i/60),pic))
   todo.remove(i)
   if not todo:break
 assert not todo,todo
 for g,items in groups.items():
  cols=2 if g in ('captions','mobile') else 3;rows={'cuts':4,'motion':3,'captions':12,'mobile':5}[g];per=cols*rows
  for off in range(0,len(items),per):
   batch=items[off:off+per];w,h=batch[0][1].size;s=Image.new('RGB',(w*cols,(h+23)*((len(batch)+cols-1)//cols)),'#151515');draw=ImageDraw.Draw(s)
   for j,(name,im) in enumerate(batch):
    x=j%cols*w;y=j//cols*(h+23);s.paste(im,(x,y));draw.text((x+3,y+h+1),name,font=font,fill='white')
   s.save(q/f'{g}-{off//per+1:02d}.jpg',quality=90)
 save(q/'extraction.json',{'master':artifact(f),'actualEncodedSamples':{k:len(v) for k,v in groups.items()},'mobileWidth':375})
def retention():
 old,rate=sf.read(P/'production/local/grid-v1/edit/narration-stem.wav',dtype='float32',always_2d=True);v,rate2=sf.read(L/'edit/narration-stem.wav',dtype='float32',always_2d=True);assert rate==rate2==48000
 offset=0;prev=0;proof=[]
 for i in read(H/'narration-insert-map.json')['inserts']:
  z=i['originalAtFrame']*800;assert np.array_equal(old[prev:z],v[prev+offset:z+offset]);proof.append({'originalSamples':[prev,z],'newStart':prev+offset,'identical':True});prev=z;offset+=i['frames']*800
 assert np.array_equal(old[prev:],v[prev+offset:]);proof.append({'originalSamples':[prev,len(old)],'newStart':prev+offset,'identical':True})
 save(H/'original-voice-retention.json',{'sourceFourteenUntouched':True,'proof':proof,'actualHumanListening':False})
if __name__=='__main__':extract();retention()
