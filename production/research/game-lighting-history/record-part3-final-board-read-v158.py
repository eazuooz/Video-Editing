"""Append explicitly supplied human-readable observations after direct board viewing."""
from pathlib import Path
import argparse, hashlib, json
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'projects/game-lighting-history-04/production'
ap = argparse.ArgumentParser()
ap.add_argument('--from-board', type=int, required=True)
ap.add_argument('--to-board', type=int, required=True)
ap.add_argument('--note', required=True)
ap.add_argument('--issue', default='')
a = ap.parse_args()
execution = json.loads((P/'part3-final-pixel-review-execution-v151.json').read_text('utf-8-sig'))
assert execution['status'] == 'complete' and execution['exitCode'] == 0
out = P/'part3-final-board-direct-progress-v158.json'
x = json.loads(out.read_text('utf-8-sig')) if out.exists() else dict(
    status='direct-review-in-progress', source=execution['source'], sourceSha256=execution['sourceSha256'],
    pairBuildSha256=execution['pairBuildSha256'], records=[], allFinalPixelsReviewed=False,
    allMovingPixelsReviewed=False, qaApproved=False, humanWholeListening='pending', newGitImages=0)
assert x['sourceSha256'] == execution['sourceSha256']
assert 1 <= a.from_board <= a.to_board <= len(execution['boards'])
stamp = datetime.now(timezone.utc).isoformat()
for i in range(a.from_board, a.to_board+1):
    b = execution['boards'][i-1]
    assert not any(r['board'] == i for r in x['records']), f'already recorded {i}'
    assert hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest() == b['sha256']
    x['records'].append(dict(board=i, path=b['path'], sha256=b['sha256'], imageIndices=b['imageIndices'],
        directlyRead=True, actualObservation=a.note, issue=a.issue or None, reviewedAt=stamp,
        tool='view_image original 2880x1204 six-frame board'))
x['records'].sort(key=lambda r:r['board'])
x.update(updatedAt=stamp, directlyReadBoards=len(x['records']), plannedBoards=len(execution['boards']))
out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(readBoards=len(x['records']), totalBoards=len(execution['boards']), finalApproved=False)))
