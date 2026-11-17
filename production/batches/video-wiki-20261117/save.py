"""Selectively save wiki prose, mapping and policy while preserving other work."""
import json, os, runpy, subprocess, tempfile
from pathlib import Path

ROOT=Path('D:/Github/VideoEditing')
HERE=Path(__file__).resolve().parent

def git(*args,data=None,env=None):
    return subprocess.check_output(['git','-c','core.safecrlf=false',*args],cwd=ROOT,input=data,env=env)

def project(path,base,current):
    a,b=base.decode('utf-8-sig'),current.decode('utf-8-sig')
    if path.endswith('.json'):
        a,b=json.loads(a),json.loads(b)
        if path=='shared/publishing/video-worklist.json':
            a['videoCompanionWiki20261117']=b['videoCompanionWiki20261117']
            return (json.dumps(a,ensure_ascii=False,indent=2)+'\n').encode('utf8')
        a['videoCompanionWikiPolicy20261117']=b['videoCompanionWikiPolicy20261117']
        a.setdefault('scopedDocumentationAuthorizations',{})['videoWiki20261117']=b['scopedDocumentationAuthorizations']['videoWiki20261117']
        return (json.dumps(a,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    if path=='AGENTS.md':
        key='- User-directed 2026-11-17 `video-companion-wiki-v1`:'
        line=next(x for x in b.splitlines() if x.startswith(key))
        if key in a:
            a='\n'.join(line if x.startswith(key) else x for x in a.splitlines())+'\n'
        else:
            marker='## Verification and delivery without repeated work'
            a=a.replace(marker,marker+'\n\n'+line,1)
        return a.encode('utf8')
    start='<!-- VIDEO-COMPANION-WIKI-20261117-START -->';end='<!-- VIDEO-COMPANION-WIKI-20261117-END -->'
    chunk=b[b.index(start):b.index(end)+len(end)]
    if start in a:a=a[:a.index(start)]+chunk+a[a.index(end)+len(end):]
    else:a=a.replace('## 1. 작업 범위와 사용자 확인','## 1. 작업 범위와 사용자 확인\n\n'+chunk,1)
    return a.encode('utf8')

def main():
    publish=runpy.run_path(str(ROOT/'projects/buckshot-roulette-reverse-engineering/production/save-selective-git.py'))['publish_index_and_ref']
    head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip()
    index=Path(git('rev-parse','--path-format=absolute','--git-path','index').decode().strip());original=index.read_bytes()
    direct=[p for p in HERE.rglob('*') if p.is_file() and 'evidence' not in p.relative_to(HERE).parts and '__pycache__' not in p.parts and p.suffix in {'.md','.json','.py','.html'}]
    direct.append(ROOT/'docs/VIDEO_WIKI_WORKFLOW.md')
    shared=['AGENTS.md','docs/VIDEO_WORKFLOW.md','shared/publishing/video-production-control.json','shared/publishing/video-worklist.json']
    with tempfile.TemporaryDirectory() as tmp:
        ce=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'commit.index'));re=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'reconcile.index'))
        git('read-tree',head,env=ce);Path(re['GIT_INDEX_FILE']).write_bytes(original)
        buffers={e['GIT_INDEX_FILE']:bytearray() for e in (ce,re)}
        def stage(path,raw,env):
            raw=raw.replace(b'\r\n',b'\n');oid=git('hash-object','-w','--stdin',data=raw).decode().strip()
            buffers[env['GIT_INDEX_FILE']].extend(f'100644 {oid}\t{path}\0'.encode('utf8'))
        for p in direct:
            raw=p.read_bytes()
            if p.suffix=='.json':json.loads(raw.decode('utf-8-sig'))
            if p.suffix=='.py':compile(raw,str(p),'exec')
            for e in (ce,re):stage(p.relative_to(ROOT).as_posix(),raw,e)
        for path in shared:
            for e,rev in ((ce,head+':'+path),(re,':'+path)):stage(path,project(path,git('show',rev),(ROOT/path).read_bytes()),e)
        for e in (ce,re):git('update-index','-z','--index-info',data=bytes(buffers[e['GIT_INDEX_FILE']]),env=e)
        git('diff','--cached','--check',env=ce)
        subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=ce,check=True)
        paths=git('diff','--cached','--name-only',head,env=ce).decode().splitlines()
        if not paths:print('No wiki changes');return
        tree=git('write-tree',env=ce).decode().strip()
        commit=git('commit-tree',tree,'-p',head,data=b'Deepen wiki articles into illustrated development methodology columns\n').decode().strip()
        publish(index,Path(re['GIT_INDEX_FILE']).read_bytes(),original,ref,head,commit)
        print(commit,len(paths),'wiki files; unrelated staging preserved')
    subprocess.run(['git','push','origin',ref],cwd=ROOT,check=True)

if __name__=='__main__':main()
