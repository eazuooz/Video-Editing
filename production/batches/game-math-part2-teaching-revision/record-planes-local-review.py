"""Record the performed review precisely, including sampled explanation pages."""
from pathlib import Path
import datetime, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
slug,digest=sys.argv[1:3]
assert slug in ['game-math-plane-distances-v2','game-math-triangle-addresses-v2']
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
P=ROOT/'projects'/slug; W=ROOT/'shared/output'/slug
m=read(P/'project.json');t=read(P/'production/timeline.json');qa=read(P/'production/qa.json')
assert sha(ROOT/m['paths']['videoBurnedCaptions'])==digest==qa['videos']['videoBurnedCaptions']['sha256']
assert qa['fullDecodePassed'] and qa['ratioErrorFrames']==0 and qa['koEnMatchingTimes']
assert t['actualFrames']*5==t['bodyFrames']*2 and t['explanationFrames']*5==t['bodyFrames']*3
assert not qa['backgroundMusic'] and not qa['sourceAudioUsed']
native=read(W/'native-final-playback.json')
assert native['sha256']==digest and native['ended'] and native['playbackRate']==1 and abs(native['currentTime']-t['seconds'])<.04
caption=read(W/'caption-review/index.json');composition=read(W/'composition-review/index.json');detail=read(W/'final-detail-review/index.json')
assert caption['sha256']==composition['sha256']==digest
assert caption['cueCount']==len(t['koCaptions']) and len(composition['records'])==len(t['scenes'])+2
assert all(r['sourceSha256']==digest for r in detail['records'])
preserved=read(B/'planes-preservation-audit.json')
assert preserved['allOriginalSceneDictionariesExact'] and preserved['originalOrderAndContractExact'] and preserved['allOriginalPCMSamplesAndSceneTimingExact']
episode=next(x for x in preserved['episodes'] if x['slug']==slug)
if slug=='game-math-plane-distances-v2':
 selected={'PF01':[1,4],'PB01':[1,3,6],'PB02':[1,5],'PB03':[1,5],'PB04':[1,4,6],'PC09':[1,4],'PF02':[1,4], 'PG01':[1,2,3],'PG02':[1,2,3],'05':[1,2,3,4],'PG03':[1,2,3,4]}
 flow='A bounds candidate leaves a surface question; surface orientation motivates the normal; the same point motivates equation residual, distance and closest position. Three points then an ordered polygon boundary establish orientation. Reaching the infinite plane leaves finite-platform membership for episode2.'
 math='Same floor y=2, n=(0,1,0), p=(4,5,-3); scaling n and d preserves distance3; projection retains x,z and sets y=2. Coordinate change to XY z=0 is narrated. Cross product(0,0,24), parallelogram24, triangle12. Newell requires an ordered closed boundary, not unordered point-cloud fitting.'
else:
 selected=read(W/'performed-detail-review.json')['selectedPages']
 assert set(selected)=={r['scene'] for r in detail['records']}
 flow='Distance to the plane leaves finite-platform membership unresolved; area motivates three vertex weights; a given point motivates recovering its weights; projected overlap motivates a separate coplanarity check; the established address then retrieves a surface attribute.'
 math='Separate original4x3 area6 from narrated new6x4 area12. Weights(.2,.3,.5) give(1.8,2,0), partial areas2.4,3.6,6. Negative first weight(-.2,.7,.5) gives outside(4.2,2,0). Point(1.8,2,7) shares XY but has plane distance7. Defined linear RGB interpolation is not an engine-internal claim.'
reviewed=[]
for r in detail['records']:
 pages=[r['pages'][i-1] for i in selected[r['scene']]]
 assert all((ROOT/p).exists() for p in pages)
 r['directlyViewedPages']=pages;r['selectedMovingPixelReviewPassed']=True
 r['allGeneratedPagesViewed']=len(pages)==len(r['pages'])
 reviewed.append({'scene':r['scene'],'pages':pages,'allGeneratedPagesViewed':r['allGeneratedPagesViewed']})
now=datetime.datetime.now().astimezone().isoformat()
audit={'reviewedAt':now,'source':m['paths']['videoBurnedCaptions'],'sha256':digest,'fullDecode':True,'body40To60Exact':True,
 'allCaptionCueSheetsDirectlyViewed':len(t['koCaptions']),'allCompositionScenesDirectlyViewed':len(composition['records']),
 'movingDetailPagesDirectlyViewed':reviewed,'nativeWholePlayback':native,'originalSceneIdsRetained':[r['scene'] for r in episode['preservedPCM']],
 'originalSceneDictionariesAndOrderExact':True,'originalPCMSamplesExact':True,'causalFlow':flow,'mathReview':math,
 'annotationReview':'Compared actual native intervals before narration. Current red boundaries and distinct colored references directly reviewed during motion; rejected ramp/unstable tracks were replaced or suppressed. Illustrative coordinates and projected observations are labelled. Some preserved shots have explanatory notes without a reliable geometric track; no tracking or hidden engine values are claimed there.',
 'humanWholeListening':'pending','gameIPHumanRights':'pending','nativeMotionCanvasEditorPlayback':'unverified','uploadedCaptionProof':'pending'}
write(P/'production/current-pixel-review.json',audit)
qa.update(directVisualReview='Current hash: native whole1x playback, all cue/composition sheets, dense action annotations and selected narration-timed explanation transitions directly reviewed',currentPixelReview='production/current-pixel-review.json');write(P/'production/qa.json',qa)
m['status']='reviewed-local-render; private-upload-pending';m['membershipOutro']['appliedToFinal']=True
m['approvals'].update(script='All22 original dictionaries/130KO/130EN and order retained across two episodes; additive prerequisites and causal bridges reviewed',voice='Approved reference and exact original PCM retained; current ASR/alignment and numeric retakes checked; human whole listening pending',pixels='Current render, all captions, actual annotation motion and whole native playback reviewed')
m['finalRender']={'status':'complete-technical-and-direct-pixel-review','currentPixelApproval':True,'review':'production/current-pixel-review.json','knownIssues':[], 'openItems':['Human whole listening and game-IP review pending.','Private upload and platform verification pending.','Native Motion Canvas editor playback unverified.']}
m['publishReady']=False;m['editing']['exampleInterleaving']['reviewStatus']='Native source comparison, current moving annotations and causal interleaving reviewed';write(P/'project.json',m)
cuts=read(P/'production/footage-cuts.json')
for cut in cuts.get('cuts',[]):cut.update(currentMovingPixelApproval=True,reviewedFinalSha256=digest)
write(P/'production/footage-cuts.json',cuts)
for index,path in [(caption,W/'caption-review/index.json'),(composition,W/'composition-review/index.json')]:
 index.update(directReviewPassed=True,reviewedAt=now);write(path,index)
detail.update(selectedReviewRecordedAt=now,wholeNormalPlaybackVerified=True);write(W/'final-detail-review/index.json',detail)
print('Precisely recorded current local review:',slug,digest)
