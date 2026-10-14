from pathlib import Path
import json,os,psutil,datetime
root=Path(__file__).resolve().parents[3]
ep=root/'production/research/game-lighting-history/local/part1-spatial-bank-v206/renders/episode04-part1-spatial-bank-v206.execution.json'
e=json.loads(ep.read_text('utf-8-sig'))
alive=psutil.pid_exists(e['ffmpegPid'])
if alive:
 p=psutil.Process(e['ffmpegPid'])
 if not p.name().lower().startswith('ffmpeg') or 'part1-spatial-bank-v206' not in ' '.join(p.cmdline()) or e['status']!='rendering':raise RuntimeError('Actual owned source-render identity required')
 i=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd())
else:
 if e.get('status')!='complete' or e.get('exitCode')!=0:raise RuntimeError('Closed renderer without successful execution')
 i=dict(pid=e['ffmpegPid'],command=e['command'],createTime=None,creationTimeNotIndependentlyRecorded=True)
r=dict(observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),actualIdentity=i,identityObservedAlive=alive,serverPid=e['serverPid'],serverSessionId=52569,execution=ep.relative_to(root).as_posix(),log=ep.relative_to(root).as_posix(),cpuThreads=2,gpuJobs=0,frames=4653,scenes=10,rendering=alive,rendererExitCode=e.get('exitCode'),previousLiveObservationAttempt='Exact recorded ffmpeg PID had already exited before this observer; no false live identity record was created.',allMovingPixelsReviewed=False,uploaded=False)
out=root/'projects/game-lighting-history-04/production/part1-spatial-render-live-v215.json'
if out.exists():raise RuntimeError('Preserve observation')
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=root/'production/research/game-lighting-history/checkpoint.json';c=json.loads(cp.read_text('utf-8-sig'))
c.update(status='episode04-physical01-10-black-spatial-source-scenes-rendered-probe-pixels-pending-v206',updatedAt=r['observedAt'],ownedActiveWork=({**i,'serverSessionId':52569,'serverPid':e['serverPid'],'execution':r['execution'],'log':r['log'],'cpuThreads':2,'gpuJobs':0} if alive else None))
c['episode04Part1SpatialSourceV215']=r
c['episode04Part1ProtectedOnsetsV211Closed']={'sessionId':18914,'sessionClosed':True,'exitCode':1,'execution':'projects/game-lighting-history-04/production/part1-protected-onsets-tts-execution-v211.json','gpuReturn':'projects/game-lighting-history-04/production/part1-protected-onsets-gpu-return-v213.json','preservedTakes':2,'failedTailIds':['geometry-car-material'],'currentApproval':False}
tmp=cp.with_name(cp.name+'.render215-'+str(os.getpid()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
print(json.dumps({'pid':e['ffmpegPid'],'alive':alive,'serverSession':52569,'frames':4653,'gpu':0}))
