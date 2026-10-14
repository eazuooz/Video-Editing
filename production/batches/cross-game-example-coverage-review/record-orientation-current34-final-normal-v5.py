"""Record actual CUA start and end observations once for the new V5 file."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['start','end'],required=True);ap.add_argument('--tab',required=True);ap.add_argument('--observation',required=True);a=ap.parse_args()
x=json.loads(a.observation);assert x['rate']==1 and x['muted'] and abs(x['duration']-1098.616667)<.00001
sp=O/'current34-final-pair-execution-v5.json';s=rd(sp);assert s['workerDead'] and s['actualOuterExitCode']==0
startp=O/'current34-final-normal-start-observation-v5.json'
if a.stage=='start':
 assert not startp.exists() and not x['paused'] and not x['ended'] and 0<x['time']<1
 data=dict(recordedAt=datetime.now(timezone.utc).isoformat(),tabId=a.tab,browserId='3',url='http://127.0.0.1:9250/orientation-current34-final-review-v5.html',execution=sp.relative_to(ROOT).as_posix(),executionSha256=sha(sp),captionedVideo=s['pair'][1]['path'],captionedVideoSha256=s['pair'][1]['sha256'],start=x,noReplay=True)
 out=startp
else:
 start=rd(startp);assert start['tabId']==a.tab and start['executionSha256']==sha(sp)
 assert x['paused'] and x['ended'] and abs(x['time']-1098.616667)<.00001
 data=dict(**start,end=x,startObservation=startp.relative_to(ROOT).as_posix(),startObservationSha256=sha(startp),allNormalStartEndObserved=True,normalPlaybackEndpointsReviewed=True,continuousListeningApproved=False,humanPronunciationApproved=False,allIntermediateFramesApproved=False,final244CaptionPixelsApproved=False)
 data['recordedAt']=datetime.now(timezone.utc).isoformat();out=O/'current34-final-normal-direct-review-v5.json';assert not out.exists()
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(stage=a.stage,tab=a.tab,path=out.relative_to(ROOT).as_posix(),sha256=sha(out))))
