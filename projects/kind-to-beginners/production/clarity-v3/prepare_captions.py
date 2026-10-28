"""Authored bilingual clause boundaries; no guessed audio timestamps."""
from pathlib import Path
import json,hashlib,re
P=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def split_ends(text,ends):
 result=[];cursor=0
 for end in ends:
  at=text.find(end,cursor)
  if at<0:raise ValueError('Unmatched authored clause: '+end)
  stop=at+len(end);result.append(text[cursor:stop].strip());cursor=stop
 if text[cursor:].strip():result.append(text[cursor:].strip())
 return result
# Each paired boundary was selected from complete locked KO/EN text.
BOUNDARIES={
'01-p01':(
 ['달려갑니다.','장면이지만,','작은 성공입니다.','그만두는지 살펴보겠습니다.','목표를 맞추고,','부담을 덜고,'],
 ['track.','ordinary.','success.','the fun?','goal,','controls,']),
'01-p02':(
 ['스스로 해 보고, 결과를 알아차리고,','기회를 지키는 일입니다.','같은 레이스에 들어왔어도,'],
 ['their chance to try, recognize the result,','and want another attempt.','Two people can enter the same race']),
'02-p01':(
 ['마리오 카트를 켰다고 생각해 보세요.','결승선에 먼저 도착하는 경기입니다.','앞서 나갈 방법을 찾습니다.','어느 버튼을 누르면 앞으로 가는지,'],
 ['has never played before.','ahead of the others.','pull ahead.','the button that makes the kart move']),
'02-p02':(
 ['잘하고 있다고 느낍니다.','벽을 따라 비비는 대신,','성과일 수 있습니다.','한쪽이 결승선에 도착했어도,'],
 ['position improves.','For their friend, avoiding the wall','may already be an achievement.','One person can reach the finish']),
'02-p03':(
 ['한 사람은 실력을 겨루러 왔고,','잠깐 만져 본 것입니다.','들어온 목적은 다릅니다.','친구가 앞으로 나아가는 것부터 어려워한다면,','빠른 지름길을 더 알려 주기 전에'],
 ['One person came to test their skill;','wanted a try.','different intentions.','If your friend is struggling just to move forward,','pause before explaining another fast shortcut']),
'03-p01':(
 ['그 약속대로 승부하면 됩니다.','원하지 않을 수도 있죠.'],
 ['honor that agreement and compete.','lose deliberately.']),
'03-p02':(
 ['목표를 작게 맞출 수 있습니다.','첫 코너를 돌아보자,','한 번 써 보자고 정하는 겁니다.','한꺼번에 잘해야 할 것을 늘리는 대신,'],
 ['agree on a smaller goal.','first make it around one corner,','then try using an item.','Instead of adding everything they need to master at once,']),
'03-p03':(
 ['친구가 직접 눌러 보게 합니다.','코너를 지나 다음 길이 보입니다.','화면의 결과와 연결되는 순간이죠.','다음 코너는 스스로 시도해 볼 수 있습니다.'],
 ['let your friend try the input.','reveals the road ahead.','connects to a visible result.','try the next corner themselves.']),
'05-p03':(
 ['선택도 남아 있습니다.','차체를 미끄러뜨리는 드리프트를 유지한 뒤,','잠깐 가속하는 미니 터보가 있습니다.','스마트 스티어링을 켠 동안에는','울트라 미니 터보를 사용할 수 없습니다.','처음 들어오는 길을 넓히면서,'],
 ['as they become comfortable.','called a drift,','for a brief Mini-Turbo boost.','While Smart Steering is enabled,','Ultra Mini-Turbo, is unavailable.','The design widens the entrance']),
'06-p01':(
 ['보조 기능일 필요는 없습니다.','새집에 놓는 게임입니다.','상자에서 물건 하나를 꺼내고,','놓을 자리를 정하고,','그곳에 내려놓습니다.'],
 ['an assistance option.','a new home.','Take out an item,','choose a place,','and set it down.']),
'06-p02':(
 ['버튼을 계속 누르고 있거나,','동시에 누르는 동작을 요구하지 않습니다.','시간 제한도 없어서','서두를 필요가 없습니다.','방금 놓은 물건을 다시 옮겨 보면서,'],
 ['The game does not require holding buttons','or pressing several buttons at once.','There is no time limit,','so slower hands do not have to hurry.','You can move an item again after placing it,']),
'06-p03':(
 ['플레이어가 고릅니다.','자기 취향과 판단이 남아 있는 거죠.','설계할 때도 무엇을 덜어 주고,','무엇을 직접 하게 둘지 나눠 볼 수 있습니다.','그런데 옆 사람이 그 자리까지 전부 정해 주면,'],
 ['chooses what goes where.','personal taste and judgment.','A designer can likewise separate what to ease','from what the player should decide.','If the person beside them dictates every placement,']),
'08-p01':(
 ['관심을 얻는 것부터 쉽지 않습니다.','어렵게 생긴 그 관심을,','끝없는 지시로 꺼뜨릴 필요는 없습니다.'],
 ['try a game is already difficult.','That small opening need not end','or a stream of instructions.']),
'08-p02':(
 ['함께 하는 목표를 맞추고,','첫 조작에서는 부담을 나눠 주고,','직접 선택할 여지를 돌려줍니다.','그러면 초보자는 누가 시켜서가 아니라'],
 ['Agree on a shared goal,','ease the first controls,','return decisions as confidence grows.','The newcomer can then reach for another try by choice,'])
}
def main():
 ko=read(P/'script/clarity-v3/narration.ko.json');en=read(P/'script/clarity-v3/narration.en.json')
 prior=read(P/'production/batch-v1/caption-units.json');out={'slug':P.name,'revision':'clarity-v3','status':'authored-bilingual-clauses','paragraphs':{}}
 for a,b in zip(ko['scenes'],en['scenes']):
  assert a['id']==b['id']
  for j,(k,e)in enumerate(zip(a['lines'],b['lines'])):
   key=f"{a['id']}-p{j+1:02d}"
   if key in BOUNDARIES:
    ks=split_ends(k,BOUNDARIES[key][0]);es=split_ends(e,BOUNDARIES[key][1]);assert len(ks)==len(es),(key,len(ks),len(es))
    units=[{'ko':x,'en':y,'twoLineReason':'Keep the complete semantic clause and paired translation; measured48px wrap may use two lines when a single line is insufficient.'}for x,y in zip(ks,es)]
    out['paragraphs'][key]={'semanticPairingReviewed':True,'basis':'Directly authored corresponding clause boundaries from complete locked KO/EN narration; unchanged final meaning and text verified.','captionUnits':units}
   else:out['paragraphs'][key]=prior['paragraphs'][key]
   if key=='05-p01':
    for unit in out['paragraphs'][key]['captionUnits']:
     if '오토 액셀러레이트는' in unit['ko']:
      unit['ko']=unit['ko'].replace('오토 액셀러레이트는','자동 액셀은');unit['emphasis']['ko']={'start':0,'end':5,'role':'term'}
   for lang,expected in [('ko',k),('en',e)]:
    got=''.join(u[lang]for u in out['paragraphs'][key]['captionUnits'])
    assert re.sub(r'\s+','',got)==re.sub(r'\s+','',expected),(key,lang)
 out['scriptInputs']=[{'path':p.relative_to(P.parents[1]).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [P/'script/clarity-v3/narration.ko.json',P/'script/clarity-v3/narration.en.json',P/'script/clarity-v3/narration.spoken-ko.json']]
 (OUT/'caption-units.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(len(out['paragraphs']),'complete bilingual paragraphs verified; no audio timing invented.')
if __name__=='__main__':main()
