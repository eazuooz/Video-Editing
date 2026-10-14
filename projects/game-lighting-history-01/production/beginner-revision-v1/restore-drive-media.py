"""Restore the exact user-supplied Drive handoff without replacing local variants."""
import datetime, hashlib, json, pathlib, shutil, tarfile

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).parent
ARCHIVE = pathlib.Path('C:/Users/1/Downloads/media.tar')
EXPECTED = '60173b689d3dd0737e2e060bf78f5b619eb69d39ddd88c93c79180d42472da67'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''): h.update(b)
    return h.hexdigest()

def main():
    assert ARCHIVE.stat().st_size == 6067906560
    assert sha(ARCHIVE) == EXPECTED, 'Archive checksum mismatch; do not extract.'
    manifest = json.loads((HERE/'handoff-media.json').read_text(encoding='utf8'))
    expected = {r['path']: r for r in manifest['files']}
    manifest_name = (HERE/'handoff-media.json').relative_to(ROOT).as_posix()
    restored = []; retained = []
    with tarfile.open(ARCHIVE, 'r') as archive:
        members = archive.getmembers()
        assert len(members) == len(expected)+1
        assert {m.name for m in members} == set(expected)|{manifest_name}
        for m in members:
            assert m.isfile() and not m.issym() and not m.islnk()
            target = (ROOT/m.name).resolve()
            assert target.is_relative_to(ROOT) and target != ROOT
            if m.name == manifest_name: continue
            row = expected[m.name]
            assert m.size == row['bytes']
            if target.exists():
                assert target.is_file() and target.stat().st_size == row['bytes'] and sha(target) == row['sha256'], f'Preserve differing local file: {m.name}'
                retained.append(m.name); continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(m) as src, target.open('xb') as dst:
                shutil.copyfileobj(src, dst, 8*1024*1024)
            assert sha(target) == row['sha256'], m.name
            restored.append(m.name)
    receipt = dict(completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        archiveDriveId='1y84MKGL6BC5oJfX2un1-1-r-Qi0gBIjX', archivePath=str(ARCHIVE),
        archiveSha256=EXPECTED, verifiedFiles=len(expected), verifiedBytes=manifest['totalBytes'],
        restoredFiles=len(restored), identicalExistingFiles=len(retained), allMediaHashesVerified=True,
        regeneratedMedia=False, priorVersionsPreserved=True)
    (HERE/'drive-recovery-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps(receipt), flush=True)

if __name__ == '__main__': main()
