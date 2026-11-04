"""Exact Marine mix word-boundary review; preserves raw ASR and hearing limits.

No common source, pronunciation aliases, media, or other project is modified.
The selected mix has three independent recognitions of the authored phrase;
both full-mix decoders disagree. This reconciles machine-content evidence only.
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import inspect
import json
import sys

ROOT = Path('D:/Github/VideoEditing')
BATCH = ROOT / 'production/batches/tech-ten-shorts-20261030'
SLUG = 'shorts-starcraft2-marine-random-firing-delay'
sys.path.insert(0, str(BATCH))
BASE_SHA = 'f03a9eda694867d0c500418412d53770ccf372b931bb5db35ca4f9e8c1f79b76'
if hashlib.sha256((BATCH / 'run-batch.py').read_bytes()).hexdigest() != BASE_SHA:
    raise RuntimeError('Common runner pin changed before import')
spec = importlib.util.spec_from_file_location('marine_scoped_runner', BATCH / 'run-batch.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
VOICE_SHA = '8ae03352e9520e11f4dff5943b610a36a84e5f439072f901f5da368e234b8735'
MIX_SHA = '9e54ebb091bb7719f1e3a5bc187c16161179ff8abab93b6a7e889fe9c5343987'
SCRIPT_SHA = '98de67b58a1be7096bec6874151249bf24d1e37d463202f63cc36c5064dcb8bd'
RAW_SHA = '8ea1d9b5c75a18dffd9d5bb78fb3606cb590768bc7625db74a31456a89e9a664'
BEFORE = '일점영이초를기다리는시기입니다'
AFTER = '일점영이초를기다리는식입니다'
ctx = r.make_context(SLUG)
P, A = ctx['P'], ctx['L']
RAW = A / 'asr-mix-9e54ebb091bb.json'
RECEIPT = A / 'asr-mix-reconciliation.json'
PINS = {
    BATCH / 'run-batch.py': BASE_SHA,
    ctx['VOICE']: VOICE_SHA,
    A / 'final-mix.m4a': MIX_SHA,
    P / 'script/narration.spoken.ko.json': SCRIPT_SHA,
    RAW: RAW_SHA,
    A / 'asr-voice-8ae03352e952.json': '965a13342a94ab7065104fc704d913eb87b651425b1d9524132d9378c3aa4deb',
    A / 'independent-asr/recognition-selected-paragraphs-8ae03352e952.json': '0a37c46790ed43e5ba69e283e9f37d17a0fe594eedc5b4cbb31492b800ff7e1e',
    A / 'independent-asr/mix-9e54ebb091bb/paragraphs.json': '5434ca8cf71458116179c395a60956439e5029ab2b20a94560fe8f5b97e5ba5d',
    A / 'independent-asr/mix-9e54ebb091bb/full-mix-beam3.json': '32f8de6e2e80989a3f4ac41f5376be163a0d499e84cc157f3c1bc43901809e7a',
}

def verify_pins():
    for path, digest in PINS.items():
        if not path.is_file() or r.sha(path) != digest:
            raise RuntimeError('Marine bounded evidence changed: ' + str(path))

verify_pins()
original = r.validate_asr_reconciliation
source = inspect.getsource(original)
old = "require((a, b) == ('그값을찾아주는시기죠', '그값을찾아주는식이죠'),"
new = "require((a, b) in {('그값을찾아주는시기죠', '그값을찾아주는식이죠'), ('" + BEFORE + "', '" + AFTER + "')},"
assert source.count(old) == 1
namespace = dict(vars(r))
exec(compile(source.replace(old, new), str(__file__) + ':exact-boundary-extension', 'exec'), namespace)
extended = namespace['validate_asr_reconciliation']

def validate(path, report_path, input_source, voice, script, expected, aliases):
    if Path(input_source).resolve() != (A / 'final-mix.m4a').resolve():
        return original(path, report_path, input_source, voice, script, expected, aliases)
    verify_pins()
    if Path(report_path).resolve() != RAW.resolve() or Path(voice).resolve() != ctx['VOICE'].resolve() or Path(script).resolve() != (P / 'script/narration.spoken.ko.json').resolve():
        raise RuntimeError('Marine exact input paths differ')
    review = r.read(path)
    # The current alias already maps the exact Arabic numeral in StarCraft II.
    # Match its ASR whitespace variant without changing display or source text.
    if aliases.get('스타크래프트2') != '스타크래프트 투':
        raise RuntimeError('Existing StarCraft II numeral alias changed')
    aliases = {**aliases, '스타크래프트 2': aliases['스타크래프트2']}
    norm = lambda text: r.normalize_speech(text, aliases)
    changes = [c for c in review['changes'] if c.get('kind') == 'contextual-method-liaison-orthography']
    if len(changes) != 1 or (norm(changes[0]['source']), norm(changes[0]['target'])) != (BEFORE, AFTER):
        raise RuntimeError('Marine exact word-boundary phrase differs')
    required = {'original-full-voice', 'independent-paragraphs', 'independent-mix-paragraphs'}
    if set(changes[0]['evidenceIds']) != required:
        raise RuntimeError('Marine exact independent evidence set differs')
    expected_refs = {
        'original-full-voice': A / 'asr-voice-8ae03352e952.json',
        'independent-paragraphs': A / 'independent-asr/recognition-selected-paragraphs-8ae03352e952.json',
        'independent-mix-paragraphs': A / 'independent-asr/mix-9e54ebb091bb/paragraphs.json',
    }
    for identifier, file in expected_refs.items():
        rows = [row for row in review['independentEvidence'] if row.get('id') == identifier]
        if len(rows) != 1 or r.evidence_path(rows[0]).resolve() != file.resolve() or rows[0].get('sha256') != PINS[file]:
            raise RuntimeError('Marine exact independent evidence file differs: ' + identifier)
    if review.get('fullMixDecoderDisagreementPreserved') is not True or review.get('actualPronunciationVerified') is not False:
        raise RuntimeError('Marine disagreement/hearing limitations were lost')
    result, files = extended(path, report_path, input_source, voice, script, expected, aliases)
    result.update(contextReviewAdapterSha256=r.sha(Path(__file__)), commonValidatorSha256=BASE_SHA,
                  selectedMixSha256=MIX_SHA, actualPronunciationVerified=False,
                  existingNumeralAliasWhitespaceVariant='스타크래프트 2',
                  fullMixDecoderDisagreementPreserved=True,
                  scope='Only exact Marine mix word boundary; full human hearing still pending')
    return result, sorted(set(files + list(PINS) + [Path(__file__)]), key=str)

def prepare_and_test():
    aliases = r.read(P / 'script/caption-clauses.json').get('pronunciationAliases', {})
    script = P / 'script/narration.spoken.ko.json'
    expected = ' '.join(x for s in r.read(script)['scenes'] for x in s['lines'])
    review = copy.deepcopy(r.read(A / 'asr-reconciliation.json'))
    review.update(role='mix', inputSha256=MIX_SHA, asrSha256=RAW_SHA,
                  fullMixDecoderDisagreementPreserved=True, actualPronunciationVerified=False,
                  machineEvidenceScope='Same-PCM contextual word-boundary reconciliation, not listened approval',
                  remainingReview=['Listen to paragraph4 phrase and paragraph6 ending in complete final video'])
    review['aliases'][BEFORE] = AFTER
    review['changes'].append(dict(source=BEFORE, target=AFTER, kind='contextual-method-liaison-orthography',
        occurrences=1, evidenceIds=['original-full-voice', 'independent-paragraphs', 'independent-mix-paragraphs'],
        reason='Original full voice, independent same-PCM voice paragraph4, and independent exact-mix paragraph4 recognize 식입니다. Both unprompted full-mix decoders choose 시기입니다. This exact contextual word-boundary reconciliation preserves their raw disagreement and leaves actual pronunciation/full hearing pending.'))
    for identifier, filename in [('original-full-voice', 'asr-voice-8ae03352e952.json'), ('independent-mix-paragraphs', 'independent-asr/mix-9e54ebb091bb/paragraphs.json')]:
        file = A / filename
        review['independentEvidence'].append(dict(id=identifier, path=str(file), sha256=r.sha(file)))
    folder = A / 'independent-asr/mix-9e54ebb091bb/bounded-adapter-tests'
    folder.mkdir(exist_ok=True)
    positive = folder / 'positive.json'
    if positive.exists():
        assert r.read(positive) == review
    else:
        r.save(positive, review)
    args = (RAW, A / 'final-mix.m4a', ctx['VOICE'], script, expected, aliases)
    result, files = validate(positive, *args)
    tests = []
    for name, mutation in [('stale-input-hash', lambda x: x.update(inputSha256='0'*64)),
                           ('wrong-phrase', lambda x: x['changes'][-1].update(target='일점영이초를기다리는때입니다')),
                           ('missing-independent-evidence', lambda x: x['changes'][-1].update(evidenceIds=['original-full-voice']))]:
        bad = copy.deepcopy(review); mutation(bad); file = folder / (name + '.json'); r.save(file, bad)
        try:
            validate(file, *args)
        except RuntimeError as error:
            tests.append(dict(name=name, rejected=True, reason=str(error)))
        else:
            raise RuntimeError('Negative test incorrectly accepted: ' + name)
    if RECEIPT.exists():
        assert r.read(RECEIPT) == review
    else:
        r.save(RECEIPT, review)
    evidence = dict(createdAt=r.now(), positive=result, negativeTests=tests,
                    adapter=r.artifact(Path(__file__)), evidence=[r.artifact(x) for x in PINS],
                    rawAsrUnmodified=True, mediaUnchanged=True, actualListening='pending', humanListening='pending')
    r.save(folder / 'test-results.json', evidence)
    print(json.dumps(evidence, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        prepare_and_test()
    else:
        if '--slug' not in sys.argv or sys.argv.count('--slug') != 1 or sys.argv[sys.argv.index('--slug')+1] != SLUG:
            raise RuntimeError('Only exact Marine slug is permitted')
        r.validate_asr_reconciliation = validate
        r.main()
