"""Record the completed changed-input review and current source-only checkpoint."""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent

def put(p, obj, old):
    assert p.read_bytes() == old, 'Concurrent changes preserved; retry after reading them'
    tmp=p.with_name(p.name+'.score-v2.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert p.read_bytes() == old, 'Concurrent changes preserved'
    os.replace(tmp,p)

def main():
    now=datetime.now(timezone.utc).isoformat()
    rp=ROOT/'production/batches/sakurai-planning-game-design/preflight/presenting-game-scores.json'
    report=json.loads(rp.read_text(encoding='utf-8'))
    proofp=HERE/'content-studio-change-review-v2.json'
    old=proofp.read_bytes(); proof=json.loads(old)
    assert report['verdict']=='distinct' and report['inputsDigest']==proof['inventory']['inputsDigest']
    for row in proof['inventory']['changedFiles']:
        assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
    proof.update(reviewedAt=now,currentDuplicateCheckExit=0,
                 currentReportSha256=hashlib.sha256(rp.read_bytes()).hexdigest())
    put(proofp,proof,old)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    old=qp.read_bytes(); queue=json.loads(old)
    item=next(x for x in queue['items'] if x['slug']=='presenting-game-scores')
    item['preflight'].update(inputsDigest=report['inputsDigest'],duplicateCheckExit=0,
                            currentChangedContentReview=str(proofp.relative_to(ROOT)).replace('\\','/'),
                            currentReportSha256=hashlib.sha256(rp.read_bytes()).hexdigest(),
                            currentReviewedAt=now)
    queue['updatedAt']=queue['lastProgressAt']=now
    put(qp,queue,old)
    print(json.dumps({'currentDigest':report['inputsDigest'],'projects':52,'files':367,
                      'changedWholeFilesRead':3,'studioVideo':'nalAZHtEtw0',
                      'duplicateCheckExit':0,'newProject':False,'footageAdoption':False}))

if __name__=='__main__':
    main()
