"""Hand-authored concept/observation bridges, preserving all accepted explanations."""
from prepare import *
# after-scene, native candidate, concept, observable question, Korean, matching English.
ROWS={
 'M21':[
 ('017','car-reflection','Specular Reflection · 정반사','차체는 그대로, 반사 무늬는?', '앞에서 배운 반사를 실제 게임에서 확인해 볼게요.|자동차를 보는 방향에 따라 밝은 무늬가 달라지죠.|이것이 반사 계산에 시선 방향도 필요한 이유입니다.', 'Let us check reflection in an actual game.|The bright patterns change as we view the car from another angle.|This is why a reflection model also needs the viewing direction.'),
 ('046','town-orbit','Shading · 표면 셰이딩','면의 밝기와 입체감', '표면 전체의 셰이딩을 실제 게임에서 보겠습니다.|탑을 둘러보면 벽의 밝기 차이로 곡면이 읽힙니다.|특정 공식을 단정하기보다, 방금 배운 표면 표현의 목적을 보세요.', 'Now observe surface shading in an actual game.|Differences in wall brightness reveal the curved tower as the camera moves.|Observe the purpose of shading; this recording does not establish a particular formula.'),
 ('059','doom-light','Projected Light · 투영 조명','손전등이 비추는 영역', '이번에는 광원의 모양을 실제 게임에서 확인해 볼게요.|둠 쓰리에서 손전등을 돌리면 밝은 영역도 벽을 따라 옮겨 갑니다.|이제 이 무늬를 만드는 방법으로 이어가겠습니다.', 'Now look at the visible footprint of a light in a game.|In Doom 3, turning the flashlight moves the bright region across the walls.|Next we will examine a way of producing that pattern.'),],
 'M22':[
 ('014','mario-water','Skinning · 스키닝','몸 전체의 이동과 관절의 굽힘', '큰 형태의 변화를 실제 게임에서 볼까요?|마리오가 헤엄칠 때 몸은 이동하고 팔과 다리는 따로 굽습니다.|방금 나눈 전체 변환과 관절 변형을 구별해 보세요.', 'Let us look at large-scale deformation in an actual game.|Mario moves through the water while his arms and legs bend separately.|Distinguish whole-body movement from the joint deformation we just discussed.'),
 ('034','doom-light','Normal Mapping · 노멀 매핑','외곽선과 표면의 요철', '작은 요철은 실제 게임에서 어떻게 보일까요?|둠 쓰리의 금속 벽을 비추면 표면의 굴곡이 빛에 드러납니다.|큰 외곽 형태와 작은 빛 반응을 나누어 보세요.', 'How do small surface details appear in an actual game?|Illuminating the metal walls in Doom 3 reveals fine surface relief.|Separate the large silhouette from small changes in the lighting response.'),],
 'M23':[
 ('008','town-build','Rendered Frame · 완성된 프레임','입력이 새 화면으로', '지금까지의 흐름을 실제 게임에서 보겠습니다.|건물을 더하거나 카메라를 돌리면 다음 화면이 달라집니다.|여러 계산의 결과가 하나의 완성된 프레임으로 보이는 겁니다.', 'Let us observe the result in an actual game.|Adding buildings or turning the camera changes the next image.|The output of many calculations appears as one completed frame.'),
 ('027','portal-occlude','Visibility · 가시성','가까운 벽이 가리는 부분', '가려짐을 실제 게임에서 확인해 볼게요.|포털에서 시점을 옮기면 가까운 벽 뒤의 공간이 드러나거나 가려집니다.|방금 설명한 깊이 판단이 해결하는 문제를 보세요.', 'Let us check visibility in an actual game.|Moving the viewpoint in Portal reveals or hides space behind nearby walls.|Observe the problem that depth testing is designed to solve.'),
 ('049','mario-water','Animated Surface · 변형된 표면','움직이는 몸 위의 표면', '표면 계산이 움직임과 만나는 모습을 보겠습니다.|헤엄치는 마리오의 팔과 몸은 형태가 바뀌어도 표면 표현을 유지하죠.|우리 예제에서는 변형된 위치와 법선으로 이 계산을 연결했습니다.', 'Now observe surface appearance together with motion.|Mario retains his surface appearance while his arms and body deform as he swims.|In our implementation, transformed positions and normals connect these stages.'),],
 'M24':[
 ('014','mario-run','Displacement · 변위','움직인 길과 두 끝점', '평균속도와 속력의 차이를 실제 게임에서 볼게요.|마리오가 방 안에서 방향을 바꾸며 달립니다.|두 끝점의 차이와, 실제로 지나온 길을 따로 생각해 보세요.', 'Let us distinguish average velocity from speed in an actual game.|Mario runs through the room, changing direction.|Consider the difference between the two endpoints separately from the path he traveled.'),
 ('028','car-speed','Instantaneous Rate · 순간 변화율','계속 달라지는 속도계', '순간 변화율을 실제 게임에서도 확인해 보겠습니다.|차가 달리는 동안 속도계의 숫자가 계속 바뀌죠.|전체 구간의 평균과 지금 이 순간의 상태가 다르다는 뜻입니다.', 'Let us observe an instantaneous rate in an actual game.|The speedometer changes while the car moves.|The average over the whole interval differs from the state at the present moment.'),
],
 'M25':[
 ('005','kart-start','Acceleration · 가속도','멈춤에서 출발로', '가속도를 실제 게임에서 확인해 볼게요.|출발 신호 뒤에 카트가 정지 상태에서 움직이기 시작합니다.|움직인 거리보다 먼저, 속도가 달라지는 과정에 주목하세요.', 'Let us observe acceleration in an actual game.|After the starting signal, the kart begins moving from rest.|Focus first on how its velocity changes rather than just the distance traveled.'),
 ('017','mario-jump','Projectile Motion · 포물선 운동','같은 순간의 가로와 세로', '두 방향을 함께 보려면 실제 점프가 좋습니다.|마리오는 앞으로 가면서 동시에 위로 올랐다 내려옵니다.|발판에 닿으려면 같은 순간에 가로와 세로가 모두 맞아야 하죠.', 'An actual jump helps us examine both directions together.|Mario moves forward while rising and then falling.|To reach a platform, both horizontal and vertical positions must agree at the same time.'),
 ('030','car-land','Integration · 적분','변화가 쌓여 다음 위치로', '적분의 관점으로 실제 움직임을 다시 보겠습니다.|차가 전진하는 동안 매 순간의 이동이 쌓여 다음 위치가 됩니다.|이 장면에 공식을 측정한 것은 아니고, 누적이라는 뜻을 연결하는 겁니다.', 'Let us view actual motion through the idea of integration.|Successive small movements accumulate as the car advances.|We are connecting the meaning of accumulation, not measuring this game with our formula.'),],
 'M26':[
 ('010','kart-turn','Centripetal Acceleration · 구심가속도','방향이 바뀌는 코너', '방향이 바뀌는 가속도를 실제 게임에서 보겠습니다.|카트가 코너를 도는 동안 앞으로 향하는 방향도 계속 꺾입니다.|속력의 변화와 방향의 변화를 구별해 보세요.', 'Let us observe acceleration associated with changing direction.|As the kart rounds a corner, its forward direction keeps turning.|Distinguish a change in speed from a change in direction.'),
 ('015','rotor','Angular Velocity · 각속도','같은 회전, 다른 반지름', '회전하는 물체에서도 확인해 볼게요.|같은 날개에서 중심에 가까운 점과 끝점을 함께 보세요.|같은 각도를 돌아도 바깥쪽 점이 더 긴 길을 지나갑니다.', 'Let us check a rotating object in an actual game.|Watch a point near the hub and a point at the tip of the same blade.|For the same angular change, the outer point travels farther.'),
],
 'M27':[
 ('011','cannon','Action and Reaction · 작용과 반작용','포탄과 발사 장치', '힘을 받는 대상을 실제 게임에서 나누어 볼게요.|포탄이 나가는 순간 발사 장치에도 움직임이 생깁니다.|서로 다른 물체에 작용하는 힘을 한 물체의 힘처럼 지우면 안 됩니다.', 'Let us separate the objects in an actual game.|The launcher also moves as its projectile is fired.|Forces acting on different objects must not be canceled as if they act on one object.'),
 ('017','mario-jump','Gravity · 중력','공중에서 오르고 내려오기', '중력의 역할은 실제 점프로 확인해 보겠습니다.|발판을 떠난 마리오는 위로 가다가 아래로 돌아옵니다.|화면의 움직임과, 우리가 만든 중력 모형을 연결해 보세요.', 'Let us observe the role of gravity in an actual jump.|After leaving the platform, Mario rises and then returns downward.|Connect the visible movement with the gravity model we constructed.'),
 ('030','beam-climb','Contact and Friction · 접촉과 마찰','타이어와 바위의 접촉', '마찰은 실제 게임에서 이동을 돕기도 합니다.|바퀴가 바위에 닿은 채 차를 밀어 올리는 모습을 보세요.|접촉을 통해 힘을 전달한다는 뜻을 떠올리면 됩니다.', 'Friction can also help movement in an actual game.|Watch the wheels push the vehicle up while touching the rocks.|Recall that contact allows forces to be transmitted.'),],
 'M28':[
 ('003','chomp','Restoring Force · 복원력','당기기와 놓기', '복원력을 실제 게임의 동작에 연결해 볼게요.|묶인 멍멍이를 당겼다가 놓으면 반대쪽으로 튀어나갑니다.|게임의 정확한 식이 아니라, 변형과 되돌아가는 움직임을 보세요.', 'Let us connect restoring force to a visible game action.|Pulling and releasing the tethered Chain Chomp sends it back the other way.|Observe displacement and return; this is not a claim about the game’s exact formula.'),
 ('015','suspension','Damping · 감쇠','충격 뒤의 차체 흔들림', '감쇠는 실제 게임의 서스펜션으로 보겠습니다.|요철을 지난 뒤 바퀴와 차체의 흔들림이 변하는 모습을 보세요.|움직임을 만드는 탄성과 흔들림을 줄이는 역할을 구별하면 됩니다.', 'Let us observe damping through a game suspension.|Watch how the wheels and body respond after crossing uneven ground.|Distinguish the elastic response from the role of reducing oscillation.'),
 ('023','rider-follow','Target Following · 목표 추종','캐릭터와 따라오는 시점', '목표를 따라가는 움직임도 실제 게임에서 볼까요?|라이더가 움직일 때 카메라도 그 뒤를 따라 위치를 바꿉니다.|방금 만든 추종 모형이 해결하려는 화면의 문제입니다.', 'Let us also observe target following in an actual game.|As the rider moves, the camera changes position to follow behind.|This is the visible problem our following model is intended to address.'),],
 'M29':[
 ('007','crash-impact','Impulse · 충격량','충돌 전후의 움직임', '짧은 충격은 실제 게임에서 확인해 보겠습니다.|차가 부딪히는 순간 전후의 움직임을 비교해 보세요.|힘이 작용한 시간 동안 운동량이 달라진다는 뜻으로 읽으면 됩니다.', 'Let us observe a short impact in an actual game.|Compare the car’s movement immediately before and after the collision.|Interpret this as a change in momentum during the interval of applied force.'),
 ('017','besiege-impact','Momentum · 운동량','발사체와 맞은 대상', '이번에는 여러 물체를 함께 보겠습니다.|발사체가 날아가 대상을 맞히면 양쪽의 움직임을 살펴보세요.|한 물체만 보는 대신, 무엇을 같은 계로 묶을지 정하는 연습입니다.', 'Now watch more than one object together.|Observe both the projectile and the target when they interact.|Practice deciding which objects belong to the system rather than examining just one.'),
 ('020','mario-contact','Collision Response · 충돌 반응','접촉과 그 뒤의 결과', '충돌 판정과 반응도 실제 게임에서 나누어 볼게요.|조종한 멍멍이가 바위에 부딪히자 바위가 부서집니다.|닿았는지 찾는 일과 결과를 만드는 일은 별개입니다.', 'Let us distinguish collision detection from response in an actual game.|The controlled Chain Chomp hits the rock, which then breaks.|Finding contact and deciding its consequence are separate tasks.'),],
 'M30':[
 ('013','cannon','Torque · 토크','밀림과 회전을 동시에', '힘의 회전 효과를 실제 게임에서 보겠습니다.|발사 장치는 뒤로 밀리면서 기울기도 달라집니다.|질량중심의 이동과 몸체의 회전을 나누어 보세요.', 'Let us observe the rotational effect of force in an actual game.|The launcher recoils while its orientation also changes.|Separate translation of the center of mass from rotation of the body.'),
 ('022','crash-impact','Rigid-Body Collision · 강체 충돌','충돌 위치와 회전 변화', '접촉점이 중요한 이유를 실제 게임에서 볼게요.|차가 충돌한 뒤 밀려나는 방향과 돌아가는 모습을 함께 보세요.|충격량은 이동뿐 아니라 회전에도 영향을 줄 수 있습니다.', 'Let us observe why the contact point matters in a game.|Watch both the displacement and rotation following a vehicle collision.|An impulse can affect rotation as well as translation.'),
 ('033','beam-joints','Constraints · 구속 조건','연결되어 함께 움직이는 부품', '연결 조건도 실제 게임에서 확인해 보겠습니다.|요철을 넘을 때 바퀴와 차체는 따로 움직이면서도 연결되어 있습니다.|여러 부품의 관계를 유지하는 것이 구속 조건의 역할입니다.', 'Let us observe connection constraints in an actual game.|Wheels and body move separately over bumps while remaining connected.|A constraint maintains a relationship between components.'),],
 'M31':[
 ('011','train-curve','Parametric Path · 매개변수 경로','지나가는 길과 진행 속도', '경로와 속도를 실제 게임에서 나누어 보겠습니다.|열차가 굽은 선로를 따라 이동합니다.|선로의 모양과, 그 위를 얼마나 빨리 지나가는지는 서로 다른 질문입니다.', 'Let us distinguish a path from speed in an actual game.|A train moves along a curved railway.|The shape of the route and how quickly it is traversed are separate questions.'),
 ('026','maker-path','Path Design · 경로 설계','지나갈 위치를 먼저 정하기', '원하는 길을 정하는 문제를 실제 게임에서 볼게요.|마리오 메이커에서는 트랙의 모양을 편집할 수 있습니다.|통과할 위치를 고르는 일과, 그 사이를 잇는 모양을 정하는 일을 구별하세요.', 'Let us observe route design in an actual game.|Mario Maker allows the track shape to be edited.|Distinguish choosing locations from deciding how the route should connect them.'),
 ('033','rail-edit','Endpoint and Tangent · 끝점과 접선','어디에, 어느 방향으로 이을까?', '끝점과 방향의 조건을 실제 게임에 연결해 보겠습니다.|선로의 끝을 옮기면 연결되는 위치와 곡선의 모양이 함께 달라집니다.|방금 에르미트 곡선에 준 입력의 의미를 떠올려 보세요.', 'Let us connect endpoint and direction constraints to an actual game.|Moving a rail endpoint changes the connection and the visible curve.|Recall the meaning of the inputs we gave to our Hermite curve.'),],
 'M32':[
 ('016','maker-path','Curve Control · 곡선 제어','입력을 바꾸면 경로가 변한다', '곡선을 조절한다는 뜻을 실제 게임에서 볼까요?|트랙을 편집하면 물체가 지나갈 길의 모양이 달라집니다.|이 장면이 베지에 구현이라는 뜻은 아니고, 우리가 제어점을 쓰는 목적과 연결됩니다.', 'Let us observe what it means to control a curve.|Editing a track changes the visible route objects will follow.|This does not establish a Bézier implementation; it illustrates the purpose of control points.'),
 ('021','galaxy-flight','Tangent · 접선','곡선을 따라 달라지는 진행 방향', '접선의 의미는 실제 비행으로 확인해 보겠습니다.|마리오가 휘어진 길을 따라갈 때 진행 방향도 함께 바뀝니다.|경로의 현재 위치와 그 자리의 방향을 따로 보세요.', 'Let us observe the meaning of a tangent through actual flight.|Mario’s direction changes as he follows a curved route.|Distinguish the present position on a path from its local direction.'),
 ('028','rail-edit','Subcurve · 부분 곡선','긴 길에서 한 구간 고르기', '부분 곡선이 필요한 상황을 실제 게임에 연결해 볼게요.|긴 선로를 편집할 때도 지금 연결할 구간에 집중합니다.|우리 계산은 이미 만든 곡선의 일부를 모양 그대로 꺼내는 방법이었죠.', 'Let us connect subcurves to a practical game situation.|When editing a long railway, we focus on the section being connected.|Our calculation extracts part of an existing curve while preserving its shape.'),],
 'M33':[
 ('016','maker-corner','Continuity · 연속성','이어짐과 부드러움은 다르다', '연속성의 차이를 실제 게임에서 확인해 보겠습니다.|트랙의 모서리를 바꾸면 이어진 길도 다르게 꺾입니다.|위치가 연결된다는 말과 방향까지 부드럽다는 말을 나누어 보세요.', 'Let us observe the distinction behind continuity in an actual game.|Changing a track corner alters how the connected route turns.|Separate positional connection from a smooth continuation of direction.'),
 ('025','rail-local','Local Editing · 국소 편집','한 연결부를 바꾸기', '한 구간을 조절하는 상황도 실제 게임에서 보겠습니다.|선로를 이을 위치를 바꾸면 가까운 구간의 모양이 달라집니다.|우리 곡선에서는 매듭점의 접선을 조절해 이 자유도를 설계했죠.', 'Let us observe local editing in an actual game.|Changing a railway connection changes the nearby section’s shape.|In our curve, tangent controls at the knots provide this kind of design freedom.'),
 ('040','rail-train','Connected Path · 연결된 경로','여러 조각을 하나의 이동으로', '마지막으로 연결된 경로의 결과를 실제 게임에서 보겠습니다.|열차는 여러 굽이를 끊기지 않고 지나갑니다.|우리가 맞춘 위치와 방향 조건이 어떤 움직임을 목표로 했는지 떠올려 보세요.', 'Finally, observe the result of a connected path in an actual game.|The train passes through successive bends without a gap.|Recall the movement that our position and direction constraints were designed to achieve.'),],
}
def main():
 inv=read(HERE.parent/'revision-teaching-sync-20261115/inventory.json')['episodes']; masters=read(OLD/'delivery.json')['episodes']
 lookup={e['id']:e for e in inv}; sources=read(HERE/'sources.json'); out=[]
 for master in masters:
  e=lookup[master['id']]; scenes={s['scene']:s for s in e['scenes']}; inserts=[]
  for n,(after,candidate,concept,question,ko,en) in enumerate(ROWS[e['id']],1):
   key=f"{e['id']}-{n:02}";src,a,z=CANDIDATES[candidate]
   inserts.append(dict(key=key,afterScene=after,atFrame=round(scenes[after]['end']*60),previousSpeech=scenes[after]['speech'],followingSpeech=next((s['speech'] for s in e['scenes'] if s['scene']==f'{int(after)+1:03}'),''),candidate=candidate,source=src,sourceIn=a,sourceOut=z,concept=concept,question=question,ko=ko.split('|'),en=en.split('|'),sourceMotionRequired=True,loop=False,freezePadding=False,rate=1,gameFormulaClaim=False,review='pending-exact-range'))
  out.append(dict(id=e['id'],slug=e['slug'],title=master['title'],baselineFiles=master['files'],baselineFrames=master['frames'],inserts=inserts))
 if (HERE/'selections.json').exists():
  choices=read(HERE/'selections.json')
  for e in out:
   scene_lookup={x['scene']:x for x in lookup[e['id']]['scenes']}
   for s in e['inserts']:
    s.update(choices.get(s['key'],{}));after=s['afterScene'];s['atFrame']=round(scene_lookup[after]['end']*60);s['previousSpeech']=scene_lookup[after]['speech'];s['followingSpeech']=scene_lookup.get(f'{int(after)+1:03}',{}).get('speech','')
   e['retainedExistingCases']=[s for s in e['inserts'] if s.get('omitAsAdjacentDuplicate')]
   e['inserts']=sorted([s for s in e['inserts'] if not s.get('omitAsAdjacentDuplicate')],key=lambda s:s['atFrame'])
 save(HERE/'plan.json',dict(scope='M21–M33',status='planning-exact-source-review',acceptedExplanationPreserved=True,newTransitionNarrationOnly=True,originalAudioTempoChange=False,episodes=out))
 print(len(out),'episodes',sum(len(e['inserts']) for e in out),'post-concept observations')
if __name__=='__main__':main()
