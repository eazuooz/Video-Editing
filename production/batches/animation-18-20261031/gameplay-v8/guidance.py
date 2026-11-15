"""Narrate the long music-only observation slots without deleting existing teaching."""
from common import *

# Units pair Korean/English clauses. Synthesize each paragraph continuously;
# final clause captions are aligned to the actual readback before rendering.
TEXT={
0:[('검을 휘두르기 전, 발과 몸통의 자세를 먼저 보세요.','Before the swing, examine the feet and torso.')],
1:[('대기 자세에서 검을 들어 올리기 시작하는 순간을 보세요.','Watch the moment the sword begins to rise from the ready pose.')],
2:[('검이 닿는 순간, 힘이 향하는 방향을 보세요.','At contact, observe the direction of the force.')],
3:[('마무리 자세를 정리하는 움직임을 보세요.','Watch the body settle after the attack.'),('몸은 아직 멈추지 않습니다.','The body is still moving.')],
4:[('도끼를 든 손이 먼저 크게 움직입니다.','The hand holding the axe makes the first large movement.'),('몸통도 함께 방향을 바꾸죠.','The torso changes direction with it.'),('큰 무기를 들어 올리는 준비를 보여 준 뒤, 공격으로 빠르게 넘어갑니다.','The raised weapon makes the preparation readable before the rapid attack.')],
5:[('피치가 칼을 뻗는 순간, 어깨와 허리도 함께 돌아갑니다.','As Peach extends the sword, her shoulders and waist turn together.'),('팔과 몸이 같은 방향을 만들 때 공격의 힘이 더 분명해집니다.','The arm and body make the direction of the attack clearer.')],
6:[('같은 칼 동작을 작은 화면에서도 보세요.','Observe the same sword action at a small screen size.'),('손끝만 움직이면 경로는 남아도, 몸에 실린 힘은 잘 읽히지 않습니다.','Moving only the hand can show a path while losing the force carried by the body.'),('준비할 때 몸을 모으고, 칼을 보낸 뒤 다시 버티는 흐름까지 보여 주면 동작의 의도가 남습니다.','Gathering the body, sending the sword out, and settling afterward preserve the intent of the action.')],
7:[('몸통이 기울어질 때 머리와 두 팔의 관계를 보세요.','As the torso leans, examine its relationship with the head and arms.'),('한 줄로 곧게 선 상태와 달리, 몸 전체에 방향이 생깁니다.','The body gains a direction that a perfectly upright pose lacks.')],
8:[('접힌 다리와 뻗은 다리를 보세요.','Observe the folded leg and the extended leg.'),('같은 두 자세라도 중간에 쓰는 시간이 달라지면 리듬이 달라집니다.','The same two poses produce a different rhythm when the time between them changes.')],
9:[('손이 나간 길과 돌아오는 길을 따로 보세요.','Examine the outgoing path and the returning path separately.'),('어깨와 몸통이 풀리면 손의 경로도 달라집니다.','As the shoulders and torso settle, the path of the hand changes.'),('타격 구간과 몸을 정리하는 구간을 나누면, 동작이 끝나는 느낌까지 읽을 수 있습니다.','Separating the strike from the settling motion makes the ending of the action readable.'),('같은 시작점으로 돌아와도, 돌아오는 과정은 따로 설계할 수 있습니다.','Even when returning to the same starting point, the return path can be designed separately.')],
10:[('동물의 숲 캐릭터 얼굴을 크게 본 뒤, 같은 순간을 작게 보겠습니다.','Compare a large and small view of the same moment in Animal Crossing.'),('눈과 입의 작은 변화 가운데, 실제 플레이 크기에서도 읽히는 것이 무엇인지 확인해 보세요.','Check which small changes in the eyes and mouth remain readable at gameplay size.')],
11:[('눈과 눈썹, 입이 함께 달라질 때 표정도 달라집니다.','The expression changes as the eyes, eyebrows, and mouth change together.')],
12:[('디제이가 오른쪽을 볼 때와 왼쪽을 볼 때를 나란히 보세요.','Compare Dee Jay facing right and facing left.'),('얼굴과 앞쪽 주먹이 어느 쪽에 남는지, 발은 어떤 순서로 놓이는지 비교합니다.','Compare the visibility of the face and leading fist, and the ordering of the feet.'),('캐릭터를 돌리는 일과 포즈를 반전하는 일이 왜 다른지도 여기서 출발합니다.','This provides a starting point for distinguishing turning a character from mirroring a pose.')],
13:[('이전 동작이 끝난 몸에서 다음 동작이 바로 시작되면, 팔과 몸통이 갑자기 튈 수 있습니다.','An immediate switch from the previous action can make the arms and torso jump.'),('원리 그림에서는 두 자세를 잠깐 섞어 이 변화를 이어 줍니다.','The principle diagram briefly blends the two poses to connect the change.'),('이전 자세가 무엇이었는지도 함께 남는다는 점을 보세요.','Notice that the previous pose still contributes during the transition.')],
14:[('손을 어디로 옮길지 정하는 방법과, 어깨부터 돌려 손을 움직이는 방법을 나누어 보겠습니다.','Distinguish setting a hand target from moving the hand by rotating from the shoulder.'),('같은 손 위치에 도착하더라도, 중간 관절이 정해지는 과정은 다릅니다.','Even with the same hand destination, the intermediate joints can be determined differently.'),('그림의 화살표 방향을 따라가 보세요.','Follow the direction of the arrows in the diagram.')],
15:[('발이 닿을 목표를 먼저 정하고, 다리가 그곳에 맞게 따라오게 할 수도 있습니다.','A foot target can also be set first, letting the leg adapt to reach it.')]
}

def prepare():
 survey=read(HERE/'guidance-gap-survey.json')['records'];records=[];scenes=[]
 for i,g in enumerate(survey):
  ep=g['id'];m=read(WORK/ep/'audio.json');identity=f'{ep}-guidance-{i:02}'
  assert not m.get('guidanceCount'), 'Guidance clock is already frozen; do not reconvert the original survey after inserting it.'
  lo=old_frame(round(g['start']*60),m['changes'])/60;hi=old_frame(round(g['end']*60),m['changes'])/60
  units=[dict(ko=ko,en=en) for ko,en in TEXT[i]]
  for unit in units:wrap_caption(unit['ko']);wrap_caption(unit['en'])
  records.append(dict(id=identity,episode=ep,captionIndex=None,kind='music-only-observation-guidance',start=lo,end=hi,
   ko=' '.join(u['ko'] for u in units),en=' '.join(u['en'] for u in units),units=units,key=g['key'],
   audioFile=str(HERE/'local/guidance-voice/chunks'/(identity+'-scene.wav')),
   reason='Explain the target/action/result during an existing long observation slot. Preserve every original spoken clause, overview and recap.',
   gapEvidence=g))
  scenes.append(dict(id=identity,title=ep+' 관찰 안내',lines=[' '.join(u['ko'] for u in units)]))
 save(HERE/'guidance-changes.json',dict(records=records,originalSpeechRemoved=False,sourceOrderPreserved=True))
 save(HERE/'local/guidance-script.json',dict(scenes=scenes))
 m=read(HERE/'tts-manifest.json');m['paths']['script']=(HERE/'local/guidance-script.json').relative_to(ROOT).as_posix()
 m['tts'].update(outputDir=(HERE/'local/guidance-voice').relative_to(ROOT).as_posix(),filenameStem='observation-guidance',maxNewTokens=1024)
 save(HERE/'guidance-manifest.json',m);print('Prepared16 guided observations; original speech retained.')

if __name__=='__main__':prepare()
