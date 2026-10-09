from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rp=ROOT/'production/batches/sakurai-planning-game-design/preflight/presenting-game-scores.json';old=read(B/'duplicate-history-before-source-only-v4.json');new=read(rp)
lookup={x['path']:x['sha256'] for x in old['inputFiles']};changed=[x for x in new['inputFiles'] if lookup.get(x['path'])!=x['sha256']]
assert [x['path'] for x in changed]==['projects/game-lighting-history-04/planning/outline.md']
assert changed[0]['sha256']=='8ab2233cfae46d07b8a5d5ecc7208f22b5e0b9fb005d488647b544cb9b5813cf'
reason='Read the complete changed game-lighting-history-04 outline. Its virtual shadow-map pages, temporal upscaling/display frames, visibility-buffer surface identity, mobile deferred tiles, path-tracing sample budgets, ray reconstruction, many-light sampling, transparency/hair, DLSS inputs/outputs, exposure/tone mapping and frame-resource audits are rendering concepts. Score quantities versus evaluation, chosen weights, event versus accumulated totals, score labels/units, comparison references and calculation feedback remain distinct. All unchanged52-project full-content evidence is preserved by duplicate-direct-review-v3. This revision only shifts one Tetris source interval to align the equality claim; no title/ID shortcut.'
proof=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/rights/current-studio-nalAZHtEtw0-source-repair-v4.ax.txt'
studio='2026-10-10 03:54KST CUA tab134 actual Studio reload and complete title/description read: nalAZHtEtw0 remains scheduled, SD/HD complete, save disabled. Its perpendicular tangent/normal, inverse transpose, UV mapping/scale/rotation/reflection/repeat/clamp and vertex wrapping examples are distinct from score-display design. Read-only; no foreign settings changed. Proof '+str(proof.relative_to(ROOT).as_posix())
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','presenting-game-scores','--decision','distinct','--reason',reason,'--studio-evidence',studio],cwd=ROOT,check=True)
subprocess.run([node,'scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
new=read(rp);target=B/'duplicate-direct-review-v4.json';assert not target.exists()
target.write_text(json.dumps(dict(reviewedAt=datetime.now(timezone.utc).isoformat(),previousReview='projects/presenting-game-scores/production/revision-balatro60-v2/duplicate-direct-review-v3.json',changedInputs=[dict(x,wholeTextDirectlyRead=True) for x in changed],reason=reason,studioEvidence=studio,studioProofSha256=sha(proof),inputsDigest=new['inputsDigest'],reportSha256=sha(rp),currentCheckExit=0,foreignFileChanges=0,foreignPublishingChanges=0),ensure_ascii=False,indent=2)+'\n','utf-8')
