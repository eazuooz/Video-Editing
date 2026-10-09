"""Recover only failed ASS sampling; preserve all69 inputs/body and667 prior images."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,re,subprocess,sys,time,traceback
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/similar-game-design/selected-inputs-v1'
STATE=BASE/'selected-inputs-execution-v1.json';SESSION=BASE/'selected-inputs-ass-recovery-v1.session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
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
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<180
s=read(STATE);assert s['exitCode']==1 and s['completedCuts']==69 and s['wholeDecodeExitCode']==0 and s['exact90000Pts']
assert 'len(list(native.glob' in s['error']
assert not psutil.pid_exists(s['pid']) or abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.1
for key,hkey in [('silentVideo','silentSha256'),('captionAss','captionAssSha256')]:assert sha(ROOT/s[key])==s[hkey]
for seg in s['segments']:assert sha(ROOT/seg['video'])==seg['videoSha256']
assert sha(ROOT/s['plan']['path'])==s['plan']['sha256'] and sha(ROOT/s['captionCandidate']['path'])==s['captionCandidate']['sha256']
cap=read(ROOT/s['captionCandidate']['path']);white=read(BASE/'white-measured-verification-v1.json');timing=read(ROOT/'motion-canvas/src/projects/similar-game-design/measured-timing-v1.json')
native=OUT/'ass-preflight-native-v2';boards=OUT/'ass-preflight-boards-v2';assert not native.exists() and not boards.exists()
old=list((OUT/'ass-preflight-native').glob('frame-*.png'));assert len(old)==667
s.setdefault('recoveryHistory',[]).append(dict(pid=s['pid'],createTime=s['createTime'],sessionId=s['sessionId'],exitCode=1,actualExitObserved=True,finishedAt=s['finishedAt'],error=s['error'],reason='VFR image output yielded667 files for664 selections. Prior files preserved without assigning them to planned frames; sample again with passthrough and explicit timebase/showinfo provenance.',preservedImages=dict(directory=rel(OUT/'ass-preflight-native'),count=len(old))))
s.update(pid=os.getpid(),createTime=psutil.Process().create_time(),commandLine=[sys.executable,*sys.argv],sessionId=None,startedAt=now(),exitCode=None,actualExitObserved=False,status='recover-ASS-samples-only-preserve-all69-body',resourceEvidence=a.resource)
s.pop('error',None)
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==os.getpid() and abs(x['createTime']-s['createTime'])<.1:s['sessionId']=x['sessionId']
 s['updatedAt']=now();save(STATE,s)
 job={k:s[k]for k in ['pid','createTime','commandLine','sessionId','status','exitCode','actualExitObserved']};job.update(state=rel(STATE),cpuThreads=2,gpuJobs=0,singleJob=True,completed=69,total=69,workerExpectedRunning=s['exitCode']is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,updatedAt=now(),nextAction='Directly read all actual ASS boards before adoption; final/mixed/render/QA/collection/private remain false.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items']if i['slug']=='similar-game-design');i.update(stage=s['status'],currentExecution=job,nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
try:
 checkpoint();samples={}
 def sample(f,reason):
  assert 0<=f<36378;samples.setdefault(f,[]).append(reason)
 for c in cap['ko']:sample(round(((c['startSeconds']+c['endSeconds'])/2-2)*60),dict(kind='cue',cue=c['index'],scene=c['scene'],paragraph=c['paragraph']))
 for c in s['segments']:
  sample(c['startFrame']-120,dict(kind='cut-first',scene=c['scene'],role=c['role']));sample(c['endFrameExclusive']-121,dict(kind='cut-last',scene=c['scene'],role=c['role']))
 for p in cap['paragraphs']:sample(min(36377,max(0,round((p['startSeconds']-2)*60))),dict(kind='PCM-paragraph-onset',scene=p['scene'],paragraph=p['paragraph']))
 for f in white['samplePlan']:
  w=next(w for w in timing['white']if w['id']==f['scene']and w['part']==f['part']);sample(w['finalStartFrame']-120+f['frame']-w['whiteProjectStartFrame'],dict(kind='white-motion',scene=f['scene'],paragraph=f['paragraph'],phase=f['phase']))
 frames=sorted(samples);assert len(frames)==664;native.mkdir();boards.mkdir();expr='+'.join(f'eq(n,{f})'for f in frames)
 cmd=[str(FF),'-v','info','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1','-i',str(ROOT/s['silentVideo']),'-an','-vf',f"ass={s['captionAss']},select='{expr}',showinfo",'-fps_mode','passthrough','-enc_time_base','1/90000','-threads','2',str(native/'frame-%04d.png')]
 log=OUT/'logs/0146-ass-passthrough-recovery.log';op=dict(kind='recover-only-ASS-samples-explicit-passthrough',commandLine=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8')as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);op.update(pid=p.pid,createTime=psutil.Process(p.pid).create_time());s['activeTask']=op;checkpoint();code=p.wait()
 op.update(exitCode=code,finishedAt=now());s['activeTask']=None;assert code==0
 assert len(list(native.glob('frame-*.png')))==664
 show=re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:',log.read_text('utf-8-sig'))
 assert len(show)==664 and [int(x[0])for x in show]==list(range(664))
 assert [int(x[1])for x in show]==[f*1500 for f in frames], 'Decoded presentation time must match each planned frame'
 rows=[]
 for i,f in enumerate(frames,1):
  path=native/f'frame-{i:04d}.png';visible=[c['index']for c in cap['ko']if round((c['startSeconds']-2)*100)/100<=f/60<round((c['endSeconds']-2)*100)/100]
  rows.append(dict(index=i,bodyFrame=f,finalFrame=f+120,path=rel(path),sha256=sha(path),decodedPts=f*1500,observations=samples[f],visibleCueIds=visible))
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);boardrows=[]
 for bi,start in enumerate(range(0,len(rows),6),1):
  group=rows[start:start+6];board=Image.new('RGB',(1920,1240),'white');draw=ImageDraw.Draw(board)
  for ci,row in enumerate(group):
   x=(ci%3)*640;y=(ci//3)*620;draw.text((x+6,y+5),f'{row["index"]:04d} n{row["finalFrame"]} cue{row["visibleCueIds"]}',font=font,fill='black');im=Image.open(ROOT/row['path']).convert('RGB');board.paste(im.resize((640,360)),(x,y+34));board.paste(im.crop((600,862,1320,1072)).resize((640,187)),(x,y+404));draw.text((x+6,y+593),'; '.join(o['kind']for o in row['observations'])[:57],font=font,fill='black')
  path=boards/f'board-{bi:03d}.jpg';board.save(path,quality=94);boardrows.append(dict(path=rel(path),sha256=sha(path),entries=group,directlyRead=False))
 s.update(status='closed-selected69-inputs-actual-ASS-await-direct-review',exitCode=0,finishedAt=now(),samples=rows,boards=boardrows,uniqueSampleFrames=664,all400CueSamplesExtracted=True,all69CutEdgesExtracted=True,all128WhiteMotionSamplesExtracted=True,decodedPtsForEverySampleMatched=True,allCurrentPcmPreserved=True,previewIsCompletedVideo=False);checkpoint();print(json.dumps(dict(exitCode=0,samples=664,boards=len(boardrows),allPixelGates=False)),flush=True)
except BaseException:
 s.update(status='failed-selected-inputs-preserve-completed-media',exitCode=1,finishedAt=now(),error=traceback.format_exc());checkpoint();raise
