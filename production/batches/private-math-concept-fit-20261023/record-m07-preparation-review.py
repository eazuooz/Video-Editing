from common import *
P=R/'projects/game-math-interpolation-paths-v2';H=P/'production/concept-fit-v2'
d=read(H/'changed-scene-asr-review.json');assert d['complete'] and len(d['scenes'])==12
notes={'01':'Initial 두 missing in recognition; 보간→보관. Original first paragraph retained; listening required, not an inferred deletion.',
'02':'호를→홀을 and 보간→보관 require direct contextual listening.',
'IB03':'의/에 and spoken 네 recognized as4; no extra clause.',
'IG01':'T and45 are numeric/letter normalization.',
'05':'잇는/있는, 보간/보관 and 의/에; listening required.',
'IG10':'Four-component sum-of-squares definition retained;4/1 numeric normalization.',
'08':'t,90,0.25,0.5 normalization; all complete clauses present.',
'IB09':'Z and90 normalization.',
'IG02':'All clauses match ignoring punctuation/spacing.',
'11':'멈추어/멈춰 contraction and 의/에; listening still pending.',
'IG07':'끝 omitted in recognition of retained paragraph; inspect actual speech before deciding on a correction.',
'14':'지금 omitted in recognition; 보간/보관 and 꼭짓점/꼭지점 require listening.'}
for x in d['scenes']:
 x['directTextReview']='expected and full recognized text compared by agent'
 x['reviewNotes']=notes[x['scene']];x['listening']='pending'
d.update(textReviewedAt=now(),actualAudioReviewed=False,automaticSpeechPass=False)
save(H/'changed-scene-asr-review.json',d)
save(H/'caption-clause-review.json',dict(at=now(),pairedCueCount=204,splitClauses=['IB03.L01','14.L06'],fontSizePreserved=True,
 englishChange='14.L06 subtitle word order follows the Korean clause order; the full meaning is retained. Frozen TTS inputs are unchanged.',actualEncodedReview='pending'))
s=read(H/'source-evidence.json');s['sourceSpeechCheck']='Automated blind screen produced an uncertain short English phrase. No direct hearing confirmation; source audio review remains pending. Original mix is not labeled isolated effects.'
s['sourceAudioScreen']='shared/output/private-math-concept-fit-20261023/sources/escape-simulator-official/doors-audio-screen.json';save(H/'source-evidence.json',s)
H5=R/'projects/game-math-quaternion-foundations-v3/production/concept-fit-v2';p=read(H5/'preflight-review.json')
p.update(allChangedSampleFramesReviewed=True,allChangedSampleFrames=48,contactSheetsReviewed=6,b06CorrectionReviewed=True,
 review='Two actual rendered frames per24 changed visual scenes directly inspected. Object/axis bounds fit the selected single-model enlargement region. Final enlarged composites and captions still require review.',reviewedAt=now())
save(H5/'preflight-review.json',p)
paths=[]
folders=[B]
for slug in ['game-math-quaternion-foundations-v3','game-math-quaternion-calculations-v3','game-math-interpolation-paths-v2']:
 p=R/'projects'/slug;folders.extend([p/'production/concept-fit-v2',p/'script/concept-fit-v2',p/'publishing/revisions/concept-fit-v2'])
for f in folders:
 if f.exists():paths.extend(rel(x) for x in f.rglob('*') if x.is_file() and x.suffix in ['.py','.json','.md','.txt','.srt'] and '__pycache__' not in x.parts and not x.name.endswith('-commit.json'))
shared=['shared/publishing/video-worklist.json','docs/GAME_MATH_PRIVATE_POLISH.md'];paths+=shared
save(B/'m07-preparation-commit.json',dict(paths=sorted(set(paths)),sharedPaths=shared,message='Prepare hinge interpolation revision and record source-action and caption checks'))
print('M07 text review and M05 sampled preflight recorded; actual hearing still pending')
