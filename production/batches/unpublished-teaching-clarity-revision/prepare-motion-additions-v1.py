"""Save the reviewed additive script/source plan; no synthesis, render or baseline edits."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
R = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
now = lambda: datetime.now(timezone.utc).isoformat()
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()
def rel(p): return p.resolve().relative_to(ROOT).as_posix()
def write(p,x):
    assert not p.exists(), 'Preserve prepared or executed state: '+str(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')

audit = read(B/'motion-script-audit-v1.json')
for path,digest in audit['inputSha256'].items(): assert sha(ROOT/path)==digest,path
proofs=[read(B/f'motion-opening-native-execution-v{v}.json') for v in [4,5,6]]
assert all(p['outerExitCode']==0 for p in proofs)
reviewed=[]
for p in proofs:
    for w in p['windows']:
        assert w['allFramePtsVerified'] and w['probeExitCode']==w['extractionExitCode']==0
        for x in w['samples']+w['boards']: assert sha(ROOT/x['path'])==x['sha256'],x['path']
        reviewed.append(dict(id=w['id'],samples=len(w['samples']),boards=len(w['boards']),
            allListedSamplePixelsDirectlyRead=True,sampleAndBoardHashesVerified=True,
            firstNativeFrame=w['firstFrame'],exclusiveEndNativeFrame=w['endExclusiveFrame']))
assert sum(x['samples'] for x in reviewed)==129 and sum(x['boards'] for x in reviewed)==23
native_review=dict(schemaVersion=1,recordedAt=now(),reviewed=reviewed,
    actualOuterExitEvidence={'v3':'2401fc/exit1 delayed final-frame probe;0images',
      'v4':'a87200/exit0','v5':'a0f886/exit0','v6':'0101fe/exit0'},
    historicalFailurePreserved=True,vfrInferred=False,
    directReadEvidence={'v4':'17roundabout/28tower samples all read before compaction',
      'v5':'36early samples read before compaction;boards07–10 directly read this turn',
      'v6':'all25samples/all5boards directly read this turn'},
    findings=[
      'Early58–69: water sweeps across dirty green playground floor; a clean strip widens, nearby posts remain visible and completion rises0to1%. Clear first-time task.',
      'Roundabout224.116667–227.266667: visible jet on dirty metal; subsequent approach/reframing is excluded from the dirt-removal claim.',
      'Tower276.9–285.8 is mainly approach and aiming; only285.9–289 is a floor-cleaning candidate.',
      'Continuing552.9–554.4 and572.9–580 carry large follower alerts covering the target. Exclude alert intervals;564.4–572.4 visibly cleans the board/post.',
      'All percentages are observed partial progress, never final victory or a comfort measurement.'
    ],sourceAudioUsed=False,allContinuousNativeFramesDirectlyViewed=False,
    finalCaptionAndOverlayPixelsApproved=False,publicRightsApproved=False,
    sourceMediaAndQaGitAdded=0,baselineModified=False)
native_review_path=R/'sources/native-source-direct-review-v1.json'
if native_review_path.exists():
    prior=read(native_review_path)
    assert {k:v for k,v in prior.items() if k!='recordedAt'}=={k:v for k,v in native_review.items() if k!='recordedAt'}
else:
    write(native_review_path,native_review)

specs=[('early-cleaning',3480,4140,'opening cleaning prerequisite:water→dirt removal→visible clean floor',6),
       ('roundabout-tail',13447,13636,'tool direction versus visible background landmarks',4),
       ('continuing-cleaning',33864,34344,'surface work continues while the nozzle follows the board/post',5),
       ('tower-unused',17154,17340,'reorient toward another surface; read the floor and post together',4)]
actions=[]
for sid,first,end,claim,v in specs:
    w=next(w for p in proofs for w in p['windows'] if w['id']==sid)
    frames=read((ROOT/next(x['path'] for x in w['samples'])).parent/'native-frames.json')['frames']
    pts=[int(x['pts']) for x in frames if first*256<=int(x['pts'])<end*256]
    assert pts==list(range(first*256,end*256,256))
    actions.append(dict(id=sid,sourceId='PF5L_2g9UVQ',sourceFirstFrame=first,
        sourceEndExclusiveFrame=end,sourceIn=first/60,sourceOut=end/60,
        sourceFirstPts=first*256,sourceEndExclusivePts=end*256,frames=end-first,
        seconds=(end-first)/60,nativeTimeBase='1/15360',nativePtsStep=256,
        sourceExecution=f'production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v{v}.json',
        claim=claim,actualNormalSpeed=1,loop=False,slowdown=False,
        exactFramePtsVerified=True,selectedSampleClarityApproved=True,
        actualFinalAllocationFrames=None,allFinalCueAndUiPixelsApproved=False))
bank=dict(schemaVersion=1,recordedAt=now(),sourceId='PF5L_2g9UVQ',
    source='shared/assets/game-footage/motion-sickness-games/PF5L_2g9UVQ.mp4',
    sourceSha256=proofs[0]['sourceSha256'],actions=actions,
    maximumUniqueFrames=sum(a['frames'] for a in actions),
    maximumUniqueSeconds=sum(a['seconds'] for a in actions),
    sourceSelectionPreflightApproved=True,finalTimedCutAdoptionApproved=False,
    sourceAudioUsed=False,loops=0,slowdowns=0,wholeDecodeRepeated=False,
    allContinuousFramePixelsApproved=False,publicRightsApproved=False)
assert bank['maximumUniqueFrames']==1515
write(R/'sources/source-action-bank-v1.json',bank)
rights=dict(schemaVersion=1,recordedAt=now(),currentPrimarySourcesReviewed=[
  {'url':'https://steamcommunity.com/app/1290000/discussions/0/4353365966426924959/',
   'publisher':'FuturLab developer FAQ','basis':'Developer allows gameplay streaming/video monetization; explains aim mode separating camera and nozzle.',
   'scope':'gameplay/IP permission, not clearance of every source recording or music track'},
  {'url':'https://canipostandmonetizevideosofdevolvergames.com/',
   'publisher':'Devolver','basis':'Permits streaming and monetized game videos; no proof-request form submitted.',
   'scope':'gameplay/IP policy; no third-party-recording sublicense inferred'},
  {'url':'https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/117',
   'publisher':'Microsoft Xbox Accessibility Guidelines117','basis':'Separate camera presentation and adjustable motion controls; explains player choices.',
   'scope':'developer design guidance; no clinical outcome or claim about every option in these games'}],
  officialSourceIds=['PF5L_2g9UVQ','6slinvkF0Rs'],
  sourceRecordings='Retained official developer/publisher demonstrations already documented in baseline sources/SOURCES.md.',
  sourceSoundOrMusicUsed=False,finalPublicRightsApproved=False,humanListeningApproved=False)
write(R/'sources/rights-current-primary-review-v1.json',rights)

ko=read(ROOT/'projects/motion-sickness-games/script/narration.ko.json')
en=read(ROOT/'projects/motion-sickness-games/script/narration.en.json')
add_ko=[{'id':'00a','title':'화면 움직임을 읽는 순서','lines':[
    '게임의 목표를 따라가면서도 화면은 덜 돌릴 수 있을까요?',
    '청소 게임의 조준과 시점, 퍼즐에서 방향이 바뀐 뒤 목표를 찾는 단서를 차례로 보겠습니다.',
    '이 관찰을 멀미를 고려한 카메라 설정과 되돌리기 기능의 설계로 연결해 보죠.',
    '먼저 물줄기로 바닥의 때를 지우는 장면에서, 빨간선으로 표시한 물줄기 방향과 파란 기둥 표시를 따로 보세요.'
  ]}, {'id':'06b','title':'방향이 바뀐 뒤에도 목표를 읽기','lines':[
    '조준을 나눠도, 다른 방향을 본 뒤에는 목표를 다시 알아볼 수 있어야 합니다.',
    '다음 예고편의 서로 다른 장면에서, 벽과 바닥이 목표를 찾는 어떤 단서가 되는지 보겠습니다.'
  ]}]
add_en=[{'id':'00a','title':'How we will read screen movement','lines':[
    "Can we follow a game's target while turning the whole view less?",
    'We will examine aiming and viewing in a cleaning game, then the cues for recognizing a target after the view changes in a puzzle game.',
    'We will connect these observations to motion-sickness-aware camera choices and a way to restore the original settings.',
    'First, as water removes dirt from the floor, watch the red line marking the spray direction and the blue marker on the background post separately.'
  ]}, {'id':'06b','title':'Read the target after changing direction','lines':[
    'Even with separate aiming, the target must remain recognizable after looking in another direction.',
    'In the following separate trailer shots, we will examine how walls and floors provide cues for finding the target.'
  ]}]
for name,baseline,additions in [('ko',ko,add_ko),('en',en,add_en)]:
    scenes=[copy.deepcopy(additions[0])]
    for scene in baseline['scenes']:
        scenes.append(copy.deepcopy(scene))
        if scene['id']=='06': scenes.append(copy.deepcopy(additions[1]))
    for original in baseline['scenes']:
        assert next(x for x in scenes if x['id']==original['id'])==original
    write(R/f'script/narration.{name}.json',dict(title=baseline['title'],status='paired-additive-pre-TTS-direct-review',scenes=scenes))
    write(R/f'script/additions.{name}.json',dict(title=baseline['title']+' · clarity additions',status='paired-pre-TTS-direct-review',scenes=additions))

baseline_manifest=read(ROOT/'projects/motion-sickness-games/project.json')
manifest=copy.deepcopy(baseline_manifest)
manifest['status']='additive-voice-measurement-only'
manifest['paths']['script']=rel(R/'script/additions.ko.json')
manifest['paths']['scriptEn']=rel(R/'script/additions.en.json')
manifest['tts'].update(outputDir='shared/output/narration/motion-sickness-games/teaching-clarity-additions-v1',filenameStem='motion-sickness-games-teaching-clarity-additions-v1')
manifest['editing'].update(exampleSeconds=0,narrationPlacement='continuous-across-example-and-explanation')
write(R/'tts-manifest-v1.json',manifest)
plan=read(ROOT/'projects/motion-sickness-games/production/final-v1/plan.json')
protected=[dict(path=p,sha256=h) for p,h in audit['inputSha256'].items()]
for scene in plan['scenes']:
    p=ROOT/scene['voice'];protected.append(dict(path=rel(p),sha256=sha(p)))
assert len(protected)==17
write(R/'baseline-protected-inputs-v1.json',dict(recordedAt=now(),inputs=protected,originalPcmCount=12,originalKoEnParagraphs=60,
    originalBodyFrames=37265,originalActualFrames=22359,originalExplanationFrames=14906,
    catFrames=120,memberFrames=600,palette='research-paper-white-v1',baselineVideoId='c18rkesgBSw'))
flow=[dict(original=x['id'],action='preserve entire original KO/EN scene and approved PCM',insertAfter='00a' if x['id']=='01' else ('06b' if x['id']=='07' else None)) for x in ko['scenes']]
review=dict(schemaVersion=1,recordedAt=now(),fullOriginalKoEnParagraphsDirectlyRead=60,
    fullNewKoEnParagraphsDirectlyRead=6,originalAllWordingAndOrderPreserved=True,
    newNarrationOnly=['00a','06b'],retentionMap=flow,overviewPromiseReview=True,
    overviewSentences=4,overviewPlannedSeconds=[20,30],overviewMeasuredSeconds=None,
    viewerQuestion='What motion does the task require, and what can players control separately?',
    viewerGain='Separate aim/view/added effects, read orientation cues, and make controls understandable and reversible.',
    promisedOrder=['cleaning aim/view','puzzle orientation cues','options/reset'],
    promisesMatchedToOriginalScenes={'cleaning aim/view':['01','03','05'],'puzzle orientation cues':['07','08'],'options/reset':['06','10','12']},
    causalBridge={'after':'06','before':'07','reason':'Options that separate controls must still let the player recognize a target after looking elsewhere; introduce the wall/floor question before switching games.'},
    reference='OS4CZkBBbW4',referenceFlowComparison='Individual response → observable motion and a stable frame → developer choices → player options/feedback. Our independent task-first lesson introduces the purpose early, then returns to separate responsibilities and reversible controls; clinical/player-medication advice is excluded.',
    referenceConceptualFlowCompared=True,referenceExactWordingClaimed=False,
    gameComparison='PowerWash has a visible water→dirt-removal result and needs fewer rules than the edited Talos puzzle shots. Start with cleaning; introduce separate trailer shots and wall/floor cues before the puzzle.',
    sampleClarityAndNativePtsPreflight=rel(R/'sources/native-source-direct-review-v1.json'),
    bank=rel(R/'sources/source-action-bank-v1.json'),
    annotationSemantics={'red':'labelled spray/aim direction','blue':'tracked background landmark','yellow':'surface being cleaned'},
    numbersAndAngles='Projected screen relationships only; do not invent game-world coordinates, engine internals or clinical measurements.',
    contentReadyForApprovedVoiceMeasurement=True,continuousFinalAnimationApproved=False,
    currentMixedAudioApproved=False,allFinalPixelsApproved=False,humanListeningApproved=False,publicRightsApproved=False)
write(R/'paired-script-direct-review-v1.json',review)
request=dict(schemaVersion=1,slug='motion-sickness-games',recordedAt=now(),
    manifest=rel(R/'tts-manifest-v1.json'),scriptReview=rel(R/'paired-script-direct-review-v1.json'),
    total=2,paragraphs=6,pairedWholeTextReview=True,overviewPromiseReview=True,
    baselineApprovedPcmRegeneration=0,protectedInputs=protected,
    preparedOnly=True,modelLoaded=False,actualOwnGpuJobs=0,researchManipulations=0,
    outputDir=manifest['tts']['outputDir'],scenes=[dict(id=s['id'],title=s['title'],text=' '.join(s['lines']),
      path=manifest['tts']['outputDir']+'/chunks/'+s['id']+'-scene.wav') for s in add_ko],
    next='One serialized owned cooperative handoff; preserve external lease; inspect actual TTS exit and original research resume, then full current-PCM ASR and measured allocation.')
write(R/'narration-tts-request-v1.json',request)
write(R/'latest-checkpoint.json',dict(schemaVersion=1,recordedAt=now(),slug='motion-sickness-games',
    stage='reviewed-source-and-paired-additions-ready-for-approved-voice-measurement',
    sourceSelectedSamplePreflightApproved=True,original12PcmPreserved=True,
    ttsStarted=False,modelLoaded=False,measuredTimingApproved=False,finalRatioApproved=False,
    currentMixedAudioApproved=False,allFinalPixelsApproved=False,qaApproved=False,
    outputCollected=False,actualReplacementVideoId=None,privateSettingsVerified=False,
    gitDelivered=False,scheduleReplacementVerified=False,humanListeningApproved=False,publicRightsApproved=False))

# Reconcile only our already-delivered polar evidence; no repeat commit or schedule.
polar=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1/publishing'
git=read(polar/'schedule-evidence-git-verification-v6.json')
assert git['exactLocalRemoteMatch'] and git['allFinalRemoteBlobsVerified'] and git['verifiedBlobCount']==15
qpath=B/'queue.json';q=read(qpath)
polar_item=next(x for x in q['items'] if x['slug']=='game-math-polar-3d')
polar_item.update(status='reviewed-replacement-scheduled-and-evidence-git-delivered',scheduleEvidenceCommit=git['commit'])
motion_item=next(x for x in q['items'] if x['slug']=='motion-sickness-games')
motion_item.update(status='source-clarity-and-paired-additions-reviewed-awaiting-measured-voice',
    currentCheckpoint=rel(R/'latest-checkpoint.json'),newOverviewAndBridgePrepared=True,actualReplacementVideoId=None)
q['execution'].update(currentSlug='motion-sickness-games',stage='motion-approved-voice-measurement-prepared',
    next='Serialize only the two reviewed additions after the current external handoff and original research resume; preserve all12originalPCM.')
q['updatedAt']=now();qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(prepared=True,newKoEnParagraphs=6,retainedKoEnParagraphs=60,
    retainedPcm=12,sourceSamplesDirectlyRead=129,boardsDirectlyRead=23,
    uniqueNativeActionSeconds=bank['maximumUniqueSeconds'],modelLoaded=False,gpuJobs=0),ensure_ascii=False))
