"""Adopt only byte-identical encoded QA boards already directly viewed; expose every change."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(BASE/'final-v1/encoded-caption-qa-local-v1/execution.json')
prior=read(BASE/'final-v1/encoded-pixel-direct-review.json')
current=read(BASE/'final-v2/encoded-caption-qa-local-v1/execution.json')
assert prior['reviewedSheetCount']==124 and prior['reviewedImageCount']==744
assert current['exitCode']==old['exitCode']==0
assert len(current['sheets'])==len(old['sheets'])==124
assert len(current['images'])==len(old['images'])==744
dest=BASE/'final-v2/encoded-pixel-direct-review.json'; assert not dest.exists()
adopted=[]; changed=[]; comparisons=[]; records=[]
for n,(a,b) in enumerate(zip(old['sheets'],current['sheets']),1):
    previous=next(r for r in prior['reviewedRecords'] if r['sheetNumber']==n)
    assert previous['sha256']==a['sha256']==sha(ROOT/a['path'])
    assert sha(ROOT/b['path'])==b['sha256']
    same=True; images=[]
    for index in b['imageIndices']:
        x=old['images'][index-1]; y=current['images'][index-1]
        assert x['frame']==y['frame'] and x['visibleCueIds']==y['visibleCueIds']
        assert sha(ROOT/x['path'])==x['sha256'] and sha(ROOT/y['path'])==y['sha256']
        identical=x['sha256']==y['sha256']
        same= same and identical
        comparisons.append(dict(frame=y['frame'],oldPath=x['path'],oldSha256=x['sha256'],
            currentPath=y['path'],currentSha256=y['sha256'],encodedPngByteIdentical=identical,
            oldSheetNumber=n,priorActualDirectRead=previous['path']))
        images.append({k:y[k] for k in ('path','sha256','frame','segment','visibleCueIds')})
    if same and a['sha256']==b['sha256']:
        adopted.append(n)
        records.append(dict(sheetNumber=n,path=b['path'],sha256=b['sha256'],images=images,
            reviewMethod='byte-identical-board-and-six-encoded-PNGs-from-prior-direct-read',priorSheet=previous['path']))
    else: changed.append(n)
ledger=dict(schemaVersion=1,status='revised-pixels-direct-review-in-progress',source=current['source'],
    sourceSha256=current['sourceSha256'],allFinalPixelsApproved=False,imagesLocalOnly=True,newGitImages=0,
    totalSheets=124,reviewedSheets=adopted,reviewedSheetCount=len(adopted),reviewedImageCount=len(records)*6,
    byteIdenticalAdoptedSheets=adopted,changedSheetsRequiringDirectRead=changed,
    priorDirectReview='projects/making-game-sequels/production/final-v1/encoded-pixel-direct-review.json',
    findings=[dict(sheets=adopted,observation='These complete boards and all six encoded PNG files are byte-identical to the actual previously directly viewed boards; no changed pixel is accepted by inference.')],
    reviewedRecords=records,updatedAt=datetime.now(timezone.utc).isoformat(),unresolvedIssues=prior['unresolvedIssues'])
dest.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(BASE/'final-v2/encoded-pixel-exact-adoption.json').write_text(json.dumps(dict(
    createdAt=ledger['updatedAt'],adoptedSheetCount=len(adopted),changedSheets=changed,comparisons=comparisons,
    changedPixelsDirectlyRead=False,noApproximateSimilarityApproval=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(adoptedBoards=len(adopted),changedBoards=changed,newlyDirectlyViewed=0)))
