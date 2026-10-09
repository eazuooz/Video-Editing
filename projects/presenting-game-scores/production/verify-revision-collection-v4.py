"""Verify the single actual four-file collection and prepare accurate upload state."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
B=P/'revision-balatro60-v2';W=B/'final-v4'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
proof=W/'collection-private-preflight-v4.json';assert not proof.exists()
qa=read(W/'final-pixel-direct-review-v4.json');d=read(P/'delivery-output.json');m=read(P.parent/'project.json')
assert qa['collectApproved'] and qa['allFinalPixelsReviewed'] and qa['qaApproved']
assert (d['cueCounts']['ko'],d['cueCounts']['en'])==(175,70)
assert len(d['files'])==4
for x in d['files']:
 assert x['source'].startswith(W.relative_to(ROOT).as_posix()+'/')
 assert sha(ROOT/x['source'])==sha(ROOT/d['directory']/x['name'])==x['sha256']
assert next(x['sha256']for x in d['files']if '.captioned.'in x['name'])==qa['sourceSha256']
save(proof,dict(recordedAt=now(),actualCollectorSession=43509,actualCollectorExitCode=0,exitDirectlyObserved=True,collectorChunk='871536',files=d['files'],allFourSourceOutputSha256Identical=True,finalPixelReview=qa['source'],qaApproved=True,collected=True,uploaded=False,actualVideoId=None,baselineDeliveryPreserved='projects/presenting-game-scores/production/revision-balatro60-v2/baseline-delivery-output-preserved.json',humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False))
m['approvals']['collected']=True;m['currentRevision']['checkpoints']['collected']=True
m['status']='revision-collected-awaiting-single-new-private-upload';m['updatedAt']=now();save(P.parent/'project.json',m)
c=read(P/'latest-checkpoint.json');c.update(stage=m['status'],recordedAt=now(),collected=True,private=False,actualVideoId=None,collectionVerification=proof.relative_to(ROOT).as_posix());c['revisionCheckpoints']['collected']=True;save(P/'latest-checkpoint.json',c)
rpath=B/'publishing/youtube-upload-v3.json';r=read(rpath);assert r['actualVideoId']is None and not r['uploadStarted']
r.update(status=m['status'],qaApproved=True,collected=True,video=next(x for x in d['files']if '.captioned.'in x['name']),updatedAt=now(),collectionVerification=proof.relative_to(ROOT).as_posix())
r['pending']=[x for x in r['pending']if x!='Final encoded pixel QA and four-file collection'];save(rpath,r)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items']if x['slug']=='presenting-game-scores');i.update(stage=m['status'],collected=True,collectionVerification=proof.relative_to(ROOT).as_posix());i['checkpoints']['collected']=True;q['updatedAt']=now();save(qp,q)
print(json.dumps(dict(collected=True,files=4,actualVideoId=None)))
