"""Save only this publishing batch and its bounded shared ledger entries."""
import argparse, copy, json, os, runpy, subprocess, tempfile
from pathlib import Path
from finish import ROOT, HERE, KEY, START, END, ROW_FIELDS

def git(*args,data=None,env=None):
    return subprocess.check_output(['git','-c','core.safecrlf=false',*args],cwd=ROOT,input=data,env=env)

def project(path,base,current):
    if path.endswith('.md'):
        a=base.decode('utf-8-sig');b=current.decode('utf-8-sig')
        start,end=(('<!-- THUMBNAIL-NATURAL-ACTION-20261117-START -->','<!-- THUMBNAIL-NATURAL-ACTION-20261117-END -->') if path.endswith('VIDEO_25D_THUMBNAIL_REVIEW.md') else (START,END))
        block=b[b.index(start):b.index(end)+len(end)]
        return (a[:a.index(start)]+block+a[a.index(end)+len(end):] if start in a else a.rstrip()+'\n\n'+block+'\n').encode('utf8')
    a=json.loads(base.decode('utf-8-sig'));b=json.loads(current.decode('utf-8-sig'))
    if path.endswith('git-essential-images.json'):
        prefix=HERE.relative_to(ROOT).as_posix()+'/thumbnail-revision-v2/'
        selected={e['path']:e for e in b['entries'] if e['path'].startswith(prefix)}
        assert len(selected)==13
        a['entries']=[copy.deepcopy(selected.pop(e['path'])) if e['path'] in selected else e for e in a['entries']]
        a['entries'].extend(copy.deepcopy(list(selected.values())))
    elif path.endswith('video-production-control.json'):
        a.setdefault('scopedPublishingAuthorizations',{})[KEY]=copy.deepcopy(b['scopedPublishingAuthorizations'][KEY])
    else:
        a[KEY]=copy.deepcopy(b[KEY]);ids=set(b[KEY]['scope'])
        updates={r['id']:r for r in b['rows'] if r['id'] in ids}
        for r in a['rows']:
            if r['id'] in updates:
                for field in ROW_FIELDS:r[field]=copy.deepcopy(updates[r['id']][field])
    return (json.dumps(a,ensure_ascii=False,indent=2)+'\n').encode('utf8')

def main(push,message):
    publish=runpy.run_path(str(ROOT/'projects/buckshot-roulette-reverse-engineering/production/save-selective-git.py'))['publish_index_and_ref']
    head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip()
    index=Path(git('rev-parse','--path-format=absolute','--git-path','index').decode().strip());original=index.read_bytes()
    extensions={'.json','.py','.cjs','.md','.txt','.svg','.html'}
    direct=[p for p in HERE.rglob('*') if p.is_file() and 'evidence' not in p.relative_to(HERE).parts and '__pycache__' not in p.parts and not p.name.startswith('worksheet') and (p.suffix in extensions or p.name=='.gitignore')]
    direct.extend(HERE/'thumbnail-revision-v2'/('M'+str(i))/'thumbnail.png' for i in range(21,34))
    shared=['shared/publishing/video-production-control.json','shared/publishing/video-worklist.json','shared/git-essential-images.json','docs/VIDEO_WORKLIST.md','docs/GAME_MATH_PRIVATE_POLISH.md','docs/VIDEO_25D_THUMBNAIL_REVIEW.md']
    with tempfile.TemporaryDirectory() as temp:
        ce=dict(os.environ,GIT_INDEX_FILE=str(Path(temp)/'commit.index'));re=dict(os.environ,GIT_INDEX_FILE=str(Path(temp)/'reconcile.index'))
        git('read-tree',head,env=ce);Path(re['GIT_INDEX_FILE']).write_bytes(original)
        buffers={e['GIT_INDEX_FILE']:bytearray() for e in (ce,re)}
        def stage(path,data,env):
            if not path.endswith('.png'):data=data.replace(b'\r\n',b'\n')
            oid=git('hash-object','-w','--stdin',data=data).decode().strip()
            buffers[env['GIT_INDEX_FILE']].extend(f'100644 {oid}\t{path}\0'.encode('utf8'))
        for p in direct:
            data=p.read_bytes();rel=p.relative_to(ROOT).as_posix()
            if p.suffix=='.json':json.loads(data.decode('utf-8-sig'))
            if p.suffix=='.py':compile(data,str(p),'exec')
            for e in (ce,re):stage(rel,data,e)
        for path in shared:
            for e,revision in ((ce,head+':'+path),(re,':'+path)):
                stage(path,project(path,git('show',revision),(ROOT/path).read_bytes()),e)
        for e in (ce,re):git('update-index','-z','--index-info',env=e,data=bytes(buffers[e['GIT_INDEX_FILE']]))
        git('diff','--cached','--check',env=ce)
        subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=ce,check=True)
        changed=git('diff','--cached','--name-only',head,env=ce).decode().splitlines()
        if not changed:print('No publishing changes');return
        tree=git('write-tree',env=ce).decode().strip()
        commit=git('commit-tree',tree,'-p',head,data=(message+'\n').encode('utf8')).decode().strip()
        publish(index,Path(re['GIT_INDEX_FILE']).read_bytes(),original,ref,head,commit)
        print(commit,len(changed),'publishing files; unrelated staging preserved')
    if push:subprocess.run(['git','push','origin',ref],cwd=ROOT,check=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--push',action='store_true');p.add_argument('--message',default='Save approved game math publishing changes');a=p.parse_args();main(a.push,a.message)
