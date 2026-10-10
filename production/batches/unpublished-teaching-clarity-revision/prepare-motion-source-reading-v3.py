"""Add one unused opening candidate while preserving every previous preview."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re

root = Path(__file__).resolve().parents[3]
batch = root / 'production/batches/unpublished-teaching-clarity-revision'
raw = root / 'shared/assets/presenting-game-scores/raw'
prepared = json.loads((batch / 'motion-native-reading-preparation-v1.json').read_text('utf-8'))
target = batch / 'motion-source-reading-preparation-v3.json'
assert not target.exists(), 'Inspect the existing follow-up instead of recreating it'
for source in prepared['sources']:
    assert os.path.samefile(root / source['source'], root / source['sameFileLink'])
    assert (root / source['source']).stat().st_size == source['bytes']
old = raw / 'motion-source-native-reading-v2.html'
new = raw / 'motion-source-native-reading-v3.html'
assert not new.exists()
html = old.read_text('utf-8')
match = re.search(r'const windows=(.*?);\nconst video=', html)
assert match
windows = json.loads(match.group(1))
windows[0]['label'] = 'Task context already used in baseline: comparison only'
windows[1]['label'] = 'Aim context partly overlaps baseline: comparison only'
extra = [{'label': 'Unused opening candidate: task transition after roundabout',
          'sourceId': 'PF5L_2g9UVQ', 'inSeconds': 224.116667, 'outSeconds': 247.5},
         {'label': 'Unused opening candidate: tower surface cleaning',
          'sourceId': 'PF5L_2g9UVQ', 'inSeconds': 276.883334, 'outSeconds': 289}]
html, count = re.subn(r'const windows=.*?;\nconst video=',
                     'const windows=' + json.dumps(extra + windows, ensure_ascii=False) + ';\nconst video=',
                     html, count=1)
assert count == 1
new.write_text(html, encoding='utf-8')
record = {'schemaVersion': 3, 'preparedAt': datetime.now(timezone.utc).isoformat(),
          'existingServerPort': 9250, 'historicalPage': str(old.relative_to(root)).replace('\\', '/'),
          'historicalPageSha256': hashlib.sha256(old.read_bytes()).hexdigest(),
          'newPage': str(new.relative_to(root)).replace('\\', '/'),
          'newPageSha256': hashlib.sha256(new.read_bytes()).hexdigest(),
          'additionalCandidates': extra,
          'historicalCorrection': '169–187 seconds lies inside baseline cut004; 69–99 overlaps cuts002/003. Neither is wholly unused footage.',
          'url': 'http://127.0.0.1:9250/motion-source-native-reading-v3.html',
          'sourceFilesReacquired': 0, 'newMediaCopied': 0, 'encodeOrDecodeJobs': 0,
          'newServerStarted': False, 'sourceAdoptionApproved': False,
          'nativeExactCutsApproved': False, 'allContinuousNativeFramesReviewed': False,
          'baselineModified': False}
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'additionalCandidates': len(extra), 'previousPreviewPreserved': True,
                  'newMediaJobs': 0, 'adoption': False}))
