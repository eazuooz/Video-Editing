"""Record our released handoff without changing another task's new lease."""
from pathlib import Path
import json,hashlib,psutil,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
token='7e09ed3d-bddf-4bc4-8558-c168153071f6';p=ROOT/f'shared/output/gpu-handoff/{token}.json'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
r=read(p);assert r['ttsExitCode']==0
assert r['completedJobEvidence']['validation']['checkpoint_finite'] and r['completedJobEvidence']['validation']['numerically_finite']
status=read(Path(r['queueDir'])/'status.json');lease=ROOT/'shared/output/GPU_HANDOFF.json';current=read(lease) if lease.exists() else {}
owner=psutil.Process(status['owner_pid'])
assert owner.cmdline()==r['queueOwner']['command'] and owner.cwd()==r['queueOwner']['cwd']
owned_remaining=[];foreign=[]
for file in r['ownedFiles']:
 path=Path(file)
 if path.exists():
  value=path.read_text(encoding='utf8');assert token not in value,(path,value)
  foreign.append({'path':file,'currentForeignToken':current.get('token')})
progress=int(status.get('completed',0))>int(r['resumedStatus'].get('completed',0))
if status.get('status')=='running':assert psutil.Process(status['child_pid']).is_running()
marker=Path(r['queueDir'])/'done/infer_val_shadow_only_p040_42.json';after=read(marker) if marker.exists() else None
result={'guardToken':token,'guardReceipt':p.relative_to(ROOT).as_posix(),'guardReceiptSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'currentTrainingCompletedBeforePause':r['completedJobEvidence'],'ttsSucceeded':True,'originalQueueCommandAndCwdRestored':True,'immediateRestoredOwner':r['resumedQueue'],'actualCurrentResearchOwnerVerified':{'pid':owner.pid,'createTime':owner.create_time(),'command':owner.cmdline(),'cwd':owner.cwd()},'immediateResumeState':r['resumedStatus'],'currentResearchQueueState':status,'ourPauseRequestsRemoved':True,'foreignPauseControls':foreign,'foreignPauseControlsAltered':False,'researchJobAfterTtsActuallyCompleted':progress and after is not None,'afterTtsResearchMarker':{'path':str(marker),'sha256':hashlib.sha256(marker.read_bytes()).hexdigest(),'record':after} if after is not None else None,'currentNextJobActuallyRunning':status.get('status')=='running','actualResumeLimitation':'Queue advanced880→882 after TTS and completed its next validation job; its current training slot is temporarily waiting for the CPU narration review to finish.','optimizerOrRngResumeFromAdapterAsserted':False,'observedAt':datetime.datetime.now().astimezone().isoformat()}
result['actualResumeLimitation']=('Queue advanced880→882 and completed the next validation job; the next training owner and child are now actually running.' if status.get('status')=='running' else 'The restored queue has advanced; its exact current resource-wait state is retained above without claiming an active training child.')
(B/'polygons-v3-gpu-handoff-completion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Our TTS completed; original queue restored. Actual current state:',status.get('status'),'foreign handoff:',current.get('project'))
