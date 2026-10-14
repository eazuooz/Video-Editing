"""Current pair after6promo-frame correction: same37current mixed windows; final pixels remain unapproved."""
from pathlib import Path
import importlib.util,hashlib,json,psutil,os
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT;P=ROOT/'projects/game-lighting-history-04/production'
OUT=ROOT/'production/research/game-lighting-history/local/part1-review-pair-v317'
PP=P/'part1-final-input-plan-v309.json';plan=m.read(PP)
settings=m.read(P/'part1-final-mix-settings-v310.json')
AP=P/'part1-final-current-mixed-asr-direct-review-v312.json';approval=m.read(AP)
assert approval['allWholeAndIndependentTextsDirectlyCompared'] and approval['allWordEndingsAndTimestampsCompared']
assert approval['finalMixedAsrApproved'] and approval['allObservedRecognitionConcernsResolved'] and approval['noRemainingContentFailures'] and approval['all37CurrentMixWindowSamplesExact']
assert approval['currentMixSha256']==settings['wavSha256']==m.sha(ROOT/settings['wav']) and approval['planSha256']==m.sha(PP)
assert len(approval['records'])==37 and approval['mainWindows']==30 and approval['additionalCompleteContexts']==7
assert approval['bitExactReusedWindows']==35 and approval['freshCurrentWindows']==2
for r in approval['records']:
 assert r['currentMixSamplesExact'] and m.sha(ROOT/r['path'])==r['sha256']
 assert r['expectedParagraphsAndFullActualTextDirectlyRead'] and r['allWordTimestampsDirectlyRead'] and r['observedResolution'].strip()
 e=r['directReviewEvidence'];assert m.sha(ROOT/e['path'])==e['sha256']
for key in ['windowReuse','freshDirectReview','originalDirectProgress','originalArtifactProgress','independentNumericalLexicalResolution','pcmPreservation']:
 e=approval[key];assert m.sha(ROOT/e['path'])==e['sha256']
currentExecution=m.read(P/'part1-current-mixed-asr-execution-v311.json')
assert currentExecution['status']=='complete' and currentExecution['exitCode']==0 and len(currentExecution['results'])==2
assert currentExecution['mixSha256']==settings['wavSha256'] and currentExecution['planSha256']==m.sha(PP)
w=currentExecution['worker'];assert not psutil.pid_exists(w['pid']) or abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01
pcm=m.read(ROOT/approval['pcmPreservation']['path'])
assert pcm['allSelectedPcmValuesExact'] and pcm['allOriginalChapterSamplesPartitionedOnce'] and pcm['allOtherNormalized48kSamplesExact']
visualproof=m.read(P/'part1-final-visual-build-v316.json')
assert visualproof['planSha256']==m.sha(PP) and visualproof['wholeDecodeExitCode']==0 and visualproof['all89148PtsExact1500']
visual=ROOT/visualproof['path'];assert m.sha(visual)==visualproof['sha256']
visualproof['inputOverrides']['vtPlan']={'planPath':m.rel(PP),'sha256':m.sha(PP),'changedInput':'texture-dependent-conversion:native'}
promo=m.read(P/'part1-promo-boundary-proposal-v315.json')
assert promo['fullProposedSourceNormalSpeedReviewed'] and promo['normalSpeedSourceReview']['movingSourceApproved']
assert visualproof['retainedOther93InputsByteIdentical'] and visualproof['newTts']==0 and visualproof['newAudioMix']==0
assert visualproof['inputOverrides']['sha256']==m.sha(P/'part1-promo-boundary-proposal-v315.json')
oldvisual=m.read(P/'part1-final-visual-build-v250.json');moving=m.read(P/'part1-corrected-moving-input-direct-review-v257.json')
assert moving['allCorrectedEncodedMovingPixelsReviewed'] and moving['visualBuildSha256']==m.sha(P/'part1-final-visual-build-v250.json') and len(moving['records'])==5
currentCuts={r['id']:r for r in visualproof['cuts']};oldcuts={r['id']:r for r in oldvisual['cuts']}
assert len(currentCuts)==94
for key,r in currentCuts.items():
 assert m.sha(ROOT/r['path'])==r['sha256']
 if key not in ['outer-comparison-before:model','texture-dependent-conversion:native','cyber-surface-observation:native']:assert r['sha256']==oldcuts[key]['sha256']
for r in oldvisual['repairs']:
 if r['id']=='cyber-surface-observation:native':
  assert currentCuts[r['id']]['sourceCuts']==promo['proposedCuts'] and currentCuts[r['id']]['frames']==1508
  continue
 assert currentCuts[r['id']]['sha256']==r['sha256']
 assert any(q['id']==r['id'] and q['sha256']==r['sha256'] and q['normalSpeedPlaybackDirectlyObserved'] and q['movingPixelsApproved'] for q in moving['records'])
guide=m.read(P/'part1-selected-guide-moving-review-v289.json')
assert guide['planSha256']==m.sha(P/'part1-final-input-plan-v288.json') and guide['normalSpeedPlaybackObserved'] and guide['actualProjectedTopSideFaces'] and guide['displaySequenceArrowProgressObserved'] and guide['separateGameStateUpdateTrackClear'] and guide['final81FramesReadableComparisonHold']
assert guide['video']==next(c['video'] for c in plan['cuts'] if c['id']=='outer-comparison-before:model')
layout=m.read(P/'part1-caption-layout-v309.json');ass=ROOT/layout['ass']['path']
assert m.sha(ass)==layout['ass']['sha256'] and layout['cueCount']==335 and layout['planSha256']==m.sha(PP)
sem=m.read(P/'part1-semantic-caption-review-v312.json');assert sem['approved'] and sem['manualSemanticReview'] and sem['paragraphCount']==77 and sem['unchanged76ParagraphsExact'] and sem['planSha256']==m.sha(PP)
audio=ROOT/settings['aac'];assert m.sha(audio)==settings['aacSha256']

old289=m.read(P/'part1-final-visual-build-v289.json');previousCuts={r['id']:r for r in old289['cuts']}
for key,r in currentCuts.items():
 if key not in ['texture-dependent-conversion:native','cyber-surface-observation:native']:assert r['sha256']==previousCuts[key]['sha256']
 elif key=='texture-dependent-conversion:native':assert r['retainedByteIdenticalToV289'] is False and r['frames']==970
 else:assert r['retainedByteIdenticalToV310'] is False and r['frames']==1508
prior310=m.read(P/'part1-final-visual-build-v310.json');prior310cuts={r['id']:r for r in prior310['cuts']}
for key,r in currentCuts.items():
 if key!='cyber-surface-observation:native':assert r['sha256']==prior310cuts[key]['sha256']
else:assert currentCuts['cyber-surface-observation:native']['sourceCuts']==promo['proposedCuts']
vtReview=m.read(P/'part1-vt-direction-direct-review-v309.json');assert vtReview['selectedForPrivateTechnicalProduction'] and vtReview['sourceReview']['fullCandidateActuallyPlayed']
assert sem['changedDirectReview']['sha256']==m.sha(P/'part1-vt-direction-direct-review-v309.json')
ancestors={p.pid for p in psutil.Process().parents()}|{os.getpid()}
for proc in psutil.process_iter(['pid','name','cmdline','create_time']):
 d=proc.info;cmd=' '.join(d['cmdline'] or [])
 if d['pid'] not in ancestors and (d['name'] or '').lower().startswith('python') and any(t in cmd for t in ['review-part1-final-mix-v243.py','review-part1-artifact-contexts-v255.py','repair-part1-observed-native-pixels-v250.py','review-part1-vt-current-mix-v311.py','build-part1-vt-correction-media-v310.py','build-part1-reviewed-pair-v313.py','build-part1-promo-only-visual-v316.py','build-part1-reviewed-pair-v317.py']):
  raise RuntimeError('Preserve the actual single owned media worker; no overlapping encode.')
resources=m.resources();SP=P/'part1-reviewed-pair-execution-v317.json'
assert not SP.exists() and not OUT.exists();OUT.mkdir(parents=True)
state={'startedAt':m.stamp(),'status':'running','worker':m.worker(),'active':None,'resourceObservation':resources,'commands':[],'results':[],
 'allFinalPixelsReviewed':False,'qaApproved':False,'collected':False,'uploaded':False}
m.save(SP,state)
def checkpoint():
 cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
 j['episode04Part1ReviewPairV317']={'execution':m.rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'completedCommands':len(state['commands']),'finalApproved':False}
 j['ownedActiveWork']={'type':'part1-reviewed-clean-captioned-pair','execution':m.rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Every335 encoded cue and94 cuts; moving annotations and spatial diagrams; then QA/four-file collection/private settings'} if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':m.rel(SP),'next':'Final encoded pixels and continuous teaching-flow review'}
 m.save(cp,j)
def run(args,label):
 checkpoint();r=m.run(args,label,state,SP,OUT);checkpoint();return r
def probe(file,label):
 cmd=[m.FP,'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,sample_rate,channels,duration:format=duration','-of','json',file]
 j=json.loads(m.subprocess.run(list(map(str,cmd)),capture_output=True,text=True,check=True).stdout)
 v=next(s for s in j['streams'] if s['codec_type']=='video');a=next(s for s in j['streams'] if s['codec_type']=='audio')
 assert len(j['streams'])==2 and (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',plan['finalFrames'])
 assert (a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2) and abs(float(j['format']['duration'])-plan['finalFrames']/60)<=1/60
 pc=[m.FP,'-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','json',file]
 pts=sorted(s['pts'] for s in json.loads(m.subprocess.run(list(map(str,pc)),capture_output=True,text=True,check=True).stdout)['packets'])
 assert pts==list(range(0,plan['finalFrames']*1500,1500))
 ac=[m.FP,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,duration,data_hash','-of','json',file]
 packets=json.loads(m.subprocess.run(list(map(str,ac)),capture_output=True,text=True,check=True).stdout)['packets']
 packetsha=hashlib.sha256(json.dumps(packets,sort_keys=True).encode()).hexdigest()
 decode=run([m.FF,'-v','error','-nostdin','-threads','2','-i',file,'-f','null','NUL'],label+'-whole-decode')
 return {'path':m.rel(file),'sha256':m.sha(file),'frames':len(pts),'allPresentationPtsContinuous':True,'probe':j,'probeCommand':list(map(str,cmd)),
 'packetCommand':list(map(str,pc)),'aacPacketHashCommand':list(map(str,ac)),'aacPacketCount':len(packets),'aacPayloadPtsDurationHash':packetsha,'wholeDecode':decode,'allPixelsReviewed':False}
try:
 clean=OUT/'game-lighting-history-04-1.clean.mp4';captioned=OUT/'game-lighting-history-04-1.captioned.mp4'
 base=[m.FF,'-n','-hide_banner','-nostdin','-threads','2','-reinit_filter','0','-i',visual,'-i',audio,'-map','0:v:0','-map','1:a:0','-t',f"{plan['finalFrames']/60:.9f}",'-c:a','copy','-video_track_timescale','90000','-movie_timescale','48000','-movflags','+faststart']
 cleanmux=run([*base,'-c:v','copy',clean],'clean-mux');cp=probe(clean,'clean')
 encode=run([*base,'-filter_threads','2','-vf',f"settb=1/90000,setpts=N*1500,ass=filename='{m.rel(ass)}'",'-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',captioned],'captioned-encode');pp=probe(captioned,'captioned')
 assert cp['aacPayloadPtsDurationHash']==pp['aacPayloadPtsDurationHash'] and cp['aacPacketCount']==pp['aacPacketCount']
 build={'createdAt':m.stamp(),'status':'encoded-review-pair-awaiting-all-pixels','slug':plan['slug'],'planSha256':m.sha(PP),
  'inputOverrides':visualproof['inputOverrides'],'mixedAsrDirectApprovalSha256':m.sha(AP),'movingInputApprovalSha256':m.sha(P/'part1-corrected-moving-input-direct-review-v257.json'),
  'visualSha256':m.sha(visual),'mixAacSha256':m.sha(audio),'captionAssSha256':m.sha(ass),'clean':dict(cp,encode=cleanmux),'captioned':dict(pp,encode=encode),
  'identicalAacPayloadPtsDuration':True,'tracks':layout['tracks'],'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'bodyFrames':plan['bodyFrames'],
  'finalFrames':plan['finalFrames'],'ratioErrorFrames':plan['ratioErrorFrames'],'loudness':settings['finalAacMeasurement']['measurement'],'sourceAudioStreams':0,
  'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'captionTimingApproved':False,'finalTimingApproved':False,'bodyRatioApproved':False,'qaApproved':False,'collected':False,'uploaded':False,
  'humanWholeListening':'pending','humanPronunciation':'pending','rightsApproved':False,'originalNimbusFileVerified':False}
 m.save(P/'part1-reviewed-pair-build-v317.json',build)
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None);m.save(SP,state);checkpoint()
 print(json.dumps({'frames':plan['finalFrames'],'twoDecodes':0,'identicalAac':True,'pixelsApproved':False}))
except BaseException as e:
 state.update(status='failed',exitCode=1,error=repr(e),failedAt=m.stamp());m.save(SP,state);checkpoint();raise
