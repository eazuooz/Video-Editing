"""Record the observed Studio delivery; never mutates a platform or media."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/ai-games-showcase-2026'
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
VIDEO_ID = '-mAIFr3z394'
URL = f'https://www.youtube.com/watch?v={VIDEO_ID}'
QA = 'production/local/elevenlabs-v2/qa/'
MASTER_HASH = 'cb5eb5267a43aff0aaedffcdbd2127bea6ab10facf5adab48beae58a72584432'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


receipt_path = PROJECT / 'publishing/youtube-upload.json'
receipt = read(receipt_path)
assert receipt['videoId'] == VIDEO_ID
master = ROOT / 'output/ai-games-showcase-2026/ai-games-showcase-2026.captioned.mp4'
assert hashlib.sha256(master.read_bytes()).hexdigest() == MASTER_HASH
receipt.update(status='uploaded-settings-saved-user-schedule-preserved', uploaded=True,
               videoId=VIDEO_ID, url=URL, scheduled=True, verifiedAt=NOW,
               privacyStatus='private-until-user-scheduled-publication', fullSettingsSaved=True)
receipt['userManagedSchedule'].update(time='08:00', timezone='Asia/Seoul',
    utcOffset='+09:00', scheduledAt='2026-10-20T08:00:00+09:00',
    userEvidence='내가 예약했어. 유지해', agentChangedSchedule=False,
    evidence=QA+'youtube-user-schedule.txt')
receipt['authorization']['userEvidence'] = '업로드해줘~ 제목 영상 자극적이고 검색잘되게 해주고 썸네일도!'
receipt['thumbnail'].update(status='applied-and-reopened-visually-verified',
    evidence=QA+'youtube-upload-complete.png')
receipt['englishMetadata']['status'] = 'published-and-reopened'
receipt['englishMetadata']['evidence'] = QA+'youtube-english-settings.txt'
for sub in receipt['subtitles']:
    sub['status'] = 'manual-upload-published-and-reopened'
    sub['cues'] = 63
receipt['subtitles'][0]['evidence'] = 'Studio language page: Korean source, manual upload; reopened subtitle editor shows current exact opening and timings.'
receipt['subtitles'][1]['evidence'] = QA+'youtube-english-settings.txt'
receipt['coachingCard'].update(status='saved-and-reopened',
    verifiedStart='0:00:00', evidence=QA+'youtube-card-reopened.txt',
    urlReadback='Exact canonical URL reopened in link dialog')
receipt['endScreen'].update(status='saved-and-reopened', fps=60,
    actualStartTimecode='5:02:56', actualEndTimecode='5:12:56',
    playlistName='도움이 되는 게임 개발 이야기', playlistSelection='Actual own-channel playlist selected in Studio; no guessed ID',
    subscribeChannelId='UCOgtkPoyC0VXhCs7Xk3jvjQ',
    memberIdentityClearance='Three elements in lower blank area; title, coaching text and right member names unobstructed',
    evidence=[QA+'youtube-endscreen-reopened.png', QA+'youtube-endscreen-reopened.txt'])
receipt['coachingEndingLink']['status'] = 'saved-and-reopened'
receipt['burnedCaptionVerification'].update(status='passed-on-uploaded-gameplay-and-explanation',
    playerCaptionsOff=True, playbackQuality='1080p60 HD selected and displayed',
    gameplaySeconds=40, explanationSeconds=90,
    evidence=[QA+'youtube-gameplay-40s.png', QA+'youtube-explanation-90s.png'])
receipt['playlist'] = {'name':'도움이 되는 게임 개발 이야기','status':'saved-and-reopened'}
receipt['metadataVerification'] = {'titleDescriptionTagsLanguage':'saved-and-reopened',
    'evidence':QA+'youtube-details-reopened.txt','videoLanguage':'ko',
    'titleAndThumbnailChangedTogether':True,'noRankingGuarantee':True}
receipt['pinnedComment']['status'] = 'pending-video-publication'
receipt['pinnedComment']['reason'] = 'Watch page explicitly says private videos do not support comments; preserve user schedule.'
receipt['platformFollowUps'] = [
    {'item':'Optional player CC availability','status':'pending-propagation',
     'detail':'Both manual tracks published in Studio; watch page initially reports captions unavailable. Burned Korean captions verified visible.'},
    {'item':'Automatic dubbing','status':'platform-processing-unreviewed',
     'detail':'English (US) and Indonesian automatic dubbing observed processing; not generated, changed or certified by this task.'},
    {'item':'Pinned comment','status':'pending-video-publication','text':'publishing/pinned-comment.ko.txt'}]
receipt['automaticNextVideo'] = False
write(receipt_path, receipt)

p = PROJECT / 'project.json'
d = read(p)
d['status'] = 'youtube-uploaded-user-scheduled'
d['publishing'].update(videoId=VIDEO_ID, youtubeUrl=URL, youtubeUploaded=True,
    youtubeSettingsSaved=True, scheduledAt='2026-10-20T08:00:00+09:00',
    scheduleOwner='user; explicitly confirmed to preserve', uploadReceipt='publishing/youtube-upload.json')
write(p,d)

p = PROJECT / 'production/checkpoint.json'
d = read(p)
d.update(updatedAt=NOW, stage='youtube-delivered-user-schedule-preserved',
    nextAction='Stop selected video. Preserve user Oct20 08:00 KST schedule. Comment only when available/authorized; no automatic next video.',
    publishingReceipt='publishing/youtube-upload.json')
d['delivery'].update(youtubeUploaded=True, youtubeVideoId=VIDEO_ID, youtubeUrl=URL,
    youtubeSettingsSaved=True, userScheduledAt='2026-10-20T08:00:00+09:00',
    userReview='accepted for upload by explicit user request; whole human listening not separately attested')
write(p,d)

p = PROJECT / 'publishing/drive-review.json'
d = read(p)
d.update(status='reviewed-for-upload-same-master-delivered-to-youtube', updatedAt=NOW)
d['humanReview']['userEvidence'] = '업로드해줘~ 제목 영상 자극적이고 검색잘되게 해주고 썸네일도!'
d['humanReview']['remaining'] = 'No separate human-listening attestation; not a blocker after explicit approval to upload this version.'
d['youtube'].update(uploaded=True, uploadAuthorized=True, videoId=VIDEO_ID, url=URL,
    approvedMasterSha256=MASTER_HASH, receipt='publishing/youtube-upload.json')
write(p,d)

p = PROJECT / 'production/review-ledger.json'
d = read(p)
d['updatedAt'] = NOW
for check in d['checks']:
    if check['name']=='Google Drive final review':
        check.update(status='user-accepted-for-upload',humanReview='explicit upload request accepted current version')
    elif check['name']=='YouTube':
        check.update(status='uploaded-settings-verified-user-schedule-preserved',
            videoId=VIDEO_ID,evidence='publishing/youtube-upload.json')
d['checks'] = [x for x in d['checks'] if x['name']!='title and thumbnail packaging']
d['checks'].append({'name':'title and thumbnail packaging','status':'pass',
    'evidence':['publishing/packaging-plan.json','publishing/thumbnail-v3.jpg',QA+'youtube-upload-complete.png'],
    'scope':'Original title and concept thumbnail; approved video/audio unchanged'})
write(p,d)

p = ROOT/'shared/publishing/video-worklist.json'
d = read(p)
r = next(r for r in d['rows'] if r.get('slug')=='ai-games-showcase-2026')
r.update(title=receipt['metadata']['title'],reviewStatus='사용자 승인 완료',
    humanApproval='Drive v2 확인 후 업로드 지시; 전체 청취 별도 진술 없음',
    platformStatus='YouTube 업로드 완료 · 사용자 예약 10월20일 08:00 유지',
    videoId=VIDEO_ID,url=URL,executionStatus='업로드·한영 자막·새 제목/썸네일·카드/엔딩 설정 완료',
    driveStatus='v2 업로드·1080p 재생 확인 / 사용자 업로드 승인',
    notes='지정6게임 소개. ElevenLabs 샘플B·1080p60·5분13초. 사용자 직접 설정한 10월20일08시 예약 유지. 비공개 댓글 및 선택형CC 전파 후속; 다음 편 자동 착수 없음.')
e='projects/ai-games-showcase-2026/publishing/youtube-upload.json'
if e not in r['evidence']:r['evidence'].append(e)
write(p,d)
subprocess.run([__import__('sys').executable,str(ROOT/'scripts/render-video-worklist.py')],cwd=ROOT,check=True)

p = PROJECT/'publishing/packaging-plan.json'
d = read(p)
d['thumbnail']['status']='published-and-reopened'
d.update(actualVideoId=VIDEO_ID, appliedAt=NOW,
    publication='User-controlled schedule2026-10-20T08:00:00+09:00 retained')
write(p,d)
print(json.dumps({'videoId':VIDEO_ID,'schedulePreserved':'2026-10-20T08:00:00+09:00','masterUnchanged':True},ensure_ascii=False))
