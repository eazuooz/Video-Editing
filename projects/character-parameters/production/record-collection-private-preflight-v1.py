"""Verify the actual single collection; prepare an accurate private upload receipt."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1';PUB=BASE.parent/'publishing'
a=argparse.ArgumentParser();a.add_argument('--collector-session',type=int,required=True);a.add_argument('--actual-collector-exit-code',type=int,required=True);a.add_argument('--collector-chunk',required=True);v=a.parse_args();assert v.actual_collector_exit_code==0
read=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
dest=BASE/'collection-private-preflight-v1.json';receipt_path=PUB/'youtube-upload-v1.json';assert not dest.exists() and not receipt_path.exists(),'Continue actual collector or upload; never repeat'
qa=read(W/'final-pixel-direct-review-v1.json');delivery=read(BASE/'delivery-output.json');metadata=read(PUB/'publishing-text-preparation-v2.json');plan=read(W/'plan.json')
assert qa['qaApproved'] and qa['collectApproved'] and qa['allFinalPixelsReviewed']
assert (delivery['cueCounts']['ko'],delivery['cueCounts']['en'])==(201,95) and len(delivery['files'])==4
for r in delivery['files']:
 assert r['source'].startswith(rel(W)+'/') and sha(ROOT/r['source'])==sha(ROOT/delivery['directory']/r['name'])==r['sha256']
video=next(r for r in delivery['files']if '.captioned.'in r['name']);assert video['sha256']==qa['sourceSha256']
assert metadata['planSha256']==qa['planSha256']==sha(W/'plan.json')
proof=dict(recordedAt=now(),actualCollectorSession=v.collector_session,actualCollectorExitCode=0,collectorChunk=v.collector_chunk,exitDirectlyObserved=True,files=delivery['files'],allFourSourceOutputSha256Identical=True,
 qaApproved=True,collected=True,uploaded=False,actualVideoId=None,finalPixelReview=rel(W/'final-pixel-direct-review-v1.json'),finalPixelReviewSha256=sha(W/'final-pixel-direct-review-v1.json'),humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False)
save(dest,proof)
receipt=dict(schemaVersion=1,slug='character-parameters',preparedAt=now(),status='collected-awaiting-single-new-private-upload',
 actualVideoId=None,actualVideoUrl=None,uploadStarted=False,uploaded=False,privateSaved=False,savedPrivateVerified=False,privacy='private',scheduled=False,scheduleVerified=False,
 video=dict(video,path=delivery['directory']+'/'+video['name'],variant='captioned',burnedKoreanCaptionsRequired=True),
 titles=metadata['titles'],metadataPreparation=rel(PUB/'publishing-text-preparation-v2.json'),metadataPreparationSha256=sha(PUB/'publishing-text-preparation-v2.json'),
 descriptions={lang:rel(PUB/f'description-measured-v2.{lang}.txt')for lang in ['ko','en']},
 subtitles={lang:dict(path=delivery['directory']+f'/character-parameters.{lang}.srt',cues=total,published=False)for lang,total in [('ko',201),('en',95)]},
 thumbnail=dict(path=metadata['thumbnail'],sha256=sha(ROOT/metadata['thumbnail']),saved=False,verified=False),
 card=dict(metadata['card'],saved=False,verified=False),endScreen=dict(metadata['endScreen'],saved=False,verified=False),
 measuredChapters=metadata['measuredChapters'],chaptersVerified=False,englishMetadataPublished=False,manualSrtPublished=False,
 monetization=dict(enabled=False,midrollEligible=False,adSelfCertificationSubmitted=False,actualAdChecksComplete=False),
 checks=dict(sd=False,hd=False,copyrightComplete=False,adSuitabilityComplete=False),uploadedCcOffPixelsVerified=False,fullSettingsVerified=False,
 wizardCompletionModalDirectlyObserved=False,publishingGitDelivered=False,productionGitDelivered=False,collectionVerification=rel(dest),qaApproved=True,collected=True,
 targetDate='2026-10-30',targetTime='09:00',timezone='Asia/Seoul',targetIsPlatformReservation=False,
 pinnedComment=metadata['pinnedComment'],humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,pending=qa['pending'],
 sourceAudioStreams=0,newMediaGitAdded=0,newQaImagesGitAdded=0)
save(receipt_path,receipt)
mp=BASE.parent/'project.json';m=read(mp);m['approvals']['collected']=True;m.update(status=receipt['status'],updatedAt=now());save(mp,m)
cp=read(BASE/'latest-checkpoint.json');cp.update(stage=receipt['status'],recordedAt=now(),collected=True,private=False,actualVideoId=None,collectionVerification=rel(dest),youtubeReceipt=rel(receipt_path));save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items']if x['slug']=='character-parameters');i.update(stage=receipt['status'],collected=True,collectionVerification=rel(dest),youtubeReceipt=rel(receipt_path));i['checkpoints']['collected']=True;q['updatedAt']=now();save(qp,q)
print(json.dumps(dict(collected=True,files=4,actualVideoId=None,uploaded=False)))
