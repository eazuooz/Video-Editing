from common import *
P=R/'projects/game-math-lines-circles-v2';H=P/'production/concept-fit-v2'
d=read(H/'changed-scene-asr-review.json');assert d['complete'] and len(d['scenes'])==6
for s in d['scenes']:
 s['directTextReview']='Full expected and recognized scene texts compared; not a listening approval.'
 if s['scene']=='02':s['focusedRecheck']=dict(evidence=rel(B/'focused-audio-screen-m09-02.json'),start=16.78,end=37.3,result='Unchunked20.52s recognition contains all three final paragraphs. Whole-scene chunk skip not reproduced. Subtitle timing uses this focused evidence.',actualListening=False)
d.update(textComparisonReviewedAt=now(),actualAudioReviewed=False,pendingListening=['Original 읽지는/익지는 in02','Original 궤적/개적 and 식의/시계 in05','changed paragraph joins and original game audio balance'])
save(H/'changed-scene-asr-review.json',d)
save(H/'caption-clause-review.json',dict(reviewedAt=now(),pairedCues=146,focusedAlignment='02 final three paragraphs use isolated sentence timestamps, replacing the whole-scene ASR skip; unchanged narration preserved.',encodedPixelQa='pending',actualListening=False))
print('M09 ASR text comparison complete; actual hearing pending')
