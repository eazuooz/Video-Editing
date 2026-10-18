"""Independently worded paired lesson; lock only after actual source inspection."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];P=R/'projects/familiar-game-rules'
parts=[
('01','처음인데 손이 먼저 움직인다',[
'안녕하세요, 얌얌코딩입니다. 처음 켠 게임인데도, 설명을 읽기 전에 손부터 움직였던 적 있나요?',
'게임이 달라도 조작의 약속이 비슷하면, 배워야 할 부분이 줄어듭니다.',
'일인칭 슈팅 게임의 공통 조작에서 시작해 버튼 재설정의 역할을 살펴보고, 익숙함을 그대로 옮길 수 없는 경우까지 보겠습니다.',
'먼저 레이지 투와 에이펙스 레전드에서 대상을 바라보고 움직이며 쏘는 장면부터 보죠.'
],[
'Hello, this is Yamyam Coding. Have your hands ever started moving in a new game before you read its instructions?',
'When different games share familiar control conventions, there is less to learn from scratch.',
'We will start with common first-person shooter controls, examine button remapping, and then consider cases where familiar inputs cannot simply be transferred.',
'Let us begin with looking, moving and shooting in RAGE 2 and Apex Legends.'
]),
('02','다른 게임에서도 이어지는 조작',[
'두 게임 모두 플레이어가 바라보는 방향을 중심으로, 화면 속 공간을 움직이며 무기를 사용합니다. 이런 시점의 슈팅 게임을 일인칭 슈팅, 영어로는 퍼스트 퍼슨 슈터라고 합니다.',
'화면 가운데의 조준점은 무기가 향하는 쪽을 읽는 기준입니다. 바라보는 방향을 바꾸면, 조준점 뒤에 놓이는 대상도 달라지죠.',
'엑스박스 기본 배치에서 두 게임은 왼쪽 스틱으로 이동하고, 오른쪽 스틱으로 시점을 바꿉니다. 왼쪽 트리거로 겨누고, 오른쪽 트리거로 발사하는 연결도 이어집니다. 이렇게 배운 조작을 다음 게임에서도 출발점으로 삼을 수 있죠.',
'물론 모든 게임과 기기에서 버튼이 같다는 뜻은 아닙니다. 키보드와 마우스인지, 컨트롤러인지에 따라서도 배치가 달라집니다.',
'그런 차이를 확인하더라도, 이동과 조준이라는 익숙한 역할까지 전부 새로 배울 필요는 없습니다. 그렇다면 새 게임의 개성은 어디에 둘 수 있을까요?'
],[
'In both games, players use weapons while moving through a world viewed from their own perspective. A shooter with this viewpoint is called a first-person shooter, or FPS.',
'The reticle near the center of the screen helps you read where the weapon is aimed. Changing the view changes which target is behind that reticle.',
'In the default Xbox layouts, both games use the left stick to move and the right stick to look. The left trigger aims and the right trigger fires. Those learned connections can become a starting point in another game.',
'This does not mean every game and device uses identical buttons. A keyboard and mouse can have a different layout from a controller.',
'Even after checking those differences, you need not learn the roles of movement and aiming entirely from scratch. So where can a new game express its identity?'
]),
('03','새로움은 조작 밖에도 있다',[
'입력 방식이 익숙해도, 플레이어가 들어갈 세계와 겪을 이야기는 달라질 수 있습니다.',
'황폐한 공간을 돌아다니며 싸우는 경험과, 팀원이나 다른 플레이어의 위치를 보며 판단하는 경험은 같은 발사 버튼만으로 설명되지 않습니다.',
'적을 어디에서 만나고, 무엇을 지키며, 어떤 상황에서 능력을 쓸지에 새로운 판단을 둘 수 있습니다.',
'조작을 모두 낯설게 바꾸어야 독창적인 게임이 되는 것은 아닙니다. 익숙한 손의 움직임이, 오히려 그 세계에 집중하는 데 도움을 줄 수도 있습니다.',
'다만 여기에는 조건이 하나 있습니다. 그 조작에 이미 익숙한 사람과, 처음 만난 사람은 출발점이 다릅니다.'
],[
'Familiar inputs can lead into a different world and a different story.',
'Exploring a devastated landscape and making decisions around teammates and opponents cannot be explained by the fire button alone.',
'New decisions can come from where enemies appear, what you protect, and when you use an ability.',
'A game does not have to make every input unfamiliar to be original. Familiar hand movements can even help players concentrate on its world.',
'There is a condition, however: someone familiar with those controls and someone encountering them for the first time have different starting points.'
]),
('04','아는 만큼 줄이고, 모르는 곳은 돕는다',[
'장르를 처음 접하는 사람에게는, 조준점과 이동, 무기 사용을 확인할 안내가 필요합니다. 이미 안다고 가정해서 모두 생략하면 첫 행동부터 막힐 수 있죠.',
'반대로 같은 장르를 해 본 사람에게는, 이미 아는 행동보다 이번 게임에서 달라진 규칙을 먼저 알려 줄 수 있습니다.',
'콜 오브 듀티, 헤일로, 파 크라이, 타이탄폴, 배틀필드로 화면이 바뀌어도, 무기를 겨누고 발사하며 남은 탄약을 확인하는 익숙한 행동이 나타납니다.',
'지금 보는 탄창의 남은 탄약 숫자는, 재장전 전에 얼마나 더 쏠 수 있는지 판단하는 정보입니다. 발사 뒤 숫자가 줄어드는 모습을 보면, 조작과 화면의 반응을 함께 확인할 수 있습니다.',
'이미 아는 행동이라면, 필요한 순간에 어떤 입력을 쓰는지 짧게 알려 주는 것으로 충분할 때도 있습니다. 처음 보는 기능이라면 무엇이 일어나는지까지 설명해야 하고요.',
'줄일 것은 설명의 양 자체가 아니라, 그 사람이 이미 아는 내용의 반복입니다. 이렇게 경험이 다음 게임으로 이어지는 데에는 공통된 약속이 작용합니다.'
],[
'A newcomer to the genre needs guidance for checking the reticle, movement and weapon use. Removing all guidance on the assumption that everyone already knows can block the very first action.',
'For someone who has played the genre, you can instead give priority to the rules that differ in this game.',
'As the screen changes between Call of Duty, Halo, Far Cry, Titanfall and Battlefield, familiar actions appear: aiming, firing and checking ammunition.',
'The remaining-rounds number in the magazine tells players how many more shots they have before reloading. Watching the number decrease after a shot connects the input with the visible response.',
'For a familiar action, a short indication of the required input at the right moment may be enough. An unfamiliar function also needs an explanation of what will happen.',
'The goal is to reduce repeated information the player already knows. Shared conventions help that experience carry into the next game.'
]),
('05','사실상의 표준',[
'여러 게임에서 널리 쓰여 익숙해진 방식을, 사실상의 표준, 디 팩토 스탠더드라고 부릅니다.',
'가령 마우스를 움직이면 화면의 가리키는 위치가 바뀐다는 약속을 배운 사람은, 새 프로그램에서도 그 관계를 먼저 기대할 수 있습니다.',
'사람과 컴퓨터가 상호작용하는 방법을 다루는 분야를 인간 컴퓨터 상호작용이라고 합니다. 이때 익숙한 약속은 사용자가 자신의 의도를 전달하는 출발점이 됩니다.',
'게임에서도 마찬가지입니다. 다만 널리 쓰인 배치라고 해서, 모든 사람의 손과 습관에 가장 편한 배치가 되는 것은 아닙니다. 그래서 약속을 이어 쓰는 것과 함께, 바꿀 수 있는 여지도 필요합니다.'
],[
'A method that has become familiar through widespread use is called a de facto standard.',
'For example, someone who has learned that moving a mouse changes the pointer position can expect that relationship in a new program.',
'Human-computer interaction, or HCI, is the field that studies how people interact with computers. Familiar conventions give users a starting point for expressing an intention.',
'The same applies to games. But a widespread layout is not necessarily the most comfortable one for every hand and habit. Alongside shared conventions, players need room to make adjustments.'
]),
('06','행동은 두고, 입력을 바꾼다',[
'스트리트 파이터 식스, 테일즈 오브 어라이즈, 아세토 코르사 콤페티치오네의 설정 화면을 보면, 행동에 연결된 입력을 바꾸는 항목이 있습니다.',
'이런 기능을 버튼 재설정, 또는 버튼 리매핑이라고 합니다. 예를 들어 점프라는 행동은 유지하면서, 그 행동을 실행할 버튼을 바꾸는 겁니다.',
'설명을 위한 가상 배치에서, 점프가 에이 버튼에 연결돼 있다고 해 보죠. 플레이어가 비 버튼을 고르면, 바뀌는 것은 버튼에서 점프로 이어지는 연결입니다.',
'이때 화면에 뜨는 버튼 안내도 같은 연결을 따라 바뀌어야 합니다. 실행은 비 버튼인데 안내는 에이 버튼으로 남아 있다면, 설정은 바뀌었어도 플레이어는 헷갈리겠죠.',
'개발할 때는 행동, 입력, 화면 안내를 함께 관리해야 합니다. 이 작업이 번거롭더라도, 누가 그 배치를 사용할지를 생각하면 필요한 이유가 드러납니다.'
],[
'The settings in Street Fighter 6, Tales of Arise and Assetto Corsa Competizione include options for changing the inputs assigned to actions.',
'This is called button remapping. For example, the action of jumping can stay the same while its assigned button changes.',
'In an illustrative layout, suppose jumping is assigned to the A button. If the player selects B, the connection from the button to the jump action changes.',
'On-screen button prompts must follow that same connection. If B performs the action but the prompt still says A, the setting has changed while the player remains confused.',
'Development must keep actions, inputs and prompts consistent. Even when that adds work, considering the people who will use the layout makes its purpose clear.'
]),
('07','만든 사람의 정답과 쓰는 사람의 선택',[
'만든 사람은 자신이 정한 배치를 오랫동안 사용합니다. 그래서 가장 자연스럽고 완성된 배치라고 느끼기 쉽습니다.',
'하지만 플레이어는 다른 게임에서 배운 손의 움직임을 가지고 들어옵니다. 손을 쓰는 방식과 기기도 서로 다를 수 있고요.',
'기본 배치를 잘 만드는 일과, 가능한 범위에서 선택권을 주는 일은 함께 할 수 있습니다. 바꾼 뒤에도 이동하며 점프하거나 조준하는 조합이 가능한지 확인해야 합니다.',
'그런데 버튼의 연결을 바꾸는 것만으로 해결되지 않는 경우도 있습니다. 입력 장치가 보내는 정보 자체가 다를 때입니다.'
],[
'Designers use their chosen layout repeatedly. It is easy for that layout to feel natural and complete.',
'Players arrive with hand movements learned in other games. Their devices and ways of using their hands can differ as well.',
'A carefully designed default can coexist with choices where they are possible. After remapping, check combinations such as moving while jumping or aiming.',
'Some differences cannot be solved by changing button assignments alone: the input devices may provide different information.'
]),
('08','방향만으로는 부족할 때',[
'슈퍼 스매시브라더스 얼티밋에서 사용하는 아날로그 스틱을 생각해 보죠. 스틱은 방향뿐 아니라 얼마나 기울였는지도 전달할 수 있습니다.',
'오른쪽 방향만 비교해 보겠습니다. 방향 패드는 누르지 않은 상태와 누른 상태를 구분합니다. 아날로그 스틱에는 그 사이의 기울임 정도를 나타내는 여러 중간값이 있습니다.',
'이 설명에서는 기울임 거리를 일정한 비율로 영부터 일까지 환산합니다. 최대 거리의 사분의 일은 영 점 이오, 사분의 삼은 영 점 칠오로 표시할 수 있죠.',
'이 숫자는 실제 컨트롤러나 게임의 속도, 판정 기준을 측정한 값이 아닙니다. 같은 오른쪽이라도, 입력의 크기에 차이가 있다는 것을 보여 주는 예입니다.',
'게임이 그 차이를 읽어 걷는 정도나 행동을 나눈다면, 방향 패드에 이동이라는 이름을 붙이는 것만으로 같은 기능이 생기지는 않습니다.',
'시리즈 전체가 언제나 방향 패드를 쓸 수 없었다는 뜻도 아닙니다. 대난투 스매시브라더스 엑스에는 위 리모컨을 옆으로 잡는 방식이 있었습니다. 여기서 따질 것은 장치 이름보다, 필요한 입력 정보를 보존했느냐입니다.'
],[
'Consider the analog stick used in Super Smash Bros. Ultimate. A stick can communicate not only direction but also how far it is tilted.',
'Compare only the rightward direction. A directional-pad button distinguishes released and pressed states. An analog stick provides intermediate values for its degree of deflection.',
'In this illustration, we linearly scale deflection distance from zero to one. One-quarter of the maximum distance is represented as 0.25, and three-quarters as 0.75.',
'These are not measurements of the actual controller, game speeds or decision thresholds. They illustrate that two rightward inputs can have different magnitudes.',
'If a game uses that difference to vary walking or distinguish actions, assigning movement to a D-pad does not automatically provide the same function.',
'This is not a claim that every Smash title has always prohibited directional-pad play. Super Smash Bros. Brawl supported a sideways Wii Remote. What matters here is preserving the information the action needs.'
]),
('09','바꿀 수 없는 부분에는 이유가 필요하다',[
'버튼 재설정은 연결을 바꾸는 기능입니다. 입력 장치에 없는 정보를 만들어 주는 기능은 아닙니다.',
'꼭 필요한 입력을 다른 방식으로 제공하려면, 별도의 보조 버튼이나 속도 선택 같은 대안을 새로 설계해야 할 수 있습니다.',
'그 대안이 같은 행동과 판단을 유지하는지는 직접 실행하며 확인해야 합니다. 따라서 모든 기능을 자유롭게 바꿀 수 있다고 약속할 수는 없습니다.',
'그렇다고 익숙함만을 기준으로 모든 조작을 같은 모습으로 만들면 될까요? 마지막으로, 낯선 연결 자체가 경험을 바꾸는 경우를 보겠습니다.'
],[
'Remapping changes connections. It does not create information that the input device cannot supply.',
'Providing an essential input in a different way may require a separately designed alternative, such as a modifier button or a speed selector.',
'Hands-on testing must establish whether that alternative preserves the same actions and decisions. Not every function can be promised unrestricted reassignment.',
'Should familiarity therefore make every game use the same controls? Finally, let us consider how an unfamiliar connection can change the experience itself.'
]),
('10','낯선 연결도 하나의 경험이 된다',[
'옛 액션 게임 체르노브는, 메가드라이브판에서는 아토믹 러너라는 이름으로도 알려져 있습니다. 달리면서 뛰고, 적을 향해 공격하는 모습을 볼 수 있죠.',
'이제 실제 게임의 기본 배치와는 구별해서, 입력의 연결을 서로 바꾼 가상의 예를 생각해 봅시다.',
'움직이려고 누른 입력에서 공격이 나오고, 공격하려고 누른 입력에서 이동이 나온다면 어떨까요? 실행할 행동은 알아도, 그 행동을 부르는 손의 움직임부터 다시 익혀야 합니다.',
'실수로 연결이 잘못된 상황과, 그런 낯섦을 의도한 설계는 구분해야 합니다. 의도한 조작이라면, 익히는 과정 자체가 새로운 도전이 될 수도 있습니다.',
'따라서 낯설다는 이유 하나로 무조건 없앨 수도 없습니다. 그 낯섦이 어떤 재미를 만들며, 처음 하는 사람에게는 어떤 부담을 주는지 함께 판단해야 합니다.'
],[
'The older action game Chelnov is also known through its Mega Drive release as Atomic Runner. You can see the character run, jump and attack enemies.',
'Now consider a hypothetical swap of input connections, clearly separate from the actual game\'s default layout.',
'What if the input you press to move produces an attack, while the input intended to attack produces movement? Even when you know the desired action, you must relearn the hand movement that calls it.',
'An accidental connection error and an intentionally unfamiliar design are different situations. With an intentional scheme, learning the controls can become part of the challenge.',
'Unfamiliarity alone is therefore not a reason to remove it. Consider both the enjoyment it creates and the burden it places on a newcomer.'
]),
('11','남길 익숙함과 배울 새로움',[
'익숙한 조작은 새 게임을 배우는 출발점을 만들어 줍니다. 이미 아는 설명을 줄이고, 이번 작품의 세계와 새로운 판단에 집중하게 할 수 있죠.',
'가능한 곳에는 버튼 재설정을 제공하고, 장치가 달라질 때는 필요한 입력 정보까지 확인하세요.',
'동시에, 익히는 과정이 재미가 되는 독특한 조작까지 지우지는 말아야 합니다. 남길 익숙함과 새로 배울 이유를 함께 설계하는 겁니다.',
'여러분이 처음 켰는데도 조작이 바로 손에 익었던 게임은 무엇인가요? 반대로 낯선 조작을 익히는 게 재미였던 게임도 댓글로 알려 주세요.'
],[
'Familiar controls create a starting point for learning a new game. They can reduce repeated instructions and leave more attention for its world and new decisions.',
'Offer remapping where possible, and check the required input information when devices change.',
'At the same time, retain distinctive controls when learning them is part of the enjoyment. Design both the familiarity to keep and the reason to learn something new.',
'Which game felt familiar in your hands on the very first try? And in which game was learning unfamiliar controls part of the fun? Tell us in the comments.'
])]
S=P/'script/reference-preserving-v2';S.mkdir(parents=True,exist_ok=True)
for lang,idx in [('ko',2),('en',3)]:
 data={'title':'처음 켠 게임인데, 왜 조작은 이미 알까?','status':'locked-after-independent-footage-and-complete-text-review',
 'scenes':[dict(id=s[0],title=s[1],lines=s[idx]) for s in parts]}
 (S/f'narration.{lang}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ko=json.loads((S/'narration.ko.json').read_text(encoding='utf-8'))
(S/'narration.tts.ko.json').write_text(json.dumps(ko,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(S/'narration.ko.txt').write_text('\n\n'.join('\n'.join(s['lines']) for s in ko['scenes'])+'\n',encoding='utf-8')
aliases={'레이지 2':'레이지 투','스트리트 파이터 6':'스트리트 파이터 식스','Xbox':'엑스박스','A 버튼':'에이 버튼','B 버튼':'비 버튼','0.25':'영 점 이오','0.75':'영 점 칠오','대난투 스매시브라더스 X':'대난투 스매시브라더스 엑스','Wii 리모컨':'위 리모컨'}
for scene in ko['scenes']:
 for i,line in enumerate(scene['lines']):
  for display,spoken in aliases.items():line=line.replace(spoken,display)
  scene['lines'][i]=line
(S/'narration.ko.json').write_text(json.dumps(ko,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(S/'caption-aliases.json').write_text(json.dumps(aliases,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Paired draft:',len(parts),'scenes,',sum(len(s[2]) for s in parts),'paragraphs,',sum(len(x) for s in parts for x in s[2]),'Korean display characters')
