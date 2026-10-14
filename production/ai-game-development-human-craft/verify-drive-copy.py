"""Preserve prior encoding/evidence, then verify the new same-content delivery."""
from pathlib import Path
import json,subprocess,shutil,hashlib,concurrent.futures
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
O=ROOT/'shared/output'/SLUG;P=ROOT/'production'/SLUG
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,r):p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=read(O/'drive-optimization.json');new=ROOT/r['target'];old=ROOT/r['source']
assert r['status'].startswith('encoded') and new.stat().st_size<536870912
assert sha(new)==r['sha256'] and sha(old)==r['sourceSha256']
backup=O/'before-drive-optimization-v4';assert not backup.exists();backup.mkdir()
def move(a,b):
    assert ROOT.resolve() in a.resolve().parents and ROOT.resolve() in b.resolve().parents
    assert not b.exists();shutil.move(a,b)
move(old,backup/old.name)
for name in ['encoded-integrity.json','encoded-motion-review','caption-pixel-qa','motion-evidence-comparison.json']:
    move(O/name,backup/name)
# The clean control is unchanged and retains its original hash/input stamp.
(O/'caption-pixel-qa').mkdir()
move(backup/'caption-pixel-qa/videoClean',O/'caption-pixel-qa/videoClean')
move(new,old);r.update(preservedSource=(backup/old.name).relative_to(ROOT).as_posix(),target=old.relative_to(ROOT).as_posix())
write(O/'drive-optimization.json',r)
def job(name):
    runtime=str(ROOT/'qwen3-tts/.venv/Scripts/python.exe') if name=='inspect-audio' else 'python'
    with (O/(name+'.drive-copy.log')).open('wb') as log:
        subprocess.run([runtime,'-X','utf8',str(P/(name+'.py'))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    return name
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    futures=[pool.submit(job,n) for n in ['check-delivery','check-caption-pixels','check-drive-compression']]
    for f in concurrent.futures.as_completed(futures):print(f.result(),flush=True)
job('inspect-audio')
print('New technical checks complete; direct compression-quality inspection still required.',flush=True)
