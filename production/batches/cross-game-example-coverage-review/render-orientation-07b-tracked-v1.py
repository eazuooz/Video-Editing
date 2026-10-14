"""One CPU2/GPU0 measured bike scene; native actions plus projected explanation."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,math,os,re,subprocess,traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='2'
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-07b-tracked-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
FONTS={n:ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',n) for n in (24,26,28,30,34,38,48,52)}
RED='#e64045';TEAL='#22b5aa';BLUE='#3e7ecb';DARK='#23313d'
def text(d,xy,s,c=DARK,n=30):
 box=d.textbbox(xy,s,font=FONTS[n]);assert box[2]<1900 and box[3]<900
 d.text(xy,s,font=FONTS[n],fill=c)
def label(d,xy,s,c,n=28):
 box=d.textbbox(xy,s,font=FONTS[n]);assert box[2]+10<1900 and box[3]+10<900
 d.rounded_rectangle((box[0]-9,box[1]-5,box[2]+9,box[3]+9),radius=5,fill=(15,19,23,226));d.text(xy,s,font=FONTS[n],fill=c)
def arrow(d,a,b,c,w=6):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 if length<9:return
 d.line((tuple(a),tuple(b)),fill=c,width=w);ux,uy=dx/length,dy/length
 d.polygon([tuple(b),(b[0]-17*ux+8*uy,b[1]-17*uy-8*ux),(b[0]-17*ux-8*uy,b[1]-17*uy+8*ux)],fill=c)

def observed(source,p):
 if any(a*60<=source<b*60 for a,b in p['hideSourceSeconds']):return None
 for a,b in zip(p['anchors'],p['anchors'][1:]):
  if a['sourceFrame']<=source<=b['sourceFrame']:
   if not a['visible'] or not b['visible'] or b['sourceFrame']-a['sourceFrame']>31:return None
   u=(source-a['sourceFrame'])/(b['sourceFrame']-a['sourceFrame'])
   return {k:[a[k][i]+u*(b[k][i]-a[k][i]) for i in (0,1)] for k in ('nose','tail','wingA','wingB')}
 return None
def gameplay(im,frame,source,seg,p):
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);sec=frame/60
 label(d,(1210,90),'Trailmakers · 조립 비행기','#ffffff',28)
 if seg['kind']=='takeoff':label(d,(1210,150),'활주로에서 떠나는 실제 행동','#ffe16b',28)
 elif seg['kind']=='next-view-return':label(d,(1210,150),'다음 시점 · 날개의 기울기 비교','#ffe16b',28)
 elif seg['kind'].startswith('related'):label(d,(1210,150),'다른 고유 구간 · 두 선을 함께 비교','#ffe16b',26)
 elif seg['kind'].startswith('camera'):label(d,(1210,150),'다른 카메라 시점 · 화면 관찰','#ffe16b',28)
 else:label(d,(1210,150),'앞과 날개 방향을 나누어 보기','#ffe16b',28)
 blue=sec>=8.76;red=sec>=16.7166666667
 if red:label(d,(1210,220),'빨강: 기체의 앞을 가리키는 선',RED,26)
 if blue:label(d,(1210,275),'파랑: 날개 양쪽을 잇는 선',BLUE,26)
 label(d,(1210,340),'화면 관찰용 · 월드축/회전각 측정 아님','#ffffff',24)
 obs=observed(source,p)
 if obs and blue:
  a,b=obs['wingA'],obs['wingB'];d.line((tuple(a),tuple(b)),fill='#111822',width=10);d.line((tuple(a),tuple(b)),fill=BLUE,width=6)
 if obs and red and math.dist(obs['tail'],obs['nose'])>=55:
  a,b=obs['tail'],obs['nose'];d.line((tuple(a),tuple(b)),fill='#111822',width=11);arrow(d,a,b,RED,6)
 assert layer.getbbox()[3]<900
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB'),obs
def model(frame,p):
 im=Image.new('RGB',(1920,1080),'#fafbf9');d=ImageDraw.Draw(im);sec=frame/60;late=frame>=1891
 local=sec-(1891/60 if late else 742/60)
 theta=math.pi/2*min(1,max(0,(local-.3)/1.3)) if late else .32*math.sin(local*1.15)
 scale=240;center=(815,555)
 def rotate(v):
  x,y,z=v;c,s=math.cos(theta),math.sin(theta);return (c*x-s*y,s*x+c*y,z)
 def proj(v):
  x,y,z=rotate(v);return (center[0]+scale*(.79*x-.61*z),center[1]+scale*(.32*x-.80*y+.41*z))
 def depth(v):
  x,y,z=rotate(v);return .49*x+.57*y+.66*z
 for k in range(-4,5):
  for a,b in [((k/2,-.8,-2),(k/2,-.8,2)),((-2,-.8,k/2),(2,-.8,k/2))]:
   def floor(v):
    x,y,z=v;return (center[0]+scale*(.79*x-.61*z),center[1]+scale*(.32*x-.80*y+.41*z))
   d.line((floor(a),floor(b)),fill='#dce4df',width=2)
 faces=[]
 def box(x0,x1,y0,y1,z0,z1,top,side):
  v=[(x,y,z) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)]
  for ids,col in [([0,1,3,2],side),([4,6,7,5],side),([0,4,5,1],side),([2,3,7,6],top),([0,2,6,4],side),([1,5,7,3],side)]:
   vv=[v[i] for i in ids];faces.append((sum(depth(t) for t in vv)/4,vv,col))
 box(-.20,.20,-.22,.22,-1.2,1.5,'#e3c56a','#af8a35')
 box(-1.65,1.65,.25,.36,-.05,.40,'#b7cce5','#637d9d')
 box(-.75,.75,.18,.28,-1.22,-.9,'#9bb4d2','#566c88')
 box(-.06,.06,.28,.70,-1.2,-.8,'#c1d2e6','#637d9d')
 for _,vv,col in sorted(faces,key=lambda x:x[0]):d.polygon([proj(v) for v in vv],fill=col,outline=DARK,width=2)
 origin=(0,.43,.25)
 red=late or sec>=13.1;blue=late or sec>=14.2
 if red:arrow(d,proj(origin),proj((0,.43,1.9)),RED,8)
 if blue:d.line((proj((-1.8,.43,.25)),proj((1.8,.43,.25))),fill=BLUE,width=9)
 text(d,(85,80),'앞과 날개를 함께 읽는 자세',DARK,48)
 text(d,(85,155),'따로 정한 설명모형 · 실제 게임 내부 축의 측정이 아닙니다',DARK,30)
 if red:text(d,(1330,390),'앞 f · 붉은 방향',RED,34)
 if blue:text(d,(1330,465),'날개 양쪽 · 파란 방향',BLUE,34)
 if not late and sec>=15.72:text(d,(1270,570),'두 방향을 함께 비교',DARK,34)
 if late:
  text(d,(1130,570),'별도 수학 예: z축 +90°',DARK,34)
  text(d,(1160,645),'x → y,  y → −x,  z → z',DARK,30)
  text(d,(1150,715),'Rz = [[0,−1,0],[1,0,0],[0,0,1]]',DARK,28)
 text(d,(85,842),'게임의 회전각을 수치로 추정하지 않습니다. 카메라와 물체의 움직임을 구분하세요.','#64716a',26)
 return im
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
 sp=O/'07b-tracked-render-execution-v1.json';assert not sp.exists() and not LOCAL.exists()
 planp=O/'07b-observation-track-plan-v1.json';p=read(planp);r=read(ROOT/args.resource)
 assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
 assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
 t=read(O/'narration-07b-guide-repair-execution-v1.json');protected=t['protectedInputs']+t['results']
 for x in protected:assert sha(ROOT/x['path'])==x['sha256']
 assert sha(ROOT/p['source'])==p['sourceSha256'] and sha(ROOT/p['voice']['path'])==p['voice']['sha256']
 for x in p['anchors']:assert sha(ROOT/x['path'])==x['sha256']
 LOCAL.mkdir(parents=True);me=psutil.Process();target=LOCAL/'07b.tracked.silent.mp4'
 state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,resource=args.resource,resourceSha256=sha(ROOT/args.resource),plan=rel(planp),planSha256=sha(planp),cpuThreads=2,gpuJobs=0,frames=p['frames'],writtenFrames=0,status='07b-measured-tracking-rendering',actualOuterExitCode=None,newImageGit=0,newTts=0,allBetweenFramesApproved=False,finalCueApproved=False,finalRatioApproved=False)
 save(sp,state);cp=read(O/'latest-checkpoint.json');cp.update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(O/'latest-checkpoint.json',cp)
 q=read(B/'queue.json');q['currentOrientationReview'].update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(B/'queue.json',q)
 enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v',str(p['frames']),'-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(target)]
 tracks=[];decoders=[]
 try:
  with (LOCAL/'encode.log').open('wb') as el:
   ep=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT);state.update(encodePid=ep.pid,encodeCreateTime=psutil.Process(ep.pid).create_time(),encodeCommand=enc);save(sp,state)
   for num,seg in enumerate(p['segments']):
    start,end=seg['frameIn'],seg['frameOut'];n=end-start
    if seg['classification']=='actual':
     ni,no=seg['nativeIn'],seg['nativeOutExclusive'];assert no-ni==n
     dec=[FF,'-hide_banner','-nostdin','-v','info','-threads','1','-filter_threads','1','-ss',str(ni/60),'-copyts','-i',str(ROOT/p['source']),'-an','-vf',f'trim=start_pts={ni*256}:end_pts={no*256},showinfo','-frames:v',str(n),'-pix_fmt','rgb24','-f','rawvideo','pipe:1']
     log=LOCAL/f'decode-{num}.log'
     with log.open('wb') as dl:
      dp=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT);info=dict(pid=dp.pid,createTime=psutil.Process(dp.pid).create_time(),command=dec,nativeIn=ni,nativeOutExclusive=no,log=rel(log));decoders.append(info);state['decoders']=decoders;save(sp,state)
      for f in range(start,end):
       raw=dp.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3
       im=Image.frombytes('RGB',(1920,1080),raw);out,obs=gameplay(im,f,ni+f-start,seg,p);ep.stdin.write(out.tobytes());tracks.append(dict(frame=f,nativeFrame=ni+f-start,classification='actual',observation=obs))
       if f%120==0:state['writtenFrames']=f+1;save(sp,state)
      assert dp.stdout.read(1)==b'';dp.stdout.close();dx=dp.wait();assert dx==0
     pts=[int(v) for v in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',log.read_text('utf-8',errors='replace'))];assert pts==[i*256 for i in range(ni,no)]
     info.update(exitCode=dx,exactNativePtsMatched=True);save(sp,state)
    else:
     for f in range(start,end):
      ep.stdin.write(model(f,p).tobytes());tracks.append(dict(frame=f,classification='explanation',kind='projected-illustrative-bike-model'))
      if f%120==0:state['writtenFrames']=f+1;save(sp,state)
   ep.stdin.close();ex=ep.wait();assert ex==0
  save(LOCAL/'track.json',dict(planSha256=state['planSha256'],frames=tracks))
  probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,time_base,nb_frames,duration','-of','json',str(target)],text=True))
  assert probe['streams'][0]['time_base']=='1/90000' and int(probe['streams'][0]['nb_frames'])==p['frames']
  with (LOCAL/'whole-decode.log').open('wb') as l:dx=subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(target),'-f','null','-'],stdout=l,stderr=subprocess.STDOUT).returncode
  assert dx==0
  for x in protected:assert sha(ROOT/x['path'])==x['sha256']
  state.update(status='07b-render-complete-awaiting-encoded-pixel-review',workerExitCode=0,finishedAt=now(),writtenFrames=p['frames'],encodeExitCode=ex,wholeDecodeExitCode=dx,all1630NativePtsMatched=True,output=rel(target),outputSha256=sha(target),probe=probe,protectedShaMatched=True);save(sp,state)
  print(json.dumps(dict(workerExitCode=0,frames=p['frames'],nativeFrames=1630,output=rel(target))),flush=True)
 except BaseException as e:
  state.update(status='failed',workerExitCode=1,error=repr(e),traceback=traceback.format_exc(),finishedAt=now());save(sp,state);raise
if __name__=='__main__':main()
