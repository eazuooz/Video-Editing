"""Seal the directly read v47 candidates; preserve its corrupt third download."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil

ROOT = Path(__file__).resolve().parents[3]
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, j):
    tmp = p.with_name(p.name + '.writing-' + str(os.getpid()))
    tmp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    tmp.replace(p)

execution = ROOT / 'production/research/game-lighting-history/local/episode04-additional-action-v47/execution.json'
state = read(execution)
assert state['status'] == 'failed-preserve-partial' and len(state['completed']) == 2
try:
    proc = psutil.Process(state['parentPid'])
    assert not any('acquire-episode04-additional-action-v47.cjs' in a for a in proc.cmdline())
except psutil.NoSuchProcess:
    pass

findings = {
    'virtual-texture-editor-goldcoast2024': {
        'boardsRead': 45,
        'candidateLocalIntervals': [
            {'inOut': [0, 35], 'observed': 'Texture asset Virtual Texture Streaming checkbox, material graph and Virtual Color sampler setting.'},
            {'inOut': [96, 120], 'observed': 'Duplicate lower UV path and reconnect the texture input; sampled material stats change from three to four Virtual Texture Stacks.'},
            {'inOut': [192, 225], 'observed': 'Select texture assets, open Convert to Virtual Texture and its dependency dialog. Loading afterward is excluded.'},
            {'inOut': [246, 266], 'observed': 'Open Project Settings and search virtual-texture options; retained only for the exact setting operation.'},
            {'inOut': [452, 467], 'observed': 'Runtime virtual-texture size control changes; reported asset size updates. This is not a shadow-resolution control.'},
            {'inOut': [514, 564], 'observed': 'Several runtime virtual-texture size values and derived virtual-size labels; exact active changes need dense review.'},
            {'inOut': [648, 682], 'observed': 'Viewport Streaming statistics and console operation; no measured workstation performance claim.'},
            {'inOut': [730, 792], 'observed': 'Project Settings virtual texture pool section and Pool Auto Grow in Editor checkbox. Long holds must be trimmed.'},
            {'inOut': [862, 906], 'observed': 'Render Resource Viewer selects distinct Lumen, virtual-shadow and virtual-texture resources; not a single shared kind of page.'},
            {'inOut': [906, 950], 'observed': 'Virtual Texturing statistics, console completion and r.VT.MaxUploadsPerFrame_Streaming. This control limits streamed texture uploads, not frame generation.'},
            {'inOut': [1047, 1069], 'observed': 'Camera moves to a courtyard wall and selects the building. No demonstrated ray toggle or internal latency measurement.'}
        ],
        'exclude': [
            {'inOut': [36, 96], 'reason': 'Considerations slide, blank asset or held graph.'},
            {'inOut': [132, 174], 'reason': 'Mostly held courtyard statistics, not a long demonstrated action.'},
            {'inOut': [226, 244], 'reason': 'Conversion loading/held assets.'},
            {'inOut': [266, 324], 'reason': 'Held settings/viewport.'},
            {'inOut': [324, 394], 'reason': 'Large Runtime Virtual Textures lecture card.'},
            {'inOut': [468, 510], 'reason': 'Drawn grid lecture explanation.'},
            {'inOut': [576, 590], 'reason': 'Held runtime virtual-texture asset.'},
            {'inOut': [606, 646], 'reason': 'Changing the Pie Slices card.'},
            {'inOut': [792, 858], 'reason': 'Held settings, Starting Values card and held rock view.'},
            {'inOut': [960, 1046], 'reason': 'Animated gray/blue page grid is a lecture diagram, not native action footage.'}
        ]
    },
    'vsm-initial-editor-goldcoast2024': {
        'boardsRead': 8,
        'candidateLocalIntervals': [
            {'inOut': [12, 29], 'observed': 'Viewport visualization menu switches to colored Virtual Page view. Exact card-free boundaries and source offset need dense/native review.'},
            {'inOut': [112, 181], 'observed': 'Ferris wheel and its shadow animate; camera moves far then returns near. No isolated cache-cost comparison or speedup is proven.'}
        ],
        'exclude': [
            {'inOut': [0, 12], 'reason': 'Shadow Maps title card.'},
            {'inOut': [29, 41], 'reason': 'World-space title card remains in the view.'},
            {'inOut': [41, 112], 'reason': 'Static vs Dynamic Caching / WPO Disable Distance lecture slide.'}
        ]
    }
}
sources = []
for source in state['completed']:
    notes = findings[source['slug']]
    assert source['wholeDownloadedWindowDecodeExit'] == 0
    assert len(source['boards']) == notes['boardsRead']
    boards = []
    for b in source['boards']:
        assert sha(ROOT / b['path']) == b['sha256']
        boards.append({**b, 'directlyViewed': True})
    sources.append({
        'id': source['id'], 'url': source['url'], 'title': source['title'],
        'media': source['media'], 'sha256': source['sha256'],
        'originalRequestedWindow': source['requestedSourceWindow'],
        'durationSeconds': float(source['probe']['format']['duration']),
        'wholeDecodeExitCode': 0, 'boards': boards, **notes,
        'sourceOffsetVerified': False, 'allMotionReviewed': False,
        'rightsApproved': False, 'recentUseCheckPassed': False,
        'finalUseApproved': False, 'localOnly': True
    })
bad = execution.parent / 'mobile-performance-texture2024.mp4'
failure = {
    'media': bad.relative_to(ROOT).as_posix(), 'sha256': sha(bad),
    'decodeExitCode': state['current']['exitCode'],
    'decodeLog': (execution.parent / 'mobile-performance-texture2024-decode.log').relative_to(ROOT).as_posix(),
    'downloadLog': (execution.parent / 'mobile-performance-texture2024-download.log').relative_to(ROOT).as_posix(),
    'causeObserved': 'Remote HTTP stream ended prematurely at4194272 of160456319 bytes. Download reported completion, but H264 NAL units are corrupt and whole decode exited69.',
    'preserved': True, 'usable': False, 'retried': False,
    'next': 'Do not reuse this file or infer approval. Obtain a new copy only if native review establishes a useful required interval.'
}
record = {
    'recordedAt': datetime.now(timezone.utc).isoformat(),
    'status': 'two-valid-windows-53-sample-boards-read-third-corrupt-preserved',
    'execution': {'path': execution.relative_to(ROOT).as_posix(), 'sha256': sha(execution), 'status': state['status'], 'endedAt': state['endedAt']},
    'sessionId': 30231, 'sameWorkerAlive': False,
    'sources': sources, 'failedSource': failure,
    'sampleReviewLimit': 'All53 sample boards were directly read. Sparse samples are not approval of every intermediate moving frame or final crop.',
    'crossGamePolicy': 'Each independent physical part requires four distinct existing games with complete narrated comparison. These Unreal engine demonstrations are eligible process candidates but do not increase that game count.',
    'newTtsStarted': False, 'newFinalRenderStarted': False, 'newGitImages': 0,
    'allFinalPixelsReviewed': False, 'bodyRatioApproved': False, 'uploaded': False,
    'next': 'Compare normal-speed existing-game candidates for each physical part; finish current duplicate review; approve exact native actions/crops and matching guides; synthesize only new framing/guides through cooperative GPU handoff.'
}
target = ROOT / 'projects/game-lighting-history-04/production/additional-action-direct-review-v48.json'
assert not target.exists()
write(target, record)
cp = ROOT / 'production/research/game-lighting-history/checkpoint.json'
j = read(cp)
j['episode04AdditionalActionReviewV48'] = {'record': target.relative_to(ROOT).as_posix(), 'sha256': sha(target), 'boardsDirectlyRead': 53, 'validWindows': 2, 'corruptWindows': 1, 'finalUseApproved': False}
j['episode04AdditionalActionV47']['latestVerification'] = target.relative_to(ROOT).as_posix()
j['ownedActiveWork'] = {'type': 'native-action-and-game-comparison-review', 'ownedMediaWorkersRunning': 0, 'ownedGpuWorkersRunning': 0, 'next': record['next']}
j['nextAction'] = record['next']
j['updatedAt'] = record['recordedAt']
write(cp, j)
print(json.dumps({'record': target.relative_to(ROOT).as_posix(), 'boards': 53, 'validWindows': 2, 'corruptWindows': 1, 'uploaded': False}))
