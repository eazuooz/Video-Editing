"""Preserve the first preview and add focused context candidates, without media jobs."""
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
target = batch / 'motion-focused-source-reading-preparation-v2.json'
assert not target.exists(), 'Preserve completed preparation and inspect its actual follow-up'
for source in prepared['sources']:
    assert os.path.samefile(root / source['source'], root / source['sameFileLink'])
    assert (root / source['source']).stat().st_size == source['bytes']
extra = [
    {'label': 'Additional task context: unused before roundabout', 'sourceId': 'PF5L_2g9UVQ', 'inSeconds': 169, 'outSeconds': 187},
    {'label': 'Additional aim context: unused interval', 'sourceId': 'PF5L_2g9UVQ', 'inSeconds': 69, 'outSeconds': 99},
    {'label': 'Talos: upward view at puzzle device', 'sourceId': '6slinvkF0Rs', 'inSeconds': 36.1, 'outSeconds': 39.7},
    {'label': 'Talos: tilted puzzle walls and laser', 'sourceId': '6slinvkF0Rs', 'inSeconds': 48, 'outSeconds': 51.9},
]
old = raw / 'motion-source-native-reading-v1.html'
new = raw / 'motion-source-native-reading-v2.html'
assert not new.exists()
html = old.read_text('utf-8')
html, count = re.subn(r'const windows=.*?;\nconst video=', 'const windows=' + json.dumps(extra + prepared['windows'], ensure_ascii=False) + ';\nconst video=', html, count=1)
assert count == 1
new.write_text(html, encoding='utf-8')
record = {'schemaVersion': 2, 'preparedAt': datetime.now(timezone.utc).isoformat(),
          'existingServerPort': 9250, 'oldPagePreservedSha256': hashlib.sha256(old.read_bytes()).hexdigest(),
          'newPageSha256': hashlib.sha256(new.read_bytes()).hexdigest(),
          'extraFocusedWindows': extra,
          'url': 'http://127.0.0.1:9250/motion-source-native-reading-v2.html',
          'sourceFilesReacquired': 0, 'newMediaCopied': 0, 'encodeOrDecodeJobs': 0,
          'newServer': False, 'sourceAdoptionApproved': False, 'newNarrationRendered': False,
          'nativeExactCutsApproved': False, 'allContinuousNativeFramesReviewed': False,
          'baselineModified': False}
target.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'focusedWindowsAdded': 4, 'oldPagePreserved': True, 'newMediaJobs': 0}))
