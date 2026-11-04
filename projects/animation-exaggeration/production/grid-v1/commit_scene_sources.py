"""A02 exact source transaction; default is read-only.

--apply-shared adds only verified A02 label rows/exceptions to working files.
--execute uses isolated indices, preserving foreign staging. --push is separate.
The source collector must have verified all 23 final current-fingerprint renders.
This A02 copy retains the established transaction mechanism without modifying A01.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,os,re,subprocess,sys,uuid

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
HOME=HERE.relative_to(ROOT).as_posix()+'/'
sys.path.insert(0,str(ROOT/'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import load,upsert
import prepare_scene_sources as source

I='shared/git-essential-images.json';G='.gitignore'
SHARED={I,G}
NATIVE_YAML=[]
CAPTURED_TEXT_WITH_LEGACY_NEWLINES={
 'unity/VideoEditing/Assets/VideoScenes/animation-series-v1/AnimationLessonStage.cs':
 '8fc7f2478dee882a31eafe77d65cb928df352ade07ce7bd315018c66414ec19c'
}

def sha(raw):return hashlib.sha256(raw).hexdigest()

def git(*args,env=None,data=None,optional=False):
    merged=os.environ.copy();merged['GIT_OPTIONAL_LOCKS']='0'
    if env:merged.update(env)
    if 'diff' in args and '--cached' in args and '--check' in args and NATIVE_YAML:
        # The exact raw native blobs are checked in full before only these paths
        # are excluded from Git's empty-scalar trailing-space false positives.
        for name in NATIVE_YAML:
            raw=git('show',':'+name,env=env)
            lines=raw.decode('utf-8-sig').splitlines()
            for line in lines:
                if line.rstrip(' \t')!=line:
                    assert re.fullmatch(r' *(?:- +)?[\w.-]+: +',line),('Non-native trailing whitespace',name,line)
                assert not re.search(r' +\t',line),('Space before tab',name)
                assert not re.match(r'^(?:<<<<<<<|=======|>>>>>>>)',line),('Conflict marker',name)
            assert not lines or lines[-1].strip(),('Extra blank line at EOF',name)
        # Windows limits one command line to32K. Hundreds of literal long paths
        # exceed it. First establish that every changed native YAML path was
        # individually validated above, then use three compact suffix filters.
        base=args[args.index('--check')+1]
        changed=git('diff','--cached','--name-only','-z',base,env=env).decode('utf8').split('\0')
        native_changed={p for p in changed if Path(p).suffix in {'.unity','.mat','.meta'}}
        assert native_changed<=set(NATIVE_YAML),('Unvalidated native YAML change',native_changed-set(NATIVE_YAML))
        # The compiled/rendered shared stage contains legacy CR-only and repeated
        # CR line endings. Its frozen SHA must stay exact. Check logical lines
        # without rewriting bytes or invalidating the captured source identity.
        for name,expected in CAPTURED_TEXT_WITH_LEGACY_NEWLINES.items():
            raw=git('show',':'+name,env=env)
            assert sha(raw)==expected,('Captured legacy text changed',name)
            lines=raw.decode('utf-8-sig').splitlines()
            for line in lines:
                assert line.rstrip(' \t')==line,('Actual trailing whitespace',name,line)
                assert not re.search(r' +\t',line),('Space before tab',name)
                assert not re.match(r'^(?:<<<<<<<|=======|>>>>>>>)',line),('Conflict marker',name)
        args=(*args,'--','.',*[':(exclude,glob)**/*'+suffix for suffix in ('.unity','.mat','.meta')],
              *[':(exclude,literal)'+name for name in CAPTURED_TEXT_WITH_LEGACY_NEWLINES])
    result=subprocess.run(['git',*args],cwd=ROOT,env=merged,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if result.returncode:
        if optional:return None
        raise RuntimeError((result.stdout+result.stderr).decode('utf8','replace')[:6000])
    return result.stdout

def overlay(name,raw,spec):
    if name==I:
        original=load(raw)
        for entry in spec['essentialImages']:
            existing=[v for v in load(raw)['entries'] if v['path']==entry['path']]
            assert not existing or existing==[entry],('Conflicting essential image',entry['path'])
            raw=upsert(raw,'entries','path',entry)
        wanted={x['path'] for x in spec['essentialImages']}
        assert [x for x in load(raw)['entries'] if x['path'] not in wanted]==[x for x in original['entries'] if x['path'] not in wanted]
        return raw
    if name==G:
        newline=b'\r\n' if b'\r\n' in raw else b'\n'
        for item in sorted(spec['essentialImages'],key=lambda x:x['path']):
            path=item['path'];lines=raw.decode('utf-8-sig').splitlines()
            if '!'+path not in lines and '!/'+path not in lines:
                raw+=(b'' if raw.endswith(b'\n') else newline)+('!/'+path).encode()+newline
        return raw
    raise AssertionError(name)

def validate(spec):
    assert spec['scope']==source.SCOPE and spec['episode']=='A02' and spec['expectedFinalSceneCount']==23
    assert spec['runtimeComplete'] and not spec['sourceRedistributionAllowed']
    assert spec['sourceFingerprint']==source.EXPECTED_FINGERPRINT
    assert spec['manifest']['path']==HOME+'saved-scene-source-manifest.json'
    source.check_artifact(spec['manifest']);manifest=source.read(ROOT/spec['manifest']['path'])
    assert manifest['sourceFingerprint']==source.EXPECTED_FINGERPRINT and len(manifest['scenes'])==23
    assert not manifest['selectedSourceUnresolvedGuids'] and not manifest['missingMetas'] and not manifest['vendorBytesSelectedForCommit']
    environment=manifest['externalEnvironmentUnresolvedGuids']
    assert manifest['unresolvedGuids']==environment==spec['externalEnvironmentUnresolvedGuids']
    assert len(environment)<=len(source.KNOWN_EXTERNAL_DEBUG_REFERENCES)
    assert len({(x['path'],x['guid']) for x in environment})==len(environment)
    assert manifest['legacyExternalResourceEvidence']==spec['legacyExternalResourceEvidence']==(source.LEGACY_RESOURCE_EVIDENCE if environment else [])
    for evidence in spec['legacyExternalResourceEvidence']:source.check_artifact(evidence)
    for item in environment:
        matches=[x for x in source.KNOWN_EXTERNAL_DEBUG_REFERENCES if x['path']==item['path'] and x['guid']==item['guid']]
        assert len(matches)==1
        for key,value in matches[0].items():assert item[key]==value
        source.check_artifact(item)
        assert item['resolved'] is False and item['unityOrResourceRestored'] is False and item['sourceAssetClosureExceptionOnly']
    a01=source.preserved_a01();assert a01==spec['a01Preservation']==manifest['a01Preservation']
    freeze,stage,ack=source.verify_freeze()
    queue=source.read(HERE/'edit-plan.json')['nativeCaptureQueue']
    assert len(queue)==23
    current_scenes,_,_=source.verify_runtime(queue,stage,ack)
    assert current_scenes==manifest['scenes'],'Final runtime receipts changed'
    assert spec['verificationInputs']==manifest['verificationInputs']
    for item in spec['verificationInputs']:source.check_artifact(item)
    for item in manifest['files']:source.check_artifact(item)
    paths=spec['ownedPaths'];assert paths and len(paths)==len(set(paths))
    recorded={x['path']:x for x in spec['ownedFiles']}
    assert set(recorded)==set(paths)-{HOME+'scene-source-commit-plan.json'}
    for item in recorded.values():source.check_artifact(item)
    assert manifest['essentialImages']==spec['essentialImages']
    image_paths={x['path'] for x in spec['essentialImages']}
    assert image_paths=={p for p in paths if p.lower().endswith('.png')}
    assert len(image_paths)==manifest['generatedRasterCount']>0
    c=source.rel(source.C);a=source.rel(source.A)
    explicit={c+'/'+n for n in source.SHARED_SOURCE_NAMES}
    explicit|={n+'.meta' for n in list(explicit)}
    explicit|={c+'.meta',c+'/Editor.meta','unity/VideoEditing/Assets/VideoScenes.meta',
      'unity/VideoEditing/Assets/VideoScenes/animation-exaggeration.meta'}
    allowed_h={HOME+x for x in ('prepare_scene_sources.py','commit_scene_sources.py','saved-scene-source-manifest.json','scene-source-commit-plan.json')}
    allowed_h|={x['path'] for x in freeze['files'] if (ROOT/x['path']).parent==HERE}
    selected_scene_paths={x['scene'] for x in manifest['scenes']}
    for name in paths:
        pure=PurePosixPath(name)
        assert not pure.is_absolute() and '..' not in pure.parts and str(pure)==name and not any(c in name for c in '\\\x00\r\n')
        assert '/local/' not in name and '/ThirdParty/' not in name and '/Preflight/' not in name and '/source-snapshots/' not in name
        assert name in explicit or name in allowed_h or name.startswith(a+'/') or name==a+'.meta',('Outside A02 exact source scope',name)
        assert pure.suffix in {'.cs','.unity','.mat','.png','.meta','.json','.py'}
        p=ROOT/name;assert p.is_file() and p.resolve().is_relative_to(ROOT.resolve())
        if pure.suffix=='.unity':assert name in selected_scene_paths
        if pure.suffix=='.png':assert name.startswith(a+'/Generated/ReferenceImages/')
    for entry in spec['essentialImages']:
        assert entry['purpose']=='required-scene-asset' and entry['project']=='animation-exaggeration'
        assert sha((ROOT/entry['path']).read_bytes())==entry['sha256']==Path(entry['path']).stem
        provenance=source.read(Path(str(ROOT/entry['path'])+'.source.json'))
        assert provenance['sha256']==entry['sha256'] and Path(provenance['source']).resolve().is_relative_to((source.L/'label-cache').resolve())
    NATIVE_YAML[:]=[p for p in paths if Path(p).suffix in {'.unity','.mat','.meta'}]
    return sorted(paths)+sorted(SHARED)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec', default=str(ROOT / HOME / 'scene-source-commit-plan.json'))
    parser.add_argument('--apply-shared', action='store_true', help='Only explicit working-tree shared overlays; no Git')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--push', action='store_true')
    parser.add_argument('--message', default='Preserve A02 native scenes and exact source dependencies')
    args = parser.parse_args()
    assert not args.push or args.execute
    assert not (args.apply_shared and (args.execute or args.push))
    spec_path = Path(args.spec); spec_raw = spec_path.read_bytes(); spec = load(spec_raw)
    paths = validate(spec)
    work = {name: (ROOT / name).read_bytes() for name in paths}
    proposed_shared = {name: overlay(name, work[name], spec) for name in SHARED}
    if args.apply_shared:
        # Checks for all files precede any write. This mode never touches Git.
        assert spec_path.read_bytes() == spec_raw
        assert all((ROOT / name).read_bytes() == raw for name, raw in work.items())
        for name, raw in proposed_shared.items():
            if raw != work[name]:
                assert (ROOT / name).read_bytes() == work[name]
                (ROOT / name).write_bytes(raw)
        print(json.dumps({'status': 'explicit-shared-overlays-applied', 'gitTouched': False}, ensure_ascii=False))
        return
    base = git('rev-parse', 'HEAD').strip().decode()
    branch = git('symbolic-ref', '--quiet', 'HEAD').strip().decode()
    assert branch.startswith('refs/heads/codex/')
    index = Path(git('rev-parse', '--git-path', 'index').strip().decode())
    if not index.is_absolute(): index = ROOT / index
    original_index = index.read_bytes()
    heads = {name: git('show', base + ':' + name) for name in SHARED}
    indexed = {name: git('show', ':' + name) for name in SHARED}
    assert index.read_bytes() == original_index
    committed = {name: overlay(name, heads[name], spec) if name in SHARED else work[name] for name in paths}
    synced = {name: overlay(name, indexed[name], spec) if name in SHARED else work[name] for name in paths}
    plan = {'mode': 'execute' if args.execute else 'read-only-plan', 'base': base, 'branch': branch,
            'paths': paths, 'indexSha256': sha(original_index), 'sharedScope': 'Exact A02 required-label entries and image exceptions; all A01 rows preserved',
            'unrelatedStagingPreserved': True, 'workingSourcesRewrittenByCommit': False, 'pushRequested': args.push}
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2)); return
    assert all(work[name] == proposed_shared[name] for name in SHARED), 'Apply the reviewed shared overlays first with --apply-shared'
    git_dir = Path(git('rev-parse', '--absolute-git-dir').strip().decode())
    run = git_dir / 'scoped-a02-scene-sources' / uuid.uuid4().hex
    run.mkdir(parents=True)
    (run / 'index-before.backup').write_bytes(original_index)
    (run / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    commit_env = {'GIT_INDEX_FILE': str(run / 'commit-index')}
    sync_env = {'GIT_INDEX_FILE': str(run / 'sync-index')}
    old_env = {'GIT_INDEX_FILE': str(run / 'index-before.backup')}
    git('read-tree', base, env=commit_env)
    (run / 'sync-index').write_bytes(original_index)
    owned = {name.encode() for name in paths}
    def foreign(env):
        return {flag: b'\0'.join(x for x in git('ls-files', flag, '-z', env=env).split(b'\0') if x and
                (x.split(b'\t', 1)[-1] if flag == '--stage' else x[2:]) not in owned)
                for flag in ['--stage', '-v']}
    foreign_before = foreign(old_env)
    # Raw source blobs retain the exact byte hashes bound to the capture.
    # Shared lexical bytes likewise preserve unrelated staged content.
    objects = {}
    for name in paths:
        for values in (committed, synced):
            args_hash = ['hash-object', '-w', '--stdin']
            object_id = git(*args_hash, data=values[name]).strip().decode()
            original_raw = values[name]
            values[name] = git('cat-file', 'blob', object_id)
            assert values[name] == original_raw, 'Frozen source bytes changed during staging'
            objects[name, sha(values[name])] = object_id
    head_modes = {x.split(b'\t', 1)[1].decode(): x.split()[0].decode() for x in git('ls-tree', '-r', '-z', base).split(b'\0') if x}
    staged_entries = [x for x in git('ls-files', '--stage', '-z', env=old_env).split(b'\0') if x]
    for item in staged_entries:
        if item.split(b'\t', 1)[1] in owned: assert item.split(b'\t', 1)[0].split()[2] == b'0', 'Owned merge conflict'
    index_modes = {x.split(b'\t', 1)[1].decode(): x.split()[0].decode() for x in staged_entries}
    for values, env, modes in ((committed, commit_env, head_modes), (synced, sync_env, index_modes)):
        payload = b''.join((modes.get(name, '100644') + ' ' + objects[name, sha(raw)] + '\t' + name).encode() + b'\0' for name, raw in values.items())
        git('update-index', '-z', '--index-info', env=env, data=payload)
    assert foreign(sync_env) == foreign_before
    git('-c', 'core.whitespace=trailing-space,space-before-tab,cr-at-eol', 'diff', '--cached', '--check', base, env=commit_env)
    policy_env = os.environ.copy(); policy_env.update(commit_env); policy_env['GIT_OPTIONAL_LOCKS'] = '0'
    subprocess.run(['node', 'scripts/media-policy.cjs'], cwd=ROOT, env=policy_env, check=True)
    changed = git('diff', '--cached', '--name-only', base, env=commit_env).decode().splitlines()
    assert changed and set(changed) <= set(paths)
    def stable():
        assert index.read_bytes() == original_index and git('rev-parse', 'HEAD').strip().decode() == base
        assert git('symbolic-ref', '--quiet', 'HEAD').strip().decode() == branch
        assert spec_path.read_bytes() == spec_raw
        assert all((ROOT / name).read_bytes() == raw for name, raw in work.items()), 'Concurrent source/shared edits'
        for item in spec['verificationInputs']: source.check_artifact(item)
    stable()
    tree = git('write-tree', env=commit_env).strip().decode()
    commit = git('commit-tree', tree, '-p', base, data=(args.message + '\n').encode()).strip().decode()
    lock = Path(str(index) + '.lock'); fd = None; lock_owned = False; moved = False
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0), 0o666)
        lock_owned = True; stable()
        payload = (run / 'sync-index').read_bytes()
        with os.fdopen(fd, 'wb') as stream:
            fd = None; assert stream.write(payload) == len(payload); stream.flush(); os.fsync(stream.fileno())
        git('update-ref', '-m', 'commit: A02 scene source closure', branch, commit, base); moved = True
        os.replace(lock, index)
    except Exception:
        if fd is not None: os.close(fd)
        if lock_owned and lock.exists(): lock.unlink()
        (run / 'interrupted.json').write_text(json.dumps({'commit': commit, 'refUpdated': moved, 'indexBackup': str(run / 'index-before.backup')}), encoding='utf-8')
        raise
    assert foreign(None) == foreign_before
    assert all((ROOT / name).read_bytes() == raw for name, raw in work.items())
    for name in SHARED: assert git('show', ':' + name) == synced[name]
    receipt = {'status': 'committed-not-pushed', 'base': base, 'commit': commit, 'paths': changed,
               'foreignIndexPreserved': True, 'unrelatedSharedBytesPreserved': True, 'workingSourcesUnchanged': True,
               'backupDirectory': str(run)}
    if args.push:
        git('push', 'origin', commit + ':' + branch)
        remote = git('ls-remote', '--heads', 'origin', branch).decode().split()[0]
        git('merge-base', '--is-ancestor', commit, remote)
        receipt.update(status='committed-and-pushed', remoteSha=remote)
    (run / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
