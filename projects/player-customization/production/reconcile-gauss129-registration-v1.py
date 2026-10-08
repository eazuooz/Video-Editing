"""Complete the record-only registration after a schema mismatch; no media work."""
from pathlib import Path
from datetime import datetime, timezone
import json, os, time
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig')); now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
    for retry in range(40):
        try:os.replace(t,p);return
        except OSError:
            if retry==39:raise
            time.sleep(.15)
rp=BASE/'gauss129-public-source-review-v1.json'; record=read(rp)
assert record['sourceVideoId']=='h7qntXMufKk' and not (BASE/'gauss129-acquisition-execution-v1.json').exists()
cp_path=BASE/'latest-checkpoint.json';cp=read(cp_path)
candidate_path=ROOT/'projects/player-customization/sources/game-candidates.json';c=read(candidate_path)
assert isinstance(c['additionalOfficialProfiles'],dict)
c['additionalOfficialProfiles']['freshGauss129Research']=record;c['reviewedAt']=now();save(candidate_path,c)
cp['ownedJob']['status']='exact-yareli155-crops-directly-reviewed-completed'
cp.update(recordedAt=now(),gauss129PublicSourceReview=rp.relative_to(ROOT).as_posix(),
    gauss129PreparationRecovery=dict(originalExitCode=1,reason='Existing additionalOfficialProfiles is a dict, not a list. Three prepared files preserved; record-only registration resumed.',mediaStartedBeforeFailure=False,observedAt=now()),
    nextAction='Acquire the newly observed official Gauss129 source once after current resource check; completed Yareli155152 crops and all prior voice/white/native work are preserved. Final allocation and all final media gates remain false.')
save(cp_path,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization')
i.update(currentExecution=cp['ownedJob'],gauss129PublicSourceReview=cp['gauss129PublicSourceReview'],nextAction=cp['nextAction'],gauss129PreparationRecovery=cp['gauss129PreparationRecovery']);q['updatedAt']=now();save(qp,q)
print(json.dumps(dict(sourceRegistered=record['sourceVideoId'],mediaStarted=False,preservedPreparedFiles=3)))
