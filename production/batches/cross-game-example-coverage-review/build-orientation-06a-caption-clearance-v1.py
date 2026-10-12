"""One CPU2/GPU0 06a render and actual current-caption binding; no audio work."""
from pathlib import Path
from datetime import datetime,timezone
import os,sys,json,hashlib,subprocess,traceback,argparse,importlib.util
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='2'
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
L=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-06a-caption-clearance-v1'
T=O/'current34-06a-caption-clearance-timing-v1.json';STATE=O/'current34-06a-caption-clearance-execution-v1.json'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
if '--render' in sys.argv:
 from manim import tempconfig
 from manim.scene.scene_file_writer import SceneFileWriter
 original=SceneFileWriter.open_partial_movie_stream
 def bounded(self,*a,**k):
  original(self,*a,**k);self._current_encode_job.stream.codec_context.thread_count=2
 SceneFileWriter.open_partial_movie_stream=bounded
 plan=rd(T);os.environ['ORIENTATION_REVISION_TIMING']=str(T)
 spec=importlib.util.spec_from_file_location('orientation_06a_clearance',ROOT/plan['code']);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 with tempconfig(dict(pixel_width=1920,pixel_height=1080,frame_rate=60,quality='high_quality',renderer='cairo',media_dir=str(L/'manim'),disable_caching=True,max_inflight_encoders=1,verbosity='WARNING')):mod.DetailedScene06a().render()
 raise SystemExit(0)
import psutil
from PIL import Image,ImageDraw,ImageFont
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
assert not STATE.exists() and not L.exists()
r=rd(ROOT/a.resource);assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
me=psutil.Process();own=[]
for p in psutil.process_iter(['pid','name','cmdline']):
 try:
  c=p.info['cmdline'] or [];cmd=' '.join(c)
  if p.pid==me.pid or (me.parent() and p.pid==me.parent().pid and c[1:]==me.cmdline()[1:]):continue
  if (p.info['name'] or '').lower() in ['python.exe','ffmpeg.exe','node.exe'] and 'cross-game-example-coverage-review' in cmd and any(v in cmd for v in ['review-orientation','render-orientation','extract-orientation','build-orientation','assemble-orientation','review-motion','render-motion','extract-motion']):own.append(p.pid)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
assert not own and psutil.virtual_memory().available//1024>8_000_000 and rd(O/'latest-checkpoint.json')['activeOwnedWorkers']==0
subprocess.run(['node','scripts/review-video-duplicates.cjs','game-math-orientation-matrices','--candidate-file',str(O/'duplicate-candidate-v1.json'),'--check'],cwd=ROOT,check=True)
proof=rd(O/'narration-07b-guide-repair-execution-v1.json');protected=proof['protectedInputs']+proof['results']
for v in protected:assert sha(ROOT/v['path'])==v['sha256']
plan=rd(T)
for v in plan['assets']:assert sha(ROOT/v['path'])==v['sha256']
for pk,hk in [('findings','findingsSha256'),('finalV4Review','finalV4ReviewSha256'),('priorPair','priorPairSha256'),('ass','assSha256')]:assert sha(ROOT/plan[pk])==plan[hk]
slot=plan['scenes'][0];assert sha(ROOT/slot['voice'])==slot['voiceSha256'] and sha(ROOT/plan['priorPiece']['path'])==plan['priorPiece']['sha256']
L.mkdir(parents=True);me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,resource=a.resource,resourceSha256=sha(ROOT/a.resource),cpuThreads=2,gpuJobs=0,code=rel(Path(__file__).resolve()),codeSha256=sha(Path(__file__).resolve()),timing=rel(T),timingSha256=sha(T),status='building-single-06a-current-caption-clearance',scenes=[],jobs=[],exitCode=None,actualOuterExitCode=None,newTts=0,newAsr=0,newMix=0,final244CaptionPixelsApproved=False,newImageGit=0,researchChanges=0)
def checkpoint():
 ss=STATE.with_name(STATE.stem+'.session.json')
 if ss.exists():state['sessionId']=rd(ss)['sessionId']
 state['updatedAt']=now();save(STATE,state)
 cp=rd(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],activeOwnedWorkers=int(state['exitCode'] is None),ownedJob=dict(active=state['exitCode'] is None,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(STATE),cpuThreads=2,gpuJobs=0),next='Inspect only newly repaired06a current-caption samples and normal endpoints; preserve all prior finalV4 direct pixels. Then bind finalV5 and changed final QA before promotion.');save(O/'latest-checkpoint.json',cp)
 qp=B/'queue.json';old=qp.read_bytes();q=rd(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=cp['activeOwnedWorkers'],ownedJob=cp['ownedJob'],next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==old;save(qp,q)
def run(cmd,log):
 with log.open('wb') as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);v=dict(pid=p.pid,createTime=psutil.Process(p.pid).create_time(),commandLine=cmd,log=rel(log));state['jobs'].append(v);checkpoint();ex=p.wait();v['exitCode']=ex;checkpoint();assert ex==0,(cmd,ex)
 return ex
checkpoint()
try:
 rx=run([str(ROOT/'manim/.venv/Scripts/python.exe'),'-X','utf8',str(Path(__file__).resolve()),'--render'],L/'render-06a.log')
 paths=list((L/'manim/videos').rglob('DetailedScene06a.mp4'));assert len(paths)==1;source=paths[0]
 probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',str(source)]));v=probe['streams'][0];count=int(v['nb_frames']);frames=slot['frames'];pad=frames-count
 assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1') and pad in (0,1)
 dx=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(source),'-f','null','-'],L/'silent-decode.log')
 absolute=plan['absoluteStartFrame'];captioned=L/'06a.current-captioned.mp4'
 filter=f'tpad=stop_mode=clone:stop_duration={pad/60:.12f},trim=end_frame={frames},settb=1/90000,setpts=N*1500+{absolute*1500},ass={plan["ass"]},setpts=PTS-STARTPTS,setsar=1'
 cx=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-i',str(source),'-vf',filter,'-frames:v',str(frames),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000',str(captioned)],L/'caption-binding.log')
 captionprobe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',str(captioned)]));cv=captionprobe['streams'][0]
 assert (cv['width'],cv['height'],cv['r_frame_rate'],cv['time_base'],int(cv['nb_frames']))==(1920,1080,'60/1','1/90000',frames)
 cdx=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(captioned),'-f','null','-'],L/'caption-decode.log')
 oldpixels=rd(O/'current34-pair-pixel-execution-v3.json')['results'][0]['samples']
 wanted=sorted({0,frames-1,*range(0,frames,60),*[x['frame']-absolute for x in oldpixels if absolute<=x['frame']<absolute+frames],*[min(frames-1,round(t*60)+45) for t in slot['lineStarts']]})
 select='+'.join(f'eq(pts\\,{f*1500})' for f in wanted)
 xx=run([FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(captioned),'-vf','select='+select,'-fps_mode','passthrough','-frames:v',str(len(wanted)),'-threads','2',str(L/'sample-%04d.png')],L/'extract.log')
 paths=sorted(L.glob('sample-*.png'));assert len(paths)==len(wanted)
 samples=[dict(frame=f,absoluteFrame=absolute+f,pts=f*1500,path=rel(p),sha256=sha(p)) for f,p in zip(wanted,paths)]
 boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
 for off in range(0,len(samples),4):
  im=Image.new('RGB',(1920,1140),'#171a1e');draw=ImageDraw.Draw(im)
  for j,x in enumerate(samples[off:off+4]):
   bx=j%2*960;by=j//2*570
   with Image.open(ROOT/x['path']) as picture:im.paste(picture.resize((960,540)),(bx,by+30))
   draw.text((bx+8,by+3),f'06a local{x["frame"]} final{x["absoluteFrame"]}',font=font,fill='white')
  p=L/f'board-{off//4+1:03d}.png';im.save(p);boards.append(dict(path=rel(p),sha256=sha(p)))
 state['scenes']=[dict(id='06a',source=rel(source),sourceSha256=sha(source),output=rel(captioned),outputSha256=sha(captioned),plannedFrames=frames,absoluteStartFrame=absolute,explanationTailPadFrames=pad,renderExitCode=rx,captionBindingExitCode=cx,wholeDecodeExitCode=dx,captionWholeDecodeExitCode=cdx,extractExitCode=xx,probe=captionprobe,sourceProbe=probe,samples=samples,boards=boards)]
 for v in protected:assert sha(ROOT/v['path'])==v['sha256']
 state.update(status='built-single-06a-current-caption-clearance-awaiting-direct-review',exitCode=0,finishedAt=now(),all79ProtectedUnchanged=True,repairCandidateUnchanged=True);checkpoint()
 print(json.dumps(dict(id='06a',frames=frames,sourceFrames=count,samples=len(samples),boards=len(boards),newAudio=0)),flush=True)
except BaseException:
 state.update(status='failed-single-06a-current-caption-clearance-preserve-history',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
