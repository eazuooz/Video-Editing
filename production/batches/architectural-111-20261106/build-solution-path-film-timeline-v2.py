"""11.05 full lesson picture clock. Default read-only and Pending.

No process, decoder, model, resource query or writes.
Current source/PCM/ASR/mix/MC/guide proofs must exist before final readiness.
"""
from __future__ import annotations
import argparse, bisect, hashlib, importlib.util, json, math, sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROJECT = ROOT / 'projects/shorts-leveldesign-11-05'
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106') / PROJECT.name
SOURCE_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
TOPIC, FPS, RATE = '11.05', 60, 24000
CAPTION_FILE = 'build-solution-path-caption-timing-v6.py'
CAPTION_SHA = '11a2765b208427d2f5a4caa8bfa0958f390adaa062ecc95d73b77208747f3421'
MIX_FILE = 'verified-solution-path-audio-build-v5.py'
MIX_SHA = '0c1d86561745ceca1260a137c57dba0231546a5cf7a1ae547f5b6eb37132a55b'
PINS = {
    'run-solution-path-voice-qa-v6.py': '59618eb71570190ec78cbae98f94b15078cfd852d3325aab7ac10531400d727e',
    'prepare-solution-path-audio-mix-v5.py': '1cfa0c387321c73d3b5442cd25ce1cbe144ea5b1573dc2f40498e887f5b62fc3',
    'solution-path-composition-data-v1.py': 'a3e8dc89206f0c188a9f818d9b07885b2fa50095848596baea33925e1d5a43ab',
    'composite-solution-path-frame-v1.py': '8646cebfc31b77daa939195ec013d7d33c0ac0ee1a926b707e511c5e3aea2f02',
    'solution-path-structure-data-v1.py': '034f3c68ec6df2ff8e7ec310d59240655e7c12b784be501bd336f8613be071d5',
}
SOURCE_PINS = {
    'narration-final-v5.json': 'e3179da81b2a23135eb6a8907ebb6205c14fc2d66e528a37372d491d0ffeaa91',
    'scene-plan-v5.json': '359e1319f550edd370b686da1e2444edeea000a42d8abf8238f2f3252484d517',
    'native-presentation-plan-v5.json': '4cc44c37204d71fcbd5d4f9acb63b2a26ed9f9f2fa171cbe8ed450e727c8ff9b',
    'native-evidence-v4.json': 'acbaa5d35763b3f20c5c6d4075bcb10275517ae125b729e0b765ed738dcd7087',
    'source-footage-v2.json': 'e25b04358a68ceff2ce671d20515f81f474d730a3797620e20b2177399908e24',
    'footage-moving-guides-v1.json': '4d23ed0a3a3cc26471a4aac6be8b465a1a0ff07d687f993b9570fdac1e759425',
    'portrait-audio-format-review-v1.json': 'f2b81e2a030e06f94254d5f73a3bcf8e6e8808ccfa86ca2222a963aaecab36d4',
}
MC_SOURCE = ROOT / 'motion-canvas/src/projects/shorts-leveldesign-11-05'
MC_PINS = {
    'solution-path-structure.tsx': '8d53d55c59e22e897d751a26ecba04cfd86d5e3b0d62b389ee4afd4f2144765a',
    'solution-path-structure-atlas-v2.tsx': 'f9d9deea68efca3cf4e36f3b271a3f52dc05b54d261f73acc183a587a5d3ac3e',
    'project-structure-atlas-v2.ts': '0e1f910da555a149371a8717ab410727b3923f0b96f9832f0701043eebfcb1be',
}
HEADLINE = ['매번 바뀌는 던전,', '출구까지 길은 누가 만들까?']
PHYSICAL = '0fdfd4b196c4daa61a9a2ec01982592c60bb476131178d2002ed04229fadee0b'
MODES = ('construction', 'branches-a', 'branches-b', 'templates-a', 'templates-b', 'threats-a', 'threats-b', 'broken-link')
# Bounds include the actual 5px room-outline stroke. The older component's
# documentary CONTENT_BOXES bottom774 is not used as a clipping/cat contract.
STRUCTURE_CONTENT_BOXES = [[130, 30, 780, 115], [142.5, 169.5, 755, 616], [110, 792, 860, 95]]


class Pending(ValueError):
    pass


def need(value, reason):
    if not value:
        raise Pending(reason)


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def pin(path):
    return dict(path=str(Path(path).resolve()), sha256=sha(path))


def self_source():
    need(sha(__file__) == SOURCE_SHA, 'Imported film builder source changed')


def self_pin():
    self_source()
    return dict(path=str(Path(__file__).resolve()), sha256=SOURCE_SHA)


def bound(row):
    p = Path(row['path']).resolve()
    need(p.is_relative_to(ROOT) or p.is_relative_to(MEDIA), 'Input escaped selected repository/media scope')
    need(p.is_file() and sha(p) == row['sha256'], 'Missing/changed exact input: ' + str(p))
    return p


def same_pin(a, b):
    return (isinstance(a, dict) and isinstance(b, dict) and a.get('sha256') == b.get('sha256')
            and Path(a.get('path', '')).resolve() == Path(b.get('path', '')).resolve())


def module(name, path, expected):
    need(isinstance(expected, str) and len(expected) == 64, 'Pending reviewed helper pin: ' + Path(path).name)
    need(sha(path) == expected, 'Reviewed helper changed: ' + Path(path).name)
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def authority():
    c = read(ROOT / 'shared/publishing/video-production-control.json')['explicitArchitectural111Batch20261106']
    cp, continuation = read(HERE / 'checkpoint.json'), read(HERE / 'continuation.json')
    need(c['status'] not in ('paused', 'stopped', 'cancelled', 'canceled') and c['automaticAdvanceWithinExactList']
         and not c['automaticAdvanceOutsideList'] and read(HERE / 'batch.json')['localFinalReviewOnly']
         and cp['currentTopicId'] == continuation['currentTopicId'] == TOPIC,
         'Current exact111 selected11.05 local authorization required')
    return dict(localFinalReviewOnly=True, currentTopicId=TOPIC)


def nearest(value):
    value = Fraction(value)
    return (value.numerator * 2 + value.denominator) // (2 * value.denominator)


def frame_of_sample(value):
    need(type(value) is int and value >= 0, 'Integer raw sample boundary required')
    return nearest(Fraction(value * FPS, RATE))


def ceil_frame(value):
    need(type(value) is int and value > 0, 'Positive integer raw sample count required')
    return (value * FPS + RATE - 1) // RATE


def source_cut(cut, start_sample, selected_elapsed=Fraction(0)):
    """Cumulative selected-source allocation, placed at the actual body anchor.

    The A/B source-duration cursor does not reset at the intervening narration.
    It never supplies a speech timestamp. Both body endpoint errors stay below
    one output frame, and coverage-constrained PTS sampling visits every input.
    """
    first, last = cut['startFrame'], cut['endFrameExclusive']
    need(type(first) is type(last) is int and 0 <= first < last, 'Exact displayed source frame range required')
    need(type(start_sample) is int and start_sample >= 0, 'Actual integer source-placement sample required')
    need(type(cut['playbackSpeed']) in (int, float) and cut['playbackSpeed'] == 1.0
         and cut['loop'] is False and cut['audioAdopted'] is False and cut['repeatOtherSelectedFrames'] is False
         and cut['fullOriginalAspect'] is True and cut['imageCrop'] is None,
         'Actual source must stay native1x, silent and unreplayed')
    begin = Fraction(start_sample, RATE)
    duration = Fraction((last - first) * 1001, 60000)
    need(isinstance(selected_elapsed, Fraction) and selected_elapsed >= 0, 'Exact cumulative selected-source cursor required')
    end_elapsed = selected_elapsed + duration
    ceiling = lambda x: -((-x.numerator) // x.denominator)
    count = ceiling(end_elapsed * FPS) - ceiling(selected_elapsed * FPS)
    finish = begin + duration
    a = nearest(begin * FPS)
    if Fraction(a + count, FPS) - finish >= Fraction(1,FPS): a -= 1
    if Fraction(a + count, FPS) - finish <= -Fraction(1,FPS): a += 1
    b = a + count
    need(a < b, 'Actual source window quantized to an empty interval')
    error_a, error_b = Fraction(a, FPS) - begin, Fraction(b, FPS) - finish
    need(abs(error_a) < Fraction(1, FPS) and abs(error_b) < Fraction(1, FPS), 'Source boundary error exceeds one output frame')
    result = dict(cutId=cut['id'], sourceRange=[first, last], startSample=start_sample,
                startFrame=a, endFrameExclusive=b, speed=[1, 1], loop=False, sourceFps=[60000, 1001],
                sourceStartTime=[begin.numerator, begin.denominator], sourceEndTime=[finish.numerator, finish.denominator],
                startQuantizationError=[error_a.numerator, error_a.denominator], endQuantizationError=[error_b.numerator, error_b.denominator],
                selectedSourceElapsedStart=[selected_elapsed.numerator,selected_elapsed.denominator],
                selectedSourceElapsedEnd=[end_elapsed.numerator,end_elapsed.denominator],
                sampling='coverage-constrained nearest pinned PTS; cumulative selected-source rational allocation; body placement uses actual PCM anchor; CFR repetitions are not editorial holds')
    indices = [source_index(result,f) for f in range(a,b)]
    errors = [abs(Fraction(f,FPS) - begin - Fraction((i-first)*1001,60000)) for f,i in zip(range(a,b),indices)]
    need(sorted(set(indices)) == list(range(first,last)) and max(errors) < Fraction(1,FPS), 'CFR sampler omitted input frames or exceeds one presentation frame')
    result['sourceIndexSequence'] = indices
    result['cfrCoverage'] = dict(inputFrames=last-first,outputFrames=count,necessaryRepeatedInputFrames=count-(last-first),
        everySelectedInputRepresented=True,editorialReplay=False,maxPresentationError=[max(errors).numerator,max(errors).denominator])
    return result


def source_index(cut, output_frame):
    need(cut['startFrame'] <= output_frame < cut['endFrameExclusive'], 'Outside exact actual-game cut')
    elapsed = Fraction(output_frame, FPS) - Fraction(*cut['sourceStartTime'])
    index = cut['sourceRange'][0] + nearest(elapsed * Fraction(60000, 1001))
    first,last=cut['sourceRange'];j=output_frame-cut['startFrame']
    extra=(cut['endFrameExclusive']-cut['startFrame'])-(last-first)
    need(extra >= 0, 'Normal-speed selected-source allocation cannot omit input frames')
    # Preserve the nearest actual PTS whenever it can still visit each input.
    # At a phase-sensitive endpoint, a <=one-frame timestamp choice prevents
    # dropping frame960; no duration, source speed or PCM is changed.
    return min(first+min(j,last-first-1),max(first+max(0,j-extra),index))


def native_index(section, output_frame):
    need(section['startFrame'] <= output_frame < section['endFrameExclusive'], 'Outside source section')
    n = section['native']
    return n['startFrame'] + (output_frame - section['startFrame'] if n['playback'] == 'native1x' else 0)


def clock_contract(timing, narration):
    need(timing['topicId'] == TOPIC and timing['fps'] == FPS and len(timing['paragraphs']) == 14,
         'Actual current14-paragraph caption clock required')
    clock = timing['audioClock']
    need(clock['rawSampleRate'] == RATE and timing['totalFrames'] == ceil_frame(clock['totalRawSamples'])
         and clock['noAudioTailPadding'] is True, 'Preserve every actual raw sample and final visual ceil')
    position, frame = 0, 0
    for i, row in enumerate(timing['paragraphs'], 1):
        need(row['paragraph'] == i and row['startSample'] == position and row['startFrame'] == frame
             and row['endSample'] > position and row['canonicalKo'] == narration['narrationKo'][i - 1]
             and row['canonicalEn'] == narration['paragraphsEn'][i - 1], 'Current paragraph literal/sample/frame partition differs')
        end_frame = ceil_frame(row['endSample']) if i == 14 else frame_of_sample(row['endSample'])
        need(row['startFrame'] == frame_of_sample(row['startSample']) and row['endFrameExclusive'] == end_frame,
             'Only the common final visual boundary may use ceil; paragraph clocks use actual sample edges')
        position, frame = row['endSample'], row['endFrameExclusive']
    need(position == clock['totalRawSamples'] and frame == timing['totalFrames'], 'Last PCM sample or visual frame was dropped')
    need(len(timing['sentences']) == len({v['sceneId'] for v in timing['sentences']}), 'Unique current complete raw takes required')
    for paragraph in timing['paragraphs']:
        rows = [s for s in timing['sentences'] if s['paragraph'] == paragraph['paragraph']]
        need(rows and ' '.join(s['canonicalKo'] for s in rows) == paragraph['canonicalKo'], 'Raw take texts do not reconstruct this paragraph')
        pos = paragraph['startSample']
        for i, row in enumerate(rows, 1):
            need(row['sceneId'] == f"p{paragraph['paragraph']:03}-c{i:02}" and row['startSample'] == pos
                 and pos < row['endSample'] <= paragraph['endSample'], 'Complete raw take clock/order differs')
            end_frame = ceil_frame(row['endSample']) if row['endSample'] == clock['totalRawSamples'] else frame_of_sample(row['endSample'])
            need(row['startFrame'] == frame_of_sample(row['startSample']) and row['endFrameExclusive'] == end_frame,
                 'Raw take frame clock differs from actual sample endpoints')
            pos = row['endSample']
        need(pos == paragraph['endSample'], 'Raw take clock dropped paragraph samples')
    for language in ('ko', 'en'):
        rows = timing['captions'][language]
        need(rows and len(rows) == len({r['id'] for r in rows}), 'Independent unique authored KO/EN display cues required')
        need(all(type(r['startFrame']) is type(r['endFrameExclusive']) is int
                 and 0 <= r['startFrame'] < r['endFrameExclusive'] <= timing['totalFrames'] for r in rows),
             'Actual whole-word display boundaries required')


def word_event_contract(timing, cut, resolve):
    """Numerical overlap is a placement gate, never moving/speech approval."""
    phrase = '부딪혀 쓰러지죠.'
    spoken = resolve(timing, 13, phrase)
    need(type(spoken.get('startSample')) is type(spoken.get('endSample')) is int
         and spoken['startSample'] < spoken['endSample'], 'Actual complete P13 impact-word edges required')
    begin = Fraction(*cut['sourceStartTime'])
    onset = [begin + Fraction((f - 480) * 1001, 60000) for f in (853, 854)]
    visible_end = begin + Fraction((961 - 480) * 1001, 60000)
    speech = [Fraction(spoken['startSample'], RATE), Fraction(spoken['endSample'], RATE)]
    overlap = max(speech[0], onset[0]) < min(speech[1], visible_end)
    need(overlap, 'Pending actual P13 impact-word/source-event fit; preserve PCM/source1x and choose an explicit picture solution')
    ratio = lambda v: [v.numerator, v.denominator]
    return dict(paragraph=13, cutId='S-HD-B', exactSpokenPhraseKo=phrase,
        actualWordInterval=spoken, sourceLastIntactFrame=853, sourceFirstImpactBurstFrame=854,
        sourceEventOnsetSeconds=[ratio(v) for v in onset], sourceVisibleAftermathEndSeconds=ratio(visible_end),
        sourceObservation='F853 intact; F854 first red/yellow contact burst; later debris is not a successful exit or an internal fatal-state timestamp.',
        numericSpeechOverlapsVisibleEventOrAftermath=overlap, actualMovingSpeechEventReviewed=False,
        actualWordEventAlignmentReviewed=False, automaticSpeechOrActionPass=False)


def plan(timing, narration, cuts, resolve):
    """Author exact current clock into native1x/state-inspection sections."""
    clock_contract(timing, narration)
    paragraphs = {v['paragraph']: v for v in timing['paragraphs']}
    sentences = {p: [s for s in timing['sentences'] if s['paragraph'] == p] for p in paragraphs}
    sections, term_cues, cat_cues = [], [], []

    def add(a, b, p, modes, layout, source_frame, playback='held', reason=None, structure=False, guides=False):
        need(type(a) is type(b) is int and a < b, 'Every authored picture interval must be positive')
        need(playback in ('held', 'native1x') and (playback != 'held' or bool(reason)), 'Purposeful state inspection needs a reason')
        row = dict(id=f'P{p:02}-{len(sections):03}', paragraph=p, kind='native', startFrame=a, endFrameExclusive=b,
                   native=dict(modes=modes, layout=layout, startFrame=source_frame, playback=playback, holdReason=reason),
                   structuralCompanion=structure, reviewedClosedPortGuide=guides, catAllowed=False)
        sections.append(row)

    def play(a, b, p, modes, layout, first, last, reason, structure=False):
        need(0 <= first < last <= 3120, 'Finite actual native source window required')
        count = min(last - first, b - a)
        add(a, a + count, p, modes, layout, first, 'native1x', structure=structure)
        if a + count < b:
            add(a + count, b, p, modes, layout, first + count - 1, reason=reason, structure=structure)

    source = {v['plannedParagraph']: v for v in cuts}
    game = {}; selected_elapsed = Fraction(0)
    for p in (1, 13):
        game[p] = source_cut(source[p], paragraphs[p]['startSample'], selected_elapsed)
        selected_elapsed = Fraction(*game[p]['selectedSourceElapsedEnd'])
        need(game[p]['endFrameExclusive'] < paragraphs[p]['endFrameExclusive'], 'Native HD excerpt does not fit this actual paragraph; never retime')

    for p, row in paragraphs.items():
        a, b = row['startFrame'], row['endFrameExclusive']
        if p in game:
            c = game[p]
            sections.append(dict(id=f'P{p:02}-HD', paragraph=p, kind='actual-game', startFrame=a,
                                 endFrameExclusive=c['endFrameExclusive'], actualGame=c, structuralCompanion=False, catAllowed=False))
            a = c['endFrameExclusive']
        if p == 1:
            play(a, b, p, ['construction'], 'single-player', 480, 3120, '입구·출구 질문을 같은 자체 모형에 연결해 살펴보기')
            for section in sections:
                if section['paragraph'] == 1 and section['kind'] == 'native': section['catAllowed'] = True
            q = sentences[1][1]
            if max(a, q['startFrame']) < q['endFrameExclusive']:
                cat_cues.append(dict(startFrame=max(a, q['startFrame']), endFrameExclusive=q['endFrameExclusive'], pose='puzzled'))
        elif p in (2, 3):
            first = 480 if p == 2 else 480 + (paragraphs[2]['endFrameExclusive'] - paragraphs[2]['startFrame'])
            need(first < 3120, 'Combined same-room source motion exhausted; explicit picture decision needed')
            play(a, b, p, ['templates-a'], 'dual', first, 3120, '같은 방의 구조와 익힐 행동 관계를 살펴보기')
        elif p == 4:
            side = resolve(timing, p, '옆에 이어지는 지형')['startFrame']
            theme = resolve(timing, p, '지역의 분위기가 바뀌면')['startFrame']
            need(a < side < theme < b, 'Actual ordered factor word boundaries required')
            add(a, side, p, ['threats-a', 'threats-b'], 'ab-player', 1680, reason='같은 입력·지형에서 적 위치만 비교')
            add(side, theme, p, ['branches-a', 'branches-b'], 'ab-observer', 0, reason='같은 출구 경로와 서로 다른 옆방 연결 비교')
            play(theme, b, p, ['construction'], 'observer', 3000, 3120, '같은 구조에 적용한 테마 색상 결과 비교')
        elif p == 5:
            play(a, b, p, ['construction'], 'observer', 0, 60, '방 격자·상단 입구와 아직 정해지지 않은 출구 살펴보기', True)
        elif p == 6:
            play(a, b, p, ['construction'], 'observer', 60, 240, '방을 잇는 경로와 맞닿은 경계 살펴보기', True)
        elif p == 7:
            need(b - a > 61, 'Early broken-port source window must remain complete at native speed')
            add(a, a + 21, p, ['branches-a', 'broken-link'], 'ab-observer', 1540, 'native1x')
            add(a + 21, b - 40, p, ['broken-link'], 'dual', 1560,
                reason='맞닿은 실제 닫힌 통로와 계속 요청되는 입력 살펴보기', guides=True)
            add(b - 40, b, p, ['broken-link'], 'dual', 1561, 'native1x')
        elif p == 8:
            reveal = resolve(timing, p, '출구 방으로')['startFrame']
            need(a < reveal < b, 'Actual derived-exit phrase boundary required')
            add(a, reveal, p, ['construction'], 'observer', 239, reason='출구를 정하기 전 경로의 끝 살펴보기', structure=True)
            add(reveal, min(reveal + 1, b), p, ['construction'], 'observer', 240, 'native1x', structure=True)
            if reveal + 1 < b:
                add(reveal + 1, b, p, ['construction'], 'observer', 240, reason='실제 공개된 경로 끝의 출구 방 살펴보기', structure=True)
        elif p == 9:
            switch = sentences[p][2]['startFrame']
            need(a < switch < b, 'Actual side-room contrast sentence boundary required')
            play(a, switch, p, ['construction'], 'observer', 240, 360, '필수 경로 밖에 더해진 방과 연결 살펴보기', True)
            add(switch, b, p, ['branches-a'], 'observer', 360, reason='실제 연결된 옆방과 봉인된 방의 포트 구별', structure=True)
        elif p == 10:
            add(a, b, p, ['templates-a', 'templates-b'], 'ab-player', 1560, reason='같은 양쪽 출입구와 서로 다른 내부 설계안 비교')
        elif p == 11:
            play(a, b, p, ['construction'], 'observer', 360, 450, '후속 적 배치 전 이미 활성화된 템플릿 가시 살펴보기')
        elif p == 12:
            need(b - a > 121, 'Actual same-frame threat comparison needs its complete current native window')
            add(a, a + 61, p, ['threats-a', 'threats-b'], 'ab-player', 1620, 'native1x')
            add(a + 61, b - 60, p, ['threats-a', 'threats-b'], 'ab-player', 1680,
                reason='같은 지형·입력에서 실제 적 트리거 접촉 기록 비교')
            add(b - 60, b, p, ['threats-a', 'threats-b'], 'ab-player', 1681, 'native1x')
        elif p == 13:
            add(a, b, p, ['threats-a', 'threats-b'], 'ab-player', 1680,
                reason='방 연결 검사와 실제 적 트리거 접촉 검사의 차이 살펴보기')
        else:
            add(a, b, p, ['construction'], 'observer', 2880,
                reason='작은 방과 연결·구성 규칙을 같은 실제 모형에서 정리', structure=True)

    for en, ko, meaning, p, sentence in (
            ('Level Chunk', '레벨 조각', '작은 플레이 상황을 담은 방 규모의 묶음', 2, 2),
            ('Solution Path', '출구 연결 경로', '생성기가 입구에서 출구로 이어지게 준비하는 경로', 6, 1),
            ('Room Type', '방 연결 유형', '어느 방향 출입구를 지켜야 하는지 정하는 구분', 7, 2),
            ('Room Template', '방 템플릿', '연결 조건 안에서 고르는 내부 설계안', 10, 2),
            ('Probabilistic Tile', '확률 타일', '추첨 결과에 따라 배치가 달라지는 타일 규칙', 11, 0),
            ('Connectivity', '연결성', '방과 통로가 서로 이어진 성질', 13, 3)):
        speech = sentences[p][sentence]
        start = max(speech['startFrame'], game[p]['endFrameExclusive']) if p in game else speech['startFrame']
        need(start < speech['endFrameExclusive'], 'Actual term definition needs a positive speech interval')
        term_cues.append(dict(startFrame=start, endFrameExclusive=speech['endFrameExclusive'], sourceSceneId=speech['sceneId'],
                              english=en, korean=ko, meaning=meaning))
    result = dict(schemaVersion='11.05-film-picture-plan-v2', topicId=TOPIC, fps=FPS, totalFrames=timing['totalFrames'],
                  audioClock=timing['audioClock'], paragraphs=timing['paragraphs'], sentences=timing['sentences'],
                  captions=timing['captions'], subtitles=timing['subtitles'], sections=sections,
                  termCues=term_cues, catCues=cat_cues, headline=HEADLINE, sourceCuts=list(game.values()),
                  structuralContentBoxes=STRUCTURE_CONTENT_BOXES, actualSpeechTimingReviewed=False,
                  actualMovingCompositeReviewed=False, actualFinalCaptionedMobileReviewed=False, humanReviewed=False)
    result['sourceSpeechTimingWatches'] = [word_event_contract(timing, game[13], resolve)]
    result['sourceKindPolicy'] = dict(actualGame='Spelunky (HD) · 실제 플레이',
        native='Classic 1.1 원리 · 자체 구현', structure='생성 규칙 설명도 · 자체 모형',
        observerPixelVisibilityUnknown=True, onlyReviewedSurfaceException='broken-link/observer/1560/closed-port-10-11 label only',
        abSameNativeFrame=True, greenBrokenRouteMeaning='의도한 입력 경로', noCommercialInternalStateClaim=True)
    validate_plan(result)
    return result


def validate_plan(t):
    need(t['topicId'] == TOPIC and t['fps'] == FPS and t['totalFrames'] == ceil_frame(t['audioClock']['totalRawSamples']), 'Wrong selected clock/topic')
    position = 0
    for section in t['sections']:
        a, b = section['startFrame'], section['endFrameExclusive']
        need(type(a) is type(b) is int and a == position and a < b <= t['totalFrames'], 'Gap/overlap/empty picture section')
        position = b
        if section['kind'] == 'native':
            n = section['native']; first = native_index(section, a); last = native_index(section, b - 1)
            need(0 <= first <= last < 3120 and n['playback'] in ('native1x', 'held'), 'Missing native source tail/retime')
            need(n['playback'] != 'held' or bool(n['holdReason']), 'State inspection cannot be unlabelled padding')
            need(len(n['modes']) == (2 if n['layout'].startswith('ab-') else 1) and len(set(n['modes'])) == len(n['modes']), 'A/B must use distinct same-frame inputs')
            need(n['layout'] in ('single-player','dual','observer','ab-player','ab-observer')
                 and all(mode in MODES for mode in n['modes']), 'Unknown native mode/layout forbidden')
            need(not section['structuralCompanion'] or n['layout'] == 'observer', 'Diagram companion needs one actual observer graph')
            need(not section['catAllowed'] or n['layout'] == 'single-player', 'Large cat requires the approved single-player hero layout')
            need(not ('broken-link' in n['modes'] and last >= 2880 and n['layout'] not in ('observer', 'ab-observer')), 'Late broken player is forbidden')
            if section['reviewedClosedPortGuide']:
                need(n['modes'] == ['broken-link'] and n['layout'] == 'dual' and n['playback'] == 'held' and first == 1560,
                     'Reviewed observer guide cannot extrapolate')
        else:
            need(section['kind'] == 'actual-game' and not section['structuralCompanion'], 'Unsupported picture kind')
            c = section['actualGame']
            need((a, b) == (c['startFrame'], c['endFrameExclusive']) and c['speed'] == [1, 1]
                 and c['sourceFps'] == [60000, 1001] and c['loop'] is False,
                 'Actual HD source clock differs from its common-clock section')
    need(position == t['totalFrames'], 'Visual coverage misses the last raw sample')
    actual = [s['actualGame'] for s in t['sections'] if s['kind'] == 'actual-game']
    need([v['cutId'] for v in actual] == ['S-HD-A', 'S-HD-B'] and [v['sourceRange'] for v in actual] == [[60, 480], [480, 961]], 'Official HD cuts must appear exactly once in order')
    for row in actual:
        indices = [source_index(row, f) for f in range(row['startFrame'], row['endFrameExclusive'])]
        need(indices == row['sourceIndexSequence'] and indices == sorted(indices)
             and sorted(set(indices)) == list(range(*row['sourceRange'])), 'Source frame clock loops, escapes or omits selected input')
    need(sum(len(v['sourceIndexSequence']) for v in actual)==902
         and sum(v['cfrCoverage']['necessaryRepeatedInputFrames'] for v in actual)==1,
         'Cumulative901-frame59.94 source contract requires902 outputframes and one necessary CFR duplicate')
    return dict(completeFramePartition=True, totalFrames=position, actualGameplayCuts=2, sourceSpeed=1,
                cfrInputFrameRepetitionsAllowed=True, editorialReplay=False, noAudioPadding=True)


def term_at(t, frame):
    active = [v for v in t['termCues'] if v['startFrame'] <= frame]
    if not active:
        return None
    row = active[-1]
    return dict(english=row['english'], korean=row['korean'], meaning=row['meaning'],
                presentation='definition' if frame < row['endFrameExclusive'] else 'chip')


def structure_requests(t):
    """Unique source snapshot assets, not a second voice/movie clock."""
    rows = {}
    for section in t['sections']:
        if not section['structuralCompanion']:
            continue
        need(section['kind'] == 'native' and len(section['native']['modes']) == 1,
             'Structural companion requires one current source graph')
        for frame in range(section['startFrame'], section['endFrameExclusive']):
            term = term_at(t, frame)
            if term and term['presentation'] == 'definition':
                continue
            mode, native = section['native']['modes'][0], native_index(section, frame)
            rows[(mode, native)] = dict(mode=mode, nativeFrame=native)
    return [rows[key] for key in sorted(rows)]


def visual_identity(packet, style_inputs):
    """Only fields actually drawn by the frozen structural Node.

    Native frame, phase, templateVariant, player point, input receipt paths and
    non-displayed physical state are excluded from the visual cache key ONLY.
    Every such full source packet still has its own exact alias/fingerprint.
    """
    return dict(styleInputs=style_inputs, sourceKindLabel=packet['sourceKindLabel'],
                rooms=[{k: row[k] for k in ('id', 'label', 'center', 'role', 'entrance', 'exit')} for row in packet['rooms']],
                ports=[{k: row[k] for k in ('a', 'b', 'open', 'role', 'center', 'broken')}
                       for row in packet['ports'] if row['open'] or row['broken']],
                route=[{k: row[k] for k in ('a', 'b')} for row in packet['route']],
                routeMeaning=packet['routeMeaning'], routeLabel=packet['routeLabel'])


def atlas_layout(packets, style_inputs):
    representatives, aliases, seen = [], [], {}
    for packet in packets:
        visual = digest(visual_identity(packet, style_inputs))
        if visual not in seen:
            seen[visual] = len(representatives)
            representatives.append(packet)
        aliases.append(dict(mode=packet['mode'], nativeFrame=packet['nativeFrame'], packetFingerprint=packet['fingerprint'],
                            visualKey=visual, atlasIndex=seen[visual]))
    return representatives, aliases


def structure_job(t):
    self_source()
    for name, expected in MC_PINS.items(): need(sha(MC_SOURCE / name) == expected, 'Reviewed structural MC source changed: ' + name)
    source = module('solution_film_source_structure', HERE / 'solution-path-structure-data-v1.py', PINS['solution-path-structure-data-v1.py'])
    data = source.NativeStructure()
    snapshots = [data.snapshot(row['mode'], row['nativeFrame']) for row in structure_requests(t)]
    style_inputs = [pin(ROOT / 'motion-canvas/src/projects/shorts-leveldesign-11-05/solution-path-structure.tsx'),
                    pin(ROOT / 'motion-canvas/src/projects/shorts-leveldesign-11-05/solution-path-structure-atlas-v2.tsx'),
                    pin(ROOT / 'motion-canvas/src/projects/shorts-leveldesign-11-05/project-structure-atlas-v2.ts')]
    style = read(ROOT / 'projects/shorts-leveldesign-03-02/visual-layout-v1.json')
    for font in style['fontMeasurement']['fontFiles']:
        source.d.checked(font)
        style_inputs.append(font)
    packets, aliases = atlas_layout(snapshots, style_inputs)
    result = dict(schemaVersion='11.05-structure-snapshot-job-v2', topicId=TOPIC, picturePlanFingerprint=t['fingerprint'],
                  assetKind='finite-structural-snapshot-atlas; not native motion or speech timestamps',
                  canvas=[1080, 900], exportFps=60, assetFrames=len(packets), packets=packets, aliases=aliases,
                  renderMode='source-pinned-structural-atlas-v2', projectEntry=str(MC_SOURCE / 'project-structure-atlas-v2.ts'),
                  actualNativeSnapshotCount=len(snapshots),
                  visualCacheIdentity='Only actually drawn graph/label/route/style fields; each actual packet/frame remains separately hash-bound in aliases',
                  inputs=[pin(HERE / 'solution-path-structure-data-v1.py'),
                          pin(ROOT / 'motion-canvas/src/projects/shorts-leveldesign-11-05/solution-path-structure.tsx'),
                          pin(ROOT / 'motion-canvas/src/projects/shorts-leveldesign-11-05/solution-path-structure-atlas-v2.tsx'),
                          pin(ROOT / 'motion-canvas/src/projects/shorts-leveldesign-11-05/project-structure-atlas-v2.ts')] + style_inputs,
                  criticalContentSourceBoxes=STRUCTURE_CONTENT_BOXES, catAllowed=False,
                  nativePixelVisibilityClaim=False, actualSpeechTimingVerified=False, actual375Reviewed=False)
    result['fingerprint'] = digest(result)
    result['outputContract'] = dict(jobPath=str(MEDIA / 'structure-jobs-v2' / result['fingerprint'][:24] / 'structure-job.json'),
        attemptRoot=str(MEDIA / 'structure-attempts-v2'), manifestSchema='11.05-structure-atlas-manifest-v2',
        actualRenderRequired=True, oneBackend='Motion Canvas structural snapshot atlas; no second overlay runtime')
    self_source()
    return result


def verify_atlas(path, t):
    manifest = read(path); job = structure_job(t)
    need(Path(path).resolve().is_relative_to(MEDIA / 'structure-attempts-v2')
         and manifest.get('schemaVersion') == '11.05-structure-atlas-manifest-v2' and manifest.get('complete') is True
         and manifest.get('jobFingerprint') == job['fingerprint'] and manifest.get('picturePlanFingerprint') == t['fingerprint']
         and manifest.get('canvas') == [1080, 900] and manifest.get('assetFrames') == len(job['packets']),
         'Actual current source-bound structural atlas missing/mismatched')
    bound(manifest['job'])
    need(Path(manifest['job']['path']).resolve() == Path(job['outputContract']['jobPath']).resolve()
         and read(manifest['job']['path']) == job, 'Atlas source job differs from freshly recomputed current packets')
    need(len(manifest['frames']) == len(job['packets']), 'Incomplete actual structure atlas')
    need(manifest.get('aliases') == job['aliases'], 'Atlas lost exact per-native-frame packet/visual-cache bindings')
    seen = set()
    for i, (row, packet) in enumerate(zip(manifest['frames'], job['packets'])):
        need(row['atlasIndex'] == i and row['packetFingerprint'] == packet['fingerprint']
             and row['mode'] == packet['mode'] and row['nativeFrame'] == packet['nativeFrame'], 'Atlas frame/source clock differs')
        image = bound(row['image'])
        need(image.is_relative_to(MEDIA / 'structure-attempts-v2') and image.suffix.lower() == '.png'
             and image not in seen, 'Structure image escaped fresh selected atlas output')
        seen.add(image)
    return manifest


def verify_moving_guides(path, t):
    guide = read(path)
    need(guide.get('schemaVersion') == '11.05-reviewed-hd-moving-guides-v1'
         and guide.get('topicId') == TOPIC and same_pin(guide.get('sourceMedia'), t['actualGameSource'])
         and same_pin(guide.get('sourceNarration'), pin(PROJECT / 'narration-final-v5.json'))
         and same_pin(guide.get('sourceFootage'), pin(PROJECT / 'source-footage-v2.json'))
         and guide.get('captionTiming') is None and guide.get('actualSpeechTimingAssigned') is False
         and guide.get('agentMovingSourceInspection') is True and guide.get('humanApproval') is False,
         'Pending reviewed current moving HD guide coverage; isolated inspected frames cannot be auto-interpolated')
    need(Path(path).resolve() == (PROJECT / 'footage-moving-guides-v1.json').resolve()
         and sha(path) == SOURCE_PINS['footage-moving-guides-v1.json'], 'Exact current reviewed guide source required')
    need(guide['sourceCanvas'] == dict(width=1920,height=1080,fpsNumerator=60000,fpsDenominator=1001,
        sampleAspectRatio='1:1',displayAspectRatio='16:9'), 'Full original HD aspect/source rate required')
    bound(guide['inspection'])
    rows = guide.get('sourceFrameRows', [])
    need([v['sourceFrame'] for v in rows] == list(range(60, 961))
         and digest(rows) == guide['sourceFrameRowsSHA256'], 'Exact complete selected source guide clock required')
    visible = []
    for row in rows:
        marks = row.get('marks', [])
        need(len(marks) <= 1, 'One primary actual-game focus at a time')
        for mark in marks:
            need(mark['kind'] in ('ellipse', 'rectangle', 'pointer') and mark['role'] in ('term', 'result', 'problem')
                 and isinstance(mark['labelKo'], str) and bool(mark['labelKo'].strip()), 'Source-bound editorial guide required')
            points = mark['sourcePoints']
            need(isinstance(points, list) and len(points) >= 2
                 and all(len(p) == 2 and all(type(v) in (int, float) and math.isfinite(v) for v in p)
                         and 0 <= p[0] <= 1920 and 0 <= p[1] <= 1080 for p in points), 'Actual guide escaped full source aspect')
            visible.append(row['sourceFrame'])
    need(any(all(f + offset in visible for offset in range(6)) for f in visible), 'A one-frame flash is not reviewed moving guide coverage')
    need(len(visible) == 217 and guide['temporalCoverage']['activeFrames'] == len(visible)
         and guide['temporalCoverage']['explicitOffFrames'] == 901 - len(visible)
         and guide['temporalCoverage']['frameInterpolation'] is False and guide['temporalCoverage']['extrapolation'] is False,
         'Reviewed visible/off source coverage differs')
    need(guide['impactObservation']['lastObservedIntactCharacterFrame'] == 853
         and guide['impactObservation']['firstObservedImpactBurstFrame'] == 854
         and guide['impactObservation']['exitSucceeded'] is False,
         'Current observed impact limits differ')
    return guide


def prepare(caption_timing=None, audio_build=None, structure_atlas=None, moving_guides=None):
    try:
        self_source()
        authority()
        for name, expected in SOURCE_PINS.items():
            need(sha(PROJECT / name) == expected, 'Current source changed: ' + name)
        for name, expected in PINS.items(): need(sha(HERE / name) == expected, 'Frozen source/helper changed: ' + name)
        for name, expected in MC_PINS.items(): need(sha(MC_SOURCE / name) == expected, 'Reviewed structural MC source changed: ' + name)
        need(caption_timing and audio_build, 'Pending current blind-ASR caption timing and accepted actual mix')
        caption = module('solution_film_caption_current', HERE / CAPTION_FILE, CAPTION_SHA)
        mix_api = module('solution_film_mix_current', HERE / MIX_FILE, MIX_SHA)
        try:
            checked = caption.verify_existing(caption_timing)
            mix = mix_api.verified_audio_build(audio_build)
        except (caption.Pending, mix_api.Pending) as error:
            raise Pending(str(error)) from error
        timing = checked['timing']
        need(mix['rawVoiceFingerprint'] == checked['voice']['fingerprint']
             and mix['rawVoice'] == checked['voice']['aggregateWav'] and mix['canonicalTiming'] == checked['voice']['timing']
             and mix['mixWav']['frames'] == timing['audioClock']['totalRawSamples'] * 2
             and mix['mixWav']['sampleRate'] == 48000 and mix['mixWav']['channels'] == 2,
             'Actual accepted mix clock differs from the exact selected raw voice')
        need(same_pin(timing['inputs']['narration'], pin(PROJECT / 'narration-final-v5.json'))
             and timing['schemaVersion'] == '11.05-selected-caption-timing-v6'
             and mix['schemaVersion'] == '11.05-audio-build-v5', 'Exact current caption6/mix5 source versions required')
        footage = read(PROJECT / 'source-footage-v2.json')
        rows = footage['sources']; need(len(rows) == 1, 'Exact current official source set required')
        source = rows[0]; bound(source['sourceMedia'])
        def actual_interval(*args):
            try: return caption.resolve_literal_interval(*args)
            except caption.Pending as error: raise Pending(str(error)) from error
        value = plan(timing, read(PROJECT / 'narration-final-v5.json'), source['selectedCuts'], actual_interval)
        inputs = [pin(PROJECT / name) for name in SOURCE_PINS] + [pin(caption_timing), pin(audio_build), pin(HERE / CAPTION_FILE), pin(HERE / MIX_FILE), self_pin()]
        inputs += [pin(HERE / name) for name in PINS]
        inputs += [pin(MC_SOURCE / name) for name in MC_PINS]
        for name, expected in PINS.items(): need(sha(HERE / name) == expected, 'Frozen frame/structure helper changed')
        value.update(inputs=inputs, captionTiming=pin(caption_timing), audioBuild=pin(audio_build), audio=dict(mix=mix['mixWav']),
                     actualGameSource=source['sourceMedia'], physicalInputFingerprint=PHYSICAL)
        value['fingerprint'] = digest(value)
        if not structure_atlas or not moving_guides:
            self_source()
            return dict(ready=False, picturePlanReady=True, picturePlan=value,
                        reason='Pending actual source-bound structure MC artifacts and reviewed moving HD guide intervals',
                        imageDecoded=False, jobLaunched=False)
        verify_atlas(structure_atlas, value); verify_moving_guides(moving_guides, value)
        timeline = dict(schemaVersion='11.05-film-timeline-v2', topicId=TOPIC, picturePlan=value,
                        structureAtlas=pin(structure_atlas), movingGuides=pin(moving_guides),
                        encodedAudioMapping=dict(reference='accepted-body-mix', bodyStartSample=0,
                            bodyEndSample=mix['mixWav']['frames'], wholeAudioFrames=mix['mixWav']['frames'],
                            rate=48000, noAudioPadding=True),
                        assemblyProfile=dict(kind='body-only-portrait-with-integrated-brand',
                            authority='docs/VIDEO_WORKFLOW.md §9; matches the prior3 portrait deliveries',
                            introAudioSamples=0, outroAudioSamples=0, rawBodyPcmPreserved=True),
                        formatDecision=pin(PROJECT / 'portrait-audio-format-review-v1.json'),
                        formatReporting=dict(kind='full-concept-vertical-local-master',
                            actualAudioDurationSeconds=timing['audioClock']['totalRawSamples'] / RATE,
                            formalShortsDurationLimitSeconds=180,
                            formalShortsDurationEligible=timing['audioClock']['totalRawSamples'] <= 180 * RATE,
                            trimmedOrRetimedToFit=False, platformActions=[]),
                        rendererSource=pin(HERE / 'render-solution-path-film-v2.py'),
                        inputs=value['inputs'] + [pin(structure_atlas), pin(moving_guides), self_pin(), pin(HERE / 'render-solution-path-film-v2.py')],
                        encoded=False, actualPixelQaPassed=False, actualListening=False, humanApproval=False)
        timeline['fingerprint'] = digest(timeline)
        self_source()
        return dict(ready=True, picturePlanReady=True, picturePlan=value, timeline=timeline,
                    output=str(MEDIA / 'film-timelines-v2' / timeline['fingerprint'][:24] / 'timeline.json'),
                    imageDecoded=False, jobLaunched=False)
    except (Pending, OSError, KeyError, ValueError) as error:
        return dict(ready=False, picturePlanReady=False, reason=str(error), imageDecoded=False, jobLaunched=False)


def verify_existing(path):
    path = Path(path).resolve(); saved = read(path)
    need(path.is_relative_to(MEDIA / 'film-timelines-v2') and saved.get('schemaVersion') == '11.05-film-timeline-v2', 'Current owned V2 timeline path required')
    plan = saved['picturePlan']
    fresh = prepare(plan['captionTiming']['path'], plan['audioBuild']['path'], saved['structureAtlas']['path'], saved['movingGuides']['path'])
    need(fresh.get('ready') is True and fresh['timeline'] == saved and Path(fresh['output']).resolve() == path,
         'Saved timeline differs from fresh current proof chain')
    return dict(timeline=saved, picturePlan=plan)


def immutable_json(path, value, root):
    path = Path(path).resolve(); root = Path(root).resolve()
    need(path.is_relative_to(root), 'Output escaped the exact owned V2 artifact directory')
    data = (json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
    if path.exists(): need(path.read_bytes() == data, 'Preserve changed/foreign existing artifact')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream: stream.write(data)
    return pin(path)


def write_timeline(result):
    need(result.get('ready') is True, 'No actual verified timeline to write')
    value=result['timeline']; p=value['picturePlan']
    fresh=prepare(p['captionTiming']['path'],p['audioBuild']['path'],value['structureAtlas']['path'],value['movingGuides']['path'])
    need(fresh == result, 'Current proof chain changed before immutable timeline write')
    return immutable_json(result['output'],value,MEDIA/'film-timelines-v2')


def write_structure_job(picture_plan):
    fresh=prepare(picture_plan['captionTiming']['path'],picture_plan['audioBuild']['path'])
    need(fresh.get('picturePlanReady') is True and fresh['picturePlan'] == picture_plan,
         'Actual current picture clock/source chain changed before finite atlas job write')
    job=structure_job(picture_plan)
    return immutable_json(job['outputContract']['jobPath'],job,MEDIA/'structure-jobs-v2')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--caption-timing'); p.add_argument('--audio-build')
    p.add_argument('--structure-atlas'); p.add_argument('--moving-guides')
    p.add_argument('--write',action='store_true'); p.add_argument('--write-structure-job',action='store_true')
    args = p.parse_args()
    result=prepare(args.caption_timing,args.audio_build,args.structure_atlas,args.moving_guides)
    try:
        if args.write: result['writtenTimeline']=write_timeline(result)
        if args.write_structure_job:
            need(result.get('picturePlanReady') is True,'Pending actual source-bound picture clock')
            result['writtenStructureJob']=write_structure_job(result['picturePlan'])
    except (Pending,OSError) as error: result.update(ready=False,reason=str(error))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
