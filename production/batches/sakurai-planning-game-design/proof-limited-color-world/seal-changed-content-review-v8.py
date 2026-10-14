from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=read(P.parent/'preflight/limited-color-world.json');snapshot=read(P/'changed-input-snapshot-v8.json')
assert report['inputsDigest']==snapshot['inputsDigest']=='e11e54b13f2d7e7f6c2124339c8f5b196568e35fb5524ccd899bf8e2d65d98ef'
assert all(sha(ROOT/x['path'])==x['sha256'] and sha(ROOT/x['snapshotPath'])==x['sha256'] for x in snapshot['inputs'])
assert all(sha(ROOT/x['path'])==x['sha256'] for x in report['inputFiles'])
ax=P/'current-quaternion-studio-v8.ax.txt';text=ax.read_text('utf-8');assert 'RENDERED TEXTBOX CONTENT:' in text and '예약됨' in text and '고화질 완료' in text
manifest=read(ROOT/snapshot['inputs'][0]['snapshotPath']);ko=read(ROOT/snapshot['inputs'][1]['snapshotPath']);en=read(ROOT/snapshot['inputs'][2]['snapshotPath'])
assert len(ko['scenes'])==len(en['scenes'])==5 and sum(len(s['lines']) for s in ko['scenes'])==13
dest=P/'content-studio-change-review-v8.json';assert not dest.exists()
proof=dict(schemaVersion=8,slug='limited-color-world',reviewedAt=datetime.now(timezone.utc).isoformat(),
 preservedPreviousReport='duplicate-history-approved59-v7.json',previousChangeReview='content-studio-change-review-v7.json',
 localOnlySnapshotProof='changed-input-snapshot-v8.json',projects=60,inputs=399,inputsDigest=report['inputsDigest'],
 changedFilesFullBodiesDirectlyRead=snapshot['inputs'],unchangedPreviouslyReviewedInputs=396,snapshotBodiesGitExcluded=True,
 wholeContentComparisons=[dict(slug=manifest['slug'],pairedScenes=5,pairedParagraphs=13,fullBothScriptsAndManifestDirectlyRead=True,
 comparison='All5paired scenes/13paragraphs read: same endpoint numbers versus temporal path; rotated x-to-y and preserved axial component; planar angle to 3D axis; inverse cancels rotation separately from translation; composing rotations and constructing intermediate flight orientations. Red torso/wing references denote projected direction, not hue-independent information design. This additions-only correction retains quaternion reference/contract, preserves baseline/v2/v3/v4 audio and cannot independently upload. It does not teach outline/pattern/height/motion/lightness redundancy when color differs.')],
 currentStudio=dict(actualId='03OXtik2nes',url='https://studio.youtube.com/video/03OXtik2nes/edit',fullTitleDescriptionAnd19ChaptersDirectlyRead=True,
 title='게임수학 Part 2 · 3D 회전 ③ 쿼터니언의 원리와 계산',observedStatus='예약됨',sdHdObserved=True,settingsChanged=False,ax=ax.relative_to(ROOT).as_posix(),axSha256=sha(ax)),
 failedNavigationPreflight=dict(toolObservation='6eb72c',exitCode=1,modelOrSourceExtractionStarted=False,stateCreated=False),
 decision='distinct',foreignFilesOrSettingsModified=0,currentProductionApprovalSeparate=True)
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),digest=report['inputsDigest'],pairedScenes=5)))
