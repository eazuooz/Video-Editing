"""Single CPU review encode, preserving current mixed audio and every frame allocation.

This is review media. Pixel, causal-flow, collection and publishing approval stay false.
Reuse the full 54-window/105-placement guard from the previously reviewed producer.
"""
from pathlib import Path
import hashlib, shutil
guard = Path(__file__).with_name('build-reviewed-pair-v15.py').read_text('utf-8').split('visual_proof_path =')[0]
exec(compile(guard, str(Path(__file__).with_name('build-reviewed-pair-v15.py')), 'exec'))
input_path = PROD/'current-input-plan-v20.json'; inputs_plan=m.read(input_path)
assert inputs_plan['pcmUnchanged'] and inputs_plan['fixedCaptionsUnchanged'] and inputs_plan['chaptersUnchanged']
assert inputs_plan['unchangedMeasuredNarrationPlan']['sha256']==m.sha(plan_path)
assert inputs_plan['totals']==plan['totals'] and inputs_plan['finalSeconds']==plan['finalSeconds']==1551.4
for ref in inputs_plan['references']:assert m.sha(ROOT/ref['path'])==ref['sha256'],ref['path']
ann_path=PROD/'native-annotation-direct-review-v19.json';ann=m.read(ann_path)
assert ann['reviewPairPreparationAllowed'] and ann['annotationsNarrationMatched'] and len(ann['cuts'])==2
assert all(c['sampledMovingPixelApproval'] for c in ann['cuts'])
boxes=m.read(PROD/'local/captions-v15/caption-layout-measurement.json');ass=ROOT/boxes['ass']['path']
assert m.sha(ass)==boxes['ass']['sha256'] and boxes['cueCount']==356
audio=ROOT/settings['aac'];assert m.sha(audio)==settings['aacSha256']
ordered=inputs_plan['inputs'];assert len(ordered)==166
input_records=[]
for i,c in enumerate(ordered):
    assert c['fromFrame']==(ordered[i-1]['toFrame'] if i else 0)
    assert c['toFrame']-c['fromFrame']==c['frames']
    file=ROOT/c.get('output',c.get('media',''));assert file.is_file()
    digest=m.sha(file)
    if 'verification' in c:
        v=m.read(ROOT/c['verification'])
        assert v['outputSha256']==digest and v['observedFrames']==c['frames'] and v['wholeDecode']['exitCode']==0 and v['allPresentationPtsContinuous'],c['id']
    else:assert c['copyByteIdentically'] and digest==c['sha256'],c['id']
    input_records.append(dict(id=c['id'],path=m.rel(file),sha256=digest,frames=c['frames'],fromFrame=c['fromFrame'],toFrame=c['toFrame']))
assert ordered[-1]['toFrame']==93084
assert sum(c['frames']for c in ordered if c['kind']=='actual-review-input')==55418
assert sum(c['frames']for c in ordered if c['kind']=='explanation-review-input')==36946
assert abs(55418-92364*.6)<=1
state_path=PROD/'current-review-pair-execution-v20.json'
out=ROOT/'production/research/game-lighting-history/local/current-review-pair-v20'
assert not state_path.exists() and not out.exists(),'Preserve existing execution and media'
disk=shutil.disk_usage(ROOT);total_bytes=sum((ROOT/c['path']).stat().st_size for c in input_records)
assert disk.free>total_bytes*2+2*1024**3,'Insufficient room for preserved old and new review pairs'
resource=m.resources();out.mkdir()
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),resourceObservation=resource,
           inputPlanSha256=m.sha(input_path),inputs=input_records,inputBytes=total_bytes,diskFreeBytes=disk.free,
           active=None,commands=[],results=[],cpuThreads=2,gpuJobs=0,
           allFinalPixelsReviewed=False,qaApproved=False,collected=False,uploaded=False)
m.save(state_path,state)
checkpoint=ROOT/'production/research/game-lighting-history/checkpoint.json'
def update(active):
    d=m.read(checkpoint);d['episode03CurrentReviewPairExecution']=dict(path=m.rel(state_path),status=state['status'],worker=state['worker'],active=state['active'],results=len(state['results']),allFinalPixelsReviewed=False)
    d['ownedActiveWork']=dict(type='CPU-current-review-pair-v20',execution=m.rel(state_path),worker=state['worker'],cpuThreads=2,gpuJobs=0)if active else None
    d['updatedAt']=m.stamp();m.save(checkpoint,d)
def run(cmd,label):
    result=m.run(cmd,label,state,state_path,out);update(True);return result
def packets(file,stream,video=False):
    cmd=[str(FP),'-v','error','-select_streams',stream,'-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash'+(',pts'if video else ''),'-of','json',str(file)]
    data=m.json.loads(m.subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)['packets']
    if video:assert sorted(x['pts']for x in data)==list(range(0,93084*1500,1500))
    return dict(count=len(data),hash=hashlib.sha256('\n'.join(x['data_hash']for x in data).encode()).hexdigest(),command=cmd)
def verify(file,label):
    cmd=[str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,sample_rate,channels:format=duration','-of','json',str(file)]
    probe=m.json.loads(m.subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
    v=next(x for x in probe['streams']if x['codec_type']=='video');a=next(x for x in probe['streams']if x['codec_type']=='audio')
    assert len(probe['streams'])==2 and (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',93084),probe
    assert(a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2)
    assert abs(float(v['duration'])-1551.4)<1/90000 and abs(float(probe['format']['duration'])-1551.4)<=1/60
    vp=packets(file,'v:0',True);ap=packets(file,'a:0')
    decode=run([FF,'-v','error','-threads','2','-i',file,'-f','null','NUL'],label+'-whole-decode')
    return dict(path=m.rel(file),sha256=m.sha(file),frames=93084,allPresentationPtsContinuous=True,probe=probe,probeCommand=cmd,videoPackets=vp,audioPackets=ap,wholeDecode=decode,allPixelsReviewed=False)
update(True)
try:
    concat=out/'current-inputs.ffconcat';lines=['ffconcat version 1.0']
    for c in input_records:
        file=(ROOT/c['path']).as_posix();assert "'"not in file and '\n'not in file
        lines += ["file '"+file+"'",'duration '+format(c['frames']/60,'.9f')]
    concat.write_text('\n'.join(lines)+'\n','utf-8')
    clean=out/'game-lighting-history-03.clean.mp4';captioned=out/'game-lighting-history-03.captioned.mp4'
    clean_encode=run([FF,'-n','-v','info','-threads','2','-f','concat','-safe','0','-i',concat,'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-t','1551.4','-video_track_timescale','90000','-movflags','+faststart',clean],'clean-current-input-concat-mux')
    cp=verify(clean,'clean');cp['encode']=clean_encode;state['results'].append(cp);m.save(state_path,state);update(True)
    source_audio=packets(audio,'a:0');assert cp['audioPackets']['count']==source_audio['count'] and cp['audioPackets']['hash']==source_audio['hash']
    encode=run([FF,'-n','-v','info','-filter_threads','2','-threads','2','-reinit_filter','0','-i',clean,'-map','0:v:0','-map','0:a:0','-t','1551.4','-vf',f"setsar=1,ass=filename='{m.rel(ass)}'",'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-enc_time_base','1/90000','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart','-progress',out/'captioned-progress.txt',captioned],'captioned-current-input-original-pts')
    pp=verify(captioned,'captioned');pp['encode']=encode
    assert pp['audioPackets']['count']==cp['audioPackets']['count'] and pp['audioPackets']['hash']==cp['audioPackets']['hash']
    record=dict(createdAt=m.stamp(),status='current-encoded-review-pair-awaiting-final-pixels-and-flow',inputPlan=dict(path=m.rel(input_path),sha256=m.sha(input_path)),
        unchangedNarrationPlan=dict(path=m.rel(plan_path),sha256=m.sha(plan_path)),mixWavSha256=settings['wavSha256'],mixAacSha256=settings['aacSha256'],mixedAsrApprovalSha256=m.sha(PROD/'review-mixed-asr-direct-review-v15.json'),
        captionAssSha256=boxes['ass']['sha256'],captionPlanSha256=m.sha(PROD/'local/captions-v15/caption-plan.json'),clean=cp,captioned=pp,identicalAacPayload=True,audioSourcePackets=source_audio,
        actualFrames=55418,explanationFrames=36946,bodyFrames=92364,finalFrames=93084,sourceAudioStreams=0,loops=0,slowdown=0,retimedPcmSamples=0,
        allFinalPixelsReviewed=False,allMovingPixelsReviewed=False,causalFlowApproved=False,captionTimingApproved=False,qaApproved=False,collected=False,uploaded=False,
        humanWholeListening='pending',humanPronunciation='pending',rightsApproved=False,newGitImages=0)
    m.save(PROD/'current-review-pair-build-v20.json',record)
    state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None,results=[cp,pp]);m.save(state_path,state);update(False)
    print(m.json.dumps(dict(frames=93084,bothDecodes=0,identicalAac=True,reviewOnly=True,finalApproval=False)),flush=True)
except BaseException as e:
    state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(state_path,state);update(False);raise
