"""Keep the approved clean mux; recover only the caption filter with original PTS."""
import importlib.util, hashlib, psutil
from pathlib import Path
_p=Path(__file__).with_name('review-media-common-v15.py')
_s=importlib.util.spec_from_file_location('review_media',_p)
m=importlib.util.module_from_spec(_s);_s.loader.exec_module(m)
ROOT,PROD,FF,FP=m.ROOT,m.PROD,m.FF,m.FP
plan_path=PROD/'measured-native-timeline-candidate-v15.json';plan=m.read(plan_path)
settings=m.read(PROD/'review-mix-settings-v15.json')
approval_path=PROD/'review-mixed-asr-direct-review-v15.json';approval=m.read(approval_path)
assert approval['all54WindowsDirectlyCompared'] and approval['currentMixedContentApproved'] and approval['resolvedRecognitionArtifactsDirectlyCompared']
assert approval['mixSha256']==settings['wavSha256'] and approval['planSha256']==m.sha(plan_path)
progress_path=PROD/'review-mixed-asr-direct-progress-v15.json';progress=m.read(progress_path)
assert approval['directProgressSha256']==m.sha(progress_path) and progress['directlyReadWindows']==54 and len(progress['records'])==54
asr=m.read(PROD/'review-mixed-asr-execution-v15.json');assert asr['status']=='complete' and asr['exitCode']==0 and len(asr['results'])==54
reviewed={r['label']:r for r in progress['records']};assert len(reviewed)==54 and set(reviewed)=={r['label'] for r in asr['results']}
for r in asr['results']:
    assert m.sha(ROOT/r['path'])==r['sha256']==reviewed[r['label']]['resultSha256']
    assert reviewed[r['label']]['directFullExpectedAndActualTextRead'] and reviewed[r['label']]['allWordTimestampsRead']
pcm_path=PROD/'review-mixed-asr-pcm-corroboration-v15.json';pcm=m.read(pcm_path)
assert approval['pcmCorroborationSha256']==m.sha(pcm_path) and pcm['mixSha256']==approval['mixSha256'] and pcm['planSha256']==approval['planSha256']
assert pcm['allOriginalSamplesPartitionedOnce'] and pcm['all105PlacementsSourceValuesExact'] and pcm['all54RecognitionWindowsCurrentMixExact']
repair_path=PROD/'caption-filter-repair-review-v17.json';repair=m.read(repair_path)
assert repair['finalPairRecoveryAllowed'] and repair['observedOriginalDropFrames']==4583 and repair['correctedDropFrames']==0
diagnostic_path=ROOT/repair['inputDiagnostic']['path'];assert m.sha(diagnostic_path)==repair['inputDiagnostic']['sha256']
diagnostic=m.read(diagnostic_path);assert diagnostic['observedFrames']==93084 and diagnostic['allInputPresentationPtsContinuous']
assert all(t['properties']['width']==1920 and t['properties']['height']==1080 and t['properties']['pix_fmt']=='yuv420p' for t in diagnostic['transitions'])
visual=ROOT/diagnostic['input']['path'];assert m.sha(visual)==diagnostic['input']['sha256']
audio=ROOT/settings['aac'];assert m.sha(audio)==settings['aacSha256']
boxes=m.read(PROD/'local/captions-v15/caption-layout-measurement.json');ass=ROOT/boxes['ass']['path']
assert m.sha(ass)==boxes['ass']['sha256'] and boxes['cueCount']==356
old_path=PROD/'review-pair-execution-v15.json';old=m.read(old_path);assert old['status']=='failed' and old['exitCode']==1
try:
    p=psutil.Process(old['worker']['pid'])
    assert abs(p.create_time()-old['worker']['createTime'])>.01, 'Preserve still-live original worker'
except psutil.NoSuchProcess:pass
old_decode=next(x for x in old['commands'] if x['log'].endswith('/clean-whole-decode.log'));assert old_decode['exitCode']==0
old_encode=next(x for x in old['commands'] if x['log'].endswith('/clean-review-mux.log'));assert old_encode['exitCode']==0
clean=ROOT/'production/research/game-lighting-history/local/review-pair-v15/game-lighting-history-03.clean.mp4'
assert str(clean) in old_decode['commandLine'] and str(clean) in old_encode['commandLine']
state_path=PROD/'review-pair-recovery-execution-v16.json'
pair_path=PROD/'review-pair-build-v15.json'
out=ROOT/'production/research/game-lighting-history/local/review-pair-v16'
assert not state_path.exists() and not pair_path.exists() and not out.exists(), 'Preserve existing recovery/media'
observation=m.resources();out.mkdir(parents=True)
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,resourceObservation=observation,commands=[],results=[],observations=[],
           priorFailure=dict(path=m.rel(old_path),sha256=m.sha(old_path)),repairReview=dict(path=m.rel(repair_path),sha256=m.sha(repair_path)),
           cleanReused=True,allFinalPixelsReviewed=False,qaApproved=False,collected=False,uploaded=False)
m.save(state_path,state)
def probe(file,label,count_frames=False):
    cmd=[str(FP),'-v','error','-threads','2',*(['-count_frames'] if count_frames else []),'-show_entries',
         'stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_frames,nb_read_frames,sample_rate,channels,duration:format=duration','-of','json',str(file)]
    d=m.json.loads(m.subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
    state['observations'].append(dict(label=label,commandLine=cmd,observedAt=m.stamp(),probe=d));m.save(state_path,state)
    v=next(x for x in d['streams'] if x['codec_type']=='video');a=next(x for x in d['streams'] if x['codec_type']=='audio')
    assert len(d['streams'])==2 and (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_frames']))==(1920,1080,'60/1','1/90000',93084),d
    if count_frames:assert int(v['nb_read_frames'])==93084,d
    assert (a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2)
    assert abs(float(v['duration'])-1551.4)<1/90000 and abs(float(d['format']['duration'])-1551.4)<=1/60
    return d,cmd
def packet_proof(file,stream,with_pts=False):
    fields='packet=data_hash'+(',pts' if with_pts else '')
    cmd=[str(FP),'-v','error','-select_streams',stream,'-show_packets','-show_data_hash','sha256','-show_entries',fields,'-of','json',str(file)]
    packets=m.json.loads(m.subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)['packets']
    hashes=[p['data_hash'] for p in packets]
    if with_pts:assert sorted(p['pts'] for p in packets)==list(range(0,93084*1500,1500))
    return dict(count=len(packets),hash=hashlib.sha256('\n'.join(hashes).encode()).hexdigest(),command=cmd)
try:
    cp,cp_cmd=probe(clean,'preserved-clean-streams')
    clean_v=packet_proof(clean,'v:0',True);visual_v=packet_proof(visual,'v:0',True)
    assert clean_v['hash']==visual_v['hash'] and clean_v['count']==visual_v['count']==93084
    clean_a=packet_proof(clean,'a:0');source_a=packet_proof(audio,'a:0');assert clean_a['hash']==source_a['hash'] and clean_a['count']==source_a['count']
    cp_record=dict(path=m.rel(clean),sha256=m.sha(clean),frames=93084,allPresentationPtsContinuous=True,probe=cp,probeCommand=cp_cmd,
                   packetCommand=clean_v['command'],videoPayloadSameAsApprovedSilent=True,videoPayloadHash=clean_v['hash'],
                   aacPacketHashCommand=clean_a['command'],aacPacketCount=clean_a['count'],aacPayloadHash=clean_a['hash'],
                   wholeDecode=old_decode,encode=old_encode,cleanReused=True,allPixelsReviewed=False)
    state['results']=[cp_record];m.save(state_path,state)
    captioned=out/'game-lighting-history-03.captioned.mp4'
    encode=m.run([FF,'-n','-v','info','-filter_threads','2','-threads','2','-reinit_filter','0','-i',visual,'-i',audio,
                  '-map','0:v:0','-map','1:a:0','-t','1551.4','-vf',f"setsar=1,ass=filename='{m.rel(ass)}'",
                  '-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',
                  '-fps_mode','passthrough','-enc_time_base','1/90000','-video_track_timescale','90000',
                  '-c:a','copy','-movflags','+faststart','-progress',out/'captioned-progress.txt',captioned],
                 'captioned-original-pts-recovery',state,state_path,out)
    quick,_=probe(captioned,'corrected-captioned-streams')
    pp,pp_cmd=probe(captioned,'corrected-captioned-all-decoded-frames',True)
    final_v=packet_proof(captioned,'v:0',True);final_a=packet_proof(captioned,'a:0')
    assert final_v['count']==93084 and final_a['hash']==clean_a['hash'] and final_a['count']==clean_a['count']
    decode=m.run([FF,'-v','error','-threads','2','-i',captioned,'-f','null','NUL'],'captioned-whole-decode',state,state_path,out)
    pp_record=dict(path=m.rel(captioned),sha256=m.sha(captioned),frames=93084,allPresentationPtsContinuous=True,probe=pp,probeCommand=pp_cmd,
                   packetCommand=final_v['command'],aacPacketHashCommand=final_a['command'],aacPacketCount=final_a['count'],aacPayloadHash=final_a['hash'],
                   wholeDecode=decode,encode=encode,allPixelsReviewed=False)
    record=dict(createdAt=m.stamp(),status='encoded-review-pair-awaiting-all-pixels',planSha256=m.sha(plan_path),
                mixedAsrDirectApprovalSha256=m.sha(approval_path),visualSha256=m.sha(visual),mixAacSha256=m.sha(audio),
                captionAssSha256=boxes['ass']['sha256'],captionPlanSha256=m.sha(PROD/'local/captions-v15/caption-plan.json'),
                clean=cp_record,captioned=pp_record,identicalAacPayload=True,sourceAudioStreams=0,
                recoveryExecution=dict(path=m.rel(state_path)),repairReview=dict(path=m.rel(repair_path),sha256=m.sha(repair_path)),
                preservedFailure=dict(path=m.rel(old_path),sha256=m.sha(old_path)),
                allFinalPixelsReviewed=False,captionTimingApproved=False,finalTimingApproved=False,bodyRatioApproved=False,
                qaApproved=False,collected=False,uploaded=False,humanWholeListening='pending',humanPronunciation='pending',rightsApproved=False)
    m.save(pair_path,record)
    state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None,results=[cp_record,pp_record]);m.save(state_path,state)
    print(m.json.dumps(dict(frames=93084,bothDecodes=0,identicalAac=True,cleanReused=True,pixelsApproved=False)),flush=True)
except BaseException as e:
    state.update(status='failed',failedAt=m.stamp(),exitCode=1,error=repr(e));m.save(state_path,state);raise
