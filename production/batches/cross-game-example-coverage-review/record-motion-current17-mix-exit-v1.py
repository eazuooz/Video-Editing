"""Verify actual mixer completion and preserve all protected PCM records."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
s=read(R/'current-mix-execution-v1.json');ss=read(R/'current-mix-execution-v1.session.json')
assert s['actualExitCode']==0 and s['pid']==ss['pid']==61276 and ss['sessionId']==99335
assert not psutil.pid_exists(s['pid']) or abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01
assert s['all17RawPcmPlacementsExact'] and s['all71ProtectedInputsUnchanged']
for row in s['files']+s['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256']
ss.update(actualOuterExitCode=0,actualCompletion='52d3af',workerCurrentlyAlive=False,verifiedAt=datetime.now(timezone.utc).isoformat());save(R/'current-mix-execution-v1.session.json',ss)
out=R/'current17-mix-actual-exit-verification-v1.json';assert not out.exists()
save(out,dict(**ss,totalFrames=s['totalFrames'],seconds=s['seconds'],decodedAacSha256=s['decodedAacSha256'],files=s['files'],all71ProtectedShaMatched=True,all17PcmBytePlacementsMatched=True,aacDecodedLufs=s['aacDecodedMeasurement']['input_i'],aacDecodedTruePeak=s['aacDecodedMeasurement']['input_tp'],currentMixedAudioDirectReviewApproved=False))
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=ss['verifiedAt'],activeOwnedWorkers=0,currentDuplicateCheckPassed=True,currentDuplicateReview='duplicate-content-and-studio-direct-review-v10.json',currentMixActualExitVerification=out.name,stage='current17-mix-actual-exit0-whole-ASR-pending',ownedJob=dict(active=False,pid=s['pid'],createTime=s['createTime'],sessionId=99335,actualOuterExitCode=0,actualCompletion='52d3af'))
save(R/'latest-checkpoint.json',cp)
print(json.dumps(dict(exitCode=0,totalFrames=s['totalFrames'],decodedLufs=s['aacDecodedMeasurement']['input_i'],directAudioApproval=False)))
