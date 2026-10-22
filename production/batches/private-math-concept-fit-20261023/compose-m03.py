"""Native-speed, individually reviewed object manipulation beside the reused math model."""
from common import *
import sys,math,shutil
P=R/'projects/game-math-orientation-matrices';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
T=read(H/'timeline.json');authorized('M03-original');C=O/'composite';C.mkdir(exist_ok=True)
SOURCES={
 'totk':dict(path='projects/game-math-euler-axis-angle/production/local/revision-v3/sources/YNQ20CKbY8U-hls.mp4',url='https://www.youtube.com/watch?v=YNQ20CKbY8U',game='젤다의 전설: 왕국의 눈물',minimumHeight=1080),
 'besiege':dict(path='shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/sources/besiege-uWKEJ92486U.mp4',url='https://www.youtube.com/watch?v=uWKEJ92486U',game='Besiege · 비시즈',minimumHeight=1440)}
SHOTS={
 '02':dict(source='totk',start=996.,seconds=14.,title='위치와 자세는 서로 다른 정보',note='돛을 세우고 붙이기',phases=[(0,4,'바닥에 누운 돛'),(4,7,'들어 올리기 → 위치 변화'),(7,11,'세우기 → 자세 변화'),(11,14,'통나무에 붙이기')],track=[(0,.65,.57,65),(3,.62,.56,65),(4,.59,.50,65),(5,.51,.25,65),(6,.50,.20,65)],track2=[(9,.51,.29,55),(10,.50,.32,55),(11,.50,.32,55)],model='돛과 함께 움직이는 축'),
 '05':dict(source='besiege',start=59.,seconds=11.,title='물체의 위쪽과 고정된 위쪽',note='선택한 부품만 회전',phases=[(0,4,'주황색 = 선택된 부품'),(4,8,'주변은 고정 · 선택 부품만 회전'),(8,11,'부품의 위쪽도 함께 바뀜')],track=[(0,.53,.58,78),(2,.51,.54,78),(4,.50,.50,78),(6,.49,.48,78),(8,.50,.51,78),(10,.51,.53,78)],model='실선: 물체 / 점선: 고정 기준'),
 '08':dict(source='totk',start=237.5,seconds=9.,title='물체의 앞을 월드에서 표현하기',note='고리를 세워 붙이기',phases=[(0,2.5,'고리를 잡고 들어 올리기'),(2.5,6.5,'고리를 세우기'),(6.5,9,'판에 붙이기')],track=[(3,.50,.22,54),(4,.50,.29,54),(5,.50,.34,54),(6,.50,.36,54)],model='설명에서는 열린 쪽을 앞으로 정함'),
 '11':dict(source='besiege',start=36.5,seconds=5.,title='물체를 고정하고 시점만 변경',note='정면에서 위쪽으로 관찰',phases=[(0,2,'같은 조립 물체'),(2,5,'시점 변화 → 화면 모양 변화')],track=[],model='고정된 물체 · 움직이는 카메라')}
ENC=['-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-video_track_timescale','60000']
SHOTS['02']['offset']=2.5
SHOTS['02']['track']=[(0,.60,.66,90),(3,.60,.64,90)]
# The game's native highlight carries the moving selection after pickup.
# An approximate screen circle drifted onto the background during camera motion.
SHOTS['02']['track2']=[]
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
 label(0,d,1320,818,'X   Y   Z = 물체의 축',28,'A7B0BC')
 for a,b,txt in s['phases']:label(a,b,36,852,txt,35,'80D3A2')
 # Each tracked mark is screen-space editorial guidance, never game telemetry.
 for track in [s.get('track',[]),s.get('track2',[])]:
  for one,two in zip(track,track[1:]):
   a,x,y,r=one;b,x2,y2,r2=two;cx=x*1280;cy=130+y*720;dx=x2*1280;dy=130+y2*720
   k=r*.55228475
   shape=f'm {-r} 0 b {-r} {-k} {-k} {-r} 0 {-r} b {k} {-r} {r} {-k} {r} 0 b {r} {k} {k} {r} 0 {r} b {-k} {r} {-r} {k} {-r} 0'
   event(a,b,'{\\an5\\move('+f'{cx:.1f},{cy:.1f},{dx:.1f},{dy:.1f}'+')\\p1\\bord5\\shad0\\1a&HFF&\\3c&HA2D380&}'+shape,1)
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
  sid=slot['id'];authorized('M03-original');model=R/progress['scenes'][sid]['path'];assert sha(model)==progress['scenes'][sid]['sha256'];dst=C/f'{sid}.mp4'
  old=next((r for r in previous['scenes'] if r['id']==sid),None)
  if old and sha(dst)==old['sha256']:records.append(old);continue
  n=slot['frames'];args=['-i',model]
  if sid in SHOTS:
   s=SHOTS[sid];src=SOURCES[s['source']];assert slot['gameWindowSeconds']==s['seconds'];annotations(sid,s)
   args+=['-ss',s['start'],'-t',s['seconds'],'-i',R/src['path']]
   offset=s.get('offset',0)
   graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),split=2[full][model];[model]crop=850:650:80:210,scale=620:474[small];color=c=0x090D12:s=1920x1080:r=60:d={slot["seconds"]}[bg];[1:v]fps=60,scale=1280:720:flags=lanczos,setsar=1,setpts=PTS+{offset}/TB[game];[bg][game]overlay=0:130:eof_action=pass[panel];[panel][small]overlay=1300:240,ass={sid}.guides.ass[split];[full][split]overlay=0:0:enable=\'between(t,{offset},{offset+s["seconds"]-1/60})\',setsar=1[v]'
  else:graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),setsar=1[v]'
  print('Compose M03',sid,'game + math' if sid in SHOTS else 'preserved math',flush=True)
  ff(args+['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],f'composite-{sid}.log')
  v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==n and v['height']==1080 and v['r_frame_rate']=='60/1'
  record=dict(id=sid,path=rel(dst),sha256=sha(dst),frames=n,game=SHOTS.get(sid),visualReview='pending encoded captioned review');records.append(record)
  save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=len(records)==24,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 assert len(records)==24
 save(receipt,dict(identity=identity,updatedAt=now(),sources=sources,scenes=records,completed=True,guideFrame='screen-space editorial; only the own model uses right-handed column-vector coordinates',nativePlayback=True,sourceAspectPreserved=True))
 print('24 exact-frame compositions complete; final pair and QA pending',flush=True)
if __name__=='__main__':main()
