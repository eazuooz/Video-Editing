"""A10 sentence052: qualitative arm-length-only illustration, original clock.

No UE/game measurement is claimed. Shoulders, body, camera and joint angles
are invariant; only the right upper/lower arm lengths change together.
"""
from pathlib import Path
import argparse,hashlib,json,math,subprocess,os
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parents[1];R=H.parents[3]
O=Path('C:/Users/1/Videos/YamyamProduction/animation-contrast-v5-work/visual-corrections/A10')
A,B=19070,19573;N=B-A;FPS=60
BG='#080c0a';WHITE='#f3f2ec';YELLOW='#f2d787';TEAL='#81cfc5';RED='#f18b81';MUTED='#a9b2ac'
FONT={}
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.pending');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(tmp,p)
def rel(p):
 try:return Path(p).resolve().relative_to(R.resolve()).as_posix()
 except ValueError:return Path(p).resolve().as_posix()
def text(d,xy,s,size=42,fill=WHITE):
 if size not in FONT:FONT[size]=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size)
 d.text(xy,s,font=FONT[size],fill=fill)
def dashed(d,a,b,fill,width=3,dash=15):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 if not length:return
 for k in range(0,int(length),dash*2):
  p=k/length;q=min(length,k+dash)/length;d.line((a[0]+dx*p,a[1]+dy*p,a[0]+dx*q,a[1]+dy*q),fill=fill,width=width)
def limb(d,a,b,width,fill):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*width/2,dx/length*width/2
 d.polygon([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)],fill=fill)
 for x,y in (a,b):d.ellipse((x-width/2,y-width/2,x+width/2,y+width/2),fill=fill)
def hand(d,wrist,angle,color):
 u=(math.cos(angle),math.sin(angle));v=(-u[1],u[0])
 def pt(t,n):return(wrist[0]+u[0]*t+v[0]*n,wrist[1]+u[1]*t+v[1]*n)
 d.polygon([pt(0,-10),pt(0,10),pt(26,12),pt(30,-11)],fill=color)
 for side,end in [(-8,44),(-2,49),(4,47),(10,40)]:limb(d,pt(19,side),pt(end,side),5,color)
 limb(d,pt(8,-8),pt(27,-21),7,color)
def person(d,cx,length_scale,accent):
 # Identical non-arm body coordinates in both panels.
 hip=(cx,707);head=(cx,385);shoulder=(cx+70,545)
 for side in (-1,1):
  limb(d,(cx+side*34,702),(cx+side*44,770),38,'#879791')
  limb(d,(cx+side*44,770),(cx+side*52,839),31,'#b8c3be')
  d.rounded_rectangle((cx+side*52-22,829,cx+side*52+39,854),radius=10,fill='#dce2dd')
 d.polygon([(cx-24,470),(cx-67,515),(cx-82,560),(cx-58,688),(cx-48,714),(cx+48,714),(cx+58,688),(cx+82,560),(cx+67,515),(cx+24,470)],fill='#bcc8c1')
 d.line((cx,522,cx,691),fill='#81928a',width=3)
 d.line((cx-46,681,cx+46,681),fill='#7a8e83',width=4)
 d.rounded_rectangle((cx-21,433,cx+21,480),radius=12,fill='#d1d9d2')
 d.ellipse((cx-56,329,cx+56,441),fill='#dce3dc',outline='#81928a',width=3)
 # Recognizable face, neutral and identical.
 for x in (cx-19,cx+19):d.ellipse((x-4,370,x+4,378),fill='#53685c')
 d.line((cx,379,cx-4,396,cx+4,396),fill='#6c8175',width=3)
 d.arc((cx-18,392,cx+18,418),5,175,fill='#6c8175',width=3)
 limb(d,(cx-70,545),(cx-96,626),31,'#b4c3b9');limb(d,(cx-96,626),(cx-78,704),27,'#ccd6cc')
 hand(d,(cx-78,704),math.radians(80),'#ccd6cc')
 ua,fa=math.radians(-55),math.radians(-80)
 elbow=(shoulder[0]+110*length_scale*math.cos(ua),shoulder[1]+110*length_scale*math.sin(ua))
 wrist=(elbow[0]+95*length_scale*math.cos(fa),elbow[1]+95*length_scale*math.sin(fa))
 limb(d,shoulder,elbow,32,'#dce3dc');limb(d,elbow,wrist,27,'#dce3dc');hand(d,wrist,fa,'#dce3dc')
 d.line((*shoulder,*elbow,*wrist),fill=accent,width=5)
 for x,y in (shoulder,elbow,wrist):d.ellipse((x-8,y-8,x+8,y+8),fill=BG,outline=accent,width=4)
 # Identical arcs denote angles without numerical or game-measured claims.
 d.arc((shoulder[0]-36,shoulder[1]-36,shoulder[0]+36,shoulder[1]+36),-55,0,fill=YELLOW,width=4)
 return {'shoulder':shoulder,'elbow':elbow,'wrist':wrist,'scale':length_scale}
def frame(f):
 t=f/FPS;u=min(1,max(0,(t-3.1)/2.2));u=u*u*(3-2*u)
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 text(d,(58,38),'같은 각도, 다른 팔 길이',64,YELLOW);text(d,(1535,55),'설명용 도식',34,MUTED)
 text(d,(62,125),'어깨 위치 · 관절 각도 · 보는 방향 고정',37,MUTED)
 text(d,(250,210),'짧은 팔',43,TEAL);text(d,(1125,210),'팔 길이만 변경',43,RED)
 d.line((960,210,960,865),fill='#26342b',width=2)
 for lo,hi in [(140,840),(1040,1740)]:
  dashed(d,(lo,545),(hi,545),'#52635a',2)
 left=person(d,400,1,TEAL);right=person(d,1300,1+.63*u,RED)
 for info,x,accent in [(left,800,TEAL),(right,1700,RED)]:
  w=info['wrist'];dashed(d,w,(x,w[1]),accent,3,12)
  d.line((x,w[1],x,545),fill=accent,width=4)
  d.polygon([(x,w[1]),(x-7,w[1]+14),(x+7,w[1]+14)],fill=accent)
  d.polygon([(x,545),(x-7,531),(x+7,531)],fill=accent)
 text(d,(619,367),'얼굴 옆',37,TEAL)
 if u>.7:text(d,(1550,282),'머리 위',37,RED)
 text(d,(610,552),'어깨 높이',30,MUTED);text(d,(1510,552),'어깨 높이',30,MUTED)
 return im,{'left':left,'right':right,'jointAnglesDegrees':[-55,-80],'onlyVariable':'right upper/lower arm length'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');args=ap.parse_args();O.mkdir(parents=True,exist_ok=True)
 control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert 'A10'in control['episodes']and control['renderAuthorized']
 for f in [0,186,285,400,N-1]:
  im,_=frame(f);im.save(O/f'design-{f:03}.png');im.resize((375,211),Image.Resampling.LANCZOS).save(O/f'design-{f:03}-375.png')
 source=R/'projects/animation-damage-animations/production/contrast-v5'
 scripts={lang:read(source/f'final.{lang}.json')for lang in ['ko','en']}
 timing=H/'baseline-sentence-timing.json';s=next(x for x in read(timing)['records']if x['id']=='A10')['sentences'];sentence=next(x for x in s if x['id']=='052')
 assert round(sentence['startSeconds']*60)==A and round(sentence['endSeconds']*60)<=B
 e=next(x for x in read(H/'renderer/integration-caption-safe.json')['episodes']if x['id']=='A10')
 underlying=[x['id']for x in e['rows']if max(A,x['relationFrameStart'])<min(B,x['relationFrameEnd'])]
 assert underlying==['A10-cut-046']
 design={'episode':'A10','oldClockRange':[A,B],'frames':N,'sentenceIds':['052'],'ko':next(x['lines']for x in scripts['ko']['scenes']if x['id']=='052'),'en':next(x['lines']for x in scripts['en']['scenes']if x['id']=='052'),'reason':'The former torso-rotation/fall picture did not show the narrated arm-length variable.','fixed':['shoulder height','body proportions apart from raised arm length','joint angles','camera/view','hand size'],'varied':'right arm length only, qualitatively short to long','sourceKind':'independently authored articulated diagram, not UE measurement or manipulated gameplay','timing':'first3.1sec same short arm, next2.2sec continuously extend right arm, retain resulting comparison','captionSafeBottomY':870,'samples':[{'frame':f,'geometry':frame(f)[1]}for f in [0,186,285,400,N-1]],'newAudio':False}
 save(H/'visual-corrections/A10-plan.json',design)
 if not args.render:return
 video=O/'A10-correction-019070-019573-arm-length.mp4';sig={'sourceCodeSha256':sha(__file__),'frames':N,'design':design}
 receipt=video.with_suffix('.json');old=read(receipt)if receipt.exists()else{}
 if not(video.exists()and old.get('signature')==sig and old.get('sha256')==sha(video)):
  temp=video.with_suffix('.pending.mp4')
  with video.with_suffix('.log').open('wb')as log:
   p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','-','-an','-frames:v',str(N),'-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-bf','0','-pix_fmt','yuv420p','-r','60','-video_track_timescale','60000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(temp)],stdin=subprocess.PIPE,stderr=log,stdout=log,creationflags=subprocess.CREATE_NO_WINDOW)
   for f in range(N):p.stdin.write(frame(f)[0].tobytes())
   p.stdin.close();assert p.wait()==0
  os.replace(temp,video);save(receipt,{'signature':sig,'sha256':sha(video),'frames':N,'modelVisualReview':'Design frames inspected separately; final encoded and caption preview QA recorded separately.'})
 v=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(video)],creationflags=subprocess.CREATE_NO_WINDOW))['streams'][0]
 assert(v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',N)
 row={'id':video.stem,'kind':'authored-explanation','startFrame':A,'endFrame':B,'newFrames':N,'picture':rel(video),'pictureSha256':sha(video),'sourceStartFrame':0,'sourceVerified':True,'expectedUnderlyingExplanationIds':underlying,'narrationEvidence':{'path':rel(timing),'sha256':sha(timing),'sentenceIds':['052']},'reason':design['reason'],'mediaSegments':[{'kind':'authored-explanation','offsetFrame':0,'frames':N,'sourceKey':'A10-arm-length-illustration','sourceLocalIn':None,'sourceLocalOut':None,'sourceSha256':sha(__file__),'nativeFrames':0}],'visualEvidence':design,'captionSafeBottomY':870,'newAudio':False,'newTts':False,'receipt':rel(receipt)}
 save(H/'visual-corrections/A10.json',{'schemaVersion':1,'episode':'A10','clock':'relations-v4','readyForAssembly':True,'pictureEdits':[row],'sourceCode':rel(__file__),'sourceCodeSha256':sha(__file__),'preservesExistingNativeGamePlates':True,'nativeGameplayFramesAdded':0,'retainsUsefulNarrationAndOrder':True,'humanFullWatch':False,'modelVisualReview':'Encoded actual-caption preview QA must be recorded before parent handoff.'})
 print(json.dumps({'file':str(video),'sha256':sha(video),'frames':N}),flush=True)
if __name__=='__main__':main()
