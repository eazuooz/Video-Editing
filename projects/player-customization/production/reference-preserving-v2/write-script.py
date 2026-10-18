"""Independently worded paired lesson; finalize only after source review."""
from pathlib import Path
import argparse,json
R=Path(__file__).resolve().parents[4];P=R/'projects/player-customization';H=P/'production/reference-preserving-v2'
ap=argparse.ArgumentParser();ap.add_argument('--draft',action='store_true');args=ap.parse_args()
parts=[
('01','고르는 시간도 게임이 된다',[
'안녕하세요, 얌얌코딩입니다. 장비를 고르고 캐릭터를 꾸미다가, 정작 게임을 시작할 시간을 놓친 적 있나요?',
'그 시간도 게임이 주는 재미일 수 있습니다. 오늘은 선택의 결과를 보여 주는 방법에서 시작해, 고르기와 시험을 편하게 만드는 방법, 성능과 별개인 꾸미기의 재미까지 이어 보겠습니다.',
'먼저 무기를 바꿀 때 숫자와 실제 공격 모습이 함께 보이는 상점으로 가 보죠.'
],[
'Hello, this is Yamyam Coding. Have you ever spent so long choosing equipment or styling a character that you barely started playing?',
'That time can be part of the fun. We will begin with showing what a choice does, then connect easier selection and testing to the pleasure of appearance changes that do not depend on power.',
'Let us begin in a shop where weapon information and the resulting attack can be seen together.'
]),
('02','숫자 옆에 결과를 보여 주기',[
'Jets’n’Guns 2는 옆으로 진행하며 적을 쏘는 슈팅 게임입니다. 상점에서는 기체에 무기를 장착하고, 바로 옆 시험 공간에서 그 조합의 발사 모습을 볼 수 있습니다.',
'무기 설명에 공격력이나 발사 속도만 적혀 있다면, 익숙하지 않은 사람은 어떤 느낌인지 짐작하기 어렵습니다. 앞으로 길게 뻗는지, 넓게 퍼지는지, 여러 발이 이어지는지는 움직이는 결과를 보면 훨씬 빠르게 알 수 있죠.',
'지금 볼 곳은 오른쪽의 시험 공간입니다. 선택 화면에서 바뀌는 항목과 실제 발사 모습을 함께 읽어 보세요. 두 기체가 함께 보이므로, 각각에서 나오는 탄환의 방향과 간격을 구별해서 살펴보면 좋습니다.',
'이렇게 선택 결과를 미리 보여 주는 것을 프리뷰라고 합니다. 프리뷰는 멋진 장면만 보여 주기보다, 플레이어가 결정하는 데 필요한 차이를 보여 줘야 합니다.',
'결과를 알 수 있게 됐다면, 다음은 그 차이가 선택할 만한 이유가 되는지입니다. 모든 면에서 더 좋은 무기 하나만 있다면, 나머지를 비교할 이유가 줄어드니까요.'
],[
'Jets’n’Guns 2 is a side-scrolling shooter. Its shop lets you equip weapons and see the resulting shots in a test area right beside the equipment.',
'Attack power and fire-rate numbers can be difficult to imagine. A moving result makes it much easier to understand whether an attack reaches forward, spreads out, or fires in a sequence.',
'Watch the test area on the right while reading the changing selection. Two ships are visible, so distinguish the direction and timing of the shots coming from each one.',
'Showing a result before committing to it is a preview. A useful preview reveals differences that help the player decide, rather than simply presenting a spectacular image.',
'Once the result is understandable, the next issue is whether those differences create a reason to choose. If one weapon is better in every respect, there is little reason to compare the rest.'
]),
('03','장점이 다르면 선택도 달라진다',[
'Armored Core VI에서는 로봇의 무기와 여러 부품을 조합합니다. 지금 비교하는 부스터는 기체의 움직임을 담당하는 부품입니다.',
'이 후보는 이동 속도 표시가 306에서 320으로 오르지만, 순간적으로 피하는 동작인 퀵부스트의 에너지 소비는 480에서 560으로 늘어납니다. 메뉴가 보여 주는 능력치 비교이며, 실제 이동 속도를 측정한 값은 아닙니다. 이렇게 얻는 것과 포기하는 것이 연결된 관계를 트레이드오프라고 합니다.',
'차이를 간단한 가상 무기로 계산해 보죠. A는 한 발에 피해 100, 발사 간격은 2초입니다. B는 피해 40, 발사 간격은 0.5초입니다. 오래 계속 맞힌다고 보면, 초당 평균 피해는 A가 50, B가 80입니다.',
'그러면 B가 언제나 더 좋을까요? 한 번 쏠 기회만 생기고 적의 남은 체력이 90이라면 A 한 발이 더 유리할 수 있습니다. 이 계산은 실제 게임 수치가 아니라, 빗나감과 방어력 같은 조건을 뺀 설명용 예시입니다.',
'핵심은 선택지마다 잘하는 일과 불리한 상황을 분명하게 만드는 겁니다. 그 차이가 커질수록 재미있는 조합도 늘지만, 원하는 장비를 찾는 일까지 어려워져서는 곤란하겠죠.'
],[
'In Armored Core VI, players combine weapons and parts for a robot. The booster being compared here is a part responsible for the machine’s movement.',
'This candidate raises the displayed boost speed from 306 to 320, but increases the energy consumption of Quick Boost, a brief evasive move, from 480 to 560. These are menu comparisons, not measured movement speeds. A linked benefit and sacrifice is called a trade-off.',
'Consider two fictional weapons. A deals 100 damage every two seconds. B deals 40 every half second. During sustained hits, their average damage per second is 50 and 80 respectively.',
'Does that make B universally better? If there is only one opportunity to fire and the enemy has 90 health left, one shot from A may be preferable. These are illustrative numbers, not game statistics; misses and armor are excluded.',
'The aim is to make each option’s strengths and unfavorable situations clear. More distinctive options can create interesting combinations, but finding the desired equipment must remain manageable.'
]),
('04','찾는 부담을 줄여 선택에 집중하기',[
'서로 다른 장비를 알아보려면, 먼저 목록에서 찾아낼 수 있어야 합니다. 젤다의 전설 브레스 오브 더 와일드에서는 장비와 아이템의 종류가 화면의 분류와 아이콘으로 구별됩니다.',
'아이콘은 작은 그림으로 종류를 알려 주는 표시입니다. 무기인지 방어구인지부터 읽을 수 있으면, 모든 이름과 설명을 한 줄씩 훑는 부담을 덜 수 있습니다. 생김새가 비슷해 헷갈리는 아이콘에는 이름이나 기능 표시도 함께 연결해야겠죠.',
'몬스터 헌터 월드: 아이스본의 방어구 제작 화면도 같은 원리로 읽을 수 있습니다. 부위별 아이콘을 선택하면 장비의 상세 정보와 캐릭터의 미리보기가 연결됩니다.',
'여기서 정렬의 원리는 설명용 목록으로 보겠습니다. 정렬은 기준에 따라 나열 순서를 바꾸는 기능입니다. 공격력 순으로 보고 싶은 사람과 자신이 쓰는 무기 종류만 찾는 사람은 필요한 기준이 다르죠. 분류와 정렬은 선택을 대신하기보다, 비교할 후보를 빠르게 좁히는 도구가 됩니다.',
'그래도 처음에는 어떤 조합부터 시작할지 막막할 수 있습니다. 후보를 찾게 해 주는 것에서 한 걸음 더 나아가, 출발할 조합을 제안할 수도 있죠.'
],[
'Players must first be able to find the options they want to compare. In The Legend of Zelda: Breath of the Wild, categories and icons help distinguish equipment and item types.',
'An icon is a small picture that identifies a type. Recognizing weapons and armor reduces the need to read every name and description. Similar-looking icons should also be connected to a readable name or function.',
'The armor-forging screen in Monster Hunter World: Iceborne follows the same principle. Selecting a body-part icon connects equipment details with a character preview.',
'We will use an illustrative list to explain sorting. Sorting changes the order according to a criterion. Someone seeking the highest attack value and someone seeking a preferred weapon type need different criteria. Categories and sorting narrow the candidates without choosing for the player.',
'A newcomer may still have no idea which combination to start with. Beyond helping players find candidates, a game can suggest an initial set.'
]),
('05','자동 장비는 출발점을 도와준다',[
'자동 장비 기능은 정해 둔 기준에 따라 부품이나 아이템을 골라 장착하는 방식입니다. 처음부터 여러 칸을 모두 이해해야 하는 부담을 줄여 줄 수 있습니다.',
'다만 자동으로 고른 최강 장비라는 말에도 기준이 필요합니다. 공격력 합계가 가장 높은 조합과, 추운 지역을 버티기 위한 조합은 같은 답이 아닐 수 있습니다.',
'여기서는 설명용 메뉴에서 공격 중심이라는 목표를 먼저 고르고, 그 기준에 맞는 조합을 채워 보겠습니다. 실제 게임의 자동 장착을 재현한 화면이나, 모든 상황의 정답을 계산한 결과는 아닙니다.',
'이렇게 시작할 조합을 마련한 뒤 마음에 들지 않는 부분만 바꿀 수 있으면, 자동 기능과 직접 고르는 재미가 함께 살아납니다. 이제 고른 조합이 손에도 맞는지 확인할 차례입니다.'
],[
'Automatic equipment selects and equips parts or items according to a defined rule. It can reduce the initial burden of understanding every equipment slot.',
'Even “strongest equipment” needs a criterion. The set with the highest combined attack may differ from one suited to surviving a cold region.',
'In this illustrative menu, we first choose an attack-focused goal and then fill the equipment slots using that rule. This is neither a reproduction of a specific game’s auto-equip system nor a universal optimum.',
'Once there is a usable starting set, players can change only the parts they dislike. Automatic assistance and manual choice can coexist. The next step is to find out whether the selected combination feels right in use.'
]),
('06','바꾸고 곧바로 시험하기',[
'선택 화면에서 좋아 보여도, 실제로 움직이거나 공격하면 느낌이 다를 수 있습니다. 그래서 바꾸는 곳과 시험하는 곳 사이의 거리가 중요합니다.',
'TerraTech는 부품을 붙여 탈것을 만드는 게임입니다. 조립한 결과를 바로 움직여 보고, 다시 손볼 수 있다는 점이 커스터마이징과 시험을 가깝게 이어 줍니다.',
'앞에서 본 Jets’n’Guns 2의 상점도 장비와 시험 공간을 함께 둡니다. 메뉴에서 나와 긴 이동이나 전투를 거쳐야만 차이를 알 수 있다면, 마음에 들지 않는 조합을 고칠 때마다 같은 준비를 반복해야 하죠.',
'바꾸기, 시험하기, 다시 바꾸기. 이 고리가 짧으면 예상과 다른 결과도 다음 선택을 위한 정보가 됩니다. 시험은 다 고른 뒤 한 번 하는 절차에 그치지 않고, 고르는 도중에도 도움이 됩니다.',
'지금까지는 잘 움직이고 잘 싸우는 조합을 봤습니다. 하지만 바꾼 결과가 마음에 든다는 말이, 꼭 성능이 좋아졌다는 뜻일까요?'
],[
'Something that looks good in a menu can feel different when moving or attacking. The distance between changing a setup and testing it therefore matters.',
'TerraTech lets players construct vehicles from parts. Being able to move the result and return to adjustments connects customization closely to testing.',
'The Jets’n’Guns 2 shop similarly places equipment and its test area together. If a long trip or battle is required before noticing a difference, every unwanted combination requires repeating that preparation.',
'Change, test, and change again. A short loop turns an unexpected result into information for the next choice. Testing can assist the selection process itself, rather than occurring only after every decision is complete.',
'So far, we have considered combinations for movement and combat. But does liking a change necessarily mean that performance improved?'
]),
('07','성능과 별개로 나를 표현하기',[
'모여봐요 동물의 숲에서는 얼굴과 머리 모양 같은 외형을 고르며, 화면 속 캐릭터를 자신이 원하는 모습에 가깝게 만들 수 있습니다.',
'선택한 모양이 미리 보이고, 다른 항목을 고르면 캐릭터의 인상도 달라집니다. 이때 중요한 결과는 피해량이 얼마나 늘었는지가 아니라, 이 모습이 내 취향에 맞는지입니다.',
'멋진 로봇을 만들고 싶은 사람도 있고, 귀여운 캐릭터를 만들고 싶은 사람도 있습니다. 같은 성능을 유지하면서 외형을 바꿀 수 있어도, 조합을 상상하고 비교하는 재미는 충분히 생길 수 있죠.',
'성능과 외형을 연결할지, 각각 선택하게 할지는 게임마다 다릅니다. 중요한 건 플레이어가 지금 무엇을 바꾸고 있는지 알게 하고, 고른 모습과 결과를 확인할 수 있게 만드는 겁니다.'
],[
'In Animal Crossing: New Horizons, choosing features such as a face and hairstyle lets players bring their character closer to the appearance they want.',
'The chosen appearance is previewed, and selecting another option changes the character’s impression. The important result is whether it suits the player’s taste, rather than how much damage it adds.',
'Some people want an impressive robot; others want a cute character. Even with unchanged performance, imagining and comparing appearances can be enjoyable.',
'Games can link performance and appearance or let players choose them separately. Players should understand what they are changing and be able to see the chosen appearance and result.'
]),
('08','무엇을 바꿀지와 어떻게 바꿀지',[
'이제 커스터마이징을 결과물만이 아니라, 선택하는 과정으로 다시 볼 수 있습니다.',
'효과가 보이면 차이를 예상할 수 있고, 장단점이 분명하면 고를 이유가 생깁니다. 원하는 항목을 쉽게 찾고 바로 시험할 수 있으면, 다음 조합을 시도하는 부담도 줄어듭니다.',
'그 선택이 꼭 강해지는 방향일 필요도 없습니다. 마음에 드는 모습을 만들며 상상하는 시간은 전투나 이동과 다른 종류의 재미가 될 수 있습니다.',
'게임을 만들 때는 바꿀 수 있는 항목과 함께, 어떻게 고르고 확인하고 다시 바꾸게 할지도 살펴보세요. 여러분이 가장 오래 머물렀던 장비창이나 꾸미기 화면은 어떤 게임이었나요?'
],[
'Customization can now be considered as a process of choosing, rather than only as the finished result.',
'Visible effects make differences predictable, while clear trade-offs create reasons to choose. Easy navigation and immediate testing reduce the burden of trying the next combination.',
'The choice need not always make the character stronger. Imagining an appealing appearance can provide a kind of enjoyment distinct from combat or movement.',
'When designing a game, consider both what can be changed and how players choose, check, and revise it. Which equipment or appearance screen has kept you occupied the longest?'
])]
if not args.draft:
 selection=json.loads((H/'source-selection.json').read_text(encoding='utf-8'))
 assert selection['allSelectedClaimsActuallyViewed'] and selection['referenceOnlyMediaExcluded']
 assert {s['key'] for s in selection['sources']} >= {'jets2-shop','acvi-assembly','botw-menu','mh-menu','terratech-build','acnh-appearance'}
out=P/'script/reference-preserving-v2';out.mkdir(parents=True,exist_ok=True)
status='draft-awaiting-independent-footage-review' if args.draft else 'locked-after-independent-footage-and-complete-text-review'
aliases={'Jets’n’Guns 2':'제츠 앤 건즈 투','Armored Core VI':'아머드 코어 식스','TerraTech':'테라테크','306':'삼백육','320':'삼백이십','480':'사백팔십','560':'오백육십','100':'백','0.5':'영 점 오','90':'구십','80':'팔십','50':'오십','40':'사십','2초':'이 초','A':'에이','B':'비'}
for lang,index in [('ko',2),('en',3),('spoken-ko',2)]:
 scenes=[]
 for sid,title,ko,en in parts:
  lines=list(ko if index==2 else en);assert len(ko)==len(en)
  if lang=='spoken-ko':
   for a,b in aliases.items():lines=[line.replace(a,b) for line in lines]
  scenes.append(dict(id=sid,title=title,lines=lines))
 data=dict(title='장비창에서 나오기 아쉬운 게임은 무엇이 다를까?',status=status,scenes=scenes)
 (out/f'narration.{lang}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'caption-aliases.json').write_text(json.dumps(aliases,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='\n\n'.join(line for s in parts for line in s[2])
(out/'narration.ko.txt').write_text(text+'\n',encoding='utf-8')
print(json.dumps(dict(status=status,scenes=len(parts),paragraphs=sum(len(s[2]) for s in parts),characters=len(text)),ensure_ascii=False))
