// Independent lesson, researched concept only. No reference transcript/media reuse.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..'), base = 'projects/game-writing';
const read = p => JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write = (p,v) => { fs.mkdirSync(path.dirname(path.join(root,p)),{recursive:true}); fs.writeFileSync(path.join(root,p),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n'); };
const pairs = [
  ['01','이야기를 읽는 순서도 플레이어가 고른다','Players Choose the Reading Order','actual',[
    ['영화에서는 편집된 순서로 장면을 봅니다. 게임에서는 먼저 말을 걸 사람부터 플레이어가 고를 수 있죠.','A film presents its scenes in an edited order. In a game, even the first person you speak to can be your choice.'],
    ['디비니티 오리지널 신 투의 공식 영상에는 대화 중 여러 답을 고르는 화면이 나옵니다. 문장을 잘 쓰는 것만으로는 이 선택 뒤의 상황까지 정해지지 않습니다.','The official Divinity: Original Sin 2 footage shows several answers during a conversation. Good sentences alone do not define what happens after each choice.'],
    ['제작 도구에서는 질문을 쓰고, 그 아래에 행동 선택지를 따로 더합니다. 여기서 보이는 것은 사건을 구성하는 작업이고, 완성된 게임의 모든 조건 분기를 증명하는 화면은 아닙니다.','In the authoring tool, a question and its action options are edited separately. This shows event construction, rather than proving every condition in the finished game.'],
    ['이 문제를 확인하려고 항구의 봉인이라는 작은 이야기 게임을 직접 만들었습니다. 지금부터 이 화면은 우리 자체 제작 테스트입니다.','We built a small story game called The Harbor Seal to test the problem. From this point, this screen is our own playable prototype.'],
    ['항구 문지기에게 바로 가면 아직 받은 물건도, 알아낸 정보도 없습니다. 문지기의 첫 반응은 그 상태에서 시작해야 합니다.','Going straight to the harbor guard means we have neither the item nor the information yet. His first response must start from that state.'],
    ['이번에는 게시판을 먼저 읽고 돌아갑니다. 같은 장소와 같은 인물이어도, 플레이어가 가져온 사실은 달라졌습니다.','This time we read the notice first and come back. The place and character are unchanged, but the facts the player brings are different.'],
    ['다음 대사는 우리가 예상한 장면 번호보다 지금 실제로 성립하는 상황을 먼저 확인해야 합니다. 이 차이를 그림으로 정리해 볼게요.','The next line should check what is true now before assuming a scene number. Let us draw that distinction.']
  ]],
  ['02','장면 순서와 세계 상태를 분리한다','Separate Scene Order from World State','explanation',[
    ['첫 번째 원칙은 순서와 상태를 따로 쓰는 것입니다. 문지기를 두 번째로 만났다는 이유만으로 단서를 안다고 처리하면 안 됩니다.','The first principle is to write order and state separately. Meeting the guard second does not mean the player knows the clue.'],
    ['왼쪽 대본은 장면 하나, 장면 둘처럼 줄을 세웁니다. 오른쪽 대본은 단서를 봤는지, 물건을 갖고 있는지, 누구와 동행하는지를 확인합니다.','The script on the left lists scene one and scene two. The one on the right checks whether the clue was seen, the item is held, and the companion is present.'],
    ['여기서 모든 조합마다 새 이야기를 쓰라는 뜻은 아닙니다. 이 대사가 사실로 성립하는 데 필요한 조건만 적으면 됩니다.','This does not require a new story for every combination. Write only the conditions needed for this particular line to be true.'],
    ['예를 들어 단서를 모를 때는 질문하고, 알 때는 그 단서를 근거로 대답합니다. 같은 인물의 말투와 목표는 유지할 수 있죠.','For example, an uninformed player asks a question. An informed player can answer using the clue. The character can keep the same voice and goal.'],
    ['장면이 바뀌는 조건과 대사가 바뀌는 조건도 구분해 둡니다. 둘을 한 줄에 섞으면 나중에 작은 수정이 예상 밖의 분기를 만들기 쉽습니다.','Keep the condition for entering a scene separate from the condition for choosing a line. Combining them can make a small edit change an unexpected branch.']
  ]],
  ['03','플레이어가 안다고 인물도 아는 것은 아니다','Player Knowledge Is Not Character Knowledge','actual',[
    ['공식 디비니티 영상의 이 대화에서는 상대가 주인공의 이름을 부릅니다. 화면에서 확인할 수 있는 것은 상대의 인식이 대사에 드러난다는 점입니다.','In this official Divinity conversation, the speaker addresses the protagonist by name. What we can observe is that recognition is expressed in the dialogue.'],
    ['이 짧은 영상만으로 인식 조건의 구현을 단정할 수는 없습니다. 그래서 누가 정보를 전달받았는지는 자체 게임에서 직접 확인합니다.','This short clip cannot establish how the recognition condition is implemented. We test who actually receives the information in our own game.'],
    ['게시판에는 통행 증명의 규칙이 쓰여 있습니다. 플레이어가 읽어도 문지기가 플레이어의 방문을 저절로 알게 되지는 않습니다.','The notice explains the rule for proving passage. Reading it does not automatically tell the guard that the player has visited it.'],
    ['문지기에게 규칙을 들었다고 말하는 선택을 누릅니다. 이 행동이 있어야 문지기에게 전달한 정보가 기록됩니다.','We choose the answer that mentions the rule. That action records the information shared with the guard.'],
    ['이제 다시 말을 걸면 처음 묻는 대사 대신 이미 나눈 대화를 이어 갑니다. 정보 읽기와 정보 전달을 서로 다른 사건으로 만든 결과입니다.','Talking again now continues the earlier conversation instead of asking the introductory question. Reading and sharing were implemented as different events.'],
    ['상대를 만나기 전에 기록부터 읽는 순서도 실행해 봅니다. 중요한 것은 방문 순서가 달라도 아직 말하지 않은 인물이 사실을 아는 척하지 않는 것입니다.','We also try reading the record before meeting the guard. Whatever the visit order, a character should not pretend to know an unshared fact.'],
    ['글을 쓰다가 어색한 대사를 찾으면 문장부터 고치기 전에, 그 인물이 이 사실을 언제 알았는지 되짚어 보세요.','When a line sounds wrong, trace when that character learned the fact before rewriting the sentence.']
  ]],
  ['04','정보는 주인공·상대·세계로 나눠 기록한다','Track Knowledge for Each Participant','explanation',[
    ['두 번째 원칙은 정보의 주인을 구분하는 것입니다. 세계에서 일어난 일, 플레이어가 본 일, 상대에게 전한 일은 같은 기록이 아닙니다.','The second principle is to distinguish the owner of information. A world event, a fact seen by the player, and a fact shared with another character are separate records.'],
    ['세 칸을 따로 놓아 보면 오류가 보입니다. 문이 잠겨 있다는 사실은 세계 상태이고, 잠긴 이유를 읽었다는 것은 플레이어 정보입니다.','Three separate columns expose mistakes. A locked door is a world state. Reading why it was locked is player knowledge.'],
    ['그 이유를 문지기에게 말했을 때 비로소 상대에게 전한 정보가 됩니다. 그 전에는 네가 게시판을 봤구나 같은 대사를 쓰지 않는 편이 자연스럽습니다.','Only telling the guard makes it shared information. Until then, a line such as I know you read the notice would need another explanation.'],
    ['이름을 아는가, 약속을 들었는가, 이미 질문했는가처럼 대사에 필요한 사실부터 작게 관리합니다. 중요하지 않은 모든 행동까지 기록할 필요는 없습니다.','Start with small facts needed by the dialogue: knowing a name, hearing a promise, or asking a question before. There is no need to record every irrelevant action.'],
    ['반복 대화에서는 이미 끝낸 질문을 정리하고 현재 가능한 답을 남깁니다. 문장의 매끄러움은 이런 조건 위에서 만들어집니다.','On repeat conversations, retire answered questions and keep the replies that still make sense. Smooth writing is built on those conditions.']
  ]],
  ['05','물건과 동료가 바뀌면 대사도 확인한다','Check the Actual Owner of a Story Item','actual',[
    ['디비니티의 공식 제작 시연에서는 반지를 만들고, 이름과 설명을 바꾸고, 인벤토리에 넣는 과정이 보입니다.','The official Divinity authoring demonstration creates a ring, changes its name and description, and puts it into an inventory.'],
    ['이것은 물건을 이야기의 소재로 준비하는 실제 도구 작업입니다. 반지가 이후 어떤 줄거리를 여는지는 이 화면만 보고 덧붙이지 않습니다.','This is actual tool work preparing an item for a story. We do not invent a later plot consequence that this footage does not show.'],
    ['우리 항구 테스트에서는 증표를 동료에게 맡길 수 있게 했습니다. 물건이 파티 어딘가에 있다는 사실과 주인공이 지금 꺼낼 수 있다는 사실을 구분합니다.','In our harbor test, a companion can hold the seal. An item being somewhere in the party is different from the protagonist being able to present it now.'],
    ['증표를 동료에게 넘긴 뒤 문지기와 대화합니다. 함께 있을 때는 동료가 증표를 보여 주는 답을 선택할 수 있습니다.','We pass the seal to the companion and speak with the guard. While the companion is present, an answer lets that companion show it.'],
    ['이번에는 동료를 쉬게 한 뒤 혼자 돌아갑니다. 동료가 떠났는데도 주인공이 주머니에서 증표를 꺼내는 대사가 나오면 모순이겠죠.','This time we let the companion rest and return alone. A line claiming the protagonist takes the seal from a pocket would contradict its current owner.'],
    ['테스트에서는 소유자를 다시 확인해 그 답을 빼고, 증표를 다시 가져올 수 있는 대화를 남겼습니다. 동료를 다시 만나 물건을 회수하는 동작까지 이어집니다.','The test checks the owner again, removes that answer, and keeps a way to recover the seal. We continue by meeting the companion and taking it back.'],
    ['소설의 문장을 게임에 옮길 때는 손에 들었다, 건넸다, 함께 왔다 같은 표현에 실제 상태가 붙는다는 점을 기억하세요.','When turning prose into game dialogue, remember that held it, handed it over, and came together all require an actual state.']
  ]],
  ['06','과거에 얻었다와 지금 가지고 있다는 다르다','Past Acquisition Is Not Current Possession','explanation',[
    ['세 번째 원칙은 한 번 있었던 사실과 지금 성립하는 사실을 구분하는 것입니다. 증표를 얻었던 기록만으로 지금 소유자를 정하면 안 됩니다.','The third principle is to distinguish historical facts from current facts. Having acquired the seal earlier does not establish its current owner.'],
    ['그림에서 물건은 주인공, 동료, 보관함 사이로 옮겨 갑니다. 얻었다는 기록은 유지돼도 위치와 소유자는 계속 바뀝니다.','In the diagram, the item moves between the protagonist, companion, and storage. Its acquisition remains in history while its owner and location change.'],
    ['대사가 요구하는 것은 어느 쪽인지 적어 둡니다. 옛날에 찾았다는 회상은 과거 기록으로 충분하지만, 지금 보여 주겠다는 말에는 현재 소유와 접근이 필요합니다.','Write which fact a line requires. Remembering an earlier discovery needs history. Offering to show the item now needs present ownership and access.'],
    ['인물이 사라질 수도 있다면 그 인물만 알고 있는 필수 정보와 그 인물만 가진 필수 물건을 점검합니다. 대체 전달자나 회수 방법은 이야기 설정 안에서 마련하세요.','If a character can leave, inspect essential information and items held only by that character. Provide a fitting alternative source or recovery path.'],
    ['모든 예외를 막아 자유를 없애기보다, 허용한 변화가 이후 문장과 행동에 일관되게 반영되는지 확인하는 편이 좋습니다.','Rather than removing freedom to prevent every exception, check that permitted changes are reflected consistently in later words and actions.']
  ]],
  ['07','선택의 결과를 남기고 다음 장면으로 합류한다','Keep Consequences When Branches Rejoin','actual',[
    ['디비니티 제작 시연의 사건 카드에는 늑대를 공격하기, 먹이 주기, 달아나기처럼 서로 다른 행동이 적힙니다.','An event card in the Divinity authoring demonstration lists distinct actions such as attacking a wolf, feeding it, and running away.'],
    ['선택지 글자가 다르다고 결과도 자동으로 다른 것은 아닙니다. 보이는 편집 작업과 결과 처리의 설계는 나누어 살펴봐야 합니다.','Different labels do not automatically produce different consequences. The visible editing operation and the design of its outcomes must be considered separately.'],
    ['자체 게임에서는 항구로 가는 길에 세 답을 제공합니다. 먹이를 건네거나, 우회하거나, 침착하게 쫓아내는 선택입니다.','Our own game gives three answers on the road to the harbor: give food, take a detour, or calmly drive the animal away.'],
    ['먹이를 주면 가진 식량이 줄고, 우회하면 시간이 더 흐릅니다. 세 선택이 모두 같은 항구 앞에 도착해도 남은 자원과 지나온 일은 다릅니다.','Giving food uses a ration. Taking the detour takes more time. All three can reach the harbor, while resources and recorded events remain different.'],
    ['지금은 먹이를 준 경로를 실행하고, 다음에는 우회 경로를 새로 실행합니다. 항구의 인물이 지나온 일을 언급하는 대사도 그 결과에 맞춰 바뀝니다.','We run the feeding route, then start a fresh run for the detour. A later line mentioning the journey changes to match the result.'],
    ['별도의 거대한 맵을 세 개 만드는 대신, 같은 장면에 합류하되 선택의 흔적을 가져오도록 한 것입니다.','Instead of building three enormous maps, the branches rejoin the same scene while carrying traces of their choices.'],
    ['중요한 것은 어느 답을 골랐든 같은 칭찬을 주는 것이 아니라, 이 사람이 무엇을 했다는 다음 문장이 실제 행동과 맞는지입니다.','The question is whether the next statement about what this person did agrees with their actual action.']
  ]],
  ['08','합류해도 과거 선택을 지우지 않는다','Rejoining Does Not Mean Forgetting','explanation',[
    ['네 번째 원칙은 분기가 합류할 때 공통 조건과 남겨 둘 차이를 함께 정하는 것입니다. 항구에 도착했다는 사실은 공통입니다.','The fourth principle is to define both common conditions and retained differences when branches rejoin. Reaching the harbor is shared.'],
    ['먹이를 썼는지, 우회했는지 같은 선택은 남길 수 있습니다. 같은 장면에서도 짧은 반응이나 다음에 쓸 수 있는 답을 다르게 만들 수 있죠.','Whether food was used or a detour taken can remain recorded. Even within the same scene, a short response or available answer can differ.'],
    ['반대로 싸움에서 이겼다고 써야 하는 대사라면 승리가 먼저 성립해야 합니다. 실패한 플레이 뒤에 멋진 승리 문장을 그대로 붙이면 연결이 끊깁니다.','A line celebrating a victory requires that victory to have happened. A triumphant sentence after a failed encounter breaks the connection.'],
    ['이겼다와 다음 지역에 갈 수 있다는 별도 사실일 수도 있습니다. 패배해도 구조받아 진행하는 이야기라면 그 경로에 맞는 말을 마련합니다.','Winning and reaching the next area may be different facts. If defeat leads to rescue and continued progress, write lines for that route.'],
    ['분기 수를 무조건 늘리는 것이 목표는 아닙니다. 허용한 행동을 나중의 이야기가 거짓으로 바꾸지 않게 하는 것이 목표입니다.','The goal is not to maximize the branch count. It is to keep the later story from contradicting an action the game allowed.']
  ]],
  ['09','놓친 장면 없이도 다음 행동을 이해하게 한다','Make Essential Story Facts Recoverable','actual',[
    ['디비니티 제작 도구에서는 지도 위의 장소와 사건 카드를 나누어 준비합니다. 장소가 보이는 것과 그 장소에서 일어날 설명을 들었다는 것은 따로 다룰 수 있습니다.','The Divinity authoring tools prepare map locations and event cards separately. Seeing a location and hearing its explanation can be treated as separate facts.'],
    ['자체 테스트에서는 시작 설명을 넘기고 바로 항구로 이동해 봅니다. 긴 배경 설명을 읽지 않았어도 현재 필요한 행동은 확인할 수 있어야 합니다.','In our test, we skip the opening explanation and go straight to the harbor. The immediate action should still be understandable without reading the long background.'],
    ['문지기는 아직 건네받지 않은 증표를 요구합니다. 지금 어떤 물건이 필요한지, 어디서 확인할 수 있는지는 이 대화 안에 남겨 두었습니다.','The guard asks for a seal he has not received. The conversation still explains what is needed and where it can be checked.'],
    ['게시판을 열면 현재 단계에 필요한 사실만 다시 읽을 수 있습니다. 모르는 역사를 이미 아는 것처럼 대답하도록 강요하지 않습니다.','Opening the notice lets the player recover the facts needed at this stage. The game does not force an answer that assumes unfamiliar history.'],
    ['설명을 읽은 경로도 따로 실행합니다. 이미 들은 내용은 되풀이하지 않고 다음 행동을 확인하는 짧은 답으로 이어집니다.','We also run the route that read the explanation. Previously heard material is not repeated; a short answer confirms the next action.'],
    ['이런 전달 경로는 아무 이야기나 붙이는 안전망이 아닙니다. 이 장소와 이 인물이 왜 그 사실을 알려 줄 수 있는지 설정도 맞아야 합니다.','This is not a license to insert arbitrary exposition. The setting must explain why this place and character can provide that information.'],
    ['필수 사실을 다시 얻을 방법은 남기고, 더 알고 싶은 배경은 선택적으로 읽게 하면 대사의 목적이 분명해집니다.','Recoverable essential facts and optional background give each line a clearer purpose.']
  ]],
  ['10','필수 사실과 배경 설명을 구분한다','Separate Essential Facts from Background','explanation',[
    ['다섯 번째 원칙은 알아야 진행되는 사실과 더 알면 풍부해지는 배경을 구분하는 것입니다. 분량이 짧은지가 아니라 역할이 무엇인지로 나눕니다.','The fifth principle distinguishes facts required for progress from background that enriches the story. Classify their role, not their length.'],
    ['항구에 들어갈 조건은 필수 사실입니다. 문지기가 어릴 때 겪은 사건은 상황에 따라 선택 배경일 수 있습니다.','The condition for entering the harbor is essential. An incident from the guard’s childhood may be optional background.'],
    ['필수 사실을 오직 한 번 나오는 장면에만 넣으면 건너뛴 플레이어는 다음 행동의 이유를 잃을 수 있습니다. 자연스러운 재확인 경로를 마련하세요.','If an essential fact exists only in a one-time scene, skipping that scene can erase the reason for the next action. Provide a natural way to check it again.'],
    ['그렇다고 이미 읽은 플레이어에게 전부 다시 보여 줄 필요는 없습니다. 아는 사람에게는 짧은 확인, 모르는 사람에게는 필요한 설명을 줍니다.','There is no need to repeat everything to a player who read it. Offer a brief confirmation to informed players and the necessary explanation to others.'],
    ['이것은 게임 시작 시간을 줄이는 튜토리얼 논의와 다릅니다. 진행 중인 이야기에서 정보가 빠지거나 순서가 바뀌었을 때에도 대사의 근거를 유지하는 설계입니다.','This concerns missing or reordered story information during play: keeping a valid basis for dialogue throughout the narrative.']
  ]],
  ['11','예쁜 문장을 읽는 대신 다른 순서로 실행한다','Test the Story in Different Orders','actual',[
    ['이제 자체 항구 게임에서 글의 조건을 실제로 흔들어 봅니다. 정상 경로 한 번만 끝내는 것으로는 놓치는 조합이 있습니다.','Now we challenge the writing conditions in our harbor game. Completing the expected route once leaves other combinations untested.'],
    ['첫 번째 실행은 게시판을 먼저 읽고 증표를 얻은 뒤 문지기를 만납니다. 요구한 물건을 실제로 건네면서 다음 장면이 열립니다.','In the first run, we read the notice, acquire the seal, and meet the guard. Handing over the required item opens the next scene.'],
    ['두 번째는 설명을 넘기고 문지기부터 만나 봅니다. 모르는 규칙을 알고 있다고 말하지 않으며, 필요한 정보를 얻을 길이 남아 있는지 확인합니다.','In the second run, we skip the explanation and meet the guard first. We check that the dialogue does not claim unlearned knowledge and that information remains accessible.'],
    ['세 번째는 증표를 동료에게 맡긴 뒤 동료를 쉬게 합니다. 없는 물건을 보여 주는 답이 사라지는지, 회수한 뒤에는 다시 가능한지 비교합니다.','In the third run, we leave the seal with a resting companion. We compare the unavailable answer with its return after retrieving the item.'],
    ['네 번째는 서로 다른 길의 선택을 실행합니다. 같은 항구에 합류해도 식량과 이동 기록이 덮어써지지 않는지 확인합니다.','In the fourth run, we make different road choices. We check that rejoining the harbor does not overwrite rations or the journey record.'],
    ['각 실행에서는 누른 행동, 바뀐 사실, 선택된 대사를 함께 남깁니다. 오류가 나면 장면 제목만 보고 추측하지 않고 그 기록에서 연결을 찾습니다.','Each run records the action, changed facts, and selected dialogue together. When something fails, the connection can be traced in that record.'],
    ['이 테스트는 이야기의 재미를 사람 대신 판정하는 것이 아닙니다. 우리 대사가 실제 플레이와 모순되는지 확인하는 작은 기술 검증입니다.','This test does not judge story enjoyment in place of people. It is a small technical check for contradictions between writing and actual play.']
  ]],
  ['12','조건까지 적어야 플레이 가능한 대본이 된다','A Playable Script Includes Its Conditions','explanation',[
    ['게임 대본에는 문장뿐 아니라 그 문장이 성립하는 조건이 필요합니다. 누가 무엇을 알고, 무엇을 가지고, 어떤 행동을 했는지 함께 적어 주세요.','A game script needs both its sentences and the conditions that make them valid. Record who knows what, who holds what, and which actions occurred.'],
    ['순서와 상태를 나누고, 정보의 주인을 구분합니다. 과거에 얻은 것과 지금 가진 것을 혼동하지 않습니다.','Separate order from state and distinguish who owns information. Do not confuse past acquisition with present possession.'],
    ['분기가 합류해도 행동의 흔적은 남기고, 필요한 사실은 놓친 플레이어도 다시 얻을 수 있게 합니다.','Keep traces of actions when branches rejoin, and let players recover essential facts they missed.'],
    ['마지막으로 다른 순서와 다른 소유 상태로 직접 실행해 보세요. 기록은 문장의 오류를 찾는 데 도움이 되고, 사람의 플레이 검토는 이해와 감정을 확인해 줍니다.','Finally, play through different orders and ownership states. Logs help locate contradictions; human play review evaluates understanding and emotion.'],
    ['지금 쓰는 대사의 옆에 한 줄만 더 적어 보세요. 이 말이 참이려면 먼저 무엇이 일어나야 할까요? 그 질문이 게임 글쓰기를 실제 플레이와 이어 줍니다.','Add one line beside the dialogue you are writing: what must happen first for this statement to be true? That question connects game writing to actual play.']
  ]]
];
for(const lang of ['ko','en']) {
  write(`${base}/script/narration.${lang}.json`,{
    title:lang==='ko'?'게임 시나리오 쓰는 법: 선택과 순서가 바뀌어도 말이 되게':'Writing Game Stories That Survive Player Choice',
    authorship:'Independent channel script; concept research only; no reference transcript translation or reuse',
    scenes:pairs.map(([id,ko,en,classification,lines])=>({id,title:lang==='ko'?ko:en,classification,lines:lines.map(p=>p[lang==='ko'?0:1])}))
  });
}
const manifest = read(`${base}/project.json`), approved = read('projects/responsive-game-feedback/project.json');
manifest.status='script-and-playtest-preparation';
manifest.paths.scriptEn=`${base}/script/narration.en.json`;
manifest.tts.maxNewTokens=1280;
manifest.audio.backgroundMusic=approved.audio.backgroundMusic;
manifest.audio.mixStatus='approved-music-awaiting-current-voice-and-timing';
manifest.channelIntro={...approved.channelIntro,appliedToFinal:false};
manifest.batch={queue:'production/batches/sakurai-planning-game-design/queue.json',sourceIndex:13,privacy:'private',noPublicSchedule:true,uploadToYouTube:true};
manifest.reference={url:'https://www.youtube.com/watch?v=ssvIEm_2mYM',kind:'concept-research-only',scriptVerbatimReuse:false,sourceVideoOrAudioReuse:false};
manifest.approvals={script:'Independent 12-scene bilingual lesson under authorized batch production; actual content/Studio duplicate preflight passed before creation',voiceSample:'Same approved Qwen3-TTS 1.7B/ref-text voice',bgm:'Existing continuous Nimbus reused by authorization',final:'pending actual narration/render/QA/collection',publication:'private only; public release belongs to user'};
manifest.publishReady=false;
manifest.warnings=[
  '현재는 독립 대본·자료·자체 플레이테스트 준비이며 최종 영상이 아닙니다.',
  '전체 인간 청취와 이야기의 이해·감정에 대한 사람 플레이 검토는 pending입니다.',
  'Larian DOS2 정책을 검토했지만 실제 게시 범위와 최종 공개 권리 판단은 pending입니다.',
  'Nimbus 복원 사본을 사용하며 원래 Audio Library 파일 확인이 남아 있습니다.',
  '회원 원본 이미지의 잘린 핸들은 추정하지 않습니다.',
  '외부 미디어 백업 위치는 아직 지정되지 않았습니다.'
];
manifest.editing.exampleInterleaving.reviewStatus='six chapter connections planned; actual footage/timing/visual review pending';
manifest.editing.timingStatus='pending-measured-narration-and-valid-action-cuts';
write(`${base}/project.json`,manifest);
const queue=read('production/batches/sakurai-planning-game-design/queue.json'),item=queue.items.find(i=>i.slug==='game-writing');
item.status='in-progress';item.stage='bilingual-script-and-fresh-source-playtest-preparation';
item.checkpoints.script=true;item.updatedAt=new Date().toISOString();
item.project=`${base}/project.json`;item.script={ko:manifest.paths.script,en:manifest.paths.scriptEn,scenes:12,paragraphs:72,ttsStarted:false};
item.nextAction='Build and validate own Harbor Seal playtest; inspect matching native DOS2 cuts; prepare independent 2.5D scenes. Wait for free GPU before the single approved TTS run.';
delete item.sourceDownload;
item.sourceDownloads=[['gm-tutorial','ZSh7hOZl9hg',85411],['gameplay-overview','YEgrKLregCw',13338]].map(([stem,sourceVideoId,sessionId])=>{
 const relative=`shared/assets/game-writing/raw/${stem}.mp4`,buffer=fs.readFileSync(path.join(root,relative));
 return {sourceVideoId,sessionId,path:relative,state:'finished',exitCode:0,bytes:buffer.length,sha256:crypto.createHash('sha256').update(buffer).digest('hex'),noRestart:true};
});
queue.updatedAt=new Date().toISOString();write('production/batches/sakurai-planning-game-design/queue.json',queue);
console.log(JSON.stringify({scenes:pairs.length,paragraphs:pairs.reduce((n,p)=>n+p[4].length,0),downloads:item.sourceDownloads.map(s=>({path:s.path,bytes:s.bytes,sha256:s.sha256})),ttsStarted:false},null,2));
