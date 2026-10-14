"""One CPU2/GPU0 job: replace only generic EX pixels in three reviewed mixed clips."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,traceback
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
import psutil
from PIL import Image,ImageDraw
from orientation_detailed_projected_subjects_v1 import frame_03b,frame_07b,frame_10b
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-mixed-detailed-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.resolve().relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,x):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
 r=read(ROOT/a.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
 assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
 me=psutil.Process();own=[]
 for p in psutil.process_iter(['pid','name','cmdline']):
  try:
   c=p.info['cmdline'] or [];cmd=' '.join(c)
   if p.pid==me.pid or (me.parent() and p.pid==me.parent().pid and c[1:]==me.cmdline()[1:]):continue
   if 'cross-game-example-coverage-review' in cmd and any(k in cmd for k in ['render-orientation','review-orientation','extract-orientation','assemble-orientation','render-motion','review-motion','extract-motion']):own.append(p.pid)
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 assert not own
 subprocess.run([NODE,'scripts/review-video-duplicates.cjs','game-math-orientation-matrices','--candidate-file',str(O/'duplicate-candidate-v1.json'),'--check'],cwd=ROOT,check=True)
 planp=O/'current34-mixed-detailed-subject-replacement-plan-v4.json';plan=read(planp)
 staticp=O/'current34-mixed-detailed-static-direct-review-v1.json';static=read(staticp)
 assert static['planSha256']==sha(planp) and static['all18CurrentStaticSamplesDirectlyRead']
 assert sha(ROOT/plan['editableModule'])==plan['editableModuleSha256']
 assert sha(ROOT/plan['subjectPolicy'])==plan['subjectPolicySha256']
 proof=read(O/'narration-07b-guide-repair-execution-v1.json');protected=proof['protectedInputs']+proof['results']
 for x in protected:assert sha(ROOT/x['path'])==x['sha256']
 for row in plan['rows']:
  for key,hkey in [('source','sourceSha256'),('plan','planSha256'),('originalExecution','originalExecutionSha256')]:assert sha(ROOT/row[key])==row[hkey]
 assert read(O/'latest-checkpoint.json')['activeOwnedWorkers']==0
 sp=O/'current34-mixed-detailed-render-execution-v1.json';assert not sp.exists() and not LOCAL.exists()
 LOCAL.mkdir(parents=True);me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
 state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,resource=a.resource,resourceSha256=sha(ROOT/a.resource),plan=rel(planp),planSha256=sha(planp),staticReview=rel(staticp),staticReviewSha256=sha(staticp),cpuThreads=2,gpuJobs=0,status='rendering-current34-three-detailed-mixed-explanations',results=[],jobs=[],actualOuterExitCode=None,workerExitCode=None,newTts=0,newAsr=0,newMix=0,newImageGit=0,gameplaySourceAcquisition=0,gameplayAnnotationRegeneration=0,final244CaptionPixelsApproved=False)
 def checkpoint():
  ss=sp.with_name(sp.stem+'.session.json')
  if ss.exists():
   sv=read(ss);assert sv['pid']==me.pid and abs(sv['createTime']-me.create_time())<.01;state['sessionId']=sv['sessionId']
  state['updatedAt']=now();save(sp,state)
  cp=read(O/'latest-checkpoint.json');cp.update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1,mixedDetailedReplacementPlan=rel(planp));save(O/'latest-checkpoint.json',cp)
  q=read(B/'queue.json');q['currentOrientationReview'].update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1,mixedDetailedReplacementPlan=rel(planp));save(B/'queue.json',q)
 def job(cmd,log,**extra):
  with log.open('wb') as f:
   p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
   j=dict(pid=p.pid,createTime=psutil.Process(p.pid).create_time(),command=cmd,log=rel(log),**extra);state['jobs'].append(j);checkpoint();ex=p.wait();j['exitCode']=ex;checkpoint();assert ex==0
  return ex
 checkpoint()
 try:
  for row in plan['rows']:
   sid=row['scene'];n=row['frames'];dout=LOCAL/sid;dout.mkdir();target=dout/f'{sid}.detailed.silent.mp4'
   fn={'03b':frame_03b,'07b':frame_07b,'10b':frame_10b}[sid]
   replaces={f for seg in row['replaceExplanationSegments'] for f in range(seg['frameIn'],seg['frameOut'])}
   dec=[FF,'-hide_banner','-nostdin','-v','error','-threads','1','-i',str(ROOT/row['source']),'-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
   enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v',str(n),'-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(target)]
   originalhash=hashlib.sha256();passedhash=hashlib.sha256();preserved=0
   with (dout/'decode-prior.log').open('wb') as dl,(dout/'encode.log').open('wb') as el:
    dp=subprocess.Popen(dec,cwd=ROOT,stdout=subprocess.PIPE,stderr=dl)
    ep=subprocess.Popen(enc,cwd=ROOT,stdin=subprocess.PIPE,stderr=el)
    dj=dict(pid=dp.pid,createTime=psutil.Process(dp.pid).create_time(),command=dec,log=rel(dout/'decode-prior.log'),kind='reuse-prior-encoded-timeline');ej=dict(pid=ep.pid,createTime=psutil.Process(ep.pid).create_time(),command=enc,log=rel(dout/'encode.log'),kind='new-explanation-encoder');state['jobs'] += [dj,ej];checkpoint()
    for f in range(n):
     raw=dp.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3
     if f in replaces:out=fn(f).tobytes()
     else:
      originalhash.update(raw);out=raw;passedhash.update(out);preserved+=1
     ep.stdin.write(out)
     if f%120==0:state.update(currentScene=sid,writtenFrames=f+1);checkpoint()
    assert dp.stdout.read(1)==b'';dp.stdout.close();ep.stdin.close();dx=dp.wait();ex=ep.wait();dj['exitCode']=dx;ej['exitCode']=ex;checkpoint();assert dx==ex==0
   assert originalhash.hexdigest()==passedhash.hexdigest()
   probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',str(target)]))['streams'][0]
   assert (probe['width'],probe['height'],probe['r_frame_rate'],probe['time_base'],int(probe['nb_frames']))==(1920,1080,'60/1','1/90000',n)
   pts=json.loads(subprocess.check_output([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(target)]))['frames']
   assert [int(x['pts']) for x in pts]==list(range(0,n*1500,1500))
   whole=job([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(target),'-an','-f','null','-'],dout/'whole-decode.log',kind='whole-new-timeline-decode')
   wanted=set(x['frame'] for x in plan['preparedSamples'] if x['scene']==sid)
   for seg in row['replaceExplanationSegments']:
    st,en=seg['frameIn'],seg['frameOut'];wanted.update(range(st,en,30));wanted.update([st,(st+en-1)//2,en-1])
   allsegs=read(ROOT/row['plan'])['segments']
   for seg in allsegs:
    for f in [seg['frameIn'],seg['frameOut']]:wanted.update(v for v in [f-1,f,f+1] if 0<=v<n)
   for sec in {'03b':[25.14,25.5,26.1],'07b':[13.1,14.2,15.72],'10b':[2.18,26.24,28.9]}[sid]:
    f=round(sec*60);wanted.update(v for v in [f-1,f,f+1] if 0<=v<n)
   wanted=sorted(wanted);select='+'.join(f'eq(pts\\,{f*1500})' for f in wanted)
   extract=job([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-i',str(target),'-vf','select='+select,'-vsync','0','-start_number','0',str(dout/'sample-%03d.png')],dout/'extract-new-pixels.log',kind='absolutePTS-new-EX-and-cuts')
   paths=sorted(dout.glob('sample-*.png'));assert len(paths)==len(wanted)
   samples=[dict(frame=f,pts=f*1500,path=rel(p),sha256=sha(p),classification='replaced-explanation' if f in replaces else 'prior-encoded-timeline-reused') for f,p in zip(wanted,paths)]
   boards=[]
   for k in range(0,len(samples),4):
    board=Image.new('RGB',(1920,1140),'#f5f5f5');bd=ImageDraw.Draw(board)
    for i,sam in enumerate(samples[k:k+4]):
     im=Image.open(ROOT/sam['path']);im.thumbnail((960,540));x=i%2*960;y=i//2*570;board.paste(im,(x,y));bd.text((x+10,y+542),f"{sid} frame{sam['frame']} pts{sam['pts']}",fill='black')
    bp=dout/f'board-{k//4:03d}.png';board.save(bp);boards.append(dict(path=rel(bp),sha256=sha(bp)))
   state['results'].append(dict(id=sid,frames=n,output=rel(target),outputSha256=sha(target),priorVideo=row['source'],priorVideoSha256=row['sourceSha256'],priorDecodedToNewEncoderBytesMatched=True,preservedDecoderInputFrames=preserved,preservedDecoderInputSha256=originalhash.hexdigest(),newEncoderInputSha256=passedhash.hexdigest(),preservationScope='Identical RGB bytes fed to encoder for retained actual/frozen intervals, not byte-identical lossy compressed outputs.',newExplanationFrames=len(replaces),decodePriorExitCode=dx,encodeExitCode=ex,wholeDecodeExitCode=whole,extractExitCode=extract,allFramePts1500Matched=True,probe=probe,samples=samples,boards=boards));checkpoint()
   print(json.dumps(dict(scene=sid,frames=n,newExplanationFrames=len(replaces),preservedInputFrames=preserved,samples=len(samples),boards=len(boards))),flush=True)
  for x in protected:assert sha(ROOT/x['path'])==x['sha256']
  assert sum(x['frames'] for x in state['results'])==5617 and sum(x['newExplanationFrames'] for x in state['results'])==1921
  state.update(status='current34-three-detailed-mixed-scenes-rendered-awaiting-direct-review',workerExitCode=0,finishedAt=now(),all79ProtectedShaMatched=True,repairCandidateShaMatched=True,all3696RetainedDecoderInputFramesMatched=True);checkpoint();print(json.dumps(dict(workerExitCode=0,scenes=3,frames=5617,newEX=1921,preservedInputFrames=3696)),flush=True)
 except BaseException as e:
  state.update(status='failed',workerExitCode=1,error=repr(e),traceback=traceback.format_exc(),finishedAt=now());checkpoint();raise
if __name__=='__main__':main()
