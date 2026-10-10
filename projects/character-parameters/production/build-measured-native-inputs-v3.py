"""Encode current unique normal-speed game inputs, serial CPU2 and GPU0."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,time,ctypes
import psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,o):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def identity(p):return dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd())
def checkpoint():
 cp_path=BASE/'latest-checkpoint.json';cp=read(cp_path);cp.update(recordedAt=now(),stage=state['status'],ownedJob=dict(state=rel(EP),processIdentity=state['processIdentity'],child=state.get('activeChild'),completed=state['completed'],total=state['total'],sessionId=state.get('sessionId')),
 nextAction='Finish only these native inputs, then all current caption/cut/UI and measured black motion pixels. No final timing/mix/pair/QA/collection/upload approval yet.');save(cp_path,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(10):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(i for i in q['items'] if i['slug']=='character-parameters')
  item.update(stage=state['status'],currentExecution=cp['ownedJob'],nextAction=cp['nextAction']);q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);return
  time.sleep(.15)
 raise RuntimeError('Concurrent queue write; preserve state')
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
resource=ROOT/args.resource;r=read(resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<180
export=read(BASE/'measured-black-export-execution-v3.json');assert export['exitCode']==0 and export['childExited']
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([NODE,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
pp=BASE/'measured-timeline-candidate-v3.json';plan=read(pp)
assert sha(ROOT/plan['currentVoiceSelection'])==plan['currentVoiceSelectionSha256']
assert sha(ROOT/plan['bank'])==plan['bankSha256']
rows=[s for s in plan['segments'] if s['role']=='actual-existing-game'];assert len(rows)==24 and sum(s['frames'] for s in rows)==13606
OUT=ROOT/'shared/output/character-parameters/measured-native-inputs-v3';EP=BASE/'measured-native-inputs-execution-v3.json'
assert not OUT.exists() and not EP.exists(),'Preserve partial/complete inputs and inspect execution before explicit recovery'
for s in {s['sourcePath']:s for s in rows}.values():assert sha(ROOT/s['sourcePath'])==s['sourceSha256'] and sha(ROOT/s['nativePtsEvidence'])==s['nativePtsEvidenceSha256']
OUT.mkdir(parents=True)
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
state=dict(schemaVersion=3,status='building-measured-native-inputs-v3',startedAt=now(),processIdentity=identity(psutil.Process()),sessionId=None,exitCode=None,
 cpuThreads=2,gpuJobs=0,resource=args.resource,resourceSha256=sha(resource),plan=rel(pp),planSha256=sha(pp),completed=0,total=24,activeChild=None,results=[],
 normalSpeed=True,sourceAudio=False,loop=False,slowdown=False,sourceAcquisitionRepeated=False,allFinalPixels=False,finalTimingApproved=False,mixedAsrApproved=False,rasterGitAdditions=0,mediaGitAdditions=0)
save(EP,state);checkpoint()
try:
 for s in rows:
  out=OUT/(s['id']+'.mp4');log=OUT/(s['id']+'.encode.log')
  trim=f"trim=start_pts={s['nativeStartPts']}:end_pts={s['nativeEndPtsExclusive']},setpts=PTS-{s['nativeStartPts']},format=rgb24"
  if s['sourceKey']=='gBbKFYZYvbc':
   filt=f'[0:v]{trim},split=5[main][bg][p1][p2][credit];'+\
    '[main]scale=1920:1080:flags=neighbor[full];[bg]crop=1280:55:0:602,gblur=sigma=12,scale=1920:95[back];'+\
    '[p1]crop=299:63:16:657,scale=449:95:flags=neighbor[left];[p2]crop=296:63:335:657,scale=444:95:flags=neighbor[right];'+\
    '[credit]crop=641:63:639:657,scale=462:45:flags=lanczos[c];[full][back]overlay=0:985:shortest=1:format=rgb[a];'+\
    '[a][left]overlay=24:985:shortest=1:format=rgb[b];[b][right]overlay=1476:985:shortest=1:format=rgb[d];[d][c]overlay=729:1035:shortest=1:format=rgb[framed];'
  elif s['sourceKey']=='a8nwpiCqyTQ':
   filt=f'[0:v]{trim},split=3[main][bg][inventory];'+\
    '[bg]crop=1114:50:406:870,gblur=sigma=12,scale=1114:144[back];[inventory]crop=1114:144:406:921,scale=424:55:flags=neighbor[inv];'+\
    '[main][back]overlay=406:921:shortest=1:format=rgb[a];[a][inv]overlay=1490:135:shortest=1:format=rgb[framed];'
  else:
   filt=f'[0:v]{trim},split=2[main][bg];[main]scale=1920:960:flags=neighbor[full];[bg]gblur=sigma=12,scale=1920:1080[back];[back][full]overlay=0:0:shortest=1:format=rgb[framed];'
  filt+=f'[framed]tpad=stop_mode=clone:stop=1,fps=60:start_time=0:round=near,trim=end_frame={s["frames"]},settb=1/90000,setpts=N*1500,setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]'
  cmd=[FF,'-nostdin','-hide_banner','-loglevel','warning','-threads','2','-reinit_filter','0','-i',str(ROOT/s['sourcePath']),'-filter_complex_threads','1','-filter_complex',filt,
       '-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-frames:v',str(s['frames']),'-fps_mode','cfr','-r','60','-video_track_timescale','90000','-movflags','+faststart',str(out)]
  with log.open('wb') as handle:
   child=subprocess.Popen(cmd,cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   state['activeChild']={**identity(psutil.Process(child.pid)), 'log':rel(log)};state['activeSegment']=s['id'];save(EP,state);checkpoint();code=child.wait()
  assert code==0,log.read_text('utf-8',errors='replace')[-3000:]
  probe=json.loads(subprocess.check_output([FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp,width,height:stream=time_base,avg_frame_rate,nb_frames,codec_name','-of','json',str(out)],text=True))
  frames=probe['frames'];stream=probe['streams'][0]
  assert len(frames)==s['frames'] and stream['time_base']=='1/90000' and stream['avg_frame_rate']=='60/1'
  assert all(int(f['best_effort_timestamp'])==i*1500 and (f['width'],f['height'])==(1920,1080) for i,f in enumerate(frames))
  pr=OUT/(s['id']+'.probe.json');save(pr,probe)
  decode=subprocess.run([FF,'-nostdin','-v','error','-threads','2','-i',str(out),'-map','0:v:0','-an','-f','null','-'],capture_output=True,text=True)
  assert decode.returncode==0,decode.stderr
  state['results'].append(dict(id=s['id'],path=rel(out),sha256=sha(out),frames=s['frames'],fps='60/1',timebase='1/90000',ptsStep=1500,allPtsVerified=True,
   encodeExitCode=code,wholeDecodeExitCode=decode.returncode,probe=rel(pr),probeSha256=sha(pr),command=cmd,sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],
   sourceStartFrame=s['sourceStartFrame'],sourceEndFrameExclusive=s['sourceEndFrameExclusive'],framing=s['framing'],normalSpeed=True,sourceAudio=False,loop=False,slowdown=False,
   finalCuePixelsReviewed=False,childIdentity=state['activeChild']))
  state['completed']+=1;state['activeChild']=None;save(EP,state);checkpoint()
  print(json.dumps(dict(completed=state['completed'],total=24,id=s['id'],frames=s['frames'])),flush=True)
 state.update(status='measured-native-inputs-complete-cue-pixel-review-pending',exitCode=0,finishedAt=now(),activeChild=None);save(EP,state);checkpoint()
except BaseException as error:
 state.update(status='measured-native-inputs-failed-preserve-all-completed-files',exitCode=1,finishedAt=now(),error=repr(error));save(EP,state);checkpoint();raise
