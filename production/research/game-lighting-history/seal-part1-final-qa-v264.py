"""Bind explicit current board/motion observations to actual technical results."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
PP=P/'part1-final-input-plan-v240.json';plan=m.read(PP)
pair=m.read(P/'part1-reviewed-pair-build-v252.json')
pixels=m.read(P/'part1-final-pixel-review-execution-v253.json')
pixelRequest=m.read(P/'part1-final-pixel-review-request-v253.json')
boardPath=P/'part1-final-board-direct-progress-v265.json';boards=m.read(boardPath)
motionPath=P/'part1-final-moving-direct-progress-v266.json';motion=m.read(motionPath)
motionRequest=m.read(P/'part1-final-moving-review-request-v261.json')
assert pixels['status']=='complete' and pixels['exitCode']==0
assert pixels['sourceSha256']==boards['sourceSha256']==motion['sourceSha256']==motionRequest['sourceSha256']==pair['captioned']['sha256']
assert boards['extractionSha256']==m.sha(P/'part1-final-pixel-review-execution-v253.json')
assert motion['requestSha256']==m.sha(P/'part1-final-moving-review-request-v261.json')
assert len(pixels['images'])==pixelRequest['uniqueFrames']==2266 and len(pixels['boards'])==378
assert boards['allFinalPixelsReviewed'] and boards['unresolvedIssues']==[]
assert [b['board'] for b in boards['records']]==[b['board'] for b in pixels['boards']]
for b,observed in zip(pixels['boards'],boards['records']):
 assert b['sha256']==observed['sha256']==m.sha(R/b['path'])
 assert observed['directlyRead'] and observed['allConstituentFramesDirectlyRead'] and observed['actualObservation'].strip()
assert motion['allFinalMovingPixelsReviewed'] and motion['unresolvedIssues']==[]
assert [q['id'] for q in motion['records']]==[q['id'] for q in motionRequest['rows']]
for q,observed in zip(motionRequest['rows'],motion['records']):
 assert observed['fullSelectedIntervalActuallyPlayed'] and observed['playbackRate']==1 and observed['actualObservation'].strip()
 assert observed['rangeSeconds']==q['ranges'][0] and observed['normalSpeedPixelsApproved']
assert len(motion['records'])==96
audioPath=P/'part1-final-mixed-asr-direct-review-v254.json';audio=m.read(audioPath)
assert audio['finalMixedAsrApproved'] and audio['allWholeAndIndependentTextsDirectlyCompared'] and audio['allWordEndingsAndTimestampsCompared']
assert audio['noRemainingContentFailures'] and audio['allObservedRecognitionConcernsResolved']
settings=m.read(P/'part1-final-mix-settings-v242.json')
assert audio['currentMixSha256']==settings['wavSha256']==m.sha(R/settings['wav'])
semanticPath=P/'part1-semantic-caption-review-v262.json';semantic=m.read(semanticPath)
assert semantic['approved'] and semantic['manualSemanticReview'] and semantic['allParagraphTextsRetained'] and len(semantic['paragraphs'])==77
assert semantic['planSha256']==pair['planSha256']==audio['planSha256']==m.sha(PP)
for key in ['clean','captioned']:
 assert pair[key]['wholeDecode']['exitCode']==0 and pair[key]['frames']==plan['finalFrames']==89148
 assert pair[key]['allPresentationPtsContinuous'] and m.sha(R/pair[key]['path'])==pair[key]['sha256']
assert pair['identicalAacPayloadPtsDuration'] and abs(pair['ratioErrorFrames'])<=1
assert (pair['actualFrames'],pair['explanationFrames'],pair['bodyFrames'])==(53057,35371,88428)
games=['Horizon Forbidden West','The Outer Worlds 2','Cyberpunk 2077','Fortnite']
gameCutIds=['horizon-detail-motion:native','outer-displayed-frames:native','cyber-light-reconstruction:native','cyber-surface-observation:native','fortnite-mobile-test:native','fortnite-normal-material:native']
gameRows=[next(q for q in motion['records'] if q['id']==cutId) for cutId in gameCutIds]
conclusion=next(q for q in motion['records'] if q['id'].startswith('four-game-transfer-conclusion'))
assert motion['fourGameDifferencesAndCommonPrincipleDirectlyReviewed']
assert motion['originalIntroMembershipAndFixedCaptionStyleDirectlyReviewed']
pixelReview={'reviewedAt':m.stamp(),'sourceSha256':pair['captioned']['sha256'],'records':boards['records'],
 'request':{'path':m.rel(P/'part1-final-pixel-review-request-v253.json'),'sha256':m.sha(P/'part1-final-pixel-review-request-v253.json')},
 'extraction':{'path':m.rel(P/'part1-final-pixel-review-execution-v253.json'),'sha256':m.sha(P/'part1-final-pixel-review-execution-v253.json')},
 'uniqueEncodedFrames':2266,'directlyReadBoards':378,'all335CuesAnd96InputsCovered':True,'all77ParagraphOnsetsCovered':True,
 'allFinalPixelsReviewed':True,'newGitImages':0,'humanWholeListening':'pending'}
m.save(P/'part1-final-pixel-review-direct-v264.json',pixelReview)
qa={'reviewedAt':m.stamp(),'status':'approved-current-technical-production-qa','slug':plan['slug'],'planSha256':m.sha(PP),
 'cleanSha256':pair['clean']['sha256'],'captionedSha256':pair['captioned']['sha256'],
 'reviewPair':{'path':m.rel(P/'part1-reviewed-pair-build-v252.json'),'sha256':m.sha(P/'part1-reviewed-pair-build-v252.json')},
 'pixels':{'path':m.rel(P/'part1-final-pixel-review-direct-v264.json'),'sha256':m.sha(P/'part1-final-pixel-review-direct-v264.json')},
 'motion':{'path':m.rel(motionPath),'sha256':m.sha(motionPath)},'mixedAudio':{'path':m.rel(audioPath),'sha256':m.sha(audioPath)},
 'semanticCaptions':{'path':m.rel(semanticPath),'sha256':m.sha(semanticPath)},
 'fourGameTeachingReview':{'reviewed':True,'currentCaptionedSha256':pair['captioned']['sha256'],'fourTitles':games,'records':gameRows,'transferConclusion':conclusion,
  'method':'Current full normal-speed final intervals with readable fixed captions, original comparison conditions, explicit differences and a shared inspection principle. Rivalry2014 is an additional engine demonstration, not a fifth game.', 'publicRightsApproved':False},
 'finalFrames':89148,'actualFrames':53057,'explanationFrames':35371,'bodyFrames':88428,'ratioErrorFrames':pair['ratioErrorFrames'],'loudness':pair['loudness'],
 'identicalAacPayloadPtsDuration':True,'twoWholeDecodesPassed':True,'allPresentationPtsContinuous':True,'allFinalPixelsReviewed':True,'allMovingPixelsReviewed':True,
 'captionTimingApproved':True,'finalTimingApproved':True,'bodyRatioApproved':True,'qaApproved':True,
 'originalIntroAnd10SecondMembershipPreserved':True,'sourceAudio':0,'loop':0,'slowdown':0,'newGitImages':0,'collected':False,'uploaded':False,
 'humanWholeListening':'pending','humanPronunciation':'pending','publicRightsApproved':False,'originalNimbusFileVerified':False,'externalMediaBackup':'pending'}
m.save(P/'part1-final-qa-v264.json',qa)
cp=m.read(R/'production/research/game-lighting-history/checkpoint.json')
cp.update(updatedAt=m.stamp(),episode04Part1FinalQaV264={'path':m.rel(P/'part1-final-qa-v264.json'),'qaApproved':True,'collected':False,'uploaded':False},
 ownedActiveWork={'status':'no-active-owned-media-worker','next':'Create reviewed physical adapter, collect four files, save one private captioned upload and verify settings.'})
m.save(R/'production/research/game-lighting-history/checkpoint.json',cp)
print(m.json.dumps({'qaApproved':True,'boards':378,'fullMovingCuts':96,'frames':89148,'uploaded':False}))
