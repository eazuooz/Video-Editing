from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
report=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
assert report['inputsDigest']=='95b12cc70917c13cd1fb1944d1da1b1b1dc2eff04bd418e03c20dc8f8a4ec4e0'
prior=read(R/'duplicate-history-current78-v9.json');old={v['path']:v['sha256'] for v in prior['inputFiles']}
changed=[v for v in report['inputFiles'] if old.get(v['path'])!=v['sha256']]
assert len(changed)==2
for v in changed:
 assert hashlib.sha256((ROOT/v['path']).read_bytes()).hexdigest()==v['sha256'];v['fullCurrentBodyDirectlyRead']=True
studio=read(R/'neighbor-current-studio-v10.json');assert studio['readOnly'] and studio['platformMutations']==0
reason='The two changed full manifests were directly read. Plane-distances measures signed residuals, nearest points, normals and Newell boundaries; triangle-addresses checks finite triangle inclusion and defined affine attributes. Their preserved baseline ID wsxSYEEj8aQ and new-episode private/settings flags remain incomplete, with no new actual upload ID or changed receipt. Updated measured 40:60 episode timings and causal-flow preparation do not change the full KO/EN mathematical claims previously read. Motion sickness addresses camera comfort, target following, view/aim roles, orientation cues and reversible settings. The current bounds Studio title/full description/private/SDHD and disabled Save were reread with no mutation. Retain prior full source/content/Studio review; shared Portal footage and colored geometry do not duplicate the viewer question or worked concept.'
o=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),inputsDigest=report['inputsDigest'],projectCount=len(report['existingProjects']),inputCount=len(report['inputFiles']),previousReportPreserved='duplicate-history-current78-v9.json',priorFullContentReviewRetained='inventory-change-direct-review-v9.json',changedFiles=changed,comparison=reason,currentStudioEvidence='neighbor-current-studio-v10.json',foreignFilesModified=0,foreignPublishingModified=0,decisionExitCode=None,checkExitCode=None)
p=R/'inventory-change-direct-review-v10.json';assert not p.exists();p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
c=subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--decision','distinct','--reason',reason,'--studio-evidence',p.relative_to(ROOT).as_posix()],cwd=ROOT);o['decisionExitCode']=c.returncode;assert c.returncode==0
assert read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')['inputsDigest']==o['inputsDigest']
c=subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT);o['checkExitCode']=c.returncode;p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');assert c.returncode==0
cp=read(R/'latest-checkpoint.json');cp.update(currentDuplicateReview=p.relative_to(ROOT).as_posix(),currentDuplicateCheckExitCode=0);(R/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
