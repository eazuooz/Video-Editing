"""Preserve the baseline receipt, or verify a separately observed successful collection."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,time
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent.parent;B=P/'production';W=B/'revision-balatro60-v2/final-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
    return h.hexdigest()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--preserve-baseline',action='store_true');ap.add_argument('--collect-outer-exit-code',type=int);ap.add_argument('--collect-session-id',type=int);ap.add_argument('--resource');a=ap.parse_args()
baseline=B/'revision-balatro60-v2/baseline-delivery-output-preserved.json'
if a.preserve_baseline:
    assert not baseline.exists(),'Already preserved; do not repeat.'
    source=B/'delivery-output.json'
    assert sha(source)=='7c4aaa1e215942065db6b0f171faba0a41fa720abceea2dcb3b0889adb3b29cb'
    baseline.write_bytes(source.read_bytes());assert sha(baseline)==sha(source)
    print(json.dumps(dict(baselineReceiptBytePreserved=True,newMedia=0)));raise SystemExit(0)
assert a.collect_outer_exit_code==0 and a.resource and baseline.exists()
assert not (W/'collection-private-preflight-v3.json').exists()
d=read(B/'delivery-output.json');qa=read(W/'final-pixel-direct-review-v3.json')
assert qa['qaApproved'] and qa['allFinalPixelsReviewed'] and d['cueCounts']==dict(ko=175,en=70) and len(d['files'])==4
for f in d['files']:
    assert 'revision-balatro60-v2/final-v3/' in f['source']
    assert sha(ROOT/f['source'])==f['sha256']==sha(ROOT/d['directory']/f['name'])
assert (ROOT/d['directory']/'index.html').exists() and (ROOT/'output/index.html').exists()
resource=read(ROOT/a.resource);assert resource['researchControlActions']==0 and resource['ownHeavyJobs']==0
record=dict(schemaVersion=3,slug='presenting-game-scores',verifiedAt=now(),collectCommand='node scripts/collect-video-output.cjs presenting-game-scores',
    sessionId=a.collect_session_id,outerExitCode=0,outerExitDirectlyObserved=True,files=d['files'],fourFileHashesMatch=True,
    currentFinalQa=(W/'final-pixel-direct-review-v3.json').relative_to(ROOT).as_posix(),
    currentFinalQaSha256=sha(W/'final-pixel-direct-review-v3.json'),outputIndex='output/index.html',pending=d['notices'],
    baselineReceipt=baseline.relative_to(ROOT).as_posix(),baselineReceiptSha256=sha(baseline),
    baselineSourceFinalPairAndHistoricalDeliveryPreserved=True,collected=True,actualVideoId=None,uploaded=False,
    gitDelivery=False,newGitImages=0,resources=a.resource,
    nextAction='Single new private captioned revision upload, all actual saved settings/readback/CCoff pixels, selective normal Git push, then authorized matching09KST schedule.')
save(W/'collection-private-preflight-v3.json',record)
m=read(P/'project.json');m['approvals']['collected']=True;m['currentRevision']['checkpoints']['collected']=True
m.update(status='revision-collected-awaiting-single-private-upload',updatedAt=now());save(P/'project.json',m)
c=read(B/'latest-checkpoint.json');c.update(stage=m['status'],collected=True,private=False,recordedAt=now(),
    collectionVerification=(W/'collection-private-preflight-v3.json').relative_to(ROOT).as_posix(),nextAction=record['nextAction'],
    activePlatformJob=dict(status='new-revision-private-upload-preparing',uploadVariant='captioned',
        path='output/presenting-game-scores/presenting-game-scores.captioned.mp4',actualVideoId=None,resource=a.resource))
save(B/'latest-checkpoint.json',c)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(20):
    raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
    i.update(stage=m['status'],collected=True,collectionVerification=c['collectionVerification'],
        activePlatformJob=c['activePlatformJob'],nextAction=c['nextAction']);i['checkpoints']['collected']=True;q['updatedAt']=now()
    if qp.read_text('utf-8-sig')==raw:save(qp,q);break
    time.sleep(.15)
else:raise RuntimeError('Concurrent queue preserved')
print(json.dumps(dict(collected=True,files=4,actualVideoId=None,uploaded=False)))
