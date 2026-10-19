"""Commit selected paths; merge only owned fields or anchored document sections."""
from pathlib import Path
import copy, datetime, json, os, shutil, subprocess, sys

R = Path(__file__).resolve().parents[3]
P = Path(__file__).resolve().parents[1]
unit, message, manifest = sys.argv[1:4]
spec = json.loads(Path(manifest).read_text(encoding='utf8'))
paths = sorted(set(spec['paths']))
control = 'shared/publishing/video-production-control.json'
registry = 'shared/git-essential-images.json'
ignore = '.gitignore'
sections = spec.get('sections', {})
assert isinstance(sections, dict), 'sections must map repository paths to start/end selectors.'
assert not set(sections) & {control, registry, ignore}, 'Section paths must not overlap JSON/image-policy merges.'
for path, selector in sections.items():
    assert isinstance(path, str) and path and not Path(path).is_absolute()
    assert '\\' not in path and '..' not in path.split('/'), 'Use repository-relative POSIX paths.'
    assert isinstance(selector, dict) and set(selector) <= {'start', 'end'}
    assert isinstance(selector.get('start'), str) and selector['start']
    assert selector.get('end') is None or isinstance(selector['end'], str) and selector['end']
    assert all('\n' not in value and '\r' not in value
               for value in selector.values() if isinstance(value, str))
mixed = list(dict.fromkeys([control] + ([registry, ignore] if spec.get('assets') else []) + list(sections)))
assert not set(paths) & set(mixed)
O = R / 'shared/output/shorts-commits' / unit
O.mkdir(parents=True, exist_ok=True)
assert not (O/'receipt.json').exists() and not (O/'commit.index').exists()

def git(*args, env=None, data=None):
    r = subprocess.run(['git', *args], cwd=R, env=env, input=data, capture_output=True)
    if r.returncode:
        raise RuntimeError((r.stdout+r.stderr).decode(errors='replace')[-3000:])
    return r.stdout

def read_revision(ref, path):
    return git('show', ref+':'+path).decode('utf8')

def section_bounds(text, selector):
    """Find one line-anchored prefix, ending before one later prefix or at EOF.

    A prefix such as ``## 9. `` survives a title change. Non-owned prefix/suffix
    text is copied verbatim from the destination (HEAD or the original index).
    Missing or ambiguous anchors fail before any branch/index update.
    """
    offsets, position = [], 0
    for line in text.splitlines(keepends=True):
        offsets.append((position, line))
        position += len(line)
    starts = [(offset, line) for offset, line in offsets if line.startswith(selector['start'])]
    assert len(starts) == 1, 'Section start must match exactly one anchored line: '+repr(selector['start'])
    start, heading = starts[0]
    if selector.get('end') is None:
        return start, len(text)
    ends = [offset for offset, line in offsets
            if offset >= start+len(heading) and line.startswith(selector['end'])]
    assert len(ends) == 1, 'Section end must match exactly one later anchored line: '+repr(selector['end'])
    return start, ends[0]

def merge(path, base, working):
    if path in sections:
        base_start, base_end = section_bounds(base, sections[path])
        work_start, work_end = section_bounds(working, sections[path])
        return base[:base_start]+working[work_start:work_end]+base[base_end:]
    if path == ignore:
        lines = ['# User-requested original Yamyam cat reaction source sprites (exact essential registry entries).']
        lines += ['!/'+p for p in spec['assets']]
        return base.rstrip()+'\n\n'+'\n'.join(x for x in lines if x not in base.splitlines())+'\n'
    out, current = json.loads(base), json.loads(working)
    if path == control:
        for field in spec.get('controlFields', ['shortsRecurringAuthorization']):
            out[field] = copy.deepcopy(current[field])
    else:
        owned = set(spec['assets'])
        keep = [e for e in out['entries'] if e['path'] not in owned]
        out['entries'] = keep + [e for e in current['entries'] if e['path'] in owned]
    return json.dumps(out, ensure_ascii=False, indent=2)+'\n'

def blob(text):
    return git('hash-object','-w','--stdin',data=text.encode('utf8')).decode().strip()

owned = set(paths+mixed)
def foreign():
    return [x for x in git('ls-files','--stage','-z').split(b'\0')
            if x and x.split(b'\t',1)[1].decode() not in owned]

before = foreign()
base = git('rev-parse','HEAD').decode().strip()
ref = git('symbolic-ref','HEAD').decode().strip()
shutil.copy2(R/'.git/index', O/'index-before.bin')
previous = {p: read_revision('',p) for p in mixed}
working = {p: (R/p).read_text(encoding='utf8') for p in mixed}
env = dict(os.environ, GIT_INDEX_FILE=str(O/'commit.index'))
git('read-tree',base,env=env)
git('add','--',*paths,env=env)
for p in mixed:
    git('update-index','--add','--cacheinfo','100644',blob(merge(p,read_revision(base,p),working[p])),p,env=env)
git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
changed = [p for p in git('diff','--cached','--name-only','-z',env=env).decode().split('\0') if p]
assert changed and set(changed) <= owned
tree = git('write-tree',env=env).decode().strip()
assert git('rev-parse','HEAD').decode().strip() == base, 'HEAD changed; rebuild from new HEAD.'
commit = git('commit-tree',tree,'-p',base,'-m',message).decode().strip()
git('update-ref',ref,commit,base)
git('reset','-q','HEAD','--',*paths)
for p in mixed:
    git('update-index','--add','--cacheinfo','100644',blob(merge(p,previous[p],working[p])),p)
assert foreign() == before
receipt = dict(commit=commit,parent=base,paths=changed,foreignIndexPreserved=True,
               mixedControlFields=spec.get('controlFields',['shortsRecurringAuthorization']),
               mixedSections=copy.deepcopy(sections),
               at=datetime.datetime.now(datetime.timezone.utc).isoformat(),remoteSha=None)
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
git('push','origin','HEAD:'+ref)
remote = git('ls-remote','origin',ref).decode().split()[0]
assert remote == commit
receipt['remoteSha'] = remote
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print(json.dumps(receipt))
