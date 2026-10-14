"""Record actual start/end once for newly repaired06a, without replay."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['start','end'],required=True);ap.add_argument('--tab',required=True);ap.add_argument('--observation',required=True);a=ap.parse_args()
x=json.loads(a.observation);assert x['rate']==1 and x['muted'] and abs(x['duration']-12.65)<.00001
sp=O/'current34-06a-caption-clearance-execution-v1.json';s=rd(sp);assert s['workerDead'] and s['actualOuterExitCode']==0
startp=O/'06a-current-caption-clearance-normal-start-v1.json'
if a.stage=='start':
 assert not startp.exists() and not x['paused'] and not x['ended'] and 0<x['time']<1
 data=dict(recordedAt=datetime.now(timezone.utc).isoformat(),tabId=a.tab,browserId='3',execution=sp.relative_to(ROOT).as_posix(),executionSha256=sha(sp),start=x,noReplay=True);out=startp
else:
 start=rd(startp);assert start['tabId']==a.tab and start['executionSha256']==sha(sp) and x['paused'] and x['ended'] and abs(x['time']-12.65)<.00001
 data=dict(**start,end=x,normal1xMutedStartEndActuallyObserved=True,allIntermediateFramesApproved=False,humanListeningApproved=False,final244CaptionPixelsApproved=False);out=O/'06a-current-caption-clearance-normal-direct-review-v1.json';assert not out.exists()
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(dict(stage=a.stage,path=out.relative_to(ROOT).as_posix(),sha256=sha(out))))
