import json, hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta

root = Path(__file__).resolve().parents[3]
now = datetime.now(timezone(timedelta(hours=9))).isoformat()
def read(rel):
    return json.loads((root / rel).read_text(encoding='utf-8-sig'))
def write(rel, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

evidence = '지금 검수·재제작을 재개'
pausepath = 'production/USER_VIDEO_WORK_PAUSE.json'
p = read(pausepath)
p.setdefault('pauseHistory', []).append({k:p.get(k) for k in ('recordedAt','status','userEvidence','automationStatus')})
p.update(status='resumed-by-user', resumedAt=now, resumeUserEvidence=evidence,
         automationStatus='ACTIVE', resumeRequiresUserInstruction=False, newProductionAllowed=True)
write(pausepath,p)
bpath = 'production/batches/unpublished-teaching-clarity-revision/queue.json'
b = read(bpath)
b.update(mode='active-cross-game-coverage-review', paused=False, updatedAt=now)
b['resume'] = {'at':now,'userEvidence':evidence,'preservePriorReviewEvidence':True}
b['crossGameCoveragePolicy'] = 'shared/publishing/game-example-coverage-policy.json'
for item in b['items']:
    item['crossGameCoverageReview'] = {'status':'pending-current-content-and-footage-review','minimumDistinctGames':4,'approved':False}
write(bpath,b)
opath='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/latest-checkpoint.json'
o=read(opath)
o.update(paused=False,resumedAt=now,resumeUserEvidence=evidence)
o['crossGameCoverageReview']={'status':'additional-game-source-preflight-required','minimumDistinctGames':4,'approved':False,'preserveCompletedPcmAndPrototypeReviews':True}
write(opath,o)

ledgerpath='shared/publishing/daily-alternating-schedule.json'
ledger=read(ledgerpath)
rows=[]
for entry in ledger['actualSchedules']:
    slug=entry.get('slug')
    rows.append({'slug':slug,'videoId':entry.get('videoId'),'recordedDate':entry.get('date'),
        'source':'current-local-ledger','currentStudioRecheckedThisAudit':False,
        'status':'pending-full-content-and-selected-footage-review','coverageApproved':False})
ids={r['videoId'] for r in rows}
for entry in b.get('publishedObservedExcluded',[]):
    if isinstance(entry,dict) and entry.get('videoId') and entry['videoId'] not in ids:
        rows.append({'slug':entry.get('slug'),'videoId':entry['videoId'],'source':'historical-public-observation',
            'currentStudioRecheckedThisAudit':False,'status':'pending-full-content-and-selected-footage-review','coverageApproved':False})
metadata=[]
for slug in ['game-math-orientation-matrices','character-parameters','limited-color-world','presenting-game-scores']:
    path=root/'projects'/slug/'sources/game-candidates.json'
    if path.exists():
        metadata.append({'slug':slug,'candidateFile':path.relative_to(root).as_posix(),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'candidateFileIsNotFinalCoverageProof':True})
queue={'schemaVersion':1,'recordedAt':now,'status':'active','resumeUserEvidence':evidence,
    'policy':'shared/publishing/game-example-coverage-policy.json','minimumDistinctGamesPerIndependentVideo':4,
    'inventoryOnly':True,'wholeCurrentScriptsReviewed':False,'allFinalPixelsReviewed':False,
    'currentUploads':rows,'newProductionTargets':b.get('newProductionTargets',[]),
    'boundedSourceMetadata':metadata,'localLedgerSha256':hashlib.sha256((root/ledgerpath).read_bytes()).hexdigest(),
    'next':'orientation current Studio and full script review; secure three additional distinct concept-matched existing games before dependent narration; preserve completed six additive PCM and source/annotation evidence',
    'newRenderStarted':False,'newTtsStarted':False,'newUploadStarted':False,'foreignResearchModified':False}
write('production/batches/cross-game-example-coverage-review/queue.json',queue)
print(json.dumps({'resumed':True,'automation':'ACTIVE','ledgerUploadsQueuedForAudit':len(rows),'newProductionTargets':len(queue['newProductionTargets']),'metadataOnly':True},ensure_ascii=False))
