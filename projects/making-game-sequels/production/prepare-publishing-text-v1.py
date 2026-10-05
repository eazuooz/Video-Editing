"""Prepare measured metadata; do not create an upload receipt or platform completion."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
DEST = BASE.parent / 'publishing'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
plan = read(BASE / 'final-v1/plan.json')
project = read(BASE.parent / 'project.json')
defaults = read(ROOT / 'shared/publishing/youtube-defaults.json')
assert plan['finalFrames'] == 35583 and plan['finalTimingApproved'] and plan['bodyRatioApproved']
DEST.mkdir(exist_ok=True)
assert not (DEST / 'youtube-upload.json').exists()
ko_titles = ['고양이 로고와 영상 안내', '벽에 배치하고 직접 막기', '제작 재사용과 다시 할 이유',
    '공통 활동 옆의 전투 도구', '추가한 개수보다 달라진 결정', '놓을 자리와 방향',
    '거리와 위치가 바꾸는 판단', '익숙함의 약속을 먼저 적기', '다른 공간에서도 준비하기',
    '선택이 나타나는 시점', '준비 뒤의 전투 관찰', '두 종류의 플레이어로 확인하기',
    '실제 행동으로 속편 기획 정리', '멤버쉽가입 감사드립니다.']
en_titles = ['Channel intro and video overview', 'Wall placement and direct defence',
    'Production reuse and a reason to return', 'Combat tools beside shared activities',
    'Changed decisions rather than added counts', 'Placement and orientation',
    'Decisions at different distances and positions', 'Write the promise of familiarity',
    'Preparation in another space', 'When a choice appears', 'Observe combat after preparation',
    'Check with returning and first-time players', 'Summarize a sequel through visible actions', 'Membership thanks']
frames = [0] + [scene['startFrame'] for scene in plan['scenes'][1:]] + [plan['finalFrames'] - 600]
assert len(frames) == len(ko_titles) == len(en_titles) == 14
timestamp = lambda frame: f'{frame // 3600:02d}:{frame // 60 % 60:02d}'
chapters_ko = [timestamp(frame) + ' ' + title for frame, title in zip(frames, ko_titles)]
chapters_en = [timestamp(frame) + ' ' + title for frame, title in zip(frames, en_titles)]
ko_body = '''익숙한 게임의 다음 작품에서는 무엇을 남기고 무엇을 바꿔야 다시 할 이유가 생길까요? 제작에서 재사용할 부분과 플레이어가 새로 결정할 부분을 나누어 자신의 속편 기획을 점검합니다.

오크스 머스트 다이! 2·3와 데스트랩의 함정 배치, 겨누기와 전투를 살펴봅니다. 유지할 핵심 행동을 먼저 적고, 도구·공간·선택 시점을 바꾸었을 때 어떤 판단이 달라질지 질문합니다. 마지막에는 전작을 아는 사람과 처음 보는 사람이 이해하고 선택할 수 있는지 확인할 검증 과제를 정리합니다.

실제 플레이에서 보인 행동과 우리의 기획 제안을 구별합니다. 별도 전투 컷을 하나의 연속 결과로 연결하거나, 화면만으로 개발사의 내부 코드·비용·의도·매출·최적 전략을 증명하지 않습니다. 두 갈래 길과 플레이어 검증 예시는 우리가 제안하는 연습입니다.'''
en_body = '''What should a familiar game's next installment retain and change to give players a reason to return? Separate what production might reuse from the decisions players will make anew, then use that distinction to check your sequel concept.

We examine trap placement, aiming and combat in Orcs Must Die! 2, Orcs Must Die! 3 and Deathtrap. First write the core activities to retain, then ask how tools, spaces and the timing of choices might change decisions. Finally, outline a test with returning and first-time players to check understanding and meaningful choices.

We distinguish visible gameplay from our design proposals. Separate combat shots do not establish one continuous result, and gameplay alone does not prove a developer's internal code, costs, intentions, sales or an optimal strategy. The branching-lane and player-check examples are our proposed exercises.'''
previous = ROOT / 'projects/avoid-game-comparisons/publishing'
ko_footer = (previous / 'description.ko.txt').read_text(encoding='utf-8-sig').split('🎮', 1)[1].rsplit('\n#', 1)[0]
en_footer = (previous / 'description.en.txt').read_text(encoding='utf-8-sig').split('🎮', 1)[1].rsplit('\n#', 1)[0]
ko = ko_body + '\n\n' + '\n'.join(chapters_ko) + '\n\n🎮 ' + ko_footer.strip() + '\n\n#게임개발 #게임기획 #속편기획\n'
en = en_body + '\n\n' + '\n'.join(chapters_en) + '\n\n🎮 ' + en_footer.strip() + '\n\n#GameDevelopment #GameDesign #GameSequels\n'
for text in [ko, en]:
    assert defaults['coaching']['url'] in text and defaults['membershipUrl'] in text
    assert 'https://discord.gg/wZuqe7fqkR' in text and len(text) < 5000
    assert '여기에-GitHub-주소' not in text and '노션 또는 강의 자료 링크' not in text
for language, text in [('ko', ko), ('en', en)]:
    (DEST / f'description.{language}.txt').write_text(text, encoding='utf-8')
    (DEST / f'youtube.{language}.md').write_text('# ' + project['titles'][language] + '\n\n' + text, encoding='utf-8')
comment = '속편 기획에서는 유지할 행동, 바꿀 조건, 확인할 선택을 함께 적어 보세요. 직접 설계하고 구현하는 게임 프로그래밍을 1:1로 점검하고 싶다면 과외 안내를 확인하세요.\n' + defaults['coaching']['url'] + '\n'
(DEST / 'pinned-comment.ko.txt').write_text(comment, encoding='utf-8')
metadata = dict(status='prepared-text-only-final-QA-and-upload-pending', preparedAt=datetime.now(timezone.utc).isoformat(),
    titleKo=project['titles']['ko'], titleEn=project['titles']['en'], chaptersKo=chapters_ko, chaptersEn=chapters_en,
    chapterStartsFrames=frames, frames=35583, seconds=593.05,
    plan='projects/making-game-sequels/production/final-v1/plan.json',
    planSha256=hashlib.sha256((BASE / 'final-v1/plan.json').read_bytes()).hexdigest(),
    descriptionKo='projects/making-game-sequels/publishing/description.ko.txt',
    descriptionEn='projects/making-game-sequels/publishing/description.en.txt',
    privacy='private', schedule=None, actualVideoId=None, uploaded=False, fullSettingsVerified=False,
    publicSourceBlock=False, preservedChannelFooter=True, pinnedCommentStatus='prepared-pending-video-publication',
    outro=dict(fromFrame=34983, toFrameExclusive=35583, startSeconds=583.05, endSeconds=593.05,
               hd60StartUi='9:43:03', hd60InclusiveEndUi='9:53:02', actualPlatformTimingVerified=False),
    thumbnailLimitNonblocking=True, humanListening='pending', finalQaApproved=False)
(DEST / 'metadata-prepared.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(chapters=14, seconds=593.05, uploaded=False, receiptCreated=False), ensure_ascii=False))
