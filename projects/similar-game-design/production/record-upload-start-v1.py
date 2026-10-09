"""Record the single ID actually observed after the authorized file chooser."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
pub=BASE.parent/'publishing';prepared=read(pub/'prepared-publishing-v1.json')
proof=ROOT/'shared/output/similar-game-design/publishing-qa-v1/upload-initial.ax.txt'
text=proof.read_text('utf-8');assert '_p1IqDeg6YE' in text and '비공개로 저장됨' in text and 'similar-game-design.captioned.mp4' in text
delivery=read(BASE/'delivery-output.json');assert delivery['files'][0]['sha256']==prepared['videoHash']
receipt=dict(schemaVersion=1,slug='similar-game-design',status='single-private-default-upload-in-progress-settings-pending',
 actualVideoId='_p1IqDeg6YE',videoId='_p1IqDeg6YE',watchUrl='https://youtu.be/_p1IqDeg6YE',
 uploadStartedAt=now,video=delivery['files'][0],metadata=prepared['metadata'],englishMetadata=prepared['englishMetadata'],
 thumbnail=prepared['thumbnail'],chapters=prepared['chapters'],
 subtitles=[dict(path=p,status='pending-manual-file-upload') for p in prepared['plannedSubtitlePaths']],
 coachingCard=prepared['coachingCard'],endScreen=prepared['endScreen'],pinnedComment=prepared['pinnedComment'],
 uploaded=False,uploadTransferComplete=False,privateDefaultObserved=True,privateVisibilitySaveVerified=False,
 scheduled=False,thumbnailSavedVerified=False,fullSettingsVerified=False,automaticChecks='not-yet-started',
 burnedCaptionUploadedPixelsVerified=False,qaApproved=True,collected=True,
 initialProof=dict(path=proof.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(proof.read_bytes()).hexdigest()),
 pending=['Upload transfer and processing','Save and reopen every platform setting','Uploaded CC-off game and 2.5D pixels',
 'Human whole listening/pronunciation','Public rights','Original Nimbus library file','Source-truncated member handles','External backup','Automatic dubbing/optional CC','Private pinned comment'])
rp=pub/'youtube-upload-v1.json';assert not rp.exists();save(rp,receipt)
cp=read(BASE/'latest-checkpoint.json');cp.update(updatedAt=now,status=receipt['status'],actualVideoId=receipt['videoId'],uploadReceipt=rp.relative_to(ROOT).as_posix(),uploaded=False);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='similar-game-design');i.update(stage=cp['status'],actualVideoId=receipt['videoId'],uploadReceipt=cp['uploadReceipt'],uploaded=False);q['updatedAt']=now;save(qp,q)
print(json.dumps(dict(actualVideoId=receipt['videoId'],uploaded=False,privateDefaultObserved=True)))
