"""Native-speed, individually reviewed object manipulation beside the reused math model."""
from common import *
import sys,math,shutil
P=R/'projects/game-math-camera-frustum';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
T=read(H/'timeline.json');authorized('M16');C=O/'composite';C.mkdir(exist_ok=True)
SOURCES={'split': {'path': 'shared/output/game-math-part2-full-series/sources/8RZ1nPWzWtg.mp4', 'audioPath': 'shared/output/private-math-concept-fit-20261023/sources/m16-audio/8RZ1nPWzWtg.mp4', 'url': 'https://www.youtube.com/watch?v=8RZ1nPWzWtg', 'game': 'Split Fiction', 'minimumHeight': 1080}, 'town': {'path': 'shared/output/game-math-part2-full-series/sources/FRfnXAIbA-M.mp4', 'audioPath': 'shared/output/private-math-concept-fit-20261023/sources/m16-audio/FRfnXAIbA-M.mp4', 'url': 'https://www.youtube.com/watch?v=FRfnXAIbA-M', 'game': 'Townscaper', 'minimumHeight': 1080}, 'tiny': {'path': 'shared/output/private-math-concept-fit-20261023/sources/tiny-glade-official/release-date-trailer.mp4', 'url': 'https://pouncelight.games/tiny-glade/presskit', 'game': 'Tiny Glade', 'minimumHeight': 1080}}
SHOTS={'02': {'scene': '02', 'source': 'split', 'start': 33, 'seconds': 8, 'offset': 0, 'title': '두 플레이어의 서로 다른 화면', 'phases': [(0, 8, '분할선 양쪽의 관찰 방향을 비교')], 'model': '관찰 방향 / 출력 영역', 'track': [], 'track2': []}, '05': {'scene': '05', 'source': 'tiny', 'start': 12, 'seconds': 4.5, 'offset': 0, 'title': '탑 앞의 건물을 직접 편집', 'phases': [(0, 4.5, '지붕과 벽이 바뀜 → 물체의 형태 변경')], 'model': '물체 변화 / 시점 변화', 'track': [(2, 0.53, 0.59, 95), (2.5, 0.49, 0.6, 95), (3, 0.48, 0.6, 95), (3.5, 0.47, 0.6, 95), (4.3, 0.46, 0.6, 95)], 'track2': []}, '08': {'scene': '08', 'source': 'town', 'start': 409.7, 'seconds': 4.3, 'offset': 0, 'title': '완성된 건물 주위로 시점 이동', 'phases': [(0, 4.3, '낮은 시점 → 높은 시점 → 다른 면')], 'model': '같은 건물 / 다른 관찰 방향', 'track': [(3.3, 0.58, 0.38, 70), (3.8, 0.58, 0.38, 70), (4.2, 0.58, 0.38, 70)], 'track2': []}, '11': {'scene': '11', 'source': 'split', 'start': 294, 'seconds': 7, 'offset': 0, 'title': '캐릭터 크기와 주변 공간', 'phases': [(0, 7, '거리·방향·시야각을 따로 확인')], 'model': '크기를 만드는 조건 / 통제된 비교', 'track': [], 'track2': []}, '13': {'scene': '13', 'source': 'town', 'start': 775.5, 'seconds': 4.5, 'offset': 0, 'title': '같은 지붕을 넓게, 가까이 보기', 'phases': [(0, 4.5, '같은 기준점을 남겨 확대 전후 비교')], 'model': '앞 지붕 A / 뒤 지붕 B', 'track': [(3.5, 0.2, 0.21, 70), (4, 0.2, 0.21, 70), (4.4, 0.2, 0.23, 70)], 'track2': []}, '16': {'scene': '16', 'source': 'town', 'start': 1450, 'seconds': 4.5, 'offset': 0, 'title': '큰 문과 뒤쪽 지붕의 관계', 'phases': [(0, 4.5, '건물 고정 · 가까워지고 방향이 바뀜')], 'model': '앞벽 A / 뒤 지붕 B', 'track': [(2.5, 0.72, 0.35, 80), (3, 0.72, 0.35, 80), (3.5, 0.72, 0.35, 80), (4, 0.72, 0.35, 80)], 'track2': []}, '19': {'scene': '19', 'source': 'tiny', 'start': 53.25, 'seconds': 5.25, 'offset': 0, 'title': '같은 성에서 주변 탑까지', 'phases': [(0, 5.25, '카메라가 물러나며 보이는 범위 변화')], 'model': '관찰 위치 / 담을 범위', 'track': [], 'track2': []}, '21-view': {'scene': '21', 'source': 'town', 'start': 1104, 'seconds': 3, 'offset': 0, 'title': '물체 변화와 관찰 변화 구분', 'phases': [(0, 3, '시점과 담는 범위를 먼저 비교')], 'model': '관찰 조건 변화', 'track': [], 'track2': []}, '21-build': {'scene': '21', 'source': 'town', 'start': 1107, 'seconds': 7, 'offset': 10.813333333333283, 'title': '블록 추가는 물체의 변화', 'phases': [(0, 7, '새로 생긴 바닥과 기존 면 구분')], 'model': '물체 자체의 변화', 'track': [(2.5, 0.55, 0.58, 100), (3, 0.55, 0.58, 100), (3.5, 0.55, 0.58, 100), (4, 0.55, 0.58, 100), (4.5, 0.55, 0.58, 100), (5, 0.55, 0.58, 100), (5.5, 0.55, 0.58, 100), (6, 0.55, 0.58, 100)], 'track2': []}}
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
 if s['source']=='split':
  event(0,d,'{\\an7\\pos(640,130)\\p1\\bord3\\shad0\\1a&HFF&\\3c&HA2D380&}m 0 0 l 0 720',1)
  label(0,d,55,150,'왼쪽 카메라',28,'80D3A2');label(0,d,700,150,'오른쪽 카메라',28,'78B7FF')
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
  sid=slot['id'];authorized('M16');model=R/progress['scenes'][sid]['path'];assert sha(model)==progress['scenes'][sid]['sha256'];dst=C/f'{sid}.mp4'
  old=next((r for r in previous['scenes'] if r['id']==sid),None)
  if old and sha(dst)==old['sha256']:records.append(old);continue
  n=slot['frames'];args=['-i',model]
  selected=[(key,v) for key,v in SHOTS.items() if v['scene']==sid]
  assert abs(sum(v['seconds'] for key,v in selected)-slot['gameWindowSeconds'])<.001
  for key,shot in selected:
   assert shot['offset']+shot['seconds']<=slot['seconds']
  prep='[0:v]null[prepared];'
  if sid in ['02','05','08','11','13','16','19','21']:
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
  print('Compose M16',sid,'game + math' if selected else 'preserved math',flush=True)
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
