from pathlib import Path
from datetime import datetime,timezone
import json,os,psutil
root=Path(__file__).resolve().parents[3];b=root/'projects/game-lighting-history-04/production'
e=json.loads((b/'part1-scoped-repair-tts-execution-v176.json').read_text('utf-8'))
i=e['actualIdentity'];p=psutil.Process(i['pid'])
if abs(p.create_time()-i['createTime'])>.001 or p.cmdline()!=i['command'] or p.cwd()!=i['cwd']:raise RuntimeError('Actual live identity changed')
out=b/'part1-scoped-repair-session-v185.json'
if out.exists():raise RuntimeError('Preserve session observation')
r=dict(observedAt=datetime.now(timezone.utc).isoformat(),sessionId=2321,status=e['status'],actualIdentity=i,proxyParentPid=p.ppid(),identityObservedAlive=True,leaseToken=e['leaseToken'],cpuThreads=2,gpuJobs=1,log='projects/game-lighting-history-04/production/local/part1-scoped-repair-tts-v176.log',repairIds=['shadow-wheel-surface','outer-comparison-before'],preservedOtherTakes=35,originalSession=dict(id=86972,closed=True,exitCode=1,technicalFailedIds=['outer-comparison-before']),beforeModelRejectedPreparation=dict(reason='Idle lease archive was still tts_process_exiting; explicit post-exit resource and naturally-completed research verification was required.',newModelJobs=0,newPcm=0),next='Observe two actual takes and idle-GPU return; select current37 then74 CPU2 whole/complete-context windows. No final audio or pixels approved.',uploaded=False)
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=root/'production/research/game-lighting-history/checkpoint.json';c=json.loads(cp.read_text('utf-8-sig'))
c['status']='episode04-physical01-two-scoped-repairs-exclusive-TTS-v176';c['updatedAt']=r['observedAt']
c['ownedActiveWork']={**i,'sessionId':2321,'execution':'projects/game-lighting-history-04/production/part1-scoped-repair-tts-execution-v176.json','log':r['log'],'cpuThreads':2,'gpuJobs':1,'total':2,'completed':None,'next':r['next']}
c['episode04Part1ScopedSessionV185']=r
tmp=cp.with_name(cp.name+'.scoped185-'+str(os.getpid()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
print(json.dumps(dict(pid=i['pid'],session=2321,alive=True,total=2,preserved=35)))
