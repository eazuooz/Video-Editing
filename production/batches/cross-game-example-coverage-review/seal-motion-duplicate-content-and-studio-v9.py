"""Seal six changed whole-content reads and actual read-only Studio evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'duplicate-content-and-studio-direct-review-v9.json'
assert not out.exists()
report=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
old=read(R/'duplicate-before-refresh-v9.json')
hashes={x['path']:x['sha256'] for x in old['inputFiles']}
changed=[x for x in report['inputFiles'] if hashes.get(x['path'])!=x['sha256']]
assert len(changed)==6 and len(report['existingProjects'])==87 and len(report['inputFiles'])==501
for row in changed:assert sha(ROOT/row['path'])==row['sha256'],row['path']
studio=[]
for part,vid,date in [('foundations','wreXZkEtLqA','2026. 10. 17.'),('calculations','Rck2eL8VtqM','2026. 10. 19.')]:
    slug=f'game-math-quaternion-{part}-v3'
    p=R/f'current-studio-{part}-v3-whole-v9.ax.txt';ax=p.read_text('utf-8')
    manifest=read(ROOT/f'projects/{slug}/project.json')
    descpath=ROOT/manifest['paths']['publishingKo']
    description=re.search(r'ID: textbox, Value: (.*?)\n\t+\d+ text ',ax,re.S).group(1)
    assert description.strip()==descpath.read_text('utf-8-sig').strip(),part
    assert manifest['titles']['ko'] in ax
    assert all(t in ax for t in ['예약됨','표준 화질 완료','고화질 완료','button (disabled) 저장'])
    sp=R/'current-studio-schedule-observations-v9.json';sched=read(sp)['observations'][vid]
    assert sched['dateLabel']==date and sched['timeLabel']=='오전 9:00' and sched['timezoneLabel']=='GMT+0900'
    studio.append(dict(videoId=vid,title=manifest['titles']['ko'],wholeDescriptionCompared=True,
        axPath=p.relative_to(ROOT).as_posix(),axSha256=sha(p),schedulePath=sp.relative_to(ROOT).as_posix(),scheduleSha256=sha(sp),
        preparedDescriptionSha256=sha(descpath),scheduledDate=date,time='09:00',timezone='Asia/Seoul',sdHd=True,saveDisabled=True,platformMutations=0))
motion=R/'current-studio-schedule-observations-v9.json'
assert read(motion)['observations']['mBDd9VzSTkA']['dateLabel']=='2026. 10. 12.'
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),
    previousReview='duplicate-content-and-studio-direct-review-v8.json',previousReviewSha256=sha(R/'duplicate-content-and-studio-direct-review-v8.json'),
    inventoryDigest=report['inputsDigest'],inventoryProjectCount=87,inventoryInputCount=501,changedInputs=changed,
    allChangedContentsReviewed=True,fullReadEvidence=['280cab: calculations v3 whole manifest','foundations v3 whole 681-line reread','8282e9: both v3 whole receipts','bef78b + 1ed50a: calculations v2 whole receipt with final tail recovery','a89834: foundations v2 whole receipt'],
    unchangedFullBilingualScriptsReusedFromPreviousDirectReview=True,studioWholeReads=studio,currentWholeStudioReviewComplete=True,
    motionReservationPreserved=dict(videoId='mBDd9VzSTkA',date='2026-10-12',time='09:00',timezone='Asia/Seoul',proof=motion.relative_to(ROOT).as_posix(),sha256=sha(motion)),
    findings=[
        'Both v2 receipts now record private superseded baselines, preserving their previous schedules as history and exact new v3 IDs. No deletion was performed in this audit; the current old-baseline privacy claim is a receipt record, not a newly observed UI fact.',
        'Both v3 manifests/receipts record four-game additions for Riders Republic, Trailmakers, Space Engineers and Besiege. Retained quaternion rotation/half-angle/inverse/composition/vector calculations differ from motion camera, aim and locomotion choices. The previously read full bilingual scripts are unchanged.',
        'Actual current Studio full Korean titles and descriptions match prepared files. Both new v3 uploads are scheduled at their original October17/19 09:00 GMT+0900 slots and have SD/HD complete. Foundations still shows platform review pending; calculations shows a dash. This audit grants no foreign pixel, listening or rights approval.',
        'Historical pending fields in manifests are distinguished from newer delivery/receipt evidence. Legacy lecture 40:60/noBGM/white and original PCM/cat/member preservation are separate from motion design 60:40.',
        'Motion remains scheduled October12 09:00; no settings, privacy, reservation or foreign files were changed.'
    ],verdict='distinct',currentDuplicateCheckPassed=False,foreignQualityOrRightsApproved=False,foreignFileOrPlatformMutations=0,newVoiceRequestStarted=False,newPcmCount=0)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(changedInputs=6,projects=87,inputs=501,digest=report['inputsDigest'],currentCheckStillRequired=True)))
