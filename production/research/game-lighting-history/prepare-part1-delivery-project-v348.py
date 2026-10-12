"""Create a physical-part adapter only from completed current QA; no platform action."""
from pathlib import Path
import importlib.util,copy,json,hashlib,re
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT;P=ROOT/'projects/game-lighting-history-04/production'
PP=P/'part1-final-input-plan-v309.json';plan=m.read(PP)
pair=m.read(P/'part1-reviewed-pair-build-v345.json');qa=m.read(P/'part1-final-qa-v347.json')
assert qa['qaApproved'] and qa['allFinalPixelsReviewed'] and qa['allMovingPixelsReviewed']
assert qa['planSha256']==pair['planSha256']==m.sha(PP)
for key in ['clean','captioned']:
 assert qa[key+'Sha256']==pair[key]['sha256']==m.sha(ROOT/pair[key]['path'])
 assert pair[key]['wholeDecode']['exitCode']==0 and pair[key]['frames']==plan['finalFrames'] and pair[key]['allPresentationPtsContinuous']
assert pair['identicalAacPayloadPtsDuration'] and abs(plan['ratioErrorFrames'])<=1
semantic=m.read(P/'part1-semantic-caption-review-v312.json')
assert semantic['approved'] and semantic['manualSemanticReview'] and semantic['unchanged76ParagraphsExact'] and semantic['paragraphCount']==77
assert semantic['planSha256']==m.sha(PP)
# Preserve the complete 76-paragraph review and splice only the explicitly
# reviewed direction correction. The collector needs a full, current cue map.
oldSemanticPath=ROOT/semantic['previous76DirectReview']['path']
assert m.sha(oldSemanticPath)==semantic['previous76DirectReview']['sha256']
oldSemantic=m.read(oldSemanticPath)
assert oldSemantic['status']=='approved-semantic-paragraph-alignment' and oldSemantic['allParagraphTextsRetained']
layoutPath=P/'part1-caption-layout-v309.json';layout=m.read(layoutPath)
def srt_rows(path):
 rows=[]
 for block in (ROOT/path).read_text('utf-8-sig').strip().split('\n\n'):
  lines=block.strip().splitlines();a,b=lines[1].split(' --> ')
  def seconds(t):
   h,mi,s,ms=map(int,re.split('[:,]',t));return h*3600+mi*60+s+ms/1000
  rows.append(dict(id=int(lines[0]),start=seconds(a),end=seconds(b),text='\n'.join(lines[2:])))
 return rows
captionRows={t['language']:srt_rows(t['path']) for t in layout['tracks']}
oldById={p['id']:p for p in oldSemantic['paragraphs']};fullParagraphs=[]
for p in sorted(plan['paragraphs'],key=lambda p:p['koCues'][0]['fromFrame']):
 old=oldById[p['id']];changed=p['id']==semantic['changedParagraph']['id']
 if not changed:
  assert [old['ko'],old['en']]==[p['ko'],p['en']]
  assert old['koCues']==[q['id'] for q in p['koCues']] and old['enCues']==[q['id'] for q in p['enCues']]
  row=copy.deepcopy(old)
 else:
  corrected=semantic['changedParagraph'];assert [p['ko'],p['en']]==[corrected['ko'],corrected['en']]
  assert p['koCues']==corrected['koCues'] and p['enCues']==corrected['enCues']
  row=dict(id=p['id'],ko=p['ko'],en=p['en'],literalTextPairSha256=hashlib.sha256(json.dumps([p['ko'],p['en']],ensure_ascii=False).encode()).hexdigest(),
   bothCompleteParagraphsDirectlyRead=True,claimsExamplesConditionsAndConclusionAligned=True,directlyReadBothFullTexts=True,
   fromFrame=p['koCues'][0]['fromFrame'],toFrame=p['koCues'][-1]['toFrame'],
   start=captionRows['ko'][p['koCues'][0]['id']-1]['start'],end=captionRows['ko'][p['koCues'][-1]['id']-1]['end'],
   koCues=[q['id'] for q in p['koCues']],enCues=[q['id'] for q in p['enCues']],directEvidence=m.rel(P/'part1-semantic-caption-review-v312.json'))
 for lang in ['ko','en']:
  indices=row[lang+'Cues'];cues=captionRows[lang]
  assert abs(cues[indices[0]-1]['start']-row['start'])<=.002 and abs(cues[indices[-1]-1]['end']-row['end'])<=.002
  assert all(re.sub(r'\s+','',cues[q['id']-1]['text'])==re.sub(r'\s+','',q['text']) for q in p[lang+'Cues'])
 fullParagraphs.append(row)
assert len(fullParagraphs)==77
for lang in ['ko','en']:
 assert [n for p in fullParagraphs for n in p[lang+'Cues']]==list(range(1,len(captionRows[lang])+1))
captionTracks=[]
for t in layout['tracks']:
 assert m.sha(ROOT/t['path'])==t['sha256'] and len(captionRows[t['language']])==t['cueCount']
 captionTracks.append(dict(t,cues=t['cueCount']))
semanticFullPath=P/'part1-semantic-caption-delivery-map-v348.json'
semanticFull=dict(status='approved-semantic-paragraph-alignment',approved=True,manualSemanticReview=True,allParagraphTextsRetained=True,
 assembledAt=m.stamp(),planSha256=m.sha(PP),layoutSha256=m.sha(layoutPath),paragraphs=fullParagraphs,captions=captionTracks,
 directReviewProvenance=[semantic['previous76DirectReview'],dict(path=m.rel(P/'part1-semantic-caption-review-v312.json'),sha256=m.sha(P/'part1-semantic-caption-review-v312.json'))],
 unchanged76ParagraphReviewRecordsPreserved=True,onlyDirectionCorrectionSpliced=True,humanWholeListening='pending',humanPronunciation='pending')
assert not semanticFullPath.exists();m.save(semanticFullPath,semanticFull)
visual=m.read(P/'part1-final-visual-build-v344.json');OP=P/'part1-delivery-input-overrides-v348.json'
assert visual['planSha256']==m.sha(PP) and visual['retainedOther92InputsByteIdenticalToV332']
assert visual['inputOverrides']['textureReview']['sha256']==m.sha(P/'part1-texture-native-input-direct-review-v344.json')
byId={r['id']:r for r in visual['cuts']};effective=[];changes={}
for original in plan['cuts']:
 row=byId[original['id']];assert (row['frames'],row['fromFrame'],row['toFrame'])==(original['frames'],original['fromFrame'],original['toFrame'])
 c=copy.deepcopy(original);c['proposedCuts']=row.get('sourceCuts',c.get('proposedCuts',[]));c['currentNative']=dict(path=row['path'],sha256=row['sha256'])
 if row['sha256']!=original['video']['sha256']:
  changes[c['id']]=dict(native=c['currentNative'],sourceIntervals=c['proposedCuts'],review=row.get('inputDirectReview'),originalVideo=original['video'])
 effective.append(c)
assert len(effective)==94
overrides=dict(preparedAt=m.stamp(),inputPlan=dict(path=m.rel(PP),sha256=m.sha(PP)),visualBuild=dict(path=m.rel(P/'part1-final-visual-build-v344.json'),sha256=m.sha(P/'part1-final-visual-build-v344.json')),effectiveCuts=effective,changes=changes,allCutFramesPreserved=True,technicalQa=dict(path=m.rel(P/'part1-final-qa-v347.json'),sha256=m.sha(P/'part1-final-qa-v347.json')))
assert not OP.exists();m.save(OP,overrides)
visual['inputOverrides']={'path':m.rel(OP),'sha256':m.sha(OP)}
assert plan['currentGuideReplacement']['allOther93CutFramesUnchanged'] and plan['currentGuideReplacement']['allOriginal36ParagraphsAndPcmUnchanged']
preparedPath=ROOT/'projects/game-lighting-history-04/publishing/part1-prepared-upload-v300.json';prepared=m.read(preparedPath)
assert prepared['privacy']=='private' and prepared['scheduled'] is False and prepared['actualVideoId'] is None
base=ROOT/'projects/game-lighting-history-04-1'
assert not (base/'project.json').exists(),'Preserve an existing physical delivery; never silently recreate.'
for folder in ['script','planning','production','sources','publishing']:(base/folder).mkdir(parents=True,exist_ok=True)
ordered=sorted(plan['paragraphs'],key=lambda p:min(c['fromFrame'] for c in p['koCues']))
for lang in ['ko','en']:
 m.save(base/f'script/narration.{lang}.json',dict(language=lang,logicalEpisode=4,physicalPart=1,sourcePlan=m.rel(PP),
  scenes=[dict(id=p['id'],narration=p[lang],startFrame=min(c['fromFrame'] for c in p['koCues']),endFrame=max(c['toFrame'] for c in p['koCues']),kind=p['kind']) for p in ordered]))
native={r['id']:r for r in visual['cuts']}
assert len(native)==len(overrides['effectiveCuts'])==94
scenes=[dict(id='original-branding',kind='branding',startFrame=0,frames=120,source=plan['branding']['path'])]
for c in overrides['effectiveCuts']:
 row=native[c['id']];assert row['sha256']==m.sha(ROOT/row['path'])
 scenes.append(dict(id=c['id'],kind=c['kind'],startFrame=c['fromFrame'],frames=c['toFrame']-c['fromFrame'],source=row['path'],sourceIn=0,
  sourceIntervals=c.get('proposedCuts',[]),sourceRecord=c.get('source'),originalInput=c.get('video'),
  repairedNative=c['id'] in overrides['changes'],inputOverride=overrides['changes'].get(c['id']),sourceAudio=False,loop=False,slowdown=False))
scenes.append(dict(id='original-membership',kind='membership',startFrame=plan['finalFrames']-600,frames=600,source=plan['membership']['path']))
m.save(base/'production/timeline.json',dict(fps=60,timeBase='1/90000',finalFrames=plan['finalFrames'],scenes=scenes,
 actualFrames=plan['actualFrames'],explanationFrames=plan['explanationFrames'],bodyFrames=plan['bodyFrames'],ratioErrorFrames=plan['ratioErrorFrames'],
 originalInputPlan=m.rel(PP),effectiveInputOverrides=visual['inputOverrides']))
games=['Horizon Forbidden West','The Outer Worlds 2','Cyberpunk 2077','Fortnite']
assert qa['fourGameTeachingReview']['fourTitles']==games and qa['fourGameTeachingReview']['reviewed']
m.save(base/'sources/selected-sources.json',dict(policy='existing-games-and-authorized-real-engine-demonstrations',framePlan=m.rel(PP),
 effectiveInputOverrides=visual['inputOverrides'],clips=[dict(id=c['id'],source=c.get('source'),video=c.get('video'),sourceIntervals=c.get('proposedCuts',[]),kind=c['kind']) for c in overrides['effectiveCuts']],
 fourGames=games,reviewedTeaching=qa['fourGameTeachingReview'],rightsApprovedForPublicUse=False,sourceAudio=False,loop=False,slowdown=False))
paths=dict(script=m.rel(base/'script/narration.ko.json'),scriptEn=m.rel(base/'script/narration.en.json'),timeline=m.rel(base/'production/timeline.json'),
 footageManifest=m.rel(base/'sources/selected-sources.json'),videoClean=pair['clean']['path'],videoBurnedCaptions=pair['captioned']['path'],
 captionsKo=next(t['path'] for t in pair['tracks'] if t['language']=='ko'),captionsEn=next(t['path'] for t in pair['tracks'] if t['language']=='en'),
 captionAlignmentReview=m.rel(semanticFullPath),finalQa=m.rel(P/'part1-final-qa-v347.json'),finalInputPlan=m.rel(PP),
 effectiveInputOverrides=m.rel(OP),finalMix=m.rel(P/'part1-final-mix-settings-v310.json'),reviewPair=m.rel(P/'part1-reviewed-pair-build-v345.json'),
 mixedAudioReview=m.rel(P/'part1-final-current-mixed-asr-direct-review-v312.json'),pixelReview=m.rel(P/'part1-current-final-pixel-review-direct-v347.json'))
overview=next(c for c in overrides['effectiveCuts'] if c['id']=='part1-overview')
project=dict(schemaVersion=2,slug=plan['slug'],logicalEpisode=4,physicalPart=1,parentProject='game-lighting-history-04',
 status='reviewed-production-ready-for-collection-and-private-upload',titles=dict(ko=prepared['titleKo'],en=prepared['titleEn']),paths=paths,
 visualStyle='research-black-v1',visualStyleGuide='docs/VIDEO_VISUAL_STYLE.md',publishReady=False,
 delivery=dict(directory='output/'+plan['slug'],required=['captioned.mp4','clean.mp4','ko.srt','en.srt'],preserveSources=True),
 editing=dict(targetGameplayShare=.6,targetExplanationShare=.4,ratioScope='body-excluding-original-branding-and-membership',ratioRoundingToleranceFrames=1,
  actualGameplaySeconds=plan['actualFrames']/60,actualExplanationSeconds=plan['explanationFrames']/60,actualGameplayShare=plan['actualFrames']/plan['bodyFrames'],ratioErrorFrames=plan['ratioErrorFrames'],
  explanationStyle='research-black-v1',captionStyle=dict(id='boxed-white-forest-v1',centerPx=[960,970],maximumLines=2,fontSize=48),
  originalContentPreserved=True,sourceAudio=False,loop=False,slowdown=False,
  openingOverview=dict(required=True,scene='part1-overview',question=plan['question'],measuredNarrationSeconds=overview['pcm']['samples']/24000,visibleSeconds=overview['frames']/60,
   review='Current whole-video question, shadows/history/mobile order and first-example connection reviewed with the actual mixed narration and final pixels; no padding.'),fourGameTeachingReview=qa['fourGameTeachingReview']),
 membershipOutro=dict(enabled=True,durationSeconds=10,title='멤버쉽가입 감사드립니다.',appliedToFinal=True,originalProfilesNamesBadgesLogoPreserved=True),
 finalRender=dict(frames=plan['finalFrames'],durationSeconds=plan['finalFrames']/60,fps=60,width=1920,height=1080,qaApproved=True,
  allFinalPixelsReviewed=True,allMovingPixelsReviewed=True,cleanSha256=pair['clean']['sha256'],captionedSha256=pair['captioned']['sha256'],knownIssues=[],
  openItems=['Human whole listening and pronunciation pending.','Public footage rights review pending.','Original Nimbus library file review pending.','Truncated original membership handles preserved.','External media backup pending.']),
 approvals=dict(humanWholeListening='pending',humanPronunciation='pending',rightsApprovedForPublicUse=False,originalNimbusFileVerified=False),
 productionEvidence=dict(qa=m.rel(P/'part1-final-qa-v347.json'),mixedAudio=m.rel(P/'part1-final-current-mixed-asr-direct-review-v312.json'),
  pcm=m.read(P/'part1-final-current-mixed-asr-direct-review-v312.json')['pcmPreservation']['path'],semanticCaptions=m.rel(P/'part1-semantic-caption-review-v312.json')))
m.save(base/'project.json',project)
receipt=copy.deepcopy(prepared);receipt.update(status='prepared-reviewed-delivery-awaiting-actual-upload',qaApproved=True,allFinalPixelsReviewed=True,collected=False,preparedParentReceipt=m.rel(preparedPath))
m.save(base/'publishing/youtube-upload.json',receipt)
for name in ['part1-description.ko.v246.txt','part1-description.en.v246.txt','part1-pinned-comment.ko.v246.txt']:
 original=ROOT/'projects/game-lighting-history-04/publishing'/name;assert original.exists()
 (base/'publishing'/name.removeprefix('part1-').replace('.v246','')).write_bytes(original.read_bytes())
print(m.json.dumps(dict(slug=plan['slug'],sceneScripts=len(ordered),timelineScenes=len(scenes),renderApproved=True,collected=False,uploaded=False)))
