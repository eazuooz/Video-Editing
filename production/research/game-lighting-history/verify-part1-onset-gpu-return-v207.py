"""Verify the exact idle-GPU handoff after the two-take batch exits."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ep=BASE/'part1-onset-repairs-tts-execution-v199.json';e=read(ep);token=e['leaseToken']
hp=ROOT/'shared/output/gpu-handoff'/(token+'.json');h=read(hp);out=BASE/'part1-onset-gpu-return-v207.json'
if out.exists():raise RuntimeError('Preserve verification')
if e.get('exitCode')!=0 or not e.get('endedAt') or not e.get('generationComplete') or [r['id'] for r in e['results']]!=['runtime-texture-size','geometry-car-material']:raise RuntimeError('Exact successful two-take batch required')
if h['token']!=token or h['state']!='tts_process_exiting' or not h.get('idleGpu') or h.get('queueDir') is not None:raise RuntimeError('Inspect non-idle research handoff separately')
ident=e['actualIdentity']
if h['coordinator']!={k:ident[k] for k in ['pid','createTime']}:raise RuntimeError('Lease owner mismatch')
if psutil.pid_exists(ident['pid']):
 p=psutil.Process(ident['pid'])
 if abs(p.create_time()-ident['createTime'])<.01 and p.cmdline()==ident['command']:raise RuntimeError('Exact TTS owner still alive')
if (ROOT/'shared/output/GPU_HANDOFF.json').exists():raise RuntimeError('An actual GPU lease remains; preserve it')
qp=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json');q=read(qp)
if q.get('status')!='complete_pending_visual_review' or q.get('completed')!=1088 or q.get('total')!=1088:raise RuntimeError('Research completion changed')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW)
name,used,free,util=[x.strip() for x in gpu.splitlines()[0].split(',')]
if int(free)<18000 or int(util)>=15:raise RuntimeError('GPU return not yet observed')
stamp=datetime.now(timezone.utc).isoformat()
r=dict(observedAt=stamp,execution=dict(path=ep.relative_to(ROOT).as_posix(),sha256=sha(ep)),leaseToken=token,endedWorkerIdentity=ident,identityStillLive=False,session=13934,sessionObservedClosedExitCode=0,activeLeaseExists=False,gpu=dict(name=name,usedMiB=int(used),freeMiB=int(free),utilization=int(util)),availableRamBytes=psutil.virtual_memory().available,researchStatus=dict(path=str(qp),sha256=sha(qp),observed=q),researchWasPausedByThisLease=False,researchRestarted=False,verificationMode='idle-GPU-return-after-natural-research-completion',selectedRepairs=e['results'],next='Select35 preserved takes and these2 new takes. Recognize only the five affected whole/complete-context windows.',allAsrApproved=False,uploaded=False)
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
h.update(previousState='tts_process_exiting',state='research_resume_verified',ttsExitCode=0,verifiedAt=stamp,verificationMode=r['verificationMode'],researchWasPaused=False,researchRestarted=False,postExitObservation=dict(path=out.relative_to(ROOT).as_posix(),sha256=sha(out)))
tmp=hp.with_name(hp.name+'.verification-'+str(os.getpid()));tmp.write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,hp)
print(json.dumps(dict(verifiedOwnLease=token,endedWorker=ident['pid'],researchNaturallyComplete=True,researchRestarted=False,freeMiB=int(free))))
