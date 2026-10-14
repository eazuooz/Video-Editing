"""Keep the failed stale gate and refresh its inventory exactly once."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
V = ROOT / 'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
REPORT = ROOT / 'production/batches/sakurai-planning-game-design/preflight/hierarchical-game-outlines.json'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
save = lambda p, o: p.write_text(json.dumps(o, ensure_ascii=False, indent=2) + '\n', 'utf-8')
now = datetime.now(timezone.utc).isoformat()
snapshot = V / 'duplicate-inventory-before-refresh-v1.json'
assert not snapshot.exists(), 'Do not refresh again; continue the pending inventory'
snapshot.write_bytes(REPORT.read_bytes())
save(V / 'duplicate-stale-check-failure-v1.json', dict(recordedAt=now,
    actualShellChunk='255ae8', actualExitCode=1,
    actualError='Existing project evidence changed: refresh duplicate review before creation.',
    oldReportSha256=sha(snapshot), dependentCreationAllowed=False, mediaOrModelStarted=False))
result = subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', 'hierarchical-game-outlines'],
    cwd=ROOT, text=True, capture_output=True, check=False)
(V / 'duplicate-refresh-v1.log.txt').write_text(result.stdout + result.stderr, 'utf-8')
assert result.returncode == 0, result.stderr
current = read(REPORT)
old = read(snapshot)
orientation_path = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1/duplicate-inventory-before-decision-v1.json'
orientation = read(orientation_path)
old_map = {x['path']: x['sha256'] for x in old['inputFiles']}
latest_map = {x['path']: x['sha256'] for x in orientation['inputFiles']}
new_map = {x['path']: x['sha256'] for x in current['inputFiles']}
since_old = [x for x in current['inputFiles'] if old_map.get(x['path']) != x['sha256']]
since_orientation = [x for x in current['inputFiles'] if latest_map.get(x['path']) != x['sha256']]
removed = [p for p in latest_map if p not in new_map and not p.startswith('projects/hierarchical-game-outlines/')]
pending = dict(schemaVersion=1, recordedAt=now, actualRefreshExitCode=result.returncode,
    currentReportPath=REPORT.relative_to(ROOT).as_posix(), currentReportSha256=sha(REPORT),
    currentDigest=current['inputsDigest'], projectCount=len(current['existingProjects']),
    inputCount=len(current['inputFiles']), exactMatches=current['exactMatches'],
    previousWholeReview='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/duplicate-content-and-studio-direct-review-v1.json',
    previousInventoryPath=orientation_path.relative_to(ROOT).as_posix(), previousInventorySha256=sha(orientation_path),
    changesSinceHistoricalHierarchyReview=since_old, changesSinceLatestOrientationInventory=since_orientation,
    removedSinceLatestOrientationInventory=removed,
    unchangedLatestInputCount=len(current['inputFiles'])-len(since_orientation),
    allNewContentsReviewed=False, currentStudioComparisonApproved=False, currentCheckPassed=False)
save(V / 'duplicate-refresh-pending-v1.json', pending)
print(json.dumps(dict(refreshExitCode=0, projects=pending['projectCount'], inputs=pending['inputCount'],
    unchangedLatest=pending['unchangedLatestInputCount'], exactMatches=[x['slug'] for x in current['exactMatches']],
    latestChanges=since_orientation, removed=removed), ensure_ascii=False))
