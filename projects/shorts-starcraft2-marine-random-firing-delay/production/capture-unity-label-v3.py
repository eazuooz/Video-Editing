"""Marine-only source selection; retain the hash-pinned native capture algorithm."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parents[2]
BATCH = ROOT / 'production/batches/tech-ten-shorts-20261030'
SLUG = 'shorts-starcraft2-marine-random-firing-delay'
BASE_SHA256 = 'b4ec0e2c742af0f3cb3e74ab5dff5dd5e052790d50b6c8b58dde97c3cf9af806'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_code():
    base = BATCH / 'capture-unity.py'
    if sha(base) != BASE_SHA256:
        raise RuntimeError('Native capture base changed; inspect before re-pinning.')
    manifest = json.loads((PRODUCTION / 'label-v3-source-manifest.json').read_text(encoding='utf8'))
    source = PRODUCTION / 'native-source-label-v3'
    files = {p.relative_to(source).as_posix(): sha(p) for p in source.rglob('*') if p.is_file()}
    if (manifest['slug'] != SLUG or manifest['baseCaptureSHA256'] != BASE_SHA256
            or files != manifest['variantSourceCode'] or len(files) != 14):
        raise RuntimeError('The exact Marine source variant changed.')
    text = base.read_text(encoding='utf8')
    token = "source = BATCH / 'unity-source'"
    if text.count(token) != 1:
        raise RuntimeError('Source selector is no longer the exact reviewed single occurrence.')
    adapted = text.replace(token, 'source = Path(' + repr(source.as_posix()) + ')')
    return base, compile(adapted, str(base) + ':marine-label-v3', 'exec'), manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slug', choices=[SLUG])
    parser.add_argument('--inspect', action='store_true', help='Compile and verify only; never import or launch the capture runner.')
    args = parser.parse_args()
    base, code, manifest = checked_code()
    if args.inspect:
        print(json.dumps({'slug': SLUG, 'baseSHA256': BASE_SHA256,
                          'variantSourceTreeSHA256': manifest['variantSourceTreeSHA256'],
                          'onlyAdaptation': 'one source-directory selection', 'captureStarted': False}))
        return
    sys.path.insert(0, str(BATCH))
    from scoped_context import make_context, read
    ctx = make_context(SLUG)
    ctx['guard']()
    prepared = ctx['LOCAL'].resolve() / 'label-v3-preparation'
    receipt = prepared / 'native-archive-receipt.json'
    if not receipt.is_file():
        raise RuntimeError('Marine v2 cannot capture until the old native tree is preserved by prepare-label-v3.py --archive-native.')
    record = read(receipt)
    if record.get('slug') != SLUG or record.get('variantSourceTreeSHA256') != manifest['variantSourceTreeSHA256']:
        raise RuntimeError('Native archive proof does not identify this exact revision.')
    for item in record['preservedFiles']:
        target = Path(item['archivedPath'])
        if not target.is_file() or target.stat().st_size != item['bytes'] or sha(target) != item['sha256']:
            raise RuntimeError('Preserved native artifact changed: ' + str(target))
    namespace = {'__file__': str(base), '__name__': 'marine_label_v2_capture'}
    exec(code, namespace)
    previous = sys.argv
    try:
        sys.argv = [str(base), SLUG]
        namespace['main']()  # Original guards, locks, lease, timing and output checks remain intact.
    finally:
        sys.argv = previous


if __name__ == '__main__':
    main()
