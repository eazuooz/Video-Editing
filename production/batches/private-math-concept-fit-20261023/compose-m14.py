"""Native-speed, individually reviewed object manipulation beside the reused math model."""
from common import *
import sys,math,shutil
P=R/'projects/game-math-polygon-partition-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
T=read(H/'timeline.json');authorized('M14');C=O/'composite';C.mkdir(exist_ok=True)
SOURCES={'tiny': {'path': 'shared/output/private-math-concept-fit-20261023/sources/tiny-glade-official/release-date-trailer.mp4', 'url': 'https://pouncelight.games/tiny-glade/', 'game': 'Tiny Glade', 'minimumHeight': 1080}, 'shapeB': {'path': 'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/shapez2-257312662.mp4', 'url': 'https://store.steampowered.com/app/2162800/shapez_2/', 'game': 'Shapez 2', 'minimumHeight': 1080, 'sourceSilent': True}, 'dorf': {'path': 'shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm', 'url': 'https://www.toukana.com/dorfromantik/presskit', 'game': 'Dorfromantik', 'minimumHeight': 1080}}
SHOTS={'QG04': {'source': 'tiny', 'start': 32.5, 'seconds': 6, 'title': '물을 그리면 남은 땅의 경계도 변경', 'phases': [(0, 6, '물로 바뀐 부분은 땅에서 제외')], 'model': '남겨야 할 땅 / 비워 둘 부분', 'track': [(1.7, 0.3, 0.85, 77), (2.5, 0.26, 0.85, 77), (3.5, 0.24, 0.84, 77), (4.5, 0.25, 0.85, 77), (5.7, 0.27, 0.85, 77)]}, 'QG06': {'source': 'shapeB', 'start': 42.8, 'seconds': 1.1, 'title': '입력 도형과 가공 뒤 조각 비교', 'phases': [(0, 1.1, '사각형 절단 · 아래 기계에서 조각 회전')], 'model': '잘린 조각 / 방향과 남은 모양', 'track': [(0.1, 0.31, 0.65, 74), (0.95, 0.31, 0.65, 74)], 'offset': 2.4}, 'QG07': {'source': 'shapeB', 'start': 30, 'seconds': 2.25, 'title': '벨트를 꺾어 이동 경로 연결', 'phases': [(0, 2.25, '물건의 이동 경로 · 땅의 외곽선 아님')], 'model': '경로의 순서 / 영역 경계는 다른 정보', 'track': [], 'contours': [[(0.4, [(1340, 365), (1340, 420), (790, 420)]), (1.4, [(1340, 365), (1340, 420), (730, 420)]), (2.1, [(1340, 365), (1340, 420), (730, 420)])]]}, 'QG09': {'source': 'dorf', 'start': 94.6, 'seconds': 2.4, 'title': '한 타일을 더해 땅의 윤곽 바꾸기', 'phases': [(0, 2.4, '타일 하나의 모양 / 합쳐진 경계')], 'model': '추가한 조각 / 전체 바깥선', 'track': [(0.9, 0.33, 0.55, 70), (1.55, 0.33, 0.55, 70)]}, '21': {'source': 'dorf', 'start': 179, 'seconds': 4.8, 'title': '한 타일과 연결된 전체 땅', 'phases': [(0, 4.8, '빈자리와 새 타일이 만나는 경계')], 'model': '한 조각의 모양 / 전체 영역', 'track': [(1, 0.69, 0.44, 68), (2, 0.69, 0.44, 68), (2.7, 0.69, 0.44, 68)]}}
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
  sid=slot['id'];authorized('M14');model=R/progress['scenes'][sid]['path'];assert sha(model)==progress['scenes'][sid]['sha256'];dst=C/f'{sid}.mp4'
  old=next((r for r in previous['scenes'] if r['id']==sid),None)
  if old and sha(dst)==old['sha256']:records.append(old);continue
  n=slot['frames'];args=['-i',model]
  prep='[0:v]null[prepared];'
  if sid=='QG06':prep='[0:v]drawbox=x=0:y=875:w=1920:h=60:color=0x090D12:t=fill[prepared];'
  if sid in SHOTS:
   s=SHOTS[sid];src=SOURCES[s['source']];assert slot['gameWindowSeconds']==s['seconds'];annotations(sid,s)
   args+=['-ss',s['start'],'-t',s['seconds'],'-i',R/src['path']]
   offset=s.get('offset',0)
   graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),split=2[full][model];[model]crop=850:540:80:210,scale=620:394[small];color=c=0x090D12:s=1920x1080:r=60:d={slot["seconds"]}[bg];[1:v]fps=60,scale=1280:720:flags=lanczos,setsar=1,setpts=PTS+{offset}/TB[game];[bg][game]overlay=0:130:eof_action=pass[panel];[panel][small]overlay=1300:240,ass={sid}.guides.ass[split];[full][split]overlay=0:0:enable=\'between(t,{offset},{offset+s["seconds"]-1/60})\',setsar=1[v]'
  else:graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),setsar=1[v]'
  graph=prep+graph.replace('[0:v]','[prepared]')
  print('Compose M14',sid,'game + math' if sid in SHOTS else 'preserved math',flush=True)
  original_video=next(x for x in probe(model)['streams'] if x['codec_type']=='video')
  passthrough_ok=sid not in SHOTS and int(original_video['nb_frames'])==n and original_video['r_frame_rate']=='60/1' and original_video['width']==1920 and original_video['height']==1080 and float(original_video.get('start_time',0))==0
  if passthrough_ok:
   shutil.copy2(model,dst)
   assert sha(dst)==sha(model)
  else:
   ff(args+['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],f'composite-{sid}.log')
  v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==n and v['height']==1080 and v['r_frame_rate']=='60/1'
  record=dict(id=sid,path=rel(dst),sha256=sha(dst),frames=n,game=SHOTS.get(sid),visualReview='pending encoded captioned review',bytePreservedScene=passthrough_ok);records.append(record)
  save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=len(records)==24,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 assert len(records)==24
 save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=True,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 print('24 exact-frame compositions complete; final pair and QA pending',flush=True)
if __name__=='__main__':main()
