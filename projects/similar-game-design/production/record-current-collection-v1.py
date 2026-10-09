"""Record the actual completed collector and byte-identical four files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
qa=read(BASE/'final-v1/final-pixel-direct-review-v1.json')
assert qa['allFinalPixelsReviewed'] and qa['qaApproved'] and qa['collectApproved']
delivery=read(BASE/'delivery-output.json')
assert delivery['cueCounts']==dict(ko=400,en=148)
for x in delivery['files']:
    p=ROOT/delivery['directory']/x['name']
    assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']==sha(ROOT/x['source'])
record=dict(schemaVersion=1,observedAt=now,command='node scripts/collect-video-output.cjs similar-game-design',
 session=81517,actualExitCode=0,files=delivery['files'],allFourBytesMatch=True,
 captionAlignment=delivery['captionAlignment'],seconds=618.3,cues=delivery['cueCounts'],
 rebuildOutputScope='13 baseline script scenes; 211 media references; current24/73 content independently sealed',
 currentFinalPixels='projects/similar-game-design/production/final-v1/final-pixel-direct-review-v1.json',
 allFinalPixels=True,collected=True,uploaded=False,actualVideoId=None,humanWholeListening='pending',publicRights='pending')
save(BASE/'current-collection-verification-v1.json',record)
cp=read(BASE/'latest-checkpoint.json')
cp.update(updatedAt=now,status='four-files-collected-awaiting-single-private-upload',collected=True,
 collectionVerification='projects/similar-game-design/production/current-collection-verification-v1.json',uploaded=False,actualVideoId=None)
save(BASE/'latest-checkpoint.json',cp)
pp=BASE.parent/'publishing/prepared-publishing-v1.json'
prepared=read(pp)
prepared.update(status='collected-and-technically-QA-approved-awaiting-private-upload',qaApproved=True,collected=True,
 videoHash=delivery['files'][0]['sha256'],collectionVerification=cp['collectionVerification'])
save(pp,prepared)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
queue=read(qp);item=next(x for x in queue['items'] if x['slug']=='similar-game-design')
item.update(stage=cp['status'],collected=True,collectionVerification=cp['collectionVerification'],uploaded=False)
queue['updatedAt']=now;save(qp,queue)
print(json.dumps(dict(collected=True,allFourBytesMatch=True,uploaded=False,actualVideoId=None)))
