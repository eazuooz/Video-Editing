"""Write the isolated D29 clarity revision; no media generation or shared mutations."""
from pathlib import Path
import copy, hashlib, json
ROOT=Path(__file__).resolve().parents[4]
PROJECT=ROOT/'projects/kind-to-beginners'
OUT=Path(__file__).resolve().parent
SCRIPT=PROJECT/'script/clarity-v3'
def load(p): return json.loads(p.read_text('utf-8-sig'))
def save(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
KO={
'01':[
'카트가 코너를 지나 다음 구간으로 달려갑니다. 익숙한 사람에게는 평범한 장면이지만, 처음 하는 사람에게는 자기 손으로 레이스를 이어 가는 것부터가 작은 성공입니다. 오늘은 처음 게임을 켠 친구가 왜 재미를 만나기도 전에 그만두는지 살펴보겠습니다. 함께 하는 목표를 맞추고, 첫 조작의 부담을 덜고, 스스로 고를 자리를 남기는 순서입니다.',
'초보자에게 친절하다는 건 스스로 해 보고, 결과를 알아차리고, 한 번 더 하고 싶어지는 기회를 지키는 일입니다. 같은 레이스에 들어왔어도, 두 사람이 기대한 첫 경험은 다를 수 있습니다.'
],
'02':[
'게임을 처음 해 보는 친구와 마리오 카트를 켰다고 생각해 보세요. 레이스는 정해진 코스를 달려 결승선에 먼저 도착하는 경기입니다. 익숙한 사람은 출발하자마자 앞서 나갈 방법을 찾습니다. 그런데 친구는 어느 버튼을 누르면 앞으로 가는지, 코너에서는 얼마나 방향을 틀어야 하는지부터 알아보는 중입니다.',
'숙련자는 순위가 올라가면 잘하고 있다고 느낍니다. 친구에게는 카트가 벽을 따라 비비는 대신, 내가 원하는 쪽으로 돌아가는 것부터가 성과일 수 있습니다. 한쪽이 결승선에 도착했어도, 다른 쪽은 자기 조작으로 무엇을 해냈는지 모른 채 첫 판을 끝낼 수 있죠.',
'한 사람은 실력을 겨루러 왔고, 다른 사람은 재미있어 보여서 잠깐 만져 본 것입니다. 같은 경기를 하고 있어도 들어온 목적은 다릅니다. 친구가 앞으로 나아가는 것부터 어려워한다면, 빠른 지름길을 더 알려 주기 전에 지금 무엇을 해 보고 싶은지부터 맞춰야 합니다.'
],
'03':[
'친구가 제대로 겨뤄 보자고 했다면 그 약속대로 승부하면 됩니다. 일부러 져 주는 것을 원하지 않을 수도 있죠. 전력 승부에 대한 예의는 서로 그 승부를 원할 때 성립합니다.',
'가볍게 처음 해 보는 자리라면 목표를 작게 맞출 수 있습니다. 이번에는 순위보다 첫 코너를 돌아보자, 그다음에는 아이템을 한 번 써 보자고 정하는 겁니다. 한꺼번에 잘해야 할 것을 늘리는 대신, 지금 직접 해낼 행동 하나를 남겨 둡니다.',
'방향 조작을 알려 준 뒤에는 친구가 직접 눌러 보게 합니다. 카트가 돌아가고, 코너를 지나 다음 길이 보입니다. 내 조작이 화면의 결과와 연결되는 순간이죠. 다음 코너는 스스로 시도해 볼 수 있습니다. 이렇게 옆 사람이 만들어 준 작은 성공을 게임의 첫 경험에도 넣을 수 있습니다.'
],
'05':[
'핸들 어시스트, 영어로 스마트 스티어링은 코너에서 코스를 벗어나려 할 때 방향 조절을 도와줍니다. 켜면 카트 뒤에 안테나가 나타납니다. 오토 액셀러레이트는 가속 버튼을 계속 누르지 않아도 앞으로 달리게 해 줍니다. 두 기능은 서로 다른 부담을 맡습니다.',
'가속을 유지하는 손의 부담을 덜면, 플레이어는 코너와 아이템을 더 살펴볼 수 있습니다. 방향 보조를 켜면 코스를 따라가는 감각부터 익힐 수 있죠. 사람이 할 일을 모두 지우는 대신, 지금 배우려는 행동에 집중할 자리를 만드는 겁니다.',
'익숙해진 뒤 보조를 끄는 선택도 남아 있습니다. 이 게임에는 코너에서 차체를 미끄러뜨리는 드리프트를 유지한 뒤, 모은 힘으로 잠깐 가속하는 미니 터보가 있습니다. 스마트 스티어링을 켠 동안에는 그 세 번째 단계인 울트라 미니 터보를 사용할 수 없습니다. 처음 들어오는 길을 넓히면서, 더 정교한 조작을 배울 여지도 함께 둔 설계입니다.'
],
'06':[
'이렇게 부담을 덜어 주는 방법이 꼭 보조 기능일 필요는 없습니다. 언패킹은 이삿짐 상자에서 물건을 꺼내 새집에 놓는 게임입니다. 상자에서 물건 하나를 꺼내고, 놓을 자리를 정하고, 그곳에 내려놓습니다. 우리가 이미 아는 정리 행동이 게임에서 할 일과 이어집니다.',
'이 게임은 버튼을 계속 누르고 있거나, 여러 버튼을 동시에 누르는 동작을 요구하지 않습니다. 시간 제한도 없어서 손이 느리다고 서두를 필요가 없습니다. 방금 놓은 물건을 다시 옮겨 보면서, 조작과 배치를 자기 속도로 익힐 수 있습니다.',
'그래도 어디에 무엇을 놓을지는 플레이어가 고릅니다. 조작의 부담을 낮춘 자리에 자기 취향과 판단이 남아 있는 거죠. 설계할 때도 무엇을 덜어 주고, 무엇을 직접 하게 둘지 나눠 볼 수 있습니다. 그런데 옆 사람이 그 자리까지 전부 정해 주면, 이제 다른 문제가 생깁니다.'
],
'08':[
'처음 게임을 해 보겠다는 관심을 얻는 것부터 쉽지 않습니다. 어렵게 생긴 그 관심을, 무엇을 해야 할지도 모른 채 끝나는 첫 판이나 끝없는 지시로 꺼뜨릴 필요는 없습니다. 한 번 해 볼 마음이 생긴 순간을 다음 시도로 이어 주면 됩니다.',
'함께 하는 목표를 맞추고, 첫 조작에서는 부담을 나눠 주고, 익숙해지는 동안에는 직접 선택할 여지를 돌려줍니다. 그러면 초보자는 누가 시켜서가 아니라 자기가 알아낸 결과 때문에 다시 손을 뻗게 됩니다.',
'게임은 결국 즐기려고 하는 것입니다. 처음 온 사람이 그 재미까지 자기 발로 들어올 수 있게 길을 열어 주세요. 초보자에게 친절한 설계는 다음 한 판을 스스로 고를 수 있게 만드는 설계입니다.'
]}
EN={
'01':[
'The kart rounds a corner and continues down the track. For an experienced player, this is ordinary. For someone new, keeping the race going under their own control can already be a small success. Why might a friend quit before reaching the fun? We will agree on a shared goal, ease the first controls, and leave room for personal choices, in that order.',
'Being kind to beginners protects their chance to try, recognize the result, and want another attempt. Two people can enter the same race expecting different first experiences.'
],
'02':[
'Imagine starting Mario Kart with a friend who has never played before. The race is about following the course and reaching the finish ahead of the others. The experienced player immediately looks for ways to pull ahead. Their friend is still finding the button that makes the kart move and learning how far to steer at a corner.',
'The experienced player feels successful when their position improves. For their friend, avoiding the wall and making the kart turn as intended may already be an achievement. One person can reach the finish while the other ends the first race without knowing what their own controls accomplished.',
'One person came to test their skill; the other simply thought it looked fun and wanted a try. They share a race but have different intentions. If your friend is struggling just to move forward, pause before explaining another fast shortcut and agree on what they want to try.'
],
'03':[
'If your friend asks for a serious race, honor that agreement and compete. They may not want you to lose deliberately. The etiquette of an all-out contest assumes that both people want one.',
'For a casual first try, agree on a smaller goal. Instead of the finishing position, first make it around one corner, then try using an item. Instead of adding everything they need to master at once, leave one achievable action.',
'After explaining steering, let your friend try the input. The kart turns, clears the corner, and reveals the road ahead. Their action connects to a visible result. They can try the next corner themselves. That small success offered by another person can also be built into a game’s opening experience.'
],
'05':[
'Smart Steering helps steer when the kart is about to leave the course around a corner. Enabling it adds an antenna to the back of the kart. Auto-Accelerate keeps it moving without holding the acceleration button. These options handle different burdens.',
'Reducing the need to hold acceleration leaves more attention for corners and items. Steering assistance lets someone begin by developing a feel for the track. Rather than removing every action, it creates room to focus on what they are learning.',
'The player can turn assistance off as they become comfortable. The game lets you hold a sideways slide through a corner, called a drift, and release the built-up charge for a brief Mini-Turbo boost. While Smart Steering is enabled, the third stage, Ultra Mini-Turbo, is unavailable. The design widens the entrance while leaving room to learn more precise control.'
],
'06':[
'Easing a burden does not always require an assistance option. Unpacking is about taking possessions out of moving boxes and finding places for them in a new home. Take out an item, choose a place, and set it down. A familiar act of tidying connects directly to the task in the game.',
'The game does not require holding buttons or pressing several buttons at once. There is no time limit, so slower hands do not have to hurry. You can move an item again after placing it, learning the controls and arrangement at your own pace.',
'The player still chooses what goes where. Reducing the control burden leaves room for personal taste and judgment. A designer can likewise separate what to ease from what the player should decide. If the person beside them dictates every placement, another problem appears.'
],
'08':[
'Getting someone interested enough to try a game is already difficult. That small opening need not end in a first round they never understood or a stream of instructions. Help the first willingness to try become another attempt.',
'Agree on a shared goal, ease the first controls, and return decisions as confidence grows. The newcomer can then reach for another try by choice, because of a result they discovered themselves.',
'People play games to enjoy themselves. Open a path that lets someone reach that enjoyment under their own power. Kindness to beginners protects their choice to play the next game.'
]}
def main():
 baseline={lang:load(PROJECT/f'script/batch-v1/narration.{lang}.json')for lang in ['ko','en']}
 result={}
 for lang,changes in [('ko',KO),('en',EN)]:
  value=copy.deepcopy(baseline[lang]);value['revision']='clarity-v3'
  for s in value['scenes']:
   if s['id'] in changes:s['lines']=changes[s['id']]
   if s['id']=='06':s['title']='조작은 가볍게, 선택은 직접'
  save(SCRIPT/f'narration.{lang}.json',value);result[lang]=value
  (SCRIPT/f'readthrough.{lang}.txt').write_text('\n\n'.join(line for s in value['scenes']for line in s['lines'])+'\n','utf-8')
 spoken=copy.deepcopy(result['ko']);spoken['language']='ko-spoken'
 save(SCRIPT/'narration.spoken-ko.json',spoken)
 # Reuse eligibility is not a claim that PCM has already been edited or heard.
 rows=[]
 for old,new in zip(baseline['ko']['scenes'],result['ko']['scenes']):
  for n,line in enumerate(new['lines']):
   preserved=n<len(old['lines'])and line==old['lines'][n]
   rows.append({'scene':new['id'],'paragraph':n+1,'unchangedText':preserved,'tts':'reuse-approved-pcm-if-clean-boundaries'if preserved else'new-sample-B-take','textSha256':hashlib.sha256(line.encode()).hexdigest()})
 save(OUT/'script-delta.json',{'revision':'clarity-v3','baseline':{'ko':sha(PROJECT/'script/batch-v1/narration.ko.json'),'en':sha(PROJECT/'script/batch-v1/narration.en.json')},'new':{l:sha(SCRIPT/f'narration.{l}.json')for l in ['ko','en']},'paragraphs':rows,'continuousVoiceDecision':'Root may generate one continuous new take to preserve natural phrasing. Unchanged text remains unchanged; no forced PCM seams. No TTS run by this preparation.','bgm':'Preserve baseline licensed track and relative narration balance.','sourceSettingDecision':'Allow items anywhere is verified but omitted as unnecessary option-list depth: current available official placement footage directly shows the lesson without an unobserved settings toggle.','readthrough':{'ko':'complete-heading-free-text-read','en':'complete-heading-free-text-read','audio':'not-yet-generated','noCombatExamples':True,'referenceClaimOrderPreserved':True}})
 save(OUT/'authorization.json',{'schemaVersion':1,'slug':'kind-to-beginners','revision':'clarity-v3','userDirectedOn':'2026-10-29','scope':'Replace fighting-heavy examples with relatable concept-matched examples; revise narration and explanatory scenes; preserve reference lesson/order, voice style/BGM and all previous outputs.','localProductionAuthorized':True,'newNarrationAuthorized':True,'newTts':'root-coordinated-only','costlyExecution':'await-parent-slot','gpuUserCondition':'user-confirmed-game-ended','noUiOrFocus':True,'platformMutation':False,'gitOwner':'root','otherVideosAuthorized':False})
 print('Wrote isolated KO/EN scripts, heading-free read-through and paragraph delta.')
if __name__=='__main__':main()
