"""Bind conservative screen observations to retained narration; prepare only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math

ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
out = O / 'current34-baseline-guide-plan-v2.json'
assert not out.exists()
proposal_path = O / 'current34-baseline-guide-timing-proposal-v1.json'
proposal = read(proposal_path)
timing = read(O / 'current34-measured-timing-plan-v1.json')
baseline = read(ROOT / timing['sourceBaselineTimeline'])
ko = read(O / 'script/current34-combined-v1.ko.json')
mix = read(O / 'current34-mix-execution-v2.json')
assert mix['actualOuterExitCode'] == 0 and mix['workerDead'] and mix['all34RawPcmPlacementsExact']
assert mix['all24BaselineDistributedPcmExact']
for x in mix['protectedInputs']:
    assert sha(ROOT / x['path']) == x['sha256']

rows = []
for row in proposal['scenes']:
    sid = row['id']
    b = next(x for x in baseline['scenes'] if x['id'] == sid)
    script = next(x for x in ko['scenes'] if x['id'] == sid)
    p = row['pointWindow']
    a, z = p['sceneFrameIn'], p['sceneFrameOut']
    # The turquoise point is an approximate visible torso location in the image.
    # It is deliberately not the body's forward/up axis or physical centroid.
    visible = [a, z]
    if sid == '20':
        visible[1] = min(z, math.ceil(b['cues'][4]['end'] * 60))
    red = []
    if sid == '02':
        red = [a + 30, min(z, math.floor(b['cues'][3]['start'] * 60))]
    gold = []
    if sid == '05':
        gold = [math.ceil(b['cues'][2]['start'] * 60), math.ceil(b['cues'][2]['end'] * 60)]
    if sid == '23':
        gold = [math.ceil(b['cues'][2]['start'] * 60), math.ceil(b['cues'][2]['end'] * 60)]
    notes = {
        '02': '관찰점의 위치와 몸의 기울기를 따로 보기',
        '05': '화면의 위와 물체의 위를 구분하기',
        '08': '보이는 몸통 위치 · 월드 축은 측정하지 않음',
        '11': '화면 모습에는 카메라 기준도 포함됩니다',
        '14': '화면의 투영과 물체의 실제 크기를 구분하기',
        '17': '화면 관찰점 · 내부 수치 오차의 측정은 아님',
        '20': '보이는 자세 관찰 · 입력 방식은 미확인',
        '23': '위치와 자세, 화면 기준을 따로 보기'
    }
    anchors = p['keyframes']
    assert len(anchors) == 25
    for x in anchors:
        assert sha(ROOT / x['inspectedImage']) == x['inspectedImageSha256']
    rows.append(dict(**row,
        pointVisibleSceneFrameRange=visible, redScreenDisplacementSceneFrameRange=red,
        goldImageUpSceneFrameRange=gold, guideNote=notes[sid],
        retainedParagraphs=[dict(index=i+1, ko=line, start=c['start'], end=c['end'])
            for i, (line, c) in enumerate(zip(script['lines'], b['cues']))],
        guideMeaning=dict(turquoise='Approximate visible torso image point p.',
            red='Half-second change of the observed image point; includes camera projection and never means forward or velocity in world space.',
            gold='Fixed camera-image up only. Shown only beside narration comparing image/body reference frames.'),
        worldOrBodyAxisOverlay=False, armAxisOverlay=False,
        observedScreenShiftIsInternalNumericDrift=False,
        originalPcmAndDistributedPausesUnchanged=True))
assert len(rows) == 8 and sum(x['frames'] for x in rows) == 21370
data = dict(preparedAt=datetime.now(timezone.utc).isoformat(),
    proposal=rel(proposal_path), proposalSha256=sha(proposal_path),
    measuredTiming=rel(O / 'current34-measured-timing-plan-v1.json'),
    measuredTimingSha256=sha(O / 'current34-measured-timing-plan-v1.json'),
    mixExecution=rel(O / 'current34-mix-execution-v2.json'),
    currentAacSha256=mix['mixAacSha256'], decodedAacSha256=mix['decodedAacSha256'],
    scenes=rows, actualFrames=21370, normalSpeed=1,
    chosenNativeCutsAlreadyReviewed=True, sourceOrAnchorReExtraction=False,
    sourceAudio=False, newTts=0, renderExecuted=False,
    currentNarrationGuideTimingDirectlyReviewed=False, movingFinalPixelApproved=False,
    finalCaptionPixelApproved=False, allIntermediateFramesApproved=False, newImageGit=0,
    visualLimits='Only interpolate manual screen points within observed visible brackets. Hide occlusions and never draw a path across them. No inferred forward/up/arm/world axes, rotation angle, game velocity, controls or internal numeric error.')
out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps(dict(preparedPlan=rel(out), scenes=8, actualFrames=21370,
    renderExecuted=False, worldAxes=False, originalPcmChanged=False)))
