from common import *
P=R/'projects/game-math-bounds-transform-v2';H=P/'production/concept-fit-v2'
d=read(H/'changed-scene-asr-review.json');assert d['complete'] and len(d['scenes'])==9
for s in d['scenes']:s['directTextReview']='Full expected and recognized scene texts compared. No missing full paragraph or duplicate sentence observed; this is not listening approval.'
d.update(textComparisonReviewedAt=now(),actualAudioReviewed=False,pendingListening=['10 피해/피의','13 거를/걸을, 구를/굴을, 축에/축의','16 반례/발레','19 아핀 and 물체의','LG07 꼭짓점/꼭지점','21 의/에 and joins','changed paragraph joins and original game sound balance'])
save(H/'changed-scene-asr-review.json',d)
save(H/'caption-clause-review.json',dict(reviewedAt=now(),pairedCues=211,manualEnglishClauseSplits=['LG04 line2','16 line6','21 line6'],reason='Align English sentence count to the unchanged Korean clause timing without changing narration.',encodedPixelQa='pending',actualListening=False))
save(H/'preflight-review.json',dict(reviewedAt=now(),frames=18,sheets=2,directReview='All18 frames on both preflight sheets directly inspected: head and limbs, roof bounds, separated beams, rotation/camera distinction and building height. Labels visible; exact gameplay tracking still needs final encoded inspection.',renderer='Manim mathematical mesh model; preserved original mathematical scenes reused',actualListening=False))
print('M10 text and18 preflight frames reviewed; encoded QA and hearing pending')
