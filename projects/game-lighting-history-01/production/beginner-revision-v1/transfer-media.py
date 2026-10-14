"""Verify or export this revision's exact local media; never regenerate it.

Run from any checkout: python path/to/transfer-media.py --verify
On the source machine: python path/to/transfer-media.py --export D:/transfer/media.tar
Restore with Python tarfile data filtering into the new checkout, then --verify.
"""
import argparse, hashlib, json, pathlib, tarfile

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).parent

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--export', type=pathlib.Path)
    args = parser.parse_args()
    assert args.verify or args.export, 'Choose --verify or --export.'
    manifest = json.loads((HERE / 'handoff-media.json').read_text(encoding='utf8'))
    failed = []
    for row in manifest['files']:
        path = (ROOT / row['path']).resolve()
        assert path.is_relative_to(ROOT) and path != ROOT
        if not path.is_file():
            failed.append({'path': row['path'], 'reason': 'missing'})
        elif path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            failed.append({'path': row['path'], 'reason': 'different-bytes'})
    if failed:
        print(json.dumps({'valid': False, 'files': failed}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps({'valid': True, 'files': len(manifest['files']), 'bytes': manifest['totalBytes']}))
    if args.export:
        target = args.export.resolve()
        assert not target.exists(), 'Preserve existing transfer packages.'
        target.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(target, 'x') as archive:
            for row in manifest['files']:
                archive.add(ROOT / row['path'], arcname=row['path'], recursive=False)
            archive.add(HERE / 'handoff-media.json', arcname='projects/game-lighting-history-01/production/beginner-revision-v1/handoff-media.json')
        with tarfile.open(target, 'r') as archive:
            assert len(archive.getmembers()) == len(manifest['files']) + 1
            for row in manifest['files']:
                assert archive.getmember(row['path']).size == row['bytes']
        receipt = {'path': str(target), 'bytes': target.stat().st_size, 'sha256': sha(target),
                   'fileCount': len(manifest['files']), 'uploadedToExternalStorage': False,
                   'note': 'Local transfer package only; Git contains source and metadata, not these media bytes.'}
        target.with_suffix(target.suffix + '.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
        print(json.dumps(receipt, ensure_ascii=False))

if __name__ == '__main__':
    main()
