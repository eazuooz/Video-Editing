"""Seal the directly compared15 KOEN paragraphs and prepare only their TTS request."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OLD = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = datetime.now(timezone.utc).isoformat()

def save(p, v):
    if p.exists():
        prior = read(p)
        assert {k:x for k,x in prior.items() if k != 'recordedAt'} == {k:x for k,x in v.items() if k != 'recordedAt'}, str(p)
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', 'utf-8')

ids = ['07b', '08b', '11b']
additions = {k: read(R / f'script/additions.{k}.json') for k in ['ko','en']}
for lang in ['ko','en']:
    full = read(R / f'script/narration.{lang}.json')
    old = read(OLD / f'script/narration.{lang}.json')
    assert [x for x in full['scenes'] if x['id'] not in ids] == old['scenes']
    assert [x for x in full['scenes'] if x['id'] in ids] == additions[lang]['scenes']
assert [x['id'] for x in additions['ko']['scenes']] == ids
for a,b in zip(additions['ko']['scenes'], additions['en']['scenes']):
    assert a['id'] == b['id'] and len(a['lines']) == len(b['lines'])
assert sum(len(x['lines']) for x in additions['ko']['scenes']) == 15
protected = read(R / 'baseline-protected-inputs-v1.json')['inputs']
for x in protected:
    assert sha(ROOT / x['path']) == x['sha256'], x['path']
bank = read(R / 'sources/source-action-bank-v1.json')
assert bank['sourcePlanningApproved'] and len(bank['actions']) == 8
review_path = R / 'paired-script-direct-review-v1.json'
save(review_path, dict(schemaVersion=1, recordedAt=now,
    allNewKoEnParagraphsDirectlyCompared=15, newScenes=3,
    originalAllWordingAndOrderPreserved=True, original14PcmRegeneration=0,
    originalWholePairedSceneReview='Continuing-task14scene audit; new paired text and all six adjacent boundaries reread directly.',
    contentReadyForApprovedVoiceMeasurement=True,
    comparisonResults=[
        '07b: Portal cube/laser/button prerequisites are explained first. Held cube and viewpoint movement are compared with PowerWash independent tool aiming. Distinct laser and button excerpts are explicitly separate.',
        '08b: Yellow destination marker precedes changed doorway viewpoint; hand board removal follows in a separate selected interval. VR destination selection and hand work are distinguished from mouse/nozzle or cube manipulation.',
        '11b: All four games return to manipulated object, visible motion and remaining orientation cue; transferable roles and reset choices connect to the preserved conclusion.',
    ],
    overviewPromiseReview=True, overviewReused=True, overviewScene='00a',
    overviewOriginalMeasuredSeconds=25.116666666666667,
    promisedSteps=['cleaning aim/view','puzzle and arrival orientation cues','understandable reversible camera options'],
    openingListsFourNamesInsteadOfTeaching=False,
    referenceFlowCompared=True, reference='OS4CZkBBbW4',
    referenceMatch='Individual response → observed screen movement → developer responsibilities → player choices/feedback. Task-first comparisons add prerequisites and preserve the original order.',
    referenceMediaOrWholeTranslationCopied=False,
    annotationRoles={'red':'working cube/board or tool direction','blue':'labelled surrounding landmark','yellow':'destination or currently relevant target'},
    prohibitedClaims=['player traverses a portal in selected clips','controlled comfort experiment','unobserved engine-world angles/distances','all movement methods equally comfortable'],
    sourceBank=rel(R / 'sources/source-action-bank-v1.json'),
    protectedBaselineMatched=True, measuredNewVoiceSeconds=None,
    movingAnnotationApproved=False, finalNarratedCoverageApproved=False,
    currentMixedAsrApproved=False, allFinalPixelsApproved=False,
    humanListeningApproved=False, humanPronunciationApproved=False, publicRightsApproved=False,
    pairedScriptHashes=[dict(path=rel(R / f'script/{name}.{lang}.json'), sha256=sha(R / f'script/{name}.{lang}.json'))
                       for name in ['narration','additions'] for lang in ['ko','en']]))

# This is a synthesis request, not a final delivery manifest. Remove inherited
# baseline publishing/QA approvals instead of implying that the new revision passed.
prepared = read(R / 'tts-manifest-v1.json')
tts_manifest = {k: prepared[k] for k in ['schemaVersion','slug','title','status','paths','tts'] if k in prepared}
tts_manifest['paths'] = {k: prepared['paths'][k] for k in ['script','scriptEn']}
tts_manifest['editing'] = dict(exampleSeconds=0, narrationPlacement='continuous-across-example-and-explanation')
tts_manifest['revisionOf'] = rel(ROOT / 'projects/motion-sickness-games/project.json')
tts_manifest['scope'] = 'Three additions only;14approved PCM and all old words/order are preserved. No upload, schedule or final QA approval.'
(R / 'tts-manifest-v1.json').write_text(json.dumps(tts_manifest, ensure_ascii=False, indent=2)+'\n', 'utf-8')
request = dict(schemaVersion=1, slug='motion-sickness-games', recordedAt=now,
    manifest=rel(R / 'tts-manifest-v1.json'), scriptReview=rel(review_path),
    total=3, paragraphs=15, pairedWholeTextReview=True, overviewPromiseReview=True,
    baselineApprovedPcmRegeneration=0, baselinePcmCount=14, protectedInputs=protected,
    preparedOnly=True, modelLoaded=False, actualOwnGpuJobs=0, researchManipulations=0,
    outputDir=tts_manifest['tts']['outputDir'],
    scenes=[dict(id=s['id'], title=s['title'], text=' '.join(s['lines']),
                 path=tts_manifest['tts']['outputDir']+'/chunks/'+s['id']+'-scene.wav')
            for s in additions['ko']['scenes']],
    next='Single serialized approved-venv cooperative handoff; verify actual exit and exact original research restoration; then whole3+complete15context ASR before measured allocation.')
save(R / 'narration-tts-request-v1.json', request)

plan = read(OLD / 'measured-additive-plan-v1.json')
games = [
    dict(gameId='powerwash-simulator', gameTitle='PowerWash Simulator', sourceId='PF5L_2g9UVQ',
         sourceUrl='https://www.youtube.com/watch?v=PF5L_2g9UVQ',
         prerequisite='Use a water jet to remove visible dirt; Aim Mode separates nozzle direction from viewing.',
         claim='A tool can aim within a temporarily stable background; viewing movement remains available.',
         narrationScenes=['00a','01','03','05','09','11'], beforeActionAfter='Dirty surface → nozzle/jet follows surface → visible cleaned strip.',
         comparisonGames=['Portal2','Half-Life:Alyx'], footageAdopted=True, narratedExample=True,
         retainedBaselineReview=rel(OLD / 'final-pixel-direct-review-v2.json')),
    dict(gameId='talos-principle-2', gameTitle='The Talos Principle2', sourceId='6slinvkF0Rs',
         sourceUrl='https://www.youtube.com/watch?v=6slinvkF0Rs',
         prerequisite='Read a puzzle target using its walls/floor; official trailer shots are separate actions.',
         claim='Changing viewing direction still requires recognizable spatial cues afterward.',
         narrationScenes=['06b','07'], beforeActionAfter='Platform view → upward view or separate changed room shot → read walls/floor/device.',
         comparisonGames=['Portal2'], footageAdopted=True, narratedExample=True,
         retainedBaselineReview=rel(OLD / 'final-pixel-direct-review-v2.json')),
    dict(gameId='portal-2', gameTitle='Portal2', sourceId='yFRbGppLaUI',
         sourceUrl='https://www.youtube.com/watch?v=yFRbGppLaUI',
         prerequisite='A cube directs a laser or activates a floor button; room landmarks identify targets.',
         claim='Held-object manipulation and viewing can move together, unlike independent nozzle aiming.',
         narrationScenes=['07b','11b'], beforeActionAfter='Cube/room targets → viewpoint and held cube change → device/button indicator state changes in separate excerpts.',
         comparisonGames=['PowerWash Simulator','The Talos Principle2'], footageAdopted=False, narratedExample=False,
         selectedForPlannedEdit=True, bankActions=[a for a in bank['actions'] if a['sourceKey']=='portal2']),
    dict(gameId='half-life-alyx', gameTitle='Half-Life:Alyx', sourceId='LTLotwKpLgk',
         sourceUrl='https://www.youtube.com/watch?v=LTLotwKpLgk',
         prerequisite='Yellow curve/feet select a travel destination; hands remove obstructing boards.',
         claim='Destination selection, reading the arrival direction and hand manipulation are separate responsibilities.',
         narrationScenes=['08b','11b'], beforeActionAfter='Yellow destination → changed position by door → grip/remove boards and read room landmarks.',
         comparisonGames=['PowerWash Simulator','Portal2'], footageAdopted=False, narratedExample=False,
         selectedForPlannedEdit=True, bankActions=[a for a in bank['actions'] if a['sourceKey']=='alyx']),
]
for game in games:
    game.update(normalSpeedCandidatePlaybackExecuted=True,
        finalMovingPixelsReviewed=False, captionAndUiClearanceReviewed=False, mixedAudioReviewed=False,
        sourceAudioUsed=False, finalPublicRightsApproved=False)
save(R / 'planning/game-example-coverage.json', dict(schemaVersion=1, recordedAt=now, minimumGames=4,
    plannedDistinctGames=4, finalNarratedDistinctGamesApproved=False, games=games,
    commonPrinciple='Preserve the task while separating manipulation, viewing, travel and added effects; retain orientation clues and understandable reversible controls.',
    differences='Mouse/nozzle aiming, puzzle room/held cube responsibilities and VR destination/hand interaction are not interchangeable input schemes.',
    retainedSourceIntervals=[x for x in plan['cuts'] if x.get('classification')=='actual-existing-game-action'],
    nativeBank=rel(R / 'sources/source-action-bank-v1.json'), actualFinalRatioApproved=False,
    finalMinimumFourGamesApproved=False, originalPcmRegenerated=0))
save(R / 'sources/game-candidates.json', dict(schemaVersion=1, recordedAt=now, candidates=games,
    selectionBasis='Actual1x candidates/endpoints plus122native samples,51fine transition samples and95reframed samples directly read; not title count alone.',
    rejectedOrHeld=[dict(game='Alyx', reason='Dark/combat and organ/jar interaction require unnecessary rules and obscure beginner landmarks.'),
                    dict(game='Portal2', reason='Ceiling/upward inspection and unobserved player portal traversal excluded from claims.'),
                    dict(game='Sea of Thieves/Halo/Minecraft/Slime Rancher', reason='Unresolved relevant source clarity/permission or link-promotion conditions; Valve official examples are clearer within current requirements.')],
    rights=bank['rights'], priorUse=bank['priorUse'], sourceAudioUsed=False,
    finalNarrationTimedCutsApproved=False, finalPublicRightsApproved=False))

c = read(R / 'latest-checkpoint.json')
c.update(recordedAt=now, stage='three-paired-insertions-reviewed-ready-for-approved-voice-measurement',
         scriptDirectReviewApproved=True, currentDuplicateCheckPassed=True,
         next='Fresh resource/CIM check, one owned serialized TTS request; original research boundary/resume verified on success or failure.')
(R / 'latest-checkpoint.json').write_text(json.dumps(c, ensure_ascii=False, indent=2)+'\n', 'utf-8')
qpath = ROOT / 'production/batches/cross-game-example-coverage-review/queue.json'
q = read(qpath)
q['currentMotionReview'].update(currentCheckpoint=rel(R/'latest-checkpoint.json'),
    pairedScriptReview=rel(review_path), newNarrationScenes=3, newNarrationParagraphs=15,
    retainedPcmCount=14, sourcePlanningApproved=True,
    stage='ready-for-single-approved-voice-measurement', finalFourGameApproval=False)
q['updatedAt'] = now
qpath.write_text(json.dumps(q, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(reviewed=True, newKoEnParagraphs=15, newScenes=3, protectedInputs=len(protected),
                     preservedPcm=14, finalFourGameApproval=False, modelLoaded=False)))
