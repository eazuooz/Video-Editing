"""Normalize the local clean master clock without touching captioned pixels or audio."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, os, traceback
ROOT=Path(__file__).resolve().parents[3]; W=Path(__file__).resolve().parent/'final-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'; FP=FF.replace('ffmpeg','ffprobe')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
execution=W/'clean-clock-execution.json'; assert not execution.exists()
r=read(W/'render-result.json'); captioned=ROOT/r['captioned']; assert sha(captioned)==r['captionedSha256']
clean=ROOT/r['clean']; assert sha(clean)==r['cleanSha256']=='34666addfa5f714da944b19d891f88831eaae2f9b4050faa19194932a0065230'
invalid=W/'avoid-game-comparisons.clean.invalid-concat-pts.mp4'; assert not invalid.exists()
write(W/'render-result-before-clean-clock-repair.json',r)
technical=read(W/'technical-execution.json'); technical.update(status='failed-clean-concat-pts',exitCode=1,endedAt=now(),sessionId=69358,reason='Decoded clean frame 120 PTS 175505 instead of 180000; average-rate/header checks alone were insufficient.')
write(W/'technical-execution-failed-clean-clock.json',technical)
r.update(done=False,status='clean-clock-repair-in-progress',technicalQa=False);write(W/'render-result.json',r)
clean.rename(invalid)
state=dict(pid=os.getpid(),status='running',startedAt=now(),sessionId=None,commands=[],newTts=0,newMix=0,changedCaptioned=False,changedSubtitles=False,sourceCleanSha256=sha(invalid),preservedCaptionedSha256=sha(captioned))
def save():write(execution,state)
def run(args,label,capture=False):
 log=W/(label+'.log')
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.PIPE if capture else f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
  state['activeChild']=dict(pid=p.pid,command=args,log=rel(log));save();out=p.communicate()[0]
 state['commands'].append(dict(**state['activeChild'],exitCode=p.returncode));state['activeChild']=None;save();assert p.returncode==0
 return out.decode('utf-8') if capture else log.read_text(encoding='utf-8')
save()
try:
 args=[FF,'-hide_banner','-y','-threads','2','-reinit_filter','0','-i',str(invalid),'-filter_threads','2','-vf','settb=1/90000,setpts=N*1500,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-fps_mode','passthrough','-frames:v','32100','-t','535','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',str(clean)]
 log=run(args,'clean-clock-encode');assert 'Non-monotonic' not in log
 pr=json.loads(run([FP,'-v','error','-show_streams','-show_format','-of','json',str(clean)],'clean-clock-probe',True));v=next(s for s in pr['streams'] if s['codec_type']=='video')
 assert (v['width'],v['height'],v['r_frame_rate'],v['avg_frame_rate'],int(v['nb_frames']),v['time_base'])==(1920,1080,'60/1','60/1',32100,'1/90000')
 assert abs(float(v['duration'])-535)<.000001
 pts=json.loads(run([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(clean)],'clean-clock-frame-pts',True))['frames'];assert len(pts)==32100
 for n,f in enumerate(pts):assert int(f['best_effort_timestamp'])==n*1500,(n,f)
 assert sha(captioned)==state['preservedCaptionedSha256']
 result=dict(observedAt=now(),path=rel(clean),sha256=sha(clean),preservedCaptionedSha256=sha(captioned),archivedInvalidClean=rel(invalid),sourceCleanSha256=sha(invalid),frames=32100,seconds=535,allFramePtsExact=True,ptsStep=1500,timeBase='1/90000',newMix=0,newTts=0,subtitlesChanged=False,fullDecodeAndIdenticalAacPending=True)
 write(W/'clean-clock-result.json',result)
 r=read(W/'render-result-before-clean-clock-repair.json');r.update(done=True,status='two-current-review-videos-awaiting-QA',cleanSha256=result['sha256'],cleanProbe=pr,cleanExactFramePts=result,technicalQa=False,allFinalCaptionPixelsApproved=False);write(W/'render-result.json',r)
 state.update(status='finished',exitCode=0,endedAt=now());save();print(json.dumps(result))
except Exception:
 traceback.print_exc();state.update(status='failed',exitCode=1,endedAt=now());save();raise
