"""Selective finite-batch commit; preserve unrelated working files and index entries."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;L=B/'local'
AUTH='explicit-ten-distinctive-shorts-20261025'
CONTROL='shared/publishing/video-production-control.json';WORK='shared/publishing/shorts-worklist.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def run(args,env=None,input=None):
    p=subprocess.run(args,cwd=R,env=env,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-6000:])
    return p.stdout
def git(*args,env=None,input=None):return run(['git',*args],env,input)
def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def blob(v):return git('hash-object','-w','--stdin',input=encoded(v)).decode().strip()
def entries(env=None):
    return {row.split(b'\t',1)[1].decode():row for row in git('ls-files','--stage','-z',env=env).split(b'\0') if row}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--commit',action='store_true');parser.add_argument('--message',default='Prepare ten researched game technique Shorts for sequential production');args=parser.parse_args()
    selected=[r['slug'] for r in read(B/'batch.json')['projects']]
    paths=[p for p in read(L/'owned-paths.json') if (R/p).exists()]
    head=git('rev-parse','HEAD').decode().strip()
    index=R/'.git/index'; original=index.read_bytes(); original_entries=entries()
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup=L/('index-before-'+stamp+'.bin');backup.write_bytes(original)
    temp=L/('index-selective-'+stamp);env=os.environ.copy();env['GIT_INDEX_FILE']=str(temp.resolve())
    git('read-tree',head,env=env)
    git('add','--',*paths,env=env)
    working_control=read(R/CONTROL);working_work=read(R/WORK)
    control=json.loads(git('show',head+':'+CONTROL));control.setdefault('scopedBatchAuthorizations',{})[AUTH]=working_control['scopedBatchAuthorizations'][AUTH]
    work=json.loads(git('show',head+':'+WORK));ours={r['slug']:r for r in working_work['rows'] if r.get('slug') in selected}
    assert set(ours)==set(selected)
    work['rows']=[r for r in work['rows'] if r.get('slug') not in ours]+[ours[s] for s in selected]
    for key in ['updatedAt','latestUserSteering']:work[key]=working_work[key]
    for name,value in [(CONTROL,control),(WORK,work)]:git('update-index','--add','--cacheinfo','100644',blob(value),name,env=env)
    staged=git('diff','--cached','--name-only','-z',env=env).decode().strip('\0').split('\0')
    assert all(name in [CONTROL,WORK] or any(name==p or name.startswith(p+'/') for p in paths) for name in staged)
    run(['node','scripts/media-policy.cjs'],env=env)
    # Unity writes empty serialized values with trailing spaces. Preserve those
    # generated scene/settings bytes; check authored code and documents normally.
    exclusions=[':(exclude)projects/'+slug+'/production/unity-project/**/*'+suffix for slug in ['shorts-viewfinder-mesh-slicing','shorts-outer-wilds-gravity'] for suffix in ['.asset','.unity','.meta','.mat','.prefab']]
    git('diff','--cached','--check','--','.',*exclusions,env=env)
    report=dict(headBefore=head,paths=staged,files=len(staged),foreignIndexBackup=str(backup),foreignIndexSha256=hashlib.sha256(original).hexdigest(),mediaPolicy='pass',whitespaceCheck='Authored code/docs checked; Unity serialized scene/settings bytes preserved.',status='prepared')
    (L/'selective-commit-plan.json').write_bytes(encoded(report))
    print(json.dumps({'files':len(staged),'mediaPolicy':'pass','commitRequested':args.commit}))
    if not args.commit:return
    assert index.read_bytes()==original,'Another task changed the index; prepare again.'
    assert git('rev-parse','HEAD').decode().strip()==head,'HEAD changed; prepare again.'
    git('commit','-m',args.message,env=env)
    committed=git('rev-parse','HEAD').decode().strip()
    # Existing unrelated entries stay byte-for-byte equivalent. Shared control
    # retains its previously staged foreign fields while adopting our one field.
    assert index.read_bytes()==original,'Real index changed during isolated commit; inspect before sync.'
    committed_entries=entries(env)
    own=[n for n in staged if n not in [CONTROL,WORK]]
    payload=b'\0'.join(committed_entries[n] for n in own)+b'\0'
    git('update-index','-z','--index-info',input=payload)
    for name in [CONTROL,WORK]:
        old_oid=original_entries[name].split()[1].decode()
        previous=json.loads(git('cat-file','blob',old_oid))
        if name==CONTROL:previous.setdefault('scopedBatchAuthorizations',{})[AUTH]=working_control['scopedBatchAuthorizations'][AUTH]
        else:
            previous['rows']=[r for r in previous['rows'] if r.get('slug') not in ours]+[ours[s] for s in selected]
            for key in ['updatedAt','latestUserSteering']:previous[key]=working_work[key]
        git('update-index','--cacheinfo','100644',blob(previous),name)
    after=entries();unchanged=[n for n in original_entries if n not in staged]
    assert all(after.get(n)==original_entries[n] for n in unchanged),'Foreign index entry changed.'
    report.update(status='committed',commit=committed,foreignEntriesVerified=len(unchanged),realIndexOwnPathsSynchronized=True)
    (L/'selective-commit-receipt.json').write_bytes(encoded(report))
    print(json.dumps({'commit':committed,'foreignEntriesPreserved':len(unchanged)}))
if __name__=='__main__':main()
