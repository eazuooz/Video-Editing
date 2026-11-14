"""Commit only this feasibility report, preserving all foreign staged work."""
import importlib.util,sys
from pathlib import PurePosixPath
from audit_pictures import HERE,ROOT,WORK,read,save

PREFIX=HERE.relative_to(ROOT).as_posix()+'/'
SPEC=WORK/'audit-commit.json'
helper=ROOT/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
module=importlib.util.spec_from_file_location('animation_audit_scoped',helper)
scoped=importlib.util.module_from_spec(module);module.loader.exec_module(scoped)

def validate(spec):
    assert spec['scope']=='animation-footage-substitution-audit-20261115'
    report=read(HERE/'report.json')
    assert report['scope']==[f'A{i:02}' for i in range(3,19)]
    assert not any(report[k] for k in ['newTtsStarted','newEngineCaptureStarted','newVideoRenderStarted','platformChanged'])
    assert report['allMastersUnchanged']
    for name in spec['ownedPaths']:
        p=PurePosixPath(name)
        assert name.startswith(PREFIX) and '..' not in p.parts and p.suffix in {'.py','.json','.html'} and (ROOT/name).is_file()
    return sorted(spec['ownedPaths'])

if __name__=='__main__':
    if sys.argv[1:]==['--prepare']:
        save(SPEC,dict(scope='animation-footage-substitution-audit-20261115',ownedPaths=sorted(p.relative_to(ROOT).as_posix()
            for p in HERE.iterdir() if p.is_file() and p.suffix in {'.py','.json','.html'})))
        print(SPEC)
    else:
        scoped.SHARED=set();scoped.validate=validate;scoped.main()
