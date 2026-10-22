from common import *
P=R/'projects/game-math-rotation-conversions-v2';H=P/'production/concept-fit-v2'
d=read(H/'changed-scene-asr-review.json');assert d['complete'] and len(d['scenes'])==10
focused=read(B/'focused-audio-screen-m08-m09.json')['results'][0]
for s in d['scenes']:
 s['directTextReview']='Expected and recognized complete scene texts read and compared; not an actual-listening signoff.'
 if s['scene']=='20':s['focusedRecheck']=dict(evidence=rel(B/'focused-audio-screen-m08-m09.json'),start=15.02,end=29.36,result='Independent unchunked14.34s recognition contains the expected two paragraphs once. Chunked whole-scene duplicate is not reproduced; no TTS changed.',actualListening=False)
d.update(textComparisonReviewedAt=now(),actualAudioReviewed=False,pendingListening=['비시즈/BCG in17','original 새/세 in17','original 화면의 선은 inIG03','original 그 and 보간/보관 inIG11','original 행렬/쿼터니언 inIG05','original 변환은 in23','changed paragraph joins and game balance'])
save(H/'changed-scene-asr-review.json',d)
save(H/'caption-clause-review.json',dict(reviewedAt=now(),corrections=['Split20.L02 and23.L03 into two paired KO/EN sentence cues; no narration/timing change.'],sourceCaptionsPreserved=True,actualPixelQa='pending'))
print('M08 text comparison reviewed; isolated recheck resolves ASR duplicate; hearing remains pending')
