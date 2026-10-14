from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rp=ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'
report=read(rp);old={x['path']:x['sha256'] for x in read(R/'duplicate-before-refresh-v5.json')['inputFiles']}
changes=[x for x in report['inputFiles'] if old.get(x['path'])!=x['sha256']]
assert {x['path'] for x in changes}=={'projects/'+s+'/'+p for s in ['game-math-polygon-centers-v2','game-math-polygon-partition-v2'] for p in ['project.json','publishing/youtube-upload.json']}
for x in report['inputFiles']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),inputsDigest=report['inputsDigest'],changedInputs=changes,
    allFourChangedCompleteContentsDirectlyRead=True,unchangedKoEnBodiesPreserved=True,
    findings=['Centers: purposeful centroid/incenter/circumcenter, ordered land boundaries and convexity; partition: fan/ears, preserving region and empty space, validity before triangle quality. These are distinct from motion camera/aim/locomotion choices.',
    'Both foreign manifests now report local technical/pixel review, private publishing still pending. This duplicate review does not approve their final video.',
    'Centers receipt actual YgcN8vs0gNo has incomplete publishing; current Studio directly read full title/description/private/SDHD. Partition receipt pfagaQK-xfI is draft/uploading; current Studio full title/description and87% upload read. No foreign settings or draft controls changed.',
    'Future Studio still preserves combined polygon L7SXFwn4i2k November2 and motion mBDd9VzSTkA October12.'],
    currentStudioEvidence=[dict(path='projects/motion-sickness-games/production/revision-cross-game-four-v1/'+n,sha256=sha(R/n)) for n in ['current-studio-list-v5.dom.txt','current-centers-studio-v5.dom.txt','current-centers-studio-v5.text.json','current-partition-studio-v5.dom.txt','current-partition-studio-v5.text.json']],
    verdict='distinct',foreignFileOrPlatformMutations=0,finalCoverageApproval=False)
p=R/'duplicate-content-and-studio-direct-review-v5.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--decision','distinct','--reason','Complete changed centers/partition manifests and receipts directly read; unchanged full KOEN comparisons preserved. Geometry centers/boundary/fan/ear/quality distinct from camera/tool/locomotion options. Current actual new Studio titles/full descriptions/private or draft and existing future schedule read. See direct-review-v5.','--studio-evidence',p.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
print('Changed4 whole contents/current Studio directly reviewed; currentduplicate check0.')
