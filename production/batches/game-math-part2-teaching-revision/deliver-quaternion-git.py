"""Explicit text/essential-image delivery using an isolated Git index.

Shared files stage only this task's causal paragraph or exact approved rows.
Foreign staged/working changes and media are never added or rewritten.
Run --prepare, inspect the saved path list/diff, then --commit-and-push.
"""
from pathlib import Path
import os,json,subprocess,hashlib,argparse,shutil,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
OUT=ROOT/'shared/output/game-math-part2-teaching-revision/git-delivery';OUT.mkdir(exist_ok=True)
GIT=shutil.which('git');assert GIT
NODE=shutil.which('node');assert NODE
parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--commit-and-push',action='store_true');args=parser.parse_args();assert args.prepare!=args.commit_and_push
def run(cmd,env=None):return subprocess.check_output(cmd,cwd=ROOT,env=env,stderr=subprocess.STDOUT)
def git(*args,env=None):return run([GIT,*args],env)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SLUGS=['game-math-quaternion-foundations-v2','game-math-quaternion-calculations-v2']
TEXT={'.json','.md','.py','.cjs','.ts','.tsx','.meta','.srt','.ass','.txt','.html','.css'}
pathlist=OUT/'explicit-paths.json';preparation=OUT/'preparation.json'
if args.prepare:
    head=git('rev-parse','HEAD').decode().strip();assert git('branch','--show-current').decode().strip()=='main'
    index=OUT/'quaternion.index'
    if index.exists():index.unlink()  # Exact owned temporary file, never normal index.
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(index)
    git('read-tree',head,env=env)
    paths=set()
    for slug in SLUGS:
        receipt=read(ROOT/f'projects/{slug}/publishing/youtube-upload.json');assert receipt['privateUploadComplete'] and receipt['fullPublishingSettingsComplete']
        for prefix in [ROOT/'projects'/slug,ROOT/'motion-canvas/src/projects'/slug]:
            for p in prefix.rglob('*'):
                if p.is_file() and p.suffix in TEXT and '__pycache__' not in p.parts:paths.add(p.relative_to(ROOT).as_posix())
        paths.add(f'projects/{slug}/publishing/thumbnail-v2.png');paths.add(f'projects/{slug}/publishing/proof/uploaded-cc-off.png')
    for version in ['v2','v3','v4','v5','v6']:
        for p in (ROOT/f'projects/game-math-quaternion-teaching-additions-{version}').rglob('*'):
            if p.is_file() and p.suffix in TEXT:paths.add(p.relative_to(ROOT).as_posix())
    for p in B.iterdir():
        if not p.is_file() or p.suffix not in TEXT:continue
        if any(x in p.name for x in ['interpolation','lines-bounds','remaining-chapter']):continue
        if 'v7' in p.name and p.name!='quaternion-v7-rejected-equipment-reading.json':continue
        paths.add(p.relative_to(ROOT).as_posix())
    for prefix in [B/'dense-body-tracks',B/'baselines/game-math-quaternion-operations',B/'baselines/landmark-drafts-before-native-time-fix']:
        for p in prefix.rglob('*'):
            if p.is_file() and p.suffix in TEXT:paths.add(p.relative_to(ROOT).as_posix())
    for name in ['supplements.py','bridges.py']:paths.add('manim/projects/game-math-part2-teaching-revision/'+name)
    image_paths=[p for p in sorted(paths) if Path(p).suffix=='.png']
    current_registry=read(ROOT/'shared/git-essential-images.json')
    for p in image_paths:
        entry=next(x for x in current_registry['entries'] if x['path']==p)
        assert entry['sha256']==sha(ROOT/p) and entry['purpose'] in ['delivery-thumbnail','minimal-publishing-proof']
    shared={}
    def headtext(p):return git('show',head+':'+p).decode('utf8')
    a=(ROOT/'AGENTS.md').read_text(encoding='utf8');paragraph=next(p for p in a.split('\n\n') if p.startswith('- Causal teaching flow,'))
    base=headtext('AGENTS.md');shared['AGENTS.md']=base if paragraph in base else base.replace('# Video production defaults\n','# Video production defaults\n\n'+paragraph+'\n',1)
    a=(ROOT/'docs/VIDEO_WORKFLOW.md').read_text(encoding='utf8');heading='## 앞의 결과가 다음 질문을 만드는 강의 흐름 — 2026-10-10 승인'
    section=a[a.index(heading):];section=section.split('\n## ',1)[0].rstrip()
    base=headtext('docs/VIDEO_WORKFLOW.md');at=base.index('\n')+1
    shared['docs/VIDEO_WORKFLOW.md']=base if heading in base else base[:at]+'\n'+section+'\n\n'+base[at:]
    path='production/batches/game-math-part2-full-series/README.md';a=(ROOT/path).read_text(encoding='utf8');paragraph=next(x for x in a.split('\n\n') if x.startswith('2026-10-10 추가 요청: 강의 전체의 질문'))
    base=headtext(path);at=base.index('\n')+1;shared[path]=base if paragraph in base else base[:at]+'\n'+paragraph+'\n'+base[at:]
    r=json.loads(headtext('shared/git-essential-images.json'));r['entries']=[x for x in r['entries'] if x['path'] not in image_paths]+[x for x in current_registry['entries'] if x['path'] in image_paths]
    shared['shared/git-essential-images.json']=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    base=headtext('.gitignore')
    for p in image_paths:
        exception='!/'+p
        if exception not in base.splitlines():base=base.rstrip()+'\n'+exception+'\n'
    shared['.gitignore']=base
    base=json.loads(headtext('motion-canvas/projects.json'));current=read(ROOT/'motion-canvas/projects.json')
    for value in current:
        if any('/'+slug+'/' in value for slug in SLUGS) and value not in base:base.append(value)
    shared['motion-canvas/projects.json']=json.dumps(base,ensure_ascii=False,indent=2)+'\n'
    assert not any(Path(p).suffix.lower() in {'.wav','.mp4','.mp3','.m4a','.zip','.pt','.jpg'} for p in paths)
    for p in sorted(paths):git('add','--',p,env=env)
    for p,content in shared.items():
        blob=OUT/('shared-'+p.replace('/','--'));blob.write_text(content,encoding='utf8')
        digest=git('hash-object','-w',str(blob)).decode().strip();git('update-index','--add','--cacheinfo','100644',digest,p,env=env)
    staged=git('diff','--cached','--name-only',env=env).decode().splitlines();assert set(staged)<=paths|set(shared)
    write(pathlist,{'explicitPaths':sorted(paths),'sharedBlobPaths':sorted(shared),'essentialImages':image_paths,'stagedPaths':staged})
    (OUT/'staged.diff').write_bytes(git('diff','--cached','--stat',env=env)+git('diff','--cached','--',*shared.keys(),env=env))
    normal_index=Path(git('rev-parse','--git-path','index').decode().strip());normal_index=normal_index if normal_index.is_absolute() else ROOT/normal_index
    write(preparation,{'baseHead':head,'isolatedIndex':str(index),'normalIndex':str(normal_index),'normalIndexSha256':sha(normal_index),'pathsSha256':sha(pathlist),'stagedCount':len(staged),'review':'pending explicit staged path/shared-diff review','createdAt':datetime.datetime.now().astimezone().isoformat()})
    print(json.dumps({'stagedCount':len(staged),'essentialImages':len(image_paths),'review':str(OUT/'staged.diff'),'commitCreated':False}))
else:
    prep=read(preparation);assert prep['review']=='directly-reviewed-explicit-paths-and-shared-diff'
    assert git('rev-parse','HEAD').decode().strip()==prep['baseHead'],'Concurrent HEAD changed; prepare again from the current HEAD.'
    assert sha(pathlist)==prep['pathsSha256'];env=os.environ.copy();env['GIT_INDEX_FILE']=prep['isolatedIndex']
    print(run([NODE,'scripts/media-policy.cjs'],env).decode(),end='')
    # Project manifests are checked against the live source tree independently
    # before preparation. A foreign global stale manifest is never rewritten.
    for slug in SLUGS:print(run([NODE,'scripts/build-rebuild-manifests.cjs',slug,'--check']).decode(),end='')
    git('commit','-m','Deliver coherent quaternion lectures with tracked gameplay and bilingual private uploads',env=env)
    commit=git('rev-parse','HEAD').decode().strip()
    normal_unchanged=sha(Path(prep['normalIndex']))==prep['normalIndexSha256']
    push=git('push','origin','HEAD:main').decode()
    remote=git('ls-remote','origin','refs/heads/main').decode().split()[0]
    assert remote==commit,'Remote advanced concurrently; verify ancestry before marking delivery.'
    record={'commit':commit,'remoteSha':remote,'pushOutput':push,'normalIndexBytesUnchanged':normal_unchanged,'normalIndexWrittenByTask':False,'explicitPaths':str(pathlist.relative_to(ROOT)),'sharedFilesStagedAsTaskOnlyBlobs':True,'videoAudioArchivesCommitted':False,'privateVideoIds':['HdJw7bgKlbM','SPq_41LyOG0'],'deliveredAt':datetime.datetime.now().astimezone().isoformat(),'scheduleReplacementComplete':False,'fullBatchCompleted':False}
    write(B/'quaternion-git-delivery.json',record)
    q=read(B/'queue.json');q['items'][0]['revision'].update(gitDelivered=True,gitCommit=commit,remoteVerifiedSha=remote);q['items'][0]['status']='reviewed-private-revision-and-git-delivered; schedule-transition-pending';write(B/'queue.json',q)
    print(json.dumps(record,ensure_ascii=False))
