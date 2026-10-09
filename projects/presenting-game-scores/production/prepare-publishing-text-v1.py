"""Prepare reviewed bilingual text only; no media or platform receipt approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/presenting-game-scores/publishing'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
defaults = read(ROOT / 'shared/publishing/youtube-defaults.json')
ko = read(ROOT / 'projects/presenting-game-scores/script/narration.ko.json')
en = read(ROOT / 'projects/presenting-game-scores/script/narration.en.json')
assert [s['id'] for s in ko['scenes']] == [s['id'] for s in en['scenes']]
coaching = defaults['coaching']['url']
member = defaults['membershipUrl']
snapshot = (ROOT / defaults['description']['channelDefaultSnapshot']).read_text('utf-8-sig')
footer = snapshot.split('📚 수업 노트')[0].rstrip().rstrip('━').rstrip()
assert coaching in footer and member in footer
discord = 'https://discord.gg/wZuqe7fqkR'
assert discord in footer
body_ko = (
    '게임 점수는 무엇을 평가할까요? 테트리스 이펙트 커넥티드의 점수와 지운 줄 수를 비교하며, 진행량과 평가가 서로 다른 정보를 말하는 순간을 살펴봅니다.\n\n'
    '같은 줄 수의 서로 다른 점수, 상대와의 차이, 이번 행동의 알림과 누적 결과를 구분해 봅니다. 발라트로의 짧은 계산 장면을 통해 숫자 변화와 강조를 읽고, 내 게임의 성과 표시를 이름·단위·비교 기준으로 점검합니다.\n\n'
    '큰 숫자를 만드는 것만큼, 플레이어가 무엇을 잘했는지 읽을 수 있게 만드는 것도 중요합니다.'
)
body_en = (
    'What does a game score evaluate? Compare points and cleared lines in Tetris Effect: Connected to see why progress and evaluation can communicate different things.\n\n'
    'We examine equal line counts with different scores, differences from an opponent, and the distinction between an event notice and a running total. Short Balatro calculation closeups help us inspect changing numbers and emphasis, then audit a score display by its name, unit, and comparison reference.\n\n'
    'An understandable account of performance matters as much as an impressive-looking total.'
)
footer_en = (
    '🎮 YamYamCoding helps you build practical game-programming skills through design and implementation.\n\n'
    '🚀 Premium one-to-one coaching\n'
    'DirectX 11/12, Unity, Unreal Engine, computer graphics, PBR, shaders, rendering, game engines, and graphics research implementation.\n'
    + coaching + '\n\n'
    '💬 Community: questions, code reviews, feedback, and study materials\nDiscord\n' + discord
    + '\n\nYouTube membership\n' + member
)
for language, script, body, channel_footer, tags in [
    ('ko', ko, body_ko, footer, '#게임개발 #게임디자인 #게임점수'),
    ('en', en, body_en, footer_en, '#GameDevelopment #GameDesign #GameScores'),
]:
    description = body + '\n\n' + channel_footer + '\n\n' + tags + '\n'
    (BASE / f'description-body.{language}.txt').write_text(body + '\n', 'utf-8')
    (BASE / f'description-prepared.{language}.txt').write_text(description, 'utf-8')
    chapters = '\n'.join(f"- {s['title']}" for s in script['scenes'])
    md = (
        '# 게시 정보 초안 — 준비만 완료\n\n'
        '실제 음성 길이와 최종 편집 검수 후 실측 챕터를 추가한다. 업로드 또는 설정 저장의 증거가 아니다.\n\n'
        '## 제목\n\n' + script['title'] + '\n\n'
        '## 설명 초안\n\n' + description + '\n'
        '## 챕터 순서 — 시간 미측정\n\n' + chapters + '\n\n'
        '## 썸네일\n\n점수는 커졌는데 / 뭘 잘한 걸까?\n\n'
        '## 남은 검수\n\n최종 음성·혼합 ASR, 본편 60:40, 고정 자막 픽셀, 두 MP4 decode·PTS·동일 AAC, KO/EN SRT 4파일 수집, 실제 비공개 저장과 모든 가능한 설정 재열람.\n'
    )
    (BASE / f'youtube.{language}.md').write_text(md, 'utf-8')
comment = (
    '내 게임의 점수가 무엇을 세고 누구와 비교하는지, 이름·단위·기준을 적어 보세요. '
    '게임 프로그래밍을 함께 설계하고 구현하는 1:1 과외 안내: ' + coaching + '\n'
)
(BASE / 'pinned-comment.ko.txt').write_text(comment, 'utf-8')
files = [BASE / n for n in ['youtube.ko.md', 'youtube.en.md', 'description-body.ko.txt', 'description-body.en.txt', 'description-prepared.ko.txt', 'description-prepared.en.txt', 'pinned-comment.ko.txt', 'thumbnail-v2.png']]
proof = dict(
    schemaVersion=1, slug='presenting-game-scores', preparedAt=datetime.now(timezone.utc).isoformat(),
    status='prepared-only-before-measured-narration-and-final-media', actualVideoId=None, uploaded=False,
    titles={'ko': ko['title'], 'en': en['title']}, thumbnail='projects/presenting-game-scores/publishing/thumbnail-v2.png',
    files=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in files],
    plannedChapters=[dict(scene=s['id'], titleKo=s['title'], titleEn=t['title'], startSeconds=None) for s, t in zip(ko['scenes'], en['scenes'])],
    measuredChaptersPrepared=False, exactCanonicalLinks={'coaching': coaching, 'discord': discord, 'membership': member},
    channelIntroductionPreserved=True, unfilledChannelPlaceholdersOmitted=True, publicSourceCredits=False,
    privacy='private', scheduled=False, optionalKoEnTracks='manual upload after final four-file collection',
    card={'startSeconds': 0, 'url': coaching, 'saved': False},
    endScreen={'durationSeconds': 10, 'startSeconds': None, 'elements': defaults['endScreen']['elements'], 'saved': False},
    pinnedComment={'path': 'projects/presenting-game-scores/publishing/pinned-comment.ko.txt', 'status': 'pending-video-publication', 'posted': False, 'pinned': False},
    sourceClaimScope='Visible quantity/evaluation, live differences and brief calculation feedback; no complete scoring-table, optimal-strategy or final-win claim.',
    platformSettingsVerified=False, savedPlatformThumbnailVerified=False, manualSrtPublished=False,
    englishMetadataPublished=False, uploadedCcOffPixelsVerified=False, actualAdChecksComplete=False,
    localOnly=True, imagesGitAdded=0)
(BASE / 'publishing-text-preparation-v1.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('Prepared truthful KO/EN metadata and exact-link comment; measured chapters, actual ID and all platform gates remain pending.')
