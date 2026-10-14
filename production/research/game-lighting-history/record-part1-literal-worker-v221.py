from pathlib import Path
import json,os,datetime,psutil
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'projects/game-lighting-history-04/production'
ep=B/'part1-literal-onset-asr-execution-v220.json';e=json.loads(ep.read_text('utf-8-sig'))
identity=e['actualIdentity'];alive=False
if psutil.pid_exists(identity['pid']):
 p=psutil.Process(identity['pid']);alive=abs(p.create_time()-identity['createTime'])<.1 and p.cmdline()==identity['command']
if not alive and not e.get('endedAt'):raise RuntimeError('Unobserved worker failure')
r=dict(observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),execution=ep.relative_to(ROOT).as_posix(),log=ep.relative_to(ROOT).as_posix(),actualIdentity=identity,alive=alive,sessionId=26428,cpuThreads=2,gpuJobs=0,completed=len(e['completed']),expectedWindows=5,status=e['status'],exitCode=e.get('exitCode'),approved=False,next='Directly read every full actual/expected sentence and timestamp in five changed contexts; reuse unchanged69 results.')
out=B/'part1-literal-worker-observation-v221.json';assert not out.exists();out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=json.loads(cp.read_text('utf-8-sig'))
c.update(updatedAt=r['observedAt'],status='episode04-physical01-five-literal-contexts-CPU-review-v220',ownedActiveWork=r if alive else None)
c['episode04Part1LiteralWorkerV221']=r
tmp=cp.with_name(cp.name+'.221-'+str(os.getpid()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
print(json.dumps({k:r[k]for k in ['alive','sessionId','completed','exitCode']}))
