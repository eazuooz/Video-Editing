"""Replay-only spacing equivalent for the existing StarCraft2 numeral alias."""
from pathlib import Path
import copy, hashlib, importlib.util, json, sys
ROOT = Path('D:/Github/VideoEditing')
B = ROOT / 'production/batches/tech-ten-shorts-20261030'
SLUG = 'shorts-starcraft2-replay-input-resimulation'
BASE = 'f03a9eda694867d0c500418412d53770ccf372b931bb5db35ca4f9e8c1f79b76'
assert hashlib.sha256((B / 'run-batch.py').read_bytes()).hexdigest() == BASE
sys.path.insert(0, str(B)); s = importlib.util.spec_from_file_location('replay_runner', B / 'run-batch.py')
r = importlib.util.module_from_spec(s); s.loader.exec_module(r)
c = r.make_context(SLUG); A, P = c['L'], c['P']
RAW = A / 'asr-mix-d6a3b37f7ee7.json'; MIX = A / 'final-mix.m4a'; SCRIPT = P / 'script/narration.spoken.ko.json'
PINS = {
    B / 'run-batch.py': BASE,
    c['VOICE']: '4c49b5ff843f2446e6387382c6c570dba113432e8e202f6aa10cf88cdd1d6ae5',
    MIX: 'd6a3b37f7ee753df0d39f500dc2f3c866fe6037578f48692aec7f163f80c9d4a',
    RAW: 'b015aedd7b7475da7581228d4b220f16873e180a669baadd9d91d3c460b19d0b',
    SCRIPT: '07b2dd10836718e37fb2584f97a5a3b372163ed5f31d3466c41b10b08e4ec530',
    P / 'script/caption-clauses.json': '41c3dabd9494c509133d4d8b60d99c104ecfaedea791664c3c81c221fb2abfce',
    A / 'asr-reconciliation.json': '299b9a0665ea5b9f6ba91ae7c40e5ae684ffff1c2c5cdcb31d13d590dc770940',
}
original = r.validate_asr_reconciliation

def validate(path, report_path, source, voice, script, expected, aliases):
    if Path(source).resolve() != MIX.resolve():
        return original(path, report_path, source, voice, script, expected, aliases)
    for file, digest in PINS.items():
        if r.sha(file) != digest:
            raise RuntimeError('Replay exact evidence changed: ' + str(file))
    if Path(report_path).resolve() != RAW.resolve() or Path(script).resolve() != SCRIPT.resolve() or Path(voice).resolve() != c['VOICE'].resolve():
        raise RuntimeError('Replay exact evidence paths differ')
    if aliases.get('스타크래프트2') != '스타크래프트 투':
        raise RuntimeError('Existing numeral alias changed')
    result, paths = original(path, report_path, source, voice, script, expected, {**aliases, '스타크래프트 2': aliases['스타크래프트2']})
    result.update(existingNumeralAliasWhitespaceVariant='스타크래프트 2', adapterSha256=r.sha(Path(__file__)), commonValidatorSha256=BASE)
    return result, sorted(set(paths + list(PINS) + [Path(__file__)]), key=str)

def prepare_and_test():
    review = copy.deepcopy(r.read(A / 'asr-reconciliation.json'))
    review.update(role='mix', inputSha256=r.sha(MIX), asrSha256=r.sha(RAW))
    aliases = r.read(P / 'script/caption-clauses.json')['pronunciationAliases']
    expected = ' '.join(line for scene in r.read(SCRIPT)['scenes'] for line in scene['lines'])
    folder = A / 'independent-asr/replay-mix-spacing-tests'; folder.mkdir(exist_ok=True)
    target = folder / 'positive.json'; r.save(target, review)
    args = (RAW, MIX, c['VOICE'], SCRIPT, expected, aliases)
    result, paths = validate(target, *args)
    bad = copy.deepcopy(review); bad['inputSha256'] = '0'*64; test = folder / 'stale-input.json'; r.save(test, bad)
    try:
        validate(test, *args)
    except RuntimeError as error:
        negative = dict(staleInputRejected=True, reason=str(error))
    else:
        raise RuntimeError('Stale input was incorrectly accepted')
    output = A / 'asr-mix-reconciliation.json'
    if output.exists():
        assert r.read(output) == review
    else:
        r.save(output, review)
    receipt = dict(positive=result, negative=negative, adapter=r.artifact(Path(__file__)), rawReport=r.artifact(RAW), actualListening='pending', humanListening='pending')
    r.save(folder / 'test-results.json', receipt); print(json.dumps(receipt, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        prepare_and_test()
    else:
        if '--slug' not in sys.argv or sys.argv.count('--slug') != 1 or sys.argv[sys.argv.index('--slug')+1] != SLUG:
            raise RuntimeError('Only exact Replay slug is permitted')
        r.validate_asr_reconciliation = validate
        r.main()
