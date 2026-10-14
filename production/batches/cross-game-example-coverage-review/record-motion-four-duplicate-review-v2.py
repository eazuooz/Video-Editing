"""Record the six changed polygon contents directly read and the refreshed Studio list."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json';report=read(p)
old={x['path']:x['sha256'] for x in read(R/'duplicate-before-refresh-v2.json')['inputFiles']}
changes=[x for x in report['inputFiles'] if old.get(x['path'])!=x['sha256']]
expected={f'projects/game-math-polygon-{n}-v2/{f}' for n in ['centers','partition'] for f in ['project.json','script/narration.ko.json','script/narration.en.json']}
assert {x['path'] for x in changes}==expected
for x in report['inputFiles']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
dom=R/'current-studio-list-v2.dom.txt';assert '27개 중 1~27' in dom.read_text('utf-8')
evidence=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),inputsDigest=report['inputsDigest'],changedInputs=changes,
    wholeChangedKoEnBodiesDirectlyRead=True,changedManifestContractsAndViewerQuestionsRead=True,
    allForeignTechnicalManifestFieldsClaimedRead=False,currentStudioScheduledListRead=True,currentStudioPath=str(dom.relative_to(ROOT)),currentStudioSha256=sha(dom),
    currentPolygonUpload='L7SXFwn4i2k',currentPolygonDate='2026-11-02',platformAndForeignFileChanges=0,
    findings=['Centers lecture selects averaging versus equal side/vertex distance, then validates boundary order and convexity.',
        'Partition lecture contrasts valid fans, ears, area sums, empty-region coverage, thin triangles and scale-aware tolerances. Shapez processing is explicitly distinguished from triangulation.',
        'These updated four-game comparisons teach geometry conditions and do not duplicate our separation of camera, tool and locomotion controls or understandable reversible options.',
        'Refreshed Studio still shows the original combined polygon lecture on November2 and motion on October12. A local planned split is not an actual new upload.'],verdict='distinct',finalFourGameCoverageApproved=False)
out=R/'duplicate-content-and-studio-direct-review-v2.json';assert not out.exists();out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n','utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason='Full changed polygon KOEN bodies and manifest contracts reviewed: geometric centers/boundaries/ears/coverage remain distinct from camera/tool/locomotion controls and individual reversible choices. Earlier full Studio metadata and new current27-row Studio list reviewed; preserve foreign plans/uploads. See duplicate-content-and-studio-direct-review-v2.json.'
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--decision','distinct','--reason',reason,'--studio-evidence',str(out.relative_to(ROOT))],cwd=ROOT,check=True)
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
