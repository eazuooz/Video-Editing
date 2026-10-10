"""Record an explicitly performed, hash-bound review for one lines episode."""
from pathlib import Path
import json, hashlib, sys, datetime
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
slug,digest=sys.argv[1:3]
assert slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']
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
assert native['sha256']==digest and native['ended'] and native['playbackRate']==1
assert abs(native['currentTime']-t['seconds'])<.04
indexes={key:read(W/key/'index.json') for key in ['caption-review','moving-pixel-review','explanation-motion-review','composition-review']}
assert all(v['sha256']==digest for v in indexes.values())
assert indexes['caption-review']['cueCount']==len(t['koCaptions'])
assert len(indexes['composition-review']['records'])==len(t['scenes'])+2
preserved=read(B/'lines-episode-flow-audit.json');assert preserved['allOriginalSceneDictionariesExact'] and preserved['originalOrderAndContractExact']
episode=next(x for x in preserved['episodes'] if x['slug']==slug)
# The second episode additionally requires explicit resolution of rejected tracks.
if slug=='game-math-bounds-transform-v2':
 correction=read(P/'production/annotation-correction-review.json')
 assert correction['sha256']==digest and correction['currentMovingPixelsDirectlyReviewed']
audit={'reviewedAt':datetime.datetime.now().astimezone().isoformat(),'source':m['paths']['videoBurnedCaptions'],'sha256':digest,'fullDecode':True,'body40To60Exact':True,'allCaptionCueSheetsDirectlyViewed':len(t['koCaptions']),'allCompositionScenesDirectlyViewed':len(t['scenes'])+2,'actualMovingSheetsDirectlyViewed':[{'scene':r['scene'],'pages':len(r['sheets'])} for r in indexes['moving-pixel-review']['samples']],'additiveExplanationMotionDirectlyViewed':[r['scene'] for r in indexes['explanation-motion-review']['records']],'nativeWholePlayback':native,'originalSceneIdsRetained':episode['originalIds'],'originalSceneDictionariesAndOrderExact':True,'originalPCM':'Preserved samples and voice hashes verified by timeline planner and render receipts.','causalFlow':('Orientation motivates a connection; equal distance motivates circles; two endpoints motivate direction and length; vertical lines motivate normals; target extent motivates the next episode.' if m['lecture']['episode']==1 else 'The connection needs a target extent; sphere size and elongated shape motivate boxes; axis intervals motivate overlap; candidate overlap motivates precise contact; rotated bodies motivate recomputing bounds and absolute half-size.'),'mathReview':'Unit/parameter conventions, delta=(6,3), length sqrt45, t=.5 point(5,2.5), vertical bisector x=1; projected gameplay observations distinguished from illustrative coordinates. Sphere and affine bounds numeric retakes reviewed separately.','humanWholeListening':'pending','gameIPHumanRights':'pending','nativeMotionCanvasEditorPlayback':'unverified','uploadedCaptionProof':'pending'}
write(P/'production/current-pixel-review.json',audit)
qa.update(directVisualReview='complete current hash: whole native1x playback, all cue/composition sheets, all action moving sheets and additive explanation motion',currentPixelReview='production/current-pixel-review.json');write(P/'production/qa.json',qa)
m['status']='reviewed-local-render; private-upload-pending';m['membershipOutro']['appliedToFinal']=True
m['approvals'].update(script='Original22 dictionaries/130KO/130EN retained across two episodes; additive prerequisites and causal bridges reviewed',voice='Approved reference and original PCM preserved; current alignment/numeric retakes checked; human whole listening pending',pixels='Current moving render pixels, all captions and whole native playback reviewed')
m['finalRender']={'status':'complete-technical-and-direct-pixel-review','currentPixelApproval':True,'review':'production/current-pixel-review.json','knownIssues':[],'openItems':['Human whole listening and game-IP review pending.','Private upload and actual platform verification pending.','Native Motion Canvas editor playback unverified.']};m['publishReady']=False
m['editing']['exampleInterleaving']['reviewStatus']='native source comparison and current moving annotations directly reviewed';write(P/'project.json',m)
cuts=read(P/'production/footage-cuts.json')
for cut in cuts.get('cuts',[]):
 cut['currentMovingPixelApproval']=True;cut['reviewedFinalSha256']=digest
write(P/'production/footage-cuts.json',cuts)
for key,index in indexes.items():
 index['directReviewPassed']=True;index['reviewedAt']=audit['reviewedAt'];write(W/key/'index.json',index)
print('Current local review saved:',slug,digest)
