"""Editable ASS direction annotations on silent crops; no delivery approval."""
from pathlib import Path
import cv2,hashlib,json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3';O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/action-drafts'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
def stamp(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
def arrow(a,b):
 import numpy as np
 a=np.asarray(a);b=np.asarray(b);v=b-a;length=np.linalg.norm(v)
 if length<24:return ''
 u=v/length;n=np.array([-u[1],u[0]]);p=[a+6*n,b-24*u+6*n,b-24*u+15*n,b,b-24*u-15*n,b-24*u-6*n,a-6*n]
 return 'm '+' l '.join(f'{x:.1f} {y:.1f}' for x,y in p)
def write_overlay(stem,target=None,red_at=0,blue_at=0):
 d=json.loads((R/(stem+'-screen-track.json')).read_text(encoding='utf8'));events=[]
 def event(start,end,text,style='Text',layer=2):events.append(f'Dialogue: {layer},{stamp(start)},{stamp(end)},{style},,0,0,0,,{text}')
 duration=len(d['frames'])/60
 names={'trail':'트레일메이커스 · 비행 중 자세 변화','gear-v3':'스페이스 엔지니어스 · 부품 방향 바꾸기','besiege':'비시지 · 선택 부품 회전'}
 event(0,duration,r'{\an7\pos(24,28)}'+names[stem])
 notes={'trail':'화면 관찰선 · 실측 각도 아님','gear-v3':'세워진 모습 ≠ 완전히 같은 자세','besiege':'회전 후의 이동 조작과 구분'}
 event(0,duration,r'{\an7\pos(24,88)}'+notes[stem])
 # Labels follow actual line visibility instead of floating over hidden cuts.
 for f in d['frames']:
  if not f or not f['visible']:continue
  t=f['frame']/60;end=min(duration,t+1/60);p=f['points']
  if t>=red_at:
   shape=arrow(*p[:2])
   if shape:event(t,end,r'{\an7\pos(0,0)\p1}'+shape+r'{\p0}',style='Red',layer=1)
  if len(p)==4 and t>=blue_at:
   shape=arrow(*p[2:])
   if shape:event(t,end,r'{\an7\pos(0,0)\p1}'+shape+r'{\p0}',style='Blue',layer=1)
  if t>=red_at:event(t,end,r'{\an7\pos(24,146)}'+d['semantics']['redLabel'].replace('두 끝을 잇는 방향','방향'),style='RedText')
  if d['semantics']['blueLabel'] and t>=blue_at:event(t,end,r'{\an7\pos(24,204)}'+d['semantics']['blueLabel'],style='BlueText')
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Text,Malgun Gothic,38,&H00202020,&H00202020,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,3,9,0,7,0,0,0,1
Style: RedText,Malgun Gothic,38,&H003F44B7,&H003F44B7,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,3,9,0,7,0,0,0,1
Style: BlueText,Malgun Gothic,38,&H00AA5F2F,&H00AA5F2F,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,3,9,0,7,0,0,0,1
Style: Red,Malgun Gothic,38,&H003F44B7,&H003F44B7,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1
Style: Blue,Malgun Gothic,38,&H00AA5F2F,&H00AA5F2F,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 out=target or O/(stem+'-annotations.ass');out.write_text(header+'\n'.join(events)+'\n',encoding='utf8');return out
if __name__=='__main__':
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
 for stem in (sys.argv[1:] or ['trail','gear-v3','besiege']):
  assert stem in ['trail','gear-v3','besiege']
  ass=write_overlay(stem);src=O/(stem+'-unannotated.mp4');dst=O/(stem+'-annotated-draft.mp4');relative=ass.relative_to(ROOT).as_posix()
  subprocess.run([str(FF),'-hide_banner','-loglevel','error','-y','-i',str(src),'-vf','ass='+relative,'-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','3',str(dst)],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  c=cv2.VideoCapture(str(dst));times=list(range(0,int(c.get(cv2.CAP_PROP_FRAME_COUNT)),60))
  for page,i in enumerate(range(0,len(times),8),1):
   sheet=Image.new('RGB',(1280,1568),'white');draw=ImageDraw.Draw(sheet)
   for k,frame in enumerate(times[i:i+8]):
    c.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,img=c.read();assert ok;x=k%2*640;y=k//2*392
    sheet.paste(Image.fromarray(cv2.cvtColor(cv2.resize(img,(640,360)),cv2.COLOR_BGR2RGB)),(x,y+32));draw.text((x+4,y+4),f'{stem} proposed overlay {frame/60:g}s',font=font,fill='black')
   sheet.save(O/f'{stem}-annotated-page-{page}.jpg',quality=95)
  c.release();print(stem,'annotated silent draft; direct moving alignment pending',flush=True)
