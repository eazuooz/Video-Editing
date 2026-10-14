from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=read(P.parent/'preflight/limited-color-world.json');snapshot=read(P/'changed-input-snapshot-v7.json')
assert report['inputsDigest']==snapshot['inputsDigest']=='08b6c292d201d34fe4088441df3fbd85e98fdc0adff36b3400a0c5e2b2c98d1a'
assert all(sha(ROOT/x['path'])==x['sha256'] and sha(ROOT/x['snapshotPath'])==x['sha256'] for x in snapshot['inputs'])
assert all(sha(ROOT/x['path'])==x['sha256'] for x in report['inputFiles'])
ax=P/'current-quaternion-studio-v7.ax.txt';assert 'RENDERED TEXTBOX CONTENT:' in ax.read_text('utf-8')
proof=dict(schemaVersion=7,slug='limited-color-world',reviewedAt=datetime.now(timezone.utc).isoformat(),
 preservedPreviousReport='duplicate-history-approved58-v6.json',previousChangeReview='content-studio-change-review-v6.json',
 localOnlySnapshotProof='changed-input-snapshot-v7.json',projects=59,inputs=396,inputsDigest=report['inputsDigest'],
 changedFilesFullBodiesDirectlyRead=snapshot['inputs'],unchangedPreviouslyReviewedInputs=389,snapshotBodiesGitExcluded=True,
 wholeContentComparisons=[
  dict(slug='game-math-quaternion-foundations-v2',pairedScenes=42,fullBothScriptsDirectlyRead=True,comparison='All current42paired scenes and metadata read: imaginary/complex planar rotation, unit axis and half-angle, two-sided operation, unit norm, q/-q, identity, conjugation and general inverse. New compact game annotations separate projected body/wing directions from measured world values. These teach rotation representation rather than multi-cue color readability.'),
  dict(slug='game-math-quaternion-calculations-v2',pairedScenes=36,fullBothScriptsDirectlyRead=True,comparison='All current36paired scenes and metadata read: dot/cross and Hamilton products, composition order and world/body frames, target deltas, minimum endpoint angle, fractional log/exp, two-sided vector rotation, code conventions and numerical exercises. New footage bridges explicitly distinguish excerpts and projected reference lines. The viewer question is algebraic orientation calculation, distinct from hue-independent outline/pattern/height/motion/lightness.'),
  dict(slug='game-math-quaternion-teaching-additions-v4',pairedScenes=17,fullBothScriptsAndManifestDirectlyRead=True,comparison='All new17paired additions and the full manifest read: causal narration and colored torso/wheel/wing/skis annotations for the existing rotation revision. standaloneUploadAllowed is false, revisionOf points to the quaternion baseline, and no new ID is invented. The supplement teaches reference frames, orientation-vs-route and calculations, without duplicating the limited-color-world information-design lesson.')],
 wholeCurrentPairedScenes=95,limitedQuestion='How do outline, pattern, height, motion and lightness retain essential gameplay information when hues differ?',
 currentStudio=dict(actualId='03OXtik2nes',url='https://studio.youtube.com/video/03OXtik2nes/edit',fullTitleDescriptionAnd19ChaptersDirectlyRead=True,title='게임수학 Part 2 · 3D 회전 ③ 쿼터니언의 원리와 계산',observedStatus='예약됨',sdHdObserved=True,settingsChanged=False,ax=ax.relative_to(ROOT).as_posix(),axSha256=sha(ax)),
 failedBankSeal=dict(toolObservation='7ba4b7',exitCode=1,sourceBankV2NotWritten=True,newTtsOrModelStarted=False,preservedV6EndpointReview=True),
 decision='distinct',foreignFilesOrSettingsModified=0,currentProductionApprovalSeparate=True)
dest=P/'content-studio-change-review-v7.json';assert not dest.exists();dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),digest=report['inputsDigest'],pairedScenes=95)))
