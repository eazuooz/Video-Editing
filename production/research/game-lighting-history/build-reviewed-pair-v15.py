"""Encode a review pair only after direct approval of every current mixed ASR window."""
import importlib.util, hashlib
from pathlib import Path
_p = Path(__file__).with_name('review-media-common-v15.py')
_s = importlib.util.spec_from_file_location('review_media', _p)
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
ROOT, PROD, FF, FP = m.ROOT, m.PROD, m.FF, m.FP
plan_path = PROD / 'measured-native-timeline-candidate-v15.json'
plan = m.read(plan_path)
settings = m.read(PROD / 'review-mix-settings-v15.json')
approval = m.read(PROD / 'review-mixed-asr-direct-review-v15.json')
assert approval['all54WindowsDirectlyCompared'] and approval['currentMixedContentApproved']
assert approval['mixSha256'] == settings['wavSha256'] and approval['planSha256'] == m.sha(plan_path)
asr = m.read(PROD / 'review-mixed-asr-execution-v15.json')
assert asr['status'] == 'complete' and asr['exitCode'] == 0 and len(asr['results']) == 54
progress_path = PROD / 'review-mixed-asr-direct-progress-v15.json'
progress = m.read(progress_path)
assert approval['directProgressSha256'] == m.sha(progress_path)
assert progress['mixSha256'] == approval['mixSha256'] and progress['planSha256'] == approval['planSha256']
assert len(progress['records']) == progress['directlyReadWindows'] == 54
reviewed = {r['label']: r for r in progress['records']}
assert len(reviewed) == 54 and set(reviewed) == {r['label'] for r in asr['results']}
for r in asr['results']:
    assert m.sha(ROOT / r['path']) == r['sha256'] == reviewed[r['label']]['resultSha256']
    assert reviewed[r['label']]['directFullExpectedAndActualTextRead'] and reviewed[r['label']]['allWordTimestampsRead']
pcm_path = PROD / 'review-mixed-asr-pcm-corroboration-v15.json'
pcm = m.read(pcm_path)
assert approval['pcmCorroborationSha256'] == m.sha(pcm_path)
assert pcm['mixSha256'] == approval['mixSha256'] and pcm['planSha256'] == approval['planSha256']
assert pcm['allOriginalSamplesPartitionedOnce'] and pcm['all105PlacementsSourceValuesExact'] and pcm['all54RecognitionWindowsCurrentMixExact']
assert approval['resolvedRecognitionArtifactsDirectlyCompared'], 'Resolve whole-window anomalies with complete contexts/current PCM first'
visual_proof_path = ROOT / 'production/research/game-lighting-history/local/explanation-framing-v15/silent-review-visual-v15.verification.json'
visual_proof = m.read(visual_proof_path)
visual = ROOT / visual_proof['output']
assert m.sha(visual) == visual_proof['outputSha256'] and visual_proof['wholeDecode']['exitCode'] == 0
assert visual_proof['observedFrames'] == plan['totals']['finalFrames'] and visual_proof['allPresentationPtsContinuous']
audio = ROOT / settings['aac']; assert m.sha(audio) == settings['aacSha256']
boxes = m.read(PROD / 'local/captions-v15/caption-layout-measurement.json')
ass = ROOT / boxes['ass']['path']; assert m.sha(ass) == boxes['ass']['sha256'] and boxes['cueCount'] == 356
observation = m.resources()
out = ROOT / 'production/research/game-lighting-history/local/review-pair-v15'
state_path = PROD / 'review-pair-execution-v15.json'
assert not state_path.exists() and not out.exists(), 'Preserve existing encoded pair; inspect before retry'
out.mkdir(parents=True)
state = dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,resourceObservation=observation,
             commands=[],results=[],allFinalPixelsReviewed=False,qaApproved=False,collected=False,uploaded=False)
m.save(state_path,state)
def probe_pair(file, label):
    cmd = [str(FP),'-v','error','-threads','2','-count_frames','-show_entries',
           'stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,sample_rate,channels,duration:format=duration',
           '-of','json',str(file)]
    probe = m.json.loads(m.subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
    video = next(x for x in probe['streams'] if x['codec_type']=='video')
    au = next(x for x in probe['streams'] if x['codec_type']=='audio')
    assert len(probe['streams'])==2
    assert (video['width'],video['height'],video['r_frame_rate'],video['time_base'],int(video['nb_read_frames']))==(1920,1080,'60/1','1/90000',plan['totals']['finalFrames'])
    assert (au['codec_name'],au['sample_rate'],au['channels'])==('aac','48000',2)
    assert abs(float(probe['format']['duration'])-plan['finalSeconds'])<=1/60
    packet_cmd=[str(FP),'-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','json',str(file)]
    pts=sorted(x['pts'] for x in m.json.loads(m.subprocess.run(packet_cmd,capture_output=True,text=True,check=True).stdout)['packets'])
    assert pts==list(range(0,plan['totals']['finalFrames']*1500,1500))
    payload_cmd=[str(FP),'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256',
                 '-show_entries','packet=data_hash','-of','json',str(file)]
    payload=m.json.loads(m.subprocess.run(payload_cmd,capture_output=True,text=True,check=True).stdout)['packets']
    packet_hashes=[x['data_hash'] for x in payload]
    decode=m.run([FF,'-v','error','-threads','2','-i',file,'-f','null','NUL'],label+'-whole-decode',state,state_path,out)
    return dict(path=m.rel(file),sha256=m.sha(file),frames=len(pts),allPresentationPtsContinuous=True,
                probe=probe,probeCommand=cmd,packetCommand=packet_cmd,aacPacketHashCommand=payload_cmd,
                aacPacketCount=len(packet_hashes),aacPayloadHash=hashlib.sha256('\n'.join(packet_hashes).encode()).hexdigest(),
                wholeDecode=decode,allPixelsReviewed=False)
try:
    clean=out/'game-lighting-history-03.clean.mp4'; captioned=out/'game-lighting-history-03.captioned.mp4'
    base=[FF,'-n','-v','error','-threads','2','-i',visual,'-i',audio,'-map','0:v:0','-map','1:a:0',
          '-t',str(plan['finalSeconds']),'-c:a','copy','-video_track_timescale','90000','-movflags','+faststart']
    clean_encode=m.run([*base,'-c:v','copy',clean],'clean-review-mux',state,state_path,out)
    cp=probe_pair(clean,'clean')
    relative_ass=m.rel(ass); assert ':' not in relative_ass and "'" not in relative_ass
    encoded=m.run([*base,'-vf',f"setpts=N/(60*TB),ass=filename='{relative_ass}'",
                   '-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',captioned],
                  'captioned-review-encode',state,state_path,out)
    pp=probe_pair(captioned,'captioned')
    assert cp['aacPayloadHash']==pp['aacPayloadHash'] and cp['aacPacketCount']==pp['aacPacketCount']
    record=dict(createdAt=m.stamp(),status='encoded-review-pair-awaiting-all-pixels',
                planSha256=m.sha(plan_path),mixedAsrDirectApprovalSha256=m.sha(PROD/'review-mixed-asr-direct-review-v15.json'),
                visualSha256=m.sha(visual),mixAacSha256=m.sha(audio),captionAssSha256=boxes['ass']['sha256'],
                captionPlanSha256=m.sha(PROD/'local/captions-v15/caption-plan.json'),
                clean=dict(cp,encode=clean_encode),captioned=dict(pp,encode=encoded),identicalAacPayload=True,
                sourceAudioStreams=0,allFinalPixelsReviewed=False,captionTimingApproved=False,
                finalTimingApproved=False,bodyRatioApproved=False,qaApproved=False,collected=False,uploaded=False,
                humanWholeListening='pending',humanPronunciation='pending',rightsApproved=False)
    m.save(PROD/'review-pair-build-v15.json',record)
    state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None)
    m.save(state_path,state)
    print(m.json.dumps(dict(frames=plan['totals']['finalFrames'],bothDecodes=0,identicalAac=True,pixelsApproved=False)))
except BaseException as e:
    state.update(status='failed',exitCode=1,failedAt=m.stamp(),error=str(e));m.save(state_path,state);raise
