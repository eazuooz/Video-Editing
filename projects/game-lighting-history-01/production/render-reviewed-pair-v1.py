"""Create and verify one captioned/clean pair from the reviewed current mix."""
import pathlib,json,hashlib,datetime,subprocess,os
import psutil
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sh(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['publishingAuthorization']['privateUploadForMobileReview']
 plan=rd(O/'plan.json');v=rd(O/'visual-execution.json');m=rd(O/'mix-execution.json');review=rd(O/'mixed-asr-direct-review.json');captions=rd(O/'captions.json')
 assert v['status']=='complete-awaiting-final-pair' and v['sha256']==sh(O/'silent-visual.mp4')
 assert review['allCurrentMixedTextsDirectlyCompared'] and review['contentCoverageApproved'] and review['mixSha256']==sh(O/'final-mix.wav')
 assert captions['allCueTextDirectReview'] and captions['planSha256']==sh(O/'plan.json')
 assert not (O/'pair-execution.json').exists(),'Inspect current output; never restart completed pair.'
 state=dict(status='running',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,planSha256=sh(O/'plan.json'),inputHashes={n:sh(O/n) for n in ['silent-visual.mp4','final-mix.m4a','captions.ko.ass','mixed-asr-direct-review.json']},steps=[],outputs={})
 def save():wr(O/'pair-execution.json',state)
 def run(label,cmd):
  log=O/(label+'.log');state['active']=dict(label=label,command=cmd,log=log.relative_to(R).as_posix());save()
  with log.open('w',encoding='utf8') as f:rc=subprocess.call(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  state['steps'].append(dict(label=label,exitCode=rc));save();assert rc==0,(label,rc)
 save()
 try:
  clean=O/'clean.mp4';captioned=O/'captioned.mp4'
  base=[FF,'-hide_banner','-nostdin','-n','-threads','2','-i',str(O/'silent-visual.mp4'),'-i',str(O/'final-mix.m4a'),'-map','0:v:0','-map','1:a:0']
  run('pair-clean',base+['-c:v','copy','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',str(clean)])
  ass=(O/'captions.ko.ass').relative_to(R).as_posix();fonts=(O/'fonts').relative_to(R).as_posix()
  run('pair-captioned',base+['-vf',f"ass='{ass}':fontsdir='{fonts}'",'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-r','60','-frames:v',str(plan['frames']),'-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',str(captioned)])
  for name,f in [('clean',clean),('captioned',captioned)]:
   run(name+'-whole-decode',[FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(f),'-f','null','-'])
   meta=json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(f)],text=True,creationflags=subprocess.CREATE_NO_WINDOW));stream=next(x for x in meta['streams'] if x['codec_type']=='video')
   assert stream['width']==1920 and stream['height']==1080 and stream['r_frame_rate']=='60/1' and stream['time_base']=='1/90000'
   proc=subprocess.Popen([FP,'-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp','-of','csv=p=0',str(f)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
   count=0
   for line in proc.stdout:
    s=line.strip().split(',')[0]
    if not s:continue
    pts=int(s);assert pts==count*1500,(name,count,pts);count+=1
   assert proc.wait()==0 and count==plan['frames']
   adts=O/(name+'.aac');run(name+'-aac-extract',[FF,'-hide_banner','-nostdin','-n','-i',str(f),'-vn','-c:a','copy','-f','adts',str(adts)])
   state['outputs'][name]=dict(path=f.relative_to(R).as_posix(),sha256=sh(f),bytes=f.stat().st_size,frames=count,duration=float(meta['format']['duration']),videoSeconds=float(stream['duration']),wholeDecodeExit=0,ptsEveryFrame1500=True,timeBase=90000,aacSha256=sh(adts));save()
  assert state['outputs']['clean']['aacSha256']==state['outputs']['captioned']['aacSha256']
  assert all(abs(x['videoSeconds']-plan['seconds'])<.001 for x in state['outputs'].values())
  state.update(status='complete-awaiting-current-encoded-pixel-review',endedAt=now(),exitCode=0,active=None,identicalAac=True,loudnessReusedFromIdenticalInputAAC=m['loudness'],allFinalPixelsApproved=False);save()
 except BaseException as e:state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()
