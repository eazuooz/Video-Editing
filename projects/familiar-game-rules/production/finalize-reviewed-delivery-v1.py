"""Publish local manifest paths only after actual pair and every final QA board review."""
from final_cpu_common import *

plan=read(FINAL/'plan.json');pair=read(FINAL/'review-pair-build.json')
pixels=read(FINAL/'encoded-caption-pixels-direct-review-v1.json')
execution=read(FINAL/'encoded-caption-qa-execution.json')
speech=read(FINAL/'full-mix-asr-review.json')
alignment=read(FINAL/'caption-alignment-review.json')
assert execution['exitCode']==0 and pixels['allFinalPixelsDirectlyReviewed'] is True
assert pixels['planSha256']==pair['planSha256']==speech['planSha256']==sha(FINAL/'plan.json')
assert pixels['captionAssSha256']==pair['captionAssSha256']==sha(FINAL/'captions.ko.ass')
assert speech['all38WindowsDirectlyCompared'] and speech['technicallyApproved']
assert alignment['approved'] and alignment['manualSemanticReview'] and alignment['allParagraphTextsRetained']
assert len(pixels['sheets'])==len(execution['sheets']) and len(pixels['images'])==len(execution['images'])
for reviewed,actual in zip(pixels['sheets'],execution['sheets']):
    assert reviewed['path']==actual['path'] and reviewed['sha256']==actual['sha256']==sha(ROOT/actual['path']) and reviewed['directlyRead']
for reviewed,actual in zip(pixels['images'],execution['images']):
    assert reviewed['path']==actual['path'] and reviewed['sha256']==actual['sha256']==sha(ROOT/actual['path']) and reviewed['directlyRead']
assert {c for r in pixels['images'] for c in r['cues']}==set(range(1,254))
assert pair['frames']==23570 and pair['identicalAacPayload']
assert plan['actualFrames']==13710 and plan['explanationFrames']==9140 and plan['body60_40ErrorFrames']==0
for row in pair['records']:
    assert sha(ROOT/row['path'])==row['sha256'] and row['wholeDecodeExitCode']==0 and row['exactPresentationClock']['allPacketPtsExact']
pending=['Human whole-video listening and pronunciation, including proper names and recognizer particle/spelling variants.','Final public rights review and original Nimbus Audio Library file bytes.','Truncated membership handles preserved from supplied original rows; external media backup confirmation.','Private pinned comment posting/pinning and optional platform automatic dubbing review.']
qa=dict(createdAt=now(),scope='Actual current encoded pair and all fixed-caption cue/cut/UI/paragraph-onset/branding/member pixels, with current mixed19+19 speech contexts.',planSha256=sha(FINAL/'plan.json'),pairBuildSha256=sha(FINAL/'review-pair-build.json'),pixelReviewSha256=sha(FINAL/'encoded-caption-pixels-direct-review-v1.json'),mixedReviewSha256=sha(FINAL/'full-mix-asr-review.json'),captionAlignmentSha256=sha(FINAL/'caption-alignment-review.json'),frames=23570,seconds=23570/60,width=1920,height=1080,fps=60,koCues=253,enCues=118,paragraphs=70,sourceCuts=85,whiteSlices=8,bodyActualFrames=13710,bodyExplanationFrames=9140,bodyRatioErrorFrames=0,allFinalPixelsDirectlyReviewed=True,all38MixedSpeechWindowsDirectlyCompared=True,twoWholeDecodesExitCode0=True,all23570PresentationPtsExact=True,timeBase='1/90000',ptsStep=1500,identicalSourceCleanCaptionedAac=True,lufs=pair['inheritedSameAacLufs'],truePeakDbtp=pair['inheritedSameAacTruePeakDbtp'],captionCenter=[960,970],captionStyle='boxed-white-forest-v1',sourceAudioStreams=0,selfGameLoopSlowdown=0,overviewPcmSeconds=24.32,originalSixWhiteFramesPreserved=8835,originalAllPcmSamplesPreserved=8968322,catFrames=120,membershipFrames=600,original12MemberIdentitiesPreserved=True,membershipTitle='멤버쉽가입 감사드립니다.',humanWholeListening='pending',humanPronunciation='pending',publicReady=False,technicalReviewApproved=True,pending=pending,localQaImagesOnly=True,newGitQaImages=0)
assert abs(qa['lufs']+16)<=.6 and qa['truePeakDbtp']<=-1.5
write(FINAL/'QA.json',qa)
manifest=read(BASE.parent/'project.json');paths=manifest['paths']
paths.update(videoClean=next(r['path'] for r in pair['records'] if '.clean.' in r['path']),videoBurnedCaptions=next(r['path'] for r in pair['records'] if '.captioned.' in r['path']),captionAlignmentReview=rel(FINAL/'caption-alignment-review.json'),audioMix=rel(FINAL/'final-mix.m4a'),audioEditorWav=rel(FINAL/'final-mix.wav'),narration=rel(FINAL/'narration-timed.wav'),finalQa=rel(FINAL/'QA.json'))
manifest.update(status='rendered-and-technically-reviewed-private-delivery-pending',publishReady=False,finalRender=dict(rendered=True,technicalQaApproved=True,finalMixAsrApproved=True,allFinalCaptionPixelsReviewed=True,qa=rel(FINAL/'QA.json'),frames=23570,seconds=23570/60,records=pair['records'],humanWholeListening='pending',humanPronunciation='pending',knownIssues=[],openItems=pending))
manifest['membershipOutro']['appliedToFinal']=True
manifest['audio']['mixStatus']='current-approved-Nimbus-mix-measured-and-mixed-ASR-technically-reviewed-human-listening-pending'
manifest['editing']['exampleInterleaving']['reviewStatus']='All85 current whole-motion inputs and every actual final caption/cut board directly reviewed; human whole listening/pronunciation pending.'
manifest['editing']['finalPlan']['scope']='Current final encoded pair technically reviewed; collection/private settings/Git pending.'
manifest['stopAfterCurrent']=STOP
write(BASE.parent/'project.json',manifest)
update_checkpoint('current-final-pair-and-all-pixel-QA-complete','Collect the4 reviewed deliverables, then one private captioned upload/settings/selective Git delivery and pause24. Do not start next queued.',rendered=True,qaComplete=True,finalMixAsrApproved=True,allFinalCaptionPixelsReviewed=True,finalQa=rel(FINAL/'QA.json'))
print(json.dumps(dict(frames=23570,qaApproved=True,publishReady=False,collected=False,uploaded=False)))
