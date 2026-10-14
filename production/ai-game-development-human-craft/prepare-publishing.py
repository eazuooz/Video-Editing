"""Prepare text only; no YouTube or Drive mutation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
P=ROOT/'projects'/SLUG/'publishing';P.mkdir(exist_ok=True)
data=json.loads((ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json').read_text(encoding='utf-8'))
assert data['captionTimingStatus']=='asr-aligned'
defaults=json.loads((ROOT/'shared/publishing/youtube-defaults.json').read_text(encoding='utf-8'))
footer=(ROOT/defaults['description']['channelDefaultSnapshot']).read_text(encoding='utf-8').split('📚 수업 노트')[0].strip()
groups=[('01','AI 시대, 배운 실력의 가치','What skills mean in the AI era'),('02','사람과 AI를 위한 개발 도구','Tools for people and AI'),
('07','자동화가 바꾸는 일과 가치','Automation, work and value'),('10','만들기 쉬워진다는 것','A wider doorway to creation'),
('11','직접 만드는 과정의 의미','The meaning of making things'),('16','시연과 제품의 차이','From a demo to a product'),
('17','상점 구매로 확인하는 조건','Testing a shop transaction'),('19','검증 기준과 게임의 느낌','Validation and game feel'),
('22','오래 기억되는 표현과 스타일','Lasting style and expression'),('25','새 도구를 판단하는 기술','Judgment behind the tools'),
('28','여러분의 경험은 어떤가요?','What has your experience been?')]
def clock(t):
 n=int(t);return f'{n//3600}:{n//60%60:02}:{n%60:02}' if n>=3600 else f'{n//60:02}:{n%60:02}'
chapters={lang:'\n'.join(f"{clock(0 if sid=='01' else 2+next(s['start'] for s in data['scenes'] if s['id']==sid))} {ko if lang=='ko' else en}" for sid,ko,en in groups) for lang in ['ko','en']}
credit='''Wholesome Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0 License
https://creativecommons.org/licenses/by/4.0/

Mix and Jam — Splatoon-Ink (development demo)
Copyright (c) 2021 Mix and Jam. Permission notice:
https://github.com/mixandjam/Splatoon-Ink/blob/10a730cc26d48d9a3f8a34983827291f4ecef5b2/LICENSE
Jammo Character — Mix and Jam / Curiomatic
Copyright (c) 2019 Mix and Jam. MIT license:
https://github.com/mixandjam/Jammo-Character/blob/master/LICENSE
WoW Classic footage: Nyhver (2020)
https://www.youtube.com/watch?v=A2VQbPrw9-g
Unity illustration assets: KayKit Adventurers / Kenney Tiny Dungeon (CC0).'''
sources=json.loads((ROOT/f'projects/{SLUG}/sources/source-manifest.json').read_text(encoding='utf-8'))['actualFootageSources']
credit+='\n\nIndependent production footage (native-speed excerpts, overlays added, original audio omitted):\n'+'\n'.join(f"{r['title']} — {r['author']} ({r['date']}) / {r['license']}\n{r['sourceUrl']}" for r in sources)+'\nCC BY3.0: https://creativecommons.org/licenses/by/3.0/\nCC BY4.0: https://creativecommons.org/licenses/by/4.0/\nCC0: https://creativecommons.org/publicdomain/zero/1.0/'
ko='''AI가 게임을 만드는 시대, 개발자의 실력은 어디에 쓰일까?

개발 도구와 자동화가 바뀌어도 조건을 정하고 결과를 검증하는 일은 남습니다. 에픽과 Unity의 공개 자료, 독립 개발 화면, 직접 만든 Unity 상점·점프 시연으로 그 차이를 살펴봅니다.

이 영상은 Wild Ox Studios 영상과 사용자가 제공한 자막의 논점을 바탕으로 설명을 확장했습니다. 제작자의 개인 경험은 해당 제작자의 이야기로 소개합니다.
https://youtu.be/Zxbn55DVi-Q

2026년 10월 14일 확인 기준입니다. Epic의 장기 계획과 보도, Unity Spark의 출시 예정 상태를 구분합니다. 자체 Unity 장면은 설명용 구현이며 상점의 저장·네트워크 기능은 구현하지 않았습니다.

챕터
'''+chapters['ko']+'\n\n라이선스 및 필수 고지\n'+credit+'\n\n'+footer
en='''When AI Makes Games, Where Do a Developer's Skills Matter?

Tools and automation change, but defining conditions and checking results still matter. We explore official Epic and Unity material, an independent development demo, and original Unity shop and input-response examples.

Expanded from ideas in the Wild Ox Studios video and the user-supplied transcript. Personal experiences are attributed to that creator.
https://youtu.be/Zxbn55DVi-Q

Information checked on October 14, 2026. Long-term plans, reporting and Unity Spark's coming-soon status are distinguished. Our Unity scenes are explanations; persistent storage and networking are not implemented in the shop demo.

Chapters
'''+chapters['en']+'\n\nLicense notices and attribution\n'+credit+f'''\n\nYamYamCoding — game programming, Unity, Unreal Engine and computer graphics.

Programming coaching
{defaults['coaching']['url']}

Community Discord
https://discord.gg/wZuqe7fqkR

Channel membership
{defaults['membershipUrl']}
'''
for lang,text in [('ko',ko),('en',en)]:
 assert len(text)<5000
 (P/f'youtube.{lang}.md').write_text(text+'\n',encoding='utf-8')
(P/'pinned-comment.ko.txt').write_text('AI를 활용하면서 쉬워진 작업과, 오히려 자신의 지식이 더 필요했던 순간을 댓글로 남겨 주세요.\n\n프로그래밍 과외 안내\n'+defaults['coaching']['url']+'\n',encoding='utf-8')
(P/'prepared-metadata.json').write_text(json.dumps({'status':'prepared-not-uploaded','driveReviewRequiredBeforeYouTube':True,'chapters':chapters,'coachingUrl':defaults['coaching']['url'],'pinnedComment':'prepared-pending-video-publication'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared measured chapters, bilingual descriptions and required license notices.')
