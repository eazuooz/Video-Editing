"""Record the current ordered final, with explicit limits on historical motion evidence."""
from pathlib import Path
from datetime import datetime
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
slug='game-math-polygon-partition-v2';P=ROOT/'projects'/slug;W=ROOT/'shared/output'/slug
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now().astimezone().isoformat();m=read(P/'project.json');t=read(P/'production/timeline.json');qa=read(P/'production/qa.json')
digest=sha(ROOT/m['paths']['videoBurnedCaptions']);clean=sha(ROOT/m['paths']['videoClean'])
assert digest=='e1f0e28db23fc5a1f8734d2be181a453186da9157e5990a35cd8236018585b73'
assert clean=='28470054a01e4dbc5b9816aee6d9bd03b8b635d71fd8c2e8247e292eff03959f'
assert qa['fullDecodePassed'] and qa['ratioErrorFrames']==0 and qa['koEnMatchingTimes']
assert qa['videos']['videoBurnedCaptions']['sha256']==digest and qa['videos']['videoClean']['sha256']==clean
native=read(W/'native-final-playback.json');v=native['media'][0]
assert v['ended'] and v['playbackRate']==1 and not v['error'] and abs(v['duration']-t['seconds'])<.03 and digest in native['text']
pres=read(B/'polygons-preservation-audit.json')
assert pres['allOriginalSceneDictionariesExact'] and pres['originalOrderAndContractExact'] and pres['allOriginalPCMSamplesAndSceneTimingExact']
repair=read(R/'factory-bridge-order-repair-v4.json')
assert repair['unchangedSceneDictionaries'] and repair['unchangedScenePcmSamples'] and repair['unchangedClipsAndLocalAnnotationTiming']
raw=read(W/'mixed-asr-v4/all-scenes.json');assert raw['complete'] and raw['sha256']==clean and raw['timelineSha256']==sha(P/'production/timeline.json')
assert [s['scene'] for s in raw['scenes']]==[s['id'] for s in t['scenes']] and len(raw['scenes'])==24
for s in raw['scenes']:assert not s['expectedTextUsedAsPrompt'];s['directlyCompared']=True
write(W/'mixed-asr-v4/all-scenes.json',raw)
focus=read(R/'polygons-v4-asr-overlap-windows.json');f=[x for x in focus['rows'] if x['slug']==slug]
assert len(f)==1 and f[0]['sourceSha256']==clean and not f[0]['expectedTextUsedAsPrompt']
audio={'reviewedAt':now,'source':m['paths']['videoClean'],'sha256':clean,'captionedSha256':digest,'timelineSha256':raw['timelineSha256'],
 'rawEvidence':f'shared/output/{slug}/mixed-asr-v4/all-scenes.json','completeScenesDirectlyRead':[s['scene'] for s in raw['scenes']],
 'mathematicalMeaningReviewPassed':True,'method':'All24 complete expected-versus-unprompted AAC recognition texts directly compared; scene19 single window separately compared. Recognition evidence does not constitute human listening.',
 'checks':['Convex six-vertex fan has four triangles; count alone does not prove coverage.','L shape anchored at(4,1) can cover a notch while signed areas sum7; origin anchor is valid only for this particular L shape.','Valid ear requires convex candidate, internal diagonal and no forbidden remaining point; first(0,0),(4,0),(4,1) ear has area2.','Remaining ear areas1.5,1.5,2 give total7; boundary connectivity differs from original vertex IDs.','Shapez2 transport route is not a polygon boundary; factory goal pieces differ from retaining all original polygon area.','Tiny Glade lake/door, Noita open passage and Dorfromantik combined land compare retained empty space; no engine implementation inferred.','Doubling lengths quadruples areas; length and area tolerances differ; validity precedes quality.','Final G(4/3,1),I(1,1),O(2,1.5),r1,R2.5 and four areas retained.'],
 'recognitionNotes':[{'scene':'19','note':'Chunked recognition repeats an ending and backtracks. The unprompted25s focused window contains the ending once with monotonic word timestamps; raw duplicate preserved.'},{'scene':'QB06','note':'Recognition 한만으로 for 합만으로 preserved; pronunciation/human listening pending.'},{'scene':'QB12,QB13,17,18,21,22','note':'Game-name/consonant and 네/내, 세/새, 엘/일 substitutions preserved in raw. No claim that ASR resolved pronunciation; mathematical numbers compared in context.'}],
 'focusedRawEvidence':'production/batches/game-math-part2-teaching-revision/cross-game-review-20261011/polygons-v4-asr-overlap-windows.json','humanWholeListening':'pending','automaticAudioApproval':False,'rightsApproval':False}
write(R/(slug+'-mixed-audio-review-v4-current-order.json'),audio)
caption=read(W/'caption-review/index.json');comp=read(W/'composition-review/index.json');detail=read(W/'final-detail-review/index-selected-QB12-QB14-QG06.json')
assert caption['sha256']==comp['sha256']==digest and caption['cueCount']==140 and len(comp['records'])==26
assert all(r['sourceSha256']==digest and r['directReviewPassed'] for r in detail['records'])
historical={'captionedSha256':repair['oldCaptionedSha256'],'preservationEvidence':str((R/'factory-bridge-order-repair-v4.json').relative_to(ROOT)).replace('\\','/'),'reason':'Unchanged scene-local clips, captions and narration retained; global sequence moved. These earlier pages are not represented as current final-file pages.',
 'boundedFinalPagesPreviouslyViewed':{'QG04':[1,3,6],'QG06':[1,2,3,4],'QG09':[1,2,3,4,5,6,7],'QB12':[1,2,3],'QB13':[1,2,3,4,5],'QB14':[1,2,3],'14':[3],'17':[4],'19':[4],'21':[2],'QG05':[3],'QG07':[1,4],'QF03':[2],'QB06':[2]}}
pixel={'reviewedAt':now,'source':m['paths']['videoBurnedCaptions'],'sha256':digest,'fullDecode':True,'body40To60Exact':True,'allCaptionCueSheetsDirectlyViewed':140,'allCompositionScenesDirectlyViewed':26,
 'currentMovingDetailPagesDirectlyViewed':detail['records'],'historicalSceneLocalMotionEvidence':historical,'nativeWholePlayback':native,'originalSceneDictionariesOrderAndPcmExact':True,
 'causalFlow':'Boundary and convexity motivate a failing fan, ear clipping and retention checks. QB12 introduces factory input/output; unchanged QB14 now immediately precedes actual QG06. Factory pieces are contrasted with complete-region partitioning before land placement/undo and validity/quality.',
 'annotationReview':'Current QG06 all4 final pages show red observed cut lines tracking circle/square, hiding at source cuts; current all140 captions and26 compositions checked. Prior dense QG09 placement/undo and QG04 lake/cave reviews retained with unchanged local timing. No world measurements or engine-internal claims.',
 'mathAudioReview':str((R/(slug+'-mixed-audio-review-v4-current-order.json')).relative_to(ROOT)).replace('\\','/'),'humanWholeListening':'pending','gameIPHumanRights':'pending','nativeMotionCanvasEditorPlayback':'unverified','uploadedCaptionProof':'pending'}
write(P/'production/current-pixel-review.json',pixel)
qa.update(directVisualReview='Current hash: all140 cue strips, all26 compositions, current10 bridge motion pages and whole native1x playback; historical unchanged scene-local motion explicitly bounded; human listening pending',currentPixelReview='production/current-pixel-review.json');write(P/'production/qa.json',qa)
m['status']='reviewed-local-render; private-upload-pending';m['membershipOutro']['appliedToFinal']=True
m['audio']['mixStatus']='measured-narration-only-current-AAC';m['editing']['causalFlow']['continuousReview']='Current complete-script read, ordered bridge pixels and native1x playback; human listening pending'
m['approvals'].update(script='Original22 dictionaries/order and128KO/EN lines preserved across both episodes; current additive comparisons reviewed',voice='Original PCM preserved; all24 current AAC recognitions and targeted19 window directly compared; human listening pending',pixels='Current captions/compositions,10 ordered bridge detail pages and preserved bounded local motion reviewed')
m['finalRender']={'status':'complete-technical-and-direct-pixel-review','currentPixelApproval':True,'review':'production/current-pixel-review.json','knownIssues':[],'openItems':['Human whole listening and game-IP review pending.','Private upload and actual publishing settings pending.']};m['publishReady']=False;write(P/'project.json',m)
coverage=read(P/'planning/game-example-coverage.json');assert coverage['actualDistinctGames']==4
coverage.update(currentWholeCoverageApproved=True,wholeMixedAudioReview=pixel['mathAudioReview'],finalContinuousPixelReview='production/current-pixel-review.json',reviewedCaptionedSha256=digest)
for g in coverage['games']:g.update(finalMovingPixelsReviewed=True,captionAndUiClearanceReviewed=True,mixedAudioReviewed=True,humanListeningComplete=False,humanRightsReviewComplete=False)
write(P/'planning/game-example-coverage.json',coverage)
for index,path in [(caption,W/'caption-review/index.json'),(comp,W/'composition-review/index.json')]:index.update(directReviewPassed=True,reviewedAt=now);write(path,index)
for episode in ['game-math-polygon-centers-v2',slug]:
 EP=ROOT/'projects'/episode;et=read(EP/'production/timeline.json');slots={s['id']:s for s in et['scenes']};p=EP/'production/footage-cuts.json';d=read(p)
 for s in d['scenes']:
  s['start']=slots[s['id']]['start']
  if 'annotationPlan' in s['cut']:s['cut']['annotationPlan']['movingPixelApproval']=True
 d.update(timelineSha256=sha(EP/'production/timeline.json'),currentPixelReview='production/current-pixel-review.json',status='current-timing and explicitly-bounded moving-pixel review recorded');write(p,d)
flow=read(B/'polygons-episode-flow-audit.json')
for e in flow['episodes']:e['finalContinuousReview']=True;e['currentReview']='projects/'+e['slug']+'/production/current-pixel-review.json';e['humanListeningComplete']=False
write(B/'polygons-episode-flow-audit.json',flow)
print('Recorded exact current partition review and four-game coverage; human/rights approval remain pending.')
