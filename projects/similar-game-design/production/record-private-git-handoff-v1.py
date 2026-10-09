"""Record the observed production push and current73-paragraph rebuild inputs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'projects/similar-game-design'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
proofpath=B/'publishing/private-delivery-git-verification-v1.json'
g=read(proofpath)
assert g['pushed'] and g['exactLocalRemoteMatch'] and g['allRemoteBlobsVerified'] and g['unrelatedIndexEntriesPreserved']
assert g['commit']==g['remoteCommit']=='00fb7a13a2be615eb2f06eb91e2719ffcfd6d3aa'
rpath=B/'publishing/youtube-upload-v1.json';r=read(rpath)
assert r['videoId']=='_p1IqDeg6YE' and r['fullSettingsVerified'] and r['burnedCaptionPixelsVerified']
gitrecord=dict(delivered=True,productionCommit=g['commit'],remoteCommit=g['remoteCommit'],
    proof=proofpath.relative_to(ROOT).as_posix(),normalPush=True,allRemoteBlobsVerified=True,
    actualLocalRemoteMatch=True,verifiedAt=g['verifiedAt'],completed=True)
r.update(status='reviewed-private-delivered',updatedAt=now,git=gitrecord);save(rpath,r)
ep=B/'publishing/private-upload-execution-v1.json';e=read(ep)
e.update(status='reviewed-private-delivered',updatedAt=now,gitDelivery=gitrecord,next='presenting-game-scores: full-source/current-content/Studio duplicate review; future research-black-v1 explanation palette.');save(ep,e)
planpath=B/'production/final-v1/plan.json';plan=read(planpath)
assert sha(planpath)=='7b57e188708370bdb904e9986770eff9b6de75d533530f66d6354f86d726cb52'
assert len(plan['scenes'])==24 and sum(len(s['paragraphs']) for s in plan['scenes'])==73
for lang in ['ko','en']:
    scenes=[dict(id=s['id'],title=s['title'],lines=[p[lang] for p in s['paragraphs']]) for s in plan['scenes']]
    save(B/f'script/narration.current.{lang}.json',dict(schemaVersion=1,language=lang,title=r['metadata']['title'] if lang=='ko' else r['englishMetadata']['title'],
        source=planpath.relative_to(ROOT).as_posix(),sourceSha256=sha(planpath),method='Literal current plan snapshot for rebuild/duplicate review; no new narration, translation, editing or TTS.',scenes=scenes))
pp=B/'project.json';p=read(pp)
p.update(status='complete-private-review',updatedAt=now)
p['duplicateReview'].update(inputsDigest=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/similar-game-design.json')['inputsDigest'],
    review='production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v20.json',
    contentEvidence='production/batches/sakurai-planning-game-design/proof-similar-game-design/content-review-v20.json',checkedAt=now,currentCheckPassed=True)
p['paths'].update(baselineScript=p['paths']['script'],baselineScriptEnglish=p['paths']['scriptEnglish'],
    script='projects/similar-game-design/script/narration.current.ko.json',scriptEnglish='projects/similar-game-design/script/narration.current.en.json',
    timeline=planpath.relative_to(ROOT).as_posix(),publishingReceipt=rpath.relative_to(ROOT).as_posix())
p['publishing'].update(videoId=r['videoId'],receipt=rpath.relative_to(ROOT).as_posix(),uploaded=True,thumbnail=True,
    fullSettingsVerified=True,privateSaveVerified=True,scheduled=False,privacy='private',gitDelivery=gitrecord)
p['format'].update(durationSeconds=618.3,frames=37098,videoTimeBase='1/90000',ptsStep=1500)
p['editing'].update(actualGameplaySeconds=21827/60,actualExplanationSeconds=14551/60,
    finalBodyFrames=dict(total=36378,actual=21827,explanation=14551,ratioErrorFrames=.2),
    timingStatus='current-measured-pair-and-bilingual-cues-reviewed',currentSceneCount=24,currentParagraphCount=73,
    allFinalPixelsReviewed=True,currentPixelReview='projects/similar-game-design/production/final-v1/final-pixel-direct-review-v1.json')
p['membership']['appliedToFinal']=True
p['audio']['mixedAsrApproved']=True
p['approvals'].update(collected=True,uploaded=True,voice='Current automated whole/mixed content integrity reviewed; human listening/pronunciation pending')
save(pp,p)
cp=B/'production/latest-checkpoint.json';c=read(cp)
c.update(status='complete-private-review',stage='reviewed-private-delivered',updatedAt=now,gitDelivery=gitrecord,nextAction=e['next']);save(cp,c)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='similar-game-design')
i.update(status='complete-private-review',stage='reviewed-private-delivered',gitDelivery=gitrecord,uploadReceipt=rpath.relative_to(ROOT).as_posix(),next=e['next'])
completed=[x for x in q['items'] if x['status'] in ['uploaded-private-awaiting-user-review','uploaded-private','complete-private-review']]
queued=[x for x in q['items'] if x['status']=='queued'];duplicates=[x for x in q['items'] if x['status']=='skipped-duplicate']
assert (len(completed),len(queued),len(duplicates))==(15,8,1)
q['progress'].update(remaining=8,rendered=15,collected=15,uploaded=15,duplicateExcluded=1,inProgress=0,queued=8,
    productionRendered=15,productionCollected=15,privateSaved=15,fullSettingsDelivered=15,
    productionDelivered=15,remainingProduction=8,productionGitDelivered=15)
q.update(currentSlug='presenting-game-scores',lastCompletedSlug='similar-game-design',updatedAt=now,lastProgressAt=now);save(qp,q)
note=f'2026-10-09 actual delivery: similar-game-design was saved once privately as _p1IqDeg6YE. Production/QA/four-file collection/available publishing settings and CC-off gameplay/spatial-caption pixels are verified. Normal production push {g["commit"]} matched actual local/remote and all608 final blobs; four individually reviewed raster additions are the thumbnail and three minimal publishing proofs, with media/QA rasters excluded and unrelated index entries preserved. Current batch:15 reviewed private deliveries, one content duplicate excluded, eight queued. Next: presenting-game-scores (source URL retained in its batch queue entry), full source/content/current Studio duplicate review before creation, with future research-black-v1. Human listening/pronunciation/public-rights/Nimbus/handles/backup/dubbing/optionalCC/private comment remain pending. No completion modal was invented and no completed media/upload/research handoff is repeated.'
for rp in [B/'README.md',ROOT/'production/batches/sakurai-planning-game-design/README.md']:
    t=rp.read_text('utf-8-sig');assert note not in t
    rp.write_text(t.replace('\n','\n\n'+note+'\n\nThe earlier checkpoint paragraphs below are preserved history; this actual delivery and current receipt take precedence.\n',1),'utf-8')
save(B/'production/private-final-delivery-rollup-v1.json',dict(schemaVersion=1,recordedAt=now,videoId=r['videoId'],productionGit=gitrecord,
    evidenceFollowup='Prepared accurate receipt/manifest/24-scene73-paragraph current snapshots and batch rollup; no future self-SHA inferred.',
    completed=15,duplicateExcluded=1,queued=8,next='presenting-game-scores',newMedia=0,mediaRepeated=False,foreignProcessesChanged=0,
    preparationRecovery=dict(firstExitCodes=[1,1],reason='This manifest uses format and membership, rather than video and membershipOutro. Receipt/execution and literal current snapshots were preserved; metadata-only resumption updates the actual existing fields.',mediaOrUploadRepeated=False)))
print(json.dumps(dict(privateDelivered=True,productionCommit=g['commit'],completed=15,queued=8,currentScenes=24,currentParagraphs=73)))
