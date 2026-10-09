from pathlib import Path
import json, subprocess
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parent
REPORT=ROOT/'production/batches/sakurai-planning-game-design/preflight/presenting-game-scores.json'
old=json.loads(REPORT.read_text('utf-8-sig'))
history=BASE/'duplicate-history-before-change-v3.json'
if not history.exists():history.write_bytes(REPORT.read_bytes())
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
 'scripts/review-video-duplicates.cjs','presenting-game-scores'],cwd=ROOT,check=True)
new=json.loads(REPORT.read_text('utf-8-sig'))
prior={x['path']:x['sha256'] for x in old['inputFiles']}
changes=[x for x in new['inputFiles'] if prior.get(x['path'])!=x['sha256']]
(BASE/'changed-duplicate-inputs-v3.json').write_text(json.dumps(dict(previousDigest=old['inputsDigest'],
 currentDigest=new['inputsDigest'],projects=len(new['existingProjects']),inputs=len(new['inputFiles']),changed=changes),
 ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(changes,ensure_ascii=False,indent=2))
