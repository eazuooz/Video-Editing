"""Seal actual reviewed private settings without editing shared/foreign files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
B = 'production/batches/unpublished-teaching-clarity-revision'
R = 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
PUB = ROOT / R / 'publishing'
now = datetime.now(timezone.utc).isoformat()
read = lambda p: json.loads((ROOT / p).read_text('utf-8-sig'))
def write(p, obj):
    (ROOT / p).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', 'utf-8')
def text(name):
    return (PUB / name).read_text('utf-8-sig')
receipt = read(R + '/publishing/youtube-upload-v1.json')
assert receipt['actualVideoId'] == 'mBDd9VzSTkA' and not receipt['baselineScheduleChanged']
history = PUB / 'youtube-upload-history-before-private-seal-v1.json'
assert not history.exists()
history.write_bytes((PUB / 'youtube-upload-v1.json').read_bytes())
cue = read(R + '/publishing/published-cue-comparison-v3.json')
assert cue['all358PublishedCueTextsAnd716VisibleTimesMatch']
member = read(R + '/publishing/member-timings-actual-ui-v2.json')
assert member['savedAndReopened'] and len(member['rows']) == 3
assert all(e['times'] == ['10:59:53', '11:09:53'] and e['saveDisabled'] for e in member['rows'])
assert '동영상에서 소유권 주장이 발견되지 않았습니다' in text('copyright-current-completed-v2.ax.txt')
assert '동영상에서 설정에 따라 수익을 창출하고 있습니다' in text('copyright-current-completed-v2.ax.txt')
ax = text('private-settings-reopened-v1.ax.txt')
assert '고화질 완료' in ax and '표준 화질 완료' in ax and '비공개' in ax and 'mBDd9VzSTkA' in ax
assert '—' in ax
for language, filename in [('ko', 'ko-metadata-current-ui-v4.json'), ('en', 'en-metadata-current-ui-v3.json')]:
    actual = read(R + '/publishing/' + filename)
    assert actual['actualVideoId'] == receipt['actualVideoId']
    assert [f['value'] for f in actual['fields'][:2]] == [receipt['metadata'][language]['title'], receipt['metadata'][language]['description']]
assert read(R + '/publishing/ko-metadata-current-ui-v4.json')['saveDisabled']
pixel = read(R + '/publishing/uploaded-pixel-observations-v1.json')
assert pixel['actualVideoId'] == receipt['actualVideoId']
assert all(pixel[k]['cc'] == 'false' and pixel[k]['width'] == 1920 and pixel[k]['height'] == 1080 and pixel[k]['rate'] == 1 for k in ['game', 'explanation'])
final = read(R + '/final-pixel-direct-review-v2.json')
flow = read(R + '/final-flow-playback-direct-review-v2.json')
collection = read(R + '/collection-private-preflight-v2.json')
assert final['allFinalCueCutPixelsApproved'] and not final['unresolved']
assert flow['wholeNormalSpeedPlaybackReachedEnd'] and flow['sampledContinuousFlowApproved'] and not flow['unresolved']
assert collection['actualCollectExitCode'] == 0 and collection['sourceAndOutputAllFourHashesEqual']
images = []
for name, reason in [
    ('private-settings-reopened-v1.png', 'Directly read actual new private ID, original illustrated thumbnail, SD/HD completion, saved title/description and no current notification.'),
    ('uploaded-game-cc-off-v1.png', 'Directly read actual 1080p60 upload at 40s with CC off: red aiming mark and blue post separate visible movement, fixed burned caption, original UI and source credit clear.'),
    ('uploaded-explanation-cc-off-v1.png', 'Directly read actual 1080p60 upload at 96.810479s with CC off: projected top/side faces and spatial comparison, helper-label margin and fixed Korean caption.')]:
    p = R + '/publishing/' + name
    images.append(dict(path=p, purpose='minimal-publishing-proof', reason=reason,
                       sha256=hashlib.sha256((ROOT / p).read_bytes()).hexdigest(), reviewedAt=now,
                       project='motion-sickness-games'))
review = dict(schemaVersion=1, actualVideoId=receipt['actualVideoId'], reviewedAt=now,
    originalThumbnailSavedReopenedAndDirectlyRead=True, privateSavedAndSdHdComplete=True,
    all358KoEnCueTextsAnd716VisibleTimesReopened=True,
    publishedCueComparison=R + '/publishing/published-cue-comparison-v3.json',
    actualPlatformMillisecondsRead=False, actualPlatformSrtDownloadCompleted=False,
    exactSourceSrtPreserved=True, koEnFullMetadataSavedReopenedAndDirectlyRead=True,
    actualCopyrightStatus='동영상에서 소유권 주장이 발견되지 않았습니다',
    actualCurrentMonetizationStatement='동영상에서 설정에 따라 수익을 창출하고 있습니다.',
    currentDetailsNotification='—', separateAdCompletionModalObserved=False,
    separateWizardCompletionModalObserved=False, cardCanonicalUrlAnd00TimeReopened=True,
    membershipEndScreen=dict(start60fps='10:59:53', end60fps='11:09:53', allThreeElementsReopened=True,
        evidence=R + '/publishing/member-timings-actual-ui-v2.json', memberIdentitiesAndTitleUnobscured=True,
        layoutImageLocalOnly=R + '/publishing/member-layout-reopened-local-only-v2.png'),
    uploadPixelReview=pixel, minimalReviewedImages=images,
    pending=['whole human listening and pronunciation', 'final public rights', 'original Nimbus external backup',
             'original truncated member handles', 'external media backup', 'automatic dubbing',
             'optional CC propagation', 'comment posting and pinning after public availability'],
    baselineChanged=False, mediaRegenerated=False, newUploadCount=1, gitDelivered=False, scheduled=False)
write(R + '/publishing/private-settings-direct-review-v1.json', review)
receipt.update(status='reviewed-private-settings-complete;selective-git-and-schedule-replacement-pending',
    uploaded=True, privateSaveVerified=True, fullSettingsVerified=True, automaticChecksPassed=True,
    burnedCaptionPixelsVerified=True, updatedAt=now, privateReviewEvidence=R + '/publishing/private-settings-direct-review-v1.json',
    currentChecks={k: review[k] for k in ['actualCopyrightStatus', 'actualCurrentMonetizationStatement', 'currentDetailsNotification', 'separateAdCompletionModalObserved', 'separateWizardCompletionModalObserved']})
receipt['thumbnail']['savedOnNewUpload'] = True
receipt['coachingCard'].update(saved=True, savedAndReopened=True, evidence=R + '/publishing/card-exact-url-reopened-v1.ax.txt')
receipt['endScreen'].update(saved=True, savedAndReopened=True, actualUiStart60fps='10:59:53', actualUiEnd60fps='11:09:53', evidence=review['membershipEndScreen']['evidence'])
for sub in receipt['subtitleFiles']:
    sub.update(status='manual-published;all-179-texts-and-visible-times-directly-read', savedAndReopened=True,
               allPlatformCueTimesReopened=True, cueComparison=review['publishedCueComparison'], actualPlatformSrtDownloadCompleted=False)
    if sub['language'] == 'ko':
        sub['downloadAttempt'] = read(R + '/publishing/ko-download-attempt-v3.json')
write(R + '/publishing/youtube-upload-v1.json', receipt)
cp = read(R + '/latest-checkpoint.json')
cp.update(recordedAt=now, stage='current-v2-private-settings-complete;selective-git-pending', uploaded=True,
    outputCollected=True, outputsCollected=True, actualReplacementVideoId=receipt['actualVideoId'],
    privateSettingsVerified=True, next='Selective normal Git delivery, then audit current baseline and replace its Oct12 09KST schedule. Preserve all published videos and pending human review.')
write(R + '/latest-checkpoint.json', cp)
queue = read(B + '/queue.json')
queue['updatedAt'] = now
queue['execution'].update(stage='motion-reviewed-private-settings-complete-selective-git-pending', actualNewVideoId=receipt['actualVideoId'], baselineScheduleChanged=False)
item = next(i for i in queue['items'] if i['slug'] == 'motion-sickness-games')
item['review']['privateSettingsVerified'] = True
item['reviewScopeNote'] = 'Current media, mixed ASR content, complete 1x flow, all final samples, output collection and actual private settings verified; selective Git and schedule replacement pending. Whole human listening/pronunciation and final public rights remain incomplete.'
item['replacementVideoIds'] = [receipt['actualVideoId']]
write(B + '/queue.json', queue)
manifest = read('projects/motion-sickness-games/project.json')
manifest['editing']['exampleInterleaving']['reviewStatus'] = 'Current teaching revision: all 1180 encoded cue/cut samples directly reviewed or proven byte-identical to directly reviewed prior samples; all179 KO/EN cues, tracked gameplay marks and whole1x flow reviewed. See current final-pixel-direct-review-v2 and final-flow-playback-direct-review-v2.'
write('projects/motion-sickness-games/project.json', manifest)
print(json.dumps(dict(actualVideoId=receipt['actualVideoId'], privateSettingsVerified=True, essentialImages=3,
                     gitDelivered=False, scheduled=False, baselineChanged=False, sharedForeignFilesWritten=0)))
