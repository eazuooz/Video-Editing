"""Record actual, directly inspected Studio evidence after a lecture upload.

This does not upload, publish, change settings, or waive human/IP review.
Run only after inspecting the uploaded pixels and saved membership layout.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, re

root = Path(__file__).resolve().parents[3]
specs = {
    'game-math-euler-axis-angle': ('iv9esV7vv_g', '18:41:25', '18:51:25', 253),
    'game-math-quaternion-operations': ('03OXtik2nes', '19:18:05', '19:28:05', 226),
    'game-math-rotation-interpolation': ('mGBYkpSC9Mw', '18:59:45', '19:09:45', 249),
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('slug')
parser.add_argument('--video-id', help='Actual new Studio video ID; required for lectures without a preserved legacy receipt specification.')
parser.add_argument('--uploaded-pixels-reviewed', action='store_true', required=True)
parser.add_argument('--member-layout-reviewed', action='store_true', required=True)
parser.add_argument('--playback-seconds', type=int, required=True)
args = parser.parse_args()
slug = args.slug
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
write = lambda p, v: p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
pub = root / f'projects/{slug}/publishing/youtube-upload.json'
u = read(pub)
if slug in specs:
    video_id, start_tc, end_tc, cue_count = specs[slug]
    if args.video_id: assert args.video_id == video_id
else:
    assert args.video_id and re.fullmatch(r'[A-Za-z0-9_-]{11}',args.video_id)
    queue=read(Path(__file__).with_name('queue.json'))
    assert any(x['slug']==slug for x in queue['items'])
    video_id=args.video_id
    timeline=read(root/f'projects/{slug}/production/timeline.json')
    assert timeline['fps']==60 and timeline['outroSeconds']==10
    def timecode(frames):
        minutes,remaining=divmod(frames,3600);seconds,frame=divmod(remaining,60)
        return f'{minutes:02}:{seconds:02}:{frame:02}'
    start_tc=timecode(timeline['frames']-600);end_tc=timecode(timeline['frames'])
    cue_count=len(timeline['koCaptions'])
    # Studio can display the inclusive last visible frame rather than the
    # exclusive MP4 boundary. Accept that exact adjacent frame only; keep the
    # ten-second source range and each element's actual platform range distinct.
    last_visible_tc=timecode(timeline['frames']-1)
qa = root / f'shared/output/{slug}/qa'
assert u['videoId'] == video_id and u['metadata']['privacyStatus'] == 'private'
assert 0 < args.playback_seconds < u['video']['seconds'] - 10
coach = 'https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328'

def proof(name):
    p = qa / name
    assert p.is_file(), f'Missing actual evidence: {p}'
    return p.read_text(encoding='utf8')

def dialog_only(text, name):
    marker = f'container Description: {name}, ID: dialog'
    assert marker in text, f'Missing native {name} dialog'
    return text[text.index(marker):]

details = proof('studio-private-details.ax.txt')
assert video_id in details and f'{slug}.captioned.mp4' in details and 'text 비공개' in details
assert 'button (disabled) 저장' in details
checks = proof('studio-checks-complete.ax.txt')
compact = re.sub(r'\s+', '', checks)
legacy_completed_checks = '저작권검사완료발견된문제없음광고적합성검사완료발견된문제없음' in compact
if not legacy_completed_checks:
    # The current Studio content list combines checks under "Notices". Accept
    # that actual completed state only with fresh, video-specific copyright
    # and active monetization pages. Never synthesize an old wizard snapshot.
    assert video_id in checks and u['metadata']['title'] in checks
    assert 'text 알림 없음' in checks and '검토중' not in compact
    copyright_state = proof('studio-copyright-no-claims.ax.txt')
    assert video_id in copyright_state
    assert '동영상에서 소유권 주장이 발견되지 않았습니다' in copyright_state
    assert '동영상에서 저작권 보호 콘텐츠가 발견되지 않았습니다.' in copyright_state
    assert '수익에 영향을 미치지 않음' in copyright_state
    completed_monet = proof('studio-monetization-saved.ax.txt')
    assert video_id in completed_monet and 'text 사용' in completed_monet
    assert '검사 중' not in completed_monet and 'button (disabled) 저장' in completed_monet
watch = proof('uploaded-cc-off.ax.txt')
assert video_id in watch and u['metadata']['title'] in watch
assert any('checkbox' in line and '자막' in line and 'Value: 0' in line for line in watch.splitlines())
assert (qa / 'uploaded-cc-off.png').is_file() and (qa / 'studio-end-screen-saved.png').is_file()
platform_end_tcs=[]
for kind, label in [('subscribe', '구독 요소'), ('playlist', '재생목록 요소'), ('link', '링크 요소')]:
    text = dialog_only(proof(f'studio-end-{kind}.ax.txt'), '최종 화면')
    assert label in text and start_tc in text
    accepted_end=end_tc if end_tc in text else (last_visible_tc if slug not in specs and last_visible_tc in text else None)
    assert accepted_end, 'Native end time must equal the MP4 boundary or its inclusive last visible frame'
    platform_end_tcs.append(accepted_end)
    assert 'button (disabled) 저장' in text
    assert '게임 수학(Game Math) PART 2' in text
    if kind == 'link':
        assert coach in text and '프로그래밍 과외' in text
assert len(set(platform_end_tcs))==1, 'All three elements must use the same actual end frame'
card = dialog_only(proof('studio-coaching-card-saved.ax.txt'), '카드')
assert '티저 시작 시간: 0분 0초 0프레임' in card and 'button (disabled) 저장' in card
assert card.count('Value: 프로그래밍 과외') >= 3
assert coach in proof('studio-coaching-card-url-saved.ax.txt')
english = proof('studio-english-metadata-saved.ax.txt')
assert u['englishMetadata']['title'] in english and u['englishMetadata']['description'] in english
assert '수동 자막' in english and '게시됨' in english
english_heading = re.search(r'heading (영어(?:\(미국\))?), Value: 1', english)
assert english_heading, 'Missing actual saved English language heading'
english_language = 'en-US' if english_heading.group(1) == '영어(미국)' else 'en'
if slug not in specs:
    korean = dialog_only(proof('studio-korean-subtitles-saved.ax.txt'), '한국어 세부정보')
    assert 'heading 한국어, Value: 1' in korean
    assert '수동 자막' in korean and 'text 수동' in korean and 'text 게시됨' in korean
    assert 'button (disabled) 업데이트' in korean
monet = proof('studio-monetization-saved.ax.txt')
assert 'text 사용' in monet and '미드롤 광고 게재, Value: 1' in monet and 'button (disabled) 저장' in monet
assert u['thumbnail']['status'] == 'saved-and-reopened-preview-verified'

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
u['url']=f'https://youtu.be/{video_id}'
proofs = []
for p in sorted(qa.iterdir()):
    if p.is_file() and (p.name.startswith('studio-') or p.name.startswith('uploaded-cc-off')):
        proofs.append({'path': p.relative_to(root).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
u.update(status='private-upload-saved-and-settings-verified', privateVisibilitySaveVerified=True,
         uploadTransferComplete=True, fullPublishingSettingsComplete=True, fullSettingsVerified=True,
         verifiedAtUtc=now)
u['burnedCaptionVerification'].update(status='passed-direct-uploaded-pixel-review',
    playerCaptionsOff=True, actualPlaybackSeconds=args.playback_seconds,
    proof=f'shared/output/{slug}/qa/uploaded-cc-off.png',
    captionControl='Native watch-page caption checkbox Value0; actual burned KO text directly inspected')
for track in u['subtitles']:
    track.update(cueCount=cue_count, platformLanguage='ko' if track['language']=='ko' else english_language,
                 status='manual-published-and-reopened-verified')
u['englishMetadata']['language'] = english_language
u['coachingCard']['status'] = 'saved-and-reopened-exact-URL-and00:00:00-verified'
u['endScreen'].update(status='saved-and-reopened-verified', startTimecode=start_tc,
    endTimecode=end_tc, timecodeFps=60, memberIdentitiesUnobscured=True,
    platformEndTimecode=platform_end_tcs[0],
    platformEndBoundary='exclusive-source-boundary' if platform_end_tcs[0]==end_tc else 'inclusive-last-visible-source-frame',
    privateWatchPageSuppressesEndScreen=True, playlistId='PLWKwcHKTXy5Soue4YKXa-dsXMV71BVGRk')
u['coachingEndingLink']['status'] = 'saved-and-reopened-verified'
u['monetization'].update(automaticAdSuitability='automatic-check-complete-no-issues-observed',
    copyrightChecks='automatic-check-complete-no-issues-observed',
    checkEvidence=f'shared/output/{slug}/qa/studio-checks-complete.ax.txt')
u['platformEvidence'] = {'verifiedAtUtc': now, 'proofs': proofs, 'actualFileName': f'{slug}.captioned.mp4'}
u['platformProcessing'] = {
    'watchPagePlaybackVerified': True,
    'nativeDetails': [line.strip() for line in details.splitlines() if 'video-resolutions' in line or 'badge-sd' in line or 'badge-hd' in line],
    'automaticDubbing': 'Platform-managed; no agent-uploaded English audio and no claim of listening review',
}
u['pending'] = ['Human full listening', 'Public game-IP review', 'Truncated member handles',
                'Coaching comment post/pin after comments become available']
assert u['pinnedComment']['commentId'] is None and u['pinnedComment']['pinnedVerified'] is False
write(pub, u)

manifest_path = root / f'projects/{slug}/project.json'
manifest = read(manifest_path)
manifest['publishing'].update(privateUploadComplete=True, fullPublishingSettingsComplete=True,
    videoId=video_id, url=u['url'], receipt=pub.relative_to(root).as_posix(), verifiedAtUtc=now)
manifest['publishReady'] = False
write(manifest_path, manifest)
queue_path = Path(__file__).with_name('queue.json')
queue = read(queue_path)
item = next(x for x in queue['items'] if x['slug']==slug)
item.update(status='private-upload-saved', privateUploadComplete=True,
    fullPublishingSettingsComplete=True, videoId=video_id, url=u['url'], checkpointAt=now,
    checkpoint='Actual private captioned upload pixels, both manual SRTs, exact English metadata, thumbnail, Part2 playlist, coaching card, three60fps membership end elements, ads and automatic checks verified. Human listening, public game-IP/member review and private comment/pin remain pending.')
write(queue_path, queue)
print(json.dumps({'slug':slug, 'videoId':video_id, 'privateUploadComplete':True,
    'fullPublishingSettingsComplete':True, 'publicPublishingAuthorized':False, 'proofs':len(proofs)}))
