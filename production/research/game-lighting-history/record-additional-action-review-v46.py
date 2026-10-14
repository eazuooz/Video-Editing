"""Record completed v44 acquisition and directly read candidate samples.

This is observation evidence, not a final footage, motion, ratio or upload gate.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os, psutil

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stamp = lambda: datetime.now(timezone.utc).isoformat()

def write(p, j):
    t = p.with_name(p.name + '.writing-' + str(os.getpid()))
    t.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    t.replace(p)

execution = ROOT / 'production/research/game-lighting-history/local/episode04-additional-action-v44/execution.json'
state = read(execution)
assert state['status'] == 'candidate-windows-and-samples-ready'
assert len(state['completed']) == 2 and state['current'] is None
old = read(P / 'additional-action-browser-progress-v44.json')
pid = old['worker']['pid']
try:
    worker = psutil.Process(pid)
    same = abs(worker.create_time() - old['worker']['createTime']) < .01
except psutil.NoSuchProcess:
    same = False
assert not same, 'Do not record a live acquisition as completed.'

findings = {
    'nanite-editor-goldcoast2024': {
        'directlyReadBoards': 17,
        'candidateLocalIntervalsSeconds': [
            {'inOut': [24, 42], 'visible': 'Draw-spline controls and road shape, followed by a mask visualization.', 'classification': 'recorded-engine-editor-operation', 'exactMotionAndCropPending': True},
            {'inOut': [96, 136], 'visible': 'Barrier camera, cyan wireframe, triangle-color debug view and normal shading.', 'classification': 'recorded-engine-viewport-operation', 'exactMotionAndCropPending': True},
            {'inOut': [180, 217], 'visible': 'Courtyard mask visualization followed by shaded courtyard and animated people.', 'classification': 'recorded-engine-viewport-operation', 'exactMotionAndCropPending': True},
            {'inOut': [306, 350], 'visible': 'Console/menu selection and different NoDerivativeOps / PixelProgrammable debug views.', 'classification': 'recorded-engine-viewport-operation', 'exactMotionAndCropPending': True},
            {'inOut': [372, 389], 'visible': 'Silver and rusty car material appearances.', 'classification': 'recorded-engine-material-operation', 'exactMotionAndCropPending': True}
        ],
        'excludedOrNotAllocated': [
            {'inOut': [0, 24], 'reason': 'Large spline-mesh world card occludes the scene.'},
            {'inOut': [48, 96], 'reason': 'Long held spline/barrier views; action duration has not been established.'},
            {'inOut': [138, 180], 'reason': 'Mesh asset is mostly held; do not count a long static display as an operation.'},
            {'inOut': [222, 276], 'reason': 'NaniteGPUDrivenMaterials lecture slide is explanation.'},
            {'inOut': [354, 372], 'reason': 'ManagingPipelineNanite card obscures the view.'}
        ],
        'scopeLimits': ['Different debug modes have different color semantics.', 'Material appearance changes do not establish a ray or reconstruction toggle.', 'No claim that every mode is a visibility buffer.']
    },
    'mobile-profile-shader-editor2024': {
        'directlyReadBoards': 12,
        'candidateLocalIntervalsSeconds': [
            {'inOut': [0, 16], 'visible': 'Texture asset and texture-group dropdown selection.', 'classification': 'recorded-editor-operation', 'exactMotionAndCropPending': True},
            {'inOut': [30, 50], 'visible': 'Device Profiles list fills, Android profile is selected and details open.', 'classification': 'recorded-editor-operation', 'exactMotionAndCropPending': True},
            {'inOut': [66, 116], 'visible': 'Texture LOD groups and console-variable categories are opened and scrolled.', 'classification': 'recorded-editor-operation', 'exactMotionAndCropPending': True},
            {'inOut': [132, 150], 'visible': 'Platform Stats columns and missing offline-compiler warning.', 'classification': 'candidate-short-editor-operation', 'exactMotionAndCropPending': True},
            {'inOut': [234, 260], 'visible': 'Fortnite Release-31.00 mobile developer profiling scene: camera traverses surface variants with live frame graph and mobile controls.', 'classification': 'official-existing-game-developer-demonstration', 'exactMotionAndCropPending': True}
        ],
        'excludedOrNotAllocated': [
            {'inOut': [18, 30], 'reason': 'Presenter split obscures the editor.'},
            {'inOut': [54, 66], 'reason': 'Presenter split.'},
            {'inOut': [120, 132], 'reason': 'Presenter split.'},
            {'inOut': [150, 162], 'reason': 'Presenter split.'},
            {'inOut': [174, 180], 'reason': 'ARM compiler web page/setup is not the requested rendering action.'},
            {'inOut': [192, 228], 'reason': 'Static FeatureLevelSwitch diagram, then presenter, is explanation.'},
            {'inOut': [264, 290], 'reason': 'Presenter composition changes; no exact endpoint/crop approval yet.'}
        ],
        'scopeLimits': ['Device settings alone do not prove measured GPU time or tile-memory traffic.', 'The Fortnite developer test is not ordinary game-map gameplay.', 'Source frame-time values are source measurements, not measurements on this workstation.']
    }
}
sources = []
for source in state['completed']:
    assert source['wholeDownloadedWindowDecodeExit'] == 0
    assert len(source['boards']) == findings[source['slug']]['directlyReadBoards']
    boards = []
    for board in source['boards']:
        assert sha(ROOT / board['path']) == board['sha256']
        boards.append({**board, 'directlyViewed': True, 'reviewScope': 'Every sample board was directly read; sampled frames do not approve all moving pixels.'})
    sources.append({
        'id': source['id'], 'title': source['title'], 'url': source['url'],
        'media': source['media'], 'sha256': source['sha256'],
        'durationSeconds': float(source['probe']['format']['duration']),
        'originalSourceWindow': source['requestedSourceWindow'],
        'wholeDownloadedWindowDecodeExit': 0, 'boards': boards,
        **findings[source['slug']],
        'sourceStartOffsetVerified': False, 'allMotionReviewed': False,
        'rightsApproved': False, 'recentUseCheckPassed': False,
        'finalUseApproved': False, 'localOnly': True
    })
record = {
    'recordedAt': stamp(), 'status': 'acquisition-complete-all29-candidate-boards-read-exact-action-review-pending',
    'execution': {'path': execution.relative_to(ROOT).as_posix(), 'sha256': sha(execution), 'actualStatus': state['status'], 'endedAt': state['endedAt']},
    'sessionId': 37029, 'sessionCompletionObserved': True, 'sessionExitCode': 0,
    'originalWorker': old['worker'], 'sameWorkerAlive': False,
    'sources': sources,
    'browserPlaybackObservations': [
        {'id': 'nZlVkI3j7Xs', 'url': 'https://www.youtube.com/watch?v=nZlVkI3j7Xs&t=1475s', 'observedTimes': [1488.17731, 1527.927978, 1586.643246], 'rate': 1, 'muted': True, 'before': 'Populated Device Profiles list.', 'after': 'Android Texture LOD Settings, then Platform Stats.', 'allIntermediateMotionReviewed': False},
        {'id': 'nZlVkI3j7Xs', 'url': 'https://www.youtube.com/watch?v=nZlVkI3j7Xs&t=1684s', 'observedTimes': [1705.474265, 1721], 'rate': 1, 'muted': True, 'finding': 'Fortnite developer profiling camera traverses material surfaces; frame graph, mobile buttons and Release-31.00 build identifier visible.', 'allIntermediateMotionReviewed': False}
    ],
    'rejectedOfficialVideo': {
        'id': 'eguKZyaDyQM', 'title': 'NTE official announcement, 2024 development build',
        'observedNormalRateTimes': [29.361872, 73.439047, 190.142172, 335.135403],
        'visible': 'City movement, combat and driving.',
        'rightsPrimaryUrl': 'https://nte.perfectworld.com/en/article/news/gamebroad/20250515/256468.html',
        'rightsDocumentDate': '2025-05-15',
        'reason': 'Guidelines prohibit direct copying/sampling official videos and require contact for commercial use. No permission established.',
        'mediaDownloaded': False, 'finalUseApproved': False, 'developerContactSent': False
    },
    'physicalFramingPrepared': {
        'ko': 'projects/game-lighting-history-04/script/physical-part-framing.ko.v45.json',
        'en': 'projects/game-lighting-history-04/script/physical-part-framing.en.v45.json',
        'paragraphPairs': 5, 'ttsProduced': False
    },
    'cpuThreads': 2, 'gpuJobs': 0, 'newTtsStarted': False,
    'original87AndAdded24Regenerated': False, 'newFinalRenderStarted': False,
    'newGitImages': 0, 'allFinalPixelsReviewed': False, 'bodyRatioApproved': False,
    'uploaded': False,
    'next': 'Approve exact non-overlapping action ranges/crops and matching native observation guides; finish independent physical-part framing; safe single GPU handoff for only new narration; measured final timelines/mixed review/pair/pixels/collection/private delivery.'
}
target = P / 'additional-action-direct-review-v46.json'
assert not target.exists()
write(target, record)
cp = ROOT / 'production/research/game-lighting-history/checkpoint.json'
j = read(cp)
j['episode04AdditionalActionReviewV46'] = {'record': target.relative_to(ROOT).as_posix(), 'sha256': sha(target), 'sessionId': 37029, 'sessionExitCode': 0, 'sameWorkerAlive': False, 'candidateBoardsDirectlyRead': 29, 'finalUseApproved': False, 'newTtsStarted': False}
j['episode04AdditionalActionV44']['latestVerification'] = target.relative_to(ROOT).as_posix()
j['episode04AdditionalActionV44']['actualWorkerAlive'] = False
j['episode04AdditionalActionV44']['current'] = None
j['episode04AdditionalActionV44']['completed'] = 2
j['ownedActiveWork'] = {'type': 'direct-source-review-and-additive-script-preparation', 'ownedMediaWorkersRunning': 0, 'ownedGpuWorkersRunning': 0, 'next': record['next']}
j['nextAction'] = record['next']
j['updatedAt'] = stamp()
write(cp, j)
print(json.dumps({'record': target.relative_to(ROOT).as_posix(), 'sessionExitCode': 0, 'boardsDirectlyRead': 29, 'uploaded': False}))
