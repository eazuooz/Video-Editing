"""Verify the repaired actual mix exit, hashes and protected PCM without controls."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
import psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--session',type=int,required=True);ap.add_argument('--outer-exit',type=int,required=True);ap.add_argument('--completion',required=True);a=ap.parse_args()
sp=R/'current-mix-execution-v2.json';ss=R/'current-mix-execution-v2.session.json';s=read(sp);v=read(ss)
assert v['sessionId']==s['sessionId']==a.session and v['actualOuterExitCode'] is None and s['actualExitCode']==a.outer_exit
assert v['pid']==s['pid'] and abs(v['createTime']-s['createTime'])<.01
try:assert abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01
except psutil.NoSuchProcess:pass
assert a.outer_exit==0 and s['all17RawPcmPlacementsExact'] and s['all71ProtectedInputsUnchanged']
assert sha(ROOT/s['plan'])==s['planSha256'] and read(ROOT/s['plan'])['sourceFirstParagraphPlacementRepaired']
for row in s['files']+s['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256']
v.update(actualOuterExitCode=a.outer_exit,actualCompletion=a.completion,workerCurrentlyAlive=False,verifiedAt=datetime.now(timezone.utc).isoformat())
t=ss.with_name(ss.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,ss)
out=R/'current17-mix-actual-exit-verification-v2.json';assert not out.exists()
out.write_text(json.dumps(dict(**v,totalFrames=s['totalFrames'],seconds=s['seconds'],decodedAacSha256=s['decodedAacSha256'],files=s['files'],all71ProtectedShaMatched=True,all17PcmBytePlacementsMatched=True,sourceFirstOnsetPlacementRepaired=True,aacDecodedLufs=s['aacDecodedMeasurement']['input_i'],aacDecodedTruePeak=s['aacDecodedMeasurement']['input_tp'],currentMixedAudioDirectReviewApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=v['verifiedAt'],activeOwnedWorkers=0,currentMixActualExitVerification=out.name,stage='current17-repaired-mix-actual-exit0-current-whole-ASR-pending',ownedJob=dict(active=False,pid=s['pid'],createTime=s['createTime'],sessionId=a.session,actualOuterExitCode=a.outer_exit,actualCompletion=a.completion),currentMixedAudioApproved=False)
temp=R/'latest-checkpoint.json.writing';temp.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,R/'latest-checkpoint.json')
print(json.dumps(dict(actualExit=0,frames=s['totalFrames'],decodedLufs=s['aacDecodedMeasurement']['input_i'],decodedTruePeak=s['aacDecodedMeasurement']['input_tp'],all17RawPcmExact=True,all71Protected=True,directAudioApproval=False)))
