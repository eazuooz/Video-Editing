"""Record only explicitly named boards after the operator has read their pixels."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os

ROOT = Path(__file__).resolve().parents[3]
W = Path(__file__).resolve().parent / 'final-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--boards', required=True)
parser.add_argument('--observation', required=True)
args = parser.parse_args()
indices = sorted(set(int(x) for x in args.boards.split(',')))
assert indices and all(1 <= x <= 302 for x in indices)
assert len(args.observation) >= 20
execution = read(W / 'encoded-caption-qa-execution.json')
assert execution['exitCode'] == 0 and execution['allActualPtsMatched']
target = W / 'encoded-caption-qa-direct-progress.json'
now = datetime.now(timezone.utc).isoformat()
progress = read(target) if target.exists() else dict(
    schemaVersion=1, slug='similar-game-design', sourceSha256=execution['sourceSha256'],
    directlyReadBoards=[], reviewedBoards=[], reviewedSampleIndices=[], observations=[],
    unresolvedPixelDefects=[], allFinalPixelsReviewed=False, qaApproved=False,
    collected=False, uploaded=False, newGitImages=0, imagesLocalOnly=True)
assert progress['sourceSha256'] == execution['sourceSha256']
assert not set(indices).intersection(progress['directlyReadBoards']), 'Do not repeat sealed board records.'
for index in indices:
    board = next(row for row in execution['boards'] if row['index'] == index)
    assert sha(ROOT / board['path']) == board['sha256']
    reviewed = dict(board)
    reviewed.update(directlyRead=True, reviewedAt=now)
    progress['reviewedBoards'].append(reviewed)
    progress['reviewedSampleIndices'] += board['sampleIndices']
progress['directlyReadBoards'] = sorted(progress['directlyReadBoards'] + indices)
progress['reviewedSampleIndices'] = sorted(set(progress['reviewedSampleIndices']))
progress['observations'].append(dict(boards=indices, reviewedAt=now, observation=args.observation))
progress.update(reviewedAt=now, status=f"{len(progress['directlyReadBoards'])}-of-302-final-boards-directly-read")
temp = target.with_name(target.name + f'.{os.getpid()}.writing')
temp.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n', 'utf-8')
os.replace(temp, target)
print(json.dumps(dict(directBoards=len(progress['directlyReadBoards']), samples=len(progress['reviewedSampleIndices']), allFinalPixels=False)))
