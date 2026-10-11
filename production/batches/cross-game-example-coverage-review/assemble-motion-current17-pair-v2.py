"""Guarded current17 pair: reuse20 originals and14 reviewed additions, mask/split3 only."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,traceback
os.environ['OMP_NUM_THREADS']='2'
import psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
LOCAL=ROOT/'shared/output/cross-game-example-coverage/motion/current17-final-pair-v2'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def probe(p):return json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-of','json',str(p)]))
def ptscheck(p,n):
 frames=json.loads(subprocess.check_output([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(p)]))['frames']
 assert [int(v['pts']) for v in frames]==list(range(0,n*1500,1500)),str(p)
 s=next(v for v in probe(p)['streams'] if v['codec_type']=='video')
 assert (s['width'],s['height'],s['r_frame_rate'],s['time_base'])==(1920,1080,'60/1','1/90000')
 return s
def audiohash(p):
 packets=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(p)]))['packets']
 rows=[v['data_hash'] for v in packets];assert rows
 return dict(packets=len(rows),orderedPacketHashesSha256=hashlib.sha256('\n'.join(rows).encode()).hexdigest())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
 resource=read(ROOT/args.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
 assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
 subprocess.run([NODE,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
 review=read(R/'current17-mixed-complete-direct-review-v2.json')
 assert review['all17WholeAnd81IndependentContextsDirectlyCompared'] and review['currentMixedContentReviewPassed']
 mix=read(R/'current-mix-execution-v2.json');assert mix['actualExitCode']==0
 assert review['mixAacSha256']==mix['mixAacSha256']==sha(ROOT/mix['mixAac'])
 plan=read(R/'measured-current17-plan-v2.json');inputs=read(R/'current17-assembly-inputs-v2.json')
 assert inputs['planSha256']==sha(R/'measured-current17-plan-v2.json') and abs(plan['ratioErrorFrames'])<=1
 layout=read(R/'caption-layout-v1.json');assert layout['allCuesMeasured'] and not layout['unresolvedLayoutErrors']
 assert read(R/'caption-alignment-v1.json')['allNewCueTimingDirectlyReviewed'],'Read all41 actual caption timing rows against current words and PCM before assembly.'
 assert layout['mixAacSha256']==mix['mixAacSha256']
 ass=ROOT/layout['ass'];assert sha(ass)==layout['assSha256']
 for v in mix['protectedInputs']:assert sha(ROOT/v['path'])==v['sha256']
 sp=R/'current17-final-pair-execution-v2.json';assert not sp.exists() and not LOCAL.exists()
 LOCAL.mkdir(parents=True);me=psutil.Process();ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
 state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,startedAt=now(),status='preparing-current17-pair',exitCode=None,resource=resource,cpuThreads=2,gpuJobs=0,pieces=[],jobs=[],allFinalPixelsApproved=False,finalRatioApproved=False,qaApproved=False,humanListeningApproved=False,publicRightsApproved=False,researchManipulations=0,newGitMedia=0)
 def checkpoint():
  ss=sp.with_name(sp.stem+'.session.json')
  if ss.exists():
   row=read(ss);assert row['pid']==me.pid and abs(row['createTime']-me.create_time())<.01;state['sessionId']=row['sessionId']
  state['updatedAt']=now();save(sp,state)
  cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],activeOwnedWorkers=0 if state['exitCode'] is not None else 1,ownedJob=dict(active=state['exitCode'] is None,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(sp),cpuThreads=2,gpuJobs=0,exitCode=state['exitCode']),qaApproved=False,allFinalPixelsApproved=False,next='Observe actual pair exit; review all current narration-timed caption/cut/annotation pixels, collect4files, one private replacement/settings/Git, then actual current Studio schedule and only corresponding obsolete deletion.')
  save(R/'latest-checkpoint.json',cp)
  qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
  q['currentMotionReview'].update(stage=cp['stage'],activeOwnedWorkers=cp['activeOwnedWorkers'],currentPairExecution=rel(sp));q.update(recordedAt=now(),next=cp['next'])
  assert qp.read_text('utf-8-sig')==raw;save(qp,q)
 def run(args,name):
  cmd=[FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args];state.update(status=name,currentCommand=cmd);checkpoint()
  log=LOCAL/(name+'.log')
  with log.open('wb') as f:x=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=f).returncode
  state['jobs'].append(dict(stage=name,exitCode=x,log=rel(log)));checkpoint();assert x==0,name
  print(json.dumps(dict(stage=name,exitCode=x)),flush=True)
 checkpoint()
 try:
  for row in inputs['pieces']:
   p=ROOT/row['path'];assert sha(p)==row['sha256']
   if row['reencodeRequired']:
    target=LOCAL/(row['id']+'.clean.mp4');a=row['sourceOutputStartFrame'];b=a+row['frames']
    filt=f'[0:v]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,crop=1920:900:0:0,split=2[upper][bg];[bg]scale=1920:1080,boxblur=40:2[blur];[blur][upper]overlay=0:0,setsar=1[v]'
    run(['-i',str(p),'-filter_complex',filt,'-map','[v]','-an','-frames:v',str(row['frames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000',str(target)],'mask-preview-'+row['id'])
    ptscheck(target,row['frames']);piece={**row,'preparedFromPath':row['path'],'preparedFromSha256':row['sha256'],'path':rel(target),'sha256':sha(target),'previewCaptionPixelsExcluded':True,'finalMaskPixelsApproved':False}
   else:piece={**row,'reencoded':False}
   state['pieces'].append(piece);checkpoint()
  assert len(state['pieces'])==37 and sum(v['frames'] for v in state['pieces'])==plan['totalFrames']
  concat=LOCAL/'current37.ffconcat';concat.write_text('ffconcat version 1.0\n'+''.join(f"file '{(ROOT/v['path']).as_posix()}'\nduration {v['frames']/60:.12f}\n" for v in state['pieces']),'utf-8')
  joined=LOCAL/'joined.unsnapped.mp4';aac=ROOT/mix['mixAac']
  run(['-f','concat','-safe','0','-i',str(concat),'-i',str(aac),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(plan['seconds']),'-video_track_timescale','90000','-movflags','+faststart',str(joined)],'concat37-with-current17-AAC')
  packets=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','json',str(joined)]))['packets']
  ordered=sorted(int(v['pts']) for v in packets);assert len(ordered)==plan['totalFrames'] and all(abs(t-i*1500)<=2 for i,t in enumerate(ordered))
  clean=LOCAL/'motion-sickness-games.clean.mp4';captioned=LOCAL/'motion-sickness-games.captioned.mp4'
  run(['-i',str(joined),'-map','0:v:0','-map','0:a:0','-c','copy','-bsf:v','setts=pts=round(PTS/1500)*1500:dts=round(DTS/1500)*1500:duration=1500','-video_track_timescale','90000','-movflags','+faststart',str(clean)],'snap37-PTS')
  ptscheck(clean,plan['totalFrames'])
  run(['-i',str(clean),'-map','0:v:0','-map','0:a:0','-vf',f'ass={rel(ass)},setsar=1','-frames:v',str(plan['totalFrames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',str(captioned)],'fixed-current17-KO-captions')
  ah=audiohash(aac);pair=[]
  for p in [clean,captioned]:
   video=ptscheck(p,plan['totalFrames']);run(['-i',str(p),'-f','null','-'],p.stem+'-whole-decode')
   audio=audiohash(p);assert audio==ah
   pair.append(dict(path=rel(p),sha256=sha(p),size=p.stat().st_size,video=video,audioPacketProof=audio,wholeDecodeExitCode=0,allPts1500Verified=True,identicalReviewedWholeAacPackets=True))
  for v in mix['protectedInputs']:assert sha(ROOT/v['path'])==v['sha256']
  state.update(status='current17-pair-encoded-awaiting-all-final-pixels',exitCode=0,finishedAt=now(),frames=plan['totalFrames'],seconds=plan['seconds'],pair=pair,all71ProtectedInputsUnchanged=True,retainedByteIdenticalPieceCount=20,originalIntroFrames=120,originalMemberFrames=600,currentAudioPacketProof=ah,bodyMeasured=dict(frames=plan['bodyFrames'],actual=plan['actualFrames'],explanation=plan['explanationFrames'],ratioErrorFrames=plan['ratioErrorFrames']))
  checkpoint();print(json.dumps(dict(exitCode=0,frames=plan['totalFrames'],decodeZero=True,aacPacketsIdentical=True,finalPixelApproval=False)))
 except BaseException:
  state.update(status='failed-current17-pair-preserve-local-files',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
if __name__=='__main__':main()
