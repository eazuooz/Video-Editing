"""Commit this project and its three bounded ledger entries; preserve other staging."""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, os, subprocess, uuid

ROOT=Path(__file__).resolve().parents[3]
PROJECT=Path(__file__).resolve().parents[1]
SLUG=PROJECT.name
PREFIX=PROJECT.relative_to(ROOT).as_posix()+'/'
CONTROL='shared/publishing/video-production-control.json'
WORKLIST='shared/publishing/video-worklist.json'
DOC='docs/VIDEO_WORKLIST.md'
START='<!-- BUCKSHOT-RE-SETUP-20261028-START -->'
END='<!-- BUCKSHOT-RE-SETUP-20261028-END -->'

def git(*args, data=None, env=None):
    return subprocess.check_output(['git',*args],cwd=ROOT,input=data,env=env)
def json_bytes(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def read_json(value):return json.loads(value.decode('utf-8-sig'))
def index_map(raw):
    return {row.split(b'\t',1)[1].decode():row.split(b'\t',1)[0] for row in raw.split(b'\0') if b'\t' in row}
def block(text):
    if START not in text:return None
    return text[text.index(START):text.index(END)+len(END)]
def project_ledger(path,base,working):
    if path==DOC:
        old=base.decode('utf-8-sig');new=block(working.decode('utf-8-sig'))
        assert new
        prior=block(old)
        return (old.replace(prior,new) if prior else old.rstrip()+'\n\n'+new+'\n').encode('utf-8')
    old=read_json(base);new=read_json(working)
    if path==CONTROL:
        old.setdefault('scopedSetupAuthorizations',{})[SLUG]=copy.deepcopy(new['scopedSetupAuthorizations'][SLUG])
    else:
        selected=next(r for r in new['rows'] if r.get('id')=='S-BUCKSHOT-RE')
        rows=old['rows'];indexes=[i for i,r in enumerate(rows) if r.get('id')=='S-BUCKSHOT-RE']
        assert len(indexes)<=1
        if indexes:rows[indexes[0]]=copy.deepcopy(selected)
        else:rows.append(copy.deepcopy(selected))
    return json_bytes(old)
def without_owned(path,payload):
    if path==DOC:
        s=payload.decode('utf-8-sig');b=block(s)
        return s.replace(b,'').rstrip() if b else s.rstrip()
    value=read_json(payload)
    if path==CONTROL:
        value.get('scopedSetupAuthorizations',{}).pop(SLUG,None)
        if value.get('scopedSetupAuthorizations')=={}:value.pop('scopedSetupAuthorizations',None)
    else:value['rows']=[r for r in value['rows'] if r.get('id')!='S-BUCKSHOT-RE']
    return value

def publish_index_and_ref(index_path, prepared_bytes, original_bytes, ref, head, commit, run_git=git):
    """Hold Git's real index lock only for final revalidation, ref CAS and replace.

    All expensive blob/tree/media work has already finished. An abandoned
    commit object is harmless if the index or HEAD changed before this point.
    Never overwrite another process's lock or roll back a newer branch tip.
    """
    lock_path=index_path.with_name(index_path.name+'.lock')
    descriptor=os.open(lock_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    identity=os.fstat(descriptor)
    identity=(identity.st_dev,identity.st_ino)
    ref_updated=False
    try:
        if index_path.read_bytes()!=original_bytes:
            raise RuntimeError('Real index changed during preparation; nothing published. Inspect and retry.')
        if run_git('symbolic-ref','HEAD').decode().strip()!=ref:
            raise RuntimeError('Checked-out branch changed during preparation; nothing published.')
        if run_git('rev-parse','HEAD').decode().strip()!=head:
            raise RuntimeError('HEAD changed during preparation; nothing published. Inspect and retry.')
        with os.fdopen(descriptor,'wb') as stream:
            descriptor=None
            stream.write(prepared_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        # Git index writers are excluded until the prepared index is installed.
        # update-ref's old-value argument still provides the independent HEAD CAS.
        run_git('update-ref',ref,commit,head)
        ref_updated=True
        os.replace(lock_path,index_path)
    except BaseException as failure:
        if ref_updated:
            try:
                run_git('update-ref',ref,head,commit)
            except BaseException as rollback_failure:
                raise RuntimeError(
                    'Index replacement failed and branch rollback was not safe/successful. '
                    'Original index is preserved; inspect HEAD and the saved index backup before retrying. '
                    f'Publication error: {failure}; rollback error: {rollback_failure}'
                ) from failure
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)
        # Only remove the exact lock created here. A pre-existing lock never
        # reaches this block because O_EXCL fails before entering the try.
        try:
            current=lock_path.stat()
            if (current.st_dev,current.st_ino)==identity:
                lock_path.unlink()
        except FileNotFoundError:
            pass

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--commit',action='store_true');ap.add_argument('--push',action='store_true');args=ap.parse_args()
    assert not args.push or args.commit
    checkpoint=read_json((PROJECT/'production/checkpoint.json').read_bytes())
    assert checkpoint.get('stage')=='local-final-review-ready', 'Finish local deliverables before saving final commit.'
    head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip()
    paths=set(git('ls-files','--cached','--others','--exclude-standard','-z','--',PREFIX).decode().split('\0'))-{''}
    assert paths and all((ROOT/p).is_file() for p in paths)
    forbidden={'.mp4','.mkv','.avi','.wav','.mp3','.zip','.png','.jpg','.jpeg','.blend','.pyc'}
    assert not any(Path(p).suffix.lower() in forbidden or '/local/' in p or '/captures/' in p for p in paths)
    owned={p:(ROOT/p).read_bytes() for p in sorted(paths)}
    ledger_work={p:(ROOT/p).read_bytes() for p in [CONTROL,WORKLIST,DOC]}
    for p,current in ledger_work.items():
        base=git('show',head+':'+p)
        projected=project_ledger(p,base,current)
        assert without_owned(p,base)==without_owned(p,projected)
        owned[p]=projected
    if not args.commit:
        print(json.dumps({'status':'prepared-no-git-write','paths':list(owned),'baseHead':head}));return
    gd=Path(git('rev-parse','--absolute-git-dir').decode().strip())
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:12]
    temporary=gd/('index-buckshot-commit-'+stamp)
    replacement=gd/('index-buckshot-replacement-'+stamp)
    env=dict(os.environ,GIT_INDEX_FILE=str(temporary))
    replacement_env=dict(os.environ,GIT_INDEX_FILE=str(replacement))
    index_path=gd/'index'
    original_bytes=index_path.read_bytes()
    try:
        # Snapshot bytes, flags and unrelated staging; all preparation uses this
        # private index, never a changing real index or a HEAD-only replacement.
        replacement.write_bytes(original_bytes)
        if git('ls-files','--unmerged','-z',env=replacement_env):
            raise RuntimeError('Unmerged index entries exist; preserve them and finish that work first.')
        original_raw=git('ls-files','--stage','-z',env=replacement_env)
        before=index_map(original_raw)
        staged_ledger={p:git('show',':'+p,env=replacement_env) for p in ledger_work}
        staged_projected={p:project_ledger(p,staged_ledger[p],ledger_work[p]) for p in ledger_work}
        for p in staged_ledger:assert without_owned(p,staged_ledger[p])==without_owned(p,staged_projected[p])
        git('read-tree',head,env=env)
        for p,data in owned.items():
            blob=git('hash-object','-w','--path',p,'--stdin',data=data).decode().strip()
            git('update-index','--add','--cacheinfo','100644',blob,p,env=env)
        # Preserve the byte-verified Godot source, including its harmless final
        # blank line. Still reject line-end spaces and spaces before indentation tabs.
        try:git('-c','core.whitespace=blank-at-eol,space-before-tab,-blank-at-eof','diff','--cached','--check',env=env)
        except subprocess.CalledProcessError as error:
            raise RuntimeError('Selected diff whitespace check failed:\n'+error.output.decode('utf-8',errors='replace')) from error
        subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=env,check=True)
        records=[]
        for p,data in owned.items():
            if p in staged_projected:data=staged_projected[p]
            blob=git('hash-object','-w','--path',p,'--stdin',data=data).decode().strip()
            records.append(('100644 '+blob+' 0\t'+p).encode()+b'\0')
        git('update-index','-z','--index-info',data=b''.join(records),env=replacement_env)
        after=index_map(git('ls-files','--stage','-z',env=replacement_env))
        assert {p:v for p,v in before.items() if p not in owned}=={p:v for p,v in after.items() if p not in owned}
        prepared_bytes=replacement.read_bytes()
        backup=gd/('index-before-buckshot-'+stamp)
        backup.write_bytes(original_bytes)
        tree=git('write-tree',env=env).decode().strip()
        commit=git('commit-tree',tree,'-p',head,data=b'Explain REA and lead the prototype video with the reverse-engineering workflow\n').decode().strip()
        publish_index_and_ref(index_path,prepared_bytes,original_bytes,ref,head,commit)
    finally:
        # These unique private indexes are ours; the real index and its lock
        # are handled only by publish_index_and_ref above.
        for path in (temporary,replacement):
            try:path.unlink()
            except FileNotFoundError:pass
    receipt={'baseHead':head,'commit':commit,'branchRef':ref,'paths':list(owned),'nonOwnedStagingPreserved':True,'ledgerOtherFieldsPreserved':True,'indexBackup':str(backup),'indexOriginalSha256':hashlib.sha256(original_bytes).hexdigest(),'indexInstalledSha256':hashlib.sha256(prepared_bytes).hexdigest(),'indexPublication':'exclusive real index.lock; revalidated original bytes and branch/HEAD; ref CAS then atomic replacement','push':'not-requested'}
    output=PROJECT/'production/local/git-save-receipt.json';output.write_bytes(json_bytes(receipt))
    if args.push:
        subprocess.run(['git','push','origin',ref],cwd=ROOT,check=True)
        remote=git('ls-remote','origin',ref).decode().split()[0];assert remote==commit
        receipt.update(push='verified',remoteHead=remote);output.write_bytes(json_bytes(receipt))
    print(json.dumps(receipt,ensure_ascii=False))

if __name__=='__main__':main()
