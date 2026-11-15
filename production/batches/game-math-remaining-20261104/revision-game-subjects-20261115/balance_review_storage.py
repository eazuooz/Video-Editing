"""Keep verified review URLs while balancing two nearly full local disks."""
from subject_revision import *
import psutil

def main():
 targetroot=ROOT/'output/game-math-game-subjects-20261115/local-masters';targetroot.mkdir(exist_ok=True)
 manifest=HERE/'local-master-storage.json';records=[]
 assert not manifest.exists(),'Migration already recorded; do not repeat'
 for eid in ('M23','M24','M25'):
  e=EPISODES[eid];source=DEST/e['slug'];target=targetroot/e['slug'];backup=DEST/(e['slug']+'.migration-verified-copy')
  assert source.resolve().parent==DEST.resolve() and not target.exists() and not backup.exists()
  assert read(work(e)/'qa.json')['status']=='pass'
  assert not any(str(source).replace('\\','/').lower() in ' '.join(x.info['cmdline'] or []).replace('\\','/').lower() for x in psutil.process_iter(['cmdline']))
  hashes={str(f.relative_to(source)):sha(f) for f in source.rglob('*') if f.is_file()}
  assert shutil.disk_usage(targetroot).free>sum(f.stat().st_size for f in source.rglob('*') if f.is_file())+512*1024**2
  shutil.copytree(source,target)
  assert hashes=={str(f.relative_to(target)):sha(f) for f in target.rglob('*') if f.is_file()}
  source.rename(backup)
  # Only creates a directory junction. No shell-built deletion/move commands.
  command=f"New-Item -ItemType Junction -Path '{source}' -Target '{target}' | Out-Null"
  subprocess.run(['powershell.exe','-NoProfile','-Command',command],check=True,capture_output=True)
  assert source.resolve()==target.resolve()
  assert hashes=={str(f.relative_to(source)):sha(f) for f in source.rglob('*') if f.is_file()}
  assert backup.resolve().parent==DEST.resolve() and backup.resolve()!=DEST.resolve()
  assert hashes=={str(f.relative_to(backup)):sha(f) for f in backup.rglob('*') if f.is_file()}
  records.append(dict(episode=eid,urlPath=str(source),physicalPath=str(target),fileHashes=hashes,status='all-copied-files-hash-verified-before-redundant-copy-removal'))
  save(manifest,dict(scope='Only three internally passed local review folders; same C URLs and all master bytes preserved',files=records,allMediaRetained=True))
  shutil.rmtree(backup)
  records[-1]['status']='hash-verified-local-review-junction';save(manifest,dict(scope='Only three internally passed local review folders; same C URLs and all master bytes preserved',files=records,allMediaRetained=True))
 print('Three verified review folders balanced onto D; C URLs and all media hashes unchanged')
if __name__=='__main__':main()
