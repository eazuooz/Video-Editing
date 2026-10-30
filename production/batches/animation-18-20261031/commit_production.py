"""Selective Animation production commit; preserve every foreign index entry.

Uses the established isolated-index/CAS transaction. The explicit spec contains
only owned text sources and evidence; source recordings, transcripts, generated
renders, environment packages and screenshots stay local.
"""
from pathlib import Path
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
engine_path = ROOT / 'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
module = importlib.util.spec_from_file_location('scoped_transaction', engine_path)
engine = importlib.util.module_from_spec(module)
module.loader.exec_module(engine)
engine.SHARED = set()

def validate(spec):
    assert spec['scope'] == 'animation-18-production'
    paths = spec['ownedPaths']
    assert paths and len(paths) == len(set(paths))
    prefixes = ['production/batches/animation-18-20261031/',
                'projects/animation-assigning/',
                'unity/VideoEditing/Assets/VideoScenes/animation-series-v1/']
    prohibited = ['/local/', '/ocr-deps/', '/local-deps/', '/exports/', '/evidence/',
                  '/Generated/', '/source-snapshots/']
    for name in paths:
        p = ROOT / name
        assert any(name.startswith(prefix) for prefix in prefixes), name
        assert p.resolve().is_relative_to(ROOT.resolve()) and p.is_file(), name
        assert not any(part in name for part in prohibited), name
        assert not any(part in name.lower() for part in ['transcript', '.info.json', '.vtt', '.srt']), name
        assert p.suffix in {'.py', '.json', '.html', '.cs', '.cjs', '.meta', '.md'} or p.name=='narration.spoken-ko.txt', name
        if p.suffix == '.json':
            json.loads(p.read_text('utf-8-sig'))
    return sorted(paths)

engine.validate = validate
if __name__ == '__main__':
    engine.main()
