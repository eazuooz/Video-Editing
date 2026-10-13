"""Sequential CPU framing/trim assembly from immutable completed explanation assets."""
import pathlib,json,hashlib,datetime,subprocess,os,sys,runpy
import psutil
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
framing=runpy.run_path(str(P/'production/final-framing-v1.py'))
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['publishingAuthorization']['privateUploadForMobileReview']
 plan=rd(O/'plan.json');assert plan['finalTimingApproved']
 rev=rd(O/'framing-preflight-review.json');assert rev['approved'] and rev['planSha256']==sh(O/'plan.json') and rev['framingCodeSha256']==sh(P/'production/final-framing-v1.py')
 execution=O/'visual-execution.json'
 assert not execution.exists(),'Inspect actual completion; do not repeat rendering.'
 segments=O/'segments';segments.mkdir(exist_ok=True)
 state=dict(status='running',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,planSha256=sh(O/'plan.json'),framingCodeSha256=sh(P/'production/final-framing-v1.py'),completed=[],active=None)
 def save():wr(execution,state)
 def run(label,cmd):
  log=O/(label+'.log');state['active']=dict(label=label,command=cmd,log=log.relative_to(R).as_posix());save()
  with log.open('w',encoding='utf8') as f:rc=subprocess.call(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  assert rc==0,(label,rc)
 def probe(f):
  return json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,r_frame_rate,time_base,nb_read_frames,duration','-of','json',str(f)],text=True,creationflags=subprocess.CREATE_NO_WINDOW))['streams'][0]
 save()
 try:
  for n in plan['nodes']:
   out=segments/(n['id']+'.mp4');assert not out.exists()
   if n['role'] in ['branding','membership']:
    assert sh(R/n['path'])==n['sha256'];cmd=[FF,'-hide_banner','-nostdin','-n','-i',str(R/n['path']),'-map','0:v:0','-c:v','copy','-an','-video_track_timescale','90000',str(out)]
   else:
    filt=framing['filtergraph'](n) if n.get('sourceId') else f"[0:v]fps=60:start_time=0,trim=end_frame={n['frames']},setpts=N/(60*TB),setsar=1,format=yuv420p[out]"
    fp=O/(n['id']+'.filter.txt');fp.write_text(filt,encoding='utf8')
    cmd=[FF,'-hide_banner','-nostdin','-n','-threads','2','-ss',f"{n['sourceStartFrame']/60:.9f}",'-i',str(R/n['path']),'-filter_complex_threads','2','-filter_complex_script',str(fp),'-map','[out]','-an','-frames:v',str(n['frames']),'-r','60','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(out)]
   run('segment-'+n['id'],cmd);v=probe(out)
   assert int(v['nb_read_frames'])==n['frames'] and v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1' and v['time_base']=='1/90000',(n['id'],v)
   state['completed'].append(dict(id=n['id'],path=out.relative_to(R).as_posix(),sha256=sh(out),probe=v));save();print('DONE',n['id'],len(state['completed']),len(plan['nodes']),flush=True)
  filelist=O/'visual-concat.txt';filelist.write_text('\n'.join("file '"+str(R/x['path']).replace('\\','/')+"'" for x in state['completed'])+'\n',encoding='utf8')
  visual=O/'silent-visual.mp4';run('visual-concat',[FF,'-hide_banner','-nostdin','-n','-f','concat','-safe','0','-i',str(filelist),'-map','0:v:0','-c:v','copy','-an','-video_track_timescale','90000','-movflags','+faststart',str(visual)])
  v=probe(visual);assert int(v['nb_read_frames'])==plan['frames']
  run('visual-decode',[FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(visual),'-f','null','-'])
  state.update(status='complete-awaiting-final-pair',endedAt=now(),exitCode=0,active=None,output=visual.relative_to(R).as_posix(),sha256=sh(visual),probe=v,wholeDecodeExit=0,finalPixelsApproved=False);save()
 except BaseException as e:
  state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()
