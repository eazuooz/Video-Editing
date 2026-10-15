"""Generate frame-aligned editable ASS vector strokes, labels and review frames."""
from probe import *
import math, hashlib, subprocess, shutil
import numpy as np

STYLE=rd(R/'shared/publishing/footage-annotation-style.json')
def color(hex):
 h=hex.lstrip('#');return '&H'+h[4:6]+h[2:4]+h[:2]+'&'
def timecode(frame):
 # Floor ASS centiseconds so each 60fps frame is inside its own event interval.
 cs=frame*100//60;return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
def coords(w,f):
 keys=w['keyframes'];j=0
 while j+1<len(keys) and keys[j+1]['frame']<=f:j+=1
 a=keys[j];b=keys[min(j+1,len(keys)-1)];t=max(0,min(1,(f-a['frame'])/max(1,b['frame']-a['frame'])))
 return (np.array(a['points'])*(1-t)+np.array(b['points'])*t)*4
def points(w,f):
 p=coords(w,f)
 if w['shape']=='contour':return p.tolist()
 (x,y),(x2,y2)=p
 if w['shape']=='rectangle':return [[x,y],[x2,y],[x2,y2],[x,y2],[x,y]]
 return [[(x+x2)/2+(x2-x)/2*math.cos(a),(y+y2)/2+(y2-y)/2*math.sin(a)] for a in np.linspace(0,2*math.pi,65)]
def trace(p,progress):
 lengths=[math.dist(a,b) for a,b in zip(p,p[1:])];remain=sum(lengths)*progress;out=[p[0]]
 for a,b,length in zip(p,p[1:],lengths):
  if remain>=length:out.append(b);remain-=length
  elif length:out.append([a[0]+(b[0]-a[0])*remain/length,a[1]+(b[1]-a[1])*remain/length]);break
 return out
def polygon(p):return 'm '+' '.join(f'{x:.1f} {y:.1f}' if i==0 else f'l {x:.1f} {y:.1f}' for i,(x,y) in enumerate(p))+' '
def stroke(p,width):
 # One continuous outline avoids even-odd holes from overlapping ASS subpaths.
 p=np.asarray(p,dtype=float);closed=len(p)>2 and np.linalg.norm(p[0]-p[-1])<.01
 if closed:p=p[:-1]
 if len(p)<2:return ''
 r=width/2;left=[];right=[];angles=[]
 for i,a in enumerate(p):
  prev=p[(i-1)%len(p)] if closed or i else a-(p[1]-a)
  nxt=p[(i+1)%len(p)] if closed or i<len(p)-1 else a+(a-p[i-1])
  v=a-prev;v/=max(np.linalg.norm(v),.001);u=nxt-a;u/=max(np.linalg.norm(u),.001)
  n1=np.array([-v[1],v[0]]);n2=np.array([-u[1],u[0]])
  n=n1+n2;n/=max(np.linalg.norm(n),.001);off=n*min(2*r,r/max(.5,np.dot(n,n2)))
  left.append((a+off).tolist());right.append((a-off).tolist());angles.append(math.atan2(u[1],u[0]))
 if closed:return polygon(left)+polygon(right[::-1])
 end=p[-1];start=p[0];a=angles[-1];b=angles[0]
 capend=[[end[0]+r*math.cos(t),end[1]+r*math.sin(t)] for t in np.linspace(a+math.pi/2,a-math.pi/2,9)]
 capstart=[[start[0]+r*math.cos(t),start[1]+r*math.sin(t)] for t in np.linspace(b-math.pi/2,b-3*math.pi/2,9)]
 return polygon(left+capend+right[::-1]+capstart)
def label(w):return w['label'].replace('\n','\\N')
def build():
 d=rd(H/'annotations.json');caps=rd(B/'captions.json')['cues']['ko'];nodes=rd(B/'plan.json')['nodes'];style=STYLE
 lines=['[Script Info]','ScriptType: v4.00+','PlayResX: 1920','PlayResY: 1080','ScaledBorderAndShadow: yes','[V4+ Styles]',
 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
 'Style: Guide,Malgun Gothic,52,&H00F5F5F5,&H00F5F5F5,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1',
 '[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
 font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',52)
 for w in d['windows']:
  if w['status']=='omitted':continue
  a,b=w['startFrame'],w['endFrame']; assert b>a
  ns=[n for n in nodes if n['endFrame']>a and n['startFrame']<b];assert all(n['role']=='actual' for n in ns)
  w['nodes']=[n['id'] for n in ns];w['narrationCues']=[dict(index=c['index'],key=c['key'],start=c['startSeconds'],end=c['endSeconds'],text=c['text']) for c in caps if c['endSeconds']*60>a and c['startSeconds']*60<b]
  w['sourceRanges']=[dict(node=n['id'],source=n['path'],sourceStartFrame=n['sourceStartFrame']+max(a-n['startFrame'],0),frames=min(b,n['endFrame'])-max(a,n['startFrame'])) for n in ns]
  x,y=[v*4 for v in w['labelAt']];tw=font.getlength(w['label']);assert x+tw+28<1920,(w['id'],x,tw)
  assert y+70<880
  def event(layer,start,end,text):lines.append(f'Dialogue: {layer},{timecode(start)},{timecode(end)},Guide,{w["id"]},0,0,0,,{text}')
  col=color(style['colors'][w['colorRole']]);start=timecode(a);end=timecode(b)
  bg=polygon([[x-12,y-7],[x+tw+14,y-7],[x+tw+14,y+65],[x-12,y+65]])
  event(2,a,b,r'{\an7\pos(0,0)\p1\bord0\shad0\1c&H000000&\fad(100,90)}'+bg)
  event(3,a,b,fr'{{\an7\pos({x},{y})\bord0\shad0\1c{col}\fad(100,90)}}'+label(w))
  for f in range(a,b):
   p=trace(points(w,f),min(1,(f-a+1)/min(21,(b-a)/5)))
   assert all(0<=x<=1920 and 0<=y<880 for x,y in p),(w['id'],f,p)
   alpha=round(255*max(0,(f-(b-6))/6))
   for layer,width,c in [(0,style['contrastStrokePx'],'&H000000&'),(1,style['strokePx'],col)]:
    event(layer,f,f+1,fr'{{\an7\pos(0,0)\p1\bord0\shad0\1c{c}\alpha&H{alpha:02X}&}}'+stroke(p,width))
  w['captionClearance']='All strokes below y880 prohibited; fixed caption remains unchanged at960,970.'
 wr(H/'annotations.json',d);(O/'annotations.ass').write_text('\n'.join(lines)+'\n','utf-8-sig')
 print('Designed callouts',sum(w['status']!='omitted' for w in d['windows']),flush=True)
def samples():
 d=rd(H/'annotations.json');q=O/'preflight';q.mkdir(exist_ok=True)
 ass=(O/'annotations.ass').relative_to(R).as_posix();ff=shutil.which('ffmpeg')
 for w in d['windows']:
  if w['status']=='omitted':continue
  f=(w['startFrame']+w['endFrame'])//2
  out=q/(w['id']+'.png')
  cmd=[ff,'-v','error','-nostdin','-y','-ss',f'{f/60:.9f}','-i',str(B/'pair/captioned.mp4'),'-vf',f"settb=1/60,setpts=N+{f},ass='{ass}'",'-frames:v','1',str(out)]
  subprocess.run(cmd,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  print(w['id'],flush=True)
def boards():
 d=rd(H/'annotations.json');ws=[w for w in d['windows'] if w['status']!='omitted'];q=O/'preflight';font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
 for i in range(0,len(ws),6):
  board=Image.new('RGB',(1440,930),'#181818');dr=ImageDraw.Draw(board)
  for j,w in enumerate(ws[i:i+6]):
   im=Image.open(q/(w['id']+'.png'));x=(j%2)*720;y=(j//2)*310;board.paste(im.resize((540,304)),(x,y));mobile=im.resize((375,211));mobile.save(q/(w['id']+'-375.png'))
   dr.text((x+540,y+15),w['id'],font=font,fill='white')
  board.save(q/f'board-{i//6}.jpg',quality=94)
if __name__=='__main__':
 import sys
 if '--samples' in sys.argv:samples();boards()
 else:build()
