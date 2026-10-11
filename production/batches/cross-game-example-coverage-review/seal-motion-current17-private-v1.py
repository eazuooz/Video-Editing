"""Record observed private settings; no platform, media or research operation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
B = Path(__file__).resolve().parent
PUB = R / 'publishing'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = datetime.now(timezone.utc).isoformat()

def save(p, value):
    temporary = p.with_name(p.name + '.private-v1.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temporary, p)

promotion = read(R / 'current17-main-promotion-v1.json')
for row in promotion['otherProtectedInputs']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
files = [
    'current17-private-saved-reopened-v1.ax.txt',
    'current17-english-metadata-and-track-saved-v1.ax.txt',
    'current17-english-srt-parsed-v2.ax.txt',
    'current17-korean-srt-reopened-v1.ax.txt',
    'current17-private-details-and-advanced-v1.ax.txt',
    'current17-end-screen-reopened-v1.ax.txt',
    'current17-end-playlist-reopened-v1.ax.txt',
    'current17-end-link-reopened-v1.ax.txt',
    'current17-card-reopened-v1.ax.txt',
    'current17-monetization-on-reopened-v1.ax.txt',
    'current17-claims-no-claim-v1.ax.txt',
    'current17-upload-watch-ccoff-quality-v1.ax.txt',
    'current17-upload-watch-summary-ccoff-v1.ax.txt',
]
texts = {f: (PUB / f).read_text('utf-8') for f in files}
assert 'lXjDBqONLWs' in texts[files[0]] and '비공개' in texts[files[0]]
assert '고화질 완료' in texts[files[0]] and '표준 화질 완료' in texts[files[0]]
assert '동영상에서 소유권 주장이 발견되지 않았습니다' in texts[files[10]]
assert '사용, Value: 1' in texts[files[9]]
assert '1080p60 HD' in texts[files[11]] and '자막 사용 안함' in texts[files[11]]
assert '14:03:06' in texts[files[5]] and '14:13:06' in texts[files[5]]
assert '14:03:06' in texts[files[6]] and '14:13:06' in texts[files[6]]
assert '14:03:06' in texts[files[7]] and '14:13:06' in texts[files[7]]
assert '티저 시작 시간: 0분 0초 0프레임' in texts[files[8]]
assert '게시됨' in texts[files[1]] and '수동' in texts[files[1]]

upload_path = PUB / 'youtube-upload-v1.json'
upload = read(upload_path)
assert upload['actualVideoId'] == 'lXjDBqONLWs' and upload['uploadSelections'] == 1
upload.update(status='private-saved-reopened;available-settings-verified', lastObservedAt=now,
    observedProgressPercent=100, observedPlatformText='Saved private; SD/HD complete badges; watch1080p60 available',
    uploadComplete=True, sdComplete=True, hdComplete=True, checksComplete=True,
    checksResult='No copyright claim; monetization on; no restriction alert',
    manualKoSrtSaved=True, manualKoSrtPublished=True, manualEnSrtSaved=True, manualEnSrtPublished=True,
    englishMetadataSaved=True, englishMetadataReopenedVerified=True,
    thumbnailSavedAndReopened=True, cardSaved=True, endScreenSaved=True,
    ccOffPixelsVerified=True, fullSettingsVerified=True,
    platformProcessingContainerNote='Details container retained99% wording while HD complete badge and actual1080p60 were available; not used as100% processing proof',
    humanListeningApproved=False, publicRightsApproved=False)
upload['card']['reopenedVerified'] = True
upload['endScreen'].update(reopenedVerified=True, reopenedUiStart='14:03:06',
    reopenedUiEnd='14:13:06', reopenedUiFps=60,
    exactStartSeconds=843.1, exactEndSeconds=853.1)
save(upload_path, upload)
proof = dict(schemaVersion=1, reviewedAt=now, actualVideoId='lXjDBqONLWs', actualCuaTabs=[100,101],
    privateSavedAndReopened=True, singleUploadSelection=1,
    koManualCues=220, enManualCues=220, allManualCueTextsComparedToCurrentFiles=True,
    koPostedToastObserved=True, enPostedToastObserved=True, enManualPublishedReopened=True,
    localizedEnglishMetadataSavedReopened=True,
    thumbnailReused='projects/motion-sickness-games/publishing/thumbnail-depth-v1.png',
    thumbnailVisibleSavedReopened=True, playlist='Planning & Game Design & Tech',
    notMadeForKids=True, paidPromotion=False, aiSynthesisDisclosed=True,
    videoLanguage='Korean', standardYouTubeLicense=True, category='Education',
    monetizationOn=True, adSelfRating='none-applicable', copyrightClaims='none-found',
    sdBadgeComplete=True, hdBadgeComplete=True, actualWatchQuality='1080p60 HD',
    uploadedPixels=dict(ccOff=True, videoWidth=1920, videoHeight=1080,
        observations=[dict(time=429.963363, scene='Portal2 tracked cube/wall roles and fixed Korean caption'),
            dict(time=802.79, scene='projected front/top/side explanation and fixed Korean caption')],
        playbackRate=1, muted=True, platformDurationSeconds=853.141,
        localEncodedDurationSeconds=853.1, allContinuousFramesApproved=False),
    card=upload['card'], endScreen=upload['endScreen'], fullAvailableSettingsVerified=True,
    humanListeningApproved=False, publicRightsApproved=False,
    pending=['human continuous listening/pronunciation','footage/Nimbus rights','member handle review',
        'external backup','automatic dubbing review','optional captions propagation','pinned comment after comments available'],
    scheduled=False, obsoleteDeleted=False,
    evidence=[dict(path=(PUB/f).relative_to(ROOT).as_posix(),sha256=sha(PUB/f)) for f in files],
    localOnlyImages=[dict(path=(PUB/f).relative_to(ROOT).as_posix(),sha256=sha(PUB/f)) for f in [
        'current17-private-saved-reopened-v1.png','current17-upload-watch-portal-ccoff-v1.png',
        'current17-upload-watch-summary-ccoff-v1.png']])
save(PUB / 'private-settings-direct-review-v1.json', proof)
main_path = ROOT / 'projects/motion-sickness-games/project.json'
main_before = sha(main_path)
main = read(main_path)
main['status'] = 'cross-game-four-current17-private-reviewed;Git-schedule-pending'
main['publishing'].update(uploaded=True, videoId='lXjDBqONLWs', actualVideoId='lXjDBqONLWs',
    videoUrl='https://youtu.be/lXjDBqONLWs', privacyStatus='private',
    status='single-captioned-private-saved-reopened-settings-reviewed', fullSettingsVerified=True,
    ccOffPixelVerification=(PUB/'private-settings-direct-review-v1.json').relative_to(ROOT).as_posix())
save(main_path, main)
save(R/'current17-main-private-update-v1.json', dict(schemaVersion=1,recordedAt=now,
    beforeSha256=main_before,afterSha256=sha(main_path),intentionalPublishingUpdate=True,
    localMediaPathsUnchanged=True,other70ProtectedInputsUnchanged=True,originalBaselineUnmodified=True,
    actualVideoId='lXjDBqONLWs',scheduleStillPending=True))
next_step = ('Private lXjDBqONLWs available settings and uploadedCCoff1080p60 pixels verified. '
    'Deliver reviewed explicit paths through isolatedGitindex/normalpush/actualremote. '
    'Read currentStudio and ledger09slot, save/reopen replacement schedule, then action-time '
    'confirmation for matchingobsolete mBDd9VzSTkA deletion. No repeat upload/media/ASR/TTS; '
    'pause after normal-transform-UV, no newSakurai6.')
cp = read(R/'latest-checkpoint.json')
cp.update(recordedAt=now,stage='current17-private-settings-reviewed-Git-schedule-pending',
    privateSettingsVerified=True,actualReplacementVideoId='lXjDBqONLWs',next=next_step)
save(R/'latest-checkpoint.json',cp)
queue=read(B/'queue.json')
queue.update(updatedAt=now,status='active-current17-private-reviewed-Git-pending',next=next_step)
queue['currentMotionReview'].update(stage=cp['stage'],status=cp['stage'],
    currentMinimumFourApproved=True,finalFourGameApproval=True,footageAdopted=True,
    newVideoId='lXjDBqONLWs',privateSettingsVerified=True,next=next_step,
    privateSettingsReview=(PUB/'private-settings-direct-review-v1.json').relative_to(ROOT).as_posix())
save(B/'queue.json',queue)
print(json.dumps(dict(actualVideoId='lXjDBqONLWs',privateSettingsVerified=True,
    manualCuesEach=220,other70Unchanged=True,git=False,schedule=False,obsoleteDeleted=False)))
