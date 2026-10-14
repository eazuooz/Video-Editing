"""Seal bounded content reads; keep the dependent TTS duplicate gate pending."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, psutil

ROOT = Path(__file__).resolve().parents[3]
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = R/'duplicate-content-partial-direct-review-v7.json'
assert not out.exists()
report_path = ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'
report = read(report_path)
assert report['inputsDigest'] == 'fa3480a768a600bfcf91b9f7f2dc3c04dc66b8caded20650f7087a4ecf1800e3'
old = {x['path']: x['sha256'] for x in read(R/'duplicate-before-refresh-v6.json')['inputFiles']}
changed = [x for x in report['inputFiles'] if old.get(x['path']) != x['sha256']]
assert len(changed) == 24
completed = {
 'projects/game-math-quaternion-foundations-v3/script/narration.ko.json': 'e3a8dda51476e837e9ffc59b51b7e0588377747b8bba652155db04e1200af1ac',
 'projects/game-math-quaternion-foundations-v3/script/narration.en.json': '0f2cd73672bcf3246eb04268b3deb3ebce7d66d7cc5ea2d09aac16d922bdc84b',
 'projects/game-math-quaternion-calculations-v3/script/narration.ko.json': 'c91c55f9e5444f0a58d61cafae0f8b2e7607f875730266c2e6baa8303dd73af5',
 'projects/game-math-quaternion-calculations-v3/script/narration.en.json': '882f143feac6f92dd8afa1418cfa5871f774dd48059610545ff4efe12f4f3c0c',
 'projects/game-math-quaternion-cross-game-additions-v3/script/narration.ko.json': '5d4ffd49100f8d1f2e69c20c6370ead654864ecd84afac8db0c8d758dbe00514',
 'projects/game-math-quaternion-cross-game-additions-v3/script/narration.en.json': 'c1bd04f36cdf515cf21f1deccd0506b60745b4a91ae9aa4022ed81f2b6c0f60d',
 'projects/game-math-quaternion-foundations-v3/planning/outline.md': '1c6f313de9de671a298888f5ea11afd56ad02734a32bf46af8fcf275c703f346',
 'projects/game-math-quaternion-foundations-v3/sources/SOURCES.md': 'a7e8f6a124f8f4115ac61c42045d1319aa7feaf99b1ef68354f7780f671dec83',
 'projects/game-math-quaternion-calculations-v3/planning/outline.md': 'a9931655cbab73c34eaa7db4609e62db70ef65c3275a29d91edeb470ab1d7c51',
 'projects/game-math-quaternion-calculations-v3/sources/SOURCES.md': 'a7e8f6a124f8f4115ac61c42045d1319aa7feaf99b1ef68354f7780f671dec83',
 'projects/game-math-quaternion-calculations-v3/project.json': 'e45e21ece6e30e97cb0eba91daa0a113befca629a5fa622cf303a35564020292',
 'projects/game-math-quaternion-cross-game-additions-v3/project.json': 'c380a46a4b1523fb70a4e0e0c2b1f611bea7b95cfab4cb1303ac5ae3d0446f3d',
 'projects/game-math-polygon-centers-v2/project.json': '5edd59b414844f3565e97a70040f6e8636d9eb0897f4053e145bfc3df820d9b8',
 'projects/game-math-polygon-partition-v2/project.json': 'f00b0551056387ee0bf60afec4c00f9eefb5ac69983a111d42527ca8fb0733d3',
}
reviewed = []
for path, expected in completed.items():
    current = sha(ROOT/path)
    reviewed.append(dict(path=path, reviewedSha256=expected, currentSha256=current,
        currentBytesMatchReviewed=current == expected, wholeContentDirectlyRead=True,
        foreignCompletionApproved=False))
remaining = [x for x in changed if x['path'] not in completed]
ax = R/'current-studio-future-list-v7.ax.txt'
assert ax.stat().st_size > 60000 and 'mBDd9VzSTkA' in ax.read_text('utf-8')
voice_resource = read(R/'voice-retry-resource-verification-v10.json')
assert voice_resource['voiceRequestEligible'] and voice_resource['stableGpuIdle20SecondsVerified']
assert voice_resource['currentForeignLease'] is None
for row in voice_resource['protectedInputs']:
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
request = read(R/'narration-tts-request-v1.json')
assert not any((ROOT/x['path']).exists() for x in request['scenes'])
now = datetime.now(timezone.utc).isoformat()
proof = dict(schemaVersion=1, reviewedAt=now, inventoryDigest=report['inputsDigest'],
    inventoryProjectCount=len(report['existingProjects']), inventoryInputCount=len(report['inputFiles']),
    changedInputs=changed, completeReviewedInputs=reviewed, remainingWholeContentReads=remaining,
    sourceScriptReview=dict(projects=3, koScenes=108, enScenes=108, koLines=338, enLines=338,
        readOutputs=['d6c8ab','991f46','f329d3','8a440c','54af9f','d01eef','6bcbc0'],
        scope='All six current KOEN bodies read in bounded chunks; truncated multi-file attempts are not completion evidence. The missing calculations EN opening was reread separately.'),
    findings=[
        'Quaternion foundations: imaginary/complex planar rotation, unit axis and half-angle, q/-q, norm, conjugate and inverse; different from motion camera/aim/locomotion design.',
        'Quaternion calculations: ordered Hamilton composition, world/body deltas, target rotation, minimal endpoint angle and worked two-sided vector rotation; not a camera comfort or input-option episode.',
        'Four-game addition project is a non-standalone voice batch for Riders Republic/Trailmakers/Space Engineers/Besiege. Its shared red/blue screen guides are teaching presentation, not duplicate viewer claims.',
        'Polygon centers and partition manifest changes record actual new IDs and later lecture anchors. This read does not independently approve foreign video quality or rights.'
    ],
    currentStudioFutureList=dict(path=ax.relative_to(ROOT).as_posix(), sha256=sha(ax),
        actualScheduledRows=28, observedScope='Visible future list titles, dates and truncated description previews. Whole edit descriptions and exact modal times not reread.',
        motionDate='2026-10-12', orientationDate='2026-10-13', hierarchicalDate='2026-10-14',
        centers=dict(videoId='YgcN8vs0gNo', date='2026-11-02'),
        partition=dict(videoId='pfagaQK-xfI', date='2026-11-04'),
        meshDate='2026-11-14', normalDate='2026-11-16',
        settingsChanged=False),
    completeAllChangedContentsDirectlyRead=False, currentWholeStudioReviewComplete=False,
    verdict='pending-remaining-receipts-and-whole-Studio-review', currentDuplicateCheckPassed=False,
    observerV10=dict(sessionId=31954, actualOuterExitCode=0, shellChunk='54321f',
        path='voice-retry-resource-verification-v10.json', sha256=sha(R/'voice-retry-resource-verification-v10.json'),
        observedAt=voice_resource['observedAt'], samples=len(voice_resource['gpuObservations']),
        stableGpuIdle20SecondsVerified=True, voiceResourceEligibleAtObservation=True,
        eligibilityForNextRequestMustBeFreshlyRevalidated=True),
    all68ProtectedHashesMatched=True, newPcmCount=0, newVoiceRequestStarted=False,
    foreignFilesOrPlatformSettingsChanged=False, mediaOrSourceQaRepeated=False)
out.write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', 'utf-8')
cp_path = R/'latest-checkpoint.json'
q_path = ROOT/'production/batches/cross-game-example-coverage-review/queue.json'
cp_bytes, q_bytes = cp_path.read_bytes(), q_path.read_bytes()
cp, queue = read(cp_path), read(q_path)
next_step = ('Finish the remaining nine changed publishing receipts and bounded foundation-manifest reread, '
    'then actual whole current Studio descriptions before current distinct/check. Reuse partial-v7 SHA-bound '
    'complete reads when unchanged. ObserverV10 completed31954/exit0 proved stable20s at23:20; it is history, '
    'not a fresh start authorization after prolonged review. Before one new voice wrapper request create one '
    'fresh resource version referencingV10; require current identity, no foreign lease, stable20s and68SHA. '
    'Do not run preparedV5 against falseV6. Preserve Oct12 baseline schedule until complete replacement.')
cp.update(recordedAt=now, stage='resource-observed-eligible-partial-new-content-review-pending',
    currentResourceVerification='voice-retry-resource-verification-v10.json',
    stableGpuIdle20SecondsVerified=True, currentForeignHandoff=None,
    currentDuplicateReviewPending=out.name, currentDuplicateCheckPassed=False,
    currentHandoff='resource-and-annotation-handoff-v11.json', next=next_step,
    currentOriginalResearchPid=voice_resource['currentOriginalResearch']['pid'],
    currentOriginalResearchCreateTime=voice_resource['currentOriginalResearch']['createTime'],
    currentOriginalResearchAlive=voice_resource['currentOriginalQueueAlive'],
    currentOriginalResearchObservationAt=voice_resource['observedAt'],
    newVoiceRequestStarted=False, newPcmCount=0)
handoff = dict(schemaVersion=1, recordedAt=now, latestContentProgress=out.name,
    observer=proof['observerV10'], currentOriginalResearchAtObservation=voice_resource['currentOriginalResearch'],
    restorationScope=voice_resource['restorationScope'],
    subsequentForeignRestorationLinks=len(voice_resource['subsequentForeignRestorationLineage']),
    next=next_step, allFinalApprovals=False, currentDuplicateCheckPassed=False,
    newRequestOrModelOrPcmOrMedia=0, sourceOrPilotOrQaReexecutions=0,
    foreignProcessOrPauseOrLeaseOrPlatformMutations=0, gitActions=0)
hp = R/'resource-and-annotation-handoff-v11.json'
assert not hp.exists()
hp.write_text(json.dumps(handoff, ensure_ascii=False, indent=2)+'\n', 'utf-8')
queue['updatedAt'] = now
motion = queue['currentMotionReview']
motion.update(status=cp['stage'], stage=cp['stage'], next=next_step,
    currentHandoff=hp.relative_to(ROOT).as_posix(),
    currentResourceVerification=(R/'voice-retry-resource-verification-v10.json').relative_to(ROOT).as_posix(),
    currentDuplicateReviewPending=out.relative_to(ROOT).as_posix(),
    currentDuplicateCheckPassed=False, currentForeignHandoff=None,
    newTts=False, newVideoId=None, deleted=False)
assert cp_path.read_bytes() == cp_bytes and q_path.read_bytes() == q_bytes
cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=2)+'\n', 'utf-8')
q_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(completeReads=len(reviewed), stillCurrent=sum(x['currentBytesMatchReviewed'] for x in reviewed),
    pending=len(remaining), observerCompleted=True, dependentDuplicatePassed=False, newPcm=0)))
