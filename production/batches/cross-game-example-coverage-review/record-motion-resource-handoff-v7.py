"""Record foreign handoff and pending duplicate changes without starting work."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, obj):
    temp = p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(temp, p)

out = R/'resource-and-annotation-handoff-v7.json'
assert not out.exists()
resource = read(R/'voice-retry-resource-verification-v8.json')
assert not resource['voiceRequestEligible'] and not resource['stableGpuIdle20SecondsVerified']
assert resource['currentForeignLease'] and resource['all68ProtectedHashesMatched']
for x in resource['protectedInputs']:
    assert sha(ROOT/x['path']) == x['sha256'], x['path']
request = read(R/'narration-tts-request-v1.json')
assert not any((ROOT/x['path']).exists() for x in request['scenes'])
prior = read(R/'duplicate-before-refresh-v6.json')
report_path = ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'
report = read(report_path)
assert report['verdict'] == 'pending-content-and-studio-review'
old = {x['path']:x['sha256'] for x in prior['inputFiles']}
changes = [x for x in report['inputFiles'] if old.get(x['path']) != x['sha256']]
assert len(changes) == 11
assert all('/publishing/youtube-upload.json' in x['path'] or
    x['path'] in ['projects/game-math-polygon-centers-v2/project.json',
        'projects/game-math-polygon-partition-v2/project.json'] for x in changes)
# Snapshot is inventory only. Never assert that these changed complete bodies or
# their current Studio pages have already been reviewed.
pending = dict(schemaVersion=1, recordedAt=datetime.now(timezone.utc).isoformat(),
    previousDirectReview='duplicate-content-and-studio-direct-review-v5.json',
    inventoryDigest=report['inputsDigest'], inputFiles=changes,
    inventoryFile=report_path.relative_to(ROOT).as_posix(), inventorySha256=sha(report_path),
    completeChangedContentsDirectlyRead=False, currentStudioDirectlyRead=False,
    verdict='pending-content-and-studio-review', actualCheckExitCode=1,
    deferReason='Foreign GPU handoff is active. Review full changed contents and actual current Studio before the next dependent voice request, after current resources become eligible.',
    foreignContentOrPlatformMutations=0)
pending_path = R/'duplicate-refresh-pending-v6.json'
assert not pending_path.exists()
save(pending_path, pending)
rows = []
for p in psutil.process_iter(['pid', 'create_time', 'cmdline', 'name']):
    try:
        if (p.info['name'] or '').lower() in ['python.exe', 'ffmpeg.exe']:
            rows.append(dict(pid=p.pid, createTime=p.create_time(), command=p.cmdline(), cwd=p.cwd()))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
stamp = datetime.now(timezone.utc).isoformat()
proof = dict(schemaVersion=1, observedAt=stamp,
    completedReadOnlyObservation=dict(actualShellChunk='16d446', actualExitCode=0,
        actualSessionId=None, path='voice-retry-resource-verification-v8.json',
        sha256=sha(R/'voice-retry-resource-verification-v8.json'), samples=1,
        stableGpuIdle20SecondsVerified=False),
    foreignRestoration=resource['subsequentForeignRestorationLineage'],
    currentOriginalResearch=resource['currentOriginalResearch'],
    currentResearchStatus=resource['currentResearchStatus'],
    currentForeignLease=resource['currentForeignLease'],
    currentOwnedVoiceOrGpuJobs=0, pythonAndFfmpeg=rows,
    duplicateReviewPending=pending_path.name, currentDuplicateCheckPassed=False,
    newPcmCount=0, all68ProtectedInputsMatched=True,
    researchPauseOrKillOrSuspendOrLeaseMutations=0, ownResearchResumeClaim=False,
    completedPortalAlyxAndStructuralReviewsPreserved=True, mediaOrGitImagesAdded=0,
    baselineVideoId='mBDd9VzSTkA', baselineScheduleChanged=False,
    replacementVideoId=None, oldUploadDeleted=False,
    next='Preserve active foreign lease and exact original research. Once foreign work closes and its actual research restoration is verified, make a single new read-only resource observation; require stable20s/current identities. Then read all changed full duplicate contents/current Studio and pass current --check before one new version TTS request. Do not repeat completed source/pilot QA or run V5 against false resources. Actual3PCM/whole3+independent15ASR/timing/mix/finalQA/4files/private/settings/Git/same09schedule must precede corresponding obsolete deletion.')
save(out, proof)
cp = read(R/'latest-checkpoint.json')
cp.update(recordedAt=stamp, currentHandoff=out.name,
    currentResourceVerification='voice-retry-resource-verification-v8.json',
    currentDuplicateCheckPassed=False, currentDuplicateReviewPending=pending_path.name,
    currentForeignHandoff=resource['currentForeignLease']['token'],
    currentOwnedVoiceWorkerAlive=False, currentOwnedGpuJobs=0,
    stableGpuIdle20SecondsVerified=False, newVoiceRequestStarted=False,
    newPcmCount=0, next=proof['next'])
save(R/'latest-checkpoint.json', cp)
qp = B/'queue.json'
raw = qp.read_text('utf-8-sig')
q = json.loads(raw)
q['currentMotionReview'].update(currentHandoff=out.relative_to(ROOT).as_posix(),
    currentResourceVerification=(R/'voice-retry-resource-verification-v8.json').relative_to(ROOT).as_posix(),
    currentDuplicateCheckPassed=False, currentDuplicateReviewPending=pending_path.relative_to(ROOT).as_posix(),
    currentForeignHandoff=resource['currentForeignLease']['token'], next=proof['next'])
q['updatedAt'] = stamp
assert qp.read_text('utf-8-sig') == raw
save(qp, q)
print(json.dumps(dict(newPcmCount=0, foreignLease=resource['currentForeignLease']['token'],
    duplicateChangesPending=len(changes), actualResourceExitCode=0), ensure_ascii=False))
