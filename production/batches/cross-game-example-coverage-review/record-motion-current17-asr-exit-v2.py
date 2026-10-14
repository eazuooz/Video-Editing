"""Record observed outer exit and exact dead worker; never infer session completion."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
import psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['whole','contexts'],required=True);ap.add_argument('--session',type=int,required=True);ap.add_argument('--outer-exit',type=int,required=True);ap.add_argument('--completion',required=True);args=ap.parse_args()
sp=R/f'current17-mixed-{args.mode}-asr-execution-v2.json';ss=sp.with_name(sp.stem+'.session.json');state=read(sp);session=read(ss)
assert state['sessionId']==session['sessionId']==args.session and session['actualOuterExitCode'] is None
assert state['pid']==session['pid'] and abs(state['createTime']-session['createTime'])<.01
alive=False
try:alive=abs(psutil.Process(state['pid']).create_time()-state['createTime'])<.01
except psutil.NoSuchProcess:pass
assert not alive,'Only record actual closed worker.'
assert state['exitCode']==args.outer_exit
mix=read(R/'current-mix-execution-v2.json')
for v in mix['protectedInputs']:assert sha(ROOT/v['path'])==v['sha256']
assert state['decodedAacSha256']==mix['decodedAacSha256']==sha(ROOT/mix['decodedAac'])
if args.outer_exit==0:
 assert state['completed']==state['total']==(17 if args.mode=='whole' else 81)
 assert read(R/f'current17-mixed-{args.mode}-asr-v2/asr.json')['complete']
 for row in state['results']:
  assert sha(ROOT/row['contextPath'])==row['contextSha256'] and row['exactSourceStereoPcmBytesMatched']
session.update(actualOuterExitCode=args.outer_exit,actualCompletion=args.completion,workerCurrentlyAlive=False,verifiedAt=datetime.now(timezone.utc).isoformat(),all71ProtectedInputsUnchanged=True,decodedAacSha256=mix['decodedAacSha256'],directContentReviewPassed=False)
t=ss.with_name(ss.name+'.writing');t.write_text(json.dumps(session,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,ss)
print(json.dumps(dict(mode=args.mode,session=args.session,actualOuterExit=args.outer_exit,workerAlive=False,completed=state['completed'],all71Protected=True,directReview=False)))
