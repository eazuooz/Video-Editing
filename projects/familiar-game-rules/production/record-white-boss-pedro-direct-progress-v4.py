"""Record explicitly viewed boards; this never approves motion or final pixels."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os

ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
SOURCE = PROOF / 'white-boss-pedro-input-v4.json'
DEST = PROOF / 'white-boss-pedro-input-direct-progress-v4.json'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = argparse.ArgumentParser()
p.add_argument('--first', type=int, required=True)
p.add_argument('--last', type=int, required=True)
p.add_argument('--notes', required=True)
a = p.parse_args()
e = read(SOURCE)
d = read(DEST) if DEST.exists() else dict(
    schemaVersion=1, slug='familiar-game-rules', evidence=SOURCE.relative_to(ROOT).as_posix(),
    evidenceSha256=sha(SOURCE), sourceCandidateSha256=e['sourceCandidateSha256'],
    captionCandidateSha256=e['captionCandidateSha256'], whiteInputSha256=e['whiteInputSha256'],
    groups=[], boards=[], allInputBoardsDirectlyRead=False,
    allSourceMotionReviewed=False, allFinalCaptionPixelsReviewed=False,
    finalTimelineAdopted=False, imagesGitPolicy='local-only', newGitImages=0,
    humanListeningPronunciation='pending')
assert d['evidenceSha256'] == sha(SOURCE)
chosen = [b for b in e['boards'] if a.first <= b['index'] <= a.last]
assert len(chosen) == a.last - a.first + 1
assert not {b['index'] for b in chosen} & {b['index'] for b in d['boards']}
now = datetime.now(timezone.utc).isoformat()
for b in chosen:
    assert sha(ROOT / b['path']) == b['sha256']
    d['boards'].append(dict(index=b['index'], path=b['path'], sha256=b['sha256'],
                           sampleIndices=b['sampleIndices'], directlyRead=True, reviewedAt=now))
d['groups'].append(dict(first=a.first, last=a.last, reviewedAt=now, notes=a.notes))
d['boards'].sort(key=lambda b: b['index'])
d['directlyReadBoards'] = len(d['boards'])
d['directlyReadSamples'] = len({n for b in d['boards'] for n in b['sampleIndices']})
d['allInputBoardsDirectlyRead'] = len(d['boards']) == e['boardCount']
d['updatedAt'] = now
d['scope'] = 'Directly viewed decoded white-input and native/PIL caption trials only. Normal-speed motion, final mix and encoded final pixels remain separate gates.'
t = DEST.with_name(DEST.name + f'.{os.getpid()}.writing')
t.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf-8')
os.replace(t, DEST)
print(json.dumps({k: d[k] for k in ['directlyReadBoards', 'directlyReadSamples', 'allInputBoardsDirectlyRead', 'allFinalCaptionPixelsReviewed']}))
