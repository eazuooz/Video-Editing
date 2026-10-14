"""Record bounded direct review; do not authorize dependent production."""
from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
target=R/'source-clarity-direct-review-v1.json';assert not target.exists()
baseline=read(R/'baseline-preservation-v1.json')
assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
ex=read(R/'audit-pixel-execution-v2.json');assert ex['workerExitCode']==0
groups=[]
for key in ['ncr','alternative','baseline']:
 m=read(R/f'local-audit-pixels-v2/{key}/manifest.json')
 assert m['actualPtsMatch'] and m['actualFfmpegExitCode']==0
 assert all(sha(ROOT/x['path'])==x['sha256'] for x in m['samples']+m['boards'])
 groups.append({'kind':key,'manifest':str((R/f'local-audit-pixels-v2/{key}/manifest.json').relative_to(ROOT)).replace('\\','/'),'samples':len(m['samples']),'boards':len(m['boards']),'allListedSamplePixelsDirectlyRead':True,'allHashesMatched':True,'exactSourcePtsVerified':True,'nativeWholeFramesApproved':False})
review={'observedAt':stamp,'actualOuterExitCode':0,'exitObservedChunk':'aa55e1','processAbsenceObservedChunk':'02deda','coverage':groups,'totalSamplesRead':50,'totalBoardsRead':10,'baselineProtectedFilesUnchanged':len(baseline['protectedFiles']),
 'comparison':[
  {'candidate':'NCR -Hpr1dqRzIk','boundedWindowSeconds':[22,61],'normalPlayback':'normal-playback-comparison-observation-v2.json','actualBrowserEndSeconds':61.076568,'decision':'preferred continuous-map candidate; annotation adoption still pending full selected-window review','beforeActionAfter':'Green/gray structures remain the same world; character banks, passes close walls, then returns to brighter open sky. The torso/arms can support a labelled projected bank guide.','clarityIssues':['30s is dark with weak silhouette separation','61.076568 browser endpoint is occluded by foreground wall; do not infer a clean native end from it'],'overlayMeaning':'Visible body/shoulder directions and screen-up reference; no measured world axes, roll degrees, input scheme or proprietary matrix values inferred.'},
  {'candidate':'Morkala FvSgGn941U0','boundedWindowSeconds':[22,61],'actualBrowserEndSeconds':61.095332,'decision':'reject this opening interval for a continuous first comparison','beforeActionAfter':'Pale gray/yellow/violet world at22/26; pink world at30/36/41; yellow world again at47/55/60. Portal/new-map changes interrupt one-body/one-reference comparison.','clarityIssues':['Character partly hidden by dark walls at41 and55','Discontinuous worlds introduce an unexplained change for a first-time viewer'],'notClaimed':'No claim that the whole recording is unsuitable; no VFR or engine-operation inference.'}
 ],
 'baselinePixelFindings':[
  {'scenes':['01'],'samplesSeconds':[2,10,19],'finding':'Overview states viewer question and actual order/outcome; retain original4 sentences/20.16seconds. Overview panels are readable but are flat cards, so add useful spatial example linkage rather than declare them projected3D.'},
  {'scenes':['02','05','08','11','14','17','20','23'],'finding':'Gameplay is full-screen with fixed bottom captions and small source credit. No narrated geometry is currently drawn on character/background. At140/166 and259 the dark body needs a contrasting tracked guide; movements alone do not show the coordinate reference.'},
  {'scenes':['03','04','06','07','09','10','13','15','16','21','22'],'finding':'Existing projected airplane/axes visibly show depth and occlusion; preserve accepted formulas and order. Add world-reference axes beside local axes and animate basis columns/projections with the same small worked example.'},
  {'scenes':['12'],'finding':'Child→parent→world card chain is readable but does not show nested poses spatially. Add a parent/body/part projected example without shortening original explanation.'},
  {'scenes':['18'],'sampleSeconds':659,'finding':'Green filled memory block covers the center label in this sampled state. Hold final adoption until a target layout/motion repair reveals Euler12B and comparison labels throughout their narrated interval.'},
  {'scenes':['19','24'],'finding':'Code and summary are readable; preserve semantic syntax colors and original API distinction. Connect code outputs to an already-worked vector and retrieve the opening flight question in the conclusion.'},
  {'sampleSeconds':[280,491],'finding':'Two isolated baseline samples have no narration box; not automatically a missing-caption defect. Check actual cue timing and current audio before deciding.'}
 ],
 'retainedOriginal':{'scenes':24,'koLines':140,'enLines':140,'approvedPcm':24,'wholeOpeningSeconds':20.16,'palette':'recorded legacy white','bodyRatio':'lecture actual40:explanation60','bgm':False,'catFrames':120,'memberFrames':600},
 'gates':{'originalFullKoEnRead':True,'relevantCurrentMathReferenceRead':True,'boundedCandidateComparisonRead':True,'allSelectedNativeCutsApproved':False,'allNewOnFootageGeometryMotionApproved':False,'dependentNewNarrationApproved':False,'newTtsStarted':False,'newFinalPixelsApproved':False,'currentMixedAudioApproved':False,'replacementVideoId':None,'publicRightsApproved':False,'humanListeningApproved':False}}
write(target,review)
ex['actualOuterExitCode']=0;ex['exitObservedChunk']='aa55e1';ex['processAbsenceObservedChunk']='02deda';ex['bounded50SamplePixelsDirectlyRead']=True;ex['allPixelsDirectlyRead']=True;ex['wholeNativeFramesApproved']=False;write(R/'audit-pixel-execution-v2.json',ex)
cp=read(R/'latest-checkpoint.json');cp.update({'observedAt':stamp,'stage':'bounded-baseline-and-candidate-pixels-reviewed-selected-native-audit-next','initialPixelReview':str(target.relative_to(ROOT)).replace('\\','/'),'auditSamplesRead':50,'auditBoardsRead':10,'allSelectedNativeCutsApproved':False,'next':'Read selected-source native windows/UI and exact frames, then annotate moving body/reference guides and insert only needed prerequisite bridges.'});write(R/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qp)
item=next(x for x in q['items'] if x['slug']=='game-math-orientation-matrices');item['baseline']['freshTimeTimezoneReopened']=True;item['review']['fullScriptAndClaimsRead']=True;item['review']['referenceFlowCompared']=True;item['review']['firstTimeGameplayCompared']=True;item['review']['openingOverviewPassed']=True;item['review']['comparisonScope']='bounded candidate and baseline samples; final and all selected native cut approval pending';item['sourceClarityAudit']=str(target.relative_to(ROOT)).replace('\\','/')
# Keep motion completion in its own item/evidence; remove misleading current-job carry-over.
old=q['execution'];hist={k:old.pop(k) for k in ['actualNewVideoId','actualReplacementVideoId','baselineScheduleChanged','currentMixedWholeReview','independentContextPlan','finalMediaAdoption','collectionEvidence','privateUploadReceipt'] if k in old}
if hist:old['preservedPreviousMotionExecutionFields']=hist
old.update({'currentSlug':'game-math-orientation-matrices','stage':cp['stage'],'ownedJob':None,'next':cp['next'],'newReplacementVideoId':None,'orientationInitialPixelReview':str(target.relative_to(ROOT)).replace('\\','/')})
q['updatedAt']=stamp;write(qp,q)
print(json.dumps({'protectedUnchanged':len(baseline['protectedFiles']),'samplesDirectlyRead':50,'boardsDirectlyRead':10,'allSelectedNativeCutsApproved':False}))
