"""Keep one filter clock across homogeneous concat segments; validate every frame PTS."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,subprocess,os,sys,traceback
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
stage=sys.argv[1]; assert stage in ['pilot','full']
execution=W/f'caption-clock-{stage}-execution.json'; assert not execution.exists()
clean=W/'avoid-game-comparisons.clean.review.mp4'; assert sha(clean)=='34666addfa5f714da944b19d891f88831eaae2f9b4050faa19194932a0065230'
plan=read(W/'plan.json'); assert plan['finalFrames']==32100 and plan['body60_40ErrorFrames']==0
state=dict(stage=stage,pid=os.getpid(),sessionId=None,status='running',startedAt=now(),commands=[],newTts=0,newMix=0,changedSubtitles=False)
def save():write(execution,state)
def run(args,label,capture=False):
 log=W/(label+'.log')
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.PIPE if capture else f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
  state['activeChild']=dict(pid=p.pid,command=args,log=rel(log));save();out=p.communicate()[0]
 state['commands'].append(dict(**state['activeChild'],exitCode=p.returncode));state['activeChild']=None;save();assert p.returncode==0
 return out.decode('utf-8') if capture else log.read_text(encoding='utf-8')
def validate(video,count):
 pr=json.loads(run([FP,'-v','error','-count_frames','-threads','2','-show_streams','-show_format','-of','json',str(video)],f'caption-clock-{stage}-probe',True))
 v=next(s for s in pr['streams'] if s['codec_type']=='video')
 assert (v['width'],v['height'],v['r_frame_rate'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'60/1','60/1',count),v
 assert abs(float(v['duration'])-count/60)<.000001
 ticks=json.loads(run([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(video)],f'caption-clock-{stage}-frame-pts',True))['frames']
 assert v['time_base']=='1/90000' and len(ticks)==count
 for n,f in enumerate(ticks):assert int(f['best_effort_timestamp'])==n*1500,(n,f)
 return dict(probe=pr,allFramePtsExact=True,framePtsCount=count,firstPts=0,lastPts=(count-1)*1500,timeBase='1/90000',ptsStep=1500)
save()
try:
 if stage=='pilot':
  old=read(W/'render-result.json'); assert old['captionedSha256']=='4dd37094eb1645e243aaa4a7569ca17c2a94b7e597b1d1921c939197236f9e2b'
  invalid=W/'avoid-game-comparisons.captioned.invalid-reset-clock.mp4'; assert not invalid.exists()
  src=ROOT/old['captioned'];assert sha(src)==old['captionedSha256'];src.rename(invalid)
  write(W/'render-result-invalid-reset-clock.json',old)
  old.update(done=False,status='rejected-reset-filter-clock',technicalQa=False,allFinalCaptionPixelsApproved=False,rejection='Frame count passed but color-property graph reinitialization reset N; video duration 509.616667s, avg_frame_rate 1926000/30577.')
  write(W/'render-result.json',old)
  failed=W/'pixel-review-v1';target=W/'pixel-review-invalid-reset-clock'
  assert failed.resolve().is_relative_to(ROOT.resolve()) and target.resolve().is_relative_to(ROOT.resolve()) and not target.exists()
  st=read(failed/'execution.json');st.update(status='failed-wrong-caption-clock',sessionId=21158,exitCode=1,endedAt=now(),actualImages=484,expectedImages=532,reason='Caption video timeline compressed by reset filter clock; frame selection returned 484/532. No pixel approval.')
  write(failed/'execution.json',st);failed.rename(target)
  write(W/'caption-clock-reset-failure.json',dict(observedAt=now(),archivedCaptioned=rel(invalid),sha256=sha(invalid),cleanUnchanged=sha(clean),rejectedRenderResult=rel(W/'render-result-invalid-reset-clock.json'),failedPixelReview=rel(target),cause='Default filter reinitialization on input color metadata change loses N and buffered frames.',documentation='https://ffmpeg.org/ffmpeg.html',correction='Disable input reinitialization only after checking every input has identical dimensions/pixel format; assign one exact frame clock.'))
 else:assert read(W/'caption-clock-pilot-result.json')['allFramePtsExact']
 count=1800 if stage=='pilot' else 32100
 output=W/('caption-clock-pilot.mp4' if stage=='pilot' else 'avoid-game-comparisons.captioned.review.mp4');assert not output.exists()
 vf=f'settb=1/90000,setpts=N*1500,subtitles={rel(W/"captions.ko.ass")},setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709'
 args=[FF,'-hide_banner','-y','-threads','2','-reinit_filter','0','-i',str(clean),'-filter_threads','2','-vf',vf,'-fps_mode','passthrough','-frames:v',str(count),'-t',str(count/60),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',str(output)]
 log=run(args,f'caption-clock-{stage}-encode');assert 'Non-monotonic' not in log and 'Reconfiguring filter graph' not in log
 result=dict(createdAt=now(),path=rel(output),sha256=sha(output),frames=count,seconds=count/60,noNonmonotonicDtsWarnings=True,filterReinitializationDisabled=True,sourceCleanSha256=sha(clean),subtitlesSha256=sha(W/'captions.ko.ass'),**validate(output,count))
 write(W/f'caption-clock-{stage}-result.json',result)
 if stage=='full':
  original=read(W/'render-result-invalid-reset-clock.json')
  original.update(createdAt=now(),status='two-current-review-videos-awaiting-QA',done=True,captionedSha256=result['sha256'],captionedProbe=result['probe'],exactFramePts=result,technicalQa=False,allFinalCaptionPixelsApproved=False)
  write(W/'render-result.json',original)
 state.update(status='finished',exitCode=0,endedAt=now());save();print(json.dumps({k:result[k] for k in ['frames','seconds','sha256','allFramePtsExact']}))
except Exception:
 traceback.print_exc();state.update(status='failed',exitCode=1,endedAt=now());save();sys.exit(1)
