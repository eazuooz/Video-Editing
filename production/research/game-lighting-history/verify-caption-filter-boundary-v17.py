"""Compare old and corrected filters at the observed colour-metadata boundary."""
import importlib.util
from pathlib import Path
_p=Path(__file__).with_name('review-media-common-v15.py')
_s=importlib.util.spec_from_file_location('review_media',_p)
m=importlib.util.module_from_spec(_s);_s.loader.exec_module(m)
ROOT,PROD,FF,FP=m.ROOT,m.PROD,m.FF,m.FP
proof_path=PROD/'caption-frame-property-diagnostic-v15.json';proof=m.read(proof_path)
assert proof['observedFrames']==93084 and proof['allInputPresentationPtsContinuous']
assert all(t['properties']['width']==1920 and t['properties']['height']==1080 and t['properties']['pix_fmt']=='yuv420p' for t in proof['transitions'])
source=ROOT/proof['input']['path'];assert m.sha(source)==proof['input']['sha256']
state_path=PROD/'caption-filter-boundary-test-execution-v17.json'
out=ROOT/'production/research/game-lighting-history/local/caption-filter-boundary-test-v17'
assert not state_path.exists() and not out.exists();observation=m.resources();out.mkdir(parents=True)
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,resourceObservation=observation,commands=[],results=[],allFinalPixelsReviewed=False)
m.save(state_path,state)
try:
    ass='projects/game-lighting-history-03/production/local/captions-v15/captions.ko.ass'
    outputs=[]
    for label,opts,filters in [('old-reset',[],f"setpts=N/(60*TB),ass=filename='{ass}'"),
                               ('fixed-preserve-pts',['-reinit_filter','0'],f"setsar=1,ass=filename='{ass}'")]:
        target=out/(label+'.mp4')
        cmd=[FF,'-n','-v','info','-filter_threads','2','-threads','2',*opts,'-i',source,'-t','82','-an','-vf',filters,
             '-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000']
        if label.startswith('fixed'):cmd+=['-fps_mode','passthrough','-enc_time_base','1/90000']
        run=m.run([*cmd,target],label,state,state_path,out)
        probe_cmd=[str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=width,height,r_frame_rate,time_base,nb_read_frames,duration','-of','json',str(target)]
        probe=m.json.loads(m.subprocess.run(probe_cmd,capture_output=True,text=True,check=True).stdout)
        packets_cmd=[str(FP),'-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','json',str(target)]
        pts=sorted(p['pts'] for p in m.json.loads(m.subprocess.run(packets_cmd,capture_output=True,text=True,check=True).stdout)['packets'])
        outputs.append(dict(label=label,path=m.rel(target),sha256=m.sha(target),encode=run,probe=probe,probeCommand=probe_cmd,packetCommand=packets_cmd,
                            observedFrames=len(pts),continuousExpectedPts=pts==list(range(0,4920*1500,1500))))
        state['results']=outputs;m.save(state_path,state)
    assert outputs[0]['observedFrames']!=4920, 'Old failure not reproduced; do not assume cause'
    assert outputs[1]['observedFrames']==4920 and outputs[1]['continuousExpectedPts']
    d=dict(verifiedAt=m.stamp(),status='boundary-failure-reproduced-correction-verified',inputDiagnostic=dict(path=m.rel(proof_path),sha256=m.sha(proof_path)),
           sourceIntervalSeconds=[0,82],expectedFrames=4920,outputs=outputs,
           correction='Use observed absolute input PTS; no N-based clock. Disable filter reinitialization only after full decoded resolution/pixel-format compatibility was verified; normalize pixel aspect ratio to1. Explicit passthrough FPS and1/90000 encoder time base. CPU/filter/encoder threads2.',
           captionVisualApproval=False,shortTestTimestampsRebased=True,notFinalVideoOrQuota=True,allFinalPixelsReviewed=False,newGitMedia=0,newGitImages=0)
    m.save(PROD/'caption-filter-boundary-test-v17.json',d)
    state.update(status='complete',completedAt=m.stamp(),exitCode=0,active=None);m.save(state_path,state)
    print(m.json.dumps(dict(oldFrames=outputs[0]['observedFrames'],correctedFrames=outputs[1]['observedFrames'],correctedPtsContinuous=True,finalVideoApproved=False)),flush=True)
except BaseException as e:
    state.update(status='failed',failedAt=m.stamp(),exitCode=1,error=repr(e));m.save(state_path,state);raise
