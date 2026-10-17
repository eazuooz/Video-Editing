"""Prepare metadata from the measured cut; do not perform any platform mutation."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';O=P/'publishing/reference-preserving-v2'
plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));assert plan['timing']=='measured-and-asr-aligned'
script=json.loads((P/'script/reference-preserving-v2/narration.ko.json').read_text(encoding='utf8'));defaults=json.loads((R/'shared/publishing/youtube-defaults.json').read_text(encoding='utf8'))
def stamp(t):
 n=int(t);return f'{n//60:02}:{n%60:02}'
chapters=['00:00 얌얌코딩 · 전편은 재밌었는데']+[stamp(s['voiceStart'])+' '+script['scenes'][i]['title'] for i,s in enumerate(plan['scenes']) if i]+[stamp(plan['totalFrames']/60-10)+' 멤버쉽가입 감사드립니다.']
intro='전편을 재미있게 했어도 속편을 꼭 사는 것은 아닙니다. 피크민, 그란 투리스모, 스매시브라더스의 실제 장면과 함께, 개발자가 이어 쓸 수 있는 기반과 플레이어가 다시 즐길 이유를 구분합니다. 재사용의 이점을 새로운 행동과 도전으로 연결하는 기획을 살펴봅니다.'
channel=(R/'shared/publishing/youtube-channel-description.ko.txt').read_text(encoding='utf8').split('📚 수업 노트')[0].rstrip().removesuffix('━━━━━━━━━━━━━━━━━━').rstrip()
credits='Gameplay: LongplayArchive / Spazbo4 — https://www.youtube.com/watch?v=wn5EsQn5NLA ; https://www.youtube.com/watch?v=663UvTXbzbM — edited commentary excerpts under recorder permission. Games © Nintendo.\nGameplay: The Geek Joint [Free to Use] — https://www.youtube.com/watch?v=1py4hV9act0 — edited excerpt under stated reuse permission. Gran Turismo 7 © Sony Interactive Entertainment / Polyphony Digital. Original source audio excluded.\nMusic: Nimbus — Eveningland (YouTube Audio Library)'
(O/'description.ko.txt').write_text(intro+'\n\n'+'\n'.join(chapters)+'\n\n'+channel+'\n\n#게임개발 #게임기획 #게임속편\n\n영상·음원 크레딧\n'+credits+'\n',encoding='utf8')
titles=['A familiar game, another purchase?','What can carry forward?','Systems, tools, and content','Playtesting the actual experience','Same series, different foundations','Expectations become memories','A new reason to return','From saved work to player value','A foundation and a fresh experience']
english=['00:00 Yamyam Coding — '+titles[0]]+[stamp(s['voiceStart'])+' '+titles[i] for i,s in enumerate(plan['scenes']) if i]+[stamp(plan['totalFrames']/60-10)+' Thank you, channel members']
en='Enjoying a game does not guarantee buying its sequel. Using Pikmin, Gran Turismo and Smash Bros., this lesson separates a developer’s reusable foundation from a player’s reason to return. Systems, tools and tested experience can help production, but the new game still needs worthwhile actions and challenges.\n\n'+'\n'.join(english)+'\n\nYamyam Coding — game programming, DirectX, Unity, Unreal and computer graphics.\nProgramming coaching: '+defaults['coaching']['url']+'\nCommunity: https://discord.gg/wZuqe7fqkR\nMembership: '+defaults['membershipUrl']+'\n\n#GameDevelopment #GameDesign #Sequels\n\nCredits\n'+credits+'\n'
(O/'description.en.txt').write_text(en,encoding='utf8')
(O/'pinned-comment.ko.txt').write_text('여러분은 어떤 변화가 있어야 좋아했던 게임의 속편을 다시 사고 싶으신가요?\n\n프로그래밍 과외: '+defaults['coaching']['url']+'\n',encoding='utf8')
print('Prepared Korean/English descriptions, actual chapter timestamps and future pinned comment; nothing posted.')
