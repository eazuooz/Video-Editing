"""Seal actual current-frame observations, preserving historical review records."""
from pathlib import Path
import importlib.util, copy
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=m.ROOT/'projects/game-lighting-history-04/production'
plan=m.read(P/'part3-final-input-plan-v145.json')
pair=m.read(P/'part3-reviewed-pair-build-v160.json')
pixels=m.read(P/'part3-final-pixel-review-execution-v161.json')
prior=m.read(P/'part3-final-board-direct-progress-v158.json')
request=m.read(P/'part3-final-moving-review-request-v160.json')
assert pixels['status']=='complete' and pixels['exitCode']==0
assert pixels['sourceSha256']==request['sourceSha256']==pair['captioned']['sha256']==m.sha(m.ROOT/pair['captioned']['path'])
assert len(pixels['images'])==2169 and len(pixels['boards'])==362
changed=[81,82,83,84,85,86,87,163,164,165,166]
assert [b['board'] for b in pixels['boards'] if not b['directlyRead']]==changed
assert sum(p['exactRgbIdentityToDirectlyReviewedSource'] for p in pixels['images'])==2113
assert prior['directlyReadBoards']==362 and all(r['directlyRead'] for r in prior['records'])
court='Directly read all six current encoded frames: the white Talk-arrival note is on the left background; Nellie Oggspire and the actual Talk prompt remain clear. Red coat brackets follow the announced garment and the later teal bracket identifies the actual Talk UI. Cues73–75 retain fixed white/forest boxes, complete text and at most two lines; cue/cut edges retain the previously inspected one-frame rasterization tolerance.'
grade='Directly read all six current encoded frames: red lowest-green-face bracket ends before the fast camera change and is absent through7.25–13 seconds. The white reacquisition note is present during the move; red returns on the correct lowest face after13 seconds. Teal Tonemapper brackets remain distinct. Cues150–151 are fully readable at fixed bottom center and explain observation position versus physical units.'
records=[]
for b in pixels['boards']:
    assert m.sha(m.ROOT/b['path'])==b['sha256']
    if b['directlyRead']:
        old=prior['records'][b['board']-1]
        assert old['sha256']==b['sha256']
        records.append(dict(b,method='All constituent current decoded RGB arrays exactly equal the previously directly read arrays.',priorObservation=old['actualObservation']))
    else:
        records.append(dict(b,directlyRead=True,method='view_image original six-frame board in current continuation',actualObservation=court if b['board']<100 else grade,reviewedAt=m.stamp()))
resolutions=[
 dict(issue='Historical cue-edge rounding assessment',resolution='Exact90000 timebase and all92038 presentation timestamps now verified. Previously directly inspected cue rasterization edges differ by at most one60fps frame from centisecond ASS events; no accumulated drift, missing clause or duplicate text. Current pixel identities preserve those reviewed edges.'),
 dict(issue='Secondary Model C selector behind cue26',resolution='The caption partially covers an unused secondary selector. The demonstrated strength/mask controls and face output remain visible; narration does not instruct selecting Model C. This is a scoped instructional-UI assessment, not a claim that every unused editor control is unobscured.'),
 dict(issue='Court white note over Nellie name',resolution='Repositioned only the external note to left background; current boards81–87 and full current normal-speed interval directly reviewed.'),
 dict(issue='Grade red bracket detached during fast camera move',resolution='Hide red7.25–13 seconds; reacquisition note and later lowest-face anchor directly reviewed in current boards163–166 and full current normal-speed interval.')]
pixelreview=dict(reviewedAt=m.stamp(),source=pixels['source'],sourceSha256=pixels['sourceSha256'],extraction=dict(path=m.rel(P/'part3-final-pixel-review-execution-v161.json'),sha256=m.sha(P/'part3-final-pixel-review-execution-v161.json')),
 records=records,uniqueEncodedFrames=2169,directNewBoards=11,inheritedExactRgbBoards=351,all362BoardsCovered=True,all330CuesAnd95InputsCovered=True,all85ParagraphOnsetsCovered=True,
 historicalIssueResolutions=resolutions,allFinalPixelsReviewed=True,humanWholeListening='pending',newGitImages=0)
m.save(P/'part3-final-pixel-review-direct-v162.json',pixelreview)
observations=[
 ('hogwarts-courtyard-ui',328.255777,'Whole approach played at rate1. Left white note stays separate from Nellie/Talk; red coat and teal actual Talk marks remain meaningful.'),
 ('grade-shared-reference',673.787600,'Whole camera/setting comparison played at rate1. Reacquisition note replaces red during the fast camera move; after13 seconds the bracket returns to the lowest green face.'),
 ('appearance-resident',149.603971,'Indoor face changes to rainy street/car. Original Off/On labels, wet garment and face are visible; final On frame144 seconds directly inspected. March2026 preview scope retained; distinct poses are not pixel-aligned ground truth.'),
 ('appearance-starfield',165.660,'Bright orange jacket/dialogue and space suits play at rate1; On space-suit frame158 seconds directly inspected. Dialogue UI is not described as a quality score.'),
 ('appearance-hogwarts',183.260721,'Interior/streets/underground sequence played at rate1; On street frame177 seconds directly inspected. Face/cloth changes are distinguished from wand/steam physics.'),
 ('appearance-nba',214.016444,'All three source intervals played at rate1. Same Detroit2 close-up Off191 seconds and On192 seconds directly inspected, then separate-angle dunk On193.5 seconds. Skin/uniform comparison does not assert ball physics or input-response changes; September2026 release scope retained.')]
movingrecords=[]
for key,end,note in observations:
 row=next(r for r in request['rows'] if r['id']==key)
 assert end>=row['ranges'][0][1]
 movingrecords.append(dict(id=key,rangeSeconds=row['ranges'][0],playbackRate=1,fullSelectedIntervalActuallyPlayed=True,observedPausedTimeSeconds=end,actualObservation=note,tool='CUA tab58 controls, actual screenshots and read-only video currentTime/paused/rate',sourceSha256=pair['captioned']['sha256']))
inputs=m.read(P/'part3-explanation-input-motion-direct-review-v157.json')
assert inputs['all40MeaningfulInputMotionReviewed']
native=m.read(P/'part3-annotated-visual-build-v159.json')
historical=m.read(P/'part3-seven-final-moving-observations-v159.json')
moving=dict(reviewedAt=m.stamp(),sourceSha256=pair['captioned']['sha256'],records=movingrecords,
 meaningfulExplanationInputs=dict(path=m.rel(P/'part3-explanation-input-motion-direct-review-v157.json'),sha256=m.sha(P/'part3-explanation-input-motion-direct-review-v157.json'),count=40),
 historicalFinalIntervals=dict(path=m.rel(P/'part3-seven-final-moving-observations-v159.json'),sha256=m.sha(P/'part3-seven-final-moving-observations-v159.json'),count=7,twoObservedIssuesRepairedAndRereviewed=True),
 method='40 meaningful explanation inputs, final spatial-motion samples in all explanation cuts, seven selected final moving intervals and six current full final intervals. Unchanged native inputs and current exact-RGB review corroborate inherited observations. This is not human whole-video listening.',allMovingPixelsReviewed=True,humanWholeListening='pending')
m.save(P/'part3-final-moving-review-direct-v162.json',moving)
games=dict(reviewed=True,currentCaptionedSha256=pair['captioned']['sha256'],fourTitles=['Resident Evil Requiem','Starfield','Hogwarts Legacy','NBA 2K27'],records=movingrecords[2:],method='Actual source comparison and current full normal-speed final intervals with readable fixed captions; within-shot Off/On labels distinguished from changes of scene/camera.',publicRightsApproved=False)
semantic=m.read(P/'part3-semantic-caption-review-v155.json');assert semantic['approved'] and len(semantic['paragraphs'])==85
audio=m.read(P/'part3-final-mixed-asr-direct-review-v147.json');assert audio['finalMixedAsrApproved'] and audio['allWholeAndIndependentTextsDirectlyCompared']
for key in ['clean','captioned']:
 assert pair[key]['wholeDecode']['exitCode']==0 and pair[key]['frames']==92038 and pair[key]['allPresentationPtsContinuous']
 assert m.sha(m.ROOT/pair[key]['path'])==pair[key]['sha256']
assert pair['identicalAacPayloadPtsDuration'] and abs(pair['ratioErrorFrames'])<=1
qa=dict(reviewedAt=m.stamp(),status='approved-current-technical-production-qa',slug=plan['slug'],planSha256=m.sha(P/'part3-final-input-plan-v145.json'),
 cleanSha256=pair['clean']['sha256'],captionedSha256=pair['captioned']['sha256'],reviewPair=dict(path=m.rel(P/'part3-reviewed-pair-build-v160.json'),sha256=m.sha(P/'part3-reviewed-pair-build-v160.json')),
 pixels=dict(path=m.rel(P/'part3-final-pixel-review-direct-v162.json'),sha256=m.sha(P/'part3-final-pixel-review-direct-v162.json')),
 motion=dict(path=m.rel(P/'part3-final-moving-review-direct-v162.json'),sha256=m.sha(P/'part3-final-moving-review-direct-v162.json')),
 mixedAudio=dict(path=m.rel(P/'part3-final-mixed-asr-direct-review-v147.json'),sha256=m.sha(P/'part3-final-mixed-asr-direct-review-v147.json')),
 semanticCaptions=dict(path=m.rel(P/'part3-semantic-caption-review-v155.json'),sha256=m.sha(P/'part3-semantic-caption-review-v155.json')),
 fourGameTeachingReview=games,finalFrames=92038,actualFrames=54791,explanationFrames=36527,bodyFrames=91318,ratioErrorFrames=pair['ratioErrorFrames'],
 loudness=pair['loudness'],identicalAacPayloadPtsDuration=True,twoWholeDecodesPassed=True,allPresentationPtsContinuous=True,
 allFinalPixelsReviewed=True,allMovingPixelsReviewed=True,captionTimingApproved=True,finalTimingApproved=True,bodyRatioApproved=True,qaApproved=True,
 originalIntroAnd10SecondMembershipPreserved=True,sourceAudio=0,loop=0,slowdown=0,newGitImages=0,collected=False,uploaded=False,
 humanWholeListening='pending',humanPronunciation='pending',publicRightsApproved=False,originalNimbusFileVerified=False,externalMediaBackup='pending')
m.save(P/'part3-final-qa-v162.json',qa)
cp=m.read(m.ROOT/'production/research/game-lighting-history/checkpoint.json');cp.update(updatedAt=m.stamp(),episode04Part3FinalQaV162=dict(path=m.rel(P/'part3-final-qa-v162.json'),qaApproved=True,collected=False,uploaded=False),ownedActiveWork=dict(status='no-active-owned-media-worker',next='Create reviewed physical delivery adapter, collect four files, save one private captioned upload and verify settings.'))
m.save(m.ROOT/'production/research/game-lighting-history/checkpoint.json',cp)
print(m.json.dumps(dict(qaApproved=True,currentCaptionedSha256=qa['captionedSha256'],newDirectBoards=11,exactRgbInheritedBoards=351,uploaded=False)))
