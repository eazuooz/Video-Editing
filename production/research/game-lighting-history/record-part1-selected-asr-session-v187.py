"""Observe the single current CPU recognizer; preserve all other workers."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,psutil,hashlib
root=Path(__file__).resolve().parents[3]
b=root/'projects/game-lighting-history-04/production'
ep=b/'part1-selected-actions-asr-execution-v182.json'
e=json.loads(ep.read_text('utf-8-sig'));i=e['actualIdentity'];p=psutil.Process(i['pid'])
if abs(p.create_time()-i['createTime'])>.001 or p.cmdline()!=i['command'] or p.cwd()!=i['cwd']:raise RuntimeError('Actual live identity changed')
out=b/'part1-selected-asr-session-v187.json'
if out.exists():raise RuntimeError('Preserve session observation')
stamp=datetime.now(timezone.utc).isoformat()
r=dict(observedAt=stamp,sessionId=94890,status=e['status'],actualIdentity=i,proxyParentPid=p.ppid(),identityObservedAlive=True,cpuThreads=2,gpuJobs=0,total=74,completed=len(e['completed']),availableRamBytes=psutil.virtual_memory().available,log='projects/game-lighting-history-04/production/local/part1-selected-actions-asr-v182.log',execution=ep.relative_to(root).as_posix(),resourceBefore='projects/game-lighting-history-04/production/part1-post-repair-resource-v186.json',retainedTakes=35,repairedTakes=2,original111Repeated=False,fiveFramingRepeated=False,next='Directly compare74 current whole/complete-context texts and PCM before current final timing/mix/pixels.',allAsrApproved=False,uploaded=False)
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=root/'production/research/game-lighting-history/checkpoint.json';c=json.loads(cp.read_text('utf-8-sig'))
c.update(status='episode04-physical01-current37-CPU2-full-and-context-ASR-v182',updatedAt=stamp)
c['ownedActiveWork']={**i,'sessionId':94890,'execution':r['execution'],'log':r['log'],'cpuThreads':2,'gpuJobs':0,'total':74,'completed':r['completed'],'next':r['next']}
c['episode04Part1SelectedAsrSessionV187']=r
c['episode04Part1ScopedRepairsClosedV187']=dict(exitCode=0,generationComplete=True,sessionId=2321,closed=True,gpuReturned=True,verification='projects/game-lighting-history-04/production/part1-post-repair-resource-v186.json',researchRestarted=False)
tmp=cp.with_name(cp.name+'.selected187-'+str(os.getpid()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
print(json.dumps(dict(pid=i['pid'],session=94890,alive=True,total=74,completed=r['completed'],gpu=0)))
