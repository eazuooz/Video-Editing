"""Verify actual collected files; never infer a saved platform upload."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,time
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/presenting-game-scores';B=P/'production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
d=read(B/'delivery-output.json');qa=read(B/'final-v1/final-pixel-direct-review-v1.json')
assert qa['qaApproved'] and qa['allFinalPixelsReviewed']
assert len(d['files'])==4 and d['cueCounts']=={'ko':168,'en':68}
for f in d['files']:
 assert sha(ROOT/f['source'])==f['sha256']==sha(ROOT/d['directory']/f['name'])
assert (ROOT/d['directory']/'index.html').exists() and (ROOT/'output/index.html').exists()
resources=read(B/'resources-before-private-upload-v1.json')
assert resources['researchControlActions']==0 and resources['ownHeavyJobs']==0
record=dict(schemaVersion=1,slug='presenting-game-scores',verifiedAt=now(),collectCommand='node scripts/collect-video-output.cjs presenting-game-scores',sessionId=77017,outerExitCode=0,outerExitDirectlyObserved=True,files=d['files'],fourFileHashesMatch=True,outputIndex='output/index.html',technicalQa=qa['sourceSha256'],pending=d['notices'],collected=True,actualVideoId=None,uploaded=False,gitDelivery=False,newGitImages=0,resources='projects/presenting-game-scores/production/resources-before-private-upload-v1.json',nextAction='CUA single new private captioned upload; actual settings/readback/CCoff pixels then selective normal Git push')
save(B/'collection-private-preflight-v1.json',record)
m=read(P/'project.json');m['approvals']['collected']=True;m['status']='collected-awaiting-single-private-upload';m['updatedAt']=now();save(P/'project.json',m)
c=read(B/'latest-checkpoint.json');c.update(stage=m['status'],collected=True,recordedAt=now(),collectionVerification='projects/presenting-game-scores/production/collection-private-preflight-v1.json',nextAction=record['nextAction'],approvalScope='Current mixed content/order/endings and exact PCM reviewed with persistent08 recognition alternatives pending human pronunciation; final encoded planned pixels and both full decodes reviewed. No human listening/public rights approval.')
c['ownedJob'].update(status='closed-all-final-pixels-directly-reviewed',activeTask=None,workerExpectedRunning=False)
c['activePlatformJob']=dict(tabId='137',status='single-private-upload-preparing',pid=None,sessionId=None,uploadVariant='captioned',path='output/presenting-game-scores/presenting-game-scores.captioned.mp4',actualVideoId=None,resource=record['resources']);save(B/'latest-checkpoint.json',c)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(20):
 raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items']if x['slug']=='presenting-game-scores');i.update(stage=m['status'],collected=True,collectionVerification=c['collectionVerification'],activePlatformJob=c['activePlatformJob'],nextAction=c['nextAction']);i['checkpoints']['collected']=True;q['updatedAt']=now()
 if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 time.sleep(.15)
else:raise RuntimeError('Concurrent queue preserved')
print(json.dumps(dict(collected=True,files=4,actualVideoId=None,uploaded=False)))
