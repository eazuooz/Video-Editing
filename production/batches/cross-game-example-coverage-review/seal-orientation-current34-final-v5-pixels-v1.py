"""Record direct V5 readings and inherit only verified exact V4 pixel evidence."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os
ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for buf in iter(lambda: f.read(1048576), b''): h.update(buf)
    return h.hexdigest()
def save(p, v):
    t = p.with_name(p.name + '.writing')
    t.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(t, p)
ap = argparse.ArgumentParser()
ap.add_argument('--first', type=int, required=True)
ap.add_argument('--last', type=int, required=True)
ap.add_argument('--observation', required=True)
a = ap.parse_args()
sp = O / 'current34-pair-pixel-execution-v4.json'
s = rd(sp)
assert s['workerDead'] and s['actualOuterExitCode'] == 0
x = s['results'][0]
samples, boards, inherited = x['directReviewSamples'], x['boards'], x['inheritedExactPixelSamples']
assert len(samples) == 118 and len(boards) == 30 and len(inherited) == 3052
assert len(x['samples']) == len(samples) + len(inherited) == 3170
assert x['allSelectedEncodedPtsExact']
prior = rd(ROOT / s['priorCompleteReview'])
assert sha(ROOT / s['priorCompleteReview']) == s['priorCompleteReviewSha256']
assert prior['allNewDirectPixelsRead']
rp = O / 'current34-final-v5-pixels-partial-direct-review-v1.json'
if rp.exists():
    r = rd(rp)
    assert r['executionSha256'] == sha(sp)
else:
    r = dict(recordedAt=now(), execution=rel(sp), executionSha256=sha(sp),
             pairExecution=s['pairExecution'], pairExecutionSha256=s['pairExecutionSha256'],
             captionedVideo=x['video'], captionedVideoSha256=x['videoSha256'],
             totalSelectedSamples=len(x['samples']), totalNewDirectSamples=len(samples),
             totalNewDirectBoards=len(boards), inheritedExactPixelSampleCount=len(inherited),
             priorCompleteReview=s['priorCompleteReview'],
             priorCompleteReviewSha256=s['priorCompleteReviewSha256'], chunks=[],
             reviewedBoards=[], reviewedSamples=[], boardsDirectlyRead=0,
             samplesDirectlyRead=0, nextBoard=1, allNewDirectPixelsRead=False,
             all244CuePixelsApproved=False, allFinalSelectedSamplesApproved=False,
             allIntermediateFramesApproved=False, humanListeningApproved=False,
             publicRightsApproved=False,
             scope='Actual V5 output: changed06a, differing GOP pixels and all piece boundaries directly read;3052 cached V4 samples inherited only after exact decoded RGB comparison. No prior sample redisplay.')
assert a.first == r['nextBoard'] and a.first <= a.last <= len(boards)
for i in range(a.first - 1, a.last):
    board = boards[i]
    assert sha(ROOT / board['path']) == board['sha256']
    r['reviewedBoards'].append(board)
    for sample in samples[i*4:i*4+4]:
        assert sample['pts'] == sample['frame'] * 1500
        assert sha(ROOT / sample['path']) == sample['sha256']
        r['reviewedSamples'].append(sample)
r['chunks'].append(dict(recordedAt=now(), firstBoard=a.first, lastBoard=a.last,
                        observation=a.observation, boundedNewSelectedPixelsDirectlyRead=True))
r.update(recordedAt=now(), boardsDirectlyRead=len(r['reviewedBoards']),
         samplesDirectlyRead=len(r['reviewedSamples']), nextBoard=a.last+1,
         allNewDirectPixelsRead=a.last == len(boards))
save(rp, r)
cp = rd(O / 'latest-checkpoint.json')
cp.update(recordedAt=r['recordedAt'], stage='current34-final-v5-new-pixels-direct-review',
          activeOwnedWorkers=0, ownedJob=None, currentFinalV5PixelReview=rel(rp),
          finalV5BoardsReviewed=r['boardsDirectlyRead'], finalV5SamplesReviewed=r['samplesDirectlyRead'],
          next=('Bind repaired06a normal and unchanged36 normal evidence;seal final pixel/ratio/technical proof;then explicit root backup/promotion,4outputs,private settings,Git,current09schedule replacement.'
                if r['allNewDirectPixelsRead'] else f'Continue only new finalV5 direct board{r["nextBoard"]};3052 cached prior exact pixels preserved without redisplay.'))
save(O / 'latest-checkpoint.json', cp)
qp = B / 'queue.json'
raw = qp.read_bytes()
q = rd(qp)
q['currentOrientationReview'].update(stage=cp['stage'], activeOwnedWorkers=0, ownedJob=None,
    currentFinalV5PixelReview=rel(rp), finalV5BoardsReviewed=r['boardsDirectlyRead'],
    finalV5SamplesReviewed=r['samplesDirectlyRead'], next=cp['next'])
q['updatedAt'] = r['recordedAt']
assert qp.read_bytes() == raw
save(qp, q)
print(json.dumps(dict(boards=r['boardsDirectlyRead'], samples=r['samplesDirectlyRead'],
                     totalBoards=len(boards), inheritedExact=len(inherited), nextBoard=r['nextBoard'])))
