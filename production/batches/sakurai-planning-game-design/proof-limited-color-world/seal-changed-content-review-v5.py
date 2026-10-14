"""Seal the directly read nine new foreign inputs without modifying them."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
report = read(BASE.parent/'preflight/limited-color-world.json')
previous = read(BASE/'duplicate-history-approved55-v4.json')
assert report['inputsDigest'] == '85de1ba396f51240d44349fac8fc081f98d4008aef52856b3fc7ab52cbc73b3a'
old = {x['path']: x['sha256'] for x in previous['inputFiles']}
current = {x['path']: x['sha256'] for x in report['inputFiles']}
assert len(current) == 393 and len(report['existingProjects']) == 58
assert all(current.get(p) == s for p, s in old.items()), 'Earlier reviewed inputs changed.'
expected = {
 'projects/game-math-quaternion-calculations-v2/project.json': '9a775a10d9a73376ad9070708056a195ad58d0a1417271e045f4deec7181c629',
 'projects/game-math-quaternion-calculations-v2/script/narration.ko.json': '9af172da551df20b93d8d1d1255fbfeef3ae37e0116dfd0a1af80eb00e80875b',
 'projects/game-math-quaternion-calculations-v2/script/narration.en.json': 'ad89a36d15923b13830b32d66ea4bc78758ad175b3b2198eeed6638a44d9f98f',
 'projects/game-math-quaternion-foundations-v2/project.json': '75d6ca283ae93667a991ae35157b6af4a2bbb9fe9b729789abfce68948a47685',
 'projects/game-math-quaternion-foundations-v2/script/narration.ko.json': 'd7b654eeda2b8face253926ae70d2eaf3cb9cbc43feb648e139359c60d1b51f9',
 'projects/game-math-quaternion-foundations-v2/script/narration.en.json': '98107004eaf703895a19f09192014037d861c10f5ef7cb655f7947af36c5d05d',
 'projects/game-math-quaternion-teaching-additions-v3/project.json': 'd71ff936de17967efc81e43a24338e027da8d47e9f71d85cc924b93e49d4e3d0',
 'projects/game-math-quaternion-teaching-additions-v3/script/narration.ko.json': '7549524475ff3e1637fc2bb5cc28ee2250cd216e3c31dde423b56a5ad8b0473d',
 'projects/game-math-quaternion-teaching-additions-v3/script/narration.en.json': '99c8084087901766ff4a69c4f92b5edcfcaecced357837d737e31f02cfb13f7a',
}
snapshot = read(BASE/'changed-input-snapshot-v5.json')
assert snapshot['inputsDigest'] == report['inputsDigest']
assert {x['path']:x['sha256'] for x in snapshot['inputs']} == expected
assert all(sha(ROOT/x['snapshotPath']) == x['sha256'] for x in snapshot['inputs'])
assert set(current)-set(old) == set(expected)
assert all(current[p] == s and sha(ROOT/p) == s for p,s in expected.items())
assert all(sha(ROOT/p) == s for p,s in current.items()), 'Current inventory drifted; reread changed files.'
ax = BASE/'current-quaternion-studio-v5.ax.txt'
assert ax.exists()
rows=[]
for slug,count,comparison in [
 ('game-math-quaternion-foundations-v2',43,'The full paired 43 scenes introduce imaginary/complex numbers, the unit circle, 3D axis and half-angle construction, q/-q, identity, norm/normalization, conjugation and general inverse. Actual orientation, speed and camera are separated. This is rotation representation and algebra, not hue-independent identification of gameplay cues.'),
 ('game-math-quaternion-calculations-v2',34,'The full paired 34 scenes teach Hamilton product order, world/body frames, target delta, the four-component dot product and minimal angle, fractional rotation/log-exp, two-sided vector rotation and code conventions. Red/teal/blue lines annotate mathematical directions; they do not teach perceptual previews, outlines/patterns or contrast accessibility.'),
 ('game-math-quaternion-teaching-additions-v3',29,'The full paired 29 scenes are authorized narration supplements to the same quaternion baseline: prerequisites, preserved numerical examples and causal game-to-calculation bridges. Its manifest disallows standalone upload. The additions develop orientation mathematics rather than limited-color-world’s information-design question.'),
]:
    k=read(ROOT/f'projects/{slug}/script/narration.ko.json')
    e=read(ROOT/f'projects/{slug}/script/narration.en.json')
    assert len(k['scenes']) == len(e['scenes']) == count
    assert [x['id'] for x in k['scenes']] == [x['id'] for x in e['scenes']]
    rows.append(dict(slug=slug,wholeManifestAndBothScriptsDirectlyRead=True,pairedScenes=count,comparison=comparison))
out = dict(schemaVersion=5, slug='limited-color-world', reviewedAt=datetime.now(timezone.utc).isoformat(),
 previousFullRelatedReview='content-studio-direct-review-v2.json', previousChangeReview='content-studio-change-review-v4.json',
 preservedPreviousReport='duplicate-history-approved55-v4.json', projects=58, inputs=393, inputsDigest=report['inputsDigest'],
 earlier384InputsUnchanged=True, changedFilesFullBodiesDirectlyRead=[dict(path=p,sha256=s) for p,s in expected.items()],
 initialPending58Preserved='duplicate-history-pending58-v5.json',
 firstSealAttempt=dict(toolObservation='3bfb5d',exitCode=1,failedBeforeProofCreation=True,reason='Six foreign paired scripts changed after the first pending inventory; all six current full bodies were then read from immutable local snapshots.'),
 localOnlySnapshotProof='changed-input-snapshot-v5.json',snapshotBodiesGitExcluded=True,
 wholeContentComparisons=rows,
 limitedQuestion='How can essential game information remain readable when hues are hard to distinguish? Use outline, pattern, height, movement, lightness and perceptual previews without claiming a universal guarantee.',
 currentStudio=dict(actualId='03OXtik2nes',url='https://studio.youtube.com/video/03OXtik2nes/edit',
  fullTitleDescriptionAnd19ChaptersDirectlyRead=True,observedStatus='예약됨',sdHdObserved=True,
  title='게임수학 Part 2 · 3D 회전 ③ 쿼터니언의 원리와 계산',
  ax=ax.relative_to(ROOT).as_posix(),axSha256=sha(ax),settingsChanged=False),
 newEpisodeIdsNotInvented=True,absenceFromChannelNotInferred=True,foreignFilesOrSettingsModified=0,
 decision='distinct',currentProductionApprovalSeparate=True)
dest=BASE/'content-studio-change-review-v5.json'
assert not dest.exists()
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),projects=58,inputs=393,inputsDigest=report['inputsDigest'],wholeNewPairedScenes=106,foreignModifications=0)))
