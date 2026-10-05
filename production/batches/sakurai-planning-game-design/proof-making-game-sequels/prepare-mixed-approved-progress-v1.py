"""Capture the observed mixed-ASR decision and live render session, not video completion."""
from pathlib import Path
from datetime import datetime, timezone
import json, os, time

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
BASE = ROOT / 'projects/making-game-sequels/production'
W = BASE / 'final-v1'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
stamp = datetime.now(timezone.utc).isoformat()

def write(path, data):
    temporary = path.with_name(path.name + f'.{os.getpid()}.writing')
    for attempt in range(120):
        try:
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(temporary, path)
            return
        except OSError:
            if attempt == 119:
                raise
            time.sleep(.25)

review = read(W / 'full-mix-asr-review.json')
state = read(W / 'review-pair-execution.json')
session = read(W / 'review-pair-session.json')
assert review['technicallyApproved'] and review['all26WindowsDirectlyCompared']
assert state['pid'] == session['pid'] == 41148 and session['sessionId'] == 15295
queue_path = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
queue = read(queue_path)
item = next(row for row in queue['items'] if row['slug'] == 'making-game-sequels')
item['execution']['sessionId'] = session['sessionId']
item['execution']['launchEvidence'] = rel(W / 'review-pair-session.json')
item['preparedReviewPairProducer']['executed'] = True
item['preparedPublishingText'] = dict(path='projects/making-game-sequels/publishing/metadata-prepared.json',
    chapters=14, uploaded=False, videoId=None, actualSettingsVerified=False)
item['currentDistinctReview'] = dict(path=rel(PROOF / 'current-math-script-rereview-v2.json'),
    existingProjects=35, fullChangedScripts=4, distinctPassed=True, foreignFilesModified=False)
item['updatedAt'] = stamp
queue['updatedAt'] = stamp
write(queue_path, queue)
for path in [BASE / 'latest-checkpoint.json', PROOF / 'latest-checkpoint.json']:
    data = read(path)
    for key in ['updatedAt', 'execution', 'preparedReviewPairProducer', 'preparedPublishingText', 'currentDistinctReview']:
        data[key] = item[key]
    write(path, data)

label = 'mixed-approved-render-progress'
checks = PROOF / (label + '-pre-delivery-checks.json')
write(checks, dict(status='placeholder-replaced-by-actual-index-checks-before-commit'))
selected = [
    'production/batches/sakurai-planning-game-design/preflight/making-game-sequels.json',
    'production/batches/sakurai-planning-game-design/queue.json',
    rel(PROOF / 'content-review.json'), rel(PROOF / 'latest-checkpoint.json'),
    rel(PROOF / 'current-math-script-rereview-v2.json'),
    rel(PROOF / 'refresh-current-math-script-review-v2.cjs'),
    rel(PROOF / 'mixed-asr-handoff-git-verification.json'),
    rel(PROOF / 'mixed-asr-prepared-automation-readback.json'),
    rel(Path(__file__).resolve()), rel(checks),
    'projects/making-game-sequels/rebuild.json', rel(BASE / 'latest-checkpoint.json'),
    rel(BASE / 'render-reviewed-pair-v1.py'), rel(BASE / 'extract-encoded-caption-qa-v1.py'),
    rel(BASE / 'record-final-mixed-asr-review-v1.py'), rel(BASE / 'record-mixed-direct-progress-v1.py'),
    rel(BASE / 'prepare-publishing-text-v1.py'),
    rel(W / 'mixed-asr-direct-progress.json'), rel(W / 'mixed-asr-execution.json'),
    rel(W / 'full-mix-asr-review.json'), rel(W / 'encoded-caption-qa-request.json'),
    rel(W / 'review-pair-execution.json'), rel(W / 'review-pair-session.json')
]
selected += [rel(path) for path in sorted((W / 'mixed-asr-v1').glob('*.json'))]
selected += ['projects/making-game-sequels/publishing/' + name for name in
    ['description.ko.txt', 'description.en.txt', 'youtube.ko.md', 'youtube.en.md', 'pinned-comment.ko.txt', 'metadata-prepared.json']]
paths_file = PROOF / (label + '-paths.json')
selected += [rel(paths_file)]
assert len(set(selected)) == len(selected)
write(paths_file, selected)
print(json.dumps(dict(selected=len(selected), mixedWindows=26, technicalMixedApproved=True,
    renderStarted=True, worker=41148, session=15295, finalPixelsApproved=False, privateUploaded=False, newImages=0)))
