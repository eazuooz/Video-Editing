"""Commit an explicit text/code allowlist with an isolated index and remote proof."""
from pathlib import Path
import os,subprocess,json,hashlib,shutil,datetime,sys
R=Path(__file__).resolve().parents[3]
unit=sys.argv[1]; spec=json.loads((R/sys.argv[2]).read_text(encoding='utf8'));paths=spec['paths']
thumbnail='projects/ai-games-showcase-2026/publishing/reference-preserving-v2/thumbnail-v2.png'
assert paths and all(p.startswith(('projects/ai-games-showcase-2026/','motion-canvas/src/projects/ai-games-showcase-2026/')) or p in ['shared/publishing/video-worklist.json','docs/VIDEO_WORKLIST.md','shared/publishing/video-production-control.json','shared/git-essential-images.json','.gitignore','scripts/render-video-worklist.py','production/preflight/ai-games-showcase-2026.json','production/preflight/ai-games-showcase-2026/candidate.json','production/preflight/ai-games-showcase-2026/studio-review.json'] for p in paths)
assert all(Path(p).suffix in ['.json','.md','.py','.cjs','.mjs','.ts','.tsx','.txt','.srt','.ass','.html','.css'] or p in ['.gitignore',thumbnail] for p in paths)
if thumbnail in paths:
 registry=json.loads((R/'shared/git-essential-images.json').read_text(encoding='utf8'))
 assert any(e['path']==thumbnail and e['sha256']==hashlib.sha256((R/thumbnail).read_bytes()).hexdigest() for e in registry['entries'])
O=R/'shared/output/ai-games-showcase-2026'/('git-'+unit);O.mkdir(parents=True,exist_ok=True)
def git(*a,env=None):return subprocess.run(['git',*a],cwd=R,env=env,capture_output=True,check=True).stdout
def foreign():return [r for r in git('ls-files','--stage','-z').split(b'\0') if r and r.split(b'\t',1)[1].decode() not in paths]
before=foreign();idx=Path(git('rev-parse','--git-path','index').decode().strip());idx=idx if idx.is_absolute() else R/idx;shutil.copy2(idx,O/'real-index-before.bin')
for p in paths:
 if p.endswith('.json'):json.loads((R/p).read_text(encoding='utf8'))
isolated=O/'commit.index';assert not isolated.exists();env=dict(os.environ,GIT_INDEX_FILE=str(isolated));git('read-tree','HEAD',env=env);git('add','--',*paths,env=env)
changed=set(git('diff','--cached','--name-only','-z',env=env).decode().split('\0'))-{''};assert changed and changed<=set(paths);git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
git('commit','-m',spec['message'],env=env);sha=git('rev-parse','HEAD').decode().strip();git('reset','-q','HEAD','--',*paths);assert before==foreign()
branch=git('branch','--show-current').decode().strip();git('push','origin','HEAD:refs/heads/'+branch);remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0];assert remote==sha
receipt=dict(commit=sha,remoteSha=remote,paths=sorted(changed),foreignIndexPreserved=True,at=datetime.datetime.now(datetime.timezone.utc).isoformat());(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
