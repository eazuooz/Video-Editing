"""One CPU job, sequential two current annotated native inputs; no audio retiming."""
import importlib.util
from pathlib import Path
p=Path(__file__).with_name('review-media-common-v15.py');s=importlib.util.spec_from_file_location('review_media',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
plan_path=m.PROD/'native-annotation-plan-v19d.json';plan=m.read(plan_path)
out=m.ROOT/'production/research/game-lighting-history/local/native-annotations-v19d';sp=m.PROD/'native-annotation-render-execution-v19d.json';assert not sp.exists()
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),resourceObservation=m.resources(),planSha256=m.sha(plan_path),active=None,results=[],cpuThreads=2,gpuJobs=0,allMovingPixelsReviewed=False,allFinalPixelsReviewed=False)
m.save(sp,state)
try:
 for c in plan['cuts'][:1]:
  assert m.sha(m.ROOT/c['source'])==c['sourceSha256'] and m.sha(m.ROOT/c['annotations'])==c['annotationsSha256']
  ap=c['annotations'];assert ':' not in ap and "'" not in ap
  m.run([m.FF,'-n','-v','error','-threads','2','-i',m.ROOT/c['source'],'-filter_complex_threads','2','-filter_complex',f"[0:v]split=2[base][detail];[detail]crop=630:585:600:495,scale=420:390[zoom];[base][zoom]overlay=32:120:enable='gte(t,278/60)*lt(t,5)',setsar=1,ass=filename='{ap}'[v]",'-map','[v]','-an','-c:v','libx264','-threads','2','-filter_threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',m.ROOT/c['output']],c['id']+'-annotate',state,sp,out)
  v=m.verify_video(m.ROOT/c['output'],c['frames'],state,sp,out,c['id']);v.update(inputSha256=c['sourceSha256'],annotationSha256=c['annotationsSha256'],screenSpaceOnly=True,pcmUnchanged=True,fullAnimatedPlaybackReviewed=False)
  m.save(m.ROOT/c['verification'],v);state['results'].append(dict(id=c['id'],frames=c['frames'],verification=c['verification'],sha256=v['outputSha256']));m.save(sp,state)
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None);m.save(sp,state)
 print(m.json.dumps(dict(cuts=1,frames=360,decodes=0,movingPixelsApproved=False)),flush=True)
except BaseException as e:
 state.update(status='failed',exitCode=1,failedAt=m.stamp(),error=str(e));m.save(sp,state);raise
