"""Edit licensed FHD recordings with speech-timed, editable Unity character studies."""
from assembly import H,P,R,L,read,save,sha,ff
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,subprocess,functools
from concurrent.futures import ThreadPoolExecutor
V=L/'picture';V.mkdir(parents=True,exist_ok=True);N=L/'native';G=L/'sources'
# Fractions are editorial priorities. The global target is distributed only
# across paragraphs that real gameplay can demonstrate, never the numeric example.
weights=[.9,.77,0,.70,.74,0,.96,.88,.43,.90,.78,0,.59,.53,0,0,0,.84,.73,.77,.34]
preferred=['great','duel','','great','great','','duel','great','duel','great','duel','','great','duel','','','','duel','great','great','duel']
pool={'great':[(1.7,9.0),(13.5,39.0),(44.0,60.5),(65.0,83.5),(86.,112.),(116.,139.),(141.,182.)],
      'duel':[(18.,40.),(43.,67.),(69.,87.),(89.,109.),(111.,131.),(133.,150.),(151.,160.)]}
names={'great':'몬스터 헌터 와일즈','duel':'슈퍼 스매시브라더스 얼티밋'}
def carve(slug,frames):
 # Carve one distinct normal-speed excerpt. A cut can continue in another
 # inspected interval, without wrapping or seeking into a previous excerpt.
 out=[]
 while frames:
  if not pool[slug]:raise ValueError('Insufficient distinct action for '+slug)
  a,b=pool[slug][0];available=int((b-a)*60);take=min(frames,available)
  if take<=0 or (take<100 and frames>take):pool[slug].pop(0);continue
  out.append((slug,a,take));frames-=take
  if take==available:pool[slug].pop(0)
  else:pool[slug][0]=(a+take/60,b)
 return out
def shots():
 t=read(L/'timeline.json');rows=t['paragraphs'];lengths=[r['f1']-r['f0'] for r in rows];target=round(.6*t['bodyFrames'])
 left,right=0.,3.
 for _ in range(36):
  m=(left+right)/2;total=sum(round(min(.96,w*m)*n) for n,w in zip(lengths,weights))
  if total<target:left=m
  else:right=m
 g=[round(min(.96,w*right)*n) for n,w in zip(lengths,weights)]
 g[0]+=target-sum(g)
 # A very short commentary-only insert between two related live cuts adds
 # little. Move that time to another useful gameplay paragraph instead.
 for i in range(len(g)):
  if g[i] and 0<lengths[i]-g[i]<80:
   delta=lengths[i]-g[i];g[i]+=delta;g[18]-=delta
 built=[]
 for ix,(row,n,game) in enumerate(zip(rows,lengths,g)):
  expl=n-game
  # Split long units into two observations of the same phenomenon, each with
  # a different source time. The Unity view bridges them on one clock.
  parts=max(1,round(n/560))
  if expl<100 or game<100:parts=1
  left_game=game;left_expl=expl;cursor=row['f0']
  for j in range(parts):
   gc=round(left_game/(parts-j));ec=round(left_expl/(parts-j));left_game-=gc;left_expl-=ec
   seq=[('game',gc),('unity',ec)]
   if ix in (3,8,10,13,17,19) and j==0:seq.reverse()
   for kind,count in seq:
    if not count:continue
    source=preferred[ix]
    for src,a,k in (carve(source,count) if kind=='game' else [('unity',j,count)]):
     built.append(dict(index=len(built)+1,paragraph=row['id'],chapter=row['chapter'],kind=kind,source=src,inPoint=a,frames=k,startFrame=cursor));cursor+=k
  assert cursor==row['f1']
 assert sum(s['frames'] for s in built)==t['bodyFrames'] and sum(s['frames'] for s in built if s['kind']=='game')==target
 evidence={}
 for key in names:
  movie=G/(key+'.mp4')
  streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(movie)]))['streams']
  stream=next(x for x in streams if x['codec_type']=='video')
  assert (stream['width'],stream['height'])==(1920,1080)
  evidence[key]={'url':read(G/(key+'.metadata.json'))['webpage_url'],'sha256':sha(movie),'width':stream['width'],'height':stream['height'],'sourceFps':stream['avg_frame_rate'],'originalStartSeconds':15 if key=='great' else 0,'nativeRateInFinal':1,'sourceAudioMuted':True}
 save(H/'edit-plan-final.json',{'totalFrames':t['totalFrames'],'bodyFrames':t['bodyFrames'],'gameFrames':target,'cuts':built,'sourceEvidence':evidence})
 return built
@functools.lru_cache(maxsize=24)
def font(px,heavy=False):return ImageFont.truetype('C:/Windows/Fonts/'+('malgunbd.ttf' if heavy else 'malgun.ttf'),px)
def label(d,xy,s,size,color='#f3f2eb',heavy=False):d.text(xy,s,font=font(size,heavy),fill=color,anchor='lt')
def tag(key):
 im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im);s=names[key];width=d.textlength(s,font=font(37,True))
 d.rectangle((48,40,100+width,108),fill=(6,18,16,228));d.rectangle((48,40,56,108),fill='#e7ca78');label(d,(74,55),s,37,heavy=True)
 im.save(V/(key+'-tag.png'))
def prepare_native():
 for name in ['ch1','ch2','ch3','ch4','ch5-early','ch5-wait','ch5-noinput','ch6']:
  movie=N/(name+'.mp4');path=V/name;path.mkdir(exist_ok=True);digest=sha(movie)
  token=path/'source.sha256'
  if token.exists() and token.read_text()==digest and len(list(path.glob('f-*.jpg')))==108:continue
  ff('-i',movie,'-fps_mode','passthrough','-start_number','0','-q:v','2',path/'f-%03d.jpg',log='extract-'+name)
  token.write_text(digest);assert len(list(path.glob('f-*.jpg')))==108
def shot_game(s,out):
 key=s['source'];src=G/(key+'.mp4')
 # The opening target was inspected at full size. Remove the mark at the
 # camera change; the fixed captions and game HUD keep their own positions.
 cfg='[0:v]fps=60,setsar=1[v];[v][1:v]overlay=0:0'
 if s['index']==1 and key=='great':
  cfg+=f",drawbox=x=470:y=245:w=505:h=650:t=7:c=0x6ee7b7:enable='between(t,0.15,{max(.2,4.36-s['inPoint']):.3f})'"
 marks={'great':[(46.2,46.85,790,452,208,220)],'duel':[(20.02,20.40,635,513,193,209),(20.78,20.85,604,241,206,242)]}
 for begin,end,x,y,w,h in marks[key]:
  lo=max(0.,begin-s['inPoint']);hi=min(s['frames']/60,end-s['inPoint'])
  if hi>lo:
   cfg+=f",drawbox=x={x}:y={y}:w={w}:h={h}:t=7:c=0x6ee7b7:enable='between(t,{lo:.3f},{hi:.3f})'"
 args=['-ss',s['inPoint'],'-threads','2','-i',src,'-i',V/(key+'-tag.png'),'-filter_complex_threads','2','-filter_complex',cfg+',format=yuv420p[out]','-map','[out]','-an','-frames:v',s['frames']]
 ff(*args,*encode,out,log='shot-'+str(s['index']))
encode=['-c:v','h264_nvenc','-preset','p4','-cq','18','-b:v','0','-bf','0','-g','120','-r','60','-pix_fmt','yuv420p','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
topics={
 1:('한 번의 공격을 나누면','대기 자세와 움직이는 세 단계','대기','준비 → 타격 → 후속'),
 2:('땅에서 출발하는 자세','대기 자세가 다음 동작의 출발점','대기 자세','준비가 시작된 자세'),
 3:('무엇을 고칠지 정하기','같은 검 동작의 서로 다른 구간','준비','타격'),
 4:('준비 동작   Anticipation','어깨와 검 끝이 먼저 바뀐다','시작 자세','휘두르기 직전'),
 5:('입력에 답하는 첫 자세','시작과 준비의 실루엣 차이','대기 자세','검을 들어 올린 자세'),
 6:('짧은 준비를 읽게 하는 법','검 끝이 차지하는 공간을 비교','시작','준비'),
 7:('공격을 예고하는 자세','입력한 사람과 피하는 사람이 받는 신호','상대가 보는 준비','검이 닿는 순간'),
 8:('타격 구간   Active frames','몸이 움직이는 시간과 실제 타격 구간','준비','충돌 발생'),
 9:('히트 스톱   Hit stop','명중한 순간 두 캐릭터가 같은 자세에 잠깐 머문다','접촉 직전','접촉 자세'),
 10:('후속 동작   Follow-through','검이 표적을 지난 뒤에도 움직임은 이어진다','타격','힘이 빠지는 궤적'),
 11:('회복 중의 자세   Recovery','같은 회복 구간을 어떤 자세로 채울까?','대기처럼 보이는 자세','힘이 남은 후속 자세'),
 12:('움직일 수 없는 동안','후속 자세로 방금 낸 힘의 방향을 남긴다','타격 직후','복귀 중'),
 13:('표현과 조작의 두 시계','자세의 복귀와 다음 입력 허용을 따로 본다','입력 대기','다음 행동 허용'),
 14:('다음 행동으로 전환하기','같은 검 동작에 같은 달리기 입력을 준다','끝까지 대기','먼저 달리기'),
 15:('캔슬 가능 프레임','허용된 다음 행동을 받아들이는 시점','48프레임에 허용','36프레임에 허용'),
 16:('48프레임과 36프레임','60fps  /  48 ÷ 60 = 0.8초    ·    36 ÷ 60 = 0.6초','0.8초 뒤 전환','0.6초 뒤 전환'),
 17:('애니메이션 길이와 조작 제한','같은 입력으로 확인한 0.2초의 차이','48프레임','36프레임'),
 18:('전환할 수 있는 행동','이번 시연에서 허용한 다음 행동은 달리기','아무 입력 없음','달리기 입력'),
 19:('제작 지시에 필요한 네 기준','대기 자세 · 공격 자세 · 판정 시작 · 다음 행동 허용','대기 자세','공격 자세'),
 20:('어떻게 휘두를 것인가','어깨의 회전과 검 끝의 높이를 함께 본다','들어 올린 검','표적을 지나는 검'),
 21:('공격 한 번을 다시 보면','준비에서 입력을 읽고, 타격 뒤에는 다음 행동을 읽는다','준비','후속 동작')}
@functools.lru_cache(maxsize=85)
def pane(key,frame):
 with Image.open(V/key/f'f-{frame:03}.jpg') as im:
  return im.crop((292,55,1627,956)).resize((825,557),Image.Resampling.LANCZOS)
def motion_frame(s,f):
 pid=int(s['paragraph']);chapter=int(s['chapter']);n=s['frames'];u=(f+.5)/n
 title,legend,ltext,rtext=topics[pid]
 compare=chapter==5
 if compare:
  left='ch5-noinput' if pid==18 else 'ch5-wait';right='ch5-early'
 else:left=right='ch'+str(chapter)
 # One replay, then a labelled phase inspection; no loop to extend run time.
 seq=int(s['inPoint'])
 keypairs={1:(18,32),2:(18,29),3:(29,32),4:(32,45),6:(29,32)}
 holdA,holdB=keypairs.get(chapter,(54,66))
 if compare:
  clock=round(18+min(75,76*u));fa=fb=clock
  if pid==16 and seq:clock=round(48+min(30,31*u));fa=fb=clock
 elif seq%2==0:
  fa=holdA;fb=int(min(84,max(0,12+u*80)))
 else:
  fa=int(min(84,12+u*80));fb=holdB
 if pid==11:fa=18;fb=round(37+20*u)
 image=Image.new('RGB',(1920,1080),'#101712');d=ImageDraw.Draw(image)
 label(d,(78,58),title,66,'#f2d787',True);label(d,(1494,77),'자체 Unity 시연',34,'#bdd3c5',True)
 image.paste(pane(left,fa),(78,185));image.paste(pane(right,fb),(1017,185))
 label(d,(80,137),ltext,33,'#91d0b8',True);label(d,(1018,137),rtext,33,'#f2cd89',True)
 if not compare:
  rec=traces[right][fb];x0,x1=80,1840;y=778
  meter(d,x0,x1,y,rec['simulationFrame'])
  state_names={'standby':'대기','lead-in':'준비','attack':'타격','follow-through':'후속','idle':'대기','run':'달리기'}
  name='히트 스톱' if rec['freezeLeft']>0 else state_names[rec['state']]
  label(d,(1042,691),name+'   /   '+str(rec['simulationFrame'])+' F',32,'#163625',True)
 else:
  for x,key,fr in [(78,left,fa),(1017,right,fb)]:
   rec=traces[key][fr];meter(d,x,x+825,774,rec['simulationFrame'])
   if rec['transitionAccepted']:label(d,(x+492,692),'달리기 시작',33,'#0c3c30',True)
 label(d,(80,831),legend,42,'#f1f0e8',True)
 return image
def meter(d,x0,x1,y,frame):
 for a,b,name,col in [(0,12,'준비','#82cec0'),(12,18,'타격','#ed9583'),(18,48,'후속','#d8c87e')]:
  xx=x0+(x1-x0)*a/48;end=x0+(x1-x0)*b/48;d.rectangle((xx,y,end-3,y+16),fill=col)
 pt=x0+(x1-x0)*min(48,frame)/48;d.polygon([(pt,y-4),(pt-10,y-19),(pt+10,y-19)],fill='#ffffff')
traces={}
def render(s):
 out=V/f"shot-{s['index']:03}.mp4"
 if s['kind']=='game':shot_game(s,out);return
 cmd=['ffmpeg','-hide_banner','-v','error','-y','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0','-an',*encode,str(out)]
 with (V/f"shot-{s['index']:03}.log").open('wb') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   last=None;cached=None
   for f in range(s['frames']):
    # The teaching state advances at most one native pose per tick.
    state=round((f+.5)/s['frames']*80)
    if state!=last:cached=motion_frame(s,f).tobytes();last=state
    proc.stdin.write(cached)
  finally:proc.stdin.close()
  if proc.wait():raise RuntimeError('Native shot encode failed: '+str(s['index']))
def main():
 grant=read(R/'shared/publishing/video-production-control.json')['scopedProductionAuthorizations'][P.name];assert grant['renderAuthorized']
 assert (N/'complete.txt').is_file()
 for k in names:tag(k)
 prepare_native()
 for f in N.glob('ch*.json'):traces[f.stem]=read(f)['samples']
 for key,threshold in [('ch5-early',36),('ch5-wait',48)]:assert next(x for x in traces[key] if x['transitionAccepted'])['simulationFrame']==threshold
 assert not any(x['transitionAccepted'] for x in traces['ch5-noinput'])
 assert next(x for x in traces['ch3'] if x['hit'])['contactFrame']==14
 plan=shots()
 with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(render,plan))
 files=[V/f"shot-{s['index']:03}.mp4" for s in plan]
 for p,s in zip(files,plan):
  frames=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','default=nw=1:nk=1',str(p)]))
  assert frames==s['frames'],(p,frames,s['frames'])
 (V/'concat.txt').write_text(''.join("file '"+p.name+"'\n" for p in files),encoding='ascii')
 ff('-f','concat','-safe','0','-i',V/'concat.txt','-c','copy',L/'body.mp4',log='join-body')
 print('Body',len(files),'shots',flush=True)
if __name__=='__main__':main()
