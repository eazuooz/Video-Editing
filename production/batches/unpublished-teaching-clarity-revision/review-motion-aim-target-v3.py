from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,subprocess,os,ctypes,psutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
OUT=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/aim-target-qa-v3'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,o):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--render-outer-exit-code',required=True,type=int);args=ap.parse_args()
resource=read(ROOT/args.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
assert args.render_outer_exit_code==0
render=read(R/'aim-target-render-execution-v3.json');assert render['actualExitCode']==0 and len(render['completed'])==1
session=read(R/'aim-target-render-execution-v3.session.json');assert session['sessionId']==49596 and session['pid']==render['pid']
assert not psutil.pid_exists(render['pid'])
assert read(R/'aim-target-render-process-closure-v3.json')['actualOuterExitCode']==0
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
assert not OUT.exists();OUT.mkdir(parents=True)
me=psutil.Process();sp=R/'aim-target-qa-execution-v3.json';assert not sp.exists()
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),startedAt=now(),sessionId=None,status='reviewing-scene02-aim-v3-clean-and-current-captioned-pixels',actualExitCode=None,resource=resource,cpuThreads=2,gpuJobs=0,completed=[],allPixelsDirectlyRead=False)
def checkpoint():
 ss=sp.with_name(sp.stem+'.session.json')
 if ss.exists():
  z=read(ss);assert z['pid']==me.pid;state['sessionId']=z['sessionId']
 save(sp,state)
 cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],ownedJob={k:state[k] for k in ['pid','createTime','commandLine','cwd','sessionId','cpuThreads','gpuJobs','actualExitCode']},allFinalPixelsApproved=False,next='Directly inspect every repaired target sample and normal-speed movement, then assemble/review current v2 pair preserving exact current audio and timings.');save(R/'latest-checkpoint.json',cp)
 qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw);q['execution'].update(stage=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next']);next(x for x in q['items'] if x['slug']=='motion-sickness-games').update(status=cp['stage'],currentExecution=cp['ownedJob']);assert qp.read_text('utf-8-sig')==raw;save(qp,q)
checkpoint()
ass=R/'captions.ko.ass';assert sha(ass)=='63507fcdf1b768e4c36f4b3db65a4a6f5b19a3681ef9fa425b0308f3149939dd'
def run(cmd,log):
 with log.open('wb') as f:code=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=f).returncode
 assert code==0,(code,str(log));return code
def probe(src,n):
 z=json.loads(subprocess.check_output([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_streams','-show_entries','frame=pts:stream=width,height,r_frame_rate,time_base','-of','json',str(src)]))
 assert [int(v['pts']) for v in z['frames']]==list(range(0,n*1500,1500));s=z['streams'][0];assert (s['width'],s['height'],s['r_frame_rate'],s['time_base'])==(1920,1080,'60/1','1/90000');return z
for row in render['completed']:
 src=ROOT/row['path'];assert sha(src)==row['sha256'];n=row['frames'];start=4843 if row['id']=='02' else 20165
 save(OUT/f"scene-{row['id']}-clean-probe.json",probe(src,n))
 dest=OUT/f"scene-{row['id']}-captioned.mp4"
 run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-i',str(src),'-vf',f"setpts=PTS+{start}*1500,subtitles=filename='{ass.relative_to(ROOT).as_posix()}',setpts=PTS-STARTPTS",'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000',str(dest)],OUT/f"scene-{row['id']}-caption.log")
 save(OUT/f"scene-{row['id']}-captioned-probe.json",probe(dest,n))
 samples=set(range(0,n,30))|{0,n-1}
 if row['id']=='02':samples|=set(range(1640,1770,10))|{643,1114,1728,1729}
 else:samples|={1,15,150,235,300,359}
 for variant,p in [('clean',src),('captioned',dest)]:
  log=(OUT/f"scene-{row['id']}-{variant}-decode.log").open('wb')
  proc=subprocess.Popen([FF,'-hide_banner','-v','error','-threads','2','-i',str(p),'-an','-threads','2','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=log)
  frames=[];selected=[];size=1920*1080*3
  for f in range(n):
   data=bytearray()
   while len(data)<size:
    block=proc.stdout.read(size-len(data));assert block,(f,len(data));data.extend(block)
   a=np.frombuffer(data,dtype=np.uint8).reshape(1080,1920,3)
   below=int(np.any(a[910:]<235,axis=2).sum()) if variant=='clean' else None
   frames.append(dict(frame=f,pts=f*1500,nonWhitePixelsBelow910=below,decodedRgbSha256=hashlib.sha256(data).hexdigest()))
   if f in samples:
    p1=OUT/f"scene-{row['id']}-{variant}-{f:05d}.png";Image.fromarray(a).save(p1);selected.append(dict(frame=f,finalFrame=start+f,pts=f*1500,path=rel(p1),sha256=sha(p1)))
  assert proc.stdout.read(1)==b'';code=proc.wait();log.close();assert code==0
  if variant=='clean':assert max(v['nonWhitePixelsBelow910'] for v in frames)==0
  save(OUT/f"scene-{row['id']}-{variant}-frames.json",frames)
  boards=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
  for bi in range(0,len(selected),6):
   subset=selected[bi:bi+6];im=Image.new('RGB',(1440,1296),(30,30,30));d=ImageDraw.Draw(im)
   for k,v in enumerate(subset):
    x=k%2*720;y=k//2*432;im.paste(Image.open(ROOT/v['path']).resize((720,405)),(x,y));d.text((x+8,y+406),f"{row['id']} {variant} f{v['frame']} final{v['finalFrame']}",fill='white',font=font)
   p1=OUT/f"scene-{row['id']}-{variant}-board-{bi//6+1:02d}.png";im.save(p1);boards.append(dict(path=rel(p1),sha256=sha(p1),frames=[v['frame'] for v in subset]))
  state['completed'].append(dict(id=row['id'],variant=variant,source=rel(p),sourceSha256=sha(p),frames=n,allPts1500=True,actualWholeDecodeExitCode=code,samples=selected,boards=boards,maxNonWhitePixelsBelow910=0 if variant=='clean' else None));checkpoint()
state.update(status='scene02-aim-v3-current-captioned-samples-awaiting-direct-review',actualExitCode=0,endedAt=now());checkpoint();print(json.dumps(dict(actualExitCode=0,sampleCount=sum(len(v['samples']) for v in state['completed']),boards=sum(len(v['boards']) for v in state['completed']))),flush=True)
