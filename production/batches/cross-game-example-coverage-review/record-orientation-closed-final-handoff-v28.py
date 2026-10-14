"""Seal actual closed workers and the resumable bounded final review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, v):
    t = p.with_name(p.name + '.handoff-writing')
    t.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(t, p)

def closed(name):
    p = O / name
    s = read(p)
    assert s['actualOuterExitCode'] == 0 and s['workerDead']
    try:
        live = psutil.Process(s['pid'])
        assert abs(live.create_time() - s['createTime']) >= .01, 'Owned identity still alive'
    except psutil.NoSuchProcess:
        pass
    cim = subprocess.check_output(['powershell', '-NoProfile', '-Command',
        f"Get-CimInstance Win32_Process -Filter 'ProcessId={s['pid']}' | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],
        text=True, encoding='utf-8', errors='replace')
    return dict(path=rel(p), sha256=sha(p), actualSession=s['actualSession'],
        actualOuterExitCode=0, completionChunk=s['completionChunk'], workerDead=True,
        pid=s['pid'], createTime=s['createTime'], commandLine=s['commandLine'], cwd=s['cwd'],
        sameIdentityAliveAtObservation=False, actualCim=cim), s

out = R / 'resource-and-annotation-handoff-v28.json'
assert not out.exists()
proof = read(O / 'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs'] + proof['results']:
    assert sha(ROOT / x['path']) == x['sha256']
pair, ps = closed('current34-final-pair-execution-v3.json')
pixel, xs = closed('current34-pair-pixel-execution-v2.json')
branding, bs = closed('current34-branding-pixel-execution-v3.json')
assert ps['frames'] == 65917 and len(ps['pieces']) == 37
assert all(x['wholeDecodeExitCode'] == 0 and x['identicalReviewedWholeAacPackets'] for x in ps['pair'])
assert len(xs['results'][0]['samples']) == 3168 and len(xs['results'][0]['boards']) == 792
assert branding['actualSession'] is None and len(bs['results'][0]['samples']) == 3
dp = O / 'current34-final-pixels-partial-direct-review-v1.json'
d = read(dp)
assert d['pixelExecutionSha256'] == pixel['sha256'] and d['pairExecutionSha256'] == pair['sha256']
assert d['boardsDirectlyRead'] < 792 and d['nextBoard'] == d['boardsDirectlyRead'] + 1
np = O / 'current34-final-normal-direct-review-v3.json'
n = read(np)
assert n['executionSha256'] == pair['sha256'] and n['allNormalStartEndObserved']
assert n['start']['rate'] == n['end']['rate'] == 1 and n['end']['ended']
bp = O / 'current34-branding-supplement-direct-review-v3.json'
br = read(bp)
assert br['executionSha256'] == branding['sha256'] and br['all3SamplesDirectlyRead']
previous = R / 'resource-and-annotation-handoff-v27.json'
stamp = datetime.now(timezone.utc).isoformat()
data = dict(recordedAt=stamp, previousHandoff=rel(previous), previousHandoffSha256=sha(previous),
    currentProject='game-math-orientation-matrices', activeOwnedWorkers=0,
    pair=pair, pixel=pixel, branding=branding,
    technicalClosure=dict(frames=65917, seconds=65917/60, pieces=37, bothWholeDecode0=True,
        identicalReviewedAACPackets=True, bodyMeasured=ps['bodyMeasured'],
        evidence='Completed pair/pixel execution and actual closure records; no repeated encoding, extraction or decoding.'),
    normalReview=dict(path=rel(np), sha256=sha(np), allNormalStartEndObserved=True,
        continuousListeningApproved=False),
    brandingReview=dict(path=rel(bp), sha256=sha(bp), all3SamplesDirectlyRead=True),
    partialFinalReview=dict(path=rel(dp), sha256=sha(dp), boardsDirectlyRead=d['boardsDirectlyRead'],
        samplesDirectlyRead=d['samplesDirectlyRead'], totalBoards=792, totalSamples=3168, nextBoard=d['nextBoard']),
    all79ProtectedUnchanged=True, repairCandidateUnchanged=True,
    newTts=0, newAsr=0, newMix=0, newRender=0, newExtraction=0, newServer=0, newImageGit=0,
    researchChanges=0, final244PixelsApproved=False, mainPromotion=False, fourOutputsCollected=False,
    newUploadId=None, publishingComplete=False, gitDeliveryComplete=False, actualReplacementSchedule=False,
    obsoleteDeleted=False, humanListeningApproved=False, humanPronunciationApproved=False, publicRightsApproved=False,
    stopBoundary='Finish authorized revisions through game-math-normal-transform-uv then pause task and owned continuation. No subsequent lectures or Sakurai6.',
    next=f"Continue bounded final direct pixel review from board{d['nextBoard']:03d}. Pair26596 and pixels83766 already exited0 and workers are dead. Branding supplemental extraction has no session and is closed. Normal1x muted start/end already observed; no replay. No repeated TTS/ASR/mix/encoding/extraction or research restart. All final selected pixels and technical/teaching QA precede explicit main promotion, four outputs, one private captioned upload/settings, selective Git and actual current Studio09slot replacement. Preserve foreign work and unanswered action-time deletion request.")
save(out, data)
cp = read(O / 'latest-checkpoint.json')
assert cp['activeOwnedWorkers'] == 0
cp['latestHandoff'] = rel(out)
save(O / 'latest-checkpoint.json', cp)
qp = B / 'queue.json'
raw = qp.read_bytes()
q = read(qp)
q['currentOrientationReview']['latestHandoff'] = rel(out)
q['updatedAt'] = stamp
assert qp.read_bytes() == raw
save(qp, q)
print(json.dumps(dict(handoff=rel(out), activeOwnedWorkers=0, nextBoard=d['nextBoard'], finalApproved=False)))
