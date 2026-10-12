"""CPU2/GPU0 measured 02aext screen observation; silent assembly input, not final."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,math,os,re,subprocess,traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='2'
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-02aext-tracked-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
FONTS={n:ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',n) for n in (22,26,28,30)}
TEAL='#43ddce';RED='#f54e4e';GOLD='#ffe16b'
def label(d,xy,text,color,size=26):
 f=FONTS[size];bb=d.textbbox(xy,text,font=f);assert bb[3]+10<900
 d.rounded_rectangle((bb[0]-9,bb[1]-5,bb[2]+9,bb[3]+9),radius=5,fill=(14,19,23,226));d.text(xy,text,font=f,fill=color)
def point_at(frame,p):
 source=min(p['nativeIn']+frame,p['nativeOutExclusive']-1)
 if any(a*60<=source<b*60 for a,b in p['hideSeconds']):return None
 for a,b in zip(p['anchors'],p['anchors'][1:]):
  if a['sourceFrame']<=source<=b['sourceFrame']:
   if source==a['sourceFrame']:return a['screenPoint']
   if source==b['sourceFrame']:return b['screenPoint']
   if not a['visible'] or not b['visible']:return None
   u=(source-a['sourceFrame'])/(b['sourceFrame']-a['sourceFrame'])
   return [a['screenPoint'][k]+u*(b['screenPoint'][k]-a['screenPoint'][k]) for k in (0,1)]
 raise ValueError(source)
def arrow(d,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy)
 if n<6:return
 d.line((tuple(a),tuple(b)),fill='#10191c',width=9);d.line((tuple(a),tuple(b)),fill=RED,width=5)
 u,v=dx/n,dy/n;d.polygon([tuple(b),(b[0]-15*u+7*v,b[1]-15*v-7*u),(b[0]-15*u-7*v,b[1]-15*v+7*u)],fill=RED)
def drawing(im,frame,p):
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
 label(d,(64,28),'Superflight · NCR Gameplay · 화면 관찰','#ffffff',22)
 label(d,(64,90),'화면 위치와 몸의 기울기를 비교하세요',GOLD,30)
 label(d,(64,153),'청록: 몸통의 화면 관찰점 p',TEAL,26)
 label(d,(64,210),'빨강: 0.5초 동안의 화면 위치 변화',RED,26)
 label(d,(64,268),'카메라 움직임도 포함 · 게임 내부 좌표값 아님','#ffffff',26)
 point=point_at(frame,p);previous=point_at(max(0,frame-30),p)
 if point is not None:
  x,y=point;d.ellipse((x-15,y-15,x+15,y+15),outline='#10191c',width=6)
  d.ellipse((x-12,y-12,x+12,y+12),outline=TEAL,width=4);d.ellipse((x-3,y-3,x+3,y+3),fill=TEAL)
 if frame>=30 and point is not None and previous is not None:
  if all(point_at(i,p) is not None for i in range(frame-30,frame+1)):arrow(d,previous,point)
 assert layer.getbbox()[3]<900
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB'),point
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
 sp=O/'02aext-tracked-render-execution-v1.json';assert not sp.exists() and not LOCAL.exists()
 p=read(O/'02aext-observation-track-plan-v1.json');r=read(ROOT/a.resource)
 assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
 assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
 tts=read(O/'narration-07b-guide-repair-execution-v1.json')
 protected=tts['protectedInputs']+tts['results']
 for x in protected:assert sha(ROOT/x['path'])==x['sha256']
 assert sha(ROOT/p['source'])==p['sourceSha256'] and sha(ROOT/p['voice']['path'])==p['voice']['sha256']
 for x in p['anchors']:assert sha(ROOT/x['inspectedImage'])==x['inspectedImageSha256']
 LOCAL.mkdir(parents=True);me=psutil.Process()
 state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,
   resource=a.resource,resourceSha256=sha(ROOT/a.resource),plan=rel(O/'02aext-observation-track-plan-v1.json'),planSha256=sha(O/'02aext-observation-track-plan-v1.json'),
   cpuThreads=2,gpuJobs=0,frames=p['sceneFrames'],nativeFrames=p['nativeFrames'],writtenFrames=0,status='02aext-measured-tracking-rendering',actualOuterExitCode=None,
   allBetweenFramesApproved=False,finalCueApproved=False,finalRatioApproved=False,newTts=0,newImageGit=0)
 save(sp,state)
 cp=read(O/'latest-checkpoint.json');cp.update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(O/'latest-checkpoint.json',cp)
 q=read(B/'queue.json');q['currentOrientationReview'].update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(B/'queue.json',q)
 target=LOCAL/'02aext.tracked.silent.mp4'
 dec=[FF,'-hide_banner','-nostdin','-v','info','-threads','1','-filter_threads','1','-ss','66.0','-copyts','-i',str(ROOT/p['source']),'-an','-vf',f"trim=start_pts={3960*256}:end_pts={4446*256},showinfo",'-frames:v','486','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
 enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v','486','-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(target)]
 save(LOCAL/'commands.json',dict(decode=dec,encode=enc));tracks=[]
 try:
  with (LOCAL/'decode.log').open('wb') as dl,(LOCAL/'encode.log').open('wb') as el:
   dp=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT);ep=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT)
   state.update(decodePid=dp.pid,decodeCreateTime=psutil.Process(dp.pid).create_time(),encodePid=ep.pid,encodeCreateTime=psutil.Process(ep.pid).create_time());save(sp,state)
   for frame in range(p['sceneFrames']):
    if frame<p['nativeFrames']:
     raw=dp.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3,(frame,len(raw))
    im=Image.frombytes('RGB',(1920,1080),raw);out,point=drawing(im,frame,p);ep.stdin.write(out.tobytes())
    tracks.append(dict(frame=frame,sourceFrame=min(3960+frame,4445),point=point,screenOnly=True,roundingHold=False))
    if frame%120==0:state['writtenFrames']=frame+1;save(sp,state)
   assert dp.stdout.read(1)==b'';dp.stdout.close();ep.stdin.close();dx=dp.wait();ex=ep.wait();assert dx==ex==0,(dx,ex)
  pts=[int(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',(LOCAL/'decode.log').read_text('utf-8',errors='replace'))]
  assert pts==[(3960+i)*256 for i in range(486)],(len(pts),pts[:2],pts[-2:])
  save(LOCAL/'track.json',dict(planSha256=state['planSha256'],frames=tracks))
  probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,time_base,nb_frames,duration','-of','json',str(target)],text=True))
  assert probe['streams'][0]['time_base']=='1/90000' and int(probe['streams'][0]['nb_frames'])==486
  with (LOCAL/'whole-decode.log').open('wb') as l:qa=subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(target),'-f','null','-'],stdout=l,stderr=subprocess.STDOUT).returncode
  assert qa==0
  for x in protected:assert sha(ROOT/x['path'])==x['sha256']
  state.update(status='02aext-render-complete-awaiting-encoded-pixel-review',workerExitCode=0,finishedAt=now(),writtenFrames=486,
   decodeExitCode=dx,encodeExitCode=ex,wholeDecodeExitCode=qa,all486NativePtsMatched=True,
   output=rel(target),outputSha256=sha(target),probe=probe,protectedShaMatched=True)
  save(sp,state);print(json.dumps(dict(workerExitCode=0,frames=486,nativePtsMatched=True,output=rel(target))),flush=True)
 except BaseException as e:
  state.update(status='failed',workerExitCode=1,error=repr(e),traceback=traceback.format_exc(),finishedAt=now());save(sp,state);raise
if __name__=='__main__':main()
