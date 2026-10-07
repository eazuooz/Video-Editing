"""Record a direct full-resolution reinspection; preserve the mistaken board finding."""
from pathlib import Path
import json, hashlib, datetime
ROOT = Path(__file__).resolve().parents[3]
folder = ROOT / 'projects/motion-sickness-games/production/visual-depth-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
index = read(folder / 'encoded-pixels-local/index.json')
progress = read(folder / 'encoded-pixel-direct-progress.json')
target = folder / 'resolved-current-pixel-findings.json'
if target.exists():
    raise RuntimeError('Preserve existing resolution; inspect instead of repeating')
if index['videoSha256'] != progress['videoSha256'] or progress['boardsRead'] != 104:
    raise RuntimeError('Exact complete direct-read record required')
names = ['frame-00600.png', 'frame-00603.png', 'frame-00616.png', 'frame-00618.png']
samples = []
for name in names:
    f = next(f for b in index['boards'] for f in b['frames'] if f['file'].endswith('/' + name))
    if sha(ROOT / f['file']) != f['sha256']:
        raise RuntimeError('Directly inspected original frame changed')
    samples.append(f)
result = dict(
    slug='motion-sickness-games', checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    videoSha256=index['videoSha256'], indexSha256=sha(folder / 'encoded-pixels-local/index.json'),
    status='resolved-by-full-resolution-direct-reinspection', allRecordedRejectionsResolved=True,
    originalFindingRange=[93, 104], originalFindingPreserved=True,
    correction='The reduced contact-board display was misread. Original 1920x1080 final encoded pixels show separate fixed footer text at x510/x960/x1430, y855. The three labels and the bottom narration box do not touch or overlap. Text is fixed in screen space, not projected with diagram yaw.',
    directlyReadOriginalFrames=samples,
    observations=[
        'Frame36136: footer fades in above cue162 without text/caption overlap.',
        'Frame36264: all three footer labels fully visible and separate above cue162.',
        'Frame37167: all three footer labels clear above the longest two-line final cue166.',
        'Frame37384: final white frame has separate labels, no caption and no overlap.'
    ],
    sourceEditsMadeForMistakenFinding=0, rerendersMadeForMistakenFinding=0,
    humanFullListening='pending', privateUploadCompleted=False)
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
progress['findingResolution'] = str(target.relative_to(ROOT)).replace('\\', '/')
progress['allRecordedRejectionsResolved'] = True
(folder / 'encoded-pixel-direct-progress.json').write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('Motion footer finding resolved by already-read original pixels; history retained, no rerender')
