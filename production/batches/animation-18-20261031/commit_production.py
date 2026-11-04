"""Selective Animation production commit; preserve every foreign index entry.

Uses the established isolated-index/CAS transaction. The explicit spec contains
only owned text sources and evidence; source recordings, transcripts, generated
renders, environment packages and screenshots stay local.
"""
from pathlib import Path
import importlib.util
import json
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
engine_path = ROOT / 'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
module = importlib.util.spec_from_file_location('scoped_transaction', engine_path)
engine = importlib.util.module_from_spec(module)
module.loader.exec_module(engine)
engine.SHARED = set()
native_meta_paths = []
original_git = engine.git

def checked_git(*args, **kwargs):
    if 'diff' in args and '--cached' in args and '--check' in args and native_meta_paths:
        # Unity writes a trailing space for empty YAML scalars. Preserve exact
        # importer identity bytes; exempt only validated selected native metas.
        for name in native_meta_paths:
            raw = original_git('show', ':' + name, env=kwargs.get('env'))
            for line in raw.decode('utf-8-sig').splitlines():
                if line.rstrip(' \t') != line:
                    assert re.fullmatch(r' *(?:- +)?[\w.-]+: +', line), (name, line)
                assert not re.search(r' +\t', line), (name, 'space before tab')
                assert not re.match(r'^(?:<<<<<<<|=======|>>>>>>>)', line), (name, 'conflict marker')
        args = (*args, '--', '.', *[':(exclude,literal)' + name for name in native_meta_paths])
    return original_git(*args, **kwargs)

engine.git = checked_git

def validate(spec):
    global native_meta_paths
    assert spec['scope'] == 'animation-18-production'
    paths = spec['ownedPaths']
    assert paths and len(paths) == len(set(paths))
    prefixes = ['production/batches/animation-18-20261031/',
                'projects/animation-assigning/',
                'projects/animation-exaggeration/',
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
    native_meta_paths = [name for name in paths if name.startswith('unity/') and name.endswith('.meta')]
    return sorted(paths)

engine.validate = validate
if __name__ == '__main__':
    engine.main()
