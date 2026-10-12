"""One CPU2/GPU0 measured bike scene; native actions plus projected explanation."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,math,os,re,subprocess,traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='2'
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-03b-tracked-v1'
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
   if not a['visible'] or not b['visible']:return None
   u=(source-a['sourceFrame'])/(b['sourceFrame']-a['sourceFrame'])
   return {k:[a[k][i]+u*(b[k][i]-a[k][i]) for i in (0,1)] for k in ('head','hip')}
 return None
def gameplay(im,frame,source,seg,p):
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
 label(d,(1200,118),'Descenders · 화면 관찰','#ffffff',28)
 if seg['kind']=='road':
  label(d,(1200,180),'산길의 이동과 기울기를 나누어 보기','#ffe16b',28)
  if frame/60>=6.84:
   label(d,(1200,245),'청록 점: 화면 속 위치',TEAL,26)
   label(d,(1200,299),'빨강: 몸의 기울기 관찰선',RED,26)
 else:
  label(d,(1200,180),'다음 점프: 바퀴의 위아래를 보세요','#ffe16b',28)
  if seg['kind']=='second-jump-observation':
   label(d,(1200,245),'다른 점프에서도 뒤집힘 → 착지','#ffffff',26)
  else:label(d,(1200,245),'위로 뒤집힌 뒤, 착지 전 아래로','#ffffff',26)
 label(d,(1200,360),'화면 투영 · 게임 월드축 측정 아님','#ffffff',24)
 obs=observed(source,p)
 if obs and frame/60>=6.84:
  hip=obs['hip'];head=obs['head'];x,y=hip
  d.ellipse((x-13,y-13,x+13,y+13),outline='#071519',width=7);d.ellipse((x-10,y-10,x+10,y+10),outline=TEAL,width=4)
  # Only an observed head/hip line; not a rigid bike axis or measured roll.
  d.line((tuple(hip),tuple(head)),fill='#071519',width=9);d.line((tuple(hip),tuple(head)),fill=RED,width=5)
 assert layer.getbbox()[3]<900
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB'),obs
def model(frame,p):
 im=Image.new('RGB',(1920,1080),'#fafbf9');d=ImageDraw.Draw(im)
 late=frame>=1270;sec=frame/60
 # Orthographic 3D projection of an illustrative bike; not a simulated game.
 local=max(0,sec-21.166666667) if late else sec
 pitch=math.pi*min(1,max(0,(local-.25)/2.2)) if late else .25*math.sin(local*1.8)
 shift=70*math.sin(local*.7) if not late else 0
 center=(920+shift,600);scale=260
 def rotate(v):
  x,y,z=v;c,s=math.cos(pitch),math.sin(pitch);return (x*c+z*s,y,-x*s+z*c)
 def proj(v):
  x,y,z=rotate(v);return (center[0]+scale*(.832*x+.555*y),center[1]+scale*(.30*x-.45*y-.84*z))
 def depth(v):
  x,y,z=rotate(v);return .46*x-.69*y+.55*z
 # Floor is independent of the object's pitch.
 for gx in range(-4,5):
  a=(center[0]+scale*(.832*gx/2+.555*-1.7),center[1]+scale*(.30*gx/2-.45*-1.7+.45))
  b=(center[0]+scale*(.832*gx/2+.555*1.7),center[1]+scale*(.30*gx/2-.45*1.7+.45));d.line((a,b),fill='#dce4df',width=2)
 for gy in range(-3,4):
  a=(center[0]+scale*(.832*-2+.555*gy/2),center[1]+scale*(.30*-2-.45*gy/2+.45))
  b=(center[0]+scale*(.832*2+.555*gy/2),center[1]+scale*(.30*2-.45*gy/2+.45));d.line((a,b),fill='#dce4df',width=2)
 faces=[]
 # Extruded triangular frame, with front, back and side faces.
 tri=[(-.68,.20),(.66,.20),(-.18,.72)]
 vertices=[(x,y,z) for y in (-.13,.13) for x,z in tri]
 for ids,col in [([0,1,2],'#92d5cb'),([3,5,4],'#bce4dc'),([0,3,4,1],'#609f9a'),([1,4,5,2],'#d8ebe5'),([2,5,3,0],'#6bb8ad')]:
  vv=[vertices[i] for i in ids];faces.append((sum(depth(v) for v in vv)/len(vv),vv,col))
 for cx in (-.8,.8):
  rings=[]
  for y in (-.19,.19):
   rings.append([(cx+.34*math.cos(i*2*math.pi/40),y,.34*math.sin(i*2*math.pi/40)) for i in range(40)])
  for ring in rings:faces.append((sum(depth(v) for v in ring)/40,ring,'#5b6870'))
  for i in range(40):
   vv=[rings[0][i],rings[0][(i+1)%40],rings[1][(i+1)%40],rings[1][i]];faces.append((sum(depth(v) for v in vv)/4,vv,'#a4aeb2'))
 for _,vv,col in sorted(faces,key=lambda x:x[0]):d.polygon([proj(v) for v in vv],fill=col,outline=DARK,width=2)
 # Fork and handlebar with changing projection, connected to the frame.
 d.line([proj((.8,-.22,0)),proj((.48,-.22,.87))],fill=DARK,width=12)
 d.line([proj((.48,-.38,.87)),proj((.48,.38,.87))],fill=DARK,width=12)
 d.line([proj((-.22,-.28,.76)),proj((-.22,.28,.76))],fill=DARK,width=12)
 text(d,(90,85),'이동하는 위치와 물체의 자세',DARK,48)
 text(d,(90,164),'자전거에서도 위치 p와 자세 R은 다른 정보입니다',DARK,34)
 text(d,(90,825),'별도 설명모형 · 게임 내부 축이나 실제 회전각의 측정이 아닙니다','#64716a',26)
 arrow(d,(260,715),(620,715),BLUE,8);text(d,(260,740),'이동 방향',BLUE,28)
 if not late or sec>=25.14:
  arrow(d,proj((0,-.24,.25)),proj((1.35,-.24,.25)),RED,8);text(d,(1420,470),'앞 f',RED,38)
 if not late or sec>=25.5:
  arrow(d,proj((0,-.24,.25)),proj((0,-.24,1.55)),TEAL,8);text(d,(1420,540),'위 u',TEAL,38)
 if late and sec>=26.1:text(d,(1370,640),'두 방향을 함께 기록',DARK,28)
 return im
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
 sp=O/'03b-tracked-render-execution-v1.json';assert not sp.exists() and not LOCAL.exists()
 planp=O/'03b-observation-track-plan-v1.json';p=read(planp);r=read(ROOT/args.resource)
 assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
 assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
 t=read(O/'narration-07b-guide-repair-execution-v1.json');protected=t['protectedInputs']+t['results']
 for x in protected:assert sha(ROOT/x['path'])==x['sha256']
 assert sha(ROOT/p['source'])==p['sourceSha256'] and sha(ROOT/p['voice']['path'])==p['voice']['sha256']
 for x in p['anchors']:assert sha(ROOT/x['path'])==x['sha256']
 LOCAL.mkdir(parents=True);me=psutil.Process();target=LOCAL/'03b.tracked.silent.mp4'
 state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,resource=args.resource,resourceSha256=sha(ROOT/args.resource),plan=rel(planp),planSha256=sha(planp),cpuThreads=2,gpuJobs=0,frames=p['frames'],writtenFrames=0,status='03b-measured-tracking-rendering',actualOuterExitCode=None,newImageGit=0,newTts=0,allBetweenFramesApproved=False,finalCueApproved=False,finalRatioApproved=False)
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
  state.update(status='03b-render-complete-awaiting-encoded-pixel-review',workerExitCode=0,finishedAt=now(),writtenFrames=p['frames'],encodeExitCode=ex,wholeDecodeExitCode=dx,all1050NativePtsMatched=True,output=rel(target),outputSha256=sha(target),probe=probe,protectedShaMatched=True);save(sp,state)
  print(json.dumps(dict(workerExitCode=0,frames=p['frames'],nativeFrames=1050,output=rel(target))),flush=True)
 except BaseException as e:
  state.update(status='failed',workerExitCode=1,error=repr(e),traceback=traceback.format_exc(),finishedAt=now());save(sp,state);raise
if __name__=='__main__':main()
