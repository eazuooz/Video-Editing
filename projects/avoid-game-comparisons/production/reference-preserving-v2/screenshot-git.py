"""Commit an explicit selected-video allowlist with a separate index."""
from pathlib import Path
import os,subprocess,json,hashlib,datetime,shutil,sys
R=Path(__file__).resolve().parents[4];V=Path(__file__).parent;phase=sys.argv[1]
assert phase in ['design','delivery']
O=R/f'shared/output/avoid-game-comparisons/git-screenshots-{phase}';O.mkdir(parents=True,exist_ok=True)
names=['screenshot-assets.py','screenshot-assets.json','prepare-screenshot-revision.py','screenshot-edit.py','screenshot-git.py','tsconfig.screenshots.json','finish-screenshot-revision.py','edit-plan.json','review-ledger.json']
paths=[(V/n).relative_to(R).as_posix() for n in names if(V/n).exists()]
paths += ['docs/VIDEO_WORKLIST.md','shared/publishing/video-worklist.json','shared/publishing/video-production-control.json','projects/avoid-game-comparisons/project.json','projects/avoid-game-comparisons/rebuild.json','projects/avoid-game-comparisons/planning/chapter-plan.json','projects/avoid-game-comparisons/production/latest-checkpoint.json','projects/avoid-game-comparisons/production/delivery-output.json']
paths += [p.relative_to(R).as_posix() for p in (R/'motion-canvas/src/projects/avoid-game-comparisons/revision-v2/screenshots').iterdir() if p.suffix in ['.tsx','.ts','.meta']]
def run(a,env=None):return subprocess.run(a,cwd=R,env=env,capture_output=True,check=True).stdout
def git(*a,env=None):return run(['git',*a],env)
def foreign():return [r for r in git('ls-files','--stage','-z').split(b'\0') if r and r.split(b'\t',1)[1].decode() not in paths]
assert not set(paths)&set(git('diff','--cached','--name-only','-z').decode().split('\0'))
idx=Path(git('rev-parse','--git-path','index').decode().strip());idx=idx if idx.is_absolute() else R/idx
shutil.copy2(idx,O/'real-index-before.bin');before=foreign()
watch=['projects/rebuild-index.json','unity/VideoEditing/ProjectSettings/URPProjectSettings.asset'];hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in watch}
for p in paths:
 if p.endswith(('.json','.meta')):json.loads((R/p).read_text(encoding='utf-8-sig'))
isolated=O/'commit.index';assert not isolated.exists()
env=dict(os.environ,GIT_INDEX_FILE=str(isolated));git('read-tree','HEAD',env=env);git('add','--',*paths,env=env)
changed=set(git('diff','--cached','--name-only','-z',env=env).decode().split('\0'))-{''};assert changed and changed<=set(paths)
git('diff','--cached','--check',env=env);run(['node','scripts/media-policy.cjs'],env)
git('commit','-m',('Design screenshot-supported D18 explanations with preserved audio and timing' if phase=='design' else 'Deliver D18 screenshot explanations and verify unchanged audio and footage ratio'),env=env)
sha=git('rev-parse','HEAD').decode().strip();git('reset','-q','HEAD','--',*paths);assert before==foreign();assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
branch=git('branch','--show-current').decode().strip();git('push','origin','HEAD:refs/heads/'+branch);remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0];assert remote==sha
receipt={'commit':sha,'remoteSha':remote,'changedPaths':sorted(changed),'foreignIndexAndFilesPreserved':True,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()};(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
