"""Commit an explicit text/code allowlist with an isolated index and remote proof."""
from pathlib import Path
import os,subprocess,json,hashlib,shutil,datetime,sys
R=Path(__file__).resolve().parents[3]
unit=sys.argv[1]; spec=json.loads((R/sys.argv[2]).read_text(encoding='utf8'));paths=spec['paths']
thumbnail='projects/game-math-euler-axis-angle/publishing/reference-preserving-v2/thumbnail-v2.png'
unity_root='unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/'
assert paths and all(p.startswith(('projects/game-math-euler-axis-angle/','motion-canvas/src/projects/game-math-euler-axis-angle/',unity_root)) or p in [unity_root.rstrip('/')+'.meta','AGENTS.md','docs/VIDEO_WORKFLOW.md','docs/NARRATION_AUDIO_STANDARD.md','templates/video-project/project.json','shared/publishing/video-worklist.json','docs/VIDEO_WORKLIST.md','shared/publishing/video-production-control.json','shared/git-essential-images.json','.gitignore','scripts/render-video-worklist.py','scripts/collect-video-output.cjs','scripts/build-rebuild-manifests.cjs','production/preflight/game-math-euler-axis-angle.json','production/preflight/game-math-euler-axis-angle/candidate.json','production/preflight/game-math-euler-axis-angle/studio-review.json'] for p in paths)
text_extensions=['.json','.md','.py','.cjs','.mjs','.ts','.tsx','.txt','.srt','.ass','.html','.css']
unity_extensions=['.cs','.asmdef','.meta','.unity','.mat','.asset','.shader']
assert all(Path(p).suffix in text_extensions or (p.startswith(unity_root) or p==unity_root.rstrip('/')+'.meta') and Path(p).suffix in unity_extensions or p in ['.gitignore',thumbnail] for p in paths)
assert all('/local/' not in p and '/__pycache__/' not in p for p in paths)
if thumbnail in paths:
 registry=json.loads((R/'shared/git-essential-images.json').read_text(encoding='utf8'))
 assert any(e['path']==thumbnail and e['sha256']==hashlib.sha256((R/thumbnail).read_bytes()).hexdigest() for e in registry['entries'])
O=R/'shared/output/game-math-euler-axis-angle'/('git-'+unit);O.mkdir(parents=True,exist_ok=True)
def git(*a,env=None):
 r=subprocess.run(['git',*a],cwd=R,env=env,capture_output=True)
 if r.returncode:raise RuntimeError('Git '+str(a[:3])+': '+(r.stdout+r.stderr).decode(errors='replace')[-2500:])
 return r.stdout
def foreign():return [r for r in git('ls-files','--stage','-z').split(b'\0') if r and r.split(b'\t',1)[1].decode() not in paths]
before=foreign();idx=Path(git('rev-parse','--git-path','index').decode().strip());idx=idx if idx.is_absolute() else R/idx;shutil.copy2(idx,O/'real-index-before.bin')
for p in paths:
 if p.endswith('.json'):json.loads((R/p).read_text(encoding='utf8'))
isolated=O/'commit.index';assert not isolated.exists();env=dict(os.environ,GIT_INDEX_FILE=str(isolated));git('read-tree','HEAD',env=env);git('add','--',*paths,env=env)
changed=set(git('diff','--cached','--name-only','-z',env=env).decode().split('\0'))-{''};assert changed and changed<=set(paths)
# Unity serializes empty YAML values with a trailing blank. Preserve the actual
# saved source bytes while checking other whitespace and every non-Unity file.
plain=[p for p in paths if not p.startswith(unity_root) and p!=unity_root.rstrip('/')+'.meta']
serialized=[p for p in paths if p not in plain]
if plain:git('diff','--cached','--check','--',*plain,env=env)
if serialized:git('-c','core.whitespace=-blank-at-eol','diff','--cached','--check','--',*serialized,env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
git('commit','-m',spec['message'],env=env);sha=git('rev-parse','HEAD').decode().strip();git('reset','-q','HEAD','--',*paths);assert before==foreign()
branch=git('branch','--show-current').decode().strip();git('push','origin','HEAD:refs/heads/'+branch);remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0];assert remote==sha
receipt=dict(commit=sha,remoteSha=remote,paths=sorted(changed),foreignIndexPreserved=True,at=datetime.datetime.now(datetime.timezone.utc).isoformat());(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
