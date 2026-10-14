"""Extract the completed seventeen corrected scenes; never rerender Motion Canvas."""
import importlib.util
from pathlib import Path
p=Path(__file__).with_name('review-media-common-v15.py');s=importlib.util.spec_from_file_location('review_media',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
plan_path=m.PROD/'current-input-plan-v19.json';plan=m.read(plan_path)
cuts=[x for x in plan['inputs'] if 'sourceAggregateVerification' in x];assert len(cuts)==17
out=m.ROOT/'production/research/game-lighting-history/local/explanation-clearance-inputs-v19';state_path=m.PROD/'explanation-clearance-inputs-execution-v19.json'
assert not out.exists() and not state_path.exists(),'Preserve completed or partial extraction'
observation=m.resources();out.mkdir(parents=True)
source=m.ROOT/cuts[0]['source'];proof=m.read(m.ROOT/cuts[0]['sourceAggregateVerification'])
assert m.sha(source)==proof['outputSha256'] and proof['wholeDecode']['exitCode']==0 and proof['observedFrames']==12635
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),resourceObservation=observation,planSha256=m.sha(plan_path),active=None,results=[],cpuThreads=2,gpuJobs=0,allFinalPixelsReviewed=False)
m.save(state_path,state)
try:
 for c in cuts:
  output=m.ROOT/c['output'];a,b=c['sourceFromFrame'],c['sourceToFrame'];assert b-a==c['frames']
  vf=f"trim=start_frame={a}:end_frame={b},setpts=N/(60*TB),setsar=1"
  m.run([m.FF,'-n','-v','error','-threads','2','-i',source,'-vf',vf,'-an','-c:v','libx264','-threads','2','-filter_threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',output],c['id']+'-extract',state,state_path,out)
  v=m.verify_video(output,c['frames'],state,state_path,out,c['id'])
  v.update(source=dict(path=m.rel(source),sha256=proof['outputSha256'],fromFrame=a,toFrame=b),unchangedNarration=True,unchangedFixedCaptions=True)
  m.save(m.ROOT/c['verification'],v)
  state['results'].append(dict(id=c['id'],frames=c['frames'],verification=c['verification'],sha256=v['outputSha256']));m.save(state_path,state)
  print(c['id']+' extracted/decode0 '+str(c['frames'])+' frames',flush=True)
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None);m.save(state_path,state)
except BaseException as e:
 state.update(status='failed',exitCode=1,failedAt=m.stamp(),error=str(e));m.save(state_path,state);raise
