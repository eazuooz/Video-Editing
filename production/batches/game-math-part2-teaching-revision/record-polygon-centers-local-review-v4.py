"""Record performed whole-caption/composition and bounded moving-pixel review."""
from pathlib import Path
from datetime import datetime
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
slug='game-math-polygon-centers-v2';P=ROOT/'projects'/slug;W=ROOT/'shared/output'/slug
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now().astimezone().isoformat();m=read(P/'project.json');t=read(P/'production/timeline.json');qa=read(P/'production/qa.json')
digest=sha(ROOT/m['paths']['videoBurnedCaptions']);clean=sha(ROOT/m['paths']['videoClean'])
assert digest=='9ba0365ec5eabe2c4b98ace5b3bc2a08f2126bc92173744023c87afd662994ff'
assert qa['fullDecodePassed'] and qa['ratioErrorFrames']==0 and qa['koEnMatchingTimes']
assert qa['videos']['videoBurnedCaptions']['sha256']==digest and qa['videos']['videoClean']['sha256']==clean
native=read(W/'native-final-playback.json');v=native['media'][0]
assert v['ended'] and v['playbackRate']==1 and not v['error'] and abs(v['duration']-t['seconds'])<.03 and digest in native['text']
pres=read(B/'polygons-preservation-audit.json')
assert pres['allOriginalSceneDictionariesExact'] and pres['originalOrderAndContractExact'] and pres['allOriginalPCMSamplesAndSceneTimingExact']
raw=read(W/'mixed-asr-v4/all-scenes.json');assert raw['complete'] and raw['sha256']==clean and raw['timelineSha256']==sha(P/'production/timeline.json')
assert [s['scene'] for s in raw['scenes']]==[s['id'] for s in t['scenes']] and len(raw['scenes'])==25
focus=read(R/'polygons-v4-asr-overlap-windows.json');f=[x for x in focus['rows'] if x['slug']==slug]
assert len(f)==2 and all(x['sourceSha256']==clean and not x['expectedTextUsedAsPrompt'] for x in f)
audio={'reviewedAt':now,'source':m['paths']['videoClean'],'sha256':clean,'captionedSha256':digest,'timelineSha256':raw['timelineSha256'],
 'rawEvidence':f'shared/output/{slug}/mixed-asr-v4/all-scenes.json','completeScenesDirectlyRead':[s['scene'] for s in raw['scenes']],
 'mathematicalMeaningReviewPassed':True,'method':'Complete direct expected-versus-unprompted recognition text comparison; targeted single windows resolve chunk-overlap uncertainty without expected-text prompting.',
 'checks':['G(4/3,1), uniform triangular lamina and median2/3 conditions retained.','I(1,1), opposite-side weights5,3,4, perimeter12, r=2A/P=1 retained.','O(2,1.5), radius2.5 and obtuse-triangle outside case(2,-1) retained.','Simple ordered planar boundary, holes and self-intersection conditions precede convexity testing.','Six-vertex angle sum720 does not distinguish concavity; 2D turn -9 and acos clamp[-1,1] retained.','All four games distinguish a reference point from a complete boundary; no engine implementation inferred.'],
 'recognitionNotes':[{'scene':'11','note':'Chunked timestamps backtracked and duplicated an ending. Unprompted single19s window contains the ending once, with monotonic word times. ASR 한만으로 for 합만으로 remains a pronunciation/listening uncertainty.'},{'scene':'12','note':'Whole ASR 역호사인 for 역코사인 preserved. The focused9s window begins mid-word and checks only zero-edge/clamp/concave-angle ending, not the full inverse-cosine pronunciation.'},{'scene':'05','note':'Recognition replacement character in a word is retained in raw evidence; no numeric/math conclusion inferred from that character.'}],
 'focusedRawEvidence':'production/batches/game-math-part2-teaching-revision/cross-game-review-20261011/polygons-v4-asr-overlap-windows.json','humanWholeListening':'pending','automaticAudioApproval':False,'rightsApproval':False}
write(R/(slug+'-mixed-audio-review-v4.json'),audio)
caption=read(W/'caption-review/index.json');comp=read(W/'composition-review/index.json');detail=read(W/'final-detail-review/index.json')
assert caption['sha256']==comp['sha256']==digest and caption['cueCount']==165 and len(comp['records'])==27
selected={'QF01':[3],'QF04':[1,2,3],'QB11':[1,2,3,4,5],'QG08':list(range(1,10)),
 'QG01':[1,4,8],'QG02':[1,3,5],'QG03':[1,4,8],'02':[1,3,6],'05':[1,3,6],'08':[1,4,7],'11':[1,3,6],
 'QB01':[2],'QB02':[2],'QB03':[2],'QB04':[2],'QB05':[2],'QF02':[2]}
performed=[]
for ident,nums in selected.items():
 row=next(x for x in detail['records'] if x['scene']==ident);assert row['sourceSha256']==digest
 pages=[row['pages'][i-1] for i in nums];assert all((ROOT/x).exists() for x in pages)
 row.update(directlyViewedPages=pages,selectedMovingPixelReviewPassed=True,allGeneratedPagesViewed=len(pages)==len(row['pages']))
 performed.append({'scene':ident,'pages':pages,'allGeneratedPagesViewed':row['allGeneratedPagesViewed']})
pixel={'reviewedAt':now,'source':m['paths']['videoBurnedCaptions'],'sha256':digest,'fullDecode':True,'body40To60Exact':True,
 'allCaptionCueSheetsDirectlyViewed':165,'allCompositionScenesDirectlyViewed':27,'movingDetailPagesDirectlyViewed':performed,'nativeWholePlayback':native,
 'originalSceneDictionariesOrderAndPcmExact':True,'causalFlow':'Placement/target references motivate purpose-specific G/I/O; terrain/combined land motivate full ordered boundary and a separate convexity check. QF04 explicitly separates this episode from the later partition lesson.',
 'annotationReview':'Final QG08 all9 pages reviewed including first red ledge8.5–13.5 and second19.98–24, hidden before camera cut. Retained QG01/QG03 full clip motion reviews plus current final bounded pages; original02/05/08/11 checked at listed pages. Only projected visible geometry claimed.',
 'mathAudioReview':str((R/(slug+'-mixed-audio-review-v4.json')).relative_to(ROOT)).replace('\\','/'),
 'humanWholeListening':'pending','gameIPHumanRights':'pending','nativeMotionCanvasEditorPlayback':'unverified','uploadedCaptionProof':'pending'}
write(P/'production/current-pixel-review.json',pixel)
qa.update(directVisualReview='Current hash: all165 cue strips, all27 compositions, bounded motion pages explicitly listed, whole native1x playback; human listening pending',currentPixelReview='production/current-pixel-review.json');write(P/'production/qa.json',qa)
m['status']='reviewed-local-render; private-upload-pending';m['membershipOutro']['appliedToFinal']=True
m['audio']['mixStatus']='measured-narration-only-current-AAC';m['editing']['causalFlow']['continuousReview']='Current complete-script read, bounded pixels and native1x playback; human listening pending'
m['approvals'].update(script='Original22 dictionaries/order and128KO/EN lines preserved across both episodes; current additive comparisons reviewed',voice='Original PCM preserved; final AAC full scene recognition and targeted windows directly compared; human listening pending',pixels='Current captions/compositions and specified moving pages reviewed')
m['finalRender']={'status':'complete-technical-and-direct-pixel-review','currentPixelApproval':True,'review':'production/current-pixel-review.json','knownIssues':[],'openItems':['Human whole listening and game-IP review pending.','Private upload and actual publishing settings pending.']};m['publishReady']=False;write(P/'project.json',m)
coverage=read(P/'planning/game-example-coverage.json');assert coverage['actualDistinctGames']==4
coverage.update(currentWholeCoverageApproved=True,wholeMixedAudioReview=pixel['mathAudioReview'],finalContinuousPixelReview='production/current-pixel-review.json',reviewedCaptionedSha256=digest)
for g in coverage['games']:g.update(finalMovingPixelsReviewed=True,captionAndUiClearanceReviewed=True,mixedAudioReviewed=True,humanListeningComplete=False,humanRightsReviewComplete=False)
write(P/'planning/game-example-coverage.json',coverage)
for index,path in [(caption,W/'caption-review/index.json'),(comp,W/'composition-review/index.json')]:index.update(directReviewPassed=True,reviewedAt=now);write(path,index)
detail.update(selectedReviewRecordedAt=now,wholeNormalPlaybackVerified=True);write(W/'final-detail-review/index.json',detail)
print('Recorded exact current centers review; four-game coverage approved; human/rights reviews pending.')
