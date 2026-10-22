from common import *
H=R/'projects/game-math-euler-axis-angle/production/concept-fit-v2'
p=H/'changed-scene-asr-review.json';d=read(p)
notes={
'01':'All claims and order retained. ASR 세/새 is homophonic; 보간/보관 needs targeted listening.',
'02':'All claims retained. ASR inserts 해 in 함께 보세요; targeted listening pending.',
'05':'All claims retained. ASR 함께해/함께 and 의/에; targeted listening pending.',
'08':'All claims retained. ASR 의/에 and 세/3 orthographic variants; listening pending.',
'11':'Normalized text exact; no omissions or repetition observed in ASR text.',
'14':'All claims retained. 삼/3 formatting; 보간/보관 needs targeted listening.',
'17':'Normalized text exact; no omissions or repetition observed in ASR text.',
'20':'All claims retained. ASR 바뀌므로/바뀜으로 spelling variation; listening pending.',
'23':'Normalized text exact; no omissions or repetition observed in ASR text.'}
for r in d['scenes']:
 r.update(directTextReview='reviewed',textReviewAt=now(),textReviewNote=notes[r['scene']],listening='pending')
d.update(actualAudioReviewed=False,reviewMethod='Read expected and independently recognized full text for all9 changed scenes; ASR review is not listening.')
save(p,d)
H3=R/'projects/game-math-orientation-matrices/production/concept-fit-v2'
save(H3/'native-playback-round2.json',dict(observedAt=now(),captionedSha256='3e8cd9ca933487102743ea67c44e276a634ce3404f82d32a492796312fecc4c9',browserTab='45',url='http://127.0.0.1:9248/output/game-math-orientation-matrices-concept-fit-v2/internal-review.html',visibleProof=[dict(start=0,end=768.666667,rate=1,ended=True)],scope='Browser native playback completed; intermittent screenshots and full extracted-frame audit, not continuous human observation or listening.',actualListening=False))
