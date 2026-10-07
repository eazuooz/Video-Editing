"""Verify the collected four-file correction without claiming private upload or Git."""
from pathlib import Path
import json, hashlib, subprocess, sys, datetime
ROOT = Path(__file__).resolve().parents[3]
slug = sys.argv[1]
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
folder = ROOT / 'projects' / slug / 'production/visual-depth-v1'
review = read(folder / 'encoded-pixel-direct-review.json')
delivery_path = ROOT / 'projects' / slug / 'production/delivery-output.json'
delivery = read(delivery_path)
if not review['allFinalPixelsReviewed'] or len(delivery['files']) != 4:
    raise RuntimeError('Approved final pixels and actual four-file delivery required')
for f in delivery['files']:
    if sha(ROOT / delivery['directory'] / f['name']) != f['sha256']:
        raise RuntimeError('Collected file identity changed')
caption = next(f for f in delivery['files'] if '.captioned.mp4' in f['name'])
if caption['sha256'] != review['videoSha256']:
    raise RuntimeError('Collected captioned video is not the directly reviewed version')
checks = []
for args in [['node', 'scripts/media-policy.cjs'], ['node', 'scripts/build-rebuild-manifests.cjs', slug, '--check']]:
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', creationflags=0x08000000)
    checks.append(dict(command=args, exitCode=r.returncode, output=r.stdout, error=r.stderr))
    if r.returncode: raise RuntimeError('Scoped delivery check failed: ' + str(args))
target = folder / 'local-collection-verification.json'
if target.exists(): raise RuntimeError('Preserve existing collection evidence')
record = dict(slug=slug, checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    files=delivery['files'], captionedSha256=caption['sha256'], checks=checks,
    collected=True, renderApproved=True, allPixelsReviewed=True, uploaded=False,
    gitDelivered=False, uploadBlock='production/batches/visual-depth-revision/private-reupload-block.json',
    gitBlock='Session .git permission is read-only; no index/commit/push bypass attempted',
    humanFullListening='pending', finalPublicRights='pending')
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
qpath = ROOT / 'production/batches/visual-depth-revision/queue.json'
original = qpath.read_bytes(); q = json.loads(original.decode('utf-8-sig'))
item = next(i for i in q['items'] if i['slug'] == slug)
item.update(stage='reviewed-collected-private-reupload-blocked', collected=True,
    renderApproved=True, allPixelsReviewed=True, uploaded=False, gitDelivered=False,
    pid=None, activePid=None, pipelinePid=None,
    collectionReport=delivery_path.relative_to(ROOT).as_posix(),
    localCollectionVerification=target.relative_to(ROOT).as_posix(), uploadBlock=record['uploadBlock'])
q['updatedAt'] = record['checkedAt']
if qpath.read_bytes() != original: raise RuntimeError('Concurrent queue update: re-read before writing')
qpath.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(slug + ': exact four files collected, scoped checks passed; private upload/Git blocked')
