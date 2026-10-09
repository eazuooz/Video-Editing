"""Record only boards actually read; never infer pixel approval from files."""
import argparse, datetime, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROD = ROOT / 'projects/presenting-game-scores/production'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
ap=argparse.ArgumentParser()
ap.add_argument('--through', type=int, required=True)
a=ap.parse_args()
source=PROD/'selected-input-preflight-v8.json'
d=json.loads(source.read_text(encoding='utf-8'))
assert 1 <= a.through <= len(d['boards'])
boards=d['boards'][:a.through]
for b in boards:
    assert sha(ROOT/b['path']) == b['sha256'], b['path']
frames={f for b in boards for f in b['sampleFrames']}
samples=[s for s in d['samples'] if s['frame'] in frames]
for s in samples:
    assert sha(ROOT/s['path']) == s['sha256'], s['path']
progress=dict(schemaVersion=8, reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    source=str(source.relative_to(ROOT)).replace('\\','/'), sourceSha256=sha(source),
    planSha256=d['planSha256'], captionCandidateSha256=d['captionCandidateSha256'],
    bodySha256=d['bodySha256'], directlyReadBoardNumbers=list(range(1,a.through+1)),
    directlyReadBoardCount=len(boards), totalBoards=len(d['boards']),
    directlyReadSampleCount=len(samples), totalSamples=len(d['samples']), boards=boards,
    observations=['All six cells on each listed board directly read; last board may contain fewer cells.',
      'Fixed bottom-centre white/forest Korean captions readable; reviewed Tetris score, LINES, names, playfields and event labels remain visible.',
      'Reviewed black diagrams show projected front/top/side faces, spatial occlusion, height comparison, arrow/token motion and clear auxiliary-label/caption spacing.'],
    unresolvedIssues=[], allBoardsDirectlyRead=False, allInputCaptionPixelsReviewed=False,
    scope='Only the listed preflight cue/cut/clause-onset/spatial-motion samples; not every continuous native frame, final encoded pair or human listening.',
    allFinalPixels=False, finalMixedAsrApproved=False, qa=False, collected=False, private=False,
    localOnly=True, imagesGitAdded=0)
write(PROD/'selected-input-direct-progress-v8.json',progress)
e=PROD/'selected-input-preflight-execution-v8.json'
state=json.loads(e.read_text(encoding='utf-8'))
assert state['exitCode']==0 and state['sessionId']==38215
state.update(outerExitCode=0, outerExitDirectlyObserved=True, sessionClosed=True,
    outerExitObservation='write_stdin session38215 returned exit_code0 after worker completion; no repeated wait.',
    directReviewProgress='projects/presenting-game-scores/production/selected-input-direct-progress-v8.json')
write(e,state)
print(json.dumps({k:progress[k] for k in ['directlyReadBoardCount','directlyReadSampleCount','totalBoards','totalSamples']},ensure_ascii=False))
