"""Observe the owned one-take repair without manipulating any lease/research job."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
ref=lambda p:dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
ep=BASE/'hogwarts-tail-execution-v105.json';e=read(ep) if ep.exists() else None
lp=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(lp) if lp.exists() else None
h=None
if e:
 hp=ROOT/'shared/output/gpu-handoff'/f"{e['leaseToken']}.json";h=read(hp) if hp.exists() else None
elif lease and lease.get('project')=='game-lighting-history-04' and any(str(x).endswith('render-hogwarts-tail-v105.py') for x in lease.get('ttsCommand',[])):
 hp=ROOT/'shared/output/gpu-handoff'/f"{lease['token']}.json";h=read(hp) if hp.exists() else lease
live=[]
for p in psutil.process_iter(['name','cmdline']):
 try:
  if p.info['name'].lower()=='python.exe' and any(str(x).endswith('render-hogwarts-tail-v105.py') for x in p.info['cmdline'] or []):live.append(dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),exe=p.exe()))
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
restored=bool(h and h.get('state')=='research_resume_verified');complete=bool(e and e.get('generationComplete'))
status=e.get('status') if e else h.get('state') if h else 'waiting-for-owned-handoff'
if restored:status='single-retake-technically-complete; research-restored; ASR-pending' if complete else 'single-retake-failed-preserved; research-restored'
j=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),sessionId=63765,status=status,execution=ref(ep) if e else None,liveOwnedProcesses=live,ownedLease=h,generationComplete=complete,researchRestorationObserved=restored,cpuThreads=2 if e and not e.get('endedAt') else 0,gpuJobs=1 if e and not e.get('endedAt') else 0,wholeAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False,allFinalPixelsReviewed=False,bodyRatioApproved=False,uploaded=False,next='Select only five passing originals plus the scoped courtyard retake, then recognize43 whole paragraphs and43 complete joins once on CPU2/GPU0; preserve all historical takes.')
out=BASE/'hogwarts-tail-progress-v109.json';out.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(cp);c['episode04HogwartsTailV105']={k:j[k] for k in ['sessionId','status','liveOwnedProcesses','generationComplete','researchRestorationObserved','cpuThreads','gpuJobs','next']};c['episode04HogwartsTailV105']['record']=out.relative_to(ROOT).as_posix();c['updatedAt']=j['observedAt'];tmp=cp.with_name(cp.name+'.tail-observing-'+str(os.getpid()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
print(json.dumps(dict(output=out.relative_to(ROOT).as_posix(),status=status,generationComplete=complete,researchRestorationObserved=restored,uploaded=False)))
