# 두 편 구성과 도입 검토

- 01 explanation: 거리와 두 각도로 3D 위치 표현하기
- 02 actual: 실제 관찰 · 높이와 시점의 변화
- 03 explanation: 원통좌표는 평면 극좌표에 높이를 더합니다
- 04 explanation: 원통좌표 변환은 2D 공식을 그대로 씁니다
- 05 actual: 실제 관찰 · 수평 이동과 점프를 구분하기
- 06 explanation: 구면좌표는 거리와 두 각도를 사용합니다
- 07 explanation: 게임 각도는 축의 약속부터 확인합니다
- 08 actual: 실제 관찰 · 화면의 기울기와 방향은 다릅니다
- 09 explanation: 헤딩·피치에서 x, y, z로 변환하기
- 10 explanation: 역변환은 수평 길이부터 구합니다
- 11 actual: 실제 관찰 · 위치를 보고 시점 관계 생각하기
- 12 explanation: 구면좌표에도 같은 점의 여러 주소가 있습니다
- 13 explanation: 극점에서는 헤딩이 정해지지 않습니다
- 14 actual: 실제 관찰 · 위아래 방향과 조작 정책
- 15 explanation: 카메라 위치와 보는 방향을 구분하세요
- 16 actual: 실제 관찰 · 대상에서 카메라로, 카메라에서 대상으로
- 17 explanation: 벡터 연산과 작은 수치 오차까지 확인합니다
- 18 actual: 실제 관찰 · 좌표 하나가 모든 동작은 아닙니다
- 19 explanation: 직접 확인할 세 가지 기준 방향

도입: 핵심 질문·시청 후 얻는 점·실제 순서를 독립 한영4문장으로 작성하고 TTS 전에 본론과 대조했다. 실제 사례40%, 설명60%; 실측 음성을 보존하며 필요한 실제 컷을 확보한다. 반복·느린 재생으로 비중을 채우지 않는다.

## 2026-10-10 공개 전 이해도 수정

원래25.2초 도입과19씬 설명 순서·승인PCM·한영206큐·화이트 설명은 보존했다. 같은 자전거 사례에서 높이와 수평 성분을 나눈 뒤, 방향/자세/카메라를 구별하고 실제 화면 위 색 선과 짧은 라벨로 계산의 의미를 짚는다. 다른 주행 발췌로 바뀌는 지점은 원래 해설과 별도 표시로 구분한다. 화면의 모델 값과 투영 관계를 게임 엔진의 실측 좌표로 주장하지 않는다.

- 01: 2D addresses lack height → Introduce cylinder, sphere and camera; state scope and boundary checks
- 02: Observe track position/air height/following view → Separate target and view point before formulas; improve mismatched landing footage
- 03: Need a third component → Build horizontal polar address plus z height; distinguish horizontal from total distance
- 04: How to calculate the address → Reuse part1 trig and apply5,0,3; recover horizontal radius/angle
- 05: Do formulas describe visible jumps → Relate horizontal projection to height and distinguish terrain clearance from world height
- 06: Want total distance with two direction angles → Construct sphere from z-up mathematical convention; explain zenith, latitude and altitude
- 07: How do game direction names correspond → Explicit switch to x-right/y-up/z-forward and positive-pitch-down; separate roll
- 08: Can a direction explain every bike rotation → Observe attitude, travel and camera projection as separate quantities
- 09: Need a usable game-convention conversion → Split into horizontal/vertical components, then heading; checkforward/right signs
- 10: Recover distance and angles from coordinates → Usehypot/atan2; treatorigin/pole without claiming camera policy
- 11: How to connect relative camera geometry → Observe target/viewpoint; subtract target position before inverse conversion
- 12: Why different angle values can describe one point → Show aliases and verify via Cartesian coordinates
- 13: Need one stored representative → Choose canonical ranges; distinguish pole singularity, attitude gimbal lock and camera policy
- 14: Do storage conventions make motion smooth → Observe ramps; motivate separate smoothing and pitch policies without inferring engine internals
- 15: Construct camera placement explicitly → Useonecenter(0,1,0) example; reverse subtraction for look vector
- 16: What opposite vectors mean in action → Track the rider and distinguish placement/look relationships, update center and check occlusion
- 17: What survives implementation → AddCartesian vectors; handle arcsine input/rounding/axis units
- 18: What these coordinates can and cannot control → Separate position, attitude, collisions and camera behavior
- 19: How to validate the learned convention → Checkthree radius2 directions, origin/pole policy; return to viewer question

새 도형은02/05/08/11/14/16/18의 독립 편집 계획에 유지한다. 첫 시청자 후보 비교,44완결음성문맥,현재 모든 자막/컷/도형 표본과 정상1배속 전체 재생의 근거는 revision-teaching-clarity-v1에 있다. 현재 본편실제21358/설명32037은 사용자 강의40:60 예외이며, 원본고양이120/회원600은 제외한다. 사람 청취·발음·공개권리는 계속 미완료다. 새 비공개 설정/Git/예약은 별도 실제 증거가 필요하다.
