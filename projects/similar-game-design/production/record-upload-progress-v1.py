"""Record only the saved current upload facts visible in preserved UI evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def save(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', 'utf-8')
now = datetime.now(timezone.utc).isoformat()
pub = BASE.parent / 'publishing'
proof = ROOT / 'shared/output/similar-game-design/publishing-qa-v1/details-private-reopened.ax.txt'
text = proof.read_text('utf-8')
receipt = read(pub / 'youtube-upload-v1.json')
assert receipt['actualVideoId'] == '_p1IqDeg6YE'
for expected in ['_p1IqDeg6YE/edit', 'similar-game-design.captioned.mp4', '비공개', '표준 화질 완료', '고화질 완료', '업로드된 썸네일', 'Planning & Game Design & Tech', receipt['metadata']['title']]:
    assert expected in text, expected
receipt.update(updatedAt=now, status='single-saved-private-upload-language-settings-checks-pending',
    uploaded=True, uploadTransferComplete=True, privateSaveVerified=True,
    privateVisibilitySaveVerified=True, sdComplete=True, hdComplete=True,
    thumbnailSavedVerified=True, koMetadataSavedReopened=True,
    fullSettingsVerified=False, availableSettingsVerified=False,
    platformAutomaticChecksComplete=False, automaticChecks='copyright-complete-no-issues-ad-suitability-pending',
    explicitWizardCompletionObserved=False,
    wizardObservation='Private processing modal observed after Save; SD/HD and explicit private state independently reopened. A separate final completion modal was not observed.',
    detailsProof=dict(path=proof.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(proof.read_bytes()).hexdigest()))
receipt['thumbnail'].update(saved=True, savedReopened=True)
save(pub / 'youtube-upload-v1.json', receipt)
execution = dict(schemaVersion=1,slug='similar-game-design',startedAt=receipt['uploadStartedAt'],
    updatedAt=now,status=receipt['status'],actualVideoId=receipt['videoId'],
    uploadCountThisAttempt=1,source='output/similar-game-design/similar-game-design.captioned.mp4',
    sourceSha256=receipt['video']['sha256'],cleanUploadAllowed=False,cuaTab='89',
    uploaded=True,uploadTransferComplete=True,privateSaved=True,privateSaveVerified=True,
    sdComplete=True,hdComplete=True,thumbnailSavedAndReopened=True,koMetadataSavedReopened=True,
    fullSettingsVerified=False,platformAutomaticChecksComplete=False,
    next='Save/reopen manual KOEN and EN metadata/card/end screen, actual checks and CC-off uploaded game/spatial pixels; selective Git after verification.')
ep=pub / 'private-upload-execution-v1.json'
if ep.exists():
    old=read(ep)
    assert old['actualVideoId']==execution['actualVideoId']
    old.update(execution)
    execution=old
save(ep,execution)
cp=read(BASE / 'latest-checkpoint.json')
cp.update(updatedAt=now,stage=receipt['status'],status=receipt['status'],actualVideoId=receipt['videoId'],videoId=receipt['videoId'],
    render=True,rendered=True,qa=True,qaApproved=True,allFinalPixelsReviewed=True,
    uploaded=True,privateSaveVerified=True,fullSettingsVerified=False,
    uploadExecution=ep.relative_to(ROOT).as_posix(),nextAction=execution['next'])
cp['ownedJob'].update(status='closed-encoded-pixels-completely-reviewed',activeTask=None,workerExpectedRunning=False)
save(BASE / 'latest-checkpoint.json',cp)
qp=ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
q=read(qp)
i=next(x for x in q['items'] if x['slug']=='similar-game-design')
i.update(stage=receipt['status'],uploaded=True,privateSaveVerified=True,fullSettingsVerified=False,
    actualVideoId=receipt['videoId'],videoId=receipt['videoId'],uploadExecution=ep.relative_to(ROOT).as_posix())
q['updatedAt']=now
save(qp,q)
print(json.dumps(dict(videoId=receipt['videoId'],privateSaved=True,sd=True,hd=True,fullSettings=False)))
