"""Prepare three independent bilingual insertions, preserving every current scene/PCM."""
import bisect
import copy
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OLD = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
NODE = Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def rel(p):
    return p.resolve().relative_to(ROOT).as_posix()

def save(p, x):
    assert not p.exists(), 'Preserve already prepared/executed state: ' + str(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', 'utf-8')

subprocess.run([str(NODE), 'scripts/review-video-duplicates.cjs', 'motion-sickness-games', '--check'], cwd=ROOT, check=True)
pre = read(R / 'source-preflight-v1.json')
review = read(R / 'native-and-clearance-direct-review-v1.json')
assert review['native']['allDisplayedSamplesDirectlyRead'] and review['clearanceMock']['allDisplayedSamplesDirectlyRead']
for x in pre['protectedBaseline'] + pre['sources']:
    assert sha(ROOT / x['path']) == x['sha256'], x['path']
pts_dir = ROOT / 'shared/output/cross-game-example-coverage/motion/native-preflight-v1'
spec = {
    'portal2': (30000, [(16, 40, 'portal-aim'), (58, 62, 'portal-room-reference'),
                       (64, 68, 'portal-device-reference'), (70, 82, 'portal-cube-and-device'),
                       (84, 99, 'portal-cube-button')]),
    'alyx': (60000, [(49, 52, 'alyx-destination'), (54, 69, 'alyx-boards-and-arrival'),
                    (109, 114, 'alyx-locker-orientation')]),
}
actions = []
for key, (tb, windows) in spec.items():
    pts = read(pts_dir / (key + '-native-pts.json'))['pts']
    pts = [int(x) for x in pts]
    assert all(b - a == 1001 for a, b in zip(pts, pts[1:]))
    for start, end, aid in windows:
        first = bisect.bisect_left(pts, start * tb)
        stop = bisect.bisect_left(pts, end * tb)
        assert first < stop < len(pts)
        actions.append(dict(id=aid, sourceKey=key, sourceFirstFrame=first,
            sourceEndExclusiveFrame=stop, sourceFirstPts=pts[first], sourceEndExclusivePts=pts[stop],
            sourceIn=pts[first] / tb, sourceOut=pts[stop] / tb, frames=stop-first,
            seconds=(pts[stop]-pts[first]) / tb, nativeTimeBase=f'1/{tb}', nativePtsStep=1001,
            speed=1, loop=False, slowdown=False, sourceAudio=False,
            exactInOutDerivedFromFullNativePts=True, selectedSamplePixelsReviewed=True,
            entireContinuousNativePixelsApproved=False, actualFinalAllocationFrames=None))
bank = dict(schemaVersion=1, recordedAt=now(), sources=pre['sources'], actions=actions,
    maximumUniqueSeconds=sum(x['seconds'] for x in actions), sourcePlanningApproved=True,
    finalCutAllocationApproved=False, finalCueAndMovingAnnotationApproval=False,
    selectedDirectReview=rel(R / 'native-and-clearance-direct-review-v1.json'),
    historicalMisnamedWindow='portal-traverse means direction-and-cube; no player portal traversal was observed',
    sourceAudioUsed=False, loops=0, slowdowns=0,
    priorUse={'portal2':'Existing game-math lectures; this chapter compares camera/tool roles rather than copying a calculation.',
              'alyx':'Responsive-game-feedback used later125–133 material; selected49–52/54–69/109–114 are separate intervals.'},
    rights=pre['policy'], finalPublicRightsApproved=False,
    excluded={'Portal2':'62–64/68–70 ceiling/upward inspection held to keep beginner targets visible.',
              'Alyx':'Dark48, weapon inspection52–54, organ/jar115–124 and dark/combat164–180 held.'})
save(R / 'sources/source-action-bank-v1.json', bank)

ko = [
    dict(id='07b', title='큐브 조작과 방의 단서를 함께 읽기', lines=[
        '퍼즐에서 방향을 읽는 문제를 포털 투로 이어 보겠습니다. 큐브로 레이저를 장치에 보내거나, 큐브를 발판 위에 놓습니다.',
        '먼저 큐브와 벽의 장치를 찾으세요. 시점을 돌리면 둘의 화면 위치가 바뀝니다. 빨간 표시는 조작할 큐브, 파란 표시는 방의 단서입니다.',
        '큐브를 들고 방향을 바꾸면 큐브도 화면 가운데를 따라갑니다. 앞의 에임 모드에서 도구만 따로 움직이던 장면과 비교해 보세요.',
        '다른 구간에서는 레이저를 장치로 보냅니다. 또 다른 구간에서 큐브를 발판에 놓자 이어진 표시가 파란색에서 노란색으로 바뀝니다.',
        '목표를 조작하려면 보는 방향을 바꿔야 할 때도 있습니다. 바뀐 뒤 장치와 바닥의 단서로 목표를 다시 찾을 수 있어야 하죠.',
        '이 비교는 조작과 시야의 연결을 보여 줍니다. 포털 이동이나 개인의 편안함을 검사한 결과는 아닙니다.',
    ]),
    dict(id='08b', title='이동 목적지와 도착 뒤 손 조작 나누기', lines=[
        '전환 뒤 방향을 읽는 질문을 가상현실 게임 하프라이프 알릭스로 이어 보겠습니다. 이 시연에서는 이동할 곳을 가리킨 뒤 그곳으로 옮깁니다.',
        '노란 곡선과 발자국 표시가 목적지입니다. 선택 뒤 시점이 문 가까이 바뀌면, 문과 벽을 보고 도착한 방향을 다시 읽으세요.',
        '이어지는 구간에서는 길을 막은 판자를 손으로 잡아 치웁니다. 목적지를 고르는 일과, 도착해서 손으로 물체를 다루는 일은 다릅니다.',
        '청소 도구와 큐브, 손의 조작은 서로 다르지만, 작업 대상과 주변 단서를 함께 보여 준다는 질문은 같습니다.',
        '이동 방식 하나만으로 모두의 편안함을 판단할 수는 없습니다. 이동 전후 방향을 이해하는지와 개인의 반응을 따로 확인해야 합니다.',
    ]),
    dict(id='11b', title='네 게임에 같은 세 질문 적용하기', lines=[
        '네 게임을 같은 세 질문으로 정리해 보겠습니다. 무엇을 조작하고, 화면의 무엇이 움직이며, 움직인 뒤 어떤 단서가 남을까요?',
        '청소에서는 물줄기와 표면, 탈로스에서는 벽과 바닥, 포털에서는 큐브와 장치, 알릭스에서는 목적지와 손의 작업을 살펴봤습니다.',
        '게임마다 필요한 움직임은 다릅니다. 한 게임의 조작법을 정답으로 옮기기보다, 작업을 유지하면서 따로 조절할 역할을 찾으세요.',
        '그 역할을 알아볼 수 있게 설명하고 되돌릴 수 있게 만드는 일이, 앞에서 본 카메라 옵션의 설계로 연결됩니다.',
    ]),
]
en = [
    dict(id='07b', title='Read cube manipulation and room landmarks together', lines=[
        'Let us extend the puzzle-orientation question to Portal2. A cube directs a laser toward a device, or is placed on a floor button.',
        'First locate the cube and the wall device. Turning the view changes their screen positions. Red marks the manipulated cube; blue marks a room landmark.',
        'When the player turns while holding the cube, it stays near the center of the view. Compare this with Aim Mode, where the tool moved separately within the screen.',
        'A separate interval directs the laser at the device. In another interval, placing the cube on the button changes the connected indicator from blue to yellow.',
        'Manipulating a target can require changing the viewing direction. The device and floor landmarks must help the player find that target again afterward.',
        'This comparison illustrates the relationship between manipulation and viewing. It does not test portal travel or individual comfort.',
    ]),
    dict(id='08b', title='Separate destination selection from hand interaction after arrival', lines=[
        'Let us carry the orientation-after-transition question into the VR game Half-Life:Alyx. This demonstration points to a destination before moving there.',
        'The yellow curve and footprints mark that destination. After the viewpoint changes to a position near the door, use the door and wall to read the arrival direction.',
        'In the following interval, hands grip and remove boards blocking the path. Choosing a destination differs from manipulating an object by hand after arriving.',
        'A cleaning tool, a cube and hands have different controls. They share the question of showing the work target together with surrounding landmarks.',
        'One movement method cannot establish comfort for everyone. Understanding orientation before and after movement and individual responses need separate checks.',
    ]),
    dict(id='11b', title='Apply the same three questions across four games', lines=[
        'Summarize the four games with the same three questions: What is manipulated, what moves on the screen, and which cues remain afterward?',
        'We examined water and surfaces in cleaning, walls and floors in Talos, cubes and devices in Portal, and destinations and hand tasks in Alyx.',
        'The required movement differs between games. Instead of treating one control scheme as the answer everywhere, find responsibilities that can be adjusted separately while retaining the task.',
        'Explaining those responsibilities clearly and letting players restore their choices connects back to the camera-option design we examined.',
    ]),
]
for lang, additions in [('ko', ko), ('en', en)]:
    baseline = read(OLD / f'script/narration.{lang}.json')
    result = []
    by_after = dict(zip(['07', '08', '11'], additions))
    for s in baseline['scenes']:
        result.append(copy.deepcopy(s))
        if s['id'] in by_after:
            result.append(copy.deepcopy(by_after[s['id']]))
    assert len(result) == 17
    assert [s for s in result if s['id'] not in {'07b', '08b', '11b'}] == baseline['scenes']
    save(R / f'script/narration.{lang}.json', dict(title=baseline['title'], status='paired-direct-review-pending', scenes=result))
    save(R / f'script/additions.{lang}.json', dict(title=baseline['title'] + ' · four-game additions', status='paired-direct-review-pending', scenes=additions))

manifest = copy.deepcopy(read(ROOT / 'projects/motion-sickness-games/project.json'))
manifest.update(status='additive-voice-measurement-only')
manifest['paths'].update(script=rel(R / 'script/additions.ko.json'), scriptEn=rel(R / 'script/additions.en.json'))
manifest['tts'].update(outputDir='shared/output/narration/motion-sickness-games/cross-game-four-additions-v1',
                       filenameStem='motion-sickness-games-cross-game-four-additions-v1', renderMode='scene')
manifest['editing'].update(exampleSeconds=0, narrationPlacement='continuous-across-example-and-explanation')
save(R / 'tts-manifest-v1.json', manifest)
oldplan = read(OLD / 'measured-additive-plan-v1.json')
voice_paths = {x['voice'] for x in oldplan['scenes']}
assert len(voice_paths) == 14
protected = pre['protectedBaseline'] + [dict(path=p, sha256=sha(ROOT / p)) for p in sorted(voice_paths)]
save(R / 'baseline-protected-inputs-v1.json', dict(recordedAt=now(), inputs=protected, pcmCount=14,
    currentVideoId='mBDd9VzSTkA', originalSchedule=pre['originalSchedule'], catFrames=120, memberFrames=600,
    preservedPalette='research-paper-white-v1', preservedBodyRatio='actual60:explanation40', preservedMusic='Nimbus'))
save(R / 'causal-flow-and-annotation-plan-v1.json', dict(schemaVersion=1, recordedAt=now(),
    viewerQuestion='Which movement is needed for the task, and what can players adjust separately?',
    overviewReuse='Retain existing four-sentence25.116-second00a: cleaning aim/view → puzzle orientation cues → understandable/resettable options. New cases deepen those existing steps, without a four-title opening montage.',
    retainedScenes=14, retainedWordingAndOrder=True, retainedPcm=14,
    insertions=[
        dict(id='07b', after='07', before='08', previousResult='Changed viewing directions need recognizable room clues.',
             newQuestion='How does a held object connect manipulation to viewing?', sourceKeys=['portal2'],
             prerequisite='Cube redirects laser or activates a floor button.',
             comparison='PowerWash independent tool direction versus Portal held cube coupled with view.',
             annotations='Narration-timed red cube outline/beam direction; blue tracked wall/device landmark. Hide when occluded, no invented world angle.'),
        dict(id='08b', after='08', before='09', previousResult='Transition duration and arrival orientation are separate responsibilities.',
             newQuestion='Can selecting a destination and working after arrival be understood separately?', sourceKeys=['alyx'],
             prerequisite='Yellow curve/feet select a destination; hands remove boards blocking the path.',
             comparison='Independent task manipulation in cleaning/cube/VR hand interaction; different input devices are explicitly distinguished.',
             annotations='Yellow destination marker, blue door/wall landmarks, red working-board/hand target; no engine-world-distance or symptom inference.'),
        dict(id='11b', after='11', before='12', previousResult='Each actual game exposes different task/view responsibilities.',
             newQuestion='Which design questions transfer to a different game?', sourceKeys=[],
             comparison='One spatial comparison of task object → visible movement → remaining orientation cue across all four games.',
             annotations='Independent projected white2.5D comparison scene with meaningful narration-timed changes; a flat shadowed card is insufficient.'),
    ],
    reference='OS4CZkBBbW4', referenceFlow='Individual response → observable screen motion → developer choices → player control/feedback.',
    intentionalDifferences='Independent task-first four-game comparisons; no copied reference footage/voice/whole translation or medical advice.',
    minimumDistinctGames=4, games=['PowerWash Simulator','The Talos Principle2','Portal2','Half-Life:Alyx'],
    finalNarratedCoverageApproved=False, finalMovingAnnotationsApproved=False,
    framing=dict(shiftYPixels=-120, bottomSameFrameBlurPixels=120, fixedCaptionCenter=[960,970], sourcePixelColorsPreserved=True),
    timing='Measure new PCM first; keep14PCM and useful explanations. Native bank is a maximum, not a padded fixed duration. Mix/starts/KOEN/chapters/outro updated together.',
    sourceAudio=False, bodyActualRatio=.6, maximumRatioErrorFrames=1,
    requiredFinalReview=['current whole and complete-context mixed ASR','all final cue/cut and moving annotations','two whole decodes and native PTS','same AAC','four output files','private settings and Git','same09KSTschedule reopened','only matching obsolete-ID deletion']))
save(R / 'latest-checkpoint.json', dict(schemaVersion=1, recordedAt=now(), slug='motion-sickness-games',
    stage='four-game-source-plan-and-three-paired-insertions-prepared-awaiting-direct-text-review',
    baselineVideoId='mBDd9VzSTkA', originalSchedule=pre['originalSchedule'], protectedPcm=14,
    sourcePlanningApproved=True, scriptDirectReviewApproved=False, ttsStarted=False,
    measuredTimingApproved=False, finalRatioApproved=False, currentMixedAudioApproved=False,
    allFinalPixelsApproved=False, qaApproved=False, outputCollected=False,
    actualReplacementVideoId=None, privateSettingsVerified=False, gitDelivered=False,
    scheduleReplacementVerified=False, oldUploadDeleted=False,
    humanListeningApproved=False, publicRightsApproved=False))
print(json.dumps(dict(prepared=True, scenes=3, paragraphs=sum(len(s['lines']) for s in ko),
    koCharacters=sum(len(' '.join(s['lines'])) for s in ko), sourceMaximumUniqueSeconds=bank['maximumUniqueSeconds'],
    preservedPcm=14, modelLoaded=False, gpuJobs=0), ensure_ascii=False))
