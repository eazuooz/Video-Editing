"""CPU2/GPU0 measured placement scene; unique native actions, screen guides and projected models."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,math,os,re,subprocess,traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='2'
import psutil
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-10b-tracked-v1'
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
FONTS={n:ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',n) for n in (24,26,28,30,34,38,48)}
RED='#e64045';TEAL='#24bfb2';BLUE='#3e7ecb';DARK='#23313d'
def text(d,xy,s,c=DARK,n=30):
 b=d.textbbox(xy,s,font=FONTS[n]);assert b[2]<1900 and b[3]<900;d.text(xy,s,font=FONTS[n],fill=c)
def label(d,xy,s,c='#ffffff',n=28):
 b=d.textbbox(xy,s,font=FONTS[n]);assert b[2]+10<1900 and b[3]+10<900;d.rounded_rectangle((b[0]-9,b[1]-5,b[2]+9,b[3]+9),radius=5,fill=(15,19,23,230));d.text(xy,s,font=FONTS[n],fill=c)
def arrow(d,a,b,c,w=6):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 if length<9:return
 d.line((tuple(a),tuple(b)),fill=c,width=w);ux,uy=dx/length,dy/length;d.polygon([tuple(b),(b[0]-17*ux+8*uy,b[1]-17*uy-8*ux),(b[0]-17*ux-8*uy,b[1]-17*uy+8*ux)],fill=c)
def observed(source,p):
 if any(a*60<=source<b*60 for a,b in p['hideSourceSeconds']):return None
 for a,b in zip(p['anchors'],p['anchors'][1:]):
  if a['sourceFrame']<=source<=b['sourceFrame']:
   if not a['visible'] or not b['visible'] or b['sourceFrame']-a['sourceFrame']>31:return None
   u=(source-a['sourceFrame'])/(b['sourceFrame']-a['sourceFrame']);return {k:[a[k][i]+u*(b[k][i]-a[k][i]) for i in range(4)] for k in ('bounds','line')}
 return None
def focused(im):
 out=im.crop((320,255,1600,975)).resize((1920,1080),Image.Resampling.LANCZOS)
 out.paste(out.filter(ImageFilter.GaussianBlur(18)).crop((0,900,1920,1080)),(0,900));return out
def source_scene(im,frame,native,seg,p):
 kind=seg['kind'];full=kind in ('full-source-ui-context','separate-size-selection')
 out=im.copy() if full else focused(im);layer=Image.new('RGBA',out.size);d=ImageDraw.Draw(layer);sec=frame/60
 label(d,(60,65),'Space Engineers · 조립할 부품의 자세','#ffffff',34)
 if kind=='full-source-ui-context':
  label(d,(60,130),'Landing Gear: 착륙용 부품 · 먼저 배치 미리보기를 확인','#ffe16b',28)
  if sec>=8.1:label(d,(60,190),'원본 오른쪽 위: 회전 키 안내 · 실제 눌린 키 추정 아님','#ffffff',26)
 elif kind=='frozen-preview-prerequisite':
  label(d,(60,130),'초록 상자 속 흐릿한 부품 = 놓기 전 미리보기','#ffe16b',30)
  label(d,(60,190),'정지 분석 · 화면상의 긴 방향을 붉은 선으로 보기',RED,26)
 elif kind=='small-preview-rotation':
  label(d,(60,130),'작은 미리보기 · 세로와 가로 자세 비교','#ffe16b',30)
  label(d,(60,190),'붉은 선: 보이는 긴 방향 · 청록: 관찰 대상',RED,26)
 elif kind=='separate-placement-action':
  label(d,(60,130),'다른 배치 구간 · 자세 선택에서 실제 부품으로','#ffe16b',30)
  if native<10728:label(d,(60,190),'놓기 전 미리보기 · 화면 관찰',TEAL,26)
  elif native>=10800:label(d,(60,190),'실제로 배치된 단단한 부품',TEAL,28)
  else:label(d,(60,190),'배치 뒤 다음 미리보기와 겹침 · 표식 숨김','#ffffff',26)
 elif kind=='separate-size-selection':
  label(d,(60,130),'크기 선택 · 별도 비교 구간','#ffe16b',34)
  label(d,(60,190),'크기 선택과 카메라 변화 · 회전만의 결과로 읽지 않기','#ffffff',26)
 obs=None if full else observed(native,p)
 if obs:
  def cp(v):return ((v[0]-320)*1.5,(v[1]-255)*1.5)
  b=obs['bounds'];a0,b0=cp(b[:2]),cp(b[2:]);assert min(a0)>=0 and b0[0]<1920 and b0[1]<900
  d.rectangle((*a0,*b0),outline=TEAL,width=5)
  l=obs['line'];a1,b1=cp(l[:2]),cp(l[2:]);d.line((a1,b1),fill='#101820',width=12);d.line((a1,b1),fill=RED,width=7)
 label(d,(60,830),'화면 관찰선 · 게임 내부 축/실제 크기/누른 키의 측정 아님','#ffffff',24)
 assert layer.getbbox()[3]<900
 return Image.alpha_composite(out.convert('RGBA'),layer).convert('RGB'),obs
def model(frame):
 sec=frame/60;late=frame>=1428;im=Image.new('RGB',(1920,1080),'#fafbf9');d=ImageDraw.Draw(im)
 text(d,(75,70),'비행 자세에서 배치 자세로',DARK,48)
 text(d,(75,145),'따로 정한 설명모형 · 실제 게임 내부 좌표축이 아닙니다',DARK,30)
 angle=.30*math.sin(sec*1.15) if not late else math.pi/2*min(1,max(0,(sec-26.24)/1.5))
 centers=[(505,540),(1340,540)];scale=145;faces=[]
 def rot(v):
  x,y,z=v;c,s=math.cos(angle),math.sin(angle);return (c*x-s*y,s*x+c*y,z)
 def proj(v,center):
  x,y,z=rot(v);return(center[0]+scale*(.79*x-.61*z),center[1]+scale*(.32*x-.80*y+.41*z))
 def box(bounds,center,top,side):
  x0,x1,y0,y1,z0,z1=bounds;v=[(x,y,z) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)]
  for ids,col in [([0,1,3,2],side),([4,6,7,5],side),([0,4,5,1],side),([2,3,7,6],top),([0,2,6,4],side),([1,5,7,3],side)]:
   vv=[v[i] for i in ids];depth=sum(.49*rot(a)[0]+.57*rot(a)[1]+.66*rot(a)[2] for a in vv)/4;faces.append((depth,[proj(a,center) for a in vv],col))
 # Extruded airplane and mounting component: distinct uses, shared orientation representation.
 box((-.18,.18,-.22,.22,-1.2,1.5),centers[0],'#e3c56a','#af8a35');box((-1.8,1.8,.25,.38,-.05,.40),centers[0],'#b7cce5','#637d9d');box((-.75,.75,.18,.32,-1.22,-.9),centers[0],'#9bb4d2','#566c88')
 box((-.95,.95,-.85,-.55,-.55,.55),centers[1],'#b7cce5','#637d9d');box((-.32,.32,-.55,1.25,-.32,.32),centers[1],'#e3c56a','#af8a35');box((-.8,.8,1.25,1.5,-.55,.55),centers[1],'#c1d2e6','#637d9d')
 for _,pts,col in sorted(faces,key=lambda x:x[0]):d.polygon(pts,fill=col,outline=DARK,width=2)
 text(d,(350,760),'비행 중인 기체',DARK,34);text(d,(1210,760),'놓기 전 부품',DARK,34)
 if sec>=2.18:arrow(d,(795,420),(1045,420),TEAL,8)
 if late:
  text(d,(70,225),'배치 상황은 달라도, 같은 기준으로 자세를 기록',DARK,34)
  if sec>=28.9:
   for center in centers:
    origin=proj((0,0,0),center)
    for v,c in [((1.5,0,0),RED),((0,1.7,0),TEAL),((0,0,1.6),BLUE)]:arrow(d,origin,proj(v,center),c,6)
   text(d,(75,830),'이 모형의 x=빨강, y=청록, z=파랑 · 게임 관찰선과 구분',DARK,26)
 else:text(d,(75,830),'한 방향만 보지 않고 여러 방향을 함께 기록합니다',DARK,26)
 return im
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args();sp=O/'10b-tracked-render-execution-v1.json';assert not sp.exists() and not LOCAL.exists()
 pp=O/'10b-observation-track-plan-v1.json';p=read(pp);r=read(ROOT/a.resource)
 assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
 assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
 t=read(O/'narration-07b-guide-repair-execution-v1.json');protected=t['protectedInputs']+t['results']
 for x in protected:assert sha(ROOT/x['path'])==x['sha256']
 assert sha(ROOT/p['source'])==p['sourceSha256'] and sha(ROOT/p['voice']['path'])==p['voice']['sha256']
 for x in p['anchors']:assert sha(ROOT/x['path'])==x['sha256']
 LOCAL.mkdir(parents=True);me=psutil.Process();target=LOCAL/'10b.tracked.silent.mp4'
 state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),resource=a.resource,plan=rel(pp),planSha256=sha(pp),cpuThreads=2,gpuJobs=0,frames=p['frames'],writtenFrames=0,status='10b-measured-tracking-rendering',actualOuterExitCode=None,newImageGit=0,newTts=0,allBetweenFramesApproved=False,finalCueApproved=False,finalRatioApproved=False,decoders=[])
 save(sp,state);cp=read(O/'latest-checkpoint.json');cp.update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(O/'latest-checkpoint.json',cp);q=read(B/'queue.json');q['currentOrientationReview'].update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(B/'queue.json',q)
 enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v',str(p['frames']),'-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(target)]
 tracks=[];frozen=None
 def decoder(ni,no,num):
  n=no-ni;cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','1','-filter_threads','1','-ss',str(ni/60),'-copyts','-i',str(ROOT/p['source']),'-an','-vf',f'trim=start_pts={ni*256}:end_pts={no*256},showinfo','-frames:v',str(n),'-pix_fmt','rgb24','-f','rawvideo','pipe:1'];log=LOCAL/f'decode-{num}.log';dl=log.open('wb');dp=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT);info=dict(pid=dp.pid,createTime=psutil.Process(dp.pid).create_time(),command=cmd,nativeIn=ni,nativeOutExclusive=no,log=rel(log));state['decoders'].append(info);save(sp,state);return dp,dl,log,info
 def close_decoder(dp,dl,log,info):
  assert dp.stdout.read(1)==b'';dp.stdout.close();dx=dp.wait();dl.close();assert dx==0;pts=[int(v) for v in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',log.read_text('utf-8',errors='replace'))];assert pts==[i*256 for i in range(info['nativeIn'],info['nativeOutExclusive'])];info.update(exitCode=dx,exactNativePtsMatched=True);save(sp,state)
 try:
  with (LOCAL/'encode.log').open('wb') as el:
   ep=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT);state.update(encodePid=ep.pid,encodeCreateTime=psutil.Process(ep.pid).create_time(),encodeCommand=enc);save(sp,state)
   for num,seg in enumerate(p['segments']):
    start,end=seg['frameIn'],seg['frameOut']
    if seg['classification']=='actual':
     ni,no=seg['nativeIn'],seg['nativeOutExclusive'];assert no-ni==end-start;dp,dl,log,info=decoder(ni,no,num)
     for f in range(start,end):
      raw=dp.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3;im=Image.frombytes('RGB',(1920,1080),raw);out,obs=source_scene(im,f,ni+f-start,seg,p);ep.stdin.write(out.tobytes());tracks.append(dict(frame=f,nativeFrame=ni+f-start,classification='actual',observation=obs))
      if f%120==0:state['writtenFrames']=f+1;save(sp,state)
     close_decoder(dp,dl,log,info)
    else:
     if seg.get('freezeNative') and frozen is None:
      ni=seg['freezeNative'];dp,dl,log,info=decoder(ni,ni+1,'frozen-prerequisite');raw=dp.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3;frozen=Image.frombytes('RGB',(1920,1080),raw);close_decoder(dp,dl,log,info)
     for f in range(start,end):
      if seg.get('freezeNative'):out,obs=source_scene(frozen,f,seg['freezeNative'],seg,p)
      else:out=model(f)
      ep.stdin.write(out.tobytes());tracks.append(dict(frame=f,classification='explanation',kind=seg['kind']))
      if f%120==0:state['writtenFrames']=f+1;save(sp,state)
   ep.stdin.close();ex=ep.wait();assert ex==0
  save(LOCAL/'track.json',dict(planSha256=state['planSha256'],frames=tracks));probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,time_base,nb_frames,duration','-of','json',str(target)],text=True));assert probe['streams'][0]['time_base']=='1/90000' and int(probe['streams'][0]['nb_frames'])==p['frames']
  with (LOCAL/'whole-decode.log').open('wb') as l:dx=subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(target),'-f','null','-'],stdout=l,stderr=subprocess.STDOUT).returncode
  assert dx==0
  for x in protected:assert sha(ROOT/x['path'])==x['sha256']
  state.update(status='10b-render-complete-awaiting-encoded-pixel-review',workerExitCode=0,finishedAt=now(),writtenFrames=p['frames'],encodeExitCode=ex,wholeDecodeExitCode=dx,all510NativePtsMatched=True,output=rel(target),outputSha256=sha(target),probe=probe,protectedShaMatched=True);save(sp,state);print(json.dumps(dict(workerExitCode=0,frames=p['frames'],nativeFrames=510,output=rel(target))),flush=True)
 except BaseException as e:
  state.update(status='failed',workerExitCode=1,error=repr(e),traceback=traceback.format_exc(),finishedAt=now());save(sp,state);raise
if __name__=='__main__':main()
