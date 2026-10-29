"""Prepare/commit this exact review-action scope without mixing foreign changes.

Source prepared for root review. Default is a read-only plan; Git writes require
--execute, and a push additionally requires --push. Supply an exact JSON path list.
Shared JSON overlays patch individual owned values, retaining unrelated bytes.
No working-tree source is rewritten. Previous index bytes remain recoverable.
"""
from pathlib import Path,PurePosixPath
import argparse,copy,datetime,hashlib,json,os,re,struct,subprocess,uuid
from scoped_json import load,patch,upsert

R=Path(__file__).resolve().parents[3]
B='production/batches/design-25-30-review-actions-20261029/'
KEY='design-25-30-review-actions-20261029'
SLUGS={'D25':'limited-color-world','D26':'computer-controlled-players','D27':'in-game-cutscenes',
       'D28':'start-with-climax','D29':'kind-to-beginners','D30':'respect-player-time'}
UPLOAD_IDS=['D26','D27','D28','D30'];REVISION_IDS=['D25','D29']
C='shared/publishing/video-production-control.json';W='shared/publishing/video-worklist.json'
D='docs/VIDEO_WORKLIST.md';G='.gitignore';I='shared/git-essential-images.json'
SHARED={C,W,D,G,I}
UNITY='unity/VideoEditing/Assets/VideoScenes/'
ROOTS=[B,UNITY+'design-25-29-clarity-v3/']
ROOTS += ['projects/kind-to-beginners/production/botw-v4/',
          'projects/kind-to-beginners/script/botw-v4/',
          UNITY+'design-d29-botw-v4/',UNITY+'kind-to-beginners/botw-v4/']
for id in UPLOAD_IDS:
    ROOTS += ['projects/'+SLUGS[id]+'/production/upload-20261029/',
              'projects/'+SLUGS[id]+'/publishing/upload-20261029/']
for id in REVISION_IDS:
    ROOTS += ['projects/'+SLUGS[id]+'/production/clarity-v3/',
              'projects/'+SLUGS[id]+'/script/clarity-v3/',UNITY+SLUGS[id]+'/clarity-v3/']
EXACT=set(SHARED)|{UNITY+'design-25-29-clarity-v3.meta','output/game-design-25-29-clarity-v3-20261029/index.html'}
EXACT.update({UNITY+'design-d29-botw-v4.meta',UNITY+'kind-to-beginners/botw-v4.meta'})
for id in REVISION_IDS:
    EXACT.add(UNITY+SLUGS[id]+'/clarity-v3.meta')
    EXACT.update('projects/'+SLUGS[id]+'/'+p for p in ['project.json','rebuild.json','production/delivery-output.json',
        'production/checkpoint.json','production/review-ledger.json'])
THUMBNAILS={'projects/'+SLUGS[id]+'/publishing/upload-20261029/thumbnail.png' for id in UPLOAD_IDS}
TEXT_EXT={'.py','.cs','.json','.txt','.md','.cjs','.js','.ts','.tsx','.css','.html','.srt','.ass','.unity','.meta','.mat','.asset','.shader','.hlsl'}
ROW_FIELDS={'productionComplete','productionStatus','reviewStatus','humanApproval','platformStatus','videoId','url','latestRulesPassed',
    'executionStatus','localMasterAvailable','activeRevision','selectedBatch','internalQaStatus','localReview',
    'revisionInProduction','userReview','uploadProgress','notes','updatedAt','localReviewHistory','evidence'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(*args,env=None,data=None,allow_missing=False):
    q=subprocess.run(['git',*args],cwd=R,env=env,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if q.returncode:
        if allow_missing:return None
        raise RuntimeError((q.stdout+q.stderr).decode('utf-8','replace')[:6000])
    return q.stdout
def check_path(path):
    assert isinstance(path,str) and '\\' not in path and '\x00' not in path and '\n' not in path and '\r' not in path
    pure=PurePosixPath(path);assert not pure.is_absolute() and '..' not in pure.parts and str(pure)==path
    assert path in EXACT or any(path.startswith(prefix) for prefix in ROOTS),('Outside exact owned roots',path)
    assert '/production/local/' not in path and '__pycache__' not in pure.parts
    assert (R/path).is_file() and (R/path).resolve().is_relative_to(R.resolve()),('External/junction file refused',path)
    assert path in SHARED or Path(path).suffix.lower() in TEXT_EXT or path in THUMBNAILS,('Media/QA image refused',path)
    if Path(path).suffix.lower()=='.png':assert path in THUMBNAILS

def markdown_rows(raw):
    found={}
    for line in raw.decode('utf-8-sig').splitlines(keepends=True):
        for id in SLUGS:
            kind='series' if line.startswith('| '+id+' | ') else 'order' if re.match(r'^\| \d+ \| 게임디자인 \| '+id+r' ',line) else None
            if kind:
                assert (id,kind) not in found,'Duplicate owned markdown row'
                found[id,kind]=line
    assert len(found)==12,('Expected exactly12 owned table rows',len(found))
    return found

def make_overlays(work,heads):
    current_control=load(work[C]);current_worklist=load(work[W]);head_worklist=load(heads[W])
    current_rows={r['id']:r for r in current_worklist['rows']};head_rows={r['id']:r for r in head_worklist['rows']}
    row_changes={id:[key for key in ROW_FIELDS if key in current_rows[id] and current_rows[id].get(key)!=head_rows[id].get(key)] for id in SLUGS}
    # Keep histories/evidence merged, not copied wholesale over foreign entries.
    auth=load((R/B/'authorization.json').read_bytes())
    approved_hashes={x.get('sha256',x.get('baseMasterSha256')) for x in auth['privateUploads']+auth['revisions']}
    d29_auth_path=R/'projects/kind-to-beginners/production/botw-v4/authorization.json'
    if d29_auth_path.is_file():
        d29_auth=load(d29_auth_path.read_bytes())
        assert d29_auth['slug']=='kind-to-beginners' and d29_auth['revision']=='botw-v4'
        approved_hashes.add(d29_auth['priorCaptionedSha256'])
    entries={x['path']:x for x in load(work[I])['entries']};new_md=markdown_rows(work[D]);old_md=markdown_rows(heads[D])
    changed_columns={}
    for key,line in new_md.items():
        columns=[2,3,4,5] if key[1]=='series' else [3,4,5]
        a=old_md[key].rstrip('\r\n').split('|');b=line.rstrip('\r\n').split('|')
        assert len(a)==len(b)
        changed_columns[key]=[col for col in columns if a[col]!=b[col]]
    def changed_values(raw,path,base,current):
        # Preserve unrelated staged subkeys even within an owned row field.
        if isinstance(base,dict) and isinstance(current,dict):
            assert not (set(base)-set(current)),('Unexpected shared-key deletion requires explicit review',path)
            for key,value in current.items():
                if key not in base or value!=base[key]:
                    raw=changed_values(raw,path+[key],base.get(key),value)
            return raw
        return patch(raw,path,current)
    def overlay(path,raw):
        if path==G:
            lines=raw.decode('utf-8-sig').splitlines();newline=b'\r\n' if b'\r\n' in raw else b'\n'
            for thumb in sorted(THUMBNAILS):
                exact='!'+thumb
                assert exact in work[G].decode('utf-8-sig').splitlines() or '!/'+thumb in work[G].decode('utf-8-sig').splitlines()
                if exact not in lines and '!/'+thumb not in lines:raw+=(b'' if raw.endswith(b'\n') else newline)+exact.encode()+newline
            return raw
        if path==I:
            for thumb in sorted(THUMBNAILS):raw=upsert(raw,'entries','path',entries[thumb])
            return raw
        if path==C:
            if 'finiteBatchAuthorizations' not in load(raw):raw=patch(raw,['finiteBatchAuthorizations'],{})
            return patch(raw,['finiteBatchAuthorizations',KEY],current_control['finiteBatchAuthorizations'][KEY])
        if path==W:
            for id in SLUGS:
                indices=[i for i,r in enumerate(load(raw)['rows']) if r['id']==id];assert len(indices)==1;i=indices[0]
                for field in sorted(row_changes[id]):
                    current=current_rows[id][field]
                    if field=='evidence':
                        value=copy.deepcopy(load(raw)['rows'][i].get(field,[]))
                        own=[x for x in current if x.startswith(B) or '/production/upload-20261029/' in x or '/production/clarity-v3/' in x or x.startswith('projects/kind-to-beginners/production/botw-v4/')]
                        for x in own:
                            if x not in value:value.append(x)
                    elif field=='localReviewHistory':
                        value=copy.deepcopy(load(raw)['rows'][i].get(field,[]))
                        for x in current:
                            if x.get('captionedSha256') in approved_hashes and x not in value:value.append(copy.deepcopy(x))
                    else:value=copy.deepcopy(current)
                    if field in {'evidence','localReviewHistory'}:raw=patch(raw,['rows',i,field],value)
                    else:raw=changed_values(raw,['rows',i,field],head_rows[id].get(field),value)
            return raw
        if path==D:
            old=markdown_rows(raw);lines=raw.decode('utf-8-sig').splitlines(keepends=True);replace={}
            for key,line in old.items():
                a=line.rstrip('\r\n').split('|');b=new_md[key].rstrip('\r\n').split('|')
                assert len(a)==len(b)
                for col in changed_columns[key]:a[col]=b[col]
                replace[line]='|'.join(a)+('\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else '')
            out=''.join(replace.get(line,line) for line in lines)
            return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+out.encode('utf-8')
        return work[path]
    return overlay,row_changes,changed_columns

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--paths',required=True,help='JSON array of exact relative paths')
    ap.add_argument('--message',default='Complete approved uploads and D25/D29 clarity revisions')
    ap.add_argument('--execute',action='store_true');ap.add_argument('--push',action='store_true');a=ap.parse_args()
    assert not a.push or a.execute,'Push requires explicit execute'
    paths=load(Path(a.paths).read_bytes());assert isinstance(paths,list) and paths and len(paths)==len(set(paths))
    for path in paths:check_path(path)
    # Read all shared files for overlays even if a particular unchanged shared file
    # is not selected; only requested exact paths can enter the isolated index.
    input_paths=set(paths)|SHARED;work={p:(R/p).read_bytes() for p in input_paths}
    base=git('rev-parse','HEAD').strip().decode();branch=git('symbolic-ref','--quiet','HEAD').strip().decode()
    assert branch.startswith('refs/heads/codex/')
    index=Path(git('rev-parse','--git-path','index').strip().decode());index=index if index.is_absolute() else R/index
    original_index=index.read_bytes()
    heads={p:git('show',base+':'+p) for p in SHARED};indexed={p:git('show',':'+p) for p in SHARED}
    assert index.read_bytes()==original_index,'Index changed while reading; retry without mutations'
    overlay,row_fields,md_columns=make_overlays(work,heads)
    committed={p:overlay(p,heads[p]) if p in SHARED else work[p] for p in paths}
    synced={p:overlay(p,indexed[p]) if p in SHARED else work[p] for p in paths}
    for thumb in THUMBNAILS & set(paths):
        raw=work[thumb];assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(1280,720) and len(raw)<2*1024*1024
        entry=next(x for x in load(work[I])['entries'] if x['path']==thumb)
        assert entry['purpose']=='delivery-thumbnail' and entry['sha256']==sha(raw)
        review=load((R/Path(thumb).parent/'thumbnail-review.json').read_bytes())
        assert review['status']=='pass' and review['final']['sha256']==sha(raw) and review['inspection']['mobile375Viewed']
        assert I in paths and G in paths,'A selected delivery thumbnail requires its scoped registry/ignore overlays'
    plan={'mode':'execute' if a.execute else 'read-only-plan','base':base,'branch':branch,'paths':paths,
        'rowFields':row_fields,'markdownChangedColumns':{id+'/'+kind:v for (id,kind),v in md_columns.items()},
        'sharedOverlays':'own finiteBatch entry,6 row changed values,12 row columns,4 image entries/exceptions only',
        'workingSourcesRewritten':False,'pushRequested':a.push,'initialIndexSha256':sha(original_index)}
    if not a.execute:print(json.dumps(plan,ensure_ascii=False,indent=2));return
    run=Path('C:/Users/1/.codex/video-production/design-25-30-review-actions-20261029/git')/uuid.uuid4().hex
    assert run.resolve().is_relative_to(Path('C:/Users/1/.codex/video-production/design-25-30-review-actions-20261029/git').resolve())
    run.mkdir(parents=True);(run/'index-before.backup').write_bytes(original_index)
    (run/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(run/'commit-index');env['GIT_OPTIONAL_LOCKS']='0'
    git('read-tree',base,env=env)
    old_env=os.environ.copy();old_env['GIT_INDEX_FILE']=str(run/'index-before.backup');old_env['GIT_OPTIONAL_LOCKS']='0'
    sync_env=os.environ.copy();sync_env['GIT_INDEX_FILE']=str(run/'sync-index');sync_env['GIT_OPTIONAL_LOCKS']='0';(run/'sync-index').write_bytes(original_index)
    ownset={p.encode() for p in paths}
    def foreign(e):
        return {flag:b'\0'.join(item for item in git('ls-files',flag,'-z',env=e).split(b'\0') if item and
           (item.split(b'\t',1)[-1] if flag=='--stage' else item[2:]) not in ownset) for flag in ['--stage','-v']}
    foreign_before=foreign(old_env)
    oid_cache={}
    def oid(raw):
        if raw not in oid_cache:oid_cache[raw]=git('hash-object','-w','--stdin',data=raw).strip().decode()
        return oid_cache[raw]
    for values in [committed,synced]:
        for path in paths:
            if path not in SHARED:
                object_id=git('hash-object','-w','--path='+path,'--stdin',data=values[path]).strip().decode()
                values[path]=git('cat-file','blob',object_id);oid_cache[values[path]]=object_id
    head_modes={x.split(b'\t',1)[1].decode():x.split()[0].decode() for x in git('ls-tree','-r','-z',base).split(b'\0') if x}
    index_modes={x.split(b'\t',1)[1].decode():x.split()[0].decode() for x in git('ls-files','--stage','-z',env=old_env).split(b'\0') if x}
    def stage(values,e,modes):
        payload=b''.join((modes.get(path,'100644')+' '+oid(raw)+'\t'+path).encode()+b'\0' for path,raw in values.items())
        git('update-index','-z','--index-info',env=e,data=payload)
    stage(committed,env,head_modes);stage(synced,sync_env,index_modes)
    assert foreign(sync_env)==foreign_before
    generated_suffixes=['.unity','.meta','.mat','.asset']
    for path in paths:
        if path.startswith(UNITY) and Path(path).suffix in generated_suffixes:
            for n,line in enumerate(committed[path].decode('utf-8-sig').splitlines(),1):
                assert not re.search(r' +\t',line),(path,n,'space before tab')
                if line.rstrip(' \t')!=line:assert re.fullmatch(r'\s*(?:-\s+)?[^\s:]+:[ \t]+',line),(path,n,'unexpected generated whitespace')
    exclude=[':(exclude,glob)'+UNITY+'**/*'+suffix for suffix in generated_suffixes]
    git('-c','core.whitespace=trailing-space,space-before-tab,cr-at-eol','diff','--cached','--check',base,'--','.',*exclude,env=env)
    subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
    changed=git('diff','--cached','--name-only',base,env=env).decode().splitlines();assert changed and set(changed)<=set(paths)
    assert index.read_bytes()==original_index and git('rev-parse','HEAD').strip().decode()==base
    assert all((R/p).read_bytes()==raw for p,raw in work.items()),'Concurrent source/shared edit; no ref changed'
    tree=git('write-tree',env=env).strip().decode();commit=git('commit-tree',tree,'-p',base,data=(a.message+'\n').encode()).strip().decode()
    lock=Path(str(index)+'.lock');fd=None;ref_moved=False;lock_owned=False
    try:
        fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_BINARY',0),0o666)
        lock_owned=True
        assert index.read_bytes()==original_index and git('rev-parse','HEAD').strip().decode()==base
        assert git('symbolic-ref','--quiet','HEAD').strip().decode()==branch
        assert all((R/p).read_bytes()==raw for p,raw in work.items()),'Concurrent owned/shared input edit; no ref changed'
        payload=(run/'sync-index').read_bytes()
        with os.fdopen(fd,'wb') as stream:fd=None;assert stream.write(payload)==len(payload);stream.flush();os.fsync(stream.fileno())
        git('update-ref','-m','commit: design review actions20261029',branch,commit,base);ref_moved=True;os.replace(lock,index)
    except Exception:
        if fd is not None:os.close(fd)
        if lock_owned and lock.exists():lock.unlink()
        (run/'interrupted.json').write_text(json.dumps({'commit':commit,'refUpdated':ref_moved,'originalIndexBackup':str(run/'index-before.backup')}),encoding='utf-8')
        raise
    assert foreign(None)==foreign_before
    assert all((R/p).read_bytes()==raw for p,raw in work.items()),'Working source unexpectedly changed after commit'
    tree_blobs={item.split(b'\t',1)[1].decode():item.split(b'\t',1)[0].split()[2].decode() for item in git('ls-tree','-r','-z',commit).split(b'\0') if item}
    for path,raw in committed.items():assert tree_blobs[path]==oid(raw)
    for path in SHARED & set(paths):assert git('show',':'+path)==synced[path]
    receipt={'status':'committed-not-pushed','base':base,'commit':commit,'paths':changed,'foreignIndexPreserved':True,
        'unrelatedSharedBytesPreserved':True,'workingSourcesUnchanged':True,'indexBackup':str(run/'index-before.backup')}
    (run/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    if a.push:
        git('push','origin',commit+':'+branch)
        remote=git('ls-remote','--heads','origin',branch).decode().split()[0];git('merge-base','--is-ancestor',commit,remote)
        receipt.update({'status':'committed-and-pushed','remoteSha':remote})
        (run/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
if __name__=='__main__':main()
