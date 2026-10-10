"""Continue the actual partial record adoption without rebuilding reviewed media."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/game-math-polar-3d'
OUT = PROJECT / 'revision-teaching-clarity-v1'
HISTORY = OUT / 'baseline-records-before-adoption-v1'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def write(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def rel(p): return p.relative_to(ROOT).as_posix()

now = datetime.now(timezone.utc).isoformat()
receipt = OUT / 'final-media-adoption-v3.json'
assert not receipt.exists()
partial = {
    'project.json': '5ca1bff0ef9f277bad4aaac288643bbe03a5e3ebc7752209cc2a02a32ba63aff',
    'production/timeline.json': 'efee1a3e05c78d1672075584364b625432eaae15edfe7344a60eaea51fb21939',
}
for name, expected in partial.items(): assert sha(PROJECT / name) == expected
snapshot = read(OUT / 'baseline-protected-sha-v1.json')
baseline = {v['path']: v['sha256'] for v in snapshot['files']}
for v in snapshot['files']:
    if v['path'] not in {rel(PROJECT / n) for n in partial}:
        assert sha(ROOT / v['path']) == v['sha256'], v['path']
names = ['project.json', 'production/timeline.json', 'production/qa.json',
         'production/delivery-output.json', 'sources/gameplay-cuts.json',
         'sources/game-candidates.json', 'planning/outline.md', 'rebuild.json',
         'publishing/youtube-upload.json']
saved = []
for name in names:
    preserved = HISTORY / name
    assert preserved.is_file()
    expected = baseline.get(rel(PROJECT / name))
    if expected is not None: assert sha(preserved) == expected
    if name not in partial: assert sha(PROJECT / name) == sha(preserved)
    saved.append({'original': rel(PROJECT / name), 'preserved': rel(preserved), 'sha256': sha(preserved)})
failure = OUT / 'final-media-adoption-partial-failure-v3.json'
assert not failure.exists()
write(failure, {'observedAt': now, 'actualExitCode': 1, 'exitObservedChunk': '35889b',
    'error': "KeyError: sourceInFrame; retained annotation plans carry scene boundaries, not native source coordinates",
    'partiallyUpdatedRecords': partial, 'baselineRecords': saved,
    'mediaChangedByAdoption': False, 'recoverOnlyRemainingRecords': True})

pair = read(OUT / 'final-pair-execution-v3.json')
pixels = read(OUT / 'final-pixel-direct-review-v2.json')
flow = read(OUT / 'final-flow-playback-direct-review-v3.json')
audio = read(OUT / 'current-aac-complete-comparison-v2.json')
assert pair['exitCode'] == 0 and pair['currentAudioComparisonPreservedByIdenticalAacAndPcm']
assert pixels['allListedSamplesDirectlyRead'] and pixels['allFinalCueCutPixelsApproved'] and not pixels['unresolved']
assert flow['wholeNormalSpeedPlaybackReachedEnd'] and flow['sampledContinuousFlowApproved'] and not flow['unresolved']
assert audio['all44CompleteContextsDirectlyCompared']
for v in pair['pair']:
    assert sha(ROOT / v['path']) == v['sha256']
    assert v['all54115Pts1500Verified'] and v['wholeDecodeExitCode'] == 0
assert pixels['sourceSha256'] == flow['sourceSha256'] == pair['pair'][1]['sha256']
jobs = [{'scene': '02', 'globalStartFrame': 1669, 'frames': 3403,
         'plan': rel(OUT / 'scene02-editorial-annotations-v3.json')}]
jobs.extend(j for j in read(OUT / 'six-moving-pilots-execution-v4.json')['jobs'] if j['scene'] not in ['11', '16'])
jobs.extend(read(OUT / 'minus-glyph-moving-pilots-execution-v5.json')['jobs'])
jobs.sort(key=lambda j: j['globalStartFrame'])
assert sum(j['frames'] for j in jobs) == 21358
plans = {j['scene']: read(ROOT / j['plan']) for j in jobs}
cuts = read(HISTORY / 'sources/gameplay-cuts.json')
old = {c['scene']: c for c in cuts['cuts']}
native = {}
native['02'] = plans['02']['cuts']
selected08 = read(OUT / 'selected-scene08-execution-v2.json')
assert selected08['exitCode'] == 0
assert sha(ROOT / selected08['sourceCandidate']) == selected08['sourceCandidateSha256']
assert all(p['allNativePtsVerified'] for p in selected08['cuts'])
native['08'] = selected08['cuts']
for sid in ['05', '11', '14', '16', '18']:
    plan = plans[sid]
    assert sha(ROOT / plan['source']) == plan['sourceSha256']
    native[sid] = []
    start = 0
    for s in old[sid]['segments']:
        frame = s['in'] * 60
        assert frame == int(frame)
        native[sid].append({'sourceInFrame': int(frame), 'frames': s['frames'], 'sceneStartFrame': start})
        start += s['frames']
for cut in cuts['cuts']:
    sid = cut['scene']; job = next(j for j in jobs if j['scene'] == sid)
    pieces = native[sid]
    assert sum(p['frames'] for p in pieces) == job['frames']
    assert [{'sceneStartFrame': p['sceneStartFrame'], 'frames': p['frames']} for p in pieces] == [
        {'sceneStartFrame': p['sceneStartFrame'], 'frames': p['frames']} for p in plans[sid]['cuts']]
    segments = [{'in': p['sourceInFrame'] / 60, 'frames': p['frames'], 'seconds': p['frames'] / 60,
        'nativeStartFrame': p['sourceInFrame'], 'nativeEndFrameExclusive': p['sourceInFrame'] + p['frames'],
        'nativeTimebase': '1/15360', 'nativeStartPts': p['sourceInFrame'] * 256,
        'nativeEndPtsExclusive': (p['sourceInFrame'] + p['frames']) * 256,
        'sceneStartFrame': p['sceneStartFrame']} for p in pieces]
    cut.update({'in': segments[0]['in'], 'segments': segments, 'sourceSegments': segments,
        'maxSeconds': job['frames'] / 60, 'annotationPlan': job['plan'],
        'nativeProvenance': rel(OUT / 'selected-scene08-execution-v2.json') if sid == '08' else
            (job['plan'] if sid == '02' else rel(HISTORY / 'sources/gameplay-cuts.json')),
        'inspection': 'First-viewer candidate comparison, native action review, moving annotations and current final cue/cut pixel coverage; original narration preserved.',
        'finalPixelReview': rel(OUT / 'final-pixel-direct-review-v2.json')})
cuts['currentRevisionReviewedAt'] = now
cuts['currentRevisionApprovalScope'] = 'Listed final cue/cut/annotation coverage; human listening and public rights remain pending.'
write(PROJECT / 'sources/gameplay-cuts.json', cuts)
candidates = read(HISTORY / 'sources/game-candidates.json')
candidates['currentRevision'] = {'reviewedAt': now, 'baselineSelectionRetainedAsHistory': True,
    'firstTimeViewerComparison': rel(OUT / 'whole-content-and-source-direct-review-v1.json'),
    'selectedExactNativePlans': [j['plan'] for j in jobs],
    'finalMovingPixelEvidence': rel(OUT / 'final-pixel-direct-review-v2.json'),
    'sourceReuseVsClarity': 'Retain coherent bicycle example; replace unclear actions, narrate colored relations and identify different rides. No loop, slowdown or source audio.',
    'publicRightsApproved': False}
write(PROJECT / 'sources/game-candidates.json', candidates)
outline = PROJECT / 'planning/outline.md'
text = (HISTORY / 'planning/outline.md').read_text(encoding='utf-8')
assert '2026-10-10 공개 전 이해도 수정' not in text
text += '\n## 2026-10-10 공개 전 이해도 수정\n\n원래25.2초 도입과19씬 설명 순서·승인PCM·한영206큐·화이트 설명은 보존했다. 같은 자전거 사례에서 높이와 수평 성분을 나눈 뒤, 방향/자세/카메라를 구별하고 실제 화면 위 색 선과 짧은 라벨로 계산의 의미를 짚는다. 다른 주행 발췌로 바뀌는 지점은 원래 해설과 별도 표시로 구분한다. 화면의 모델 값과 투영 관계를 게임 엔진의 실측 좌표로 주장하지 않는다.\n\n'
for c in read(OUT / 'causal-flow-and-primary-reference-review-v1.json')['chapterChain']:
    text += f"- {c['scene']}: {c['incomingQuestion']} → {c['reasonAndResult']}\n"
text += '\n새 도형은02/05/08/11/14/16/18의 독립 편집 계획에 유지한다. 첫 시청자 후보 비교,44완결음성문맥,현재 모든 자막/컷/도형 표본과 정상1배속 전체 재생의 근거는 revision-teaching-clarity-v1에 있다. 현재 본편실제21358/설명32037은 사용자 강의40:60 예외이며, 원본고양이120/회원600은 제외한다. 사람 청취·발음·공개권리는 계속 미완료다. 새 비공개 설정/Git/예약은 별도 실제 증거가 필요하다.\n'
outline.write_text(text, encoding='utf-8')
qa = {'reviewedAt': now, 'frames': 54115, 'seconds': 54115 / 60, 'fullDecodePassed': True,
    'videos': pair['pair'], 'allPts1500Verified': True, 'identicalReviewedWholeAacAndPcm': True,
    'measurement': pair['measurement'], 'bodyFrames': 53395, 'actualFrames': 21358, 'explanationFrames': 32037,
    'actualShare': .4, 'explanationShare': .6, 'ratioErrorFrames': 0, 'originalIntroFrames': 120,
    'originalMembershipFrames': 600, 'captionCount': 206, 'captionCounts': {'ko': 206, 'en': 206},
    'pixelEvidence': rel(OUT / 'final-pixel-direct-review-v2.json'),
    'normalSpeedFlowEvidence': rel(OUT / 'final-flow-playback-direct-review-v3.json'),
    'mixedAudioEvidence': rel(OUT / 'current-aac-complete-comparison-v2.json'), 'narrationChanged': False,
    'allListedFinalPixelsDirectlyReviewed': True, 'humanListeningApproved': False, 'pronunciationApproved': False,
    'publicRightsApproved': False, 'currentUploadId': None, 'privateSettingsVerified': False,
    'gitDelivered': False, 'scheduled': False}
write(PROJECT / 'production/qa.json', qa)
intended = {rel(PROJECT / n) for n in ['project.json', 'production/timeline.json',
    'sources/gameplay-cuts.json', 'sources/game-candidates.json']}
assert all(sha(ROOT / v['path']) == v['sha256'] for v in snapshot['files'] if v['path'] not in intended)
write(receipt, {'adoptedAt': now, 'status': 'reviewed-local-media-adopted-collection-private-git-schedule-pending',
    'recovery': rel(OUT / 'final-media-adoption-recovery-v4.json'), 'baselineRecords': saved,
    'intentionallyChangedProtectedRecords': sorted(intended), 'allOtherProtectedInputsUnchanged': True,
    'clean': pair['pair'][0], 'captioned': pair['pair'][1], 'narrationChanged': False,
    'humanListeningApproved': False, 'publicRightsApproved': False, 'uploaded': False,
    'gitDelivered': False, 'scheduled': False, 'actualId': None})
write(OUT / 'final-media-adoption-recovery-v4.json', {'completedAt': now,
    'failureEvidence': rel(failure), 'partialTwoRecordsRetained': partial,
    'nativeCoordinatesRecoveredFromExactProvenance': True,
    'retainedClipHashesVerified': True, 'allOtherProtectedInputsUnchanged': True,
    'originalNineBackupsPreserved': saved, 'noMediaRenderOrExtractionOrAsrRepeated': True,
    'reviewedLocalMediaAdopted': True, 'collectionPending': True, 'actualId': None})
qpath = ROOT / 'production/batches/unpublished-teaching-clarity-revision/queue.json'
q = read(qpath)
q['execution']['stage'] = 'polar-local-final-adopted-collection-private-pending'
q['execution']['failedJobs'].append({'actualOuterExitCode': 1, 'exitObservedChunk': '35889b',
    'causeEvidence': rel(failure), 'recoveredBy': rel(OUT / 'final-media-adoption-recovery-v4.json')})
q['execution']['finalMediaAdoption'] = rel(receipt)
write(qpath, q)
print(json.dumps({'reviewedLocalMediaAdopted': True, 'nativeCutFrames': 21358,
    'baselineBackupsPreserved': 9, 'otherProtectedInputsUnchanged': True, 'collectionPending': True}))
