"""Final review pair is gated on all current mixed-ASR text and PCM comparisons."""
from pathlib import Path
import importlib.util,hashlib,json
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT;P=ROOT/'projects/game-lighting-history-04/production';OUT=ROOT/'production/research/game-lighting-history/local/part3-review-pair-v149'
PP=P/'part3-final-input-plan-v145.json';plan=m.read(PP);settings=m.read(P/'part3-final-mix-settings-v146.json')
AP=P/'part3-final-mixed-asr-direct-review-v147.json';approval=m.read(AP);execution=m.read(P/'part3-final-mixed-asr-execution-v147.json');request=m.read(P/'part3-final-mixed-asr-request-v147.json')
assert approval['allWholeAndIndependentTextsDirectlyCompared'] and approval['finalMixedAsrApproved']
assert approval['currentMixSha256']==settings['wavSha256']==m.sha(ROOT/settings['wav'])
assert approval['planSha256']==m.sha(PP)
assert execution['status']=='complete' and execution['exitCode']==0 and len(execution['results'])==len(request['windows'])
direct=m.read(ROOT/approval['directProgress']['path']);assert m.sha(ROOT/approval['directProgress']['path'])==approval['directProgress']['sha256']
assert len(direct['records'])==len(request['windows'])
reviewed={r['label']:r for r in direct['records']}
for r in execution['results']:
 assert m.sha(ROOT/r['path'])==r['sha256']==reviewed[r['label']]['resultSha256']
 assert reviewed[r['label']]['directFullExpectedAndActualTextRead'] and reviewed[r['label']]['allWordTimestampsRead']
pcm=m.read(ROOT/approval['pcmCorroboration']['path']);assert m.sha(ROOT/approval['pcmCorroboration']['path'])==approval['pcmCorroboration']['sha256']
assert pcm['allOriginalChapterSamplesPartitionedOnce'] and pcm['allSelectedPcmValuesExact'] and pcm['all23RecognitionWindowsCurrentMixExact']
assert pcm['allAdditionalArtifactContextsCurrentMixExact'] and pcm['additionalWindowCount']==5
artifactreview=m.read(ROOT/approval['artifactContextReview']['path'])
assert m.sha(ROOT/approval['artifactContextReview']['path'])==approval['artifactContextReview']['sha256']
assert artifactreview['allFullTextsAndTimestampsDirectlyCompared'] and artifactreview['observedChunkArtifactsResolved']
assert artifactreview['currentMixSha256']==settings['wavSha256'] and artifactreview['planSha256']==m.sha(PP)
artifactexecution=m.read(P/'part3-artifact-context-execution-v152.json')
assert artifactexecution['status']=='complete' and artifactexecution['exitCode']==0
for r in artifactexecution['results']:
 assert m.sha(ROOT/r['path'])==r['sha256']
 assert any(q['label']==r['label'] and q['resultSha256']==r['sha256'] and q['directFullExpectedAndActualTextRead'] and q['allWordTimestampsRead'] for q in artifactreview['records'])
visualproof=m.read(P/'part3-annotated-visual-build-v148.json');assert visualproof['planSha256']==m.sha(PP) and visualproof['wholeDecodeExitCode']==0
visual=ROOT/visualproof['path'];assert m.sha(visual)==visualproof['sha256']
layout=m.read(P/'part3-caption-layout-v147.json');ass=ROOT/layout['ass']['path'];assert m.sha(ass)==layout['ass']['sha256'] and layout['cueCount']==330 and layout['planSha256']==m.sha(PP)
audio=ROOT/settings['aac'];assert m.sha(audio)==settings['aacSha256']
resources=m.resources();SP=P/'part3-reviewed-pair-execution-v149.json';assert not SP.exists() and not OUT.exists();OUT.mkdir(parents=True)
state={'startedAt':m.stamp(),'status':'running','worker':m.worker(),'active':None,'resourceObservation':resources,'commands':[],'results':[],'allFinalPixelsReviewed':False,'qaApproved':False,'collected':False,'uploaded':False}
m.save(SP,state)
def checkpoint():
 cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
 j['episode04Part3ReviewPairV149']={'execution':m.rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'completedCommands':len(state['commands']),'finalApproved':False}
 j['ownedActiveWork']={'type':'part3-reviewed-clean-captioned-pair','execution':m.rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Every encoded cue/cut, moving annotations and spatial diagrams; then technical QA/four-file collection/private settings'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':m.rel(SP),'next':'Final encoded pixel and continuous teaching-flow review'}
 m.save(cp,j)
def run(args,label):
 checkpoint();r=m.run(args,label,state,SP,OUT);checkpoint();return r
def probe(file,label):
 cmd=[m.FP,'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,sample_rate,channels,duration:format=duration','-of','json',file]
 j=json.loads(m.subprocess.run(list(map(str,cmd)),capture_output=True,text=True,check=True).stdout);v=next(s for s in j['streams'] if s['codec_type']=='video');a=next(s for s in j['streams'] if s['codec_type']=='audio')
 assert len(j['streams'])==2 and (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',plan['finalFrames'])
 assert (a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2) and abs(float(j['format']['duration'])-plan['finalFrames']/60)<=1/60
 pc=[m.FP,'-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','json',file];pts=sorted(s['pts'] for s in json.loads(m.subprocess.run(list(map(str,pc)),capture_output=True,text=True,check=True).stdout)['packets']);assert pts==list(range(0,plan['finalFrames']*1500,1500))
 ac=[m.FP,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,duration,data_hash','-of','json',file];packets=json.loads(m.subprocess.run(list(map(str,ac)),capture_output=True,text=True,check=True).stdout)['packets'];packetsha=hashlib.sha256(json.dumps(packets,sort_keys=True).encode()).hexdigest()
 decode=run([m.FF,'-v','error','-nostdin','-threads','2','-i',file,'-f','null','NUL'],label+'-whole-decode')
 return {'path':m.rel(file),'sha256':m.sha(file),'frames':len(pts),'allPresentationPtsContinuous':True,'probe':j,'probeCommand':list(map(str,cmd)),'packetCommand':list(map(str,pc)),'aacPacketHashCommand':list(map(str,ac)),'aacPacketCount':len(packets),'aacPayloadPtsDurationHash':packetsha,'wholeDecode':decode,'allPixelsReviewed':False}
try:
 clean=OUT/'game-lighting-history-04-3.clean.mp4';captioned=OUT/'game-lighting-history-04-3.captioned.mp4'
 base=[m.FF,'-n','-hide_banner','-nostdin','-threads','2','-reinit_filter','0','-i',visual,'-i',audio,'-map','0:v:0','-map','1:a:0','-t',f"{plan['finalFrames']/60:.9f}",'-c:a','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart']
 cleanmux=run([*base,'-c:v','copy',clean],'clean-mux');cp=probe(clean,'clean')
 encode=run([*base,'-filter_threads','2','-vf',f"settb=1/90000,setpts=N*1500,ass=filename='{m.rel(ass)}'",'-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',captioned],'captioned-encode');pp=probe(captioned,'captioned')
 assert cp['aacPayloadPtsDurationHash']==pp['aacPayloadPtsDurationHash'] and cp['aacPacketCount']==pp['aacPacketCount']
 build={'createdAt':m.stamp(),'status':'encoded-review-pair-awaiting-all-pixels','slug':plan['slug'],'planSha256':m.sha(PP),'mixedAsrDirectApprovalSha256':m.sha(AP),'visualSha256':m.sha(visual),'mixAacSha256':m.sha(audio),'captionAssSha256':m.sha(ass),'clean':dict(cp,encode=cleanmux),'captioned':dict(pp,encode=encode),'identicalAacPayloadPtsDuration':True,'tracks':layout['tracks'],'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'bodyFrames':plan['bodyFrames'],'finalFrames':plan['finalFrames'],'ratioErrorFrames':plan['ratioErrorFrames'],'loudness':settings['finalAacMeasurement']['measurement'],'sourceAudioStreams':0,'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'captionTimingApproved':False,'finalTimingApproved':False,'bodyRatioApproved':False,'qaApproved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending','humanPronunciation':'pending','rightsApproved':False,'originalNimbusFileVerified':False};m.save(P/'part3-reviewed-pair-build-v149.json',build)
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None);m.save(SP,state);checkpoint();print(json.dumps({'frames':plan['finalFrames'],'twoDecodes':0,'identicalAac':True,'pixelsApproved':False}))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
