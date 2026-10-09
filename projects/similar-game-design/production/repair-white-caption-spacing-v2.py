"""Move reviewed projected content 32px up, preserving all timings and game inputs."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,ctypes,hashlib,json,os,re,subprocess,sys,time,traceback
import psutil,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/similar-game-design/selected-inputs-v1/caption-spacing-v2'
STATE=BASE/'white-caption-spacing-execution-v2.json';SESSION=BASE/'white-caption-spacing-v2.session.json'
SELECTED=BASE/'selected-inputs-execution-v1.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(60):
  try:os.replace(t,p);return
  except OSError:
   if n==59:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args();r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<180
old=read(SELECTED);assert old['exitCode']==0 and old['actualExitObserved'] and old['completedCuts']==69
review=read(BASE/'selected-inputs-pre-spacing-direct-review-v1.json')
assert review['all111BoardsDirectlyRead'] and review['executionSha256']==sha(SELECTED) and review['unresolvedDefects']
assert not OUT.exists() and not STATE.exists(),'Preserve existing repair; inspect checkpoint'
OUT.mkdir();(OUT/'segments').mkdir();(OUT/'logs').mkdir();(OUT/'native').mkdir();(OUT/'boards').mkdir()
s=dict(schemaVersion=1,slug='similar-game-design',pid=os.getpid(),createTime=psutil.Process().create_time(),commandLine=[sys.executable,*sys.argv],sessionId=None,startedAt=now(),status='repair-white-content-spacing-only',cpuThreads=2,gpuJobs=0,singleJob=True,resourceEvidence=a.resource,previousExecutionSha256=sha(SELECTED),previousExecution=old,operations=[],segments=[],completedWhite=0,totalWhite=19,exitCode=None,actualExitObserved=False,captionOffset=[0,0],contentOffset=[0,-32],render=False,qa=False,collected=False,uploaded=False,newGitImages=0)
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
def checkpoint():
 if SESSION.exists():
  se=read(SESSION)
  if se['pid']==os.getpid() and abs(se['createTime']-s['createTime'])<.1:s['sessionId']=se['sessionId']
 s['updatedAt']=now();save(STATE,s)
 job={k:s[k]for k in ['pid','createTime','commandLine','sessionId','status','exitCode','actualExitObserved']};job.update(state=rel(STATE),cpuThreads=2,gpuJobs=0,singleJob=True,completed=s['completedWhite'],total=19,workerExpectedRunning=s['exitCode']is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,whiteCaptionSpacing=rel(STATE),updatedAt=now(),nextAction='Read repaired actual white ASS pixels; refresh changed50-project content/Studio duplicate gate, then adopt timing/mix. Final gates false.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items']if i['slug']=='similar-game-design');i.update(stage=s['status'],currentExecution=job,whiteCaptionSpacing=rel(STATE),nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
def run(exe,args,kind):
 cmd=[str(exe),*map(str,args)];log=OUT/'logs'/f'{len(s["operations"])+1:04d}.log';op=dict(kind=kind,commandLine=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8')as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);op.update(pid=p.pid,createTime=psutil.Process(p.pid).create_time());s['activeTask']=op;checkpoint();code=p.wait()
 op.update(exitCode=code,finishedAt=now());s['activeTask']=None;checkpoint();assert code==0,f'{kind} exit{code}: {log}';return log.read_text('utf-8-sig')
def ff(args,kind,level='error'):return run(FF,['-v',level,'-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
def scan_blank_bands(p,n):
 # The header ends above248px. Verify every frame has no content in the
 # 32px destination margin or below the translated region before moving it.
 filt='split=2[a][b];[a]crop=1920:32:0:248[t];[b]crop=1920:170:0:910[u];[t][u]vstack,format=rgb24'
 cmd=[str(FF),'-v','error','-nostdin','-threads','2','-filter_complex_threads','1','-i',str(p),'-an','-filter_complex',filt,'-f','rawvideo','-pix_fmt','rgb24','-threads','2','-']
 log=OUT/'logs'/f'{len(s["operations"])+1:04d}.log';op=dict(kind='verify-all-frames-clear-translation-bands',commandLine=cmd,log=rel(log),startedAt=now());s['operations'].append(op);count=0;minimum=255
 with log.open('w',encoding='utf-8')as err:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW);op.update(pid=child.pid,createTime=psutil.Process(child.pid).create_time());s['activeTask']=op;checkpoint()
  block=1920*202*3
  while True:
   b=child.stdout.read(block)
   if not b:break
   assert len(b)==block;count+=1;minimum=min(minimum,int(np.frombuffer(b,dtype=np.uint8).min()))
  code=child.wait()
 op.update(exitCode=code,finishedAt=now(),frames=count,minimum=minimum,clear=minimum>=250);s['activeTask']=None;checkpoint();assert code==0 and count==n and minimum>=250,'Translation band contains content; do not crop it'
 return dict(frames=count,minimum=minimum,clear=True)
try:
 checkpoint()
 for cut in old['segments']:
  assert sha(ROOT/cut['video'])==cut['videoSha256'];c=copy.deepcopy(cut)
  if c['role']=='explanation':
   band=scan_blank_bands(ROOT/c['video'],c['frames']);p=OUT/'segments'/f'{c["index"]:03d}-{c["scene"]}.mp4'
   filt='split=2[a][b];[a]crop=1920:630:0:280[content];[b]drawbox=x=0:y=248:w=iw:h=662:color=white:t=fill[blank];[blank][content]overlay=x=0:y=248:shortest=1:format=yuv420,setpts=N/(60*TB)'
   ff(['-i',ROOT/c['video'],'-an','-map_metadata','-1','-write_tmcd','0','-filter_complex',filt,'-frames:v',c['frames'],'-fps_mode','passthrough','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',p],'translate-white-projected-content-only')
   pr=json.loads(run(FP,['-v','error','-threads','2','-show_streams','-of','json',p],'probe-repaired-white'));v=pr['streams'][0]
   assert len(pr['streams'])==1 and v['time_base']=='1/90000' and int(v['nb_frames'])==c['frames'] and int(v['duration_ts'])==c['frames']*1500
   assert not ff(['-i',p,'-an','-f','null','-'],'decode-repaired-white').strip()
   c.update(priorVideo=c['video'],priorVideoSha256=c['videoSha256'],video=rel(p),videoSha256=sha(p),probe=pr,contentOffset=[0,-32],captionOffset=[0,0],blankBandVerification=band,wholeDecodeExitCode=0)
   s['completedWhite']+=1;print(f'White spacing {s["completedWhite"]}/19',flush=True)
  s['segments'].append(c);checkpoint()
 listing=OUT/'concat-body.txt';listing.write_text('ffconcat version 1.0\n'+''.join("file '"+(ROOT/c['video']).as_posix()+"'\nduration "+f"{c['frames']/60:.12f}"+'\n'for c in s['segments']),'utf-8')
 body=OUT/'candidate-body.silent.mp4'
 ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-c:v','copy','-bsf:v','setts=pts=round(PTS/1500)*1500:dts=round(DTS/1500)*1500:duration=1500:time_base=1/90000','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',body],'assemble-preserved-game-and-repaired-white')
 pr=json.loads(run(FP,['-v','error','-show_streams','-of','json',body],'probe-repaired-body'));v=pr['streams'][0];assert int(v['nb_frames'])==36378 and v['time_base']=='1/90000'
 packets=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',body],'all-repaired-body-PTS'))['packets'];assert sorted(int(p['pts'])for p in packets)==list(range(0,36378*1500,1500)) and all(int(p['duration'])==1500 for p in packets)
 assert not ff(['-i',body,'-an','-f','null','-'],'decode-repaired-body').strip()
 changed=[row for row in old['samples']if any(c['role']=='explanation'and c['startFrame']<=row['finalFrame']<c['endFrameExclusive']for c in s['segments'])]
 expr='+'.join(f'eq(pts,{row["decodedPts"]})'for row in changed)
 logtext=ff(['-i',body,'-an','-vf',f"ass={old['captionAss']},select='{expr}',showinfo",'-fps_mode','passthrough','-enc_time_base','1/90000','-threads','2',OUT/'native/frame-%04d.png'],'extract-only-repaired-white-ASS','info')
 show=re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:',logtext);assert [int(x[1])for x in show]==[row['decodedPts']for row in changed]
 replacement={row['index']:OUT/'native'/f'frame-{i:04d}.png'for i,row in enumerate(changed,1)};rows=[]
 for row in old['samples']:
  r=copy.deepcopy(row)
  if r['index']in replacement:r.update(priorPath=r['path'],priorSha256=r['sha256'],path=rel(replacement[r['index']]),sha256=sha(replacement[r['index']]),contentOffset=[0,-32])
  else:assert sha(ROOT/r['path'])==r['sha256']
  rows.append(r)
 boards=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
 for bi,start in enumerate(range(0,len(rows),6),1):
  group=rows[start:start+6]
  if not any(row['index']in replacement for row in group):
   b=copy.deepcopy(old['boards'][bi-1]);b.update(directlyRead=True,reviewProvenance=rel(BASE/'selected-inputs-pre-spacing-direct-review-v1.json'));boards.append(b);continue
  board=Image.new('RGB',(1920,1240),'white');draw=ImageDraw.Draw(board)
  for ci,row in enumerate(group):
   x=(ci%3)*640;y=(ci//3)*620;draw.text((x+6,y+5),f'{row["index"]:04d} n{row["finalFrame"]} cue{row["visibleCueIds"]}',font=font,fill='black');im=Image.open(ROOT/row['path']).convert('RGB');board.paste(im.resize((640,360)),(x,y+34));board.paste(im.crop((600,820,1320,1072)).resize((640,187)),(x,y+404));draw.text((x+6,y+593),'; '.join(o['kind']for o in row['observations'])[:57],font=font,fill='black')
  p=OUT/'boards'/f'board-{bi:03d}.jpg';board.save(p,quality=94);boards.append(dict(path=rel(p),sha256=sha(p),entries=group,directlyRead=False,captionCrop=[600,820,1320,1072]))
 s.update(status='closed-white-spacing-repair-await-direct-pixels',exitCode=0,finishedAt=now(),silentVideo=rel(body),silentSha256=sha(body),bodyProbe=pr,wholeDecodeExitCode=0,exact90000Pts=True,samples=rows,boards=boards,repairedSamples=len(changed),reusedGameSamples=len(rows)-len(changed),changedBoards=sum(not b['directlyRead']for b in boards),all50GameInputsByteIdentical=True,allCurrentPcmPreserved=True,captionAssByteIdentical=True)
 checkpoint();print(json.dumps(dict(exitCode=0,whiteParts=19,repairedSamples=len(changed),changedBoards=s['changedBoards'],allPixelGates=False)),flush=True)
except BaseException:
 s.update(status='failed-white-spacing-preserve-prior-inputs',exitCode=1,finishedAt=now(),error=traceback.format_exc());checkpoint();raise
