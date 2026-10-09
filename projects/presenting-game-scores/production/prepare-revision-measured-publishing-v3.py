"""Prepare revision-only measured metadata, including the approved recorder credit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[3]
P = Path(__file__).resolve().parent.parent
B = P / 'production/revision-balatro60-v2'
F = B / 'final-v3'
PUB = B / 'publishing'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan = read(F / 'plan.json')
prior = read(P / 'publishing/publishing-text-preparation-v1.json')
approval = read(B / 'description-credit-approval-v1.json')
assert plan['finalTimingApproved'] and plan['allInputSegmentCaptionPixelsReviewed']
assert (plan['finalFrames'], plan['actualFrames'], plan['balatroFrames']) == (19988,11561,6936)
assert not (PUB / 'publishing-text-preparation-v3.json').exists()
credit = {lang:(PUB / f'description-credit.{lang}.txt').read_text('utf-8-sig').strip() for lang in ['ko','en']}
assert credit['ko'].startswith('플레이 녹화: Squeaky Whale Gameplay Archive — https://www.youtube.com/channel/')
assert 'UCoMF_6EsJYSq8vWG8zqRvtA' in credit['en']
chapters=[]
for index,(actual,old) in enumerate(zip(plan['chapters'],prior['plannedChapters'])):
    assert actual['id'] == old['scene'][:2]
    seconds=0 if index==0 else math.floor(actual['startFrame']/60)
    chapters.append(dict(scene=old['scene'],titleKo=old['titleKo'],titleEn=old['titleEn'],
        startFrame=0 if index==0 else actual['startFrame'],narrationChapterStartFrame=actual['startFrame'],
        narrationChapterExactSeconds=actual['startFrame']/60,displaySeconds=seconds,
        timestamp=f'{seconds//60:02d}:{seconds%60:02d}'))
t=math.floor(plan['membershipStartFrame']/60)
chapters.append(dict(scene='membership',titleKo='멤버십 감사 인사',titleEn='Membership thanks',
    startFrame=plan['membershipStartFrame'],narrationChapterStartFrame=plan['membershipStartFrame'],
    narrationChapterExactSeconds=plan['membershipStartFrame']/60,displaySeconds=t,timestamp=f'{t//60:02d}:{t%60:02d}'))
assert len(chapters)==11 and all(b['displaySeconds']-a['displaySeconds']>=10 for a,b in zip(chapters,chapters[1:]))
bodies={
 'ko':'게임 점수는 무엇을 평가할까요? 테트리스 이펙트 커넥티드에서 지운 줄 수와 평가 점수를 비교한 뒤, 발라트로의 카드 기여와 손패 계산, 라운드 누적값을 살펴봅니다.\n\n선택한 카드와 실제 점수를 만드는 카드는 어떻게 다를까요? 이번 손패의 결과와 라운드 점수, 넘어야 할 목표를 나누어 읽고, 숫자의 이름·단위·비교 기준과 피드백 순서를 점검합니다.\n\n발라트로와 테트리스의 실제 게임 구간을 6:4로 구성했습니다. 검정 배경의 입체 설명과 게임 장면을 번갈아 보며, 플레이어가 다음 행동을 판단할 수 있는 점수 화면을 설계해 봅니다.',
 'en':'What does a game score evaluate? Compare cleared lines and evaluation scores in Tetris Effect: Connected, then examine card contributions, hand calculations, and round totals in Balatro.\n\nWhich selected cards actually contribute to the score? Distinguish the current hand result, round score, and target, then audit names, units, comparison references, and the order of feedback.\n\nThe actual gameplay portions use a 60:40 Balatro-to-Tetris balance. Alternating gameplay and spatial explanations on a black background, we explore score displays that help players choose their next action.'}
titles=dict(ko='게임 점수 디자인: 이름·단위·비교 기준으로 읽는 성과',en='Game Score Design: Names, Units, and Comparisons')
files=[]
for lang in ['ko','en']:
    original=(P / f'publishing/description-prepared.{lang}.txt').read_text('utf-8-sig').strip()
    oldbody=(P / f'publishing/description-body.{lang}.txt').read_text('utf-8-sig').strip()
    assert original.startswith(oldbody)
    footer=original[len(oldbody):]
    assert all(url in footer for url in prior['exactCanonicalLinks'].values())
    header='챕터' if lang=='ko' else 'Chapters'
    chaptertext='\n'.join(c['timestamp']+' '+c['titleKo' if lang=='ko' else 'titleEn'] for c in chapters)
    final=bodies[lang]+'\n\n'+header+'\n'+chaptertext+'\n\n'+credit[lang]+footer+'\n'
    assert final.count('UCoMF_6EsJYSq8vWG8zqRvtA')==1 and len(final)<5000
    for name,content in [('description-body-v3',bodies[lang]+'\n'),('description-measured-v3',final),('title-measured-v3',titles[lang]+'\n')]:
        p=PUB / f'{name}.{lang}.txt';p.write_text(content,'utf-8')
        files.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
proof=dict(schemaVersion=3,slug='presenting-game-scores',preparedAt=datetime.now(timezone.utc).isoformat(),
    status='revision-measured-metadata-prepared-only-final-QA-and-platform-save-pending',titles=titles,files=files,
    measuredChapters=chapters,planSha256=sha(F/'plan.json'),durationSeconds=plan['durationSeconds'],finalFrames=plan['finalFrames'],
    exactCanonicalLinks=prior['exactCanonicalLinks'],existingChannelIntroductionPreserved=True,
    descriptionCreditException=dict(approvalPath=(B/'description-credit-approval-v1.json').relative_to(ROOT).as_posix(),
        approvalSha256=sha(B/'description-credit-approval-v1.json'),userAnswer='응 넣어',scope='This Balatro60:Tetris40 revision only',lines=credit),
    card=prior['card'],endScreen=dict(prior['endScreen'],startSeconds=plan['membershipStartFrame']/60,endSeconds=plan['durationSeconds'],saved=False),
    thumbnail='projects/presenting-game-scores/publishing/thumbnail-v2.png',
    midroll=dict(eligible=False,reason='333.133333 seconds is below eight minutes'),
    targetSchedule=dict(date='2026-10-28',time='09:00',timezone='Asia/Seoul',planningOnly=True,actualVideoId=None),
    actualVideoId=None,uploaded=False,platformSettingsVerified=False,savedPlatformThumbnailVerified=False,
    actualAdChecksComplete=False,finalMixedAsrApproved=False,allFinalPixels=False)
(PUB/'publishing-text-preparation-v3.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(chapters=chapters,files=files,credit=credit,uploaded=False),ensure_ascii=False))
