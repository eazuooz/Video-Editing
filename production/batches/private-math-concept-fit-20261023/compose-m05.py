"""Native-speed, individually reviewed object manipulation beside the reused math model."""
from common import *
import sys,math,shutil
P=R/'projects/game-math-quaternion-foundations-v3';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
T=read(H/'timeline.json');authorized('M05');C=O/'composite';C.mkdir(exist_ok=True)
SOURCES={'totk': {'path': 'projects/game-math-euler-axis-angle/production/local/revision-v3/sources/YNQ20CKbY8U-hls.mp4', 'url': 'https://www.youtube.com/watch?v=YNQ20CKbY8U', 'game': '젤다의 전설: 왕국의 눈물', 'minimumHeight': 1080}, 'se2': {'path': 'shared/output/private-math-concept-fit-20261023/sources/se2-official/vs1.2.mp4', 'url': 'https://mirror.keenswh.com/PressKits/SE2%20Press%20Kit.zip', 'game': 'Space Engineers 2', 'minimumHeight': 2160}, 'dorf': {'path': 'shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm', 'url': 'https://www.toukana.com/dorfromantik/presskit', 'game': 'Dorfromantik', 'minimumHeight': 1080}}
SHOTS={'02': {'source': 'totk', 'start': 418.0, 'seconds': 18.0, 'title': '통나무를 돌려 다리로 놓기', 'note': '움직이는 위치와 긴 방향을 구분', 'phases': [(0, 5, '통나무를 잡아 들어 올리기'), (5, 13, '건너편으로 옮겨 위치 조절'), (13, 16, '긴 방향을 돌려 다리와 맞추기'), (16, 18, '통나무를 내려 다리로 배치')], 'track': [(15, 0.41, 0.39, 82), (16, 0.41, 0.39, 82)], 'model': '앞쪽과 위쪽 · 자체 모형'}, 'GA01': {'source': 'se2', 'start': 101.0, 'seconds': 11.0, 'title': '부품을 복사해 배치하기', 'note': '위치와 면의 방향을 구분', 'phases': [(0, 3, '복사할 부품을 선택'), (3, 6, '배치 미리보기의 앞면·옆면'), (6, 11, '다른 위치로 옮겨 배치')], 'track': [(4, 0.57, 0.42, 103), (5, 0.58, 0.42, 103), (6, 0.59, 0.42, 103), (7, 0.6, 0.42, 103)], 'model': '위치 이동 / 축 방향'}, 'QF30': {'source': 'dorf', 'start': 38.0, 'seconds': 6.0, 'title': '타일을 돌려 주변 지도에 배치', 'note': '타일의 집 방향을 관찰', 'phases': [(0, 2, '선택한 타일을 놓을 곳 찾기'), (2, 4, '집이 있는 타일의 방향 바꾸기'), (4, 6, '주변 타일과 맞춰 배치')], 'track': [(2, 0.51, 0.61, 91), (3, 0.53, 0.6, 91), (4, 0.42, 0.56, 91)], 'model': '타일 회전 · 자체 모형'}}
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
 label(0,d,1320,818,'각도는 자체 계산 예시' if sid=='QF30' else 'X 앞 / Y 옆 / Z 위',28,'A7B0BC')
 for a,b,txt in s['phases']:label(a,b,36,852,txt,35,'80D3A2')
 # Each tracked mark is screen-space editorial guidance, never game telemetry.
 for track in [s.get('track',[]),s.get('track2',[])]:
  for one,two in zip(track,track[1:]):
   a,x,y,r=one;b,x2,y2,r2=two;cx=x*1280;cy=130+y*720;dx=x2*1280;dy=130+y2*720
   k=r*.55228475
   # Non-negative drawing coordinates + explicit top-left avoid libass bbox offset.
   shape=f'm 0 {r} b 0 {r-k} {r-k} 0 {r} 0 b {r+k} 0 {2*r} {r-k} {2*r} {r} b {2*r} {r+k} {r+k} {2*r} {r} {2*r} b {r-k} {2*r} 0 {r+k} 0 {r}'
   event(a,b,'{\\an7\\move('+f'{cx-r:.1f},{cy-r:.1f},{dx-r:.1f},{dy-r:.1f}'+')\\p1\\bord5\\shad0\\1a&HFF&\\3c&HA2D380&}'+shape,1)
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
  sid=slot['id'];authorized('M05');model=R/progress['scenes'][sid]['path'];assert sha(model)==progress['scenes'][sid]['sha256'];dst=C/f'{sid}.mp4'
  old=next((r for r in previous['scenes'] if r['id']==sid),None)
  if old and sha(dst)==old['sha256']:records.append(old);continue
  n=slot['frames'];args=['-i',model]
  # Enlarging only our authored model viewport improves mobile readability.
  # Text, axis legend, source game pixels and timing are not enlarged or moved.
  enlarge=progress['scenes'][sid]['origin']=='concept-matched own model' and sid not in ['GA05','GA02','11','N05']
  prep='[0:v]split=2[base][modelcrop];[modelcrop]crop=620:450:230:300,scale=868:630:flags=lanczos[big];[base]drawbox=x=80:y=200:w=870:h=620:color=0x090d12:t=fill[clear];[clear][big]overlay=106:190[prepared];' if enlarge else '[0:v]null[prepared];'
  if sid in SHOTS:
   s=SHOTS[sid];src=SOURCES[s['source']];assert slot['gameWindowSeconds']==s['seconds'];annotations(sid,s)
   args+=['-ss',s['start'],'-t',s['seconds'],'-i',R/src['path']]
   offset=s.get('offset',0)
   graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),split=2[full][model];[model]crop=850:650:80:210,scale=620:474[small];color=c=0x090D12:s=1920x1080:r=60:d={slot["seconds"]}[bg];[1:v]fps=60,scale=1280:720:flags=lanczos,setsar=1,setpts=PTS+{offset}/TB[game];[bg][game]overlay=0:130:eof_action=pass[panel];[panel][small]overlay=1300:240,ass={sid}.guides.ass[split];[full][split]overlay=0:0:enable=\'between(t,{offset},{offset+s["seconds"]-1/60})\',setsar=1[v]'
  else:graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),setsar=1[v]'
  graph=prep+graph.replace('[0:v]','[prepared]')
  print('Compose M05',sid,'game + math' if sid in SHOTS else 'preserved math',flush=True)
  ff(args+['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],f'composite-{sid}.log')
  v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==n and v['height']==1080 and v['r_frame_rate']=='60/1'
  record=dict(id=sid,path=rel(dst),sha256=sha(dst),frames=n,game=SHOTS.get(sid),visualReview='pending encoded captioned review');records.append(record)
  save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=len(records)==50,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 assert len(records)==50
 save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=True,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 print('50 exact-frame compositions complete; final pair and QA pending',flush=True)
if __name__=='__main__':main()
