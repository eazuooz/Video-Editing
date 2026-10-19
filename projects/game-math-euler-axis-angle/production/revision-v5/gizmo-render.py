"""Original, source-anchored educational rotation rings; no recovered game transforms."""
from pathlib import Path
import json,math,importlib.util,hashlib,copy,subprocess,sys
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v5';E=O/'gizmos';E.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('ann',P/'production/revision-v3/annotation-render.py');ann=importlib.util.module_from_spec(spec);spec.loader.exec_module(ann)
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
def run(args,name):
 with (E/(name+'.log')).open('wb') as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if q.returncode:raise RuntimeError((E/(name+'.log')).read_text(errors='replace')[-2500:])
COL={'X':'#F27873','Y':'#7FD69B','Z':'#54A3E8'}
def bgr(c):return c[5:7]+c[3:5]+c[1:3]
def txt(a,b,value,x,y,size=42,col='#FFFFFF',layer=8):
 return f'Dialogue: {layer},{ann.stamp(a)},{ann.stamp(b)},Label,,0,0,0,,{{\\an7\\pos({x:.2f},{y:.2f})\\fs{size}\\1c&H{bgr(col)}&\\bord3\\3c&H101010&}}'+value
def stroke(a,b,points,color,width=6,alpha='00',layer=5):
 path=ann.poly(points);return f'Dialogue: {layer},{ann.stamp(a)},{ann.stamp(b)},Guide,,0,0,0,,{{\\an7\\pos(0,0)\\clip(0,0,1920,878)\\1a&HFF&\\bord{width}\\3c&H{bgr(color)}&\\3a&H{alpha}&\\p1}}'+path
def projection(v,c,r):
 x,y,z=v;return [c[0]+r*(.94*x-.34*z),c[1]+r*(-.86*y-.48*z)],(-.29*x+.45*y-.84*z)
def rings(c,r):
 result=[]
 for axis in 'XYZ':
  points=[]
  for i in range(97):
   th=i*math.tau/96;a,b=math.cos(th),math.sin(th)
   v={'X':(0,a,b),'Y':(a,0,b),'Z':(a,b,0)}[axis];xy,d=projection(v,c,r);points.append((xy,d))
  result.append((axis,points))
 return result
def draw(window,tracker,f,frames):
 time=window['start']+f/60;p=ann.interpolate(tracker['keyframes'],time)
 if not p:return []
 anchor=p.get('center',p.get('points',[None,None])[1]);c=list(anchor)
 offset=window.get('offset',[0,0]);c=[c[i]+offset[i] for i in range(2)]
 r=150 if window['id']!='20-mast' else 132
 # A low-on-screen kart remains visible even when its center enters the
 # caption reserve. Keep its conceptual rings above that reserve and connect
 # the actual tracked center, rather than toggling the rings at radius95.
 clampedKart=window['id']=='05-kart' and c[1]>700
 if clampedKart:c[1]=700
 if offset!=[0,0]:c[0]=min(1710,max(190,c[0]));c[1]=min(700,max(185,c[1]))
 else:
  r=min(r,868-c[1])
  if r<95:return []
 if window['id']=='14-turn' and anchor[1]>765:return []
 a,b=f/60,(f+1)/60;events=[]
 if offset!=[0,0] or clampedKart:
  edge=[c[0],c[1]+r*.85] if clampedKart else [c[0]-r*.9,c[1]+r*.1]
  events +=[stroke(a,b,[anchor,edge],'#101010',7,layer=3),stroke(a,b,[anchor,edge],'#B8B8B8',3,layer=4)]
 # All three orthogonal rings share a single explicitly illustrative screen
 # projection. No numeric game angle, fitted world camera or telemetry is shown.
 for axis,pts in rings(c,r):
  active=window.get('activeAxis')==axis;col=COL[axis]
  # Back arcs are dashed and lower contrast. Front arcs are solid; no filled
  # ring or opaque card covers the actual object or surface being explained.
  for side in [-1,1]:
   chunks=[];chunk=[]
   for k,(xy,depth) in enumerate(pts):
    visible=(depth>=0 if side==1 else depth<0) and (side==1 or k%8<4) and k<=max(8,min(96,round((f+1)/24*96)))
    if visible:chunk.append(xy)
    elif len(chunk)>1:chunks.append(chunk);chunk=[]
    else:chunk=[]
   if len(chunk)>1:chunks.append(chunk)
   for points in chunks:
    width=8 if active and side==1 else 4
    alpha='00' if active else ('30' if side==1 else '85')
    events +=[stroke(a,b,points,'#101010',width+3,alpha,layer=4 if side<0 else 6),stroke(a,b,points,col,width,alpha,layer=5 if side<0 else 7)]
  q={'X':(0,.85,.52),'Y':(.98,0,-.2),'Z':(-.78,-.62,0)}[axis];xy,_=projection(q,c,r)
  events.append(txt(a,b,axis,xy[0]-12,xy[1]-26,36,col,9))
 return events
ENC=['-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-color_range','tv','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000']
def main():
 selected();plan=read(H/'gizmo-plan.json');timeline=read(P/plan['timeline']);annotations=read(P/plan['sourceAnnotation']);outputs=[];verified_sources=set()
 for window in plan['windows']:
  selected();tracker=next(w for w in annotations['windows'] if w['id']==window['id']);c=next(c for c in timeline['cuts'] if c['scene']==tracker['scene'] and c['sourceId']==tracker['sourceId'] and c['sourceStart']<=window['start'] and c['sourceEnd']>=window['end'])
  frames=round(window['end']*60)-round(window['start']*60);globalFrame=c['globalStartFrame']+round((window['start']-c['sourceStart'])*60)
  if c['sourceFile'] not in verified_sources:
   assert sha(R/c['sourceFile'])==c['sourceSha256'],'Independent source bytes changed'
   verified_sources.add(c['sourceFile'])
  mini=copy.deepcopy(c);mini.update(sourceStart=window['start'],frames=frames)
  original=copy.deepcopy(annotations)
  # Keep original spoken yellow observation marks. Replace only the old turn
  # ellipse with the meaningful rings; long-axis/road guides remain untouched.
  if window['id'] in ['05-kart','14-turn']:
   # Keep tracker keys available for another guide's occlusion mask while
   # suppressing its redundant visible body shape and old label.
   for w in original['windows']:
    if w['id']==window['id']:w['sourceIn']=0;w['sourceOutExclusive']=0
  else:
   for w in original['windows']:
    if w['id']==window['id'] and 'center' in w['keyframes'][0]:w['shape']='brackets'
  body,_=ann.cut_ass(mini,original);events=[]
  label=window.get('label',window['meaning']);x,y=window.get('labelPosition',[1320,220])
  events.append(txt(0,frames/60,'회전 기즈모 · 개념도',x,y,38))
  events.append(txt(0,frames/60,label,x,y+58,44,COL.get(window.get('activeAxis'),'#F4D557')))
  for f in range(frames):events+=draw(window,tracker,f,frames)
  ass=E/(window['id']+'.ass');ass.write_text(body+'\n'.join(events)+'\n',encoding='utf8')
  graph='[0:v]fps=60,setsar=1,settb=1/60,setpts=N,ass='+ass.relative_to(R).as_posix()+',split=2[clean][cap];[cap]setpts=PTS+'+str(globalFrame)+',ass='+(P/'production/local/revision-v3/captions.ko.ass').relative_to(R).as_posix()+',setpts=PTS-STARTPTS[captioned]'
  sig=dict(sourceSha256=c['sourceSha256'],sourceStart=window['start'],globalStartFrame=globalFrame,frames=frames,assSha256=sha(ass),captionAssSha256=sha(P/'production/local/revision-v3/captions.ko.ass'),filterGraph=graph,codec=ENC)
  receipt=E/(window['id']+'.json');files={kind:E/(window['id']+'-'+kind+'.mp4') for kind in ['clean','captioned']}
  if not (receipt.exists() and read(receipt).get('inputs')==sig and all(f.exists() for f in files.values())):
   cmd=['ffmpeg','-v','warning','-y','-ss',str(window['start']),'-i',str(R/c['sourceFile']),'-an','-filter_complex',graph]
   for kind,f in files.items():cmd+=['-map',f'[{kind}]','-frames:v',str(frames),'-r','60','-enc_time_base','1:60',*ENC,str(f)]
   run(cmd,window['id']);save(receipt,dict(inputs=sig,files={k:dict(file=f.relative_to(R).as_posix(),sha256=sha(f)) for k,f in files.items()}))
  outputs.append(dict(id=window['id'],globalStartFrame=globalFrame,frames=frames,kind='gizmo',files=read(receipt)['files']));print('Prepared',window['id'],frames,flush=True)
 save(E/'outputs.json',dict(revision=plan['revision'],replacements=outputs,narrationAndTimingChanged=False))
if __name__=='__main__':main()
