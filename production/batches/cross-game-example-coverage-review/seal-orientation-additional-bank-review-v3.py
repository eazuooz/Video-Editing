"""Seal the previously directly inspected 36 native samples and eight boards."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil
ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, x):
    tmp = p.with_name(p.name + f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)
s = read(O / 'additional-bank-native-extraction-v3.json')
assert s['actualExitObserved'] and s['actualOuterExitCode'] == 0
assert not psutil.pid_exists(s['pid']) and not psutil.pid_exists(s['ffmpegPid'])
m = read(O / 'additional-bank-native-v3/manifest.json')
assert len(m['samples']) == 36 and len(m['boards']) == 8
for x in m['samples'] + m['boards']:
    assert sha(ROOT / x['path']) == x['sha256']
for x in m['sources']:
    assert sha(ROOT / x['sourcePath']) == x['sourceSha256'] and x['exactPtsMatched']
for x in m['samples']:
    assert x['pts'] == x['nativeFrame'] * 256
t = read(O / 'narration-07b-guide-repair-execution-v1.json')
for x in t['protectedInputs'] + t['results']:
    assert sha(ROOT / x['path']) == x['sha256']
p = O / 'additional-bank-native-direct-review-v3.json'
assert not p.exists()
data = dict(
    reviewedAt=datetime.now(timezone.utc).isoformat(),
    actualExtraction=dict(chunk='e6367d', exitCode=0, closure='41b30b', pid=71768, workerDead=True),
    all36DisplayedNativeSamplesDirectlyRead=True, all8BoardsDirectlyRead=True,
    freshSamples=15, reusedShaBoundSamples=21,
    evidence=m['samples'] + m['boards'], sourceHashes=m['sources'],
    nativeWindow=dict(nativeIn=4770, nativeOutExclusive=5802, seconds=[79.5,96.7], frames=1032),
    findings=[
        '79.5–82.5 is a new flight after the earlier respawn: body approaches grey/green structures.',
        '83–84.5 body is too dark/small against foreground structures; hide uncertain guides.',
        '85–86.5 silhouette is visible against a bright gap; screen inclination changes, without a measured rigid roll.',
        '87–89 approaches a framed hole; hide the foreground-occluded comparison instead of interpolating through it.',
        '89–90.5 body is visible near the Awesome +2000 score; guide must avoid that UI.',
        '92.5–94.5 dark body/cliff requires conservative guide hiding; later body is visible against a bright strip.',
        'No death/respawn or world change appears in the 36 inspected native samples within this window.'
    ],
    conservativeGuideHideSeconds=[[83,85],[87.5,89],[92.5,94.5]],
    normalPlayback=dict(tabId='107', requested=[79.5,96.7], actualSeek=79.501744,
                        actualPause=96.777169, speed=1, muted=True, boundedEndpointsOnly=True),
    rejectedLateTrail=dict(tabId='104', requested=[735.5,751.5], actualSeek=735.500519,
                           actualPause=751.738628, finding='Crossfade into orange branded outro; no gameplay bank adopted.', extraction=0),
    sourcePlanningBounded=True, sourceContinuousCandidate=True,
    allBetweenFramesApproved=False, physicalCentroidApproved=False,
    engineWorldAxesApproved=False, rigidRollMeasured=False,
    finalNativeAllocationApproved=False, narrationTimedApproved=False,
    finalRatioApproved=False, humanListeningApproved=False, publicRightsApproved=False, newImageGit=0)
save(p, data)
cp = read(O / 'latest-checkpoint.json')
cp.update(recordedAt=data['reviewedAt'], stage='measured-native-allocation-and-tracking-preparation',
          additionalNativeReview=p.relative_to(ROOT).as_posix(), activeOwnedWorkers=0, ownedJob=None,
          currentAsrHeldParagraphs=[], currentUnmixedAsrApproved=True,
          next='Use source79.5–96.7 conditional bank with occlusion hiding, and measured current voice to allocate four-game scenes. Preserve all completed TTS/ASR/Manim/native audits. Current34 mix, final captions/pixels/ratio/delivery remain false.')
save(O / 'latest-checkpoint.json', cp)
qp = B / 'queue.json'; before = qp.read_bytes(); q = read(qp)
q['currentOrientationReview'].update(stage=cp['stage'], additionalNativeReview=cp['additionalNativeReview'],
                                   activeOwnedWorkers=0, ownedJob=None, heldParagraphs=[],
                                   currentUnmixedAsrApproved=True, next=cp['next'])
q['updatedAt'] = data['reviewedAt']; assert qp.read_bytes() == before; save(qp,q)
print(json.dumps(dict(samples=36, boards=8, exactHashes=True, workerDead=True, finalRatioApproved=False)))
