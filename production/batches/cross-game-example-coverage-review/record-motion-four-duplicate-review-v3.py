from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
old={x['path']:x['sha256'] for x in read(R/'duplicate-before-refresh-v3.json')['inputFiles']}
changes=[x for x in report['inputFiles'] if old.get(x['path'])!=x['sha256']]
assert {x['path'] for x in changes}=={f'projects/game-math-polygon-{n}-v2/project.json' for n in ['centers','partition']}
for x in report['inputFiles']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
dom=R/'current-studio-list-v3.dom.txt';text=dom.read_text('utf-8')
assert all(x in text for x in ['27개 중 1~27','/video/L7SXFwn4i2k/edit','/video/mBDd9VzSTkA/edit','2026. 10. 12.','2026. 11. 2.'])
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),inputsDigest=report['inputsDigest'],
    changedInputs=changes,bothChangedFullManifestsDirectlyRead=True,
    previousWholeKoEnReview='duplicate-content-and-studio-direct-review-v2.json',changedKoEnBodies=0,
    currentStudioEvidence=dict(path=str(dom.relative_to(ROOT)),sha256=sha(dom),tabId='34',
        relevantPolygonAndMotionRowsDirectlyRead=True,all27FullMetadataClaimedRead=False),
    findings=['The two changed complete manifests retain the same polygon centers/boundary/convexity and partition/fan/ears/empty-region contracts and viewer questions.',
        'Foreign status is now cross-game-additions-rendered-final-review-in-progress with explicit resumed userPause history; private upload/final pixels remain pending.',
        'Current Studio still shows the original combined polygon L7SXFwn4i2k on November2 and motion mBDd9VzSTkA on October12. No polygon replacement is inferred from local plans.',
        'Purpose-dependent geometric centers, valid boundaries and triangulation remain distinct from camera/tool/locomotion roles and reversible individual options.'],
    verdict='distinct',foreignFileOrPublishingMutations=0,finalFourGameCoverageApproved=False)
out=R/'duplicate-content-and-studio-direct-review-v3.json';assert not out.exists();out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason='Both changed polygon manifests read in full; unchanged complete KOEN texts retain prior direct review. Centers/boundaries/partition claims remain distinct from camera/tool/locomotion options. Current Studio polygon and motion scheduled rows directly re-read. See duplicate-content-and-studio-direct-review-v3.json.'
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--decision','distinct','--reason',reason,'--studio-evidence',str(out.relative_to(ROOT))],cwd=ROOT,check=True)
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
