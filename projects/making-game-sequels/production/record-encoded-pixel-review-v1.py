"""Record explicitly inspected encoded boards; never infer a visual review."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--sheets', required=True, help='Explicit comma-separated directly viewed sheet numbers.')
parser.add_argument('--observation', required=True)
parser.add_argument('--work-directory', choices=('final-v1', 'final-v2'), default='final-v1')
args = parser.parse_args()
FINAL = ROOT / 'projects/making-game-sequels/production' / args.work_directory
numbers = sorted(set(int(n) for n in args.sheets.split(',')))
execution = read(FINAL / 'encoded-caption-qa-local-v1/execution.json')
ledger_path = FINAL / 'encoded-pixel-direct-review.json'
ledger = read(ledger_path)
assert execution['exitCode'] == 0 and len(execution['sheets']) == 124
assert ledger['sourceSha256'] == execution['sourceSha256']
assert numbers and all(1 <= n <= 124 for n in numbers)
assert args.observation.strip()
reviewed = sorted(set(ledger['reviewedSheets']) | set(numbers))
records = []
for n in reviewed:
    sheet = execution['sheets'][n - 1]
    assert sha(ROOT / sheet['path']) == sheet['sha256'], sheet['path']
    images = []
    for index in sheet['imageIndices']:
        item = execution['images'][index - 1]
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
        images.append({k: item[k] for k in ('path', 'sha256', 'frame', 'segment', 'visibleCueIds')})
    records.append({'sheetNumber': n, 'path': sheet['path'], 'sha256': sheet['sha256'], 'images': images})
ledger['reviewedSheets'] = reviewed
ledger['reviewedSheetCount'] = len(reviewed)
ledger['reviewedImageCount'] = sum(len(r['images']) for r in records)
ledger['reviewedRecords'] = records
ledger['findings'].append({'sheets': numbers, 'observation': args.observation})
ledger['updatedAt'] = datetime.now(timezone.utc).isoformat()
ledger['allFinalPixelsApproved'] = False
ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'reviewedSheets': len(reviewed), 'reviewedImages': ledger['reviewedImageCount'], 'allFinalPixelsApproved': False}))
