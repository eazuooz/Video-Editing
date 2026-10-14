"""Record the six complete paired-script rereads; preserve foreign files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[4]
P = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = read(P.parent/'preflight/limited-color-world.json')
previous = read(P/'duplicate-history-approved58-v5.json')
snapshot = read(P/'changed-input-snapshot-v6.json')
assert report['inputsDigest'] == snapshot['inputsDigest'] == 'c5d0904096685e691a342e25f2b37fa5539ed8480236d32cbd9efc2e371b238f'
old = {x['path']:x['sha256'] for x in previous['inputFiles']}
current = {x['path']:x['sha256'] for x in report['inputFiles']}
changed = {p:h for p,h in current.items() if old.get(p)!=h}
assert set(current)==set(old) and len(current)==393 and len(report['existingProjects'])==58
assert changed == {x['path']:x['sha256'] for x in snapshot['inputs']}
assert len(changed)==6
assert all(sha(ROOT/x['snapshotPath'])==x['sha256'] for x in snapshot['inputs'])
assert all(sha(ROOT/p)==h for p,h in current.items()), 'Current inventory changed again; reread changed bodies.'
comparisons = [
 ('game-math-quaternion-foundations-v2',42,'All 42 current paired scenes and metadata were read. Imaginary numbers, complex-plane/unit-circle rotation, 3D unit axes and half-angle, q/-q, identity, normalization, conjugation and general inverse establish rotation representation. Speed, position, camera and posture are separated. Colored direction annotations support algebra rather than hue-independent information design.'),
 ('game-math-quaternion-calculations-v2',36,'All 36 current paired scenes and metadata were read. The new causal bridge to Hamilton multiplication and dot/cross prerequisites continue through noncommutativity, world/body frames, current-to-target deltas, four-component dot/minimal angles, log-exp fractional turns, two-sided vector rotation, code conventions and exercises. These are orientation calculations, distinct from reading outlines, patterns, motion and lightness when colors differ.'),
 ('game-math-quaternion-teaching-additions-v3',30,'All 30 current paired additions and metadata were read. Numerical prerequisites and causal bridges preserve the rotation baseline; new scene30 connects inverse rotation to two-operation composition and dot/cross tools. It is the previously read manifest\'s authorized additive supplement, without a new standalone ID. It does not replace limited-color-world\'s readability question.'),
]
rows=[]
for slug,count,comparison in comparisons:
    k=read(ROOT/f'projects/{slug}/script/narration.ko.json'); e=read(ROOT/f'projects/{slug}/script/narration.en.json')
    assert len(k['scenes'])==len(e['scenes'])==count
    assert [x['id'] for x in k['scenes']]==[x['id'] for x in e['scenes']]
    rows.append(dict(slug=slug,fullBothScriptsAndMetadataDirectlyRead=True,pairedScenes=count,previousManifestUnchanged=True,comparison=comparison))
ax=P/'current-quaternion-studio-v6.ax.txt'
assert ax.exists() and 'RENDERED TEXTBOX CONTENT:' in ax.read_text('utf-8')
proof=dict(schemaVersion=6,slug='limited-color-world',reviewedAt=datetime.now(timezone.utc).isoformat(),
 previousFullRelatedReview='content-studio-direct-review-v2.json',previousChangeReview='content-studio-change-review-v5.json',
 preservedPreviousReport='duplicate-history-approved58-v5.json',localOnlySnapshotProof='changed-input-snapshot-v6.json',
 projects=58,inputs=393,inputsDigest=report['inputsDigest'],unchangedPreviouslyReviewedInputs=387,
 changedFilesFullBodiesDirectlyRead=[dict(path=p,sha256=h) for p,h in changed.items()],snapshotBodiesGitExcluded=True,
 wholeContentComparisons=rows,wholeCurrentPairedScenes=108,
 firstExtraNativeAttempt=dict(toolObservation='9450a9',exitCode=1,rejectedBeforeStateQaOrFfmpeg=True,reason='Current duplicate gate rejected changed foreign scripts. All six current full bodies were subsequently reread before a new attempt.'),
 limitedQuestion='How can essential game information remain readable when hues are hard to distinguish? Compare outline, pattern, height, motion and lightness; previews do not guarantee accessibility for everyone.',
 currentStudio=dict(actualId='03OXtik2nes',url='https://studio.youtube.com/video/03OXtik2nes/edit',fullTitleDescriptionAnd19ChaptersDirectlyRead=True,
  title='게임수학 Part 2 · 3D 회전 ③ 쿼터니언의 원리와 계산',observedStatus='예약됨',sdHdObserved=True,settingsChanged=False,
  ax=ax.relative_to(ROOT).as_posix(),axSha256=sha(ax)),
 newEpisodeIdsNotInvented=True,absenceFromChannelNotInferred=True,foreignFilesOrSettingsModified=0,decision='distinct',currentProductionApprovalSeparate=True)
dest=P/'content-studio-change-review-v6.json'; assert not dest.exists()
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),inputsDigest=report['inputsDigest'],pairedScenes=108,foreignModifications=0)))
