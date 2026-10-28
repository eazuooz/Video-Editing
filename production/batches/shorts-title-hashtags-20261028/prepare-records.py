from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

task = Path(__file__).resolve().parent
batch = Path('D:/Github/VideoEditing/production/batches/shorts-title-hashtags-20261028')
load = lambda name: json.loads((task / name).read_text(encoding='utf-8-sig'))
plan, receipts, after = load('plan.json'), load('platform-receipts.json'), load('studio-after.json')
assert len(receipts) == len(plan['items']) == 14
assert after['allFourteenTitlesMatch'] and after['allFourteenVisibilityAndDatesPreserved']
summary = {
    'status': 'fourteen-title-hashtag-suffixes-saved-and-reopened',
    'completedAt': datetime.now(timezone.utc).isoformat(),
    'request': plan['request'],
    'scope': 'Same fourteen Shorts selected in the immediately preceding title and thumbnail task.',
    'commonHashtag': '#게임개발', 'hashtagCountPerTitle': 3,
    'format': 'Preserved base title + #게임개발 + relevant game + relevant technique',
    'maximumTitleLength': max(len(x['title']) for x in receipts),
    'scheduledDatesAndTimesUnchanged': 13,
    'privateRightsHoldUnchanged': 'QlIwFupj9Dk',
    'thumbnailFilesUnchanged': 14,
    'descriptionEnglishMetadataVideoAndHumanReviewUnchanged': True,
    'newUploadOrPublicationPerformed': False,
    'performanceImprovementClaimed': False,
    'officialGuidance': 'https://support.google.com/youtube/answer/6390658?hl=ko',
    'verification': 'Exact title readback after page reload and final Studio list; each date/time/zone or private state re-opened.',
    'proof': str(task / 'studio-overview-hashtags.png'),
    'proofSHA256': hashlib.sha256((task / 'studio-overview-hashtags.png').read_bytes()).hexdigest(),
    'items': [{'videoId': x['videoId'], 'title': x['title'], 'hashtags': x['hashtags']} for x in receipts],
}
(task / 'completion.json').write_bytes((json.dumps(summary, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
batch.mkdir(parents=True, exist_ok=True)
names = ['plan.json', 'completion.json', 'platform-receipts.json', 'studio-before.json', 'studio-after.json',
         'assets-audit.json', 'schedule-plan.json', 'build-plan.py', 'merge-title-hashtag-records.py',
         'commit-own-publishing-records.py', 'prepare-records.py']
for name in names:
    source, dest = task / name, batch / name
    assert source.is_file() and not dest.exists()
    data = source.read_bytes().replace(b'\r\n', b'\n')
    assert len(data) < 2_000_000
    data.decode('utf-8-sig')
    dest.write_bytes(data)
print(json.dumps({'textRecords': len(names), 'batch': str(batch)}))
