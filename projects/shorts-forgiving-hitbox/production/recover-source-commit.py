"""Recover the created commit after a verified stale, empty Git lock blocked index sync."""
from pathlib import Path
import json,subprocess,time,psutil
R=Path(__file__).resolve().parents[3];O=R/'shared/output/shorts-commits/shorts-hitbox-scenes-20261018'
receipt=O/'receipt.json';v=json.loads(receipt.read_text());paths=set(v['paths'])
assert not v['indexSynchronized'] and v['remoteSha'] is None
def git(*args):
 r=subprocess.run(['git',*args],cwd=R,capture_output=True);assert r.returncode==0,(r.stdout+r.stderr).decode(errors='replace')[-1200:];return r.stdout
lock=(R/'.git/index.lock').resolve();assert lock==R.resolve()/'.git/index.lock'
assert not [p for p in psutil.process_iter(['name']) if (p.info['name'] or '').lower() in ['git.exe','git-remote-https.exe','git-lfs.exe']]
st=lock.stat();assert st.st_size==0 and time.time()-st.st_mtime>300
assert git('rev-parse','HEAD').decode().strip()==v['commit']
before=[x for x in git('ls-files','--stage','-z').split(b'\0') if x and x.split(b'\t',1)[1].decode() not in paths]
destination=O/'stale-index.lock.preserved';assert not destination.exists();lock.rename(destination)
git('reset','-q',v['commit'],'--',*sorted(paths))
after=[x for x in git('ls-files','--stage','-z').split(b'\0') if x and x.split(b'\t',1)[1].decode() not in paths];assert before==after
v.update(indexSynchronized=True,foreignIndexPreserved=True,staleLockRecovery=dict(bytes=0,ageSeconds=time.time()-st.st_mtime,activeGitProcesses=0,preservedAt=str(destination.relative_to(R))))
receipt.write_text(json.dumps(v,indent=2)+'\n')
ref=git('symbolic-ref','HEAD').decode().strip();git('push','origin',v['commit']+':'+ref)
remote=git('ls-remote','origin',ref).decode().split()[0];assert remote==v['commit'];v['remoteSha']=remote;receipt.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(commit=v['commit'],remoteSha=remote,indexSynchronized=True)))
