"""Name actual Unity-exported axes/points; no inferred commercial-game data."""
from pathlib import Path
import importlib.util,json,subprocess,math
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_labels_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
COLORS=['635AEF','8ECE6C','EDB966'];N=c.O/'unity/native';D=c.O/'unity/labeled'
def at(sec):
 cs=math.floor(sec*100+1e-7);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1000
PlayResY: 700
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Malgun Gothic,42,&H00F5F5F5,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def escape(p):return c.rel(p).replace(':',r'\:').replace("'",r"\'")
def labels(row,shot):
 anchors={a['name']:a for a in row['anchors']};out=[];placed=[]
 def add(name,text,color,size=42):
  a=anchors[name]
  if not a['inViewport']:return
  x,y=a['pixel']['x'],a['pixel']['y'];x=max(15,min(870,x+10));y=max(8,min(630,y-30))
  if any(abs(x-px)<80 and abs(y-py)<42 for px,py in placed):return
  placed.append((x,y));out.append((x,y,text,color,size))
 if shot['axes']:
  for i,k in enumerate('XYZ'):add('object'+k,k,COLORS[i])
 if shot['upright']:
  for k in 'XYZ':add('upright'+k,k+' 기준','BBBBBB',34)
 if shot.get('point'):add('point','P','83CFE8',42)
 if row['mode']=='projection':out.append((18,640,f'기준 X축의 성분 = {row["projection"]:.2f}','C2C773',40))
 if row['mode']=='arm':
  for n,l in [('armOrigin','C 몸'),('handOrigin','B 손'),('swordOrigin','A 도구')]:add(n,l,'F5F5F5',38)
 if row['mode']in ['creep','normalize','orthonormalize']:
  out.append((12,642,'오차를 확대한 설명 모형','83CFE8',36))
 return out
def main():
 c.authorized();D.mkdir(parents=True,exist_ok=True);plan=c.read(H/'unity-plan.json');records=[]
 for shot in plan['shots']:
  sid=shot['id'];src=N/(sid+'.mp4');anchor=N/(sid+'.anchors.ndjson');data=[json.loads(x)for x in anchor.read_text(encoding='utf8').splitlines()];assert len(data)==shot['frames']
  ass=D/(sid+'.ass');events=[]
  for row in data:
   f=row['frame'];start,end=at(f/60),at((f+1)/60)
   for x,y,text,color,size in labels(row,shot):events.append(f'Dialogue: 1,{start},{end},Label,,0,0,0,,{{\\an7\\pos({x:.2f},{y:.2f})\\fs{size}\\1c&H{color}&}}{text}')
  ass.write_text(HEADER+'\n'.join(events)+'\n',encoding='utf8');dst=D/(sid+'.mp4');log=D/(sid+'.log')
  cmd=['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-threads','2','-filter_threads','2','-i',str(src),'-vf','ass='+escape(ass),'-an','-frames:v',str(shot['frames']),'-r','60','-fps_mode','cfr','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-video_track_timescale','60000',str(dst)]
  with log.open('wb')as f:r=subprocess.run(cmd,cwd=c.R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  assert r.returncode==0,log.read_text(encoding='utf8',errors='replace')[-1500:]
  indices={0,shot['frames']//2,shot['frames']-1}
  if sid=='projection':indices|={120,180}
  states={}
  for frame in sorted(indices):
   png=D/f'{sid}.frame-{frame:04}.png';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-n','-threads','1','-ss',f'{frame/60:.9f}','-i',str(dst),'-frames:v','1','-update','1',str(png)],check=True,cwd=c.R,creationflags=subprocess.CREATE_NO_WINDOW)
   states[str(frame)]=dict(file=c.rel(png),sha256=c.sha(png))
  records.append(dict(id=sid,file=c.rel(dst),sha256=c.sha(dst),frames=shot['frames'],sourceSha256=c.sha(src),anchors=dict(file=c.rel(anchor),sha256=c.sha(anchor)),ass=dict(file=c.rel(ass),sha256=c.sha(ass)),states=states))
  c.save(H/'labeled-native.json',dict(records=records,complete=len(records)==len(plan['shots']),visibility='Actual exported viewport tips; coincident labels suppressed. No fabricated depth detector; visual inspection still required.'))
  print('Labeled',sid,flush=True)
if __name__=='__main__':main()
