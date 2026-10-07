"""Append only board ranges that have actually been visually read in this session."""
from pathlib import Path
import datetime, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[3]
slug, first, last = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
observations = sys.argv[4:]
folder = ROOT / 'projects' / slug / 'production/visual-depth-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
index_path = folder / 'encoded-pixels-local/index.json'
index = read(index_path)
if not observations or not 1 <= first <= last <= len(index['boards']):
    raise RuntimeError('Actual direct review range and observations required')
target = folder / 'encoded-pixel-direct-progress.json'
data = read(target) if target.exists() else dict(slug=slug, indexSha256=sha(index_path), videoSha256=index['videoSha256'], ranges=[], allFinalPixelsReviewed=False)
if data['indexSha256'] != sha(index_path) or data['videoSha256'] != index['videoSha256']:
    raise RuntimeError('Review identity changed; preserve history before new review')
seen = {i for r in data['ranges'] for i in range(r['firstBoard'], r['lastBoard'] + 1)}
if seen.intersection(range(first, last + 1)):
    raise RuntimeError('Do not duplicate already recorded direct reads')
boards = index['boards'][first - 1:last]
for board in boards:
    if sha(ROOT / board['path']) != board['sha256']:
        raise RuntimeError('Directly read board changed')
data['ranges'].append(dict(firstBoard=first,lastBoard=last,checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),boardHashes=[b['sha256'] for b in boards],observations=observations))
seen.update(range(first,last+1))
data.update(boardsRead=len(seen),boardsTotal=len(index['boards']),allIndexedBoardsDirectlyRead=len(seen)==len(index['boards']),allFinalPixelsReviewed=False)
target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(slug=slug,boardsRead=len(seen),boardsTotal=len(index['boards']),allFinalPixelsReviewed=False)))
