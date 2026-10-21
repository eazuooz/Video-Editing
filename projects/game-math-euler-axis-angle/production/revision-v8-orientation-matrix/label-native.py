"""Name actual Unity-exported axes/points; no inferred commercial-game data."""
from pathlib import Path
import importlib.util,json,subprocess,math,argparse,shutil
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
 if shot['axes'] and shot['upright']:
  for k in 'XYZ':add('upright'+k,k+' 기준','BBBBBB',34)
 if shot['id']=='home-y90':add('activeRotationAxisTip','회전축 Y','BBBBBB',36)
 if shot.get('point'):add('point','P','C2C773',42)
 if row['mode']=='projection':out.append((18,640,f'기준 X축의 성분 = {row["projection"]:.2f}','C2C773',40))
 if row['mode']=='arm':
  # All three narrated frames must remain named even when hand/tool origins coincide.
  out.extend([(85,300,'C 몸 기준','F5F5F5',40),(85,346,'어깨 원점','BBBBBB',30),
              (645,465,'B 손','F5F5F5',42),(645,205,'A 도구','F5F5F5',42)])
 if row['mode']in ['creep','normalize','orthonormalize']:
  out.append((12,642,'오차를 확대한 설명 모형','83CFE8',36))
 return out

def arm_leaders(row,start,end):
 if row['mode']!='arm':return []
 anchors={a['name']:a for a in row['anchors']};events=[]
 for name,x,y in [('armOrigin',290,330),('handOrigin',635,492),('swordTip',635,238)]:
  a=anchors[name];tx,ty=a['pixel']['x'],a['pixel']['y'];length=math.hypot(tx-x,ty-y);nx,ny=-(ty-y)/length*2.5,(tx-x)/length*2.5
  points=[(x+nx,y+ny),(tx+nx,ty+ny),(tx-nx,ty-ny),(x-nx,y-ny)]
  path='m '+' l '.join(f'{px:.2f} {py:.2f}'for px,py in points)
  events.append(f'Dialogue: 0,{start},{end},Label,,0,0,0,,{{\\an7\\pos(0,0)\\p1\\bord0\\1c&HBBBBBB&}}{path}{{\\p0}}')
 return events
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--only',action='append');ap.add_argument('--rebuild-selected',action='store_true');a=ap.parse_args()
 c.authorized();D.mkdir(parents=True,exist_ok=True);plan=c.read(H/'unity-plan.json');records=[]
 capture=c.read(N/'capture-receipt.json');assert capture['complete'] and not capture['sampleOnly'];actual={x['id']:x for x in capture['outputs']}
 previous=c.read(H/'labeled-native.json')if a.only else None
 chosen=set(a.only or [x['id']for x in plan['shots']]);assert chosen.issubset({x['id']for x in plan['shots']})
 if a.rebuild_selected:assert a.only and chosen.issubset({'arm-hand-sword','home-y90'}),'Only the explicitly approved two labeled outputs may be replaced'
 oldrecords={x['id']:x for x in previous['records']}if previous else{}
 archive=None
 if a.rebuild_selected:
  archive=c.O/'unity/labeled-history'/('before-two-label-fix-'+c.sha(H/'labeled-native.json')[:12]);archive.mkdir(parents=True,exist_ok=False)
  c.save(archive/'manifest.json',previous)
  for sid in sorted(chosen):
   row=oldrecords[sid];assert c.sha(c.R/row['file'])==row['sha256']
   for path in D.glob(sid+'.*'):
    path.resolve().relative_to(D.resolve());dest=archive/path.name;dest.resolve().relative_to(archive.resolve());assert path.is_file()and not dest.exists();shutil.move(str(path),str(dest))
 for shot in plan['shots']:
  if shot['id'] not in chosen:
   row=oldrecords[shot['id']];assert c.sha(c.R/row['file'])==row['sha256'];records.append(row);continue
  sid=shot['id'];src=N/(sid+'.mp4');anchor=N/(sid+'.anchors.ndjson');data=[json.loads(x)for x in anchor.read_text(encoding='utf8').splitlines()];assert len(data)==shot['frames']
  assert actual[sid]['file']['sha256']==c.sha(src) and actual[sid]['anchors']['sha256']==c.sha(anchor)
  assert (actual[sid]['frames'],actual[sid]['width'],actual[sid]['height'],actual[sid]['fps'])==(shot['frames'],1000,700,60)
  ass=D/(sid+'.ass');events=[]
  for row in data:
   f=row['frame'];start,end=at(f/60),at((f+1)/60)
   for x,y,text,color,size in labels(row,shot):events.append(f'Dialogue: 1,{start},{end},Label,,0,0,0,,{{\\an7\\pos({x:.2f},{y:.2f})\\fs{size}\\1c&H{color}&}}{text}')
   events.extend(arm_leaders(row,start,end))
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
  records.append(dict(id=sid,file=c.rel(dst),sha256=c.sha(dst),frames=shot['frames'],sourceSha256=c.sha(src),anchors=dict(file=c.rel(anchor),sha256=c.sha(anchor)),ass=dict(file=c.rel(ass),sha256=c.sha(ass)),states=states,implementationSha256=c.sha(Path(__file__))))
  if not a.only:c.save(H/'labeled-native.json',dict(records=records,complete=len(records)==len(plan['shots']),sourceCaptureSha256=c.sha(N/'capture-receipt.json'),implementationSha256=c.sha(Path(__file__)),visibility='Actual exported viewport tips; coincident axis labels suppressed. Arm A/B/C names use editorial leaders to actual anchors. No fabricated depth detector; visual inspection still required.'))
  print('Labeled',sid,flush=True)
 if a.only:
  unchanged=[dict(id=x['id'],sha256=x['sha256'])for x in records if x['id']not in chosen]
  c.save(H/'labeled-native.json',dict(records=records,complete=len(records)==len(plan['shots']),sourceCaptureSha256=c.sha(N/'capture-receipt.json'),implementationSha256=c.sha(Path(__file__)),visibility='Actual exported viewport tips; coincident axis labels suppressed. Arm A/B/C names use editorial leaders to actual anchors. No fabricated depth detector; visual inspection still required.',selectiveRebuild=dict(changed=sorted(chosen),previousImplementationSha256=previous['implementationSha256'],archivedPreviousOutputs=c.rel(archive)if archive else None,unchangedMedia=unchanged,nativeChanged=False)))
if __name__=='__main__':main()
