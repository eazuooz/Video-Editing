"""Save only this batch's completed planning unit, preserving other staged entries."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,re,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).parent
KEY='explicitMathRemainingBatch20261104'
CONTROL='shared/publishing/video-production-control.json'
WORKLIST='shared/publishing/video-worklist.json'
DOC='docs/VIDEO_WORKLIST.md'
WORKFLOW='docs/VIDEO_WORKFLOW.md'
MARKER='<!-- MATH-REMAINING-20261104 -->'
HASH_CACHE={}
INDEX_UPDATES={}
def git(*args,data=None,env=None):return subprocess.check_output(['git','-c','core.safecrlf=false',*args],cwd=ROOT,input=data,env=env)
def decode(b):return json.loads(b.decode('utf-8-sig'))
def pack(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def projected(path,base,working):
    if path in [CONTROL,WORKLIST]:
        a,b=decode(base),decode(working)
        if path==CONTROL:a[KEY]=copy.deepcopy(b[KEY])
        else:
            selected={r['id']:r for r in b['rows'] if r['id'] in {f'M{i:02}' for i in range(21,34)}}
            a['rows']=[copy.deepcopy(selected.get(r['id'],r)) for r in a['rows']]
            a['mathRemainingBatch20261104']=copy.deepcopy(b['mathRemainingBatch20261104'])
        return pack(a)
    old,new=base.decode('utf-8-sig'),working.decode('utf-8-sig')
    if path==WORKFLOW:
        addition=new[new.index(MARKER):].strip()
        old=old[:old.index(MARKER)].rstrip() if MARKER in old else old.rstrip()
        return (old+'\n\n'+addition+'\n').encode('utf-8')
    for line in new.splitlines():
        m=re.match(r'\| (M(?:2[1-9]|3[0-3]))(?: \|| [^|]+ \|)',line)
        if m:
            identifier=m.group(1)
            pattern=r'^\| '+identifier+(r' \|.*$' if line.startswith('| '+identifier+' |') else r' [^|]+ \|.*$')
            old=re.sub(pattern,lambda _:line,old,flags=re.M)
    old=old.replace('- M21 이후는 기존 승인 상한 밖 후속 후보다. 이번 목록 작성으로 착수하지 않는다.',next(l for l in new.splitlines() if l.startswith('- 2026-11-04 사용자가 M21~M33')))
    return old.encode('utf-8')
def blob(path,payload,env):
    payload=payload.replace(b'\r\n',b'\n')
    key=hashlib.sha256(payload).hexdigest()
    if key not in HASH_CACHE:HASH_CACHE[key]=git('hash-object','-w','--stdin',data=payload).decode().strip()
    sha=HASH_CACHE[key]
    INDEX_UPDATES.setdefault(env['GIT_INDEX_FILE'],[]).append(f'100644 {sha}\t{path}\0'.encode('utf-8'))
def main():
    commit='--commit' in sys.argv;push='--push' in sys.argv;include_drafts='--include-drafts' in sys.argv
    head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip()
    index=Path(git('rev-parse','--git-path','index').decode().strip())
    if not index.is_absolute():index=ROOT/index
    original=index.read_bytes()
    staging=BATCH/'local-git'/str(uuid.uuid4());staging.mkdir(parents=True)
    (staging/'original.index').write_bytes(original)
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(staging/'commit.index')
    git('read-tree',head,env=env)
    reconcile=os.environ.copy();reconcile['GIT_INDEX_FILE']=str(staging/'reconcile.index')
    Path(reconcile['GIT_INDEX_FILE']).write_bytes(original)
    batch=json.loads((BATCH/'batch.json').read_text(encoding='utf-8'))
    files=[p for p in BATCH.glob('*') if p.is_file() and p.suffix in ['.py','.json','.md','.cs']]
    files+=[BATCH/'.gitignore',BATCH/'sources/index.json']
    for item in batch['items']:
        project=ROOT/'projects'/item['slug']
        files += [project/'project.json',project/'planning/production-plan.json',project/'production/tts-manifest.json',project/'production/checkpoint.json',project/'production/review-ledger.json']
        if include_drafts and item['status']=='source-audit-bilingual-draft-ready':
            files+=list((project/'planning').glob('*.json'))
            files+=list((project/'script').glob('*.json'))+list((project/'script').glob('*readthrough*.txt'))
            files+=list((project/'production').glob('*.py'))
            # Retain evidence, not full fetched article text or licensed media.
            for pattern in ('*audit.json','*numeric-qa.json','worked-calculations.json'):
                files+=list((project/'research').glob(pattern))
    if include_drafts:
        for ready_module in ('game-math-shading-lights','game-math-skinning-normal-map','game-math-pipeline-shaders','game-math-velocity-derivatives','game-math-forces-friction','game-math-momentum-collisions','game-math-parametric-hermite'):
            unity_staging=ROOT/'projects'/ready_module/'production/unity-staging'
            files+=[p for p in unity_staging.glob('*') if p.is_file() and (p.suffix in ('.cs','.shader','.py','.json') or p.name=='.gitignore') and p.name!='receipt.json' and not p.name.startswith('local-')]
    files=list(dict.fromkeys(files))
    shared=[CONTROL,WORKLIST,DOC,WORKFLOW]
    owned=[]
    for file in files:
        if not file.exists():continue
        path=file.relative_to(ROOT).as_posix();payload=file.read_bytes()
        assert file.suffix not in ['.mp4','.wav','.png','.fbx','.zip']
        if file.suffix=='.json':json.loads(payload.decode('utf-8-sig'))
        if file.suffix=='.py':compile(payload,str(file),'exec')
        blob(path,payload,env);blob(path,payload,reconcile);owned.append(path)
    for path in shared:
        payload=(ROOT/path).read_bytes()
        blob(path,projected(path,git('show',head+':'+path),payload),env)
        blob(path,projected(path,git('show',':'+path),payload),reconcile)
        owned.append(path)
    for target_env in (env,reconcile):
        git('update-index','-z','--index-info',data=b''.join(INDEX_UPDATES[target_env['GIT_INDEX_FILE']]),env=target_env)
    before=git('ls-files','--stage','-z')
    after=git('ls-files','--stage','-z',env=reconcile)
    def outsiders(raw):return {r.split(b'\t',1)[1]:r.split(b'\t',1)[0] for r in raw.split(b'\0') if b'\t' in r and r.split(b'\t',1)[1].decode() not in owned}
    assert outsiders(before)==outsiders(after),'Unrelated staged entries changed'
    git('diff','--cached','--check',env=env)
    subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=env,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    tree=git('write-tree',env=env).decode().strip()
    report={'baseHead':head,'ownedPaths':owned,'unrelatedStagingPreserved':True,'stage':'source-faithful drafts, actual-game audits and Unity source staging; no final video completion','committed':False}
    if commit:
        message=b'Build source-faithful math drafts and M21 lighting lab preflight\n' if include_drafts else b'Prepare authorized M21-M33 math lectures and source audit queue\n'
        new=git('commit-tree',tree,'-p',head,data=message).decode().strip()
        helper=ROOT/'projects/buckshot-roulette-reverse-engineering/production/save-selective-git.py'
        spec=importlib.util.spec_from_file_location('scoped_git_helper',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.publish_index_and_ref(index,Path(reconcile['GIT_INDEX_FILE']).read_bytes(),original,ref,head,new)
        report.update(committed=True,commit=new)
        if push:
            subprocess.run(['git','push','origin',ref],cwd=ROOT,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            remote=git('ls-remote','origin',ref).decode().split()[0]
            assert remote==new
            report.update(pushed=True,remoteSha=remote)
    (staging/'receipt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='ownedPaths'},ensure_ascii=False))
if __name__=='__main__':main()
