"""Write independent bilingual narration and the selected revision's scene plan."""
from pathlib import Path
import json, datetime, hashlib
R=Path(__file__).resolve().parents[3]
P=R/'projects/avoid-game-comparisons'
S=P/'script/reference-preserving-v2';S.mkdir(parents=True,exist_ok=True)
V=P/'production/reference-preserving-v2';V.mkdir(parents=True,exist_ok=True)
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
scenes=[
('01','같은 이름, 다른 게임','overview','R01',[
'안녕하세요, 얌얌코딩입니다.',
'마리오 같은 게임이라고 설명하면, 듣는 사람도 나와 같은 장면을 떠올릴까요?',
'오늘은 익숙한 게임에 빗대는 설명이 왜 내 게임의 매력을 가리고, 서로 다른 기획으로 전달될 수 있는지 살펴보겠습니다.',
'마리오의 서로 다른 플레이를 비교한 뒤, 목표와 행동과 조건을 말하는 방식으로 설명을 바꿔 보죠.'
],[
'Hello, this is Yamyam Coding.',
'If you describe something as a Mario-like game, will your listener picture the same scene as you?',
'Today we will examine how comparing a game to something familiar can hide its appeal and leave people imagining different designs.',
'We will compare different Mario experiences, then rewrite a description in terms of goals, actions and conditions.'
]),
('02','익숙한 이름을 찾는 이유','familiar','R01',[
'우선 비교가 편리한 이유부터 생각해 봅시다.',
'처음 보는 게임을 설명할 때, 이미 아는 작품을 꺼내면 긴 설명을 줄일 수 있습니다.',
'가령 화면 옆에서 캐릭터를 바라보고, 발판 사이를 뛰어넘는다고 말하는 대신 마리오를 떠올려 달라고 하는 거죠.',
'지금 장면에서는 오른쪽으로 이동하면서 구멍을 넘고, 적을 피하거나 밟으며 앞으로 나아갑니다.',
'같은 장면을 기억하는 상대라면, 작품 이름 하나가 이런 움직임을 빠르게 불러올 수 있습니다.',
'하지만 그 이름이 설명해 주는 것은 이미 존재하는 게임입니다. 이제부터 만들 게임까지 설명해 주는 건 아닙니다.'
],[
'First, consider why comparisons are useful.',
'Mentioning a familiar title can shorten the explanation of an unfamiliar game.',
'Instead of describing a side view and jumps between platforms, you might ask the listener to think of Mario.',
'Here, the player moves right, crosses gaps, and avoids or jumps on enemies to advance.',
'If the listener remembers the same scene, a single title can quickly bring those actions to mind.',
'But the name describes a game that already exists. It does not automatically explain the game you intend to make.'
]),
('03','아직 없는 게임을 전달하기','pitch','R02',[
'아직 없는 게임은 직접 보여 주거나 플레이해 보라고 할 수 없습니다.',
'내 머릿속에는 주인공의 움직임과 화면이 선명해도, 함께 만들 사람은 그 모습을 모릅니다.',
'그래서 기획을 설명할 때는 무엇을 만들지뿐 아니라, 왜 함께 만들 가치가 있는지도 전달해야 합니다.',
'이렇게 프로젝트의 핵심 매력과 방향을 짧게 전달하는 설명을 피치라고 부릅니다.',
'팀원이든 제작을 지원할 사람이든, 설명을 듣고 구체적인 플레이와 이 게임만의 이유를 이해할 수 있어야 하죠.',
'여기서 다른 작품과 닮았다는 말만 남으면, 첫 번째 문제가 생깁니다.'
],[
'You cannot ask someone to play a game that does not exist yet.',
'The character and screen may be clear in your mind, but a potential teammate cannot see them.',
'Your explanation must communicate both what you intend to make and why it is worth making together.',
'A concise presentation of a project’s central appeal and direction is often called a pitch.',
'A teammate or potential supporter should be able to understand the play experience and the reason for this particular game.',
'If all that remains is its resemblance to another title, the first problem appears.'
]),
('04','왜 이 게임을 선택해야 할까','difference','R03',[
'듣는 사람은 이렇게 생각할 수 있습니다. 비슷한 재미라면, 이미 있는 게임을 하면 되는 것 아닌가?',
'만드는 쪽이 유사성만 강조하면, 정작 우리 게임을 선택할 이유가 설명에서 사라집니다.',
'예를 들어 이 장면을 단지 점프하는 마리오라고 소개해 보죠. 그러면 모자를 던져 다른 대상을 조종하는 행동이 잘 드러나지 않습니다.',
'모자를 맞힌 뒤 조종 대상이 바뀌고, 그 대상의 능력으로 지나가지 못했던 곳을 통과한다면, 바로 그 행동과 결과를 말해야 합니다.',
'비슷하다는 말에 새로움을 맡기지 말고, 플레이어가 무엇을 다르게 경험하는지 보여 주는 겁니다.',
'이 설명은 실제 개발사의 제안서를 소개하는 것이 아니라, 눈앞의 플레이를 말로 옮기는 연습입니다.'
],[
'The listener might wonder: if the appeal is similar, why not play the game that already exists?',
'When the creator emphasizes only similarity, the reason to choose this game disappears from the explanation.',
'Suppose we describe this scene merely as Mario jumping. That overlooks throwing a cap to control another target.',
'If hitting a target changes what you control, and its ability lets you pass an obstacle, describe that action and result.',
'Do not leave novelty to the comparison. Show what the player experiences differently.',
'This is an exercise in describing visible play, not a presentation of the developer’s actual pitch.'
]),
('05','비교를 금지하는 규칙은 아니다','exception','R03',[
'그렇다고 다른 게임의 이름을 무조건 금지하자는 뜻은 아닙니다.',
'같은 시리즈의 후속작이라면 익숙한 조작과 재미가 중요한 약속이 될 수도 있습니다.',
'또 듣는 사람이 스스로 다른 게임을 떠올리는 것과, 만드는 사람이 그 이름에 설명을 맡기는 것은 다릅니다.',
'조심해야 할 것은 비교 자체보다, 비교를 빼고 나면 내 게임을 설명할 내용이 남지 않는 상황입니다.',
'그런데 고유한 매력을 덧붙여도, 아직 두 번째 문제가 남습니다. 같은 작품 이름을 들었다고 같은 경험을 떠올리는 건 아니니까요.'
],[
'This does not mean that every mention of another game should be banned.',
'In a sequel, familiar controls and appeal can be an important promise.',
'A listener making their own association is also different from a creator relying on that title to do the explaining.',
'The problem is a description that has nothing left once the comparison is removed.',
'Even after adding a distinctive appeal, a second problem remains: the same title does not summon the same experience for everyone.'
]),
('06','누군가에게 마리오는 이 장면','nes','R04',[
'슈퍼 마리오 브라더스를 먼저 떠올린 사람은 이런 화면을 생각할 수 있습니다.',
'캐릭터를 옆에서 바라보며 오른쪽으로 진행하고, 구멍이나 적을 점프로 넘어갑니다.',
'가까운 발판과 다음 발판의 높이, 그 사이의 빈 공간을 보고 뛰어야 하죠.',
'끝의 깃대에 도착하면 그 구간의 목표를 달성합니다.',
'이 경험을 기준으로 마리오 같은 게임을 이해하면, 옆으로 이어지는 길과 점프의 타이밍을 먼저 상상하기 쉽습니다.',
'하지만 다른 사람이 최근에 주로 플레이한 마리오가 삼차원 공간을 탐험하는 게임이라면 어떨까요?'
],[
'Someone thinking first of Super Mario Bros. might picture this screen.',
'You see the character from the side and move right, jumping over gaps or enemies.',
'You judge the height of the next platform and the empty space between platforms before jumping.',
'Reaching the flagpole completes the objective of that section.',
'With this experience as a reference, a Mario-like game may suggest a sideways route and carefully timed jumps.',
'But what if the other person has mainly played a Mario game about exploring a three-dimensional space?'
]),
('07','다른 사람은 공간과 능력을 떠올린다','odyssey','R04',[
'슈퍼 마리오 오디세이에서는 캐릭터 주변의 공간을 살펴보고, 갈 곳과 사용할 대상을 찾습니다.',
'여기서 모자 캐피로 특정 대상을 조종하는 기능이 캡처입니다. 화면을 저장한다는 뜻이 아니라, 그 대상이 되어 능력을 사용하는 행동이죠.',
'지금은 티라노사우루스를 캡처합니다. 모자를 던진 뒤 조종 대상이 바뀌고, 커다란 몸으로 돌을 부수며 길을 엽니다.',
'대상이 달라지면 할 수 있는 행동도 달라지는 거죠. 이 장면의 과제는 점프 타이밍만 맞추는 것이 아니라, 어떤 대상을 이용해 길을 열지 알아내는 데 있습니다.',
'같은 마리오라는 말에서 한 사람은 횡스크롤 점프를, 다른 사람은 공간 탐색과 능력 활용을 먼저 생각할 수 있는 겁니다.',
'어느 쪽이 틀린 기억인 것은 아닙니다. 서로 다른 경험을 같은 단어로 압축했을 뿐이죠.'
],[
'In Super Mario Odyssey, you inspect the space around the character and look for places to go and targets to use.',
'Taking control of certain targets with Cappy is called Capture. Here it means using that target’s abilities, not saving an image.',
'Mario captures a T. rex. Throwing Cappy changes the controlled character, and its large body breaks rocks to open a route.',
'A different target gives the player different actions. The task here is not only timing a jump, but finding a target that can open the route.',
'The same word, Mario, can therefore suggest side-scrolling jumps to one person and spatial exploration with different abilities to another.',
'Neither memory is wrong. Different experiences have been compressed into the same word.'
]),
('08','공통된 장면부터 만들기','conditions','R05',[
'이 차이를 줄이려면, 상대가 무엇을 떠올렸는지 먼저 확인해야 합니다.',
'같은 장면을 함께 본 뒤, 어디로 가는지, 무엇을 조작하는지, 어떤 조건에서 결과가 달라지는지를 짚어 보세요.',
'이번에는 쇠사슬에 묶인 멍멍이를 봅시다. 모자로 캡처하고 뒤로 당겼다가 놓으면, 앞으로 튀어나가 벽을 부숩니다. 그 안에서 달 모양 수집물인 파워문이 드러나죠.',
'목표는 파워문을 얻는 것, 행동은 당겼다가 놓는 것입니다. 필요한 조건은 부술 벽을 향하도록 방향을 맞추는 것이죠.',
'여기서 방향이라는 조건만 바꿔 봅시다. 벽 쪽으로 보내는 설명과, 아무 방향으로 보내도 된다는 설명은 서로 다른 플레이를 뜻합니다.',
'실제 장면이 보여 준 것은 벽을 향해 발사해 부수는 결과입니다. 아무 데나 보내도 해결된다고 설명을 넓히면 안 됩니다.',
'이렇게 작품 이름 뒤에 숨어 있던 조건을 꺼내면, 듣는 사람이 무엇을 구현해야 할지 훨씬 구체적으로 이해할 수 있습니다.'
],[
'To reduce this difference, first check what the listener pictured.',
'Look at the same scene together and identify the destination, the controlled action and the conditions that affect the result.',
'Now look at the chained Chain Chomp. Capture it with Cappy, pull back and release: it launches forward and breaks the wall, revealing a moon-shaped collectible called a Power Moon.',
'The goal is to obtain the Power Moon; the action is to pull back and release. The relevant condition is aiming at the breakable wall.',
'Change just that condition: aiming at the wall and sending it in any direction describe different play experiences.',
'The footage shows the wall breaking after a launch toward it. It does not establish that any direction would solve the task.',
'Making the hidden condition explicit gives the listener a more concrete idea of what must be implemented.'
]),
('09','세 문장으로 바꿔 말하기','rewrite','R05',[
'이제 이 장면을 게임 이름 없이 세 문장으로 정리해 보겠습니다.',
'첫째, 플레이어는 벽 너머에 있는 파워문을 얻으려 합니다. 먼저 목표를 말합니다.',
'둘째, 주변의 멍멍이를 조종하고 뒤로 당겼다가 놓아 앞으로 발사합니다. 반복해서 할 행동을 말하는 겁니다.',
'셋째, 부술 수 있는 벽을 향해 발사하면 벽이 무너지고, 파워문에 접근할 수 있습니다. 조건과 결과를 연결합니다.',
'목표, 행동, 조건과 결과. 이것은 모든 기획서를 대신하는 정답 양식이 아니라, 서로 같은 플레이를 상상하는지 확인하는 출발점입니다.',
'실제 기획에서는 조작 입력과 실패했을 때의 처리처럼 필요한 규칙을 여기에 더 붙이면 됩니다.'
],[
'Now describe this scene in three sentences without naming the game.',
'First: the player wants to obtain the Power Moon beyond the wall. State the goal.',
'Second: the player controls a nearby Chain Chomp, pulls it back and releases it forward. Describe the action.',
'Third: launching it at the breakable wall destroys the wall and gives access to the Power Moon. Connect the condition to the result.',
'Goal, action, condition and result: this is a starting point for checking shared understanding, not a universal replacement for a design document.',
'For a real design, add the necessary rules, such as the control input and what happens after a failed attempt.'
]),
('10','잘 전달됐는지 확인하기','retell','R05',[
'필요한 규칙을 적었다면, 상대에게 이해했는지만 묻고 끝내지 마세요.',
'플레이어가 처음 무엇을 하고, 그 다음 화면에서 무엇이 바뀌는지 자기 말로 설명해 달라고 해 보세요.',
'가령 상대가 점프해서 벽을 넘는다고 답했다면, 우리가 전달하려던 캡처와 벽 파괴가 빠진 겁니다.',
'그러면 설명 전체를 더 길게 만드는 대신, 조종 대상이 바뀌는 순간과 벽이 무너지는 결과를 다시 연결합니다.',
'다시 설명했을 때 같은 행동이 돌아오는지 확인하면, 작품 이름이 통했다는 느낌과 실제로 기획이 전달된 상태를 구별할 수 있습니다.',
'이 대화는 설명을 위한 가상 예시입니다. 실제 팀의 실험 결과나 이해도를 측정한 수치는 아닙니다.'
],[
'After writing the necessary rules, do not stop at asking whether the listener understands.',
'Ask them to explain, in their own words, the player’s first action and what changes on screen afterward.',
'If they answer that the player jumps over the wall, the intended Capture and wall destruction are missing.',
'Instead of making the entire description longer, reconnect the change of controlled target to the wall breaking.',
'Checking whether the same action comes back in the retelling distinguishes a familiar-sounding title from a successfully communicated design.',
'This conversation is a fictional teaching example, not a measured result from an actual team.'
]),
('11','비교는 공통 이해 위에 얹기','shared','R05',[
'같은 행동과 조건을 공유한 뒤에는 비교가 다시 유용해질 수 있습니다.',
'두 사람이 방금 본 구간을 기준으로 말한다면, 어떤 시점과 조작을 가리키는지 확인하기가 쉬워지니까요.',
'다만 무엇을 빌려 설명하고, 무엇은 다른지 경계를 붙여 주세요.',
'예를 들어 옆에서 보는 시점은 비슷하지만, 목표는 끝까지 달리는 것이 아니라 흩어진 물건을 모으는 것이라고 말할 수 있습니다.',
'이 마지막 제안은 실제 마리오의 규칙을 바꿨다는 뜻이 아니라, 비교의 범위를 정하는 가상의 기획 문장입니다.',
'익숙한 이름으로 대화를 시작하더라도, 마지막에는 내 게임의 목표와 선택과 결과가 남아 있어야 합니다.'
],[
'Once the action and conditions are shared, a comparison can become useful again.',
'If both people refer to the section they just watched, the viewpoint and controls are easier to identify.',
'Still, specify what the comparison covers and what differs.',
'For example: the side view is similar, but the goal is to collect scattered objects rather than run to the end.',
'That is a fictional design sentence defining the comparison’s scope, not a claim that Mario’s actual rules have changed.',
'A familiar name can open the conversation, but the explanation must leave the listener with your game’s goals, choices and results.'
]),
('12','이름 없이도 남는 설명','conclusion','R06',[
'오늘 확인한 문제는 두 가지였습니다. 비교만 강조하면 우리 게임을 선택할 이유가 사라지고, 같은 이름도 서로 다른 경험을 떠올리게 할 수 있습니다.',
'그래서 이름을 더 붙이기 전에, 실제로 무엇을 하고 무엇이 달라지는지 설명해 보세요.',
'목표와 행동과 조건을 말하고, 상대의 말로 돌아온 플레이까지 확인하는 겁니다.',
'비교는 그 설명을 도와줄 수 있습니다. 하지만 게임 자체의 매력까지 대신해 주지는 않습니다.'
],[
'We found two problems: emphasizing similarity can erase the reason to choose your game, and the same name can evoke different experiences.',
'Before adding more titles, explain what the player actually does and what changes as a result.',
'State the goal, action and conditions, then check the play experience that comes back in the listener’s own words.',
'A comparison can support that explanation. It cannot replace the game’s own appeal.'
])]

ko={'title':'마리오 같다는 말로는 게임 기획이 전달되지 않는 이유','revision':'reference-preserving-v2','scenes':[]}
en={'title':'Why “Like Mario” Does Not Explain Your Game','revision':'reference-preserving-v2','scenes':[]}
for sid,title,kind,ref,k,e in scenes:
 assert len(k)==len(e)
 ko['scenes'].append({'id':sid,'title':title,'lines':k})
 en['scenes'].append({'id':sid,'title':title,'lines':e})
save(S/'narration.ko.json',ko);save(S/'narration.en.json',en)
save(S/'narration.tts.ko.json',ko)
manifest=read(R/'projects/game-reward-planning/production/reference-preserving-v2/tts-manifest.json')
manifest.update(slug='avoid-game-comparisons',revision='reference-preserving-v2')
manifest['paths']['script']='projects/avoid-game-comparisons/script/reference-preserving-v2/narration.tts.ko.json'
manifest['tts'].update(outputDir='shared/output/narration/avoid-game-comparisons/reference-preserving-v2',filenameStem='avoid-comparisons-reference-v2',sceneGapSeconds=.30)
save(V/'tts-manifest.json',manifest)
plan=read(P/'planning/chapter-plan.json');rev=plan['currentRevision']
rev['scriptDraft']={'ko':str((S/'narration.ko.json').relative_to(R)).replace('\\','/'),'en':str((S/'narration.en.json').relative_to(R)).replace('\\','/'),'status':'written-awaiting-source-motion-and-continuous-read-review','koCharacters':sum(len(x) for s in ko['scenes'] for x in s['lines']),'ttsManifest':str((V/'tts-manifest.json').relative_to(R)).replace('\\','/')}
rev['scenePlan']=[{'id':sid,'title':title,'kind':kind,'referenceBlock':ref,'renderer':'Motion Canvas','rendererReason':'2D relationships and word-to-action mapping, with independent gameplay evidence','implementationKind':'conceptual-illustration with separately identified gameplay','before':k[0],'visibleResult':k[-1],'transitionToNext':scenes[i+1][4][0] if i+1<len(scenes) else 'Existing exact10-second member screen','captionSpace':'960,970;48px;max2lines; actual layout preflight pending','sourcePlan':'NES and/or Odyssey only; precise cuts follow speech/source review','savedScene':None} for i,(sid,title,kind,ref,k,e) in enumerate(scenes)]
rev['terminology']=[{'ko':'피치','en':'Pitch','meaning':'프로젝트의 핵심 매력과 방향을 짧게 전달하는 설명','firstScene':'03','pronunciation':'피치'},{'ko':'캡처','en':'Capture','meaning':'캐피로 특정 대상을 조종해 그 능력을 사용하는 기능','firstScene':'07','source':'https://supermario.nintendo.com/mario-cappy/','pronunciation':'캡처'},{'ko':'파워문','en':'Power Moon','meaning':'오디세이에서 수집하는 달 모양 목표물','firstScene':'07','source':'https://supermario.nintendo.com/explore/','pronunciation':'파워문'}]
rev['selectedTitle']=ko['title'];plan['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(P/'planning/chapter-plan.json',plan)
print(json.dumps({'scenes':len(scenes),'lines':sum(len(s['lines']) for s in ko['scenes']),'koCharacters':rev['scriptDraft']['koCharacters']},ensure_ascii=False))
