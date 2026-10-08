"""Prepare paired additive guides; protect original audio/scripts and reviewed white inputs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;MC=ROOT/'motion-canvas/src/projects/player-customization'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
fixed=read(BASE/'white-fixes-verification-v2.json');assert fixed['exitCode']==0 and len(fixed['boards'])==6
for r in fixed['boards']+fixed['samplePlan']:assert sha(ROOT/r['path'])==r['sha256']
assert sha(ROOT/fixed['currentWhite']['path'])==fixed['currentWhite']['sha256']
save(BASE/'white-fixes-motion-direct-review-v2.json',{'schemaVersion':1,'reviewedAt':now,'slug':'player-customization',
 'directlyReadBoards':fixed['boards'],'all24SamplesDirectlyRead':True,'currentWhite':fixed['currentWhite'],
 'findings':{'01-overview':'All three labels remain readable through camera yaw and token travel/lift. Exact prominent rights notice remains visible in all12 samples.',
  '05-manageable-choice':'Candidate travels from the grid to the separate green right pedestal. Blue current choice remains separate. Comparison and departure arrow remain clear in paragraphs2/3/4.'},
 'fixPixelsApproved':True,'genuineProjectedDepthObserved':True,'verificationExitCodeObserved':0,'verificationSessionId':54389,
 'worker58308AbsentObserved':True,'workerCreationIdentityObserved':False,'originalOtherSixNotRerendered':True,
 'allOriginalPcmPreserved':True,'finalCaptionPixelsReviewed':False,'finalMixedAsrApproved':False,'finalVideoComplete':False})
fixed.update(fixPixelsApproved=True,actualAnimatedSamplesDirectlyRead=True,directReview='projects/player-customization/production/white-fixes-motion-direct-review-v2.json',
 sessionId=54389,actualSessionExitCodeObserved=0,actualCimPidAbsent=True);save(BASE/'white-fixes-verification-v2.json',fixed)
old=read(BASE/'current-white-source-verification-v1.json');rows=read(MC/'current-voice-timing-v1.json')['rows'];offset=0;inputs=[]
for r in rows:
 replacement=r['id'] in ['01-overview','05-manageable-choice']
 inputs.append({'id':r['id'],'path':fixed['currentWhite']['path'] if replacement else old['currentWhite']['path'],
  'sha256':fixed['currentWhite']['sha256'] if replacement else old['currentWhite']['sha256'],
  'sourceInFrame':(0 if r['id']=='01-overview' else 1325) if replacement else offset,'frames':r['frames'],
  'motionPixelsDirectlyReviewed':True,'review':'projects/player-customization/production/white-fixes-motion-direct-review-v2.json' if replacement else 'projects/player-customization/production/current-white-motion-direct-review-v1.json'})
 offset+=r['frames']
save(BASE/'current-reviewed-original-white-inputs-v2.json',{'schemaVersion':1,'reviewedAt':now,'status':'original-eight-source-motion-approved-before-final-composite',
 'scenes':inputs,'frames':13439,'originalScenePcmPreserved':True,'allSourceMotionSamplesRead':True,'allFinalCaptionPixelsReviewed':False,'finalVideoComplete':False})
ko_path=ROOT/'projects/player-customization/script/observation-guides.ko.v1.json';en_path=ROOT/'projects/player-customization/script/observation-guides.en.v1.json'
ko=read(ko_path);en=read(en_path);assert len(ko['scenes'])==len(en['scenes'])==8
old_req=read(BASE/'narration-tts-request-v1.json');protected=old_req['protectedInputs'].copy()
for x in protected:assert sha(ROOT/x['path'])==x['sha256'],x['path']
oldtts=read(BASE/'narration-tts-execution-v1.json');assert oldtts['generationComplete'] and len(oldtts['results'])==8
for r in oldtts['results']:protected.append({'path':r['path'],'sha256':r['sha256']})
for p in [ko_path,en_path,MC/'observation-guide-explanation-v1.tsx',BASE/'current-reviewed-original-white-inputs-v2.json']:
 protected.append({'path':rel(p),'sha256':sha(p)})
bank=read(ROOT/'projects/player-customization/sources/native-source-bank-v1.json')
source_ranges=[
 [('gauss',21.5,30),('gauss',39.5,65),('gauss',71.5,91.8),('dante',30,64)],
 [('dante',68,100),('dante',109,124),('dante',221,233)],
 [('jade',47,53.5),('jade',72,75.8),('jade',140,148.8),('jade',171.7,192.8)],
 [('yareli',61,63.5),('yareli',65,66.5),('yareli',69.5,72.8),('jade',524,539.5),('dante',233,244)],
 [('dante',100,129),('dante',134,164),('dante',431,440)],
 [('dante',165,175),('dante',215,221),('dante',250,254),('dante',258,279)],
 [('jade',153,169),('dante',285,295),('dante',410,431)],
 [('dante',441,449),('dante',455,490),('dante',500,524)]
]
reviews={'gauss':'projects/player-customization/production/gauss-profile-direct-review-v1.json','jade':'projects/player-customization/production/jade-native-direct-review-v1.json',
 'yareli':'projects/player-customization/production/yareli-native-direct-review-v1.json','dante':'projects/player-customization/production/dante-native-direct-review-v1.json'}
guide_rows=[];mc_dir=MC/'observation-guide-scenes-v1';mc_dir.mkdir()
for i,(k,e) in enumerate(zip(ko['scenes'],en['scenes'])):
 assert k['id']==e['id'] and k['insertAfter']==e['insertAfter'] and len(k['lines'])==len(e['lines'])==4
 assert all(len(x)>30 for x in k['lines'])
 wrapper=mc_dir/(k['id']+'.tsx')
 wrapper.write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {observationGuideExplanation} from '../observation-guide-explanation-v1';\nimport timing from '../observation-guide-timing-prepared-v1.json';\nexport default makeScene2D(function*(view){yield* observationGuideExplanation(view,'"+k['id']+"',timing.rows["+str(i)+"]);});\n",'utf-8')
 guide_rows.append({'id':k['id'],'koTitle':k['title'],'enTitle':e['title'],'insertAfter':k['insertAfter'],
  'fullKoLinesDirectlyReviewed':k['lines'],'fullEnLinesDirectlyReviewed':e['lines'],
  'tentativeResearchRanges':[{'source':s,'localInSeconds':a,'localOutSeconds':b,'nativeReview':reviews[s],
   'boundaryStatus':'native samples read; exact continuous final edge/crop selection pending; exclusions inside broad research range are not quota'} for s,a,b in source_ranges[i]],
  'diagramConnection':k['title'],'independentMcScene':rel(wrapper),'mcRendered':False,'actualQuotaApproved':False})
save(MC/'observation-guide-timing-prepared-v1.json',{'status':'unmeasured-authoring-only-not-final-render','rows':[{'id':s['id'],'durationSeconds':40,'paragraphStarts':[0,10,20,30],'measured':False} for s in ko['scenes']]})
review={'schemaVersion':1,'reviewedAt':now,'slug':'player-customization','status':'paired-additive-guides-ready-for-approved-voice-measurement',
 'original32KoAnd32EnAnd223point92SecondsPcmPreserved':True,'newScenes':8,'newKoParagraphs':32,'newEnParagraphs':32,
 'koSha256':sha(ko_path),'enSha256':sha(en_path),'rows':guide_rows,'pairedWholeTextDirectReview':True,
 'overviewPromiseReview':{'centralQuestion':'Equipment/appearance selection becomes enjoyable through understood outcomes, short tests and expression.',
  'openingStill22point08Seconds':True,'firstExampleStillGauss':True,'order':['Gauss/action outcomes','Jade/spatial outcome','situations','selection purpose','test and return','appearance preview','original conclusion'],
  'danteAddsObservedExamplesWithinSameWarframeStep':True,'newConclusionOrUnpromisedTopicAdded':False,'matched':True},
 'claimLimits':['Observed positions, casts, projectile directions, effects and targets only. No complete loadout before/after claim, optimal build, damage ranking, developer intent or victory inference.',
  'Original profiles2019/2021 and2024 developer work-in-progress shots are separate versions; no present-build fidelity claim.',
  'Research ranges overlap for writing context only. Final unique selected footage must not overlap; no loop, slowdown, idle, host, community art or logo quota.',
  'Timing, exact60:40, per-paragraph visible role, final crop/caption pixels and mixed ASR remain false until measured review.'],
 'allResearchSourcesInspectedBeforeWriting':True,'danteContinuousReview':'projects/player-customization/production/dante-continuous-crop-review-v1.json',
 'contentReadyForApprovedVoiceMeasurement':True,'finalTimingApproved':False,'finalVideoComplete':False}
review_path=BASE/'observation-guides-paired-review-v1.json';save(review_path,review);protected.append({'path':rel(review_path),'sha256':sha(review_path)})
outline=ROOT/'projects/player-customization/planning/observation-guide-additions-v1.md'
outline.write_text('# Player customization: additive observation guides\n\nThe original eight scenes,32 KO/EN paragraphs,223.92 seconds of PCM and original overview/conclusion are preserved. The additions were written after native source and bounded CUA inspection. They connect actual observed action to the original explanation.\n\n'+
 '\n'.join(f'- {r["id"]}: after {r["insertAfter"]}; {r["koTitle"]}. Independent KO/EN and MC authoring prepared; exact voice/timing/cut approval remains pending.' for r in guide_rows)+
 '\n\nUse only uniquely allocated actual action segments. Broad research ranges above are not selected intervals. Preserve all useful original white explanation, allocate the measured body at60:40 with at most one-frame rounding, and keep UI/diagrams classified as explanation. Only cat2s/member10s are excluded. Measure current audio before deciding guide white bridge durations.\n\nFixed boxed-white-forest-v1 captions remain at960,970/MC0,430. Preserve approved Qwen1.7/reference and continuous Nimbus. All final audio, captions, current mixed ASR, rendered pixels, collection and private upload remain pending.\n','utf-8')
protected.append({'path':rel(outline),'sha256':sha(outline)})
request={'schemaVersion':1,'slug':'player-customization','preparedAt':now,'device':'cpu','cpuThreads':2,'gpuJobs':0,
 'pairedWholeTextReview':True,'overviewPromiseReview':True,'scriptReview':rel(review_path),'protectedInputs':protected,
 'scenes':[{'id':k['id'],'text':' '.join(k['lines']),'enLines':e['lines'],'path':f'shared/output/narration/player-customization/observation-guides-qwen1.7-v1/{k["id"]}-scene.wav'} for k,e in zip(ko['scenes'],en['scenes'])]}
save(BASE/'observation-guides-tts-request-v1.json',request)
worker=(BASE/'render-narration-cpu-v1.py').read_text('utf-8')
for a,b in [('narration-tts-execution-v1','observation-guides-tts-execution-v1'),('narration-tts-v1.log','observation-guides-tts-v1.log'),
 ('narration-tts-request-v1','observation-guides-tts-request-v1'),('narration-tts-session-v1','observation-guides-tts-session-v1'),
 ('approved-voice-single-CPU2-measurement','additional-observation-guides-single-CPU2-measurement'),('eight-scenes-measured-awaiting-full-ASR','eight-observation-guides-measured-awaiting-full-ASR')]:worker=worker.replace(a,b)
worker=worker.replace("        rn.assemble_outputs(rn.load_jobs())\n",'')
worker=worker.replace("            provisionalNarration=dict(path=rel(rn.FINAL_WAV),sha256=sha(rn.FINAL_WAV),timing=rel(rn.TIMING_JSON),koSrt=rel(rn.FINAL_SRT),paragraphBoundaryMethod='quiet valleys near text weights, not final ASR alignment'))", "            originalEightSceneNarrationAndProvisionalMixPreserved=True)")
worker=worker.replace("if launch.get('pid')==os.getpid(): state['sessionId']=launch['sessionId']", "if launch.get('pid')==os.getpid(): state.update(sessionId=launch['sessionId'],processIdentity=launch.get('processIdentity'))")
worker=worker.replace("completed=len(state['results']),total=8,workerExpectedRunning", "processIdentity=state.get('processIdentity'),completed=len(state['results']),total=8,workerExpectedRunning")
worker=worker.replace("item.update(stage=cp['stage'],currentExecution=job,ttsStarted=True,narrationMeasurement=", "item.update(stage=cp['stage'],currentExecution=job,ttsStarted=True,additionalGuidesNarrationMeasurement=")
(BASE/'render-observation-guides-cpu-v1.py').write_text(worker,'utf-8')
cp=read(BASE/'latest-checkpoint.json');cp['executionHistory'].append(dict(cp['ownedJob'],actualSessionExitCodeObserved=0,sessionId=54389,actualCimPidAbsent=True))
cp.update(recordedAt=now,stage='original-eight-white-source-motion-reviewed-additive-guides-prepared',ownedJob=None,
 currentReviewedWhiteInputs='projects/player-customization/production/current-reviewed-original-white-inputs-v2.json',
 additionalGuidesReview=rel(review_path),additionalGuidesPrepared=True,additionalGuidesTtsStarted=False,
 nextAction='Fresh actual resources then one guarded CPU2 guide voice job. Original media complete; do not repeat original TTS/ASR/white renders. Final allocation/guide ASR/mix/captions/QA/private pending.')
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(i for i in q['items'] if i['slug']=='player-customization');item.update(stage=cp['stage'],currentExecution=None,currentReviewedWhiteInputs=cp['currentReviewedWhiteInputs'],additionalGuidesReview=rel(review_path),nextAction=cp['nextAction']);q['updatedAt']=now;save(qp,q)
print(json.dumps({'originalWhiteSourceScenesApproved':8,'originalPcmPreserved':True,'newPairedGuideParagraphs':32,'guideTtsStarted':False,'finalVideoComplete':False}))
