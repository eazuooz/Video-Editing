"""Native-speed, individually reviewed object manipulation beside the reused math model."""
from common import *
import sys,math,shutil
P=R/'projects/game-math-lines-circles-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
T=read(H/'timeline.json');authorized('M09');C=O/'composite';C.mkdir(exist_ok=True)
SOURCES={'grapple': {'path': 'shared/output/private-game-math-polish-20261022/fhd-candidates/5u3sUKuncSU.mp4', 'audioPath': 'shared/output/private-math-concept-fit-20261023/sources/uncle-5u3sUKuncSU-audio.m4a', 'url': 'https://www.youtube.com/watch?v=5u3sUKuncSU', 'game': 'A Story About My Uncle', 'minimumHeight': 1080}, 'factory': {'path': 'shared/output/private-math-concept-fit-20261023/sources/satisfactory-official/SATISFACTORY_1.2_LAUNCHTRAILER_MASTER.mp4', 'url': 'https://www.satisfactorygame.com/press/', 'game': 'Satisfactory', 'minimumHeight': 1440}}
SHOTS={'02': {'source': 'grapple', 'start': 407, 'seconds': 12.5, 'title': '보이는 연결의 두 끝점', 'phases': [(0, 5, '밝은 연결을 먼저 확인'), (5, 10, '초록: 손 쪽 시작 · 파랑: 반대쪽 끝'), (10, 12.5, '빠른 이동에서는 표식을 걷고 연결을 관찰')], 'model': '두 점의 관계 · 계산용 선분', 'track': [(5, 0.69, 0.66, 44), (5.5, 0.68, 0.6, 44), (6, 0.68, 0.62, 44), (6.5, 0.68, 0.65, 44), (7, 0.67, 0.61, 44), (7.5, 0.68, 0.62, 44), (8, 0.68, 0.66, 44), (8.5, 0.68, 0.64, 44), (9, 0.68, 0.63, 44), (9.5, 0.68, 0.64, 44), (10, 0.69, 0.66, 44)], 'track2': [(5, 0.597, 0.288, 32), (5.5, 0.51, 0.386, 32), (6, 0.54, 0.27, 32), (6.5, 0.565, 0.19, 32), (7, 0.547, 0.195, 32), (7.5, 0.467, 0.2, 32), (8, 0.472, 0.28, 32), (8.5, 0.495, 0.29, 32), (9, 0.508, 0.23, 32), (9.5, 0.435, 0.145, 32), (10, 0.432, 0.26, 32)]}, 'LG01': {'source': 'factory', 'start': 71.5, 'seconds': 4.0, 'title': '배선은 연결되는 두 지점부터', 'phases': [(0, 1.0, '배선할 장치와 접점 선택'), (1.0, 3.5, '접점 선택 → 연결 미리보기'), (3.5, 4.0, '연결 결과를 계산용 선분과 비교')], 'model': '곡선 모양 · 직선 연결은 별개', 'track': [(1, 0.51, 0.3, 34), (1.25, 0.51, 0.31, 34), (1.5, 0.51, 0.31, 34), (1.75, 0.51, 0.3, 34), (1.83, 0.51, 0.3, 34)], 'track2': []}}
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
 label(0,d,1320,818,'게임 거리·힘의 측정값 아님',28,'A7B0BC')
 for a,b,txt in s['phases']:label(a,b,36,852,txt,35,'80D3A2')
 # Each tracked mark is screen-space editorial guidance, never game telemetry.
 for ti,track in enumerate([s.get('track',[]),s.get('track2',[])]):
  for one,two in zip(track,track[1:]):
   a,x,y,r=one;b,x2,y2,r2=two;cx=x*1280;cy=130+y*720;dx=x2*1280;dy=130+y2*720
   k=r*.55228475
   # Non-negative drawing coordinates + explicit top-left avoid libass bbox offset.
   shape=f'm 0 {r} b 0 {r-k} {r-k} 0 {r} 0 b {r+k} 0 {2*r} {r-k} {2*r} {r} b {2*r} {r+k} {r+k} {2*r} {r} {2*r} b {r-k} {2*r} 0 {r+k} 0 {r}'
   event(a,b,'{\\an7\\move('+f'{cx-r:.1f},{cy-r:.1f},{dx-r:.1f},{dy-r:.1f}'+')\\p1\\bord5\\shad0\\1a&HFF&\\3c&H'+('A2D380' if ti==0 else 'FFB778')+'&}'+shape,1)
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
  sid=slot['id'];authorized('M09');model=R/progress['scenes'][sid]['path'];assert sha(model)==progress['scenes'][sid]['sha256'];dst=C/f'{sid}.mp4'
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
  print('Compose M09',sid,'game + math' if sid in SHOTS else 'preserved math',flush=True)
  original_video=next(x for x in probe(model)['streams'] if x['codec_type']=='video')
  passthrough_ok=sid not in SHOTS and int(original_video['nb_frames'])==n and original_video['r_frame_rate']=='60/1' and original_video['width']==1920 and original_video['height']==1080 and float(original_video.get('start_time',0))==0
  if passthrough_ok:
   shutil.copy2(model,dst)
   assert sha(dst)==sha(model)
  else:
   ff(args+['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],f'composite-{sid}.log')
  v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==n and v['height']==1080 and v['r_frame_rate']=='60/1'
  record=dict(id=sid,path=rel(dst),sha256=sha(dst),frames=n,game=SHOTS.get(sid),visualReview='pending encoded captioned review',bytePreservedScene=passthrough_ok);records.append(record)
  save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=len(records)==18,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 assert len(records)==18
 save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=True,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 print('18 exact-frame compositions complete; final pair and QA pending',flush=True)
if __name__=='__main__':main()
