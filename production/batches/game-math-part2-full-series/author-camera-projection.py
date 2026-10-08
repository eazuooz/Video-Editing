"""Full10.3 with one consistent point, after actual source and overlap review."""
from pathlib import Path
import json
B=Path(__file__).parent;slug='game-math-camera-projection';scenes=[]
P='yFRbGppLaUI';T='FRfnXAIbA-M'
def E(i,title,mode,rows):
 assert all(len(x)==4 for x in rows)
 scenes.append(dict(id=f'{i:02}',title=title,kind='explanation',mode=mode,ko=[x[0] for x in rows],en=[x[1] for x in rows],beats=[x[2] for x in rows],formulas=[x[3] for x in rows]))
def A(i,title,source,start,end,rows,focus,claim):
 assert all(len(x)==2 for x in rows)
 scenes.append(dict(id=f'{i:02}',title=title,kind='actual',sourceId=source,sourceSegments=[{'in':start,'maxSeconds':end-start}],**{'in':start},maxSeconds=end-start,ko=[x[0] for x in rows],en=[x[1] for x in rows],focus=focus,claim=claim))
E(1,'한 점이 픽셀이 될 때까지','overview',[
 ('게임 속 건물의 한 꼭짓점은 어떻게 화면의 특정 위치에 그려질까요?','How does one corner of a game building end up at a specific screen position?','한3D점 → 화면의 어디?','로컬 → 월드 → 뷰 → 클립 → 픽셀'),
 ('먼저 실제 게임의 기준점을 따라가며, 한 점의 좌표를 물체 기준에서 카메라 기준까지 계산하겠습니다.','First we follow landmarks in real games and calculate one point from object coordinates to camera coordinates.','실제 기준점 → 공간 변환','같은 점 / 달라지는 기준'),
 ('이어서 시야 밖을 자르고, 나눗셈과 출력 창 변환으로 최종 화면 좌표를 구합니다.','Next we clip the viewing volume, divide, and map through an output rectangle to obtain the screen coordinates.','클리핑 → 나눗셈 → 출력 창','마지막 좌표를 직접 검산'),
 ('마지막에는 깊이와, 텍스처 값을 원근에 맞춰 이어 주는 보간을 살펴봅니다. 어느 단계에서 오류가 났는지 찾는 방법까지 정리하겠습니다.','Finally, we examine depth and perspective-correct interpolation of texture values, then organize a method for locating the stage responsible for a rendering error.','깊이·보간 → 단계별 검사','중간 값을 남기면 원인을 찾기 쉽다')])
A(2,'기둥은 그대로인데 화면 위치는 바뀝니다',P,16,40,[
 ('포털 투의 공식 플레이 장면입니다. 이동하는 시점과 화면 가운데의 기둥을 함께 따라가 보세요.','This is official Portal2 gameplay. Follow both the moving viewpoint and the central pillar.'),
 ('기둥을 옮기지 않아도 보이는 위치가 바뀌고, 뒤의 장치가 기둥에 가려집니다.','The pillar changes screen position without moving, while a device behind it becomes hidden.'),
 ('이 차이를 계산하려면 같은 점을 세계 기준과 카메라 기준에서 따로 적어야 합니다.','To calculate that difference, express the same point in world coordinates and camera coordinates.')],
 '실제1인칭 이동과 고정된 기둥·뒤의 장치','세계의 점과 카메라에서 읽는 좌표는 다르다; 게임 내부 좌표는 추정하지 않는다')
E(3,'계산 전에 네 가지 약속부터','conventions',[
 ('행렬 이름만 같다고 식을 그대로 옮기면 안 됩니다. 오늘은 왼손 좌표계에서 카메라 앞쪽을 플러스 제트로 정합니다.','Matching matrix names do not guarantee matching formulas. Today we use left-handed view coordinates with forward plusz.','앞쪽+z / 오른쪽+x / 위+y','LH / +z forward'),
 ('벡터는 가로로 적는 행벡터이고, 행렬은 벡터 오른쪽에 곱합니다. 이전 회전 강의의 열벡터 약속과 구분하세요.','Vectors are rows with matrices multiplied on the right; distinguish this from the earlier rotation lesson’s column convention.','행벡터 / 오른쪽에 행렬','p_world = p_local M'),
 ('클립 깊이는 영부터 더블유까지이고, 나눈 뒤 깊이는 영부터 일까지입니다. 두 단계의 범위를 섞지 않습니다.','Clip depth runs from0 tow; after division depth runs from0 to1. Keep the stages distinct.','클립[0,w] / 나눈 뒤[0,1]','0 ≤ z_clip ≤ w'),
 ('화면 원점은 왼쪽 위이고 아래로 갈수록 와이가 커집니다. 카메라 공간의 위쪽 플러스 와이와 반대입니다.','The screen origin is top-left andy increases downward, opposite the camera’s upwardy.','화면 왼쪽 위 / 아래+y','뷰 위+y → 화면 아래+y'),
 ('공간과 벡터 방향, 깊이 범위와 화면 원점을 각각 기록하세요. 실제 엔진의 선택은 에이피아이 이름 하나로 단정할 수 없습니다.','Record space,vector convention,depth range and screen origin separately; an API name alone cannot settle them all.','네 약속을 각각 확인','공간 / 행·열 / 깊이 / 원점'),
 ('기존 강의에서 다룬 행렬 유도는 필요한 만큼만 떠올리고, 오늘은 한 점의 중간 값과 최종 결과를 끝까지 연결하겠습니다.','Recall the earlier matrix derivations as needed; this lesson connects every intermediate value of one point to its final result.','이전 유도 → 이번 완결 계산','한 점의 전체 변환 기록')])
E(4,'로컬 점을 세계에 배치하기','model',[
 ('작은 상자에 붙은 한 꼭짓점을 고르겠습니다. 상자 기준 좌표는 일, 영, 영입니다. 위치이므로 네 번째 성분 더블유는 일입니다.','Choose a corner of a small box at local coordinates(1,0,0); its position hasw1.','같은 꼭짓점 P / 로컬 기준','p_local = (1,0,0,1)'),
 ('상자를 세계의 삼, 이, 오만큼 이동합니다. 회전과 크기 변경은 없다고 정해 계산을 단순하게 시작합니다.','Translate the box by(3,2,5), with no rotation or scale in this first example.','모델 이동(3,2,5)','M = translate(3,2,5)'),
 ('좌표를 더하면 세계에서 꼭짓점은 사, 이, 오입니다. 상자의 로컬 좌표 일, 영, 영이 틀린 것이 아니라 기준이 달라진 것입니다.','Adding the translation gives world coordinates(4,2,5); the local coordinates remain valid in their own frame.','월드의 P=(4,2,5)','(1,0,0) + (3,2,5) = (4,2,5)'),
 ('행벡터 약속에서 이동은 행렬의 마지막 행에 놓습니다. 열벡터 행렬의 마지막 열과 모양을 혼동하지 마세요.','For our row vectors, translation occupies the last row, rather than the last column of a column-vector matrix.','이동 성분은 마지막 행','M 마지막 행: [3,2,5,1]'),
 ('반면 방향은 더블유가 영입니다. 일, 영, 영이라는 방향에 같은 이동 행렬을 곱해도 삼, 이, 오가 더해지지 않습니다.','A direction hasw0, so transforming direction(1,0,0) by the same translation does not add(3,2,5).','위치 w1 / 방향 w0','(1,0,0,0) M = (1,0,0,0)'),
 ('표면 법선도 방향이지만, 크기를 비균일하게 바꿀 때는 위치와 같은 식을 무조건 쓰지 않습니다. 법선 변환은 뒤의 조명 강의에서 다룹니다.','Normals are directions, but nonuniform scaling requires a separate normal transformation, covered in the lighting lesson.','법선은 별도 변환 확인','오늘은 이동만 / 법선 상세는 뒤에서')])
A(5,'새 건물과 기존 지붕을 구별하기',T,274,379,[
 ('타운스케이퍼의 앞쪽 지붕 모서리 하나를 기준점으로 골라 보세요. 작은 발판에 새 블록이 붙으며 건물의 형태가 바뀝니다.','Choose a front roof corner in Townscaper. New blocks grow from a platform and change the structure.'),
 ('이때 새로 만들어진 지붕의 꼭짓점과, 처음 고른 기존 꼭짓점을 구분해야 합니다. 다른 점을 비교하면 좌표 변환을 검증할 수 없습니다.','Distinguish newly created corners from the original landmark; comparing different points cannot verify one coordinate transformation.'),
 ('시점이 돌아가면 긴 지붕의 옆면과 안쪽 빈 공간이 드러납니다. 화면에서는 기존 모서리의 위치도 계속 달라집니다.','Orbiting reveals the long roof’s sides and interior opening, while the original corner keeps changing screen position.'),
 ('세계에 놓인 건물의 좌표와 관찰하는 카메라의 좌표가 따로 있다는 사실을 실제 장면으로 연결해 보세요.','Connect these visible changes to separate world placement and camera-relative coordinates.'),
 ('세계의 좌표를 기록하고 싶다면 물체를 기준으로 정한 점을 먼저 고르고, 모델 변환을 거친 값을 저장해야 합니다.','To record a world position, identify a point in the object’s frame and store the resulting world-space position after its model transform.'),
 ('카메라가 돌아갔다고 해서 모든 건물의 세계 좌표를 다시 작성할 필요는 없습니다. 관찰 기준으로 바꾸는 다음 단계가 있습니다.','Orbiting a camera does not require rewriting every building’s world coordinates; a later step changes the viewing frame.'),
 ('이 화면에서 실제 게임의 행렬 값을 읽어낸 것은 아닙니다. 우리가 정한 상자의 일, 영, 영과 이동값 삼, 이, 오는 별도의 계산 예제입니다.','These pixels do not reveal the game’s matrices. Our local point and translation are separately defined teaching values.'),
 ('건축으로 바뀐 부분과 시점 때문에 다르게 보이는 부분을 나누어 보는 습관이, 중간 좌표를 검사하는 첫걸음입니다.','Separating construction changes from viewpoint changes is the first habit for inspecting intermediate coordinates.')],
 '실제 블록 추가·기존 지붕·회전에 따른 새 면','모델 배치와 카메라 관찰을 구별하고 같은 점을 추적한다')
E(6,'카메라를 기준으로 다시 읽기','view',[
 ('카메라를 세계의 이, 일, 일에 놓겠습니다. 오른쪽, 위쪽, 앞쪽 방향은 세계 축과 같다고 정합니다.','Place the camera at(2,1,1), aligned with the world’s right,up and forward axes.','카메라 C 위치(2,1,1)','카메라 축 = 세계 축'),
 ('점의 세계 좌표 사, 이, 오에서 카메라 위치를 빼면 이, 일, 사입니다. 카메라 기준 오른쪽 이, 위쪽 일, 앞쪽 사에 있는 점입니다.','Subtracting the camera position from world point(4,2,5) gives view point(2,1,4): right2,up1,forward4.','뷰의 P=(2,1,4)','(4,2,5) − (2,1,1) = (2,1,4)'),
 ('카메라가 돌아가 있다면 위치를 빼는 것만으로 끝나지 않습니다. 빼서 얻은 벡터를 카메라의 오른쪽, 위쪽, 앞쪽 축으로 읽어야 합니다.','A rotated camera also requires expressing the displacement along its right,up and forward axes.','이동을 빼고 카메라 축으로 읽기','view 성분 = 변위·카메라 각 축'),
 ('그래서 뷰 행렬은 카메라를 세계에 놓는 변환의 역변환입니다. 카메라 자신의 위치를 넣었을 때 원점이 나오는지 확인해 보세요.','The view matrix is the inverse camera-to-world transform; check that it maps the camera’s own position to the origin.','V는 카메라 변환의 역','V = C⁻¹ / camera × V = origin'),
 ('회전 축이 정규직교이면 역회전은 전치로 구할 수 있습니다. 하지만 크기나 기울임을 섞은 일반 행렬까지 무조건 전치하지는 않습니다.','An orthonormal rotation can be inverted by transposing; this does not extend blindly to arbitrary scale or shear.','정규직교 회전에서만 전치','R⁻¹ = Rᵀ 조건 확인'),
 ('오늘 행벡터의 순서는 로컬 점에 모델, 뷰, 투영 행렬을 차례로 곱하는 것입니다. 열벡터로 바꾸면 곱의 표시 순서도 달라집니다.','For our rows, multiply the point by model,view and projection in that order; column-vector notation reverses the written product.','행벡터 순서 M → V → P','p_clip = p_local M V P')])
E(7,'행렬은 w를 준비하고 나눗셈은 나중에','homogeneous',[
 ('카메라 공간의 점은 이, 일, 사입니다. 가장 단순한 원근 준비 행렬은 원래 제트 사를 네 번째 성분 더블유에 복사합니다.','Our view point is(2,1,4). The simplest perspective preparation copies itsz4 into the fourth componentw.','z를 w로 복사','(2,1,4,1) → (2,1,4,4)'),
 ('아직 좌표를 사로 나누지 않았습니다. 지금은 네 숫자를 가진 클립 형태를 만들었을 뿐입니다.','No division by4 has occurred yet; this step only prepares a four-component clip representation.','곱하기와 나누기 분리','행렬 곱 → 아직 w 나눗셈 전'),
 ('나중에 사로 나누면 가로는 영 점 오, 세로는 영 점 이오, 깊이는 일이 됩니다. 하지만 이 단순한 행렬은 깊이 구간을 보존하는 완성 행렬이 아닙니다.','Dividing this simplified result gives(0.5,0.25,1), but this is not a complete near-to-far depth mapping.','단순 예제의 한계','단순 행렬: (0.5,0.25,1)'),
 ('완성된 행렬에서는 두 축의 줌과 가까운 평면, 먼 평면의 깊이까지 함께 준비합니다. 다음 계산에서 그 항을 채우겠습니다.','The complete matrix also prepares both zoom axes and near-to-far depth; we fill those terms next.','줌·깊이를 채운 완성 P','x·zx / y·zy / Az+B / w=z'),
 ('직교 투영은 더블유를 일로 유지합니다. 같은 나눗셈 단계를 통과하지만 일로 나누므로 거리 때문에 가로와 세로가 작아지지 않습니다.','Orthographic projection keepsw1, so the same division stage does not introduce distance-based shrinking.','직교는 w1','원근 w=z / 직교 w=1'),
 ('이 공통 표현은 비대칭 시야나 큰 이미지를 조각내어 렌더링할 때도 유용합니다. 왼쪽과 오른쪽 경계가 언제나 대칭일 필요는 없습니다.','The common representation also supports asymmetric views and tiled rendering; left and right bounds need not be symmetric.','대칭 아닌 시야도 표현','하나의 동차 좌표 틀'),
 ('더블유로 나누는 절차를 쓰는 이유는 모든 투영을 한 가지 숫자 약속으로 연결하기 위해서입니다. 별도의 세계 좌표를 잃어버리라는 뜻은 아닙니다.','Homogeneous division connects different projections through one convention; it does not replace the separately retained world coordinates.','각 단계 값을 따로 보관','world / view / clip 구분')])
A(8,'같은 탑의 앞면과 옆면을 따라가기',T,505,606,[
 ('높은 탑의 지붕 모서리와 아래 테라스를 함께 따라가 보겠습니다. 시점이 돌아가면 같은 탑에서 보이는 면이 달라집니다.','Track the tall tower’s roof corner and lower terrace as orbiting changes which faces are visible.'),
 ('화면에서 좌우로 움직이는 위치만 보면 점이 세계에서 움직였는지, 카메라 기준이 바뀌었는지 구분하기 어렵습니다.','Screen movement alone cannot tell whether the point moved in the world or the camera frame changed.'),
 ('건물에 새 블록이 붙는 순간에는 실제 구조도 달라집니다. 그 전후에는 기존 창문이나 난간처럼 이어서 찾을 수 있는 기준점이 유용합니다.','New blocks also change the structure; persistent windows or railings help compare the surrounding moments.'),
 ('멀리 보는 화면과 가까운 화면에서는 작은 모서리가 차지하는 범위가 달라집니다. 계산에서는 카메라 기준 좌표와 투영 매개변수를 따로 남깁니다.','Wide and close framing change a corner’s image extent; calculations should retain view coordinates and projection parameters separately.'),
 ('삼차원 값에 행렬을 곱했다고 곧바로 최종 픽셀이 생기는 것은 아닙니다. 잘라낼 범위와 나눗셈, 출력 창 변환이 더 남아 있습니다.','Multiplying a3D value by a matrix does not immediately produce the final pixel; clipping,division and viewport mapping remain.'),
 ('탑이 화면의 위쪽에 보인다고 그 점의 세계 와이를 화면 와이에 그대로 넣을 수는 없습니다. 카메라가 보는 위쪽과 화면의 아래쪽도 다릅니다.','A tower near the top of the image cannot use worldy directly as screeny; camera up and screen down also differ.'),
 ('실제 장면을 볼 때는 눈에 보이는 변화만 확인하고, 수치 증명은 약속을 정한 우리 예제에서 이어가겠습니다.','We observe visible changes in the game and continue the numeric proof in our separately defined example.')],
 '탑·테라스의 실제 회전·건축·가까운 보기','3D 공간의 좌표는 행렬 후에도 클립·나눗셈·출력 변환이 필요하다')
E(9,'완성된 원근 행렬에 값을 넣기','projection',[
 ('앞 강의의 수평 구십 도 보기에서 가로 줌은 일입니다. 정사각형 픽셀의 십육 대 구 창에서는 세로 줌을 십육 나누기 구로 정하겠습니다.','Use the previous lesson’s horizontal90-degree view: zoomX1 and zoomY16/9 for a square-pixel16:9 viewport.','zx1 / zy16/9','두 축 줌과 창16:9'),
 ('가까운 평면은 일, 먼 평면은 십일입니다. 깊이 범위 영부터 일에 맞추려면 클립 제트를 에이 곱하기 제트 더하기 비로 만듭니다.','With near1 andfar11, map normalized depth to0–1 using clipz equalAz plusB.','n1 / f11 / clip z=Az+B','A=f/(f−n) / B=−nf/(f−n)'),
 ('가까운 제트 일에서는 나눈 깊이가 영, 먼 제트 십일에서는 일이 되어야 합니다. 두 조건을 넣으면 에이는 일 점 일, 비는 마이너스 일 점 일입니다.','Requiring depth0 atz1 and1 atz11 givesA1.1 andB minus1.1.','양 끝 조건으로 A·B 결정','A=1.1 / B=−1.1'),
 ('우리 점의 카메라 제트 사를 넣으면 클립 제트는 삼 점 삼입니다. 더블유에는 원래 제트 사가 들어갑니다.','For viewz4, clipz is3.3 andw stores the originalz4.','z4 → clip z3.3 / w4','1.1×4 − 1.1 = 3.3'),
 ('가로는 이에 일, 세로는 일에 십육 나누기 구를 곱합니다. 완성된 클립 좌표는 이, 십육 나누기 구, 삼 점 삼, 사입니다.','The complete clip coordinate is(2,16/9,3.3,4), from the two zoom terms and the depth mapping.','같은 P의 완성 클립 값','p_clip = (2,16/9,3.3,4)'),
 ('행렬의 세 번째 행에는 일 점 일과 일, 마지막 행에는 마이너스 일 점 일과 영이 들어갑니다. 마지막 열이 제트를 더블유로 복사하는 역할을 확인하세요.','The third row contains1.1 and1; the last contains minus1.1 and0. The final column copiesz intow.','행벡터 P의 마지막 두 행','[0,0,1.1,1] / [0,0,−1.1,0]')])
E(10,'나누기 전에 여섯 경계를 검사하기','clip',[
 ('지금 클립 좌표의 가로와 세로는 마이너스 더블유부터 더블유 사이여야 합니다. 깊이는 오늘 약속대로 영부터 더블유 사이입니다.','Before division, clipx andy lie between minusw andw, while depth lies between0 andw.','클립 공간의 여섯 반공간','−w≤x≤w / −w≤y≤w / 0≤z≤w'),
 ('우리 점에서 더블유는 사입니다. 가로 이는 마이너스 사와 사 사이이고, 세로 십육 나누기 구도 그 사이입니다.','Our point hasw4; x2 andy16/9 both lie between minus4 and4.','가로·세로 경계 통과','−4≤2≤4 / −4≤16/9≤4'),
 ('깊이 삼 점 삼은 영과 사 사이입니다. 세 조건을 모두 만족하므로 이 점은 시야 안에 있습니다.','Depth3.3 is between0 and4, so the point satisfies all three pairs of bounds.','깊이 경계도 통과','0≤3.3≤4'),
 ('가로 클립 값이 오이고 더블유가 사인 점은, 오른쪽 경계를 넘어서 시야 밖에 있습니다. 아직 최종 픽셀을 계산하지 않아도 경계 검사를 할 수 있습니다.','A point with clip x five and w four crosses the right boundary and lies outside the view. We can test that boundary before calculating its final pixel position.','별도 반례 x5 / w4','x>w → 오른쪽 밖'),
 ('이 단계는 화면에 보일 수 있는 영역을 자르는 검사입니다. 다른 물체 뒤에 가려졌는지는 깊이 비교 같은 별도 과정에서 확인합니다.','Clipping limits the viewing region; occlusion behind another object is determined through a separate process such as depth testing.','시야 경계와 가림을 구별','클리핑 ≠ 앞 물체의 가림'),
 ('더블유를 먼저 나눈 점만으로 카메라 뒤와 경계를 처리하려 하면 부호와 특이점을 놓칠 수 있습니다. 삼각형은 동차 클립 공간에서 먼저 잘라야 합니다.','Dividing first can lose crucial sign and singularity handling; triangles must be clipped in homogeneous clip space before division.','클립 → 나눗셈 순서','clip first / divide afterward')])
A(11,'큐브를 옮긴 변화와 시점을 옮긴 변화',P,40,99.5,[
 ('플레이어가 큐브를 들고 옮기는 장면에서는 물체 자체가 방 안에서 이동합니다. 방의 기둥과 큐브를 함께 비교해 보세요.','Carrying the cube changes its location in the chamber; compare it with the fixed pillars.'),
 ('이어 다른 시점에서 큐브를 내려놓고, 레이저가 연결되는 모습을 볼 수 있습니다. 큐브의 세계 배치와 화면 위치는 같은 정보가 아닙니다.','The player sets down the cube from another view and connects the laser; world placement and image position are different information.'),
 ('큐브가 화면의 큰 영역을 차지하는 순간과, 방 전체를 넓게 보는 순간을 구분해 보세요. 화면의 비율만으로 카메라 제트를 정확히 알 수는 없습니다.','Compare the large close cube with wider chamber views; image proportions alone do not reveal its exact viewz.'),
 ('포털 너머의 영상은 또 다른 관찰 문제입니다. 오늘은 포털의 내부 구현을 해석하지 않고, 눈앞의 큐브와 기둥이라는 기준점을 사용합니다.','The portal view is another viewing problem; we use visible cube and pillar landmarks without inferring portal rendering internals.'),
 ('레이저가 장치에 닿으면 길과 출구 쪽 표시가 바뀝니다. 이 게임 규칙의 변화와 카메라 좌표 계산의 변화도 따로 읽어야 합니다.','Laser activation changes the route and exit indicators; distinguish game-state changes from camera-coordinate changes.'),
 ('실제 화면에서는 여러 변화가 동시에 일어납니다. 한 점의 문제를 풀 때는 세계 배치와 카메라, 투영을 하나씩 고정하는 이유입니다.','Real gameplay mixes changes; a one-point calculation isolates world placement,camera and projection one at a time.')],
 '큐브 운반·배치·시점 이동·레이저 출구 활성화','물체 배치·관찰 기준·게임 상태를 구별한다; 포털 구현이나 실제 near값을 추정하지 않는다')
E(12,'가까운 경계를 가로지르는 삼각형','near',[
 ('다음은 별도의 삼각형 문제입니다. 가까운 평면은 일입니다. 꼭짓점 에이는 깊이 영 점 오 영, 나머지 두 꼭짓점은 깊이 이입니다.','Consider a separate triangle with its near plane at one. Vertex A has view depth zero point five zero, while the other two vertices have depth two.','별도 삼각형 / near1','A z0.5 밖 / B·C z2 안'),
 ('하나의 꼭짓점이 밖이라고 삼각형 전체를 버리면, 시야 안에 있는 넓은 부분까지 사라집니다. 경계와 만나는 두 점을 새로 구합니다.','Discarding the whole triangle would remove its visible portion; compute the two edge intersections instead.','전체 제거 대신 두 교점','삼각형과 near 평면의 교차'),
 ('깊이 이에서 영 점 오 영으로 가는 변에서, 깊이가 일이 되는 위치를 찾겠습니다. 차이를 나눈 교점의 비율은 삼 분의 이입니다.','Travel along an edge from depth two toward zero point five zero. The near-plane intersection at depth one occurs two-thirds of the way along that directed edge.','교점 비율 t=2/3','t=(2−1)/(2−0.5)=2/3'),
 ('같은 비율로 가로와 세로도 보간합니다. 이 예제에서는 두 교점의 가로가 마이너스 삼 분의 일과 삼 분의 일입니다.','Interpolate the other coordinates at the same parameter; our intersections havex minusone-third and plusone-third.','두 교점의 x=±1/3','I₁·I₂: z_view=1'),
 ('원래 안쪽의 두 꼭짓점과 새 교점 두 개가 남으면 사각형이 됩니다. 화면에 그릴 때는 다시 삼각형들로 나눌 수 있습니다.','The two inside vertices and two intersections form a quadrilateral, which can be triangulated for drawing.','남는 영역은 사각형','밖 꼭짓점 제외 / 교점 추가'),
 ('교점의 클립 제트는 영이고 더블유는 일입니다. 경계 검사가 끝난 뒤 각 점을 더블유로 나누겠습니다.','At each new intersection, clipz0 andw1 match the near boundary; divide only after completing clipping.','교점은 clip z0 / w1','새 점도 클립 → 나눗셈'),
 ('작은 양수 제트가 커다란 더블유를 만든다는 원문 표현은 바로잡아야 합니다. 더블유는 작아지고, 커지는 것은 일 나누기 더블유와 나눗셈 결과입니다.','Correct the source’s wording: a small positivez makesw small, while1/w and divided results can grow large.','원문 작은 z 오류 교정','z→0⁺ / w→0⁺ / 1/w→∞'),
 ('가까운 평면은 이런 불안정한 영역을 제한하지만, 너무 크게 잡으면 가까운 벽이나 바닥을 잘라냅니다. 실제 값은 필요한 범위와 정밀도를 함께 보고 정합니다.','A near plane limits that unstable region, but an overly large value cuts nearby walls and floors; choose it with range and precision in mind.','near 범위와 정밀도 함께','특이점 제한 / 가까운 기하 손실')])
E(13,'같은 장면을 다른 규약으로 적는 법','alternate',[
 ('깊이 범위를 마이너스 일부터 일로 정할 수도 있습니다. 이때 클립 제트의 허용 범위는 마이너스 더블유부터 더블유입니다.','Normalized depth may instead use minus1 to1, requiring clipz between minusw andw.','다른 깊이 범위[-1,1]','−w≤z_clip≤w'),
 ('가까운 평면 일과 먼 평면 십일은 유지합니다. 먼저 제트에 일 점 이를 곱하고, 거기에서 이 점 이 영을 뺍니다. 이 클립 깊이를 더블유로 나눕니다.','Keep near one and far eleven. Multiply view z by one point two, subtract two point two zero, and divide the resulting clip depth by w.','같은 n·f / 다른 깊이 식','z_clip=1.2z−2.2 / w=z'),
 ('우리 점의 제트 사를 넣으면 클립 제트는 이 점 육, 나눈 깊이는 영 점 육오입니다. 앞의 영 점 팔이오와 다른 규약의 값입니다.','Atz4 this gives clipz2.6 and depth0.65, rather than0.825 from the previous convention.','같은 P / 깊이0.65','(1.2×4−2.2)/4=0.65'),
 ('영 점 육오에 일을 더하고 이로 나누면 영 점 팔이오입니다. 두 깊이 범위 사이의 변환을 거치면 같은 위치를 가리킵니다.','Mapping0.65 by adding1 and dividing by2 gives0.825; the two ranges describe the same location.','[-1,1] → [0,1]','(0.65+1)/2=0.825'),
 ('오른손 카메라에서 앞쪽을 마이너스 제트로 두고 열벡터를 쓰려면, 전치뿐 아니라 입력 제트의 부호도 바꿔야 합니다.','For right-handed negativez-forward camera coordinates and column vectors, transpose and account for the changed inputz sign.','열벡터 전치 + 앞쪽 부호','행→열 / +z→−z'),
 ('예를 들어 열벡터의 맨 아래 행이 영, 영, 마이너스 일, 영이면 더블유는 마이너스 제트입니다. 앞의 점 깊이 사는 새 카메라 좌표에서 마이너스 사로 적습니다.','A column matrix with last row(0,0,−1,0) makesw equal−z; our depth4 is written as viewz−4 in that camera convention.','w=−z / 앞쪽 z−4','마지막 행 [0,0,−1,0]'),
 ('직교 깊이는 더블유를 일로 유지하며 선형 변환합니다. 영부터 일인 범위에서는, 제트에서 일을 빼고 그 결과를 십으로 나눕니다. 마이너스 일부터 일인 범위에서는, 방금 구한 값에 숫자 이를 곱한 뒤 일을 뺍니다.','Orthographic depth keeps w at one and changes linearly. For zero to one, subtract one from view z and divide by ten. For minus one to one, multiply that result by two, then subtract one.','직교의 두 깊이 범위','(z−1)/10 / 2(z−1)/10−1'),
 ('식의 이름보다 네 가지 약속을 대조하세요. 옛 하드웨어의 특정 행렬 제약을 모든 현대 그래픽스 환경의 규칙으로 넓히지 않습니다.','Compare the four conventions rather than just formula names; historical hardware restrictions do not define all modern graphics systems.','현재 코드의 실제 약속 확인','역사적 하드웨어 제한은 별도')])
A(14,'가려진 지붕과 화면 밖을 구별하기',T,626,730,[
 ('앞쪽 테라스에 새 건물이 붙고, 긴 지붕의 모양이 달라집니다. 안쪽 공간과 뒤의 탑을 함께 관찰해 보세요.','New construction changes the front terrace and long roof; watch the interior opening and rear tower together.'),
 ('시점이 돌아가면 탑의 일부가 앞쪽 지붕 뒤로 숨습니다. 이런 가림은 화면 바깥으로 나가서 잘린 것과 다릅니다.','Orbiting hides part of the tower behind a front roof; that differs from leaving the screen boundary.'),
 ('더 높은 시점에서는 처음에 보이지 않던 내부 발판이 드러납니다. 보이지 않는 이유를 하나로 뭉뚱그리면 오류를 찾기 어렵습니다.','An elevated view reveals previously hidden platforms; treating all invisibility as one problem makes debugging difficult.'),
 ('같은 점이 시야 안에 있는지 먼저 검사하고, 그다음 앞쪽 물체와의 관계를 확인한다고 생각해 보세요.','First ask whether a point is within the view, then consider its relation to foreground objects.'),
 ('이 장면에서 가까운 평면 때문에 생긴 구멍을 관찰했다고 말하지는 않겠습니다. 눈에 보이는 것은 건축과 회전에 따른 가림의 변화입니다.','We have not identified a near-plane hole here; the observed changes are construction and viewpoint-dependent occlusion.'),
 ('실제 게임의 가까운 평면 값이나 깊이 버퍼 형식도 화면만으로 알 수 없습니다. 명시한 삼각형 예제가 클리핑의 수치 근거입니다.','The image does not establish the game’s near distance or depth format; our defined triangle supplies the numeric clipping proof.'),
 ('화면을 가까이 보거나 멀리 볼 때에도 건물의 기준점을 계속 유지하세요. 다른 지붕으로 바뀌었다면 비교의 대상부터 달라집니다.','Keep the same landmark through closer or wider views; switching to another roof changes the object of comparison.'),
 ('이제 시야 안에서 남은 점을 최종 화면 좌표로 바꾸겠습니다. 이 단계에서도 카메라 공간과 픽셀 공간의 축을 구분해야 합니다.','Next we map surviving points to screen coordinates, still distinguishing camera axes from pixel axes.')],
 '실제 새 테라스·탑과 앞 지붕의 가림·높은 보기','클립 경계의 제거와 물체 간 가림을 구분한다; 관찰하지 않은 게임 near현상을 주장하지 않는다')
E(15,'w로 나누고 출력 창에 놓기','viewport',[
 ('우리 점의 클립 좌표로 돌아오겠습니다. 가로는 이, 세로는 십육 나누기 구, 깊이는 삼 점 삼, 네 번째 성분은 사입니다. 이 네 값을 모두 사로 나눕니다.','Return to our point in clip space: horizontal two, vertical sixteen ninths, depth three point three, and fourth component four. Divide all four components by four.','같은 P / w4로 나눔','(2,16/9,3.3,4) ÷ 4'),
 ('정규화된 가로는 영 점 오, 세로는 구 분의 사, 깊이는 영 점 팔이오입니다. 아직 화면의 픽셀 좌표는 아닙니다.','NDC is(0.5,4/9,0.825); these are not yet pixel coordinates.','NDC=(0.5,4/9,0.825)','x=2/4 / y=(16/9)/4 / z=3.3/4'),
 ('출력 창은 왼쪽에서 백, 위에서 오십 떨어진 곳에 놓고, 너비 팔백과 높이 사백오십으로 정합니다. 전체 화면과 다른 작은 창입니다.','Use a viewport starting at(100,50), width800 and height450: a rectangle offset within the full image.','viewport=(100,50;800,450)','작은 창의 위치·크기를 반영'),
 ('가로는 먼저 정규화된 값에 숫자 일을 더합니다. 그 결과를 이로 나누고, 너비를 곱한 뒤 창의 시작 위치를 더합니다. 영 점 오는 창 너비의 사 분의 삼 위치입니다.','For horizontal position, first add one to the normalized coordinate. Divide by two, multiply by the window width, then add its starting position. Zero point five maps to three-quarters of the window width.','가로를 창에 대응','x_screen=100+(0.5+1)×800/2'),
 ('계산하면 가로는 칠백입니다. 창의 중심 오백보다 오른쪽으로 이백 떨어져 있습니다.','The result isx700, two hundred pixels right of the viewport’s center500.','최종 가로700','100+600=700'),
 ('세로는 위가 플러스였던 방향을 뒤집습니다. 일에서 구 분의 사를 빼고, 높이 사백오십의 절반을 곱한 다음 오십을 더합니다.','For top-left screen coordinates, use1 minus4/9, multiply by half the height450,then add50.','세로 부호를 뒤집기','y_screen=50+(1−4/9)×450/2'),
 ('세로는 백칠십오입니다. 따라서 같은 한 점의 최종 화면 좌표는 칠백, 백칠십오입니다.','This givesy175, so the point’s final screen coordinate is(700,175).','같은 P의 최종 화면좌표','P_screen=(700,175)'),
 ('이 값은 연속적인 화면 위치입니다. 픽셀 중심을 어느 위치에 두고 어떤 샘플이 덮이는지는 래스터화의 약속입니다. 무조건 정수로 반올림해 정점을 옮기지는 않습니다.','This is a continuous screen position; pixel-center and coverage rules belong to rasterization. Do not blindly round the vertex to an integer.','연속 위치 / 픽셀 커버리지는 별도','viewport 변환 뒤 래스터화')])
E(16,'깊이0.825는 실제 거리0.825가 아닙니다','depth',[
 ('가로와 세로를 픽셀로 옮긴 뒤에도 깊이를 남깁니다. 겹치는 삼각형 중 어느 표면이 앞인지 판단하는 데 필요합니다.','Retain depth after mappingx andy to pixels; it helps determine the front surface where triangles overlap.','화면 위치와 깊이를 함께','screen(x,y) / depth'),
 ('우리 원근 행렬의 깊이는 일 점 일에서 일 점 일을 제트로 나눈 값을 뺀 것입니다. 거리와 같은 속도로 증가하지 않습니다.','Our perspective depth is1.1 minus1.1/z, so it is not linear in forward distance.','원근 깊이 d=1.1−1.1/z','z=1 →0 / z=11 →1'),
 ('깊이 이는 영 점 오오, 깊이 사는 영 점 팔이오입니다. 세계에서 같은 거리 차이여도 저장되는 깊이의 차이는 같지 않습니다.','Atz2 depth is0.55; atz4 it is0.825. Equal distance increments do not produce equal stored-depth increments.','z2→0.55 / z4→0.825','가까운 쪽에서 변화가 더 큼'),
 ('깊이 육은 영 점 구일육칠 정도입니다. 일과 십일의 중간 거리인데도 영 점 오가 되지 않습니다.','Atz6 depth is about0.9167, not0.5 even though6 is midway between1 and11.','중간 거리 z6의 반례','1.1−1.1/6≈0.9167'),
 ('직교 투영은 같은 구간에서 제트 빼기 일을 십으로 나눕니다. 깊이 육은 영 점 오가 되어 거리와 선형으로 연결됩니다.','Orthographic depth uses(z−1)/10;z6 maps to0.5 and varies linearly with distance.','직교는 선형 깊이','(6−1)/10=0.5'),
 ('깊이 버퍼의 정밀도는 이 변환과 저장 형식을 함께 보고 판단합니다. 부동소수점이라는 이유만으로 모든 거리에 같은 정밀도를 주는 것은 아닙니다.','Precision depends on the projection mapping and storage format together; floating-point storage alone does not guarantee equal distance precision.','변환 + 저장 형식 + near·far','float라고 거리 정밀도가 균일하지 않음'),
 ('원문에 나온 더블유 버퍼링은 더블유를 거리처럼 사용하는 역사적 방식입니다. 직교에서는 더블유가 언제나 일이므로 그 값만으로 깊이를 구분할 수 없습니다.','The source’sw-buffering is historical distance-related storage; constant orthographicw1 cannot distinguish depths by itself.','역사적 w 버퍼링 / 직교 w1','perspective w=z / ortho w=1')])
A(17,'겹치는 건물의 앞뒤를 읽기',T,1184,1269,[
 ('앞의 발판과 뒤의 높은 건물을 같이 보겠습니다. 작은 건물이 추가되며, 긴 난간 앞에 새로운 벽이 생깁니다.','Watch the front platform and taller rear buildings as new small structures add walls in front of the long railing.'),
 ('화면 위치가 비슷해도 한 표면이 다른 표면을 덮을 수 있습니다. 가로와 세로 좌표만 저장하면 이런 앞뒤 관계를 정할 수 없습니다.','Surfaces at similar screen positions may cover one another; screenx andy alone cannot determine that relationship.'),
 ('높은 시점에서는 안쪽 발판을 넓게 보고, 낮은 시점에서는 지붕과 벽이 겹쳐 보입니다. 어떤 면이 먼저 보이는지 살펴보세요.','Elevated views expose interior platforms, while lower views overlap roofs and walls; notice which surface comes first.'),
 ('계산한 깊이 값은 거리의 이름표가 아니라 우리가 선택한 변환의 결과입니다. 영 점 팔이오를 공간의 영 점 팔이오 단위라고 읽지 않습니다.','Computed depth is the output of a chosen mapping, not a distance label;0.825 is not0.825 world units.'),
 ('앞뒤 비교에서 사용할 크고 작은 값의 방향도 명시해야 합니다. 오늘 예제에서 가까운 평면의 저장 깊이는 영이고, 먼 평면의 저장 깊이는 일입니다.','State which direction represents nearer and farther surfaces. In this example the stored depth at the near plane is zero, and the stored depth at the far plane is one.'),
 ('게임이 이 예제와 같은 깊이 저장 방식을 쓴다고 확인한 것은 아닙니다. 지금은 실제 가림의 필요와 명시한 계산을 연결합니다.','We have not established the game’s depth representation; this footage motivates the need for occlusion handling.'),
 ('여러 건물의 좌표를 비교할 때는 같은 카메라와 같은 투영에서 얻은 값인지 확인하세요. 서로 다른 카메라의 깊이를 바로 비교하지 않습니다.','Compare depth values produced by the same camera and projection; values from different views are not directly comparable.'),
 ('중간 좌표를 남겨 두면, 표면이 사라진 원인이 세계 배치인지 시야 경계인지 깊이 비교인지 차례로 확인할 수 있습니다.','Retaining intermediate coordinates lets you check world placement,view boundaries and depth comparison in turn.')],
 '실제 새 벽·발판·지붕의 겹침과 관찰 높이 변화','최종 가로세로 외에 깊이 정보가 필요하고 규약에 맞게 해석한다')
E(18,'텍스처 값도 w를 기억해야 합니다','interpolation',[
 ('더블유의 역할은 좌표를 나누는 데서 끝나지 않습니다. 삼각형 위의 텍스처 좌표나 색을 보간할 때도 원근을 반영해야 합니다.','The role ofw continues into perspective-correct interpolation of texture coordinates and other vertex attributes.','좌표 나눗셈 뒤에도 w 필요','정점별 속성의 원근 보정'),
 ('별도의 변 예제를 보겠습니다. 화면 왼쪽 끝의 더블유는 일, 오른쪽 끝의 더블유는 사입니다. 텍스처 값은 각각 영과 일입니다.','For a separate edge example, endpoints havew1 and4 and texture coordinateu0 and1.','두 끝 w1·w4 / u0·u1','왼쪽: (w1,u0) / 오른쪽: (w4,u1)'),
 ('화면의 정확한 중간에서 값을 단순 평균하면 영 점 오입니다. 하지만 원근 투영한 화면의 중간이 원래 변의 길이 중간은 아닙니다.','A direct screen-space average gives0.5, but a projected midpoint is not the geometric midpoint of the3D edge.','화면 중간 ≠ 공간 변 중간','단순 평균 u=0.5'),
 ('각 끝에서 텍스처 값을 더블유로 나눈 것과, 일 나누기 더블유를 따로 보간한 다음 두 결과를 나눕니다.','Interpolateu/w and1/w separately, then divide the interpolated results.','u/w와1/w를 함께 보간','u = interp(u/w) / interp(1/w)'),
 ('분자의 평균에 들어갈 값은 영과 영 점 이오입니다. 평균은 영 점 일이오, 즉 팔 분의 일입니다. 분모에서는 일과 영 점 이오의 평균을 구하므로, 영 점 육이오, 즉 팔 분의 오가 됩니다.','The numerator averages zero and zero point two five, giving zero point one two five, or one-eighth. The denominator averages one and zero point two five, giving zero point six two five, or five-eighths.','분자1/8 / 분모5/8','(1/8)/(5/8)=1/5'),
 ('따라서 올바른 텍스처 값은 영 점 이입니다. 영 점 오로 칠한 결과와 비교하면 무늬가 원근에 맞게 붙는 이유를 이해할 수 있습니다.','The correctu is0.2, rather than0.5, explaining how a texture remains attached under perspective.','올바른 u=0.2','공간 변의20% → 화면 변의50%'),
 ('실제 삼각형에서는 화면의 세 보간 가중치를 사용해 같은 원리를 적용합니다. 보간 방식의 예외를 요청하지 않았다면 보통 하드웨어가 이 과정을 처리합니다.','For triangles, use three screen-space weights with the same principle; hardware commonly handles this unless another interpolation mode is requested.','삼각형도 같은 분모 원리','Σ(λu/w) / Σ(λ/w)')])
E(19,'투영 평면의 거리와 행렬 배율','plane-scale',[
 ('단순 투영에서 제트가 일인 평면을 사용한 것은 편리한 약속입니다. 같은 시야를 유지하면서 가상 평면을 둘로 옮겨도 최종 보기는 같을 수 있습니다.','Using a plane atz1 is convenient; moving the virtual plane to2 can preserve the final image if the view is kept unchanged.','임의의 투영 평면 d1→d2','프러스텀 모양을 유지'),
 ('광선이 평면과 만나는 위치는 두 배가 됩니다. 하지만 그 평면에서 사용하는 직사각형의 너비와 높이도 두 배로 키웁니다.','Ray intersections double, but so do the rectangle’s width and height on that plane.','교점과 창을 함께2배','투영점2배 / 평면 창2배'),
 ('점이 창에서 차지하는 비율은 그대로입니다. 최종 픽셀에 매핑하면 앞과 같은 위치에 놓입니다.','The point’s fraction of the rectangle stays unchanged, yielding the same final pixel position.','비율 유지 → 같은 픽셀','(2x)/(2W) = x/W'),
 ('물리 카메라에서 센서 크기를 고정하고 초점 거리를 바꾸는 경우와는 조건이 다릅니다. 앞 강의의 센서와 줌 예제는 이 차이를 보여주었습니다.','A physical camera with a fixed sensor and changing focal length has different conditions, as the preceding lesson illustrated.','고정 센서의 줌과 구별','센서 고정 / 프러스텀 변경'),
 ('클립 좌표 네 성분에 같은 양수 배율을 곱해도 나눈 위치는 같습니다. 예를 들어 두 배로 만든 좌표를 더블유 팔로 나누면 같은 정규화 좌표입니다.','Multiplying all four clip components by the same positive factor preserves their divided position; doubling also doublesw to8.','동차 좌표의 양수 공통 배율','(4,32/9,6.6,8) → 같은 NDC'),
 ('다만 나누기 전의 더블유 값과 하드웨어의 지원 조건은 별도로 확인합니다. 출력된 그림이 같다는 성질을 모든 내부 처리의 동일함으로 확대하지 않습니다.','Still verify the pre-divisionw value and supported hardware conditions; equal images do not imply every internal operation is identical.','같은 나눈 위치 / 내부 조건 별도','양수 배율 / 지원 조건 확인')])
A(20,'지붕 무늬와 표면을 함께 보기',T,1269,1322,[
 ('가까이 보이는 지붕의 반복 무늬와 옆의 창문을 골라 보세요. 시점이 바뀌어도 무늬는 건물 표면과 함께 보입니다.','Choose a roof pattern and nearby window; the pattern remains on the building surface as the view changes.'),
 ('화면에서 보이는 무늬의 간격만 그대로 따라가면, 기울어진 면의 서로 다른 지점에 같은 비율을 붙이기 어렵습니다.','Screen spacing alone cannot determine matching surface fractions across a tilted face.'),
 ('앞의 변 예제는 화면 중간에서 텍스처 값 영 점 이가 필요한 이유를 계산했습니다. 그 숫자는 이 게임에서 측정한 값은 아닙니다.','Our edge calculation explained why a screen midpoint needsu0.2; that number was not measured from this game.'),
 ('실제 지붕의 무늬가 어떤 셰이더에서 만들어졌는지도 단정하지 않습니다. 표면과 화면 사이의 연결이 필요한 모습을 관찰한 것입니다.','We do not infer the shader that creates this roof pattern; it motivates the required connection between surface and image.'),
 ('다음 텍스처 강의에서는 표면의 위치에 유브이 좌표를 붙이는 방법으로 이 연결을 이어가겠습니다.','The texture lesson continues this connection by assigningUV coordinates to surfaces.')],
 '실제 지붕의 반복 무늬·창문·시점 변화','표면에 연결된 값의 보간 필요를 보여주며 게임의 텍스처 방식은 추정하지 않는다')
E(21,'어디까지 GPU가 자동으로 처리할까요?','pipeline',[
 ('일반적인 그래픽스 경로에서 정점 셰이더는 클립 좌표를 출력합니다. 정규화 좌표나 최종 픽셀을 미리 넣는 것과 구분하세요.','In a conventional graphics path, the vertex shader outputs clip coordinates, rather than pre-divided NDC or screen pixels.','정점 셰이더 출력은 clip','출력 p_clip / 아직 w 나눗셈 전'),
 ('이후 삼각형의 클리핑, 더블유 나눗셈과 출력 창 변환을 파이프라인이 처리합니다. 오늘의 손 계산은 자동 단계에서 무엇이 일어나는지 이해하기 위한 것입니다.','The pipeline then clips triangles,divides and maps to the viewport; our manual calculation explains those automatic stages.','클립 → 나눗셈 → viewport','일반 렌더 파이프라인의 자동 단계'),
 ('캐릭터 머리 위에 이름을 놓거나, 화면에 들어오는지를 검사할 때는 같은 계산을 씨피유에서 사용할 수 있습니다. 이때도 더블유와 클립 조건을 함께 확인합니다.','CPU calculations can place name labels or test visibility; retainw and the clipping conditions there too.','CPU 화면 표식·가시성 검사','w 부호 / 클립 경계 / 출력 창'),
 ('한 점이 시야 안에 있다고 물체 전체가 보인다는 뜻은 아닙니다. 범위 검사, 가림 검사와 세부 수준 선택의 목적을 나누어야 합니다.','One point inside the view does not prove an entire object visible; bounds,occlusion andLOD selection serve different purposes.','점의 검사와 물체의 검사 구별','한 점 통과 ≠ 전체 물체 가시'),
 ('조명은 위치와 광원을 같은 공간에 놓고 계산해야 합니다. 그 공간이 세계인지 카메라인지는 선택할 수 있지만 서로 다른 공간의 값을 바로 빼지는 않습니다.','Lighting must combine geometry and lights in the same space; world or view space can be chosen, but values from different spaces cannot be directly subtracted.','기하·광원을 같은 공간으로','같은 공간에서 조명 계산'),
 ('광원도 장면을 바라보는 별도 카메라처럼 공간을 가질 수 있습니다. 그림자 맵이나 고보 이미지 투사를 이해할 때 유용합니다.','A light can have a camera-like viewing space, useful for shadow maps and projectedgobo images.','광원 기준의 또 다른 보기','light space / 그림자·이미지 투사'),
 ('표면에는 접선, 종접선, 법선이라는 세 축을 붙일 수도 있습니다. 이 접선 공간의 구체적인 구성은 유브이와 노멀 매핑 강의에서 다시 설명하겠습니다.','A surface can carry tangent,bitangent and normal axes; their construction returns in theUV and normal-mapping lessons.','표면의 T·B·N 기준','tangent space / 뒤의 매핑 강의')])
E(22,'숫자를 바꾸어 직접 풀어보기','exercise',[
 ('연습 문제입니다. 같은 로컬 점과 모델 이동을 유지하고, 카메라만 삼, 일, 일로 옮깁니다. 회전과 투영 행렬은 그대로입니다.','For practice, keep the local point and model translation but move the camera to(3,1,1), with rotation and projection unchanged.','별도 연습 / 카메라만 변경','local(1,0,0) / world(4,2,5)'),
 ('세계의 점 사, 이, 오에서 새 카메라를 빼면 일, 일, 사입니다. 앞쪽 깊이는 사로 유지되고 오른쪽 값만 일이 됩니다.','Subtracting the new camera gives view(1,1,4), changing only the horizontal component.','새 view=(1,1,4)','(4,2,5)−(3,1,1)=(1,1,4)'),
 ('클립 좌표는 일, 십육 나누기 구, 삼 점 삼, 사입니다. 나눈 가로는 영 점 이오이고 세로와 깊이는 앞과 같습니다.','Clip becomes(1,16/9,3.3,4); dividedx is0.25 whiley and depth stay unchanged.','새 NDC x0.25','NDC=(0.25,4/9,0.825)'),
 ('같은 출력 창에 놓으면 가로는 육백, 세로는 백칠십오입니다. 카메라가 오른쪽으로 옮겨져 같은 세계의 점은 화면 왼쪽으로 이동했습니다.','The same viewport yields(600,175); moving the camera right moves this fixed point left in the image.','새 화면좌표(600,175)','100+(0.25+1)×400=600'),
 ('두 번째로 출력 창의 시작 위치만 영, 영으로 바꾸어 보세요. 처음 점의 나눈 좌표는 그대로인데 최종 좌표는 육백, 백이십오가 됩니다.','For another exercise, change only the viewport origin to(0,0); the original point’s NDC stays fixed and screen position becomes(600,125).','별도 연습 / 원점만 이동','원래 P / viewport(0,0;800,450)'),
 ('화면 크기를 천구백이십 곱하기 천팔십 전체로 바꾸면 처음 점은 천사백사십, 삼백에 놓입니다. 앞의 작은 창 결과와 섞지 마세요.','Using the full1920-by1080 viewport instead places the original point at(1440,300); distinguish it from the offset small-window result.','별도 전체 창 결과(1440,300)','원래 P / viewport(0,0;1920,1080)'),
 ('각 문제에서 바꾼 입력을 하나만 표시하세요. 로컬, 세계, 뷰, 클립과 출력 중 처음 달라지는 값을 찾으면 오류를 좁힐 수 있습니다.','Mark only the changed input and find the first differing stage among local,world,view,clip and screen to narrow down errors.','바꾼 입력 → 최초 차이 찾기','같은 점 / 한 조건 변경 / 단계 비교')])
A(23,'실제 건물의 한 점으로 확인하는 습관',T,1459,1559,[
 ('마지막으로 건물 사이의 아치와 앞쪽 테라스를 살펴보겠습니다. 화면이 넓어지거나 시점이 돌아가도 같은 기준점을 계속 찾아보세요.','Look at the arch between buildings and the front terrace; keep finding the same landmark through wider and rotating views.'),
 ('화면에서 안 보이는 순간에는 먼저 다른 건물 뒤로 가렸는지 확인합니다. 다른 위치의 비슷한 아치를 같은 점으로 착각하지 않는 것도 중요합니다.','When it disappears, first check foreground occlusion and avoid confusing a similar arch elsewhere with the original point.'),
 ('새 블록을 붙여 테라스의 높이가 바뀌는 장면에서는 물체의 구조 자체가 달라집니다. 관찰 카메라만 움직였던 구간과 구분하세요.','Adding blocks changes terrace height and structure; distinguish those moments from camera-only movement.'),
 ('높은 테라스에서 보이는 난간과 작은 나무를 같이 기준으로 삼으면, 어느 면을 보고 있는지 더 쉽게 확인할 수 있습니다.','Railings and small trees near a high terrace help identify which surface is being viewed.'),
 ('실제 개발에서 좌표를 출력할 수 있다면, 먼저 물체에 붙은 점의 이름과 로컬 위치를 기록해 보세요. 그다음 세계와 카메라 값을 순서대로 남깁니다.','In a real development project, name an object-attached point and log its local coordinates,then world and view values in order.'),
 ('클립 좌표의 네 성분은 나누기 전 상태로 저장합니다. 더블유를 빼먹으면 경계 검사와 투영 이후 값의 관계를 확인하기 어렵습니다.','Log all four clip components before division; omittingw obscures the connection between clipping and the projected result.'),
 ('출력 창이 바뀌면 시작 위치와 너비, 높이도 함께 남깁니다. 분할 화면의 작은 창을 전체 화면 크기로 변환하면 표식이 잘못 놓입니다.','Record viewport origin and size when they change; mapping a split window with full-screen dimensions misplaces the marker.'),
 ('게임의 픽셀만으로 이런 중간 숫자를 알아냈다고 주장하지는 않습니다. 실습에서는 자신이 접근할 수 있는 프로젝트의 실제 값으로 확인하세요.','These game pixels do not reveal the intermediate numbers; practice with actual values accessible in your own project.'),
 ('앞뒤 깊이와 표면의 무늬도 함께 보면, 좌표가 그저 점 하나의 이동으로 끝나지 않는다는 것을 알 수 있습니다. 가림과 보간까지 같은 계산 흐름에 연결됩니다.','Depth and surface patterns show that the chain also supports occlusion and interpolation, beyond moving a single point.'),
 ('계산이 어긋났다면 마지막 좌표만 고치기보다 처음 달라진 공간의 변환을 살펴보세요. 이 방법을 다음 메시와 텍스처 실습에서도 이어가겠습니다.','When the result is wrong, inspect the first incorrect transform; carry that method into the upcoming mesh and texture exercises.')],
 '실제 아치·테라스 건축·난간·회전과 확대','관찰 기준점을 유지하고 실제 접근 가능한 코드의 단계별 값을 검사한다; 직접 개발 영상으로 오분류하지 않는다')
E(24,'한 점의 여정을 끝까지 정리하기','summary',[
 ('오늘 한 점은 로컬의 일, 영, 영에서 시작해 세계의 사, 이, 오, 카메라의 이, 일, 사를 거쳤습니다. 같은 점을 다른 기준으로 읽은 것입니다.','Our point moved through local(1,0,0),world(4,2,5) andview(2,1,4): the same point expressed in different frames.','같은 P / local → world → view','(1,0,0) → (4,2,5) → (2,1,4)'),
 ('투영 행렬은 줌과 깊이를 준비하고 더블유에 사를 넣었습니다. 클립 경계를 검사한 다음 나누어 정규화 좌표를 얻었습니다.','The projection prepared zoom and depth withw4; clipping preceded division into normalized coordinates.','projection → clip → divide','clip(2,16/9,3.3,4) → NDC'),
 ('왼쪽 백, 위쪽 오십에서 시작하는 팔백 곱하기 사백오십 창에 놓으면 칠백, 백칠십오입니다. 최종 창의 위치도 계산의 일부입니다.','The800-by450 viewport at(100,50) placed the point at(700,175); viewport placement is part of the calculation.','최종 화면좌표(700,175)','NDC(0.5,4/9) + 지정한 viewport'),
 ('깊이는 실제 거리와 다른 변환 값이고, 텍스처 보간에는 더블유의 정보가 다시 필요합니다. 이 두 가지를 좌표 나눗셈 뒤에도 잊지 마세요.','Depth is not metric distance, and interpolation still usesw information after coordinate division.','깊이와 보간도 연결','d=1.1−1.1/z / u/w와1/w'),
 ('다음 강의에서는 점들을 연결한 메시와 표면에 붙이는 유브이 좌표를 다루겠습니다. 오늘의 공간 변환이 그 표면을 화면으로 옮기는 바탕이 됩니다.','Next we connect vertices into meshes and attachUV coordinates; today’s transforms move those surfaces onto the screen.','다음: 메시·UV·표면','좌표의 흐름 → 표면의 데이터')])
data={'slug':slug,'chapter':10,'part':3,'totalParts':7,'renderModule':'camera_projection','sourceDependencies':['manim/projects/game-math-part2-full-series/lesson.py','manim/projects/game-math-part2-full-series/camera_frustum.py'],'sourceSections':['10.3.1','10.3.2','10.3.3','10.3.4','10.3.5','10.3.6'],'contract':{'coordinates':'LH row vectors,+z view-forward,+y up;clipz[0,w],NDC depth[0,1];top-left pixel origin. API name alone does not determine all conventions.','mainPoint':'local(1,0,0,1),Mtranslate(3,2,5),world(4,2,5,1);Ctranslate(2,1,1),V=Cinverse;view(2,1,4,1);zx1,zy16/9,n1,f11;clip(2,16/9,3.3,4);NDC(.5,4/9,.825);viewport100,50,800,450;continuous screen(700,175).','nearTriangle':'Separate A(0,−.6,.5),B(−1,.5,2),C(1,.5,2);near1;t2/3 from B/C toward A;intersection(±1/3,−7/30,1);clipz0,w1;retainedquad,clipbeforedivide.','alternate':'Same n1/f11:LHrow[-1,1]Az+B withA1.2/B−2.2;mainz4depth.65→.825. RHcolumn−z-forward uses transposition plus inputz sign conversion. Ortho[0,1]d=(z−1)/10;[-1,1]d=2(z−1)/10−1.','interpolation':'Separate original view edge endpoints(0,0,1),(4,0,4),w1/4,u0/1;screenweight.5givesu.2viau/wand1/w;geometrict.2projectstoscreen.5.','exercises':'Explicit separate camera(3,1,1)→screen(600,175);originalpointviewportorigin0,0,size800,450→(600,125);originalfull1920×1080→(1440,300). Never mix those with main(700,175).','historical':'w-buffering and Wii matrix restrictions are historical context,not modern requirements; positivehomogeneousscale leaves NDC unchanged but check clip/hardware/attribute conventions; float not equal metric precision.','gameEvidence':'Official prerelease2010 Portal2 gameplay and unused unique Townscaper source intervals; actual visible actions only,no matrices/depth/UV/portal internals inferred. Source audio and BGM excluded; visible source credit retained.'},'coverage':{'10.3.1':['03','04','05','06'],'10.3.2':['07','09','10'],'10.3.3':['07','08','19'],'10.3.4':['09','10','11','12','13','14'],'10.3.5':['15','16','17','18','20','21','22'],'10.3.6':['21','23','24'],'completePractice':['15','18','22','24']},'scenes':scenes,'gameCandidates':json.loads((B/'preflight/camera-projection-fresh-game-review.json').read_text(encoding='utf8'))}
assert len(scenes)==24 and sum(s['kind']=='actual' for s in scenes)==8
assert all(len(s['ko'])==len(s['en']) for s in scenes)
p=B/'lessons'/f'{slug}.json';assert not p.exists(),'Resume saved authoring rather than overwrite it'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'slug':slug,'scenes':len(scenes),'paragraphs':sum(len(s['ko']) for s in scenes),'koCharacters':sum(len(x) for s in scenes for x in s['ko']),'actualCapacitySeconds':sum(s.get('maxSeconds',0) for s in scenes),'noBgm':True}))
