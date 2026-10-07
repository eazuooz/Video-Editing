"""Correct only the observed motion-sickness source frame0; preserve the original clip."""
from pathlib import Path
import subprocess,json,hashlib,datetime,os
ROOT=Path(__file__).resolve().parents[3];folder=ROOT/'projects/motion-sickness-games/production/visual-depth-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
review=read(folder/'source-outro-direct-review.json');src=ROOT/review['source'];target=folder/'outro-boundary-fixed.mp4'
if not review['directlyRead'] or not review['oldPptFirstFrameObserved'] or sha(src)!=review['sourceSha256']:raise RuntimeError('Observed exact source rejection required')
if target.exists() or (folder/'outro-boundary-execution.json').exists():raise RuntimeError('Inspect existing correction; do not repeat')
ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';probe='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
cmd=[ff,'-v','error','-threads','2','-i',str(src),'-vf','trim=start_frame=1,settb=1/60,setpts=N,tpad=start=1:start_mode=clone','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-enc_time_base','1:60','-fps_mode','passthrough','-video_track_timescale','90000',str(target)]
state=dict(status='running',pid=os.getpid(),command=cmd,gpu=0,startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
write(folder/'outro-boundary-execution.json',state)
with (folder/'outro-boundary-fix.log').open('w',encoding='utf-8') as f:
 p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000);state['activePid']=p.pid;write(folder/'outro-boundary-execution.json',state);code=p.wait()
if code:raise RuntimeError('Observed boundary correction failed; preserve log')
v=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-of','json',str(target)],text=True))['streams'][0]
if int(v['nb_frames'])!=600 or v['time_base']!='1/90000':raise RuntimeError('Exact 600-frame boundary correction required')
subprocess.run([ff,'-v','error','-threads','2','-i',str(target),'-f','null','-'],check=True,creationflags=0x08000000)
write(folder/'outro-boundary-fix.json',dict(source=review['source'],sourceSha256=sha(src),path=target.relative_to(ROOT).as_posix(),sha256=sha(target),frames=600,fullDecodeExitCode=0,change='Remove only original old-PPT frame0; clone actual original member frame1 once. Source/timing/identities preserved.',command=cmd,pixelsPending=True))
state.update(status='corrected-full-decode-passed-awaiting-direct-pixels',activePid=None,exitCode=0,endedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());write(folder/'outro-boundary-execution.json',state)
print('Observed frame0 corrected; actual encoded final boundary pixels still pending.')
