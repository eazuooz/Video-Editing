"""Editable independent KO/EN cue phrasing, preserving all fifteen paragraph texts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));norm=lambda s:re.sub(r'[^가-힣a-zA-Z0-9]','',s).lower()
out=R/'current17-caption-editorial-groups-v1.json';assert not out.exists()
# These are corresponding editorial units, not recognition prompts.
groups={
'07b':[
(1,'퍼즐에서 방향을 읽는 문제를 포털 투로 이어 보겠습니다.','Let us extend the puzzle-orientation question to Portal2.'),
(1,'큐브로 레이저를 장치에 보내거나, 큐브를 발판 위에 놓습니다.','A cube directs a laser toward a device, or is placed on a floor button.'),
(2,'먼저 큐브와 벽의 장치를 찾으세요.','First locate the cube and the wall device.'),
(2,'시점을 돌리면 둘의 화면 위치가 바뀝니다.','Turning the view changes their screen positions.'),
(2,'빨간 표시는 조작할 큐브,','Red marks the manipulated cube;'),
(2,'파란 표시는 방의 단서입니다.','blue marks a room landmark.'),
(3,'큐브를 들고 방향을 바꾸면 큐브도 화면 가운데를 따라갑니다.','When the player turns while holding the cube, it stays near the center of the view.'),
(3,'앞의 에임 모드에서 도구만 따로 움직이던 장면과 비교해 보세요.','Compare this with Aim Mode, where the tool moved separately within the screen.'),
(4,'다른 구간에서는 레이저를 장치로 보냅니다.','A separate interval directs the laser at the device.'),
(4,'또 다른 구간에서 큐브를 발판에 놓자','In another interval, placing the cube on the button'),
(4,'이어진 표시가 파란색에서 노란색으로 바뀝니다.','changes the connected indicator from blue to yellow.'),
(5,'목표를 조작하려면 보는 방향을 바꿔야 할 때도 있습니다.','Manipulating a target can require changing the viewing direction.'),
(5,'바뀐 뒤 장치와 바닥의 단서로 목표를 다시 찾을 수 있어야 하죠.','The device and floor landmarks must help the player find that target again afterward.'),
(6,'이 비교는 조작과 시야의 연결을 보여 줍니다.','This comparison illustrates the relationship between manipulation and viewing.'),
(6,'포털 이동이나 개인의 편안함을 검사한 결과는 아닙니다.','It does not test portal travel or individual comfort.')],
'08b':[
(1,'전환 뒤 방향을 읽는 질문을','Let us carry the orientation-after-transition question'),
(1,'가상현실 게임 하프라이프 알릭스로 이어 보겠습니다.','into the VR game Half-Life:Alyx.'),
(1,'이 시연에서는 이동할 곳을 가리킨 뒤 그곳으로 옮깁니다.','This demonstration points to a destination before moving there.'),
(2,'노란 곡선과 발자국 표시가 목적지입니다.','The yellow curve and footprints mark that destination.'),
(2,'선택 뒤 시점이 문 가까이 바뀌면,','After the viewpoint changes to a position near the door,'),
(2,'문과 벽을 보고 도착한 방향을 다시 읽으세요.','use the door and wall to read the arrival direction.'),
(3,'이어지는 구간에서는 길을 막은 판자를 손으로 잡아 치웁니다.','In the following interval, hands grip and remove boards blocking the path.'),
(3,'목적지를 고르는 일과,','Choosing a destination differs from'),
(3,'도착해서 손으로 물체를 다루는 일은 다릅니다.','manipulating an object by hand after arriving.'),
(4,'청소 도구와 큐브, 손의 조작은 서로 다르지만,','A cleaning tool, a cube and hands have different controls.'),
(4,'작업 대상과 주변 단서를 함께 보여 준다는 질문은 같습니다.','They share the question of showing the work target together with surrounding landmarks.'),
(5,'이동 방식 하나만으로 모두의 편안함을 판단할 수는 없습니다.','One movement method cannot establish comfort for everyone.'),
(5,'이동 전후 방향을 이해하는지와 개인의 반응을 따로 확인해야 합니다.','Understanding orientation before and after movement and individual responses need separate checks.')],
'11b':[
(1,'네 게임을 같은 세 질문으로 정리해 보겠습니다.','Summarize the four games with the same three questions:'),
(1,'무엇을 조작하고,','What is manipulated,'),
(1,'화면의 무엇이 움직이며,','what moves on the screen,'),
(1,'움직인 뒤 어떤 단서가 남을까요?','and which cues remain afterward?'),
(2,'청소에서는 물줄기와 표면,','We examined water and surfaces in cleaning,'),
(2,'탈로스에서는 벽과 바닥,','walls and floors in Talos,'),
(2,'포털에서는 큐브와 장치,','cubes and devices in Portal,'),
(2,'알릭스에서는 목적지와 손의 작업을 살펴봤습니다.','and destinations and hand tasks in Alyx.'),
(3,'게임마다 필요한 움직임은 다릅니다.','The required movement differs between games.'),
(3,'한 게임의 조작법을 정답으로 옮기기보다,','Instead of treating one control scheme as the answer everywhere,'),
(3,'작업을 유지하면서 따로 조절할 역할을 찾으세요.','find responsibilities that can be adjusted separately while retaining the task.'),
(4,'그 역할을 알아볼 수 있게 설명하고 되돌릴 수 있게 만드는 일이,','Explaining those responsibilities clearly and letting players restore their choices'),
(4,'앞에서 본 카메라 옵션의 설계로 연결됩니다.','connects back to the camera-option design we examined.')]
}
ko={s['id']:s['lines'] for s in read(R/'script/additions.ko.json')['scenes']}
en={s['id']:s['lines'] for s in read(R/'script/additions.en.json')['scenes']}
rows=[]
for sid,units in groups.items():
 for i,(kt,et) in enumerate(zip(ko[sid],en[sid]),1):
  selected=[v for v in units if v[0]==i]
  assert norm(''.join(v[1] for v in selected))==norm(kt),(sid,i,'KO changed')
  assert norm(''.join(v[2] for v in selected))==norm(et),(sid,i,'EN changed')
 for i,(paragraph,kt,et) in enumerate(units,1):rows.append(dict(id=f'{sid}-cue-{i:02d}',scene=sid,paragraph=paragraph,ko=kt,en=et,currentTimingAssigned=False))
out.write_text(json.dumps(dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),groups=rows,newCueCount=len(rows),retainedCueCount=179,all15OriginalKoEnParagraphTextsPreserved=True,currentMixedTimingApproved=False,currentPixelsApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedNewCuePhrases=len(rows),original15KoEnTextsPreserved=True,timingAssigned=False)))
