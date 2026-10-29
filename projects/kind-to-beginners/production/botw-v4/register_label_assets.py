"""Register only typography used by the reviewed, final D29 native captures."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import upsert


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    pixels = read(HERE / 'pixel-review.json')
    assert pixels['status'] == 'passed'
    assert pixels['editPlanSha256'] == sha(HERE / 'edit-plan.json')
    binding = read(HERE / 'native-binding.json')
    inventory = read(HERE / 'label-assets-measured-v2.json')
    assert inventory['status'] == 'final-native-used-texture-candidates'
    assert inventory['capturePhase'] == 'render' and inventory['captureVariant'] == 'measured-v2'
    captures = {c['cutId']: c for c in binding['captures']}
    entries = []
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    prefix = 'unity/VideoEditing/Assets/VideoScenes/design-d29-botw-v4/Generated/ReferenceImages/'
    for item in inventory['assets']:
        assert item['assetPath'].startswith(prefix) and item['assetPath'].endswith('.png')
        assert item['uses']
        for use in item['uses']:
            capture = captures[use['cutId']]
            assert capture['scene'].endswith(use['scene'])
            receipt = ROOT / use['receipt']
            assert sha(receipt) == capture['successSha256']
            relative_asset = item['assetPath'].removeprefix('unity/VideoEditing/')
            assert relative_asset in read(receipt)['assets']
        assert sha(ROOT / item['assetPath']) == item['sha256']
        assert sha(ROOT / item['metaPath']) == item['metaSha256']
        entries.append({
            'path': item['assetPath'], 'purpose': 'required-scene-asset',
            'reason': 'Own rasterized typography referenced by final D29 captures as saved-scene or animated-label assets. Source footage, QA images and unreferenced generated combinations are excluded.',
            'sha256': item['sha256'], 'reviewedAt': stamp,
            'project': 'kind-to-beginners', 'revision': 'botw-v4',
            'text': item['text'], 'uses': [u['cutId'] for u in item['uses']],
            'fontBinaryRedistributed': False,
        })
    assert entries and len({e['path'] for e in entries}) == len(entries)
    registry_path, ignore_path = ROOT / 'shared/git-essential-images.json', ROOT / '.gitignore'
    old_registry, old_ignore = registry_path.read_bytes(), ignore_path.read_bytes()
    registry, ignore = old_registry, old_ignore
    for item in entries:
        registry = upsert(registry, 'entries', 'path', item)
    lines = ignore.decode('utf-8-sig').splitlines()
    newline = b'\r\n' if b'\r\n' in ignore else b'\n'
    for item in entries:
        exception = '!' + item['path']
        if exception not in lines and '!/' + item['path'] not in lines:
            ignore += (b'' if ignore.endswith(b'\n') else newline) + exception.encode('utf-8') + newline
            lines.append(exception)
    assert registry_path.read_bytes() == old_registry and ignore_path.read_bytes() == old_ignore, 'Concurrent shared-file edit; retry from fresh bytes.'
    registry_path.write_bytes(registry)
    ignore_path.write_bytes(ignore)
    record = {'revision': 'botw-v4', 'status': 'reviewed-final-scene-assets',
              'inventory': str((HERE / 'label-assets-measured-v2.json').relative_to(ROOT)).replace('\\', '/'),
              'inventorySha256': sha(HERE / 'label-assets-measured-v2.json'),
              'pixelReviewSha256': sha(HERE / 'pixel-review.json'), 'entries': entries}
    (HERE / 'essential-label-images.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(f'Registered {len(entries)} final-used typography textures; other shared entries retained.')


if __name__ == '__main__':
    main()
