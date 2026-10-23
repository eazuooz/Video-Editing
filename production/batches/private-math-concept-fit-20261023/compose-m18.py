"""Native-speed, individually reviewed object manipulation beside the reused math model."""
from common import *
import sys,math,shutil
P=R/'projects/game-math-projection-depth';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
T=read(H/'timeline.json');authorized('M18');C=O/'composite';C.mkdir(exist_ok=True)
SOURCES={'town': {'path': 'shared/output/game-math-part2-full-series/sources/FRfnXAIbA-M.mp4', 'audioPath': 'shared/output/private-math-concept-fit-20261023/sources/m16-audio/FRfnXAIbA-M.mp4', 'url': 'https://www.youtube.com/watch?v=FRfnXAIbA-M', 'game': 'Townscaper', 'minimumHeight': 1080}, 'tinyB': {'path': 'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-256965562.mp4', 'url': 'https://store.steampowered.com/app/2198150/Tiny_Glade/', 'game': 'Tiny Glade', 'minimumHeight': 1080, 'sourceSilent': True}}
SHOTS={'03': {'scene': '03', 'source': 'town', 'start': 1205, 'seconds': 6, 'offset': 0, 'title': '새 건물이 뒤 난간을 가림', 'phases': [(0, 6, '새 지붕·벽과 기존 난간 구분')], 'model': '가까운 지붕 / 뒤의 면', 'track': [], 'track2': []}, '06': {'scene': '06', 'source': 'tinyB', 'start': 13.5, 'seconds': 5, 'offset': 0, 'title': '기울어진 지붕에 붙은 무늬', 'phases': [(0, 5, '면의 경계와 반복 무늬를 함께 보기')], 'model': '표면 격자 / 원근 보간', 'track': [], 'track2': []}, '09-view': {'scene': '09', 'source': 'town', 'start': 1507.2, 'seconds': 2.4, 'offset': 0, 'title': '같은 테라스의 모서리 찾기', 'phases': [(0, 2.4, '나무와 모서리를 함께 기준으로 보기')], 'model': '같은 기준점 / 관찰 방향', 'track': [], 'track2': []}, '09-build': {'scene': '09', 'source': 'town', 'start': 1492, 'seconds': 5, 'offset': 17.959999999999997, 'title': '새 벽과 지붕이 생기는 순간', 'phases': [(0, 5, '시점 변화와 구조 편집은 다른 조건')], 'model': '새 블록 / 기존 기준점', 'track': [], 'track2': []}}
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
  sid=slot['id'];authorized('M18');model=R/progress['scenes'][sid]['path'];assert sha(model)==progress['scenes'][sid]['sha256'];dst=C/f'{sid}.mp4'
  old=next((r for r in previous['scenes'] if r['id']==sid),None)
  if old and sha(dst)==old['sha256']:records.append(old);continue
  n=slot['frames'];args=['-i',model]
  selected=[(key,v) for key,v in SHOTS.items() if v['scene']==sid]
  assert abs(sum(v['seconds'] for key,v in selected)-slot['gameWindowSeconds'])<.001
  for key,shot in selected:
   assert shot['offset']+shot['seconds']<=slot['seconds']
  prep='[0:v]null[prepared];'
  if sid in ['03','06','09']:
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
  print('Compose M18',sid,'game + math' if selected else 'preserved math',flush=True)
  original_video=next(x for x in probe(model)['streams'] if x['codec_type']=='video')
  passthrough_ok=not selected and int(original_video['nb_frames'])==n and original_video['r_frame_rate']=='60/1' and original_video['width']==1920 and original_video['height']==1080 and float(original_video.get('start_time',0))==0
  if passthrough_ok:
   shutil.copy2(model,dst)
   assert sha(dst)==sha(model)
  else:
   ff(args+['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],f'composite-{sid}.log')
  v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==n and v['height']==1080 and v['r_frame_rate']=='60/1'
  record=dict(id=sid,path=rel(dst),sha256=sha(dst),frames=n,game=[v for key,v in selected],visualReview='pending encoded captioned review',bytePreservedScene=passthrough_ok);records.append(record)
  save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=len(records)==10,guideFrame='screen-space editorial; own spatial illustration uses a z-up pinhole projection; preserved numeric lesson explicitly uses row vectors / left-handed view +z / depth0..1',nativePlayback=True,sourceAspectPreserved=True))
 assert len(records)==10
 save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=True,guideFrame='screen-space editorial; own spatial illustration uses a z-up pinhole projection; preserved numeric lesson explicitly uses row vectors / left-handed view +z / depth0..1',nativePlayback=True,sourceAspectPreserved=True))
 print('10 exact-frame compositions complete; final pair and QA pending',flush=True)
if __name__=='__main__':main()
