from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changes=read(BASE/'changed-duplicate-inputs-v3.json')
for x in changes['changed']:
 assert sha(ROOT/x['path'])==x['sha256'], 'Changed input moved again; read its new whole content'
 x['wholeTextDirectlyRead']=True
reason='The complete changed normal-transform-uv manifest, README and private receipt record final publishing verification, not new score-design claims. Its unchanged full narration covers perpendicular normals, inverse transpose and UV interpolation/addressing. Presenting Scores concerns achieved performance, quantity versus evaluation, names/units, opponent baselines and readable calculation feedback. Prior7 related whole KO/EN and current Studio comparisons remain as recorded; no decision relies on empty exact matches.'
studio='2026-10-09 read-only CUA tab134 https://studio.youtube.com/video/nalAZHtEtw0/edit: full title 게임수학 Part 2 · 렌더링 ⑥ 법선 변환과 UV and complete description/chapter claims directly read. Private, SD/HD complete, notification dash, save disabled. No edits. Description remains normal perpendicularity/inverse transpose, wall/roof UV correspondence, repeat/clamp and interpolate-before-wrap. Existing math40:60/noBGM exception does not change this batch60:40/Nimbus.'
proof=dict(schemaVersion=3,slug='presenting-game-scores',reviewedAt=datetime.now(timezone.utc).isoformat(),
 previousReview='content-studio-change-review-v2.json',previousReportPreserved='duplicate-history-before-change-v3.json',
 changedFiles=changes['changed'],newOrChangedScriptInputs=0,fullChangedContentsDirectlyRead=True,
 currentStudio=dict(tabId='134',url='https://studio.youtube.com/video/nalAZHtEtw0/edit',videoId='nalAZHtEtw0',
  title='게임수학 Part 2 · 렌더링 ⑥ 법선 변환과 UV',wholeTitleAndDescriptionDirectlyRead=True,
  privacy='비공개',sdHd='complete',notification='—',saveDisabled=True,edits=0),reason=reason,studioEvidence=studio,
 foreignFilesModified=0,foreignPublishingChanges=0,decision='distinct',priorRelatedWholeContentReviewPreserved=True)
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','presenting-game-scores','--decision','distinct','--reason',reason,'--studio-evidence',studio],cwd=ROOT,check=True)
subprocess.run([node,'scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
report=ROOT/'production/batches/sakurai-planning-game-design/preflight/presenting-game-scores.json'
proof.update(inputsDigest=read(report)['inputsDigest'],currentCheckExit=0,reportSha256=sha(report))
(BASE/'content-studio-change-review-v3.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
