"""Native-speed, individually reviewed object manipulation beside the reused math model."""
from common import *
import sys,math,shutil
P=R/'projects/game-math-polygon-centers-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
T=read(H/'timeline.json');authorized('M13');C=O/'composite';C.mkdir(exist_ok=True)
SOURCES={'dorf': {'path': 'shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm', 'url': 'https://www.toukana.com/dorfromantik/presskit', 'game': 'Dorfromantik', 'minimumHeight': 1080}, 'tinyA': {'path': 'shared/output/private-math-concept-fit-20261023/sources/tiny-glade-official/release-date-trailer.mp4', 'url': 'https://pouncelight.games/tiny-glade/', 'game': 'Tiny Glade', 'minimumHeight': 1080}, 'tinyB': {'path': 'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-256965562.mp4', 'url': 'https://store.steampowered.com/app/2198150/Tiny_Glade/', 'game': 'Tiny Glade', 'minimumHeight': 1080, 'sourceSilent': True}}
SHOTS={'02': {'source': 'dorf', 'start': 21, 'seconds': 7, 'title': '타일을 돌리고 빈자리에 배치', 'phases': [(0, 2, '한 타일: 가운데와 바깥 변'), (2, 7, '타일 추가 → 연결된 영역의 변화')], 'model': '한 점의 기준 / 바깥선의 전체', 'track': [(0.1, 0.49, 0.49, 60), (1.5, 0.49, 0.49, 60)]}, '11': {'source': 'dorf', 'start': 117, 'seconds': 4, 'title': '타일 하나와 전체 땅의 윤곽', 'phases': [(0, 4, '추가 · 되돌리기 → 남는 땅과 빈자리')], 'model': '볼록한 조각 / 전체의 홈', 'track': [], 'contours': [[(0.05, [(688, 736), (820, 710), (840, 630)]), (0.8, [(688, 736), (820, 710), (840, 630)])]]}, 'QG01': {'source': 'tinyA', 'start': 12, 'seconds': 6, 'title': '건물을 놓고 폭과 높이 조절', 'phases': [(0, 1.5, '놓을 위치 선택'), (1.5, 6, '외곽선이 바뀌는 부분 확인')], 'model': '같은 기준점 / 달라지는 외곽', 'track': [(1.5, 0.54, 0.64, 86), (2, 0.54, 0.61, 86), (2.5, 0.5, 0.64, 90), (3, 0.48, 0.66, 90), (4, 0.48, 0.66, 90), (5.8, 0.48, 0.65, 90)]}, 'QG02': {'source': 'tinyB', 'start': 1, 'seconds': 9.8, 'title': '벽을 고치고 빈 통로 만들기', 'phases': [(0, 5, '벽을 지워 열린 공간 확인'), (5, 7.5, '벽을 다시 그리기'), (7.5, 9.8, '길을 이으면 아치형 통로가 생김')], 'model': '남은 벽 / 제외할 빈 통로', 'track': [(8.5, 0.438, 0.7, 54), (9.7, 0.438, 0.7, 54)]}, 'QG03': {'source': 'tinyB', 'start': 23, 'seconds': 5, 'title': '같은 건물 아래의 땅 높이 변경', 'phases': [(0, 2, '건물 아래의 지면 확인'), (2, 5, '지면 높이 변화 · 실제 높이 수치 미측정')], 'model': '높이가 다른 표면 / 평면의 오목한 홈', 'track': [], 'contours': [[(2.5, [(925, 800), (1145, 845), (1360, 800)]), (3, [(925, 780), (1145, 835), (1360, 780)]), (3.5, [(925, 760), (1145, 815), (1360, 760)]), (4, [(925, 760), (1145, 815), (1360, 760)]), (4.8, [(925, 760), (1145, 815), (1360, 760)])]]}}
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
  sid=slot['id'];authorized('M13');model=R/progress['scenes'][sid]['path'];assert sha(model)==progress['scenes'][sid]['sha256'];dst=C/f'{sid}.mp4'
  old=next((r for r in previous['scenes'] if r['id']==sid),None)
  if old and sha(dst)==old['sha256']:records.append(old);continue
  n=slot['frames'];args=['-i',model]
  prep='[0:v]null[prepared];'
  if sid in SHOTS:
   s=SHOTS[sid];src=SOURCES[s['source']];assert slot['gameWindowSeconds']==s['seconds'];annotations(sid,s)
   args+=['-ss',s['start'],'-t',s['seconds'],'-i',R/src['path']]
   offset=s.get('offset',0)
   graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),split=2[full][model];[model]crop=850:540:80:210,scale=620:394[small];color=c=0x090D12:s=1920x1080:r=60:d={slot["seconds"]}[bg];[1:v]fps=60,scale=1280:720:flags=lanczos,setsar=1,setpts=PTS+{offset}/TB[game];[bg][game]overlay=0:130:eof_action=pass[panel];[panel][small]overlay=1300:240,ass={sid}.guides.ass[split];[full][split]overlay=0:0:enable=\'between(t,{offset},{offset+s["seconds"]-1/60})\',setsar=1[v]'
  else:graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),setsar=1[v]'
  graph=prep+graph.replace('[0:v]','[prepared]')
  print('Compose M13',sid,'game + math' if sid in SHOTS else 'preserved math',flush=True)
  original_video=next(x for x in probe(model)['streams'] if x['codec_type']=='video')
  passthrough_ok=sid not in SHOTS and int(original_video['nb_frames'])==n and original_video['r_frame_rate']=='60/1' and original_video['width']==1920 and original_video['height']==1080 and float(original_video.get('start_time',0))==0
  if passthrough_ok:
   shutil.copy2(model,dst)
   assert sha(dst)==sha(model)
  else:
   ff(args+['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],f'composite-{sid}.log')
  v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==n and v['height']==1080 and v['r_frame_rate']=='60/1'
  record=dict(id=sid,path=rel(dst),sha256=sha(dst),frames=n,game=SHOTS.get(sid),visualReview='pending encoded captioned review',bytePreservedScene=passthrough_ok);records.append(record)
  save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=len(records)==25,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 assert len(records)==25
 save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=True,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 print('25 exact-frame compositions complete; final pair and QA pending',flush=True)
if __name__=='__main__':main()
