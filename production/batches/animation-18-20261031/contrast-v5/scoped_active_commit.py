"""Commit approved-roster progress without consuming unrelated staged work."""
from pathlib import Path, PurePosixPath
import importlib.util
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('scope', ROOT/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
C = 'shared/publishing/video-production-control.json'
W = 'shared/publishing/video-worklist.json'
D = 'docs/VIDEO_WORKLIST.md'
IDS = {f'A{i:02}' for i in range(1,19) if i != 3}

def overlay(name, raw, value):
    if name == C:
        return mod.patch(raw, ['animationContrastRevision20261108'], value['control'])
    if name == W:
        for entry in value['worklist']:
            assert entry['id'] in IDS
            rows = mod.load(raw)['rows']
            indices = [i for i, row in enumerate(rows) if row['id'] == entry['id']]
            assert len(indices) == 1
            for key, item in entry['set'].items():
                assert key in {'executionStatus','contrastRevision','updatedAt'}
                raw = mod.patch(raw, ['rows',indices[0],key], item)
        return raw
    if name == D:
        text = raw.decode('utf-8-sig')
        for identity in sorted(IDS):
            matches = re.findall(r'^\| '+identity+r' \| .*?$', text, re.M)
            assert len(matches) == 1
            old = matches[0]
            parts = old.rstrip('\r').rsplit('|',2)
            assert len(parts) == 3
            new = parts[0]+'| '+value['markdownStatus']+' |'+ ('\r' if old.endswith('\r') else '')
            text = text.replace(old,new)
        return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+text.encode('utf-8')
    raise AssertionError(name)

def validate(value):
    assert value['scope'] == 'animation-17-approved-roster-production-20261108'
    control = value['control']
    assert set(control['episodes']) == IDS
    assert control['renderAuthorized'] and control['fullLocalProductionAuthorized']
    assert control['candidateUserApproval']['text'] == '이 목록으로 진행'
    assert not any(control[x] for x in ['youtubeAuthorized','schedulingAuthorized','deletionAuthorized'])
    assert {row['id'] for row in value['worklist']} == IDS
    paths = value['ownedPaths']
    assert len(paths) == len(set(paths))
    for name in paths:
        p = PurePosixPath(name)
        assert not p.is_absolute() and '..' not in p.parts
        assert name.startswith('production/batches/animation-18-20261031/contrast-v5/') and '/local/' not in name
        assert p.suffix in {'.json','.md','.py','.txt'}
        assert (ROOT/name).is_file()
    return sorted(paths)+sorted(mod.SHARED)

mod.SHARED = {C,W,D}
mod.overlay = overlay
mod.validate = validate
if __name__ == '__main__':
    if '--spec' not in sys.argv:
        sys.argv[1:1] = ['--spec',str(HERE/'active-commit-spec.json')]
    mod.main()
