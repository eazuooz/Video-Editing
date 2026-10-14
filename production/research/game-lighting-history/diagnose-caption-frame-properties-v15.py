"""Observe decoded frame-property transitions without modifying any media."""
import importlib.util
from pathlib import Path
_p=Path(__file__).with_name('review-media-common-v15.py')
_s=importlib.util.spec_from_file_location('review_media',_p)
m=importlib.util.module_from_spec(_s);_s.loader.exec_module(m)
ROOT,PROD,FP=m.ROOT,m.PROD,m.FP
state_path=PROD/'caption-frame-property-diagnostic-execution-v15.json'
assert not state_path.exists(), 'Preserve prior diagnostic'
old_path=PROD/'review-pair-execution-v15.json';old=m.read(old_path)
assert old['status']=='failed' and old['exitCode']==1
plan=m.read(PROD/'measured-native-timeline-candidate-v15.json')
visual=ROOT/'production/research/game-lighting-history/local/explanation-framing-v15/silent-review-visual-v15.mp4'
out=ROOT/'production/research/game-lighting-history/local/caption-frame-property-diagnostic-v15'
assert not out.exists();observation=m.resources();out.mkdir(parents=True)
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,resourceObservation=observation,commands=[],results=[],newMedia=0,newImages=0,allFinalPixelsReviewed=False)
m.save(state_path,state)
try:
    cmd=[FP,'-v','error','-threads','2','-select_streams','v:0','-show_frames',
         '-show_entries','frame=best_effort_timestamp,width,height,pix_fmt,sample_aspect_ratio,color_range,color_space,color_transfer,color_primaries',
         '-of','json',visual]
    run=m.run(cmd,'all-decoded-input-frame-properties',state,state_path,out)
    raw_path=ROOT/run['log'];frames=m.json.loads(raw_path.read_text('utf-8'))['frames']
    keys=['width','height','pix_fmt','sample_aspect_ratio','color_range','color_space','color_transfer','color_primaries']
    transitions=[];previous=None
    for index,f in enumerate(frames):
        props={k:f.get(k) for k in keys}
        if props!=previous:
            transitions.append(dict(frame=index,pts=f.get('best_effort_timestamp'),seconds=index/60,properties=props))
            previous=props
    expected=plan['totals']['finalFrames']
    assert len(frames)==expected and [f['best_effort_timestamp'] for f in frames]==list(range(0,expected*1500,1500))
    observed=m.stamp()
    proof=dict(observedAt=observed,status='decoded-input-properties-observed',expectedFrames=expected,observedFrames=len(frames),
               allInputPresentationPtsContinuous=True,input=dict(path=m.rel(visual),sha256=m.sha(visual)),transitions=transitions,
               failedPairExecution=dict(path=m.rel(old_path),sha256=m.sha(old_path)),
               rawLocalOnly=dict(path=m.rel(raw_path),sha256=m.sha(raw_path)),command=run,
               officialDocumentation='https://ffmpeg.org/ffmpeg.html#Main-options',
               documentationFinding='Filter reinitialization loses buffered frames and frame-count state; decoded transitions are observed separately, not inferred from stream-level metadata.',
               mediaModified=False,newMedia=0,newImages=0,repairApproved=False,allFinalPixelsReviewed=False)
    m.save(PROD/'caption-frame-property-diagnostic-v15.json',proof)
    state.update(status='complete',completedAt=observed,exitCode=0,active=None)
    m.save(state_path,state);print(m.json.dumps(dict(frames=len(frames),transitions=transitions,newMedia=0,newImages=0)),flush=True)
except BaseException as e:
    state.update(status='failed',failedAt=m.stamp(),exitCode=1,error=repr(e));m.save(state_path,state);raise
