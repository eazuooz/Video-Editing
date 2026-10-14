"""Seal the observed CUA start/end; never claim whole listening or every frame."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
startp = O / 'current34-final-normal-start-observation-v3.json'
start = read(startp)
pairp = ROOT / start['execution']
pair = read(pairp)
assert sha(pairp) == start['executionSha256']
assert pair['actualOuterExitCode'] == 0 and pair['workerDead']
assert start['tabId'] == '110' and start['start']['rate'] == 1
assert start['start']['muted'] and not start['start']['paused']
assert not start['start']['ended'] and 0 < start['start']['time'] < 1
out = O / 'current34-final-normal-direct-review-v3.json'
assert not out.exists()
end = dict(duration=1098.616667, ended=True, muted=True, paused=True,
           rate=1, time=1098.616667)
data = dict(recordedAt=datetime.now(timezone.utc).isoformat(),
            tabId='110', browserId='3', url=start['url'],
            execution=rel(pairp), executionSha256=sha(pairp),
            startObservation=rel(startp), startObservationSha256=sha(startp),
            start=start['start'], end=end,
            allNormalStartEndObserved=True, normalPlaybackEndpointsReviewed=True,
            observations='CUA110 existing vfinal video observed from running 0.148177 to ended 1098.616667 at rate1/muted, with no replay. Actual final assembled captioned media endpoint observation; not continuous listening or review of every intermediate frame.',
            continuousListeningApproved=False, humanPronunciationApproved=False,
            allIntermediateFramesApproved=False, final244CaptionPixelsApproved=False)
out.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(review=rel(out), sha256=sha(out), normalEndpoints=True,
                      finalPixelApproval=False)))
