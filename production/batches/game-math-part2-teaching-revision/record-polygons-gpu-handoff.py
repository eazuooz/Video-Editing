"""Verify sealed boundary and actual resumed job without controlling foreign work."""
from pathlib import Path
import json,hashlib,psutil,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
token='9c49398b-1fdb-43f0-9fe3-7659182af06c';file=ROOT/f'shared/output/gpu-handoff/{token}.json'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
r=read(file);status=read(Path(r['queueDir'])/'status.json')
assert r['ttsExitCode']==0 and status['status']=='running' and status['owner_pid']==r['resumedQueue']['pid']
owner=psutil.Process(status['owner_pid']);child=psutil.Process(status['child_pid'])
assert abs(owner.create_time()-r['resumedQueue']['createTime'])<.01 and child.is_running()
assert owner.cmdline()==r['queueOwner']['command'] and owner.cwd()==r['queueOwner']['cwd']
for p in r['ownedFiles']:assert not Path(p).exists(),p
result={'guardToken':token,'guardReceipt':file.relative_to(ROOT).as_posix(),'guardReceiptSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'currentTrainingCompletedBeforePause':r['completedJobEvidence'],'ttsSucceeded':True,'originalCommandAndCwdRestored':True,'immediateResume':r['resumedStatus'],'finalActualResearchResume':status,'actualRunningOwnerAndChildVerified':True,'ownedPauseRequestsRemoved':True,'foreignPauseControlsRemoved':False,'optimizerOrRngResumeFromAdapterAsserted':False,'observedAt':datetime.datetime.now().astimezone().isoformat()}
(B/'polygons-v2-gpu-handoff-completion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Actual resumed research owner/child:',status['owner_pid'],status['child_pid'],status['job'])
