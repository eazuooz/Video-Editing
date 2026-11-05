"""Replace the twenty-seven Unity shots with actual Unreal plates, keeping gameplay at the original time and speed."""
from edit import *
from PIL import Image,ImageDraw,ImageFont
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
O=L/'picture';O.mkdir(exist_ok=True);ST=read(H/'stage-plan.json')['stages']
SOURCES={'motion-brief':'walk','motion-list':'turn','pose-versus-motion':'pose','walk-intent':'walk','attack-timing':'strike','pose-document':'pose','pose-connection':'stop','idle-intent':'walk','reference-transfer':'pose','joint-limit':'reach'}
specific={4:'turn',7:'walk',12:'walk',14:'reach',16:'strike',18:'strike',28:'walk',32:'pose',39:'turn',41:'stop',42:'reach',43:'reach',44:'reach',45:'turn',49:'turn',50:'stop',51:'turn',52:'stop',53:'turn'}
labels={
3:('어떻게 걸어야 할까?','느낌을 몸의 높이와 무릎 각도로 바꿔 적는다'),4:('목록 → 참고 포즈 → 검수','같은 동작을 함께 보며 지시를 구체화한다'),5:('사진 한 장과 이어지는 움직임','포즈는 한 순간, 애니메이션은 그 사이의 변화'),6:('같은 걷기라도','머리 높이 · 무릎 굽힘 · 팔의 위치'),7:('무엇을 만들지 목록에 적기','걷기와 몸을 낮춰 걷기를 다른 동작으로 기록'),9:('동작 길이와 판정 시간','설명용 시간표  /  60fps에서 12프레임은 0.2초'),12:('반복 재생   Loop','마지막 발 위치가 다음 첫걸음으로 이어지는지'),13:('어떤 자세를 원할까?','움직임의 이름 옆에 기준 자세를 붙인다'),14:('손을 뻗는 두 방향','어깨 높이와 팔꿈치 방향을 관찰'),15:('참고 포즈 한 장 만들기','같은 동작의 두 시점에서 발이 분리되는 쪽 선택'),16:('사진과 실제 동작','손과 어깨의 위치를 한 장에 표시'),18:('기준 포즈에서 앞뒤로','손을 뻗기 전과 힘을 거두는 자세'),28:('기다리는 자세의 인상','서 있는 높이와 팔의 긴장을 비교'),32:('사진에 남길 한 순간','발과 손이 겹치지 않는 방향을 선택'),33:('새 동작에 남길 특징','같은 첫걸음을 다른 방향에서 비교'),39:('한 장 사이를 채우는 일','발이 바닥을 디디고 몸이 돌아가는 순서'),41:('어느 발이 몸을 받을까?','왼발 정지와 오른발 정지 자료'),42:('관절 가동 범위','앞으로 뻗기와 위로 뻗기를 비교'),43:('같은 손끝, 다른 어깨 자세','어깨가 무너지거나 몸통과 겹치지 않는지'),44:('의도를 살리는 다른 자세','힘을 전달할 방향을 기준으로 수정'),45:('실제 속도로 검수','발을 디딘 뒤에 몸통이 따라오는가?'),49:('조작과 맞물리는 순간','방향을 바꾸기 시작하는 발을 확인'),50:('수정할 위치를 한 곳으로','왼발 또는 오른발을 정지의 기준으로 지정'),51:('지시와 결과를 나란히','같은 카메라에서 좌우 회전을 확인'),52:('팀에 남길 수정 기록','어느 발인지, 어느 자세에서 달라졌는지 기록'),53:('제작 지시 다시 읽기','동작 목록 · 포즈와 시간 · 완성 동작 검수'),54:('다음 작업으로 이어지는 자료','한 장과 실제 속도 영상을 같은 기준으로 남긴다')}
newLabels={'01':('막연한 걷기를 한 줄로 바꾸기','발을 디뎌도 머리 높이가 크게 솟지 않도록'),'02':('참고 포즈를 고르는 시점','어느 발이 먼저 나오는지 분명하게 보이는 방향'),'03':('마지막 발을 지정하기','멈추기 직전과 완전히 멈춘 뒤를 한 쌍으로'),'04':('방향 전환을 검수하기','어느 발을 디딘 뒤 몸통이 돌아가는지')}
@lru_cache(16)
def font(size,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('malgunbd.ttf' if b else 'malgun.ttf'),size)
def text(d,xy,value,size,color='#eeeee6',b=False):d.text(xy,value,font=font(size,b),fill=color,anchor='lt')
def src_stage(key):
 if key=='strike':
  return R/'projects/animation-exaggeration/production/local/fighters-v4-kula-lili/unreal/renders/A02-E004'
 return L/'unreal'/('final-renders' if key in ('stop','turn') else 'locked-renders')/key
@lru_cache(maxsize=48)
def panel(key,frame):
 folder=src_stage(key);img=Image.open(folder/f'{frame:06d}.png').convert('RGB')
 return img.crop((0,111,1920,900)).resize((1760,723),Image.Resampling.LANCZOS)
@lru_cache(maxsize=96)
def silhouette(key,frame,side):
 arr=np.asarray(panel(key,frame));offset=side*880
 rgb=arr[:,offset:offset+880].astype('int16')
 mask=(rgb[:,:,0]>rgb[:,:,1]+22)&(rgb[:,:,1]>rgb[:,:,2]+12)&(rgb[:,:,0]>120)
 y,x=np.nonzero(mask)
 if len(x)<900:return None
 return (int(np.quantile(x,.03))+offset,int(np.quantile(y,.015)),int(np.quantile(x,.97))+offset,int(np.quantile(y,.985)))
def focus(im,key,f,phase):
 if phase=='실제 속도' or key=='strike':return
 d=ImageDraw.Draw(im)
 for side in range(2):
  box=silhouette(key,f,side)
  if not box:continue
  x0,y0,x1,y1=box
  if key=='walk':
   yy=111+y0;d.line((78+x0-22,yy,78+x1+24,yy),fill='#276caa',width=7)
  elif key in ('pose','stop','turn'):
   # A bracket just below each visible pair of feet points to the support region.
   xx,yy=78+x0-9,min(817,119+y1)
   d.line([(xx,yy-18),(xx,yy),(78+x1+10,yy),(78+x1+10,yy-18)],fill='#186956',width=7)
def sample(s,key,local,headline,bottom):
 # First show the motion at original speed. Then use source-sampled frames to
 # study support, silhouette or the stopping pose in step with this explanation.
 n=s['frames'];duration=n/60;p=local/max(1,n-1);tm=local/60
 if local<120:f=local;phase='실제 속도'
 elif s['kind']=='added':
  # Cycle through distinct evidence: native-speed pass, slowed replay, then
  # three deliberately held poses. The original frame is shown on each hold.
  part=(local-120)%600
  if part<240:f=part//2;phase='느린 재생 · 0.5배'
  elif part<480:f=(18,57,96)[(part-240)//80];phase='참고 포즈 · '+str(f)+' F'
  else:f=part-480;phase='실제 속도'
 elif p<.66:f=round(16+62*(p/.66));phase='참고 포즈 분석'
 else:f=round(62+52*(p-.66)/.34);phase='마무리 자세'
 f=min(119,max(0,f))
 if key=='strike':f=min(156,round(f*1.3))
 im=Image.new('RGB',(1920,1080),'#111913');d=ImageDraw.Draw(im)
 text(d,(78,38),headline,57,'#f2d58a',True);text(d,(1345,54),'언리얼 · 게임 애니메이션 샘플',32,'#bfd3c5',True)
 im.paste(panel(key,f),(78,111));focus(im,key,f,phase)
 left,right=(ST[key]['left'],ST[key]['right']) if key in ST else ('기준이 되는 자세','팔과 몸통의 움직임')
 for x,label in [(112,left),(1050,right)]:
  ww=math.ceil(d.textlength(label,font=font(34,True)));d.rectangle((x,137,x+ww+39,199),fill='#1e3027');text(d,(x+17,150),label,34,'#ffffff',True)
 if s.get('mode')=='pose-versus-motion':
  frozen=panel(key,34);im.paste(frozen.crop((0,92,880,723)),(78,203));left='참고 포즈'
 if key=='strike' and s.get('mode')=='attack-timing':
  x,yy=151,766;d.rectangle((x,yy,x+1200,yy+20),fill='#58675c');d.rectangle((x+240,yy,x+480,yy+20),fill='#e5a680')
  text(d,(x+245,717),'가정한 판정 12 F',33,'#563a27',True)
 elif phase!='실제 속도':
  # The red floor line provides a fixed point of comparison in both camera views.
  d.rectangle((93,772,320,825),fill='#203127');text(d,(108,782),phase,28,'#f4e5bf',True)
 text(d,(80,851),bottom,39,'#f2f3eb',True)
 return im
enc=['-r','60','-c:v','h264_nvenc','-preset','p4','-cq','19','-b:v','0','-bf','0','-g','120','-pix_fmt','yuv420p','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709']
def cut(job):
 i,s=job;dst=O/f'cut-{i:03d}.mp4'
 if s['kind']=='old':
  master=B/'delivery/output'/P.name/(P.name+'.clean.mp4')
  ff(['-ss',s['oldStart']/60,'-threads','2','-i',master,'-frames:v',s['frames'],'-an','-vf','fps=60,setsar=1',*enc,dst],f'old-{i:03}')
  return
 if s['kind']=='added':key=s['study'];head,foot=newLabels[s['voice']]
 else:
  num=int(s['cut'].split('E')[-1]);key=specific.get(num,SOURCES[s['mode']]);head,foot=labels[num]
 with (O/f'cut-{i:03d}.log').open('wb') as log:
  proc=subprocess.Popen(['ffmpeg','-v','error','-y','-threads','2','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-an',*enc,str(dst)],stdin=subprocess.PIPE,stderr=log)
  try:
   last=None;buf=None
   for frame in range(s['frames']):
    marker=frame if frame<120 or s['kind']=='added' else (120+round((frame/max(1,s['frames']-1))*120))
    if marker!=last:buf=sample(s,key,frame,head,foot).tobytes();last=marker
    proc.stdin.write(buf)
  finally:proc.stdin.close()
  assert proc.wait()==0,dst
def main():
 timeline=read(L/'timeline.json');pieces=timeline['segments'];assert len([s for s in pieces if s['kind']=='added'])==4
 expected=[L/'unreal'/(key+('-final.mp4' if key in ('stop','turn') else '-inplace.mp4')) for key in ST]
 import time
 deadline=time.monotonic()+360
 while not all(p.is_file() for p in expected) and time.monotonic()<deadline:time.sleep(3)
 assert all(p.is_file() for p in expected)
 with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(cut,enumerate(pieces)))
 files=[]
 for i,s in enumerate(pieces):
  f=O/f'cut-{i:03d}.mp4';n=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','default=nw=1:nk=1',str(f)]));assert n==s['frames'],(f,n,s)
  files.append(f)
 listing=O/'parts.txt';listing.write_text(''.join("file '"+f.name+"'\n" for f in files),encoding='ascii')
 ff(['-f','concat','-safe','0','-i',listing,'-c','copy',L/'full-picture.mp4'],'full-picture')
 total=timeline['totalFrames'];args=['-filter_complex_threads','2','-threads','3','-i',L/'full-picture.mp4','-i',L/'audio.m4a','-filter_complex','[0:v]settb=1/60,setpts=N,split=2[c][in];[in]ass='+rel(L/'captions.ko.ass')+'[cc]']
 for tag,name in [('c','clean'),('cc','captioned')]:
  args+=['-map',f'[{tag}]','-map','1:a','-t',total/60,'-frames:v',total,*enc,'-c:a','copy','-movflags','+faststart',L/(name+'.mp4')]
 ff(args,'pair')
if __name__=='__main__':main()
