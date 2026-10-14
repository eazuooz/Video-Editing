import json
from pathlib import Path
from datetime import datetime, timezone, timedelta, date

root=Path(__file__).resolve().parents[3]
now=datetime.now(timezone(timedelta(hours=9))).isoformat()
path=root/'production/batches/cross-game-example-coverage-review/queue.json'
q=json.loads(path.read_text(encoding='utf-8-sig'))
evidence='제작완료되면 확인해보고 퀄리티 기존꺼 삭제하고 새로만든걸로 바꿔줘 가까운 날짜것부터 진행해줘 그게 다끝나면 나머지 6개영상 진행해주면 돼!'
q['priorityInstruction']={'recordedAt':now,'userEvidence':evidence,'order':'closest-actual-future-scheduled-first','newSixStartOnlyAfterCurrentUploadReviewAndNecessaryReplacementsComplete':True,'baselineDeletionAfterReviewedReplacementAndReopenedMatchingScheduleOnly':True,'preserveNondeficientUploads':True,'studioMustBeReadBeforeActing':True}
future=[]
public=[]
for row in q['currentUploads']:
    d=row.get('recordedDate')
    if d and d>'2026-10-11': future.append(row)
    else: public.append(row)
future.sort(key=lambda r:(r['recordedDate'],r.get('slug') or ''))
q['futureScheduledPriority']=[{'rank':i+1,'slug':r['slug'],'videoId':r['videoId'],'ledgerDate':r['recordedDate'],'dateIsLocalLedgerPendingFreshStudio':True} for i,r in enumerate(future)]
q['publishedAuditParallelScope']=[{'slug':r.get('slug'),'videoId':r.get('videoId'),'currentPublicStatusRequiresStudioCheck':True} for r in public]
q['next']='Read and audit current motion-sickness-games mBDd9VzSTkA scheduled Oct12, then orientation Oct13, then later future slots. Preserve prior completed motion/orientation work; review minimum4 games before any dependent synthesis. New Sakurai6 wait until all current-upload necessary revisions complete.'
q['updatedAt']=now
path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bpath=root/'production/batches/unpublished-teaching-clarity-revision/queue.json'
b=json.loads(bpath.read_text(encoding='utf-8-sig'))
b['replacementPriorityInstruction']=q['priorityInstruction']
b['newProductionTargetsStartAllowed']=False
b['newProductionTargetsHoldReason']='Finish current-upload reviews and necessary closest-date replacements first, per latest user sequencing instruction.'
b['updatedAt']=now
bpath.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'futureLedgerSlots':len(future),'first':q['futureScheduledPriority'][:3],'newSixDeferred':True},ensure_ascii=False))
