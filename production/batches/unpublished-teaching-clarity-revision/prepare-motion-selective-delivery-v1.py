"""Prepare explicit current motion paths only after real private/settings review."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
B = 'production/batches/unpublished-teaching-clarity-revision'
P = 'projects/motion-sickness-games'
R = P + '/production/revision-teaching-clarity-v1'
read = lambda p: json.loads((ROOT / p).read_text('utf-8-sig'))
receipt = read(R + '/publishing/youtube-upload-v1.json')
assert receipt['actualVideoId'] and receipt['uploaded'] and receipt['privateSaveVerified']
assert receipt['fullSettingsVerified'] and receipt['automaticChecksPassed'] and receipt['burnedCaptionPixelsVerified']
review = read(R + '/publishing/private-settings-direct-review-v1.json')
images = review['minimalReviewedImages']
allowed = {'.json', '.md', '.py', '.cjs', '.ts', '.tsx', '.meta', '.srt', '.ass', '.csv', '.html'}
def text(p):
    return p.suffix in allowed or p.name in {'upload-description.ko.txt', 'upload-description.en.txt', 'pinned-comment.ko.txt'}
def eligible(p):
    return p.is_file() and not p.is_symlink() and text(p) and not p.name.endswith(('.ax.txt', '.info.json')) and not any(x in {'__pycache__', 'raw', 'assets', 'frames', 'boards', 'node_modules', '.git', 'delivery-history'} for x in p.parts)
excluded = {R + '/publishing/private-delivery-git-verification-v1.json', R + '/publishing/schedule-evidence-git-verification-v1.json', R + '/publishing/final-handoff-git-verification-v1.json'}
files = {p.relative_to(ROOT).as_posix() for p in (ROOT / R).rglob('*') if eligible(p)}
files |= {p.relative_to(ROOT).as_posix() for p in (ROOT / B).iterdir() if eligible(p) and ('motion' in p.name or p.name in {'queue.json', 'README.md'})}
mc = ROOT / 'motion-canvas/src/projects/motion-sickness-games/teaching-clarity-v1'
files |= {p.relative_to(ROOT).as_posix() for p in mc.rglob('*') if eligible(p)}
files |= {P + '/' + n for n in ['project.json', 'planning/outline.md', 'production/qa.json', 'production/delivery-output.json', 'rebuild.json']}
files |= {'motion-canvas/vite.motion-sickness-games.config.ts', 'motion-canvas/tsconfig.motion-sickness-games.json', 'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'}
files -= excluded
dest = R + '/publishing/git-source-selection-v1.json'
files |= {dest, R + '/publishing/git-stage-paths-v1.json'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for image in images:
    assert image['path'].startswith(R + '/publishing/') and image['purpose'] == 'minimal-publishing-proof'
    assert image['reviewedAt'] and image['reason'] and sha(ROOT / image['path']) == image['sha256']
    files.add(image['path'])
assert not (ROOT / dest).exists()
selection = dict(schemaVersion=1, preparedAt=datetime.now(timezone.utc).isoformat(), slug='motion-sickness-games',
    actualVideoId=receipt['actualVideoId'], selectedPaths=sorted(files), reviewedEssentialImages=images,
    sharedOwnedOnlyPaths=['shared/git-essential-images.json', '.gitignore'],
    sourceHashesAtPreparation={p: sha(ROOT / p) for p in sorted(files) if (ROOT / p).exists()},
    historicalBaselinePublishingFilesSelected=False, mediaAdded=0, rasterAutomaticallySelected=False,
    staged=False, committed=False, externalIndexPolicy='Temporary index from actual HEAD; preserve all external index bytes and entries.')
(ROOT / dest).write_text(json.dumps(selection, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps(dict(preparedSelection=True, explicitPaths=len(files), essentialImages=len(images), staged=False)))
