"""Compare a fresh continuing-cleaning interval rather than padding with repositioning."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

root = Path(__file__).resolve().parents[3]
raw = root / 'shared/assets/presenting-game-scores/raw'
batch = Path(__file__).resolve().parent
old = raw / 'motion-source-native-reading-v3.html'
new = raw / 'motion-source-native-reading-v4.html'
record = batch / 'motion-continuing-cleaning-preparation-v4.json'
assert not new.exists() and not record.exists()
html = old.read_text('utf-8')
match = re.search(r'const windows=(.*?);\nconst video=', html)
windows = json.loads(match.group(1))
windows[1]['label'] = 'Tower approach then floor cleaning: not all seconds show spraying'
extra = {'label': 'Unused continuing cleaning after baseline', 'sourceId': 'PF5L_2g9UVQ', 'inSeconds': 552.4, 'outSeconds': 585}
html, count = re.subn(r'const windows=.*?;\nconst video=', 'const windows=' + json.dumps([extra] + windows, ensure_ascii=False) + ';\nconst video=', html, count=1)
assert count == 1
new.write_text(html, encoding='utf-8')
data = {'schemaVersion': 4, 'preparedAt': datetime.now(timezone.utc).isoformat(), 'newCandidate': extra,
        'url': 'http://127.0.0.1:9250/motion-source-native-reading-v4.html',
        'oldPageSha256': hashlib.sha256(old.read_bytes()).hexdigest(),
        'newPageSha256': hashlib.sha256(new.read_bytes()).hexdigest(),
        'reason': 'Native45 samples show that most276.9–285.8 is repositioning rather than dirt removal. Compare a longer unused cleaning action before assigning the overview actual time.',
        'sourceAdoptionApproved': False, 'newMediaOrServer': False, 'baselineModified': False}
record.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Prepared one additional clarity comparison; historical pages and all media preserved.')
