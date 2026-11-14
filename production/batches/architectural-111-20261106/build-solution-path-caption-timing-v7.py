"""11.05 source-exact caption clocks from completed blind raw ASR only.

Default is read-only. --write may create immutable caption JSON/plain SRT after
all current PCM/cache/source boundaries resolve. No model, audio or render job.
"""
from __future__ import annotations
import argparse, ast, copy, difflib, hashlib, importlib.util, json, math, re, sys, types, wave
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
PROJECT = ROOT / 'projects/shorts-leveldesign-11-05'
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05')
FPS, RATE, TOPIC = 60, 24000, '11.05'
SCHEMA = '11.05-selected-caption-timing-v7'
PINS = {'build-prospect-refuge-caption-timing.py': 'e5cfcc3994a2d52bced9ee66b9ff6213355acbaef45286d31aa3e1461d7ef609', 'verify-solution-path-caption-clauses.py': '92e7f8e2ad7b57acb3171c38aa415ec8f2381b627a5627b5f14c7521e3bb17d5', 'author-solution-path-caption-clauses-v3.py': '4afb43717cb45b015bbbf49e3277463be974ab162429074b83137087b51b7e19', 'run-solution-path-voice-qa-v14.py': '411c7263bc90433cdba7556fb45195e39a77a9e0957a0c716ced7728454c1eeb', 'build-solution-path-caption-timing-v6.py': '11a2765b208427d2f5a4caa8bfa0958f390adaa062ecc95d73b77208747f3421'}
SOURCE_PINS = {'narration-final-v7.json': '0e4786acc33531b5e1df18a95f6c4a07ab85fc86c4c8f07221ae800662ccf0a1', 'caption-clauses-v3.json': 'baf30eb1038e5bdd040ef30d790453a3e904c34b6836bdacae68df90cd095a7e', 'translated-caption-display-boundaries-v3.json': 'ade0020004978ad746703b507edd75188d7235fd4c6a51bee9378bf2d2a87ec4', 'voice-asr-content-review-v14.json': 'aefbc0825979537ba35eac69164a613502ad0b2dda50640b53dec469982b2661'}


class Pending(RuntimeError):
    pass


def require(value, reason):
    if not value:
        raise Pending(reason)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def pin(path):
    return dict(path=str(Path(path).resolve()), sha256=sha(path))


def assert_pin(row):
    require(Path(row['path']).is_file() and sha(row['path']) == row['sha256'], 'Missing/changed input: ' + row['path'])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


for name, expected in PINS.items():
    require(sha(HERE / name) == expected, 'Reviewed caption/ASR helper changed: ' + name)
asr_adapter = load('solution_caption_v7_blind_asr', HERE / 'run-solution-path-voice-qa-v14.py')
display = load('solution_caption_v7_measured_display', HERE / 'verify-solution-path-caption-clauses.py')
asr = asr_adapter.qa.raw

author = load('solution_caption_v7_authored_source', HERE / 'author-solution-path-caption-clauses-v3.py')
edge_library = load('solution_caption_v7_pure_whole_word_evidence', HERE / 'build-solution-path-caption-timing-v6.py')
def validate_authored(document, narration, fonts):
    fresh, _, _ = author.prepare()
    require(document == fresh and narration == read(PROJECT / 'narration-final-v7.json'),
            'Explicit V3 measured meaning clauses or Nar7 differ')
display = types.SimpleNamespace(fonts=display.fonts, widths=display.widths, validate=validate_authored)



def sample(seconds):
    require(type(seconds) in (int, float) and math.isfinite(seconds), 'Nonfinite actual word time')
    return int(math.floor(seconds * RATE + .5))


def frame_from_sample(value):
    require(type(value) is int and value >= 0, 'Nonnegative integer sample required')
    return (value * FPS + RATE // 2) // RATE


def ceil_frame(value):
    return (value * FPS + RATE - 1) // RATE


# Extract two reviewed, topic-neutral PURE functions, not the old06 module or
# its source paths/prepare/CLI/boundary exceptions. Generic07 literal_alignment
# permits within-word fractions; it is deliberately not used for these clocks.
_tree = ast.parse((HERE / 'build-prospect-refuge-caption-timing.py').read_text(encoding='utf-8'))
_names = {'aligned_sentence', 'char_boundary'}
_nodes = [n for n in _tree.body if isinstance(n, ast.FunctionDef) and n.name in _names]
require({n.name for n in _nodes} == _names, 'Pinned strict literal primitive missing')
_scope = dict(require=require, Pending=Pending, asr=asr, sample=sample, RATE=RATE,
              frame_from_sample=frame_from_sample, math=math, re=re, difflib=difflib)
exec(compile(ast.Module(body=_nodes, type_ignores=[]), str(HERE / 'build-prospect-refuge-caption-timing.py'), 'exec'), _scope)


def aligned_sentence(sentence, take):
    return _scope['aligned_sentence'](sentence, take, support=None)


def char_boundary(sentence, offset):
    return _scope['char_boundary'](sentence, offset)


def verified_asr_review(path):
    """Existing current review + every cache; reconstruct without ANY write."""
    job = asr_adapter.prepare_job()
    target = Path(job['output']) / 'review.json'
    require(Path(path).resolve() == target.resolve() and target.is_file(), 'Current completed11.05 ASR review required')
    jp = target.parent / 'job.json'
    require(jp.is_file(), 'Existing exact ASR job is missing')
    saved = read(jp)
    for key in ('protocol', 'fingerprint', 'identity', 'output', 'voiceOutput', 'modelPath', 'sourcePins', 'voiceEvidence'):
        require(saved.get(key) == job.get(key), 'ASR job provenance differs: ' + key)
    require(sha(target.parent / 'adapter-source.py') == job['identity']['adapterSHA256'], 'Actual ASR adapter snapshot changed')
    for row in job['sourcePins']:
        assert_pin(row)
    require(all(asr_adapter.qa.cached(job, task) is not None for task in job['identity']['tasks']), 'Missing actual independent take/join cache')
    current = read(target)
    def check_existing(destination, value):
        require(Path(destination).resolve() == target.resolve() and value == current, 'ASR summary differs from its exact raw caches')
    function = asr_adapter.qa.summary
    scope = dict(function.__globals__, voice=types.SimpleNamespace(immutable_json=check_existing))
    rebuilt = types.FunctionType(function.__code__, scope, 'read_only_existing_asr_summary')(job)
    require(rebuilt == current and current.get('aliasesApplied') is False and current.get('expectedPrompt') is None
            and current.get('automaticSpeechPass') is False, 'Independent raw literal ASR provenance differs')
    return current


def voice_binding(voice, review, narration):
    require(voice.get('topicId') == TOPIC and digest(voice['identity']) == voice['fingerprint'], 'Exact selected11.05 voice identity required')
    require(len(narration.get('narrationKo', [])) == len(narration.get('paragraphsEn', [])) == 14, 'Exact14 paragraphs required')
    _, current, _, source = asr_adapter.exact_voice()
    require(voice == current and source == narration, 'Exact completed V10 canonical context required')
    mapping = current['paragraphMapping']; scenes = current['identity']['scenes']
    require(len(mapping) == 51 and len(scenes) == 51, 'Exact51 physical utterances required')
    require(voice['identity']['scenes'] == scenes and voice['paragraphMapping'] == mapping, 'Exact complete-sentence/source character mapping differs')
    require({k:v for k,v in voice['identity'].items() if k!='repairSelection'} == asr_adapter.qa7.profile_identity(scenes, read(asr_adapter.qa7.PROFILE_PATH)), 'Approved voice model/reference/profile differs')
    out = Path(voice['output']).resolve()
    chunks = voice['sceneWavs']
    assert_pin(voice['timing']); assert_pin(voice['aggregateWav'])
    timing = read(voice['timing']['path'])
    require(timing['sample_rate'] == RATE and len(chunks) == len(scenes) == len(timing['entries']), 'Exact raw sentence/timing count differs')
    position = 0; pcm = hashlib.sha256(); sentences = []
    for scene, part, chunk, entry in zip(scenes, mapping, chunks, timing['entries']):
        require(Path(chunk['path']).resolve() == out / 'chunks' / (scene['id'] + '-scene.wav'), 'Raw chunk path escaped selected output')
        actual = asr_adapter.qa.voice.wav_info(chunk['path'])
        require(actual == chunk, 'Actual raw WAV/PCM/format/sample metadata differs')
        require(entry['scene_id'] == scene['id'] and entry['text'] == part['canonicalText'] == scene['lines'][0], 'Raw sentence text/order differs')
        require(abs(entry['start'] - position / RATE) < 1e-9 and abs(entry['end'] - (position + chunk['frames']) / RATE) < 1e-9, 'Raw take sample boundary differs')
        begin = position; position += chunk['frames']; pcm.update(asr_adapter.qa.pcm_bytes(chunk['path']))
        sentences.append(dict(sceneId=scene['id'], paragraph=part['paragraph'], canonicalKo=part['canonicalText'],
                              paragraphCharRange=part['sourceCharRange'], startSample=begin, endSample=position,
                              startFrame=frame_from_sample(begin), endFrameExclusive=frame_from_sample(position), rawWav=chunk))
    aggregate = asr_adapter.qa.voice.wav_info(voice['aggregateWav']['path'])
    require(aggregate == voice['aggregateWav'] and aggregate['frames'] == position and aggregate['pcmSHA256'] == pcm.hexdigest(), 'Canonical aggregate is not exact selected raw concatenation')
    require(review.get('voiceFingerprint') == voice['fingerprint'] and review.get('aggregateSHA256') == aggregate['sha256']
            and review.get('timingSHA256') == voice['timing']['sha256'], 'ASR belongs to different raw PCM/timing')
    require(len(review.get('takes', [])) == len(sentences) and len(review.get('boundaryWindows', [])) == len(sentences) - 1
            and len(review.get('paragraphs', [])) == 14, 'Complete independent sentence/join/paragraph coverage required')
    expected_tasks = asr_adapter.qa.build_tasks(voice, timing)
    require([r['task'] for r in review['takes']] == [t for t in expected_tasks if t['kind'] == 'take']
            and [r['task'] for r in review['boundaryWindows']] == [t for t in expected_tasks if t['kind'] == 'boundary'],
            'Exact ordered raw take/join PCM envelopes differ')
    for p, row in enumerate(review['paragraphs'], 1):
        ss = [s for s in sentences if s['paragraph'] == p]
        require(row['paragraph'] == p and row['sceneIds'] == [s['sceneId'] for s in ss]
                and row['expectedLiteral'] == narration['narrationKo'][p - 1], 'ASR paragraph literal/order differs')
        require((row['startSample'], row['endSample']) == (ss[0]['startSample'], ss[-1]['endSample'])
                and abs(row['start'] - ss[0]['startSample'] / RATE) < 1e-9
                and abs(row['end'] - ss[-1]['endSample'] / RATE) < 1e-9, 'ASR paragraph raw clock differs')
    sentences[-1]['endFrameExclusive'] = ceil_frame(position)
    return dict(voiceFingerprint=voice['fingerprint'], aggregate=aggregate, timing=voice['timing'], sampleRate=RATE,
                totalSamples=position, totalFrames=ceil_frame(position), rawSelectedTakes=len(sentences),
                canonicalExactConcatVerified=True, sentences=sentences, automaticSpeechPass=False)


def validate_translated(sidecar, clauses, narration):
    require(sidecar.get('topicId') == TOPIC and sidecar.get('schemaVersion') == '11.05-translated-caption-display-boundaries-v3', 'Wrong translated-display source')
    require(sidecar['sourceNarration'] == clauses['sourceNarration'] and sidecar['semanticTimingVerified'] is False
            and sidecar['actualTimingAssigned'] is False and sidecar['originalMeaningAnchorsUsedAsClock'] is False, 'Translated display must not invent semantic clocks')
    require(sidecar['captionClauses']['sha256'] == SOURCE_PINS['caption-clauses-v3.json'], 'Translated display caption source differs')
    require([r['groupId'] for r in sidecar['groups']] == [r['id'] for r in clauses['groups']], 'Translated group order/coverage differs')
    for group, row in zip(clauses['groups'], sidecar['groups']):
        paragraph = narration['narrationKo'][group['paragraph'] - 1]
        cuts = row['koDisplayBoundaryCharOffsets']; anchors = row['boundaryAnchors']
        require(row['paragraph'] == group['paragraph'] and row['enCueIds'] == [c['id'] for c in group['enCues']], 'Translated cue order differs')
        require(len(cuts) == len(group['enCues']) + 1 and len(anchors) == len(cuts)
                and all(type(x) is int for x in cuts) and all(a < b for a, b in zip(cuts, cuts[1:]))
                and [cuts[0], cuts[-1]] == group['koSourceCharRange'], 'Translated display partition has gap/reversal/source drift')
        words = list(re.finditer(r'\S+', paragraph))
        for offset, anchor in zip(cuts, anchors):
            left = next((w for w in words if w.end() == offset), None)
            right = next((w for w in words if w.start() == offset), None)
            if left is not None:
                j = words.index(left); right = words[j + 1] if j + 1 < len(words) else None
            elif right is not None:
                j = words.index(right); left = words[j - 1] if j else None
            require(left is not None or right is not None, 'Display cut bisects a Korean source word')
            require(anchor['offset'] == offset and anchor['leftWordKo'] == (left.group() if left else None)
                    and anchor['rightWordKo'] == (right.group() if right else None)
                    and anchor['leftWordCharRange'] == ([left.start(), left.end()] if left else None)
                    and anchor['rightWordCharRange'] == ([right.start(), right.end()] if right else None)
                    and anchor['actualSample'] is None and anchor['actualFrame'] is None, 'Authored whole-word boundary evidence differs')


def paragraph_boundary(sentences, paragraph, offset):
    matches = [s for s in sentences if s['paragraph'] == paragraph and s['paragraphCharRange'][0] <= offset <= s['paragraphCharRange'][1]]
    require(len(matches) == 1, 'Requested paragraph character is not inside one exact source sentence')
    sentence = matches[0]
    value = copy.deepcopy(char_boundary(sentence, offset - sentence['paragraphCharRange'][0]))
    value.update(sceneId=sentence['sceneId'], paragraphCharOffset=offset, rawWav=sentence['rawWav'], asrResult=sentence['asrResult'])
    return value


def one_line_emphasis(text, lines, spans):
    """Project one exact authored span into ONE line; never shorten/rewrite it."""
    require(' '.join(lines) == text and len(spans) <= 1, 'Exact authored caption lines/span required')
    result = []; cursor = 0
    for index, line in enumerate(lines):
        for span in spans:
            if cursor <= span['start'] < span['end'] <= cursor + len(line):
                require(text[span['start']:span['end']] == span['text'], 'Authored emphasis text changed')
                result.append(dict(line=index, start=span['start'] - cursor, end=span['end'] - cursor,
                                   role=span['role'], text=span['text']))
        cursor += len(line) + 1
    require(len(result) == len(spans), 'Authored emphasis crosses a line; no silent shortening')
    return result


def display_cue(cue, language, group, left, right, fonts):
    require(right['sample'] > left['sample'] and right['frame'] > left['frame'], 'Positive actual sample/frame caption interval required')
    measured = display.widths(cue, fonts)
    require(measured == cue['measuredLineWidthsPx'], 'Authored mixed-weight display measurement differs')
    return dict(id=cue['id'], paragraph=group['paragraph'], groupId=group['id'], beatId=group['beatId'], language=language,
                text=cue['text'], lines=cue['lines'], emphasis=one_line_emphasis(cue['text'], cue['lines'], cue['emphasis']),
                sourceEmphasis=cue['emphasis'], measuredLineWidthsPx=measured,
                startSample=left['sample'], endSample=right['sample'], startFrame=left['frame'], endFrameExclusive=right['frame'],
                actualStartBoundary=left, actualEndBoundary=right, humanTimingReviewRequired=True, actualListening=False)


def build(narration, clauses, translated, review, binding, result_pins, aligned_rows=None):
    fonts = display.fonts()
    display.validate(clauses, narration, fonts)
    validate_translated(translated, clauses, narration)
    takes = {r['task']['sceneId']: r for r in review['takes']}
    require(len(takes) == len(binding['sentences']), 'Duplicate/missing actual ASR sentences')
    sentences = []
    for source in binding['sentences']:
        sid = source['sceneId']; row = copy.deepcopy(aligned_rows[sid]) if aligned_rows is not None else aligned_sentence(source, takes[sid]); row['asrResult'] = result_pins[sid]
        sentences.append(row)
    cues = {'ko': [], 'en': []}; groups = []
    for group, translated_group in zip(clauses['groups'], translated['groups']):
        p = group['paragraph']; get = lambda x: paragraph_boundary(sentences, p, x)
        begin, finish = map(get, group['koSourceCharRange'])
        groups.append(dict(id=group['id'], paragraph=p, beatId=group['beatId'], startSample=begin['sample'], endSample=finish['sample'],
                           startFrame=begin['frame'], endFrameExclusive=finish['frame'], koSourceCharRange=group['koSourceCharRange'],
                           enSourceCharRange=group['enSourceCharRange'], sourceSceneIds=[s['sceneId'] for s in sentences if s['paragraph'] == p
                           and group['koSourceCharRange'][0] <= s['paragraphCharRange'][0] and s['paragraphCharRange'][1] <= group['koSourceCharRange'][1]]))
        for cue in group['koCues']:
            left, right = map(get, cue['sourceCharRange'])
            row = display_cue(cue, 'ko', group, left, right, fonts)
            row.update(sourceCharRange=cue['sourceCharRange'], spokenLiteralAnchorKo=cue['spokenLiteralAnchorKo'], aliasesApplied=False,
                       timingBasis='Actual literal whole-ASR-word boundaries in exact selected raw components; no within-word interpolation')
            cues['ko'].append(row)
        cuts = translated_group['koDisplayBoundaryCharOffsets']
        for cue, a, b in zip(group['enCues'], cuts, cuts[1:]):
            row = display_cue(cue, 'en', group, get(a), get(b), fonts)
            row.update(sourceCharRange=cue['sourceCharRange'], authoredMeaningAnchor=cue['spokenKoAnchor'],
                       koDisplayCharRange=[a, b], koDisplayLiteral=narration['narrationKo'][p - 1][a:b],
                       timingBasis='Explicit authored monotonic Korean display slots resolved only from actual whole word/take boundaries; not English ASR',
                       translatedSemanticTimingVerified=False, translatedTimingReviewPending=True,
                       originalMeaningWindowsNonordered=translated_group['originalMeaningWindowsNonordered'])
            cues['en'].append(row)
    for language, rows in cues.items():
        require(all(a['endSample'] <= b['startSample'] and a['endFrameExclusive'] <= b['startFrame'] for a, b in zip(rows, rows[1:])), language + ' actual captions overlap/reverse')
        for p, text in enumerate(narration['narrationKo'] if language == 'ko' else narration['paragraphsEn'], 1):
            require(' '.join(r['text'] for r in rows if r['paragraph'] == p) == text, 'Plain subtitle text/paragraph reconstruction differs')
    require(len(cues['ko']) == clauses['counts']['koCues'] and len(cues['en']) == clauses['counts']['enCues'], 'Caption cue count/coverage differs')
    paragraphs = []
    for p in range(1, 15):
        ss = [s for s in sentences if s['paragraph'] == p]
        paragraphs.append(dict(paragraph=p, canonicalKo=narration['narrationKo'][p - 1], canonicalEn=narration['paragraphsEn'][p - 1],
                               startSample=ss[0]['startSample'], endSample=ss[-1]['endSample'], startFrame=ss[0]['startFrame'],
                               endFrameExclusive=ss[-1]['endFrameExclusive'], sceneIds=[s['sceneId'] for s in ss]))
    paragraphs[-1]['endFrameExclusive'] = binding['totalFrames']
    return dict(schemaVersion=SCHEMA, topicId=TOPIC, fps=FPS, totalFrames=binding['totalFrames'], captions=cues, groups=groups,
                paragraphs=paragraphs, sentences=sentences, voiceBinding={k: v for k, v in binding.items() if k != 'sentences'},
                audioClock=dict(rawSampleRate=RATE, totalRawSamples=binding['totalSamples'], rawAggregate=binding['aggregate'],
                                rawTiming=binding['timing'], visualFinalFrameCeil=True, noAudioTailPadding=True,
                                mixedAudioTimingAccepted=False, finalMix=None),
                alignmentReview=dict(rawLiteralDifferencesPreserved=True, unsupportedWordBoundariesPreserved=True,
                                     aliasesApplied=False, withinWordInterpolationUsed=False, draftFractionTimingUsed=False,
                                     translationMeaningAnchorsPreserved=True, translatedSemanticTimingVerified=False,
                                     translatedTimingReviewPending=True, nativeCameraOrMarkBindingsAssigned=False),
                automaticSpeechPass=False, actualListening=False, actualFinalPlayback=False, actualPixelReview=False,
                humanTimingReviewRequired=True, humanApproval=False, platformActions=[])


def resolve_literal_interval(timing, paragraph, phrase):
    row = next((p for p in timing['paragraphs'] if p['paragraph'] == paragraph), None)
    require(row is not None and isinstance(phrase, str) and phrase and row['canonicalKo'].count(phrase) == 1, 'Exact unique spoken phrase required')
    start = row['canonicalKo'].index(phrase)
    left = paragraph_boundary(timing['sentences'], paragraph, start)
    right = paragraph_boundary(timing['sentences'], paragraph, start + len(phrase))
    require(right['sample'] > left['sample'], 'Actual phrase has no positive raw interval')
    return dict(paragraph=paragraph, exactSpokenAnchorKo=phrase, startSample=left['sample'], endSample=right['sample'],
                startFrame=left['frame'], endFrameExclusive=right['frame'], actualStartBoundary=left, actualEndBoundary=right,
                aliasesApplied=False, nativeFrameOrCameraAssigned=False)


def srt(cues):
    def stamp(frame):
        ms = (frame * 1000 + FPS // 2) // FPS; h, ms = divmod(ms, 3600000); minute, ms = divmod(ms, 60000); second, ms = divmod(ms, 1000)
        return f'{h:02}:{minute:02}:{second:02},{ms:03}'
    return '\n\n'.join(f"{i}\n{stamp(row['startFrame'])} --> {stamp(row['endFrameExclusive'])}\n{row['text']}" for i, row in enumerate(cues, 1)) + '\n'


def prepare(asr_review=None, voice_evidence=None, alignment_evidence=None):
    for name, expected in PINS.items():
        require(sha(HERE / name) == expected, 'Reviewed helper changed: ' + name)
    for name, expected in SOURCE_PINS.items():
        require(sha(PROJECT / name) == expected, 'Selected caption/narration source changed: ' + name)
    qualification = read(PROJECT / 'voice-asr-content-review-v14.json')
    require(qualification['disposition'] == 'rewritten-explanations-qualified-for-downstream-local-review-production' and qualification['numericalHold'] is False and qualification['newTargetsLiteralMatch'] is True, 'Current raw explanations not qualified')
    for row in qualification['inputs'].values(): assert_pin(row)
    job = asr_adapter.prepare_job()
    require(job['fingerprint'] == '78518c6c1911a276b04e0b2002e576c12d1d6307188de8706080d67db4933798', 'Foreign ASR context')
    target = Path(job['output']) / 'review.json'
    review = verified_asr_review(asr_review or target)
    out, voice, _, narration = asr_adapter.exact_voice()
    require(voice['fingerprint'] == '55c5e387f06e6afae95e176f5e6c278de931ef6e66f36a0e9cdb6d5ab0adf037', 'Foreign voice context')
    source_path = PROJECT / 'narration-final-v7.json'
    require(asr_adapter.repair.source_context()[0].resolve() == source_path.resolve(), 'Selected final narration differs')
    if voice_evidence is not None:
        supplied = Path(voice_evidence).resolve()
        require(supplied in (Path(asr_adapter.PROOF).resolve(), out / 'voice-complete-proof.json'), 'Foreign voice evidence path')
        value = read(supplied)
        require(all(value[k] == voice[k] for k in ('fingerprint', 'identity', 'sceneWavs', 'aggregateWav', 'timing', 'paragraphMapping')), 'Supplied voice evidence differs')
    clauses = read(PROJECT / 'caption-clauses-v3.json'); translated = read(PROJECT / 'translated-caption-display-boundaries-v3.json')
    require(clauses['sourceNarration'] == pin(source_path) and translated['captionClauses'] == pin(PROJECT / 'caption-clauses-v3.json'), 'Authored source pin differs')
    binding = voice_binding(voice, review, narration)
    result_pins = {task['sceneId']: pin(Path(job['output']) / (task['key'] + '.json')) for task in job['identity']['tasks'] if task['kind'] == 'take'}
    takes={row['task']['sceneId']:row for row in review['takes']}
    aligned={source['sceneId']:aligned_sentence(source,takes[source['sceneId']]) for source in binding['sentences']}
    context=dict(sourceNarration=pin(source_path),voiceEvidence=pin(out/'voice-complete-proof.json'),voiceFingerprint=voice['fingerprint'],rawAsrReview=pin(target),rawAsrJob=pin(Path(job['output'])/'job.json'))
    supported={};evidence_pin=None
    if alignment_evidence is not None:
        require(isinstance(alignment_evidence,dict),'Explicit evidence path and SHA required');assert_pin(alignment_evidence)
        ep=Path(alignment_evidence['path']).resolve();require(ep.is_relative_to(PROJECT) or ep.is_relative_to(MEDIA),'Foreign display-evidence scope')
        evidence_pin=pin(ep);supported=edge_library.validate_evidence(read(ep),context,aligned,takes,result_pins)
    aligned={sid:edge_library.apply_evidence(row,supported.get(sid,[]),evidence_pin) for sid,row in aligned.items()}
    timing = build(narration, clauses, translated, review, binding, result_pins,aligned)
    timing['alignmentReview'].update(explicitWholeWordEvidence=evidence_pin,literalResolverPreferred=True,technicalDisplayAlignmentOnly=True,hearingTargetsRemain=True)
    inputs = dict(voiceEvidence=pin(out / 'voice-complete-proof.json'), rawAsrJob=pin(Path(job['output']) / 'job.json'), rawAsrReview=pin(target),
                  rawAsrResults=[pin(Path(job['output']) / (t['key'] + '.json')) for t in job['identity']['tasks']],
                  narration=pin(source_path), captionClauses=pin(PROJECT / 'caption-clauses-v3.json'),
                  translatedDisplayBoundaries=pin(PROJECT / 'translated-caption-display-boundaries-v3.json'),
                  wordEdgeEvidence=evidence_pin, rawVoiceQualification=pin(PROJECT / 'voice-asr-content-review-v14.json'), font=pin(clauses['style']['fontPath']), helpers=[pin(Path(__file__))] + [pin(HERE / name) for name in PINS])
    fingerprint = digest(dict(inputs=inputs, timing=timing)); folder = MEDIA / 'caption-timing-v7' / fingerprint[:24]
    subtitles = {language: dict(path=str(folder / ('narration.' + language + '.srt')),
                                sha256=hashlib.sha256(srt(rows).encode('utf-8')).hexdigest()) for language, rows in timing['captions'].items()}
    timing.update(fingerprint=fingerprint, inputIdentitySHA256=digest(inputs), inputs=inputs, subtitles=subtitles)
    return dict(ready=True, fingerprint=fingerprint, output=str(folder / 'caption-timing.json'), timing=timing, voice=voice, asr=review)


def verify_existing(path):
    saved=read(path);result = prepare(alignment_evidence=saved.get('inputs',{}).get('wordEdgeEvidence'))
    target = Path(result['output'])
    require(Path(path).resolve() == target.resolve() and target.is_file() and read(target) == result['timing'], 'Current caption artifact differs/missing')
    for language, row in result['timing']['subtitles'].items():
        require(Path(row['path']).is_file() and sha(row['path']) == row['sha256']
                and Path(row['path']).read_bytes() == srt(result['timing']['captions'][language]).encode('utf-8'), 'Plain source-exact subtitle changed')
    return dict(timing=result['timing'], voice=result['voice'], asr=result['asr'])


def write_outputs(result):
    fresh = prepare(alignment_evidence=result['timing']['inputs']['wordEdgeEvidence'])
    require(result == fresh, 'Caption inputs changed before immutable write')
    for language, row in result['timing']['subtitles'].items():
        asr_adapter.qa.voice.immutable(Path(row['path']), srt(result['timing']['captions'][language]).encode('utf-8'))
    asr_adapter.qa.voice.immutable_json(Path(result['output']), result['timing'])
    return pin(result['output'])


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--asr-review'); parser.add_argument('--voice-evidence'); parser.add_argument('--write', action='store_true'); parser.add_argument('--alignment-evidence'); parser.add_argument('--alignment-evidence-sha256'); args = parser.parse_args()
    require(bool(args.alignment_evidence)==bool(args.alignment_evidence_sha256),'Explicit evidence path and SHA must both be supplied')
    evidence=dict(path=args.alignment_evidence,sha256=args.alignment_evidence_sha256) if args.alignment_evidence else None
    try:
        result = prepare(args.asr_review, args.voice_evidence,evidence)
        written = write_outputs(result) if args.write else None
        print(json.dumps(dict(ready=True, fingerprint=result['fingerprint'], totalFrames=result['timing']['totalFrames'],
                              cueCounts={k: len(v) for k, v in result['timing']['captions'].items()}, written=written,
                              translatedTimingReviewPending=True, modelLoaded=False, actualPixelReview=False), ensure_ascii=False))
    except (Pending, asr_adapter.Pending, FileNotFoundError) as exc:
        print(json.dumps(dict(ready=False, reason=str(exc), written=False, modelLoaded=False, actualPixelReview=False), ensure_ascii=False))


if __name__ == '__main__':
    main()
