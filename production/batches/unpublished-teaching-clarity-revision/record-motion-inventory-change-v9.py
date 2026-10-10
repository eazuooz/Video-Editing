from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
report=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
assert report['inputsDigest']=='654a3d3bb7714a0f22431a9924e6e7e106e5bd4a92395b114b9011e74cf5bfbe'
prior=read(R/'duplicate-history-current77-v8.json')
old={v['path']:v['sha256'] for v in prior['inputFiles']}
changed=[v for v in report['inputFiles'] if old.get(v['path'])!=v['sha256']]
assert len(changed)==9
for v in changed:
    assert hashlib.sha256((ROOT/v['path']).read_bytes()).hexdigest()==v['sha256']
    v['fullCurrentBodyDirectlyRead']=True
proof=read(R/'neighbor-current-studio-v9.json')
assert proof['videoId']=='W5UkJkep7yo' and proof['readOnly'] and proof['platformMutations']==0
reason=('The full nine changed files were directly read. Bounds transform teaches spheres, AABBs, per-axis overlap, broad candidates versus contact and rotated center/half-size extents. Its full current KO/EN publishing receipt and saved current Studio title, complete25-chapter description, private badge, SD/HD complete and disabled Save were read. The entire plane-distance KO/EN scripts connect normals and plane constants to signed distance, closest points, three-point normals and ordered Newell boundaries. The complete new retakes manifest and KO/EN explain floor versus normal, nearest projection, finite passage versus plane membership, and surface position versus attributes; standalone upload is disabled. The complete triangle-address KO/EN connects lengths/area to signed barycentric weights, coplanarity versus projected inclusion, stability and defined affine attributes. Portal footage is illustrative with explicit limits. Motion sickness instead connects target following and reduced camera rotation, visual/body mismatch, separate aim/view roles, orientation cues and reversible comfort controls. Shared footage/colored geometry does not duplicate these viewer questions or worked claims. Prior full inventory/source/Studio comparisons are retained; foreign changes and settings remain untouched.')
o=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),inputsDigest=report['inputsDigest'],projectCount=len(report['existingProjects']),inputCount=len(report['inputFiles']),previousReportPreserved='duplicate-history-current77-v8.json',priorFullContentReviewRetained='inventory-change-direct-review-v8.json',changedFiles=changed,comparison=reason,currentStudioEvidence='neighbor-current-studio-v9.json',foreignFilesModified=0,foreignPublishingModified=0,decisionExitCode=None,checkExitCode=None)
p=R/'inventory-change-direct-review-v9.json';assert not p.exists()
p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
c=subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--decision','distinct','--reason',reason,'--studio-evidence',str(p.relative_to(ROOT)).replace('\\','/')],cwd=ROOT)
o['decisionExitCode']=c.returncode
assert c.returncode==0
assert read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')['inputsDigest']==o['inputsDigest']
c=subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT)
o['checkExitCode']=c.returncode
p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');assert c.returncode==0
cp=read(R/'latest-checkpoint.json');cp.update(currentDuplicateReview=str(p.relative_to(ROOT)).replace('\\','/'),currentDuplicateCheckExitCode=0)
(R/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
