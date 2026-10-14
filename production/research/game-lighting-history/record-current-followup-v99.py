"""Observe actual v98 identities/lease only; never manipulate GPU/research."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def ref(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def identity(p):
    try:return dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),exe=p.exe())
    except (psutil.NoSuchProcess,psutil.AccessDenied):return None
ep=BASE/'guided-followup-current-execution-v98.json';e=read(ep) if ep.exists() else None
lp=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(lp) if lp.exists() else None
history=None
if e:
    hp=ROOT/'shared/output/gpu-handoff'/f"{e['leaseToken']}.json"
    history=read(hp) if hp.exists() else None
elif lease and lease.get('project')=='game-lighting-history-04' and any(str(x).endswith('render-guided-followup-current-v98.py') for x in lease.get('ttsCommand',[])):
    hp=ROOT/'shared/output/gpu-handoff'/f"{lease['token']}.json";history=read(hp) if hp.exists() else lease
processes=[]
for p in psutil.process_iter(['name','cmdline']):
    try:
        if p.info['name'].lower()=='python.exe' and any(str(x).endswith('render-guided-followup-current-v98.py') for x in p.info['cmdline'] or []):
            i=identity(p)
            if i:processes.append(i)
    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
status=e.get('status') if e else history.get('state') if history else 'waiting-for-foreign-exclusive-handoff' if lease else 'waiting-for-owned-handoff-observation'
if history and history.get('state')=='research_resume_verified':status='technical-followup-complete; research-restored; ASR-pending' if e and e.get('generationComplete') else 'followup-failed-preserved; research-restored'
record=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),status=status,sessionId=78913,execution=ref(ep) if e else None,liveOwnedProcesses=processes,ownedLease=history,foreignLease=({k:lease.get(k) for k in ['token','project','state','coordinator']} if lease and lease.get('project')!='game-lighting-history-04' else None),completedChildJobs=e.get('jobs',[]) if e else [],currentChild=e.get('currentChild') if e else None,generationComplete=bool(e and e.get('generationComplete')),researchRestorationObserved=bool(history and history.get('state')=='research_resume_verified'),cpuThreads=e.get('cpuThreads',0) if e and not e.get('endedAt') else 0,gpuJobs=e.get('gpuJobs',0) if e and not e.get('endedAt') else 0,wholeAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False,allFinalPixelsReviewed=False,bodyRatioApproved=False,collected=False,uploaded=False,next='Complete only4 scoped retakes+6 Hogwarts observations, verify research restoration, select37+6, measure source capacity, review86 whole/context ASR windows, then current classified native/moving annotation production.')
out=BASE/'guided-followup-current-progress-v99.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(cp);c['episode04GuidedFollowupCurrentV98']={k:record[k] for k in ['status','sessionId','currentChild','generationComplete','researchRestorationObserved','cpuThreads','gpuJobs','next']};c['episode04GuidedFollowupCurrentV98']['record']=out.relative_to(ROOT).as_posix();c['updatedAt']=record['observedAt']
tmp=cp.with_name(cp.name+'.observing-'+str(os.getpid()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
print(json.dumps(dict(output=out.relative_to(ROOT).as_posix(),status=status,children=len(record['completedChildJobs']),researchRestorationObserved=record['researchRestorationObserved'],uploaded=False)))
