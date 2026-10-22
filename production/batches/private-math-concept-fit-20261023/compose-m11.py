"""Native-speed, individually reviewed object manipulation beside the reused math model."""
from common import *
import sys,math,shutil
P=R/'projects/game-math-plane-distances-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
T=read(H/'timeline.json');authorized('M11');C=O/'composite';C.mkdir(exist_ok=True)
SOURCES={'polybridge3': {'path': 'shared/output/private-math-concept-fit-20261023/sources/polybridge-official/release-trailer.mp4', 'url': 'https://store.steampowered.com/app/1850160/Poly_Bridge_3/', 'game': 'Poly Bridge 3', 'minimumHeight': 1080}}
SHOTS={'02': {'source': 'polybridge3', 'start': 8, 'seconds': 3.5, 'title': '차량이 놓인 다리의 표면', 'phases': [(0, 3.5, '초록 선: 유한한 다리 표면의 앞쪽 경계')], 'model': '유한한 표면 / 계산용 평면', 'track': [], 'track2': [], 'contours': [[(0.2, [(771, 590), (1219, 559)]), (0.5, [(775, 590), (1220, 552)]), (1.5, [(755, 582), (1210, 562)]), (2.5, [(741, 574), (1205, 577)]), (3.4, [(738, 568), (1200, 585)])]]}, 'PG02': {'source': 'polybridge3', 'start': 17, 'seconds': 2.8, 'title': '다리가 열리며 표면이 기울어짐', 'phases': [(0, 2.8, '초록 선: 왼쪽 다리 표면의 앞쪽 경계')], 'model': '면의 회전 / 함께 변하는 법선', 'track': [], 'track2': [], 'contours': [[(0.8, [(716, 726), (798, 729), (965, 687)]), (1, [(716, 726), (798, 731), (948, 675)]), (1.5, [(713, 724), (794, 727), (903, 673)]), (2, [(709, 718), (786, 725), (868, 683)]), (2.5, [(708, 710), (780, 721), (855, 686)]), (2.75, [(706, 704), (776, 715), (853, 683)])]]}, '08': {'source': 'polybridge3', 'start': 5.8, 'seconds': 2.1, 'title': '연결점 세 개로 삼각형 만들기', 'phases': [(0, 1.5, '연결점을 놓고 선으로 이어 붙이기'), (1.5, 2.1, '초록 윤곽: 완성된 삼각형 한 개')], 'model': '직접 정한 A · B · C / 둘레 순서', 'track': [], 'track2': [], 'contours': [[(1.5, [(773, 688), (861, 556), (949, 688), (773, 688)]), (2.09, [(773, 688), (861, 556), (949, 688), (773, 688)])]]}}
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
  sid=slot['id'];authorized('M11');model=R/progress['scenes'][sid]['path'];assert sha(model)==progress['scenes'][sid]['sha256'];dst=C/f'{sid}.mp4'
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
  print('Compose M11',sid,'game + math' if sid in SHOTS else 'preserved math',flush=True)
  original_video=next(x for x in probe(model)['streams'] if x['codec_type']=='video')
  passthrough_ok=sid not in SHOTS and int(original_video['nb_frames'])==n and original_video['r_frame_rate']=='60/1' and original_video['width']==1920 and original_video['height']==1080 and float(original_video.get('start_time',0))==0
  if passthrough_ok:
   shutil.copy2(model,dst)
   assert sha(dst)==sha(model)
  else:
   ff(args+['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],f'composite-{sid}.log')
  v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==n and v['height']==1080 and v['r_frame_rate']=='60/1'
  record=dict(id=sid,path=rel(dst),sha256=sha(dst),frames=n,game=SHOTS.get(sid),visualReview='pending encoded captioned review',bytePreservedScene=passthrough_ok);records.append(record)
  save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=len(records)==19,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 assert len(records)==19
 save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=True,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 print('19 exact-frame compositions complete; final pair and QA pending',flush=True)
if __name__=='__main__':main()
