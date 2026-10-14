"""Seal actual CUA112 endpoints for the new current-caption clip, without replay."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--end',required=True);a=ap.parse_args();end=json.loads(a.end)
start=dict(time=.281643,duration=34.666667,rate=1,muted=True,paused=False,ended=False)
assert end['rate']==1 and end['muted'] and end['paused'] and end['ended']
assert abs(end['time']-34.666667)<.00001 and abs(end['duration']-34.666667)<.00001
sp=O/'current34-clearance-caption-bindings-execution-v1.json';s=rd(sp)
assert s['workerDead'] and s['actualOuterExitCode']==0
x=next(x for x in s['scenes'] if x['id']=='07b');assert sha(ROOT/x['output'])==x['outputSha256']
out=O/'07b-current-caption-clearance-normal-direct-review-v1.json';assert not out.exists()
r=dict(recordedAt=datetime.now(timezone.utc).isoformat(),tabId='112',browserId='3',url='http://127.0.0.1:9250/orientation-07b-current-caption-clearance-review-v1.html',
 execution=sp.relative_to(ROOT).as_posix(),executionSha256=sha(sp),source=x['output'],sourceSha256=x['outputSha256'],start=start,end=end,
 normal1xMutedStartEndActuallyObserved=True,noReplay=True,continuousListeningApproved=False,humanPronunciationApproved=False,allIntermediateFramesApproved=False,final244PixelsApproved=False,
 observation='CUA112 current-caption clip started once at0.281643 normal1xmute and reached actual34.666667 endpoint. Fullframe sharp reframe preserves wing/control context in125 selected samples; this is normal endpoint plus bounded-pixel review, not human listening or all intermediate frames.')
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(review=out.relative_to(ROOT).as_posix(),sha256=sha(out),normalEndpoints=True)))
