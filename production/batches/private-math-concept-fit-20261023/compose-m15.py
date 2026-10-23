"""Native-speed, individually reviewed object manipulation beside the reused math model."""
from common import *
import sys,math,shutil
P=R/'projects/game-math-rendering-light';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
T=read(H/'timeline.json');authorized('M15');C=O/'composite';C.mkdir(exist_ok=True)
SOURCES={'big': {'path': 'shared/output/game-math-part2-full-series/sources/wzQLP0Z3zII.mp4', 'audioPath': 'shared/output/private-math-concept-fit-20261023/sources/m15-audio/wzQLP0Z3zII.m4a', 'url': 'https://www.youtube.com/watch?v=wzQLP0Z3zII', 'game': 'Big Walk', 'minimumHeight': 1080}, 'sub': {'path': 'shared/output/game-math-part2-full-series/sources/dYyWmhVuc3w.mp4', 'audioPath': 'shared/output/private-math-concept-fit-20261023/sources/m15-audio/dYyWmhVuc3w.m4a', 'url': 'https://www.youtube.com/watch?v=dYyWmhVuc3w', 'game': 'Subnautica 2', 'minimumHeight': 1080}}
SHOTS={'02': {'scene': '02', 'source': 'big', 'start': 515.5, 'seconds': 8, 'offset': 0, 'title': '노란 벽과 뒤쪽 캐릭터', 'phases': [(0, 8, '가까운 벽이 겹친 부분을 가림')], 'model': '앞벽 / 뒤 물체', 'track': [], 'track2': [(3.5, 0.454, 0.464, 65), (3.625, 0.433, 0.464, 65), (3.75, 0.433, 0.467, 65), (3.875, 0.45, 0.5, 65), (4.0, 0.466, 0.533, 65), (4.125, 0.468, 0.548, 65), (4.25, 0.473, 0.555, 65), (4.375, 0.466, 0.564, 65), (4.5, 0.472, 0.545, 65), (4.625, 0.481, 0.491, 65), (4.75, 0.49, 0.491, 65), (4.875, 0.491, 0.558, 65), (5.0, 0.51, 0.57, 65), (5.125, 0.522, 0.573, 65), (5.25, 0.511, 0.555, 65), (5.375, 0.524, 0.527, 65)]}, '05-hole': {'scene': '05', 'source': 'big', 'start': 1595.65, 'seconds': 1.5, 'offset': 0, 'title': '빈 구멍으로 보이는 배경', 'phases': [(0, 1.5, '구멍에는 앞벽 표면이 없음')], 'model': '구멍 / 뒤의 나무', 'track': [(0.1, 0.875, 0.13, 64), (0.35, 0.9, 0.16, 64), (0.6, 0.8, 0.16, 64), (0.85, 0.8, 0.15, 64), (1.1, 0.8, 0.15, 64), (1.35, 0.88, 0.13, 64)], 'track2': []}, '05-glass': {'scene': '05', 'source': 'big', 'start': 1561, 'seconds': 7, 'offset': 15.66, 'title': '반투명 상자의 표면과 내부', 'phases': [(0, 7, '표면이 있어도 뒤 물체의 빛이 기여')], 'model': '반투명 표면 / 뒤 물체', 'track': [(0.3, 0.5, 0.63, 86), (1, 0.5, 0.63, 86), (3, 0.49, 0.62, 86), (5, 0.5, 0.63, 86), (6.8, 0.5, 0.63, 86)], 'track2': []}, '08-entry': {'scene': '08', 'source': 'sub', 'start': 618.5, 'seconds': 6, 'offset': 0, 'title': '입구 너머 벽과 수납장 비교', 'phases': [(0, 6, '재질과 조명 조건이 함께 만든 명암')], 'model': '표면 색 / 빛의 조건', 'track': [], 'track2': []}, '08-preview': {'scene': '08', 'source': 'sub', 'start': 742, 'seconds': 2, 'offset': 12.68, 'title': '문틀 설치와 주변 벽', 'phases': [(0, 2, '문틀 미리 보기 → 설치된 표면')], 'model': '도구 표시 / 주변 벽 밝기', 'track': [(1, 0.3, 0.52, 67), (1.7, 0.3, 0.52, 67)], 'track2': []}, '11': {'scene': '11', 'source': 'big', 'start': 797, 'seconds': 5, 'offset': 0, 'title': '빨간 표면 안의 밝고 어두운 부분', 'phases': [(0, 5, '표시된 색과 빛의 스펙트럼은 다른 정보')], 'model': '픽셀 색 / RGB 표현', 'track': [], 'track2': []}, '14': {'scene': '14', 'source': 'sub', 'start': 249, 'seconds': 5.5, 'offset': 0, 'title': '전방 조명이 비추는 굽은 바위', 'phases': [(0, 5.5, '법선 외에도 거리·가림·재질이 함께 변함')], 'model': '표면의 굴곡 / 각 위치의 법선', 'track': [(2, 0.49, 0.72, 86), (3, 0.48, 0.72, 86), (4, 0.5, 0.72, 86)], 'track2': []}, '17': {'scene': '17', 'source': 'sub', 'start': 764.5, 'seconds': 13.5, 'offset': 13.326499999999998, 'title': '천장 조명 설치 전후 비교', 'phases': [(0, 13.5, '미리 보기 → 조명 설치 → 밝아진 벽')], 'model': '빛을 내는 면 / 빛을 받는 벽', 'track': [(0.2, 0.5, 0.49, 93), (1, 0.5, 0.49, 93), (2, 0.5, 0.49, 93), (2.5, 0.5, 0.49, 93)], 'track2': []}, '19': {'scene': '19', 'source': 'big', 'start': 1945.5, 'seconds': 5, 'offset': 0, 'title': '그늘에서도 보이는 바닥', 'phases': [(0, 5, '한 방향이 가려져도 다른 빛은 남을 수 있음')], 'model': '가려진 방향 / 남은 방향', 'track': [], 'track2': []}, '21': {'scene': '21', 'source': 'big', 'start': 1708, 'seconds': 4, 'offset': 0, 'title': '앞뒤로 겹친 캐릭터', 'phases': [(0, 4, '가시성은 앞면 선택 / 밝기는 그다음 계산')], 'model': '어느 표면 / 얼마나 밝은가', 'track': [(1, 0.46, 0.43, 43), (2, 0.46, 0.43, 43), (3, 0.45, 0.43, 43)], 'track2': []}}
ENC=['-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-video_track_timescale','60000']


def ff(args,log):
 with (O/log).open('w',encoding='utf8') as f:subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y',*map(str,args)],cwd=C,stdout=f,stderr=f,check=True)
def stamp(t):
 n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
HEADER='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nScaledBorderAndShadow: yes\nWrapStyle: 2\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Malgun Gothic,42,&H00F5F5EF,&H00FFFFFF,&H00120D09,&H00120D09,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
def annotations(sid,s):
 lines=[]
 def event(a,b,txt,layer=2):
  offset=s.get('offset',0)
  lines.append(f'Dialogue: {layer},{stamp(a+offset)},{stamp(b+offset)},Default,,0,0,0,,{txt}')
 def label(a,b,x,y,txt,size=42,color='F5F5EF'):
  # Convert RGB to libass BGR, preserving the shared semantic palette.
  bgr=color[4:6]+color[2:4]+color[0:2]
  event(a,b,'{\\pos('+f'{x},{y}'+')\\fs'+str(size)+'\\1c&H'+bgr+'&}'+txt)
 d=s['seconds'];label(0,d,36,24,s['title'],52,'FFD773');label(0,d,36,92,SOURCES[s['source']]['game']+' · 실제 게임',28,'A7B0BC')
 label(0,d,1320,145,'원리 비교',48,'FFD773');label(0,d,1320,205,'자체 설명용 모형',32,'A7B0BC')
 label(0,d,1320,740,s['model'].replace(' · ','\\N').replace(' / ','\\N'),28)
 label(0,d,1320,818,'게임 내부 좌표의 측정값 아님',28,'A7B0BC')
 for a,b,txt in s['phases']:label(a,b,36,852,txt,35,'80D3A2')
 # Each tracked mark is screen-space editorial guidance, never game telemetry.
 for ti,track in enumerate([s.get('track',[]),s.get('track2',[])]):
  for one,two in zip(track,track[1:]):
   a,x,y,r=one;b,x2,y2,r2=two;cx=x*1280;cy=130+y*720;dx=x2*1280;dy=130+y2*720
   k=r*.55228475
   # Non-negative drawing coordinates + explicit top-left avoid libass bbox offset.
   shape=f'm 0 {r} b 0 {r-k} {r-k} 0 {r} 0 b {r+k} 0 {2*r} {r-k} {2*r} {r} b {2*r} {r+k} {r+k} {2*r} {r} {2*r} b {r-k} {2*r} 0 {r+k} 0 {r}'
   event(a,b,'{\\an7\\move('+f'{cx-r:.1f},{cy-r:.1f},{dx-r:.1f},{dy-r:.1f}'+')\\p1\\bord5\\shad0\\1a&HFF&\\3c&H'+('A2D380' if ti==0 else 'FFB778')+'&}'+shape,1)

 # Inspectable surface contours, interpolated between observed source pixels.
 for keys in s.get('contours',[]):
  for (a,points),(b,nextpoints) in zip(keys,keys[1:]):
   steps=max(1,round((b-a)*60))
   for frame in range(steps):
    u=(frame+.5)/steps;t0=a+(b-a)*frame/steps;t1=a+(b-a)*(frame+1)/steps
    pts=[((p[0]*(1-u)+q[0]*u)*2/3,130+(p[1]*(1-u)+q[1]*u)*2/3) for p,q in zip(points,nextpoints)]
    for p,q in zip(pts,pts[1:]):
     x=min(p[0],q[0]);y=min(p[1],q[1]);shape=f'm {p[0]-x:.2f} {p[1]-y:.2f} l {q[0]-x:.2f} {q[1]-y:.2f}'
     event(t0,t1,'{\\an7\\pos('+f'{x:.2f},{y:.2f}'+')\\p1\\bord3\\shad0\\1a&HFF&\\3c&HA2D380&}'+shape,1)

 # Reference labels follow three directly inspected roof corners and clear before reshaping.
 for (a,pts),(b,nxt) in zip(s.get('points',[]),s.get('points',[])[1:]):
  for i,(p,q) in enumerate(zip(pts,nxt)):
   x=p[0]*2/3;y=130+p[1]*2/3;xx=q[0]*2/3;yy=130+q[1]*2/3
   event(a,b,'{\\an5\\move('+f'{x:.1f},{y:.1f},{xx:.1f},{yy:.1f}'+')\\fs33\\bord3\\1c&H73D7FF&}'+chr(65+i))
 path=C/f'{sid}.guides.ass';path.write_text(HEADER+'\n'.join(lines)+'\n',encoding='utf8');return path
def main():
 progress=read(H/'render-progress.json');assert progress['state']=='rendered-qa-pending','Wait for the existing finite render job'
 records=[];sources={}
 for key,v in SOURCES.items():
  path=R/v['path'];meta=probe(path);video=next(s for s in meta['streams'] if s['codec_type']=='video');assert video['height']>=v['minimumHeight']
  sources[key]=dict(**v,sha256=sha(path),width=video['width'],height=video['height'],fps=video['r_frame_rate'],audioStreams=[s['codec_name'] for s in meta['streams'] if s['codec_type']=='audio'])
 receipt=H/'composition.json';identity=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(__file__)).encode()).hexdigest();previous=read(receipt) if receipt.exists() else {'identity':identity,'scenes':[]}
 assert previous['identity']==identity,'Preserve mismatched prior composite; inspect before replacing'
 for slot in T['scenes']:
  sid=slot['id'];authorized('M15');model=R/progress['scenes'][sid]['path'];assert sha(model)==progress['scenes'][sid]['sha256'];dst=C/f'{sid}.mp4'
  old=next((r for r in previous['scenes'] if r['id']==sid),None)
  if old and sha(dst)==old['sha256']:records.append(old);continue
  n=slot['frames'];args=['-i',model]
  selected=[(key,v) for key,v in SHOTS.items() if v['scene']==sid]
  assert abs(sum(v['seconds'] for key,v in selected)-slot['gameWindowSeconds'])<.001
  for key,shot in selected:
   assert shot['offset']+shot['seconds']<=slot['seconds']
  prep='[0:v]null[prepared];'
  if sid in ['02','05','08','11','14','17','19','21']:
   prep='[0:v]drawbox=x=0:y=875:w=1920:h=60:color=0x090D12:t=fill[prepared];'
  if selected:
   graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),split={len(selected)+1}[full]'+''.join(f'[m{i}]' for i in range(len(selected)))+';'
   current='full'
   for i,(key,shot) in enumerate(selected):
    src=SOURCES[shot['source']];annotations(key,shot);off=shot['offset'];sec=shot['seconds']
    args+=['-ss',shot['start'],'-t',sec,'-i',R/src['path']]
    graph+=f'[m{i}]crop=850:540:80:210,scale=620:394[small{i}];color=c=0x090D12:s=1920x1080:r=60:d={slot["seconds"]}[bg{i}];[{i+1}:v]fps=60,scale=1280:720:flags=lanczos,setsar=1,setpts=PTS+{off}/TB[game{i}];[bg{i}][game{i}]overlay=0:130:eof_action=pass[panel{i}];[panel{i}][small{i}]overlay=1300:240,ass={key}.guides.ass[split{i}];[{current}][split{i}]overlay=0:0:enable=\'between(t,{off},{off+sec-1/60})\'[out{i}];'
    current=f'out{i}'
   graph+=f'[{current}]setsar=1[v]'
  else:graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),setsar=1[v]'
  graph=prep+graph.replace('[0:v]','[prepared]')
  print('Compose M15',sid,'game + math' if selected else 'preserved math',flush=True)
  original_video=next(x for x in probe(model)['streams'] if x['codec_type']=='video')
  passthrough_ok=not selected and int(original_video['nb_frames'])==n and original_video['r_frame_rate']=='60/1' and original_video['width']==1920 and original_video['height']==1080 and float(original_video.get('start_time',0))==0
  if passthrough_ok:
   shutil.copy2(model,dst)
   assert sha(dst)==sha(model)
  else:
   ff(args+['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],f'composite-{sid}.log')
  v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==n and v['height']==1080 and v['r_frame_rate']=='60/1'
  record=dict(id=sid,path=rel(dst),sha256=sha(dst),frames=n,game=[v for key,v in selected],visualReview='pending encoded captioned review',bytePreservedScene=passthrough_ok);records.append(record)
  save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=len(records)==22,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 assert len(records)==22
 save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=True,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 print('22 exact-frame compositions complete; final pair and QA pending',flush=True)
if __name__=='__main__':main()
