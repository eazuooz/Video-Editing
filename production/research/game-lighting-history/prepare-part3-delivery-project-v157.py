"""Create the physical delivery adapter only after actual final QA approval."""
from pathlib import Path
import importlib.util,copy
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT;P=ROOT/'projects/game-lighting-history-04/production'
plan=m.read(P/'part3-final-input-plan-v145.json');pair=m.read(P/'part3-reviewed-pair-build-v149.json')
qa=m.read(P/'part3-final-qa-v157.json')
assert qa['qaApproved'] and qa['allFinalPixelsReviewed'] and qa['allMovingPixelsReviewed']
assert qa['captionedSha256']==pair['captioned']['sha256']==m.sha(ROOT/pair['captioned']['path'])
assert qa['cleanSha256']==pair['clean']['sha256']==m.sha(ROOT/pair['clean']['path'])
assert qa['planSha256']==pair['planSha256']==m.sha(P/'part3-final-input-plan-v145.json')
assert pair['identicalAacPayloadPtsDuration'] and pair['clean']['wholeDecode']['exitCode']==pair['captioned']['wholeDecode']['exitCode']==0
semantic=m.read(P/'part3-semantic-caption-review-v155.json');assert semantic['approved'] and len(semantic['paragraphs'])==85
prepared=m.read(ROOT/'projects/game-lighting-history-04/publishing/part3-prepared-upload-v150.json')
base=ROOT/'projects/game-lighting-history-04-3';assert not (base/'project.json').exists(), 'Preserve existing adapter; update explicitly'
for folder in ['script','planning','production','sources','publishing']: (base/folder).mkdir(parents=True,exist_ok=True)
ordered=sorted(plan['paragraphs'],key=lambda x:min(q['fromFrame'] for q in x['koCues']))
for lang in ['ko','en']:
    m.save(base/f'script/narration.{lang}.json',dict(language=lang,logicalEpisode=4,physicalPart=3,sourcePlan=m.rel(P/'part3-final-input-plan-v145.json'),
        scenes=[dict(id=p['id'],narration=p[lang],startFrame=min(q['fromFrame'] for q in p['koCues']),endFrame=max(q['toFrame'] for q in p['koCues']),kind=p['kind']) for p in ordered]))
visual=m.read(P/'part3-annotated-visual-build-v148.json')
native={r['id']:r for r in visual['cuts']}
scenes=[dict(id='original-branding',kind='branding',startFrame=0,frames=120,source=plan['branding']['path'])]
for c in plan['cuts']:
    row=dict(id=c['id'],kind=c['kind'],startFrame=c['fromFrame'],frames=c['toFrame']-c['fromFrame'],source=native[c['id']]['path'],sourceIn=0,
        sourceIntervals=c.get('proposedCuts',[]),sourceRecord=c.get('source'),originalInput=c.get('video'),
        repairedNative=native[c['id']]['repairedNative'],sourceAudio=False,loop=False,slowdown=False)
    scenes.append(row)
scenes.append(dict(id='original-membership',kind='membership',startFrame=plan['finalFrames']-600,frames=600,source=plan['membership']['path']))
m.save(base/'production/timeline.json',dict(fps=60,timeBase='1/90000',finalFrames=92038,scenes=scenes,
    actualFrames=54791,explanationFrames=36527,bodyFrames=91318,ratioErrorFrames=.2,originalInputPlan=m.rel(P/'part3-final-input-plan-v145.json')))
m.save(base/'sources/selected-sources.json',dict(policy='existing-games-and-authorized-real-engine-demonstrations',
    sourcePlan=m.rel(P/'selected-part3-source-plan-v144.json'),framePlan=m.rel(P/'part3-final-input-plan-v145.json'),
    clips=[dict(id=c['id'],source=c.get('source'),video=c.get('video'),sourceIntervals=c.get('proposedCuts',[]),kind=c['kind']) for c in plan['cuts']],
    fourGames=['Resident Evil Requiem','Starfield','Hogwarts Legacy','NBA 2K27'],
    reviewedTeaching=qa['fourGameTeachingReview'],rightsApprovedForPublicUse=False,sourceAudio=False,loop=False,slowdown=False))
paths=dict(script=m.rel(base/'script/narration.ko.json'),scriptEn=m.rel(base/'script/narration.en.json'),timeline=m.rel(base/'production/timeline.json'),
    footageManifest=m.rel(base/'sources/selected-sources.json'),videoClean=pair['clean']['path'],videoBurnedCaptions=pair['captioned']['path'],
    captionsKo=next(t['path'] for t in pair['tracks'] if t['language']=='ko'),captionsEn=next(t['path'] for t in pair['tracks'] if t['language']=='en'),
    captionAlignmentReview=m.rel(P/'part3-semantic-caption-review-v155.json'),finalQa=m.rel(P/'part3-final-qa-v157.json'),
    finalInputPlan=m.rel(P/'part3-final-input-plan-v145.json'),finalMix=m.rel(P/'part3-final-mix-settings-v146.json'),reviewPair=m.rel(P/'part3-reviewed-pair-build-v149.json'),
    mixedAudioReview=m.rel(P/'part3-final-mixed-asr-direct-review-v147.json'),pixelReview=m.rel(P/'part3-final-pixel-review-direct-v157.json'))
project=dict(schemaVersion=2,slug=plan['slug'],logicalEpisode=4,physicalPart=3,parentProject='game-lighting-history-04',
    status='reviewed-production-ready-for-collection-and-private-upload',titles=dict(ko=prepared['titleKo'],en=prepared['titleEn']),
    paths=paths,visualStyle='research-black-v1',visualStyleGuide='docs/VIDEO_VISUAL_STYLE.md',publishReady=False,
    delivery=dict(directory='output/'+plan['slug'],required=['captioned.mp4','clean.mp4','ko.srt','en.srt'],preserveSources=True),
    editing=dict(targetGameplayShare=.6,targetExplanationShare=.4,ratioScope='body-excluding-original-branding-and-membership',ratioRoundingToleranceFrames=1,
        actualGameplaySeconds=54791/60,actualExplanationSeconds=36527/60,actualGameplayShare=54791/91318,ratioErrorFrames=.2,
        explanationStyle='research-black-v1',captionStyle=dict(id='boxed-white-forest-v1',centerPx=[960,970],maximumLines=2,fontSize=48),
        originalContentPreserved=True,sourceAudio=False,loop=False,slowdown=False,
        openingOverview=dict(required=True,scene='part3-overview',question=plan['question'],measuredNarrationSeconds=16.4833333333,visibleSeconds=1032/60,
            review='Whole-video question, appearance/controls/resources order and first-example connection directly compared; no narration padding.'),
        fourGameTeachingReview=qa['fourGameTeachingReview']),
    membershipOutro=dict(enabled=True,durationSeconds=10,title='멤버쉽가입 감사드립니다.',appliedToFinal=True,originalProfilesNamesBadgesLogoPreserved=True),
    finalRender=dict(frames=92038,durationSeconds=92038/60,fps=60,width=1920,height=1080,qaApproved=True,
        allFinalPixelsReviewed=True,allMovingPixelsReviewed=True,cleanSha256=pair['clean']['sha256'],captionedSha256=pair['captioned']['sha256'],
        knownIssues=[],openItems=['Human whole listening and pronunciation pending.','Public footage rights review pending.','Original Nimbus library file review pending.','Truncated original membership handles preserved.','External media backup pending.']),
    approvals=dict(humanWholeListening='pending',humanPronunciation='pending',rightsApprovedForPublicUse=False,originalNimbusFileVerified=False),
    productionEvidence=dict(qa=m.rel(P/'part3-final-qa-v157.json'),mixedAudio=m.rel(P/'part3-final-mixed-asr-direct-review-v147.json'),
        pcm=m.rel(P/'part3-current-mix-pcm-corroboration-v147.json'),semanticCaptions=m.rel(P/'part3-semantic-caption-review-v155.json')))
m.save(base/'project.json',project)
receipt=copy.deepcopy(prepared);receipt.update(status='prepared-reviewed-delivery-awaiting-actual-upload',qaApproved=True,allFinalPixelsReviewed=True,collected=False,
    preparedParentReceipt=m.rel(ROOT/'projects/game-lighting-history-04/publishing/part3-prepared-upload-v150.json'))
m.save(base/'publishing/youtube-upload.json',receipt)
for name in ['part3-description.ko.v150.txt','part3-description.en.v150.txt','part3-pinned-comment.ko.v150.txt']:
    original=ROOT/'projects/game-lighting-history-04/publishing'/name
    assert original.exists(), name
    (base/'publishing'/name.removeprefix('part3-').replace('.v150','')).write_bytes(original.read_bytes())
print(m.json.dumps(dict(slug=plan['slug'],sceneScripts=85,timelineScenes=95,renderApproved=True,collected=False,uploaded=False)))
