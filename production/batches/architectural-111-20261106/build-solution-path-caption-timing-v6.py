"""11.05 repaired NarV5 caption clocks; read-only unless explicit --write.

Strict literal alignment is the first choice. Optional explicitly hash-pinned
evidence can supply ONLY whole observed ASR-word interval endpoints. It never
changes canonical/recognized text, creates within-word times or approves speech.
Actual evidence rows must be authored after the current repaired95-task ASR.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, math, re, sys, types, uuid
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
PROJECT = ROOT / 'projects/shorts-leveldesign-11-05'
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05')
TOPIC, RATE, FPS = '11.05', 24000, 60
SCHEMA = '11.05-selected-caption-timing-v6'
EVIDENCE_SCHEMA = '11.05-whole-asr-word-edge-evidence-v1'
VOICE_DATA_KEYS = ('topicId', 'output', 'fingerprint', 'identity', 'sceneWavs', 'aggregateWav', 'timing', 'paragraphMapping',
    'repairProtocol', 'repairFingerprint', 'repairIdentity', 'reusedRawScenes', 'newlyGeneratedSceneIds', 'engineOutputsPreserved')
PINS = {
    'build-solution-path-caption-timing-v5.py': '9fbbae07231103f3b11ece20443349005902ce0af87e265555f06a1be91c1ad5',
    'run-solution-path-voice-qa-v6.py': '59618eb71570190ec78cbae98f94b15078cfd852d3325aab7ac10531400d727e',
    'verify-solution-path-caption-clauses.py': '92e7f8e2ad7b57acb3171c38aa415ec8f2381b627a5627b5f14c7521e3bb17d5',
}
SOURCE_PINS = {
    'narration-final-v5.json': 'e3179da81b2a23135eb6a8907ebb6205c14fc2d66e528a37372d491d0ffeaa91',
    'caption-clauses-v2.json': 'b1629be657702b8910cbf4eafafcabbd7452a688ae0b976c04a898aadf47fc0c',
    'translated-caption-display-boundaries-v2.json': 'f3d174651b0af77bf85847f76e53dec8e07c8a5d4143d936fc260f75f12e7be1',
}


class Pending(RuntimeError): pass


def require(value, reason):
    if not value: raise Pending(reason)


def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    with Path(path).open('rb') as handle: return hashlib.file_digest(handle, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def pin(path): return dict(path=str(Path(path).resolve()), sha256=sha(path))


def assert_pin(row):
    require(isinstance(row, dict) and isinstance(row.get('path'), str) and isinstance(row.get('sha256'), str)
            and Path(row['path']).is_file() and sha(row['path']) == row['sha256'], 'Missing/changed exact evidence pin')


def sample(seconds):
    require(type(seconds) in (int, float) and math.isfinite(seconds), 'Finite actual word timestamp required')
    return int(math.floor(seconds * RATE + .5))


def frame_from_sample(value):
    require(type(value) is int and value >= 0, 'Actual nonnegative raw sample required')
    return (value * FPS + RATE // 2) // RATE


def same_voice_data(value, current):
    require(isinstance(value, dict) and isinstance(current, dict)
            and all(k in value and k in current and value[k] == current[k] for k in VOICE_DATA_KEYS)
            and all(value.get(k) is not True for k in ('actualListening', 'humanApproval', 'automaticSpeechPass')),
            'Supplied voice differs from actual current raw/repair proof')


def edge_offsets(text, a, b):
    words = list(re.finditer(r'\S+', text))
    require(type(a) is type(b) is int and 0 <= a < b <= len(text), 'Canonical span must be an exact nonempty source interval')
    require(any(w.start() == a for w in words) and any(w.end() == b for w in words),
            'Evidence span must include complete canonical source words')
    starts, ends = {a}, {b}
    previous = next((w for w in words if w.end() < a and text[w.end():a].isspace()), None)
    following = next((w for w in words if w.start() > b and text[b:w.start()].isspace()), None)
    if previous: starts.add(previous.end())
    if following: ends.add(following.start())
    return dict(start=starts, end=ends)


def validate_evidence(document, context, sentences, takes, result_pins):
    """Pure validation after the actual source/voice/cache context is verified.

    Recognition is never rewritten. The caller supplies its independently
    validated exact current take cache and actualWords, not a prompt/glossary.
    """
    require(document.get('schemaVersion') == EVIDENCE_SCHEMA and document.get('topicId') == TOPIC
            and document.get('reviewScope') == 'technical-caption-display-whole-word-edges-only'
            and isinstance(document.get('reviewedBy'), str) and bool(document['reviewedBy'].strip()), 'Explicit audited display-only evidence required')
    for key, value in context.items(): require(document.get(key) == value, 'Evidence belongs to a different current context: ' + key)
    require(all(document.get(key) is False for key in ('aliasesApplied', 'recognitionModified', 'pcmModified',
            'expectedPromptsUsed', 'automaticSpeechPass', 'actualListening', 'humanApproval')), 'Display evidence cannot waive speech/PCM/recognizer review')
    require(isinstance(document.get('rows'), list), 'Explicit word-edge evidence rows required')
    result, ids, prior = {}, set(), {}
    for row in document['rows']:
        sid = row.get('sceneId'); rid = row.get('id')
        require(isinstance(rid, str) and rid and rid not in ids and sid in sentences and sid in takes, 'Unique current sentence evidence ID required')
        ids.add(rid); sentence, take = sentences[sid], takes[sid]
        require(digest(row.get('rawWav')) == digest(sentence['rawWav']) and row.get('asrResult') == result_pins[sid], 'Whole-word evidence raw PCM/cache identity differs')
        require(row.get('canonicalTakeLiteral') == sentence['canonicalKo'] and row.get('recognizedTakeLiteral') == take['text'], 'Full original canonical/recognized context must remain literal')
        span = row.get('canonicalCharRange'); require(isinstance(span, list) and len(span) == 2, 'Exact canonical source span required')
        a, b = span; allowed = edge_offsets(sentence['canonicalKo'], a, b)
        require(row.get('canonicalLiteral') == sentence['canonicalKo'][a:b], 'Canonical evidence literal changed')
        indices = row.get('actualWordIndices'); words = sentence['words']
        require(isinstance(indices, list) and indices and all(type(i) is int and 0 <= i < len(words) for i in indices)
                and indices == list(range(indices[0], indices[-1] + 1)), 'Complete contiguous actual ASR-word indices required')
        selected = [words[i] for i in indices]
        require(digest(row.get('recognizedWords')) == digest(selected) and row.get('recognizedLiteral') == ''.join(w['text'] for w in selected), 'Actual unmodified word records/literal differ from cache')
        require(isinstance(row.get('reason'), str) and bool(row['reason'].strip()), 'Audited mismatch/spacing reason required')
        for i, word in zip(indices, selected):
            require(word.get('sourceWordIndex') == i and type(word['startSample']) is type(word['endSample']) is int
                    and sentence['startSample'] <= word['startSample'] <= word['endSample'] <= sentence['endSample']
                    and sample(word['start']) == word['startSample'] and sample(word['end']) == word['endSample'],
                    'Only actual unclipped whole-word timestamp edges inside exact PCM are supported')
        begin, finish = selected[0]['startSample'], selected[-1]['endSample']
        require(begin < finish and all(x['endSample'] <= y['startSample'] for x, y in zip(selected, selected[1:])), 'Actual word interval overlaps/reverses')
        if sid in prior:
            end_char, end_index = prior[sid]
            require(a >= end_char and indices[0] > end_index, 'Audited canonical/word spans overlap or reverse')
        prior[sid] = (b, indices[-1])
        mappings = row.get('boundaryMappings')
        require(isinstance(mappings, list) and mappings and len({m.get('canonicalOffset') for m in mappings}) == len(mappings), 'Explicit unique endpoint mappings required')
        derived = []
        for mapping in mappings:
            edge, offset = mapping.get('actualEdge'), mapping.get('canonicalOffset')
            require(edge in ('start', 'end') and type(offset) is int and offset in allowed[edge],
                    'Boundary inside a canonical/actual merged word stays Pending; reflow the cue, never interpolate')
            point = begin if edge == 'start' else finish
            derived.append(dict(charOffset=offset, sample=point, frame=frame_from_sample(point),
                                actualEdge=edge, sourceWordIndices=indices, supportId=rid,
                                method='Explicit audited whole-ASR-word interval ' + edge + ' edge; technical display only'))
        result.setdefault(sid, []).append(dict(row=copy.deepcopy(row), boundaries=derived))
    return result


def apply_evidence(sentence, rows, proof):
    """Literal boundaries win; fallback can add only explicitly audited edges."""
    result = copy.deepcopy(sentence)
    original = {r['charOffset']: r for r in sentence['canonicalWordBoundaries']}
    added, used = {}, []
    for row in rows:
        for boundary in row['boundaries']:
            offset = boundary['charOffset']
            if offset in original: continue
            value = dict(boundary, supportProof=proof)
            require(offset not in added or added[offset]['sample'] == value['sample'], 'Audited word edges disagree at one source boundary')
            added[offset] = value; used.append(row['row']['id'])
    boundaries = sorted([*original.values(), *added.values()], key=lambda x: x['charOffset'])
    require(all(a['sample'] <= b['sample'] for a, b in zip(boundaries, boundaries[1:])), 'Evidence would reverse the exact literal clock')
    result['literalUnsupportedWordBoundaries'] = copy.deepcopy(sentence['unsupportedWordBoundaries'])
    result['canonicalWordBoundaries'] = boundaries
    result['unsupportedWordBoundaries'] = [v for v in sentence['unsupportedWordBoundaries'] if v['charOffset'] not in added]
    result['alignmentReview']['explicitWordEdgeEvidence'] = dict(proof=proof, auditedRows=[r['row'] for r in rows],
        appliedEvidenceIds=sorted(set(used)), appliedBoundaryCount=len(added), literalBoundariesPreferred=True,
        rawLiteralDifferencesPreserved=True, aliasesApplied=False, automaticSpeechPass=False,
        actualListening=False, hearingTargetsRemain=True)
    return result


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name + '_' + uuid.uuid4().hex, path)
    value = importlib.util.module_from_spec(spec); sys.modules[spec.name] = value; spec.loader.exec_module(value)
    return value


def libraries():
    for name, expected in PINS.items(): require(sha(HERE / name) == expected, 'Reviewed caption/ASR source changed: ' + name)
    old = _load('solution_caption_v6_previous', HERE / 'build-solution-path-caption-timing-v5.py')
    asr = _load('solution_caption_v6_repaired_blind', HERE / 'run-solution-path-voice-qa-v6.py')
    old.asr_adapter, old.asr = asr, asr.qa.raw
    old.Pending, old.require, old.SCHEMA = Pending, require, SCHEMA
    old._scope.update(asr=asr.qa.raw, Pending=Pending, require=require)
    return old, asr


def verified_asr_review(path):
    old, asr = libraries()
    function = types.FunctionType(old.verified_asr_review.__code__, dict(old.__dict__, asr_adapter=asr, require=require), 'verified_current_repaired_asr')
    try: return function(path)
    except asr.Pending as error: raise Pending(str(error)) from error


def voice_binding(voice, review, narration):
    old, asr = libraries()
    try: _, current, _, source = asr.exact_voice()
    except asr.Pending as error: raise Pending(str(error)) from error
    same_voice_data(voice, current)
    require(narration == source, 'Binding must use actual current repaired source')
    voice = current  # Publication-only metadata need not equal immutable D receipt bytes.
    expected = asr.profile_identity(voice['identity']['scenes'], read(asr.PROFILE_PATH))
    core = dict(voice['identity']); selection = core.pop('repairSelection', None)
    require(selection is not None and core == expected, 'Only the separately validated current repairSelection may extend the approved profile')
    proxy = types.SimpleNamespace(**asr.__dict__)
    def full_profile(scenes, profile):
        value = asr.profile_identity(scenes, profile)
        require(value == expected, 'Approved profile/source scenes changed')
        return dict(value, repairSelection=selection)
    proxy.profile_identity = full_profile
    fn = types.FunctionType(old.voice_binding.__code__, dict(old.__dict__, asr_adapter=proxy, require=require), 'exact_repaired_voice_binding')
    return fn(voice, review, narration)


def configure_display(old, clauses, translated, narration):
    require(clauses['schemaVersion'] == '11.05-caption-clauses-v2' and translated['schemaVersion'] == '11.05-translated-caption-display-boundaries-v2'
            and clauses['sourceNarration'] == pin(PROJECT / 'narration-final-v5.json')
            and translated['sourceNarration'] == clauses['sourceNarration']
            and translated['captionClauses'] == pin(PROJECT / 'caption-clauses-v2.json'), 'Exact authored V5/V2 source scope required')
    display = old.display
    def validate(document, source, fonts):
        require(document == clauses and source == narration, 'Display source changed during build')
        view = copy.deepcopy(document); view['schemaVersion'] = '11.05-caption-clauses-v1'
        return display.validate(view, source, fonts)
    old.display = types.SimpleNamespace(fonts=display.fonts, widths=display.widths, validate=validate)
    fn = types.FunctionType(old.validate_translated.__code__, dict(old.__dict__, require=require,
        SOURCE_PINS={'caption-clauses-v1.json': SOURCE_PINS['caption-clauses-v2.json']}), 'validate_current_translated_structure')
    def validate_translated(sidecar, document, source):
        require(sidecar == translated and document == clauses and source == narration, 'Translation source changed during build')
        view = copy.deepcopy(sidecar); view['schemaVersion'] = '11.05-translated-caption-display-boundaries-v1'
        return fn(view, document, source)
    old.validate_translated = validate_translated


def prepare(asr_review=None, voice_evidence=None, alignment_evidence=None):
    for name, expected in SOURCE_PINS.items(): require(sha(PROJECT / name) == expected, 'Current caption source changed: ' + name)
    old, asr = libraries()
    try:
        job = asr.prepare_job()
        target = Path(job['output']) / 'review.json'
        review = verified_asr_review(asr_review or target)
        out, voice, _, narration = asr.exact_voice()
    except asr.Pending as error: raise Pending(str(error)) from error
    if voice_evidence is not None:
        supplied = Path(voice_evidence).resolve()
        require(supplied in (Path(asr.PROOF).resolve(), out / 'voice-complete-proof.json'), 'Foreign supplied repaired voice path')
        same_voice_data(read(supplied), voice)
    require(asr.source_context()[0].resolve() == (PROJECT / 'narration-final-v5.json').resolve(), 'Current final source path differs')
    clauses = read(PROJECT / 'caption-clauses-v2.json'); translated = read(PROJECT / 'translated-caption-display-boundaries-v2.json')
    configure_display(old, clauses, translated, narration)
    binding = voice_binding(voice, review, narration)
    takes = {r['task']['sceneId']: r for r in review['takes']}
    pins = {t['sceneId']: pin(Path(job['output']) / (t['key'] + '.json')) for t in job['identity']['tasks'] if t['kind'] == 'take'}
    aligned = {s['sceneId']: old._scope['aligned_sentence'](s, takes[s['sceneId']], None) for s in binding['sentences']}
    evidence_pin, supported = None, {}
    context = dict(sourceNarration=pin(PROJECT / 'narration-final-v5.json'), voiceEvidence=pin(out / 'voice-complete-proof.json'),
                   voiceFingerprint=voice['fingerprint'], rawAsrReview=pin(target), rawAsrJob=pin(Path(job['output']) / 'job.json'))
    if alignment_evidence is not None:
        require(isinstance(alignment_evidence, dict), 'Evidence requires an explicitly supplied reviewed path AND SHA, not an auto-hashed path')
        assert_pin(alignment_evidence); p = Path(alignment_evidence['path']).resolve()
        require(p.is_relative_to(PROJECT) or p.is_relative_to(MEDIA), 'Word evidence escaped selected11.05 scope')
        evidence_pin = pin(p)
        supported = validate_evidence(read(p), context, aligned, takes, pins)
    aligned = {sid: apply_evidence(row, supported.get(sid, []), evidence_pin) for sid, row in aligned.items()}
    def already_aligned(source, take):
        row = aligned[source['sceneId']]
        require(all(row[k] == source[k] for k in source) and take == takes[source['sceneId']], 'Actual alignment source changed during build')
        return copy.deepcopy(row)
    old.aligned_sentence = already_aligned
    timing = old.build(narration, clauses, translated, review, binding, pins)
    inputs = dict(voiceEvidence=context['voiceEvidence'], rawAsrReview=context['rawAsrReview'], rawAsrJob=context['rawAsrJob'],
                  narration=context['sourceNarration'], captionClauses=pin(PROJECT / 'caption-clauses-v2.json'),
                  translatedDisplayBoundaries=pin(PROJECT / 'translated-caption-display-boundaries-v2.json'),
                  rawAsrResults=[pin(Path(job['output']) / (t['key'] + '.json')) for t in job['identity']['tasks']],
                  font=pin(clauses['style']['fontPath']), helpers=[pin(__file__)] + [pin(HERE / name) for name in PINS],
                  wordEdgeEvidence=evidence_pin)
    timing['alignmentReview'].update(explicitWholeWordEvidence=evidence_pin, literalResolverPreferred=True,
        aliasesApplied=False, withinWordInterpolationUsed=False, rawLiteralDifferencesPreserved=True,
        technicalDisplayAlignmentOnly=True, automaticSpeechPass=False, hearingTargetsRemain=True)
    fingerprint = digest(dict(inputs=inputs, timing=timing)); folder = MEDIA / 'caption-timing-v6' / fingerprint[:24]
    timing.update(fingerprint=fingerprint, inputIdentitySHA256=digest(inputs), inputs=inputs,
                  subtitles={language: dict(path=str(folder / ('narration.' + language + '.srt')),
                    sha256=hashlib.sha256(old.srt(rows).encode('utf8')).hexdigest()) for language, rows in timing['captions'].items()})
    return dict(ready=True, fingerprint=fingerprint, output=str(folder / 'caption-timing.json'), timing=timing, voice=voice, asr=review)


def verify_existing(path):
    saved = read(path); evidence = saved.get('inputs', {}).get('wordEdgeEvidence')
    fresh = prepare(alignment_evidence=evidence)
    require(Path(path).resolve() == Path(fresh['output']).resolve() and saved == fresh['timing'], 'Current actual caption timing differs')
    old, _ = libraries()
    for language, row in saved['subtitles'].items():
        assert_pin(row); require(Path(row['path']).read_bytes() == old.srt(saved['captions'][language]).encode('utf8'), 'Source-exact plain SRT differs')
    return dict(timing=fresh['timing'], voice=fresh['voice'], asr=fresh['asr'])


def resolve_literal_interval(timing, paragraph, phrase):
    old, _ = libraries()
    return old.resolve_literal_interval(timing, paragraph, phrase)


def write_outputs(result):
    evidence = result['timing']['inputs']['wordEdgeEvidence']; fresh = prepare(alignment_evidence=evidence)
    require(result == fresh, 'Actual caption/evidence inputs changed before immutable write')
    old, asr = libraries()
    for language, row in result['timing']['subtitles'].items():
        asr.qa.voice.immutable(Path(row['path']), old.srt(result['timing']['captions'][language]).encode('utf8'))
    asr.qa.voice.immutable_json(Path(result['output']), result['timing'])
    return pin(result['output'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--asr-review'); p.add_argument('--voice-evidence'); p.add_argument('--alignment-evidence'); p.add_argument('--alignment-evidence-sha256'); p.add_argument('--write', action='store_true')
    args = p.parse_args()
    require(bool(args.alignment_evidence) == bool(args.alignment_evidence_sha256), 'Supply both audited evidence path and exact SHA')
    evidence = dict(path=args.alignment_evidence, sha256=args.alignment_evidence_sha256) if args.alignment_evidence else None
    try:
        value = prepare(args.asr_review, args.voice_evidence, evidence)
        print(json.dumps(dict(ready=True, output=value['output'], fingerprint=value['fingerprint'],
            artifact=write_outputs(value) if args.write else None, actualListening=False, humanApproval=False, jobLaunched=False), ensure_ascii=False))
    except (Pending, FileNotFoundError) as error:
        print(json.dumps(dict(ready=False, reason=str(error), written=False, jobLaunched=False), ensure_ascii=False))


if __name__ == '__main__': main()
