"""Native-speed FHD excerpts with source-verified editorial callouts.

All coordinates are explicit editorial keyframes; this is not detector output.
The clean master retains these instructional marks, but has no narration captions.
"""
from pathlib import Path
import json,hashlib,subprocess,math
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit';O.mkdir(exist_ok=True)
SCALE=5/6
def stamp(v):
 n=round(v*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
def bgr(c):return c[4:6]+c[2:4]+c[:2]
def ass_header():return '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Mark,Malgun Gothic,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,5,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def event(a,b,content,layer=1):return f'Dialogue: {layer},{stamp(a)},{stamp(b)},Mark,,0,0,0,,{content}\n'
def poly(points):return 'm '+' l '.join(f'{round(x)} {round(y)}' for x,y in points)+' c'
def ring(shape,x,y,w,h,thickness=8):
 if shape=='circle':
  points=lambda a,b:[(x+w/2+a*math.cos(i*math.pi/24),y+h/2+b*math.sin(i*math.pi/24)) for i in range(48)]
  return poly(points(w/2,h/2))+' '+poly(list(reversed(points(max(1,w/2-thickness),max(1,h/2-thickness)))))
 return poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)])+' '+poly([(x+thickness,y+thickness),(x+thickness,y+h-thickness),(x+w-thickness,y+h-thickness),(x+w-thickness,y+thickness)])
def interpolate(keys,t):
 for a,b in zip(keys,keys[1:]):
  if a[0]<=t<=b[0]:
   q=(t-a[0])/max(b[0]-a[0],1e-9);return [u+(v-u)*q for u,v in zip(a[1:],b[1:])]
 return keys[0][1:] if t<=keys[0][0] else keys[-1][1:]
def arrow_path(points,progress=1):
 lengths=[math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(points,points[1:])];remain=sum(lengths)*progress;shapes=[];last=None
 for a,b,length in zip(points,points[1:],lengths):
  if remain<=0:break
  part=min(1,remain/max(length,1e-6));end=(a[0]+(b[0]-a[0])*part,a[1]+(b[1]-a[1])*part);dx=(b[0]-a[0])/length;dy=(b[1]-a[1])/length;nx=-dy*5;ny=dx*5
  shapes.append(poly([(a[0]+nx,a[1]+ny),(end[0]+nx,end[1]+ny),(end[0]-nx,end[1]-ny),(a[0]-nx,a[1]-ny)]));last=(end,dx,dy);remain-=length
 if last:
  (x,y),dx,dy=last;shapes.append(poly([(x,y),(x-dx*26-dy*16,y-dy*26+dx*16),(x-dx*26+dy*16,y-dy*26-dx*16)]))
 return ' '.join(shapes)
def annotations(c):
 d=c['frames']/60;src=c['sourceStart'];ass=ass_header()
 credit=c['credit'];ass+=event(0,d,'{\\an7\\pos(178,858)\\fs26\\bord3\\1c&HFFFFFF&}'+credit,0)
 if c.get('showGameTitle'):ass+=event(.1,min(3,d),'{\\an8\\pos(960,22)\\fs39\\bord6}'+c['game'],0)
 for label in c.get('labels',[]):
  x,y=label['position'];ass+=event(label['from'],label['to'],f'{{\\an7\\pos({x},{y})\\fs39\\bord6}}'+label['text'],1)
 for m in c.get('marks',[]):
  a=max(src,m['from']);b=min(src+d,m['to'])
  if b<=a:continue
  color=bgr(m['color']);label=m['label'];lx,ly=m['labelPosition']
  ass+=event(a-src,b-src,f'{{\\an7\\pos({lx},{ly})\\fs42\\1c&H{color}&\\bord6}}'+label,3)
  # Two-frame steps provide smooth editorial tracking. No extrapolation across
  # camera cuts, occlusion or off-screen intervals: each is a separate mark.
  for frame in range(math.ceil((a-src)*60),math.floor((b-src)*60),2):
   t=src+frame/60
   if m.get('shape')=='path':shape=arrow_path([(160+x*SCALE,y*SCALE) for x,y in m['points']],min(1,(t-a+.033)/.6))
   else:
    x,y,w,h=interpolate(m['keyframes'],t);x=160+x*SCALE;y*=SCALE;w*=SCALE;h*=SCALE
    shape=ring(m.get('shape','rectangle'),x,y,w,h)
   ass+=event(frame/60,min(frame/60+2/60,b-src),f'{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c&H{color}&}}'+shape,2)
 return ass
def run(args,log):
 with log.open('w',encoding='utf8') as f:r=subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-3000:])
if __name__=='__main__':
 plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));codehash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 assert plan.get('timing')=='measured-and-asr-aligned','Estimated cuts must not enter production'
 for c in plan['cuts']:
  if c['kind']!='independent-gameplay':continue
  assert c['playbackSpeed']==1 and not c.get('loop')
  source=R/c['sourceFile'];out=O/(c['id']+'.mp4');receipt=O/(c['id']+'-footage.json');ass=annotations(c);asspath=O/(c['id']+'-marks.ass');asspath.write_text(ass,encoding='utf8')
  signature=dict(cut=c,sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),codeSha256=codehash,marksSha256=hashlib.sha256(ass.encode()).hexdigest())
  if out.exists() and receipt.exists() and json.loads(receipt.read_text())==signature:continue
  vf='fps=60,scale=1600:900:flags=lanczos,pad=1920:1080:160:0:black,setsar=1,ass='+asspath.relative_to(R).as_posix()
  run(['-ss',str(c['sourceStart']),'-i',str(source),'-an','-vf',vf,'-frames:v',str(c['frames']),'-c:v','libx264','-threads','4','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000','-movflags','+faststart',str(out)],O/(c['id']+'-render.log'))
  receipt.write_text(json.dumps(signature,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(c['id'],c['frames'],'frames',flush=True)
