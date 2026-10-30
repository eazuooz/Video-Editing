"""Commit exact editable scene assets with isolated indices and narrow overlays."""
from pathlib import Path
import importlib.util, hashlib, json, re, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
module=importlib.util.spec_from_file_location('scene_transaction',ROOT/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py')
engine=importlib.util.module_from_spec(module);module.loader.exec_module(engine)
I='shared/git-essential-images.json';G='.gitignore'
engine.SHARED={I,G}
NATIVE_YAML=[]
original_git=engine.git

def checked_git(*args, **kwargs):
    # Unity serializes empty scalar values with one trailing space. Retain the
    # exact saved-scene bytes/hashes, while rejecting every other whitespace
    # defect. Exclusions apply only to this transaction's explicit YAML paths.
    if 'diff' in args and '--cached' in args and '--check' in args:
        for name in NATIVE_YAML:
            raw=original_git('show', ':'+name, env=kwargs.get('env'))
            for line in raw.decode('utf-8-sig').splitlines():
                if line.rstrip(' \t')!=line:
                    assert re.fullmatch(r'\s*(?:-\s+)?[\w.-]+:[ \t]+', line), ('Non-native trailing whitespace',name,line)
                assert not re.search(r' +\t',line), ('Space before tab',name)
        return original_git(*args,'--','.',*[':(exclude,literal)'+p for p in NATIVE_YAML],**kwargs)
    return original_git(*args,**kwargs)

engine.git=checked_git

def overlay(name,raw,spec):
    if name==I:
        for entry in spec['essentialImages']:
            existing=[v for v in engine.load(raw)['entries'] if v['path']==entry['path']]
            assert not existing or existing==[entry],('Conflicting essential asset',entry['path'])
            raw=engine.upsert(raw,'entries','path',entry)
        return raw
    if name==G:
        newline=b'\r\n' if b'\r\n' in raw else b'\n'
        for entry in sorted(spec['essentialImages'],key=lambda v:v['path']):
            path=entry['path'];lines=raw.decode('utf-8-sig').splitlines()
            if '!'+path not in lines and '!/'+path not in lines:
                raw+=(b'' if raw.endswith(b'\n') else newline)+('!/'+path).encode()+newline
        return raw
    raise AssertionError(name)

def validate(spec):
    assert spec['scope']=='animation-scene-source-assets'
    paths=spec['ownedPaths'];assert paths and len(paths)==len(set(paths))
    roots=['unity/VideoEditing/Assets/VideoScenes/animation-assigning/',
      'unity/VideoEditing/Assets/VideoScenes/animation-series-v1/',
      'production/batches/animation-18-20261031/',
      'projects/animation-assigning/production/grid-v1/']
    exact={'unity/VideoEditing/Assets/VideoScenes/animation-assigning.meta',
      'unity/VideoEditing/Assets/VideoScenes/animation-series-v1.meta',
      'unity/VideoEditing/Assets/VideoScenes.meta'}
    for name in paths:
        p=ROOT/name
        assert name in exact or any(name.startswith(r) for r in roots),name
        assert p.resolve().is_relative_to(ROOT.resolve()) and p.is_file(),name
        assert '/local/' not in name and '/source-snapshots/' not in name,name
        assert p.suffix in {'.cs','.unity','.mat','.png','.meta','.json','.py'},name
    images={v['path']:v for v in spec['essentialImages']}
    assert set(images)=={name for name in paths if name.endswith('.png')}
    for name,entry in images.items():
        assert name.startswith('unity/VideoEditing/Assets/VideoScenes/animation-series-v1/Generated/ReferenceImages/')
        assert entry['purpose']=='required-scene-asset' and entry['project']=='animation-assigning'
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==entry['sha256']
    NATIVE_YAML[:]=[p for p in paths if Path(p).suffix in {'.unity','.mat','.meta'}]
    return sorted(paths)+sorted(engine.SHARED)

engine.overlay=overlay;engine.validate=validate
if __name__=='__main__':engine.main()
