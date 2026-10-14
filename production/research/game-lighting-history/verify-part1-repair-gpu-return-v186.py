"""Verify this exact ended idle-GPU lease; never restart naturally completed research."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,subprocess,psutil
root=Path(__file__).resolve().parents[3]
base=root/'projects/game-lighting-history-04/production'
ep=base/'part1-scoped-repair-tts-execution-v176.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e=read(ep);token='0a6f16a9-f147-485c-9b3b-1fb57a3002c9'
hp=root/'shared/output/gpu-handoff'/(token+'.json');h=read(hp)
out=base/'part1-post-repair-resource-v186.json'
if out.exists():raise RuntimeError('Preserve verification')
if e['leaseToken']!=token or not e.get('endedAt') or e['exitCode']!=0 or len(e['results'])!=2 or not e.get('generationComplete'):raise RuntimeError('Unexpected limited repair batch')
if h['token']!=token or h['state']!='tts_process_exiting' or not h.get('idleGpu') or h.get('queueDir') is not None:raise RuntimeError('Only this exact idle-GPU exit may be verified')
if h['coordinator']!={k:e['actualIdentity'][k] for k in ['pid','createTime']}:raise RuntimeError('Lease identity mismatch')
identity=e['actualIdentity'];live=False
if psutil.pid_exists(identity['pid']):
 p=psutil.Process(identity['pid'])
 live=abs(p.create_time()-identity['createTime'])<.01 and p.cmdline()==identity['command']
if live or (root/'shared/output/GPU_HANDOFF.json').exists():raise RuntimeError('Ended owner and no current lease required')
queue=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json');q=read(queue)
if q.get('status')!='complete_pending_visual_review' or q.get('completed')!=q.get('total') or q.get('total')!=1088:raise RuntimeError('Research completion changed; inspect rather than assume restoration')
raw=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW)
name,used,free,util=[s.strip() for s in raw.splitlines()[0].split(',')]
if int(free)<18000 or int(util)>=15:raise RuntimeError('GPU is not idle enough for the next exclusive job')
processes=[]
for p in psutil.process_iter(['pid','name','cmdline','create_time']):
 try:
  if 'python' in (p.info['name'] or '').lower() or 'ffmpeg' in (p.info['name'] or '').lower():processes.append(p.info)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
for p in processes:
 c=' '.join(p.get('cmdline') or []).lower()
 if any(x in c for x in ['train_v2.py','placement_focus','render-part1-guided-actions-v169.py','render-part1-scoped-repair-v176.py']) and p['pid']!=os.getpid():raise RuntimeError('Another relevant worker remains live; preserve it')
stamp=datetime.now(timezone.utc).isoformat()
r=dict(observedAt=stamp,originalExecution=dict(path=ep.relative_to(root).as_posix(),sha256=sha(ep)),originalLease=dict(path=hp.relative_to(root).as_posix(),sha256BeforeVerification=sha(hp)),endedWorkerIdentity=identity,identityStillLive=False,activeLeaseExists=False,gpu=dict(name=name,usedMiB=int(used),freeMiB=int(free),utilization=int(util)),availableRamBytes=psutil.virtual_memory().available,researchStatus=dict(path=str(queue),sha256=sha(queue),observed=q),foreignPythonOrFfmpeg=processes,researchWasPausedByThisLease=False,researchRestarted=False,verificationMode='idle-GPU-return-after-natural-research-completion',technicalFailedIds=[x['id'] for x in e['results'] if not x['technicalTailGatePassed']],next='Select35 retained takes and these2 successful repairs for current37 full/context ASR.',allAsrApproved=False,uploaded=False)
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
h.update(previousState='tts_process_exiting',state='research_resume_verified',ttsExitCode=e['exitCode'],verifiedAt=stamp,verificationMode=r['verificationMode'],researchWasPaused=False,researchRestarted=False,postExitObservation=dict(path=out.relative_to(root).as_posix(),sha256=sha(out)))
tmp=hp.with_name(hp.name+'.verification-'+str(os.getpid()));tmp.write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,hp)
print(json.dumps(dict(verifiedOwnLease=token,endedWorker=identity['pid'],researchNaturallyComplete=True,researchRestarted=False,freeMiB=int(free),selectedRepairedIds=[x['id'] for x in e['results']]),ensure_ascii=False))
