"""Commit only the Animation authorization overlays, preserving foreign staging.

Uses the existing isolated-index/CAS/index-backup transaction implementation.
No production media or raw reference transcripts are included.
"""
from pathlib import Path
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import authorize

engine_path = ROOT / 'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
spec = importlib.util.spec_from_file_location('scoped_transaction', engine_path)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.SHARED = set(authorize.SHARED)

def validate(document):
    assert document['scope'] == 'animation-18-20261031-authorization'
    owned = document['ownedPaths']
    assert len(owned) == len(set(owned)) and owned
    for name in owned:
        path = ROOT / name
        assert path.resolve().is_relative_to(HERE.resolve())
        assert path.is_file() and path.suffix in {'.py', '.json', '.html'}
        assert not any(word in name for word in ['local-deps', '.info.json', 'transcript', 'exports'])
        if path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8-sig'))
    return sorted(owned) + sorted(engine.SHARED)

engine.validate = validate
engine.overlay = lambda name, raw, document: authorize.mutate(name, raw)

if __name__ == '__main__':
    engine.main()
