"""Prepare measured bilingual metadata only; no upload or receipt completion."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PUB = BASE.parent / 'publishing'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan_path = BASE / 'final-v1/plan.json'
plan = read(plan_path)
manifest = read(BASE.parent / 'project.json')
defaults_path = ROOT / 'shared/publishing/youtube-defaults.json'
defaults = read(defaults_path)
titles = {
    '01-overview': ('이번 영상의 질문과 순서', 'Our question and route'),
    '02-familiar-action': ('비슷한 행동은 출발점', 'Familiar actions are a starting point'),
    '03-patterns-not-ranking': ('공격 패턴을 한 줄 순위로 줄이지 않기', 'Read attack patterns before ranking'),
    '04-mining-route': ('이동에 채굴 목적이 붙을 때', 'Movement with a mining goal'),
    '05-route-under-pressure': ('목적과 추격을 함께 읽기', 'Read goals and pursuit together'),
    '06-follow-the-space': ('좁은 길과 통과할 틈 관찰하기', 'Observe passages and gaps'),
    '07-purpose-combination': ('익숙한 행동 위에 관계 쌓기', 'Build relationships around familiar actions'),
    '08-world-and-route': ('공간과 분위기를 플레이에 연결하기', 'Connect space and atmosphere to play'),
    '09-combination-in-motion': ('목적지와 위험을 함께 읽기', 'Read destinations and danger'),
    '10-playing-together': ('함께 하는 플레이의 관계', 'Relationships in shared play'),
    '11-several-appeals': ('여러 매력과 서로 다른 선택 이유', 'Several appeals and different reasons to choose'),
    '12-check-your-reason': ('내 게임을 고를 이유 한 문장', 'One sentence about choosing your game'),
    '13-conclusion': ('익숙함에서 자기 경험으로', 'From familiarity to your own experience'),
}


def stamp(seconds):
    integer = math.floor(seconds)
    return f'{integer // 60:02d}:{integer % 60:02d}'


chapters = []
for scene in plan['scenes']:
    if scene['id'] in titles:
        frame = 0 if scene['id'] == '01-overview' else scene['startFrame']
        ko, en = titles[scene['id']]
        chapters.append(dict(scene=scene['id'], startFrame=frame, seconds=frame / 60,
                             displayedTimestamp=stamp(frame / 60), titleKo=ko, titleEn=en))
chapters.append(dict(scene='membership', startFrame=36498, seconds=608.3,
                     displayedTimestamp='10:08', titleKo='멤버쉽가입 감사드립니다.', titleEn='Thank you to our members'))
assert len(chapters) == 14 and chapters[0]['startFrame'] == 0
assert all(y['startFrame'] - x['startFrame'] >= 600 for x, y in zip(chapters, chapters[1:]))
assert 37098 - chapters[-1]['startFrame'] == 600
body_ko = '''좋아하는 게임과 비슷한 게임을 만들 때, 플레이어가 내 작품을 새로 선택할 이유는 무엇일까요?

브로테이토의 경기장, 딥록 갤럭틱 서바이버의 채굴 경로, 함께 하는 플레이를 차례로 관찰합니다. 익숙한 이동과 공격에 어떤 목적과 상황이 연결되는지 입체 설명으로 비교하고, 내 게임을 선택할 이유를 한 문장으로 점검합니다.

기능을 한 줄 순위로 줄이기보다, 플레이어가 읽을 공간과 판단할 상황을 구체적으로 설계해 보세요.'''
body_en = '''If you start from a game you love, why would players choose your new game?

Observe Brotato's arenas, mining routes in Deep Rock Galactic: Survivor, and playing together. Compare the purposes and situations connected to familiar movement and attacks through spatial illustrations, then describe a reason to choose your own game in one sentence.

Design what players will notice and decide instead of reducing features to a single ranking.'''
chapter_ko = '\n'.join(f'{x["displayedTimestamp"]} {x["titleKo"]}' for x in chapters)
chapter_en = '\n'.join(f'{x["displayedTimestamp"]} {x["titleEn"]}' for x in chapters)
footer_path = ROOT / defaults['description']['channelDefaultSnapshot']
footer_ko = footer_path.read_text('utf-8-sig').split('📚 수업 노트')[0].strip()
footer_en = f'''🎮 Build games with real programming skills.

YamYamCoding is a Korean game-programming channel covering DirectX, Unity, Unreal Engine and computer graphics.

━━━━━━━━━━━━━━━━━━

🚀 Premium 1:1 programming coaching

Learn to design and implement real projects with guided feedback.
DirectX11 / DirectX12 · Unity / Unreal Engine · Computer Graphics & PBR · Shaders / Rendering · Game engines · Graphics papers and implementation

Programming coaching
{defaults['coaching']['url']}

━━━━━━━━━━━━━━━━━━

💬 YamYamCoding community

Questions, code reviews, feedback and course materials.

Discord
https://discord.gg/wZuqe7fqkR

YouTube channel membership
{defaults['membershipUrl']}

━━━━━━━━━━━━━━━━━━'''
description_ko = body_ko + '\n\n챕터\n' + chapter_ko + '\n\n' + footer_ko
description_en = body_en + '\n\nChapters\n' + chapter_en + '\n\n' + footer_en
for title, description in [(manifest['titles']['ko'], description_ko), (manifest['titles']['en'], description_en)]:
    assert len(title) <= 100 and len(description) <= 5000
    for url in [defaults['coaching']['url'], defaults['membershipUrl'], 'https://discord.gg/wZuqe7fqkR']:
        assert url in description
assert defaults['coaching']['url'] in (PUB / 'pinned-comment.ko.txt').read_text('utf-8-sig')
prepared = dict(schemaVersion=1, preparedAt=datetime.now(timezone.utc).isoformat(), status='prepared-only-awaiting-final-QA-and-collection',
                slug='similar-game-design', planSha256=sha(plan_path), defaultsSha256=sha(defaults_path),
                footerSnapshotSha256=sha(footer_path), frames=37098, seconds=618.3, chapters=chapters,
                metadata=dict(title=manifest['titles']['ko'], description=description_ko, language='ko', privacyStatus='private'),
                englishMetadata=dict(title=manifest['titles']['en'], description=description_en, language='en', saved=False),
                thumbnail=dict(path='projects/similar-game-design/publishing/thumbnail-v1.png', sha256=sha(PUB / 'thumbnail-v1.png'), saved=False),
                plannedVideoPath='output/similar-game-design/similar-game-design.captioned.mp4', videoHash=None,
                plannedSubtitlePaths=['output/similar-game-design/similar-game-design.ko.srt', 'output/similar-game-design/similar-game-design.en.srt'],
                subtitleMethod='manual-file-upload-with-timing', burnedCaptions=dict(center=[960, 970], ccOffUploadedPixelsVerified=False),
                coachingCard=dict(url=defaults['coaching']['url'], startSeconds=0, saved=False),
                endScreen=dict(startFrame=36498, startSeconds=608.3, endSeconds=618.3,
                               elements=defaults['endScreen']['elements'], saved=False),
                pinnedComment=dict(path='projects/similar-game-design/publishing/pinned-comment.ko.txt',
                                   status='pending-video-publication', actualCommentId=None, pinnedVerified=False),
                actualVideoId=None, uploaded=False, scheduled=False, fullSettingsVerified=False,
                qaApproved=False, collected=False, externalPlatformWrites=0)
(PUB / 'prepared-publishing-v1.json').write_text(json.dumps(prepared, ensure_ascii=False, indent=2) + '\n', 'utf-8')
(PUB / 'upload-description-draft.ko.txt').write_text(description_ko + '\n', 'utf-8')
(PUB / 'upload-description-draft.en.txt').write_text(description_en + '\n', 'utf-8')
print(json.dumps(dict(preparedOnly=True, chapters=14, koreanCharacters=len(description_ko), englishCharacters=len(description_en),
                     actualVideoId=None, uploaded=False), ensure_ascii=False))
