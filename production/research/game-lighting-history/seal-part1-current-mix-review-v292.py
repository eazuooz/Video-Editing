"""Gate current review on direct new texts plus exact unchanged current PCM."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy,psutil
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production';rd=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(R).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def binding(p):return {'path':rel(p),'sha256':sha(p)}
PP=P/'part1-final-input-plan-v288.json';plan=rd(PP);settings=rd(P/'part1-final-mix-settings-v289.json');reusep=P/'part1-current-mixed-window-reuse-v289.json';reuse=rd(reusep);mix=R/settings['wav'];ex=rd(P/'part1-current-mixed-asr-execution-v290.json')
assert sha(PP)==settings['planSha256']==reuse['planSha256']==ex['planSha256'] and sha(mix)==settings['wavSha256']==reuse['mixSha256']==ex['mixSha256']
assert ex['status']=='complete' and ex['exitCode']==0
w=ex['worker'];assert not psutil.pid_exists(w['pid']) or abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01
freshp=P/'part1-current-mixed-fresh-direct-review-v290.json';fresh=rd(freshp);assert fresh['allFullTextsAndWordTimestampsDirectlyCompared'] and fresh['allObservedRecognitionConcernsResolved'] and fresh['currentMixSha256']==settings['wavSha256'] and fresh['planSha256']==sha(PP)
assert len(fresh['records'])==len(ex['results'])==reuse['freshCount']
freshmap={r['label']:r for r in fresh['records']};freshresults={r['label']:r for r in ex['results']}
for label,r in freshresults.items():
 q=freshmap[label];assert q['sha256']==r['sha256']==sha(R/r['path']) and q['expectedParagraphsAndFullActualTextDirectlyRead'] and q['allWordTimestampsDirectlyRead'] and q['contentApproved'] and q['observedResolution'].strip()
oldmainp=P/'part1-final-mixed-asr-direct-progress-v251.json';oldmain=rd(oldmainp);assert oldmain['allWholeAndIndependentTextsDirectlyCompared'] and oldmain['allWordEndingsAndTimestampsCompared'];mainmap={r['label']:r for r in oldmain['manuallyReadResults']}
oldextrap=P/'part1-artifact-context-direct-progress-v273.json';oldextra=rd(oldextrap);assert oldextra['allFullTextsAndTimestampsDirectlyCompared'];extramap={r['label']:r for r in oldextra['records']}
altp=P/'part1-independent-recognition-direct-review-v279.json';alt=rd(altp);assert alt['allFullTextsAndTimestampsDirectlyCompared'];altmap={r['label']:r for r in alt['records'] if r['contentApproved']}
proofp=P/'part1-final-pcm-preservation-v289.json';proof=rd(proofp);assert proof['allSelectedPcmValuesExact'] and proof['allOriginalChapterSamplesPartitionedOnce'] and proof['allOtherNormalized48kSamplesExact'] and proof['planSha256']==sha(PP)
records=[]
for item in reuse['reusedExactWindows']+reuse['freshRequiredWindows']:
 win=item['window'];label=win['label'];reused=item['stereo48kSamplesExact'];r=item['oldResult'] if reused else freshresults[label];result=rd(R/r['path']);assert sha(R/r['path'])==r['sha256'];wav=R/r['path'];wav=wav.with_suffix('.wav')
 assert sha(wav)==result['windowSha256']
 with sf.SoundFile(mix) as f:
  f.seek(win['fromFrame']*800);current=f.read((win['toFrame']-win['fromFrame'])*800,dtype='float32',always_2d=True).mean(axis=1)
 old,sr=sf.read(wav,dtype='float32');assert sr==48000 and np.array_equal(current,old),label
 if reused:
  assert item['oldSampleSha256']==item['currentSampleSha256'];q=mainmap.get(label) or extramap[label];assert q['sha256']==r['sha256'] and q['expectedParagraphsAndFullActualTextDirectlyRead'] and q['allWordTimestampsDirectlyRead']
  note=q.get('finding',q.get('observedResolution'));evidence=binding(oldmainp if label in mainmap else oldextrap)
  if label.startswith('artifact-context') and not q['contentApproved']:
   aq=altmap[label];assert aq['expectedParagraphsAndFullActualTextDirectlyRead'] and aq['allWordTimestampsDirectlyRead'] and sha(R/aq['path'])==aq['sha256'];ar=rd(R/aq['path']);assert ar['inputWindow']['sha256']==sha(wav);note=aq['observedResolution'];evidence=binding(altp)
 else:q=freshmap[label];note=q['observedResolution'];evidence=binding(freshp)
 records.append({'label':label,'path':r['path'],'sha256':r['sha256'],'window':win,'windowPcmSha256':sha(wav),'currentMixSamplesExact':True,'reusedExactRecognition':reused,'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,'directReviewEvidence':evidence,'observedResolution':note,'humanPronunciation':'pending'})
assert len(records)==36 and len({r['label'] for r in records})==36
whole=sorted([r for r in records if r['label'].startswith('whole')],key=lambda r:r['window']['fromFrame']);assert len(whole)==11 and whole[0]['window']['fromFrame']==120 and whole[-1]['window']['toFrame']==88548 and all(a['window']['toFrame']==b['window']['fromFrame'] for a,b in zip(whole,whole[1:]));assert sum(r['window']['toFrame']-r['window']['fromFrame'] for r in whole)==88428
assert len([p for r in whole for p in r['window']['paragraphIds']])==77
resolutions=[{'main':'whole-03','independent':['artifact-context-texture-streaming-input'],'concern':'Chunk-edge invented news ending and backward repeat resolved by complete independent context'}, {'main':'whole-04','independent':['artifact-context-ordinary-streaming-budget','context-texture-scene-return'],'concern':'Chunk-edge goodbye/backward repeat; budget and editing words corroborated'}, {'main':'whole-05','independent':['context-tsr-silhouette-history','context-tsr-rotation-vectors','artifact-context-original-18t-3'],'concern':'Quarter fractions resolved by full32-layer recognition on exact retained mix'}, {'main':'whole-06','independent':['artifact-context-outer-comparison-before','context-outer-displayed-frames'],'concern':'Replacement guide is freshly recognized in whole region and complete independent current mix'}, {'main':'whole-07','independent':['context-geometry-barrier-views','artifact-context-07-pre-visibility-interpolation'],'concern':'No independent repeated sentence, numeric interpolation values retained'}, {'main':'whole-10','independent':['context-rivalry-mobile-history','context-rivalry-surface-observation'],'concern':'Chunk-edge greeting and backward repetition absent from independent complete contexts'}, {'main':'context-runtime-texture-size','independent':['artifact-context-runtime-texture-consumer'],'concern':'정보 resolved by independent full32-layer recognition on exact retained mix'}]
known={r['label'] for r in records};assert all(r['main'] in known and all(k in known for k in r['independent']) for r in resolutions)
record={'reviewedAt':datetime.now(timezone.utc).isoformat(),'currentMixSha256':settings['wavSha256'],'planSha256':sha(PP),'records':records,'mainWindows':30,'additionalCompleteContexts':6,'freshCurrentWindows':3,'bitExactReusedWindows':33,'windowReuse':binding(reusep),'freshDirectReview':binding(freshp),'originalDirectProgress':binding(oldmainp),'originalArtifactProgress':binding(oldextrap),'independentNumericalLexicalResolution':binding(altp),'pcmPreservation':binding(proofp),'recognitionConcernResolutions':resolutions,'allWholeAndIndependentTextsDirectlyCompared':True,'allWordEndingsAndTimestampsCompared':True,'all36CurrentMixWindowSamplesExact':True,'allObservedRecognitionConcernsResolved':True,'noRemainingContentFailures':True,'finalMixedAsrApproved':True,'approvalScope':'Current mixed-ASR sentence coverage and independent complete context plus exact PCM for private technical review; human listening/pronunciation are pending. No ending heuristic approval.','humanWholeListening':'pending','humanPronunciation':'pending','publicRightsApproved':False,'originalNimbusFileVerified':False,'allFinalPixelsReviewed':False,'qaApproved':False,'uploaded':False}
dest=P/'part1-final-current-mixed-asr-direct-review-v292.json';assert not dest.exists();dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'mixedTechnicalApproved':True,'currentWindows':36,'newRecognitions':3,'bitExactReused':33,'humanListening':'pending'}))
