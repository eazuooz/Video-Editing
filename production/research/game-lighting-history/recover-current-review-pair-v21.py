"""Round the observed -3..0 ticks to exact1500-tick frames without re-encoding source pixels."""
from pathlib import Path
import hashlib
guard=Path(__file__).with_name('build-reviewed-pair-v15.py').read_text('utf-8').split('visual_proof_path =')[0]
exec(compile(guard,str(Path(__file__).with_name('build-reviewed-pair-v15.py')),'exec'))
old_path=PROD/'current-review-pair-execution-v20.json';old=m.read(old_path)
assert old['status']=='failed' and old['exitCode']==1
diagnostic_path=PROD/'current-review-pair-pts-diagnostic-v20.json';diagnostic=m.read(diagnostic_path)
assert diagnostic['packetCount']==93084 and diagnostic['deltaMin']==-3 and diagnostic['deltaMax']==0
assert diagnostic['roundedPresentationPtsContinuous'] and diagnostic['roundedDecodePtsStrictlyIncreasing']
source=ROOT/diagnostic['input']['path'];assert m.sha(source)==diagnostic['input']['sha256']
for c in old['inputs']:assert m.sha(ROOT/c['path'])==c['sha256'],c['id']
input_path=PROD/'current-input-plan-v20.json';assert m.sha(input_path)==old['inputPlanSha256']
settings=m.read(PROD/'review-mix-settings-v15.json');audio=ROOT/settings['aac'];assert m.sha(audio)==settings['aacSha256']
boxes=m.read(PROD/'local/captions-v15/caption-layout-measurement.json');ass=ROOT/boxes['ass']['path'];assert m.sha(ass)==boxes['ass']['sha256'] and boxes['cueCount']==356
state_path=PROD/'current-review-pair-recovery-execution-v21.json';out=ROOT/'production/research/game-lighting-history/local/current-review-pair-v21'
assert not state_path.exists() and not out.exists(),'Preserve existing recovery'
resource=m.resources();out.mkdir()
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),resourceObservation=resource,
 priorFailure=dict(path=m.rel(old_path),sha256=m.sha(old_path)),diagnostic=dict(path=m.rel(diagnostic_path),sha256=m.sha(diagnostic_path)),
 active=None,commands=[],results=[],inputPlanSha256=m.sha(input_path),cpuThreads=2,gpuJobs=0,
 allFinalPixelsReviewed=False,qaApproved=False,collected=False,uploaded=False)
m.save(state_path,state);checkpoint=ROOT/'production/research/game-lighting-history/checkpoint.json'
def update(active):
    d=m.read(checkpoint);d['episode03CurrentReviewPairRecovery']=dict(path=m.rel(state_path),status=state['status'],worker=state['worker'],active=state['active'],results=len(state['results']),allFinalPixelsReviewed=False)
    d['ownedActiveWork']=dict(type='CPU-current-review-pair-recovery-v21',execution=m.rel(state_path),worker=state['worker'],cpuThreads=2,gpuJobs=0)if active else None
    d['updatedAt']=m.stamp();m.save(checkpoint,d)
def run(cmd,label):
    result=m.run(cmd,label,state,state_path,out);update(True);return result
helper=Path(__file__).with_name('build-current-review-pair-v20.py').read_text('utf-8')
helper=helper[helper.index('def packets('):helper.index('update(True)\ntry:')]
exec(compile(helper,str(Path(__file__).with_name('build-current-review-pair-v20.py')),'exec'))
update(True)
try:
    clean=out/'game-lighting-history-03.clean.mp4';captioned=out/'game-lighting-history-03.captioned.mp4'
    encode=run([FF,'-n','-v','info','-threads','2','-i',source,'-map','0:v:0','-map','0:a:0','-c','copy','-bsf:v','setts=pts=round(PTS/1500)*1500:dts=round(DTS/1500)*1500:duration=1500:time_base=1/90000','-video_track_timescale','90000','-movflags','+faststart',clean],'clean-tick-rounding-remux')
    cp_video=packets(clean,'v:0',True);source_video=packets(source,'v:0')
    assert cp_video['count']==source_video['count']==93084 and cp_video['hash']==source_video['hash'],'Video bitstream payload changed'
    cp=verify(clean,'clean');cp.update(encode=encode,videoPayloadIdenticalToFailedConcat=True)
    source_audio=packets(audio,'a:0');assert cp['audioPackets']['count']==source_audio['count'] and cp['audioPackets']['hash']==source_audio['hash']
    state['results'].append(cp);m.save(state_path,state);update(True)
    encode=run([FF,'-n','-v','info','-filter_threads','2','-threads','2','-reinit_filter','0','-i',clean,'-map','0:v:0','-map','0:a:0','-t','1551.4','-vf',f"setsar=1,ass=filename='{m.rel(ass)}'",'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-enc_time_base','1/90000','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart','-progress',out/'captioned-progress.txt',captioned],'captioned-current-input-original-pts')
    pp=verify(captioned,'captioned');pp['encode']=encode
    assert pp['audioPackets']['count']==cp['audioPackets']['count'] and pp['audioPackets']['hash']==cp['audioPackets']['hash']
    record=dict(createdAt=m.stamp(),status='current-encoded-review-pair-awaiting-final-pixels-and-flow',
      inputPlan=dict(path=m.rel(input_path),sha256=m.sha(input_path)),unchangedNarrationPlan=dict(path=m.rel(plan_path),sha256=m.sha(plan_path)),
      mixWavSha256=settings['wavSha256'],mixAacSha256=settings['aacSha256'],mixedAsrApprovalSha256=m.sha(PROD/'review-mixed-asr-direct-review-v15.json'),
      captionAssSha256=boxes['ass']['sha256'],captionPlanSha256=m.sha(PROD/'local/captions-v15/caption-plan.json'),
      clean=cp,captioned=pp,identicalAacPayload=True,sourceAudioPackets=source_audio,
      originalVideoPayloadHash=source_video['hash'],tickCorrection=dict(observedMin=-3,observedMax=0,timebase=90000,frameTicks=1500,videoPayloadChanged=False,frameCountChanged=False),
      actualFrames=55418,explanationFrames=36946,bodyFrames=92364,finalFrames=93084,sourceAudioStreams=0,loops=0,slowdown=0,retimedPcmSamples=0,
      preservedFailure=state['priorFailure'],diagnostic=state['diagnostic'],recoveryExecution=dict(path=m.rel(state_path)),
      allFinalPixelsReviewed=False,allMovingPixelsReviewed=False,causalFlowApproved=False,captionTimingApproved=False,qaApproved=False,collected=False,uploaded=False,
      humanWholeListening='pending',humanPronunciation='pending',rightsApproved=False,newGitImages=0)
    m.save(PROD/'current-review-pair-build-v21.json',record)
    state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None,results=[cp,pp]);m.save(state_path,state);update(False)
    print(m.json.dumps(dict(frames=93084,bothDecodes=0,identicalAac=True,sourceVideoPayloadUnchanged=True,reviewOnly=True,finalApproval=False)),flush=True)
except BaseException as e:
    state.update(status='failed',exitCode=1,failedAt=m.stamp(),error=repr(e));m.save(state_path,state);update(False);raise
