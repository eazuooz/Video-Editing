"""Single CPU2 render for three overview/conclusion depth repairs; no main promotion."""
from pathlib import Path
from datetime import datetime,timezone
import os,sys,json,hashlib,subprocess,traceback,argparse,importlib.util
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='2'
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
L=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-overview-v4'
M=ROOT/'manim/projects/game-math-orientation-matrices/teaching_overview_revision_v3.py'
T=O/'current34-overview-timing-plan-v3.json';STATE=O/'current34-overview-render-execution-v4.json'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
if '--render' in sys.argv:
 from manim import tempconfig
 from manim.scene.scene_file_writer import SceneFileWriter
 original=SceneFileWriter.open_partial_movie_stream
 def bounded(self,*a,**k):
  original(self,*a,**k);self._current_encode_job.stream.codec_context.thread_count=2
 SceneFileWriter.open_partial_movie_stream=bounded
 sid=sys.argv[sys.argv.index('--render')+1];os.environ['ORIENTATION_OVERVIEW_TIMING']=str(T)
 spec=importlib.util.spec_from_file_location('orientation_overview',M);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 with tempconfig(dict(pixel_width=1920,pixel_height=1080,frame_rate=60,quality='high_quality',renderer='cairo',media_dir=str(L/'manim'),disable_caching=True,max_inflight_encoders=1,verbosity='WARNING')):getattr(mod,'OverviewScene'+sid)().render()
 raise SystemExit(0)
import psutil
from PIL import Image,ImageDraw,ImageFont
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
assert not STATE.exists() and not L.exists()
r=rd(ROOT/a.resource);assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
me=psutil.Process();parent=me.parent();own=[]
for p in psutil.process_iter(['pid','name','cmdline']):
 try:
  c=p.info['cmdline'] or [];cmd=' '.join(c)
  if (p.info['name'] or '').lower() not in ['python.exe','ffmpeg.exe','node.exe']:continue
  if p.pid in [me.pid] or (parent and p.pid==parent.pid and c[1:]==me.cmdline()[1:]):continue
  if ('cross-game-example-coverage-review' in cmd or 'unpublished-teaching-clarity-revision' in cmd) and any(v in cmd for v in ['review-orientation','render-orientation','extract-orientation','build-orientation','assemble-orientation','review-motion','render-motion','extract-motion']):own.append(p.pid)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
assert not own and psutil.virtual_memory().available//1024>8_000_000
proof=rd(O/'narration-07b-guide-repair-execution-v1.json')
protected=proof['protectedInputs']+proof['results']
for v in protected:assert sha(ROOT/v['path'])==v['sha256']
plan=rd(T);assert sha(M)==plan['codeSha256'];assert [s['id'] for s in plan['scenes']]==['01','01b','24']
for s in plan['scenes']:assert sha(ROOT/s['voice'])==s['voiceSha256']
cp=rd(O/'latest-checkpoint.json');assert cp['activeOwnedWorkers']==0
me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS);L.mkdir(parents=True)
state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,resource=a.resource,resourceSha256=sha(ROOT/a.resource),cpuThreads=2,gpuJobs=0,code=rel(M),codeSha256=sha(M),timing=rel(T),timingSha256=sha(T),status='rendering-three-current34-overviews',scenes=[],exitCode=None,actualOuterExitCode=None,allFinalPixelsApproved=False,newImageGit=0,researchChanges=0)
def checkpoint():
 ss=STATE.with_name(STATE.stem+'.session.json')
 if ss.exists():state['sessionId']=rd(ss)['sessionId']
 save(STATE,state)
 cp=rd(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],activeOwnedWorkers=int(state['exitCode'] is None),ownedJob=dict(active=state['exitCode'] is None,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(STATE),currentScene=state.get('currentScene'),cpuThreads=2,gpuJobs=0),next='Directly review all rendered overview/depth samples and normal playback; current mixed context/captions/final pixels remain required. No main promotion/upload.');save(O/'latest-checkpoint.json',cp)
 qp=B/'queue.json';old=qp.read_bytes();q=rd(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=cp['activeOwnedWorkers'],ownedJob=cp['ownedJob'],next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==old;save(qp,q)
checkpoint()
try:
 for s in plan['scenes']:
  sid=s['id'];cmd=[str(ROOT/'manim/.venv/Scripts/python.exe'),'-X','utf8',str(Path(__file__).resolve()),'--render',sid]
  with (L/f'render-{sid}.log').open('wb') as log:
   p=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);state.update(currentScene=sid,childPid=p.pid,childCommand=cmd);checkpoint();ex=p.wait()
  assert ex==0,(sid,ex)
  paths=list((L/'manim/videos').rglob('OverviewScene'+sid+'.mp4'));assert len(paths)==1
  video=paths[0];probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,time_base,nb_frames,duration','-of','json',str(video)],text=True));stream=probe['streams'][0];count=int(stream['nb_frames'])
  assert (stream['width'],stream['height'],stream['r_frame_rate'])==(1920,1080,'60/1') and abs(count-s['frames'])<=1
  folder=L/('scene-'+sid);folder.mkdir()
  with (folder/'decode.log').open('wb') as log:dx=subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(video),'-f','null','-'],stdout=log,stderr=subprocess.STDOUT).returncode
  assert dx==0
  indices=sorted(set([*range(0,count,30),count-1,*[min(count-1,round(t*60)+45) for t in s['lineStarts']]]))
  selection='+'.join(f'eq(n,{n})' for n in indices)
  with (folder/'extract.log').open('wb') as log:xx=subprocess.run([FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(video),'-vf',f"select='{selection}',showinfo",'-fps_mode','passthrough','-frames:v',str(len(indices)),'-threads','2',str(folder/'frame-%03d.png')],stdout=log,stderr=subprocess.STDOUT).returncode
  assert xx==0
  rows=[dict(frame=n,path=rel(folder/f'frame-{i:03d}.png'),sha256=sha(folder/f'frame-{i:03d}.png')) for i,n in enumerate(indices,1)]
  boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
  for off in range(0,len(rows),6):
   im=Image.new('RGB',(1920,780),'#171a1e');draw=ImageDraw.Draw(im)
   for j,v in enumerate(rows[off:off+6]):
    bx=j%3*640;by=j//3*390
    with Image.open(ROOT/v['path']) as f:im.paste(f.resize((640,360)),(bx,by+30))
    draw.text((bx+8,by+5),f'scene{sid} f{v["frame"]}',font=font,fill='white')
   path=folder/f'board-{off//6+1:02d}.png';im.save(path);boards.append(dict(path=rel(path),sha256=sha(path)))
  state['scenes'].append(dict(id=sid,output=rel(video),outputSha256=sha(video),renderExitCode=ex,wholeDecodeExitCode=dx,extractExitCode=xx,probe=probe,plannedFrames=s['frames'],roundingTailFrames=s['frames']-count,samples=rows,boards=boards));checkpoint()
  print(json.dumps(dict(id=sid,frames=count,samples=len(rows),boards=len(boards),decode=dx)),flush=True)
 for v in protected:assert sha(ROOT/v['path'])==v['sha256']
 state.update(status='rendered-current34-overviews-awaiting-direct-pixel-review',exitCode=0,finishedAt=now(),all79ProtectedUnchanged=True);checkpoint()
except BaseException:
 state.update(status='failed-current34-overview-render-preserve-history',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
