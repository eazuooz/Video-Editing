"""Exact source crops and same-frame control magnifiers for episode01."""
import pathlib,json
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1'
NAMES={'epic-robo-performance-2017':'Robo Recall · UE4 엔진 시연 (2017)','epic-lighting-techniques-2017':'UE4 조명 · 공식 엔진 시연 (2017)','epic-material-baking-2017':'UE4 표면 데이터 내보내기 (2017)','epic-post-processing-2017':'UE4 앰비언트 오클루전 시연 (2017)','epic-csm-receiver':'UE4 캐스케이드 그림자 수신 예제','steam-quake-enhanced-2021':'Quake · 2021 재발매판','bethesda-quake2-enhanced-2023':'Quake II · 2023 Enhanced','steam-doom-2024':'DOOM · 2024 재발매판','steam-doom3-original':'DOOM 3 · 공식 게임 화면','steam-hl2-legacy-trailer':'Half-Life 2 · 공식 게임 화면','steam-hl2-current-trailer':'Half-Life 2 · 현재 공식 트레일러','epic-robo-recall-announce-2016':'Robo Recall · 공식 발표 화면 (2016)'}
def spec(n):
 sid=n.get('sourceId');k=n.get('packetIndex');t=n['sourceStartFrame']/60
 d=dict(crop=None,magnifiers=[],header=NAMES.get(sid),focus=n.get('focusKo'),presenterExclusionRequired=True,sourceAudio=False,playbackSpeed=1)
 if sid=='steam-doom3-original':d['crop']=[118,64,704,396]
 elif sid=='epic-robo-performance-2017':
  d['crop']=[308,120,960,540]
  if k in [17,18,25,28,39]:d['crop']=[202,116,1248,702]
  if k in [41,47]:d['crop']=[0,0,1488,837]
  if k==42 and t<2000:d['magnifiers']=[dict(crop=[726,1043,475,34],rect=[48,810,950,68],label='실제 콘솔 입력 확대',sourceEnableSeconds=[1913.5,1916.02])]
 elif sid=='epic-lighting-techniques-2017':
  d['crop']=[0,0,1488,837]
  if k in [29,30,34]:d['crop']=[250,80,1248,702]
  if k==34:d['crop']=[320,70,1152,648]
  if k in [36,37]:d['magnifiers']=[dict(crop=[1438,695,350,138],rect=[1100,150,770,304],label='실제 CSM 설정 확대')]
 elif sid=='epic-material-baking-2017':d['crop']=[0,0,1488,837]
 elif sid=='epic-post-processing-2017':d['magnifiers']=[dict(crop=[860,375,360,285],rect=[1210,150,680,538],label='실제 AO 설정 확대')]
 return d
def filtergraph(n,tail=None):
 d=spec(n);magnifiers=d['magnifiers'];parts=[]
 if magnifiers:parts.append('[0:v]split='+str(len(magnifiers)+1)+'[main]'+''.join(f'[m{i}]' for i in range(len(magnifiers))));src='[main]'
 else:src='[0:v]'
 crop=d['crop'];cropstr=('crop=%d:%d:%d:%d,'%tuple([crop[2],crop[3],crop[0],crop[1]])) if crop else ''
 parts.append(src+cropstr+"scale=1920:1080:flags=lanczos,setsar=1,fps=60:start_time=0[base]")
 out='base'
 for i,m in enumerate(magnifiers):
  x,y,w,h=m['crop'];dx,dy,dw,dh=m['rect'];parts.append(f'[m{i}]crop={w}:{h}:{x}:{y},scale={dw}:{dh}:flags=lanczos,setsar=1,fps=60:start_time=0[mag{i}]')
  enable=''
  if m.get('sourceEnableSeconds'):
   origin=n['sourceStartFrame']/60+n.get('_previewOffsetSeconds',0)
   a,z=m['sourceEnableSeconds'];enable=f":enable='between(t,{a-origin:.6f},{z-origin:.6f})'"
  parts.append(f'[{out}][mag{i}]overlay={dx}:{dy}:shortest=1{enable}[ov{i}]');out=f'ov{i}'
 # Text files avoid shell/font-parser interpretation of user-visible Korean.
 if d['header']:
  texts=O/'framing-text';texts.mkdir(exist_ok=True)
  lines=[d['header'],d['focus'] or '']
  for i,text in enumerate(lines):
   f=texts/f"{n['id']}-{i}.txt";f.write_text(text,encoding='utf8')
   fpath=f.relative_to(R).as_posix();font=(O/'fonts/YamYamCaptionMedium.ttf').relative_to(R).as_posix()
   # Cache demo starts at its viewport toolbar; keep its menu area clear.
   x=1040 if n.get('packetIndex') in [29,30,34] else 48
   size=23 if x==1040 else (32 if i==0 else 27)
   if x==1040 and i==1:continue
   parts.append(f"[{out}]drawtext=fontfile='{font}':textfile='{fpath}':fontsize={size}:fontcolor={'0xFFE18A' if i==0 else 'white'}:x={x}:y={40+i*48}:box=1:boxcolor=black@0.72:boxborderw=12[tx{i}]");out=f'tx{i}'
 if tail:parts.append(f'[{out}]{tail}[out]')
 else:parts.append(f'[{out}]trim=end_frame={n["frames"]},setpts=N/(60*TB),format=yuv420p[out]')
 return ';'.join(parts)
