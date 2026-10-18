"""Commit an explicit D21 allowlist, preserving foreign staging and history."""
from pathlib import Path
import datetime, json, os, shutil, subprocess, sys
R=Path(__file__).resolve().parents[4]
unit=sys.argv[1]
spec=json.loads((R/sys.argv[2]).read_text(encoding='utf-8-sig'))
paths=spec['paths']
shared={'AGENTS.md','docs/VIDEO_WORKFLOW.md','shared/publishing/game-example-coverage-policy.json','shared/publishing/video-production-control.json','.gitignore','shared/git-essential-images.json','shared/publishing/video-worklist.json','docs/VIDEO_WORKLIST.md'}
assert paths and all(p.startswith(('projects/player-customization/','motion-canvas/src/projects/player-customization/')) or p in shared for p in paths)
rasters=[p for p in paths if Path(p).suffix.lower() in ['.png','.jpg','.webp']]
assert all('/publishing/' in p for p in rasters)
assert all(Path(p).suffix.lower() in ['.json','.md','.py','.cjs','.mjs','.ts','.tsx','.txt','.srt','.ass','.html','.css'] or p in rasters or p=='.gitignore' for p in paths)
O=R/'shared/output/player-customization'/('git-'+unit)
O.mkdir(parents=True,exist_ok=True)

def git(*args,env=None):
    p=subprocess.run(['git',*args],cwd=R,env=env,capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
def foreign():
    return [v for v in git('ls-files','--stage','-z').split(b'\0') if v and v.split(b'\t',1)[1].decode() not in paths]

for p in paths:
    if p.endswith('.json'):json.loads((R/p).read_text(encoding='utf-8-sig'))
before=foreign()
index=Path(git('rev-parse','--git-path','index').decode().strip())
if not index.is_absolute():index=R/index
shutil.copy2(index,O/'real-index-before.bin')
head=git('rev-parse','HEAD').decode().strip()
isolated=O/'commit.index';assert not isolated.exists()
env=dict(os.environ,GIT_INDEX_FILE=str(isolated))
git('read-tree',head,env=env);git('add','--',*paths,env=env)
changed=set(git('diff','--cached','--name-only','-z',env=env).decode().split('\0'))-{''}
assert changed and changed<=set(paths)
git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
assert git('rev-parse','HEAD').decode().strip()==head,'Concurrent HEAD changed; refresh isolated index from new HEAD before commit'
git('commit','-m',spec['message'],env=env)
sha=git('rev-parse','HEAD').decode().strip()
git('reset','-q','HEAD','--',*paths)
assert before==foreign(),'Foreign staging changed concurrently; do not restore or overwrite it'
branch=git('branch','--show-current').decode().strip()
git('push','origin','HEAD:refs/heads/'+branch)
remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0]
git('merge-base','--is-ancestor',sha,remote)
receipt={'commit':sha,'remoteSha':remote,'commitIsRemoteAncestor':True,'paths':sorted(changed),
 'foreignIndexPreserved':True,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
