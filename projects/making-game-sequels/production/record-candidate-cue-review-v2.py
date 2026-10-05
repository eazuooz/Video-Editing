"""Record direct visual observations, not final render or publishing approval."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROD = ROOT / 'projects/making-game-sequels/production'
EDIT = PROD / 'measured-edit-v2'
BATCH = ROOT / 'production/batches/sakurai-planning-game-design'
STAMP = datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def relative(path):
    return path.relative_to(ROOT).as_posix()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(rows):
    result = []
    for row in rows:
        actual = sha(ROOT / row['path'])
        assert actual == row['sha256'], row['path']
        result.append({**row, 'localHashVerified': True, 'directlyRead': True,
                       'finalApproved': False, 'gitStorage': 'local-only'})
    return result


extraction = read(EDIT / 'cue-review-local-v1/execution.json')
assert len(extraction['images']) == 475 and len(extraction['sheets']) == 80
assert extraction['exitCode'] == 0 and extraction['completedCuts'] == 84
observations = [
    {'scenes': ['02'], 'imageIndices': [23, 24], 'issue': 'Dark foreground rail hides the center target during the first roughly0.35 seconds of02-p2-action-10-17370-17550.', 'next': 'Inspect the exact native motion and trim/recompose this interval; do not pad with unrelated action.'},
    {'scenes': ['02'], 'imageIndices': [60, 61, 62, 63], 'issue': 'Action12 stairs tail and action13 camera pillar can stop showing the narrated enemy action.', 'next': 'Review the last meaningful native action, not just the static end sample.'},
    {'scenes': ['04'], 'imageIndices': [77, 93], 'observation': 'Staff, sword and Knight footage are individually visible and match the ordered terms in these trial samples. The later own-planning question is a separate white explanation.'},
    {'scenes': ['06'], 'imageIndices': [114, 127, 132], 'issue': 'The spike-preview interval ends with a brief Spring selection/rotation. Preview direction words need exact alignment and cannot prove an installed device or effect.', 'next': 'Align current word timestamps to the native selection boundary without changing approved PCM.'},
    {'scenes': ['06'], 'imageIndices': [150, 151], 'issue': 'The prospective phrase about the following preparation begins before the combat cut ends.', 'next': 'Review sentence intention and exact actual-word/preview boundary; no final timing approval yet.'},
    {'scenes': ['06'], 'imageIndices': [152, 168], 'observation': 'Wall attack, invalid placement, barricade and floor preview/rotation remain distinct. Selected HUD items do not prove placement or damage.'},
    {'scenes': ['06'], 'imageIndices': [193, 201], 'issue': 'A long unvoiced tail contains device preview/invalid placement. Active pixels alone do not justify quota time.', 'next': 'Write independent guided commentary for necessary relevant observations, or remove unneeded tail and obtain related unique action. Preserve all good white explanation and approved PCM.'},
    {'scenes': ['13'], 'imageIndices': [202, 216], 'issue': 'A large overhead foreground beam makes distant enemies and traps small/dark.', 'next': 'Use the separately sampled source-framing proposal and inspect all affected cue motion.'},
    {'scenes': ['13'], 'imageIndices': [217, 250], 'issue': 'Near/far action samples are distinct, but an unvoiced observation tail and the Minecart camera remain limited evidence.', 'next': 'Guide any retained long observation; do not call the upper camera a controlled cart.'},
    {'scenes': ['13'], 'imageIndices': [251, 272], 'observation': 'Near body turn and later distant-path aiming are visible as separate actions. Exact new quiet joins still need final-mix ASR and timing review.'},
    {'scenes': ['08'], 'imageIndices': [288, 301], 'observation': 'ReadyUp blue route ghosts are distinguished from actual combat enemies. Do not treat route previews as fighting enemies.'},
    {'scenes': ['08'], 'imageIndices': [315, 320], 'issue': 'The original top crop removed the counter used by the resource sentence.', 'next': 'The new lower-source crop preserves the left counter in12 targeted samples; review every affected cue and full action before adopting final framing.'},
    {'scenes': ['08'], 'imageIndices': [326, 332], 'observation': 'A sale prompt is visible, but the narration distinguishes the prompt from an actual selling action.'},
    {'scenes': ['10', '12'], 'imageIndices': [352, 475], 'observation': 'Actual combat, wall/floor/overhead selections and conclusions are distinguishable in the sampled ranges; these do not prove internal reuse, intent, costs, optimal strategy or victory.'},
    {'scenes': ['10', '12'], 'imageIndices': [399, 400, 445, 473, 474, 475], 'issue': 'Several final observations continue after the voice. Scene12 ends with about7.5 unvoiced seconds.', 'next': 'Review purposeful observation and guide retained action with independent narration. No idle or quota-only tail approval.'},
    {'scenes': ['08', '12'], 'imageIndices': [301, 405, 420], 'issue': 'Some prospective captions begin around a native shot boundary, with ASS centisecond and60fps rounding to distinguish.', 'next': 'Inspect exact current-PCM and final composite boundary; sampled caption headers alone are not the final sync verdict.'},
]
direct = {
    'schemaVersion': 1, 'reviewedAt': STAMP,
    'scope': 'All475 trial samples on80 six-tile boards directly read through local view_image. Current candidate84 encoded cuts; caption layoutv1, not the laterv2 timings.',
    'execution': relative(EDIT / 'cue-review-local-v1/execution.json'),
    'planSha256': extraction['planSha256'],
    'captionLayoutSha256': extraction['captionLayoutSha256'],
    'images': verified(extraction['images']), 'sheets': verified(extraction['sheets']),
    'directlyReadImages': 475, 'directlyReadBoards': 80,
    'observations': observations,
    'fixedCaptionCenterPx': [960, 970], 'fontPixels': 48,
    'captionPositionMoved': False, 'newGitImages': 0,
    'allFinalCaptionPixelsReviewed': False, 'allMotionReviewed': False,
    'finalTimingApproved': False, 'finalFramingApproved': False,
    'humanWholeListening': 'pending', 'humanPronunciation': 'pending'
}
write(EDIT / 'all-cue-framing-direct-review-v2.json', direct)

target = read(EDIT / 'targeted-framing-v2.json')
assert len(target['images']) == 12
target_review = {
    'schemaVersion': 1, 'reviewedAt': STAMP,
    'images': verified(target['images']), 'directlyReadImages': 12,
    'directlyReadBoards': 2,
    'method': 'Raw versus recomposed native start/middle/end with current literal caption layoutv2;12 images directly read in two local boards.',
    'sourceFramingProposals': [
        {'cut': '08-p3-action-28-26580-26820', 'crop': [0, 252, 1472, 828],
         'observedCounterValues': [11000, 9800, 10200],
         'observation': 'The left resource counter remains above the fixed bottom-center caption; right presenter excluded. Central hotbar details are not all legible, and no universal cost or selection-effect rule is inferred.',
         'sampleCompositionReviewed': True, 'allAffectedCueMotionReviewed': False},
        {'cut': '13-p1-action-49', 'crop': [192, 270, 1056, 594],
         'observation': 'Distant enemies and purple aiming/trap action are larger; upper beam occupies less height. The nearby body remains partially behind captions, so this is not universal character-motion approval.',
         'sampleCompositionReviewed': True, 'allAffectedCueMotionReviewed': False}
    ],
    'sessionId': 3063, 'workerPid': None, 'workerPidDirectlyObserved': False,
    'workerExitCode': 0, 'activeTasks': [], 'doNotRerunExtraction': True,
    'allCaptionPixelsReviewed': False, 'finalFramingApproved': False,
    'newGitImages': 0, 'sourceAudioUsed': False
}
write(EDIT / 'targeted-framing-direct-review-v2.json', target_review)

white_rows = [('01', '01-corrected', 180), ('03', '03-corrected', 1079),
              ('04', '04', 1978), ('05', '05-corrected', 2877),
              ('07', '07', 3776), ('09', '09', 4675), ('11', '11-corrected', 5574)]
white_images = []
for scene, stem, frame in white_rows:
    base = PROD / 'lookdev-local/current13-v1'
    png, ax = base / (stem + '.png'), base / (stem + '.ax.txt')
    white_images.append({'scene': scene, 'previewFrame': frame,
                         'png': relative(png), 'pngSha256': sha(png),
                         'ax': relative(ax), 'axSha256': sha(ax),
                         'directlyRead': True, 'gitStorage': 'local-only'})
write(PROD / 'white-lookdev-direct-review.json', {
    'schemaVersion': 1, 'reviewedAt': STAMP, 'images': white_images,
    'scope': 'Seven independent muted composition previews directly read through CUA browser2/tab50 on owned Vite9222. Guides are not final literal narration captions.',
    'corrections': ['Preserve manual line breaks with textWrap=pre.',
                    'Distinguish production reuse and new player choices with two-way comparison arrows; no causal implication.',
                    'Label both diagram paths as 길A/길B.',
                    'Show returning and first-time players as parallel lanes converging on observations; do not imply one player becomes the other.'],
    'sampleWhiteCompositionReviewed': True, 'finalDiagramPixelsReviewed': False,
    'allFinalCaptionPixelsReviewed': False, 'voiceSynchronized': False,
    'newGitImages': 0, 'cueFactoryApprovalGatesPreserved': True
})

tracks = read(EDIT / 'caption-tracks-v2.json')
assert len(tracks['koRows']) == 278 and len(tracks['enRows']) == 157
cue = next(x for x in tracks['koRows'] if x['index'] == 139)
write(EDIT / 'caption-pcm-boundary-correction-review-v2.json', {
    'schemaVersion': 1, 'reviewedAt': STAMP,
    'scope': 'Literal KO/EN text timing candidates. Clamp recognizer anchors to preserved PCM paragraph bounds; do not display captions across inserted silence.',
    'tracksSha256': sha(EDIT / 'caption-tracks-v2.json'),
    'koCues': 278, 'enCues': 157, 'preservedParagraphs': 52,
    'corrections': tracks['actualPcmBoundaryCorrections'],
    'cue139': cue,
    'historicalCue139': {'startSeconds': 285.17633333333333,
                         'endSeconds': 302.8426666666667,
                         'problem': 'A recognizer onset14ms before the preserved quiet split incorrectly attached the next paragraph caption across inserted observation silence.'},
    'pcmChanged': False, 'captionTextChanged': False, 'captionPositionChanged': False,
    'allCorrectedCuePixelsReviewed': False, 'allFinalTimingApproved': False,
    'newJoinAsrApproved': False, 'newGitImages': 0
})

plan = read(EDIT / 'plan.json')
stage = 'current13-native-cue-and-white-lookdev-reviewed-targeted-framing-and-guided-tails-pending'
next_action = ('Review the corrected cue139 and affected PCM-boundary cues; adopt the resource-counter lower crop and distant-action zoom only after full affected-cue motion review. '
               'Resolve02 rail/tail and06 device-word boundaries. Guide retained long06/13/12 observation tails with independent KO/EN commentary or replace unnecessary time with relevant unique action; preserve all current509.624sPCM and original six white explanations. '
               'Then approve exact frame roles, update mix/scenes/KOEN/chapters/outro together, and perform new final-mix ASR/joins/full pixels/decode/audio QA before collection/private/Git.')
review_rollup = {
    'candidatePlan': relative(EDIT / 'plan.json'), 'status': 'candidate-not-final-approved',
    'scenes': 13, 'paragraphs': 52, 'speechSeconds': 509.624,
    'nativeCuts': 84, 'actualFrames': plan['actualFrames'],
    'explanationFrames': plan['explanationFrames'], 'bodyFrames': plan['bodyFrames'],
    'finalFrames': plan['finalFrames'], 'candidateSeconds': plan['finalSeconds'],
    'roundingErrorFrames': plan['ratioRoundingErrorFrames'],
    'nativeCompile': relative(EDIT / 'native-review-v1/compiled.json'),
    'cueDirectReview': relative(EDIT / 'all-cue-framing-direct-review-v2.json'),
    'targetedFramingReview': relative(EDIT / 'targeted-framing-direct-review-v2.json'),
    'whiteLookdevReview': relative(PROD / 'white-lookdev-direct-review.json'),
    'captionBoundaryCorrectionReview': relative(EDIT / 'caption-pcm-boundary-correction-review-v2.json'),
    'captionTracks': relative(EDIT / 'caption-tracks-v2.json'),
    'captionLayout': relative(EDIT / 'caption-layout-v2.json'),
    'koCues': 278, 'enCues': 157,
    'trialImagesDirectlyRead': 475, 'trialBoardsDirectlyRead': 80,
    'targetedFramingSamplesDirectlyRead': 12, 'whiteLookdevScenesDirectlyRead': 7,
    'allFinalPixelsReviewed': False, 'allMotionReviewed': False,
    'newJoinAsrApproved': False, 'finalTimingApproved': False,
    'bodyRatioApproved': False, 'finalMixBuilt': False, 'rendered': False,
    'qaApproved': False, 'collected': False, 'privateUploaded': False,
    'newGitImages': 0, 'sourceAudioStreams': 0, 'selfCreatedGames': 0,
    'loops': 0, 'slowdown': 0
}
checkpoints = [PROD / 'latest-checkpoint.json', BATCH / 'proof-making-game-sequels/latest-checkpoint.json']
for checkpoint in checkpoints:
    d = read(checkpoint)
    d.update({'updatedAt': STAMP, 'observedAt': STAMP, 'stage': stage,
              'nextAction': next_action, 'measuredEditCandidate': review_rollup,
              'whiteLookdevDirectReview': relative(PROD / 'white-lookdev-direct-review.json')})
    legacy_keys = ['narrationReadback', 'independentContextReadback', 'targetedClarity', 'additiveNarration', 'additionalNarration']
    d.setdefault('historicalPreCurrent13Rollups', {k: d.get(k) for k in legacy_keys})
    d['narrationReadback']['wholeDirectScriptReview'] = True
    d['independentContextReadback'].update({'directReview': True, 'status': 'finished-direct-current-context-review'})
    d['targetedClarity'].update({'candidatesApproved': True, 'status': 'five-current-meaning-clarity-repairs-technically-adopted-human-listening-pending'})
    d['additiveNarration']['wholeNewAsrDirectReview'] = True
    d['additionalNarration']['asrApproved'] = True
    d['narrationApproved'] = True
    d['narrationApprovalScope'] = 'Unmixed current13 narration technical ASR comparison only; final mix/joins and human listening/pronunciation pending.'
    d['execution'].update({'observedAt': STAMP, 'phase': stage, 'status': 'no-active-production-worker',
                           'pid': None, 'sessionId': None, 'alive': False,
                           'activeTasks': [], 'cpuProductionJobs': 0, 'primaryCpuProductionJobs': 0,
                           'gpuSynthesisJobs': 0, 'renderJobs': 0, 'uploads': 0,
                           'commandLine': None})
    write(checkpoint, d)

queue = read(BATCH / 'queue.json')
item = next(x for x in queue['items'] if x['slug'] == 'making-game-sequels')
item.update({'stage': stage, 'updatedAt': STAMP, 'nextAction': next_action,
             'measuredEditCandidate': review_rollup})
item['execution'] = read(checkpoints[0])['execution']
queue.update({'updatedAt': STAMP, 'lastProgressAt': STAMP})
write(BATCH / 'queue.json', queue)

manifest_path = ROOT / 'projects/making-game-sequels/project.json'
manifest = read(manifest_path)
manifest['status'] = stage
manifest['paths']['timeline'] = relative(EDIT / 'plan.json')
manifest['editing']['timingStatus'] = 'measured-candidate-current13-final-cues-framing-and-joins-pending'
manifest['editing']['measuredCandidate'] = review_rollup
manifest['editing']['openingOverview']['measuredSeconds'] = 24.14
manifest['editing']['exampleInterleaving']['reviewStatus'] = 'All475 candidate samples directly read; listed cue/action/framing and unvoiced-tail corrections pending, final pixels not approved.'
manifest['audio']['mixStatus'] = 'Current13 unmixed509.624sPCM technically compared; approved Nimbus preserved. No active synthesis; final mix and new joins pending.'
write(manifest_path, manifest)
print(json.dumps({'reviewedImages': 475, 'targetedImages': 12,
                  'whiteSamples': 7, 'koCues': 278, 'enCues': 157,
                  'stage': stage, 'newGitImages': 0}))
