"""Select four passed takes and one scoped retry, with both actual research resumes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
binding=lambda p:dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
oldp=BASE/'native-followup-execution-v121.json';newp=BASE/'native-tail-execution-v126.json'
old=read(oldp);new=read(newp);req=read(BASE/'native-tail-request-v126.json')
if not new['generationComplete'] or new['exitCode']!=0:raise RuntimeError('Retry incomplete')
results=[x for x in old['results'] if x['technicalTailGatePassed']]+new['results']
if len(results)!=5 or not all(x['technicalTailGatePassed'] for x in results):raise RuntimeError('Five individual passes required')
for x in [req['script'],req['sourceReview'],req['currentDuplicateReview'],*req['protectedInputs'],*req['existingSelectedTakeFiles'],*results]:
    if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected file changed '+x['path'])
histories=[]
for execution in [old,new]:
    p=ROOT/'shared/output/gpu-handoff'/(execution['leaseToken']+'.json');h=read(p)
    if h['state']!='research_resume_verified':raise RuntimeError('Unverified research restore')
    original=h['queueOwner'];resumed=h['resumedQueue']
    if original['command']!=resumed['command'] or original['cwd']!=resumed['cwd']:raise RuntimeError('Research command/cwd changed')
    if execution is new:
        worker=psutil.Process(resumed['pid'])
        if abs(worker.create_time()-resumed['createTime'])>.01:raise RuntimeError('Resumed identity changed')
        status=read(Path(h['queueDir'])/'status.json')
        if status['owner_pid']!=worker.pid or status['status'] not in ['waiting_for_resources','running']:raise RuntimeError('Queue not live')
    histories.append(dict(**binding(p),state=h['state'],ttsExitCode=h['ttsExitCode'],resumedQueue=resumed,resumedStatus=h['resumedStatus']['status']))
lease=ROOT/'shared/output/GPU_HANDOFF.json'
if lease.exists() and read(lease)['token'] in [old['leaseToken'],new['leaseToken']]:raise RuntimeError('Owned lease remains')
out=BASE/'native-followup-selected-v126.json'
if out.exists():raise RuntimeError('Preserve existing selection')
bindings=[binding(oldp),binding(newp),binding(BASE/'native-tail-request-v126.json'),req['script'],req['sourceReview'],req['currentDuplicateReview'],*req['protectedInputs'],*req['existingSelectedTakeFiles']]
record=dict(schemaVersion=1,selectedAt=datetime.now(timezone.utc).isoformat(),status='five-passed-takes-selected-awaiting-ten-direct-ASR-windows',results=results,bindings=bindings,researchHistories=histories,allOriginalSelectedPcmPreserved=True,failedTakePreserved=True,thresholdChanged=False,wholeAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False,uploaded=False)
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(selected=5,originalPcmPreserved=True,researchRestored=True,resumedPid=histories[-1]['resumedQueue']['pid'],asrApproved=False)))
