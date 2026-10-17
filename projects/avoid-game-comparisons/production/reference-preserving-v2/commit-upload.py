from pathlib import Path
import os,subprocess,json,hashlib,shutil,datetime
R=Path(__file__).resolve().parents[4];P='projects/avoid-game-comparisons';O=R/'shared/output/avoid-game-comparisons/git-private-upload-v2';O.mkdir(parents=True,exist_ok=True)
paths=['shared/publishing/video-production-control.json','shared/publishing/video-worklist.json','docs/VIDEO_WORKLIST.md',P+'/project.json',P+'/production/latest-checkpoint.json',P+'/production/reference-preserving-v2/review-ledger.json']+[P+'/production/reference-preserving-v2/'+n for n in ['authorize-upload.py','finish-upload.py','commit-upload.py']]+[P+'/publishing/reference-preserving-v2/'+n for n in ['metadata.json','description.en.txt','youtube-upload.json']]
def git(*a,env=None):return subprocess.run(['git',*a],cwd=R,env=env,capture_output=True,check=True).stdout
def foreign():return [r for r in git('ls-files','--stage','-z').split(b'\0') if r and r.split(b'\t',1)[1].decode() not in paths]
before=foreign();idx=Path(git('rev-parse','--git-path','index').decode().strip());idx=idx if idx.is_absolute() else R/idx;shutil.copy2(idx,O/'real-index-before.bin')
watch=['projects/rebuild-index.json','unity/VideoEditing/ProjectSettings/URPProjectSettings.asset'];hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in watch}
for p in paths:
 if p.endswith('.json'):json.loads((R/p).read_text(encoding='utf8'))
isolated=O/'commit.index';assert not isolated.exists();env=dict(os.environ,GIT_INDEX_FILE=str(isolated));git('read-tree','HEAD',env=env);git('add','--',*paths,env=env)
changed=set(git('diff','--cached','--name-only','-z',env=env).decode().split('\0'))-{''};assert changed and changed<=set(paths);git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
git('commit','-m','Upload approved D18 screenshot master privately and activate D19 production',env=env)
sha=git('rev-parse','HEAD').decode().strip();git('reset','-q','HEAD','--',*paths);assert before==foreign();assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
branch=git('branch','--show-current').decode().strip();git('push','origin','HEAD:refs/heads/'+branch);remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0];assert remote==sha
receipt=dict(commit=sha,remoteSha=remote,paths=sorted(changed),foreignIndexAndFilesPreserved=True,at=datetime.datetime.now(datetime.timezone.utc).isoformat());(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
