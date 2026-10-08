"""Full10.4–10.5 lecture after source, legacy-script and actual-footage review."""
from pathlib import Path
import json
B=Path(__file__).parent; slug='game-math-mesh-uv'; scenes=[]
def E(i,title,mode,lines):
 scenes.append(dict(id=f'{i:02}',title=title,kind='explanation',mode=mode,ko=[x[0] for x in lines],en=[x[1] for x in lines],beats=[x[2] for x in lines]))
def A(i,title,source,segments,lines,focus,claim):
 scenes.append(dict(id=f'{i:02}',title=title,kind='actual',sourceId=source,sourceSegments=[dict(**{'in':a},maxSeconds=b-a) for a,b in segments],**{'in':segments[0][0]},maxSeconds=sum(b-a for a,b in segments),ko=[x[0] for x in lines],en=[x[1] for x in lines],focus=focus,claim=claim))
S='fN4iMYUyODc'; W='wzQLP0Z3zII'
E(1,'형태·빛·무늬는 어떤 데이터로 연결될까요?','overview',[
 ('삼차원 물체의 형태와 빛, 표면 무늬를 연결하려면 정점에 무엇을 저장해야 할까요?','What vertex data connects a3D shape with lighting and surface patterns?','형태 / 빛 / 무늬 → 정점 데이터'),
 ('먼저 게임 속 지붕과 벽을 보고, 삼각형을 인덱스로 연결하는 방법을 계산합니다.','We inspect game roofs and walls, then calculate how indices connect triangles.','지붕·벽 → 삼각형과 인덱스'),
 ('이어서 매끄러운 면과 날카로운 모서리에 맞는 법선을 만들고, 확대할 때 법선을 올바르게 변환합니다.','Then we construct normals for smooth surfaces and sharp corners and transform them correctly under scale.','법선 만들기 → 변환하기'),
 ('마지막에는 유브이 좌표로 무늬를 연결하고, 반복을 너무 일찍 처리하면 왜 틀리는지 직접 확인하겠습니다.','Finally we map patterns with UVs and demonstrate why applying repeat too early fails.','UV 연결 → 보간 뒤 주소 처리')])
A(2,'지붕 패널의 선이 전부 삼각형일까요?',S,[(60,81),(110,132)],[
 ('선셋 오버드라이브에서 지붕 위를 이동하는 장면입니다. 경사진 지붕의 바깥 윤곽과 표면의 길게 반복되는 선을 따로 보세요.','Traverse a roof in Sunset Overdrive. Separate its sloped outline from repeated lines across the surface.'),
 ('옆으로 이동하면 지붕과 벽의 다른 면이 드러납니다. 모양을 정하는 표면과 그 위의 무늬를 같은 정보라고 생각하기 쉽습니다.','Moving sideways reveals roof and wall faces. It is easy to confuse the surface shape with its pattern.'),
 ('다음 지붕에서도 패널과 환기구가 보입니다. 외곽을 바꾸는 형태와 면 안에 보이는 선을 구분해 보세요.','The next roof has panels and vents. Distinguish shape that changes the outline from lines inside a face.'),
 ('이 선 하나마다 실제 모서리가 있는지는 완성 화면만으로 알 수 없습니다. 기하 구조와 텍스처가 모두 비슷한 선을 만들 수 있습니다.','Rendered pixels cannot prove that each line is a geometric edge: geometry and textures can both create lines.'),
 ('그래서 먼저 우리가 직접 정의한 작은 메시로 저장 방식을 보겠습니다. 게임의 숨은 정점 개수를 추측하는 예제가 아닙니다.','We therefore define our own small mesh to explain storage, without guessing this game hidden vertex count.')],
 '움직이는 카메라에서 경사 지붕·환기구·표면 패널 선과 외곽을 구별','완성 화면의 무늬와 실제 메시 모서리는 구분해야 한다')
E(3,'부피를 만드는 방법과 표면을 저장하는 방법','representation',[
 ('물체를 기술하는 방법은 하나가 아닙니다. 구성적 입체 기하는 기본 도형의 합집합, 교집합과 차집합으로 모양을 만듭니다.','Shapes have multiple representations. CSG combines solids using union, intersection and difference.','CSG: 합집합 / 교집합 / 차집합'),
 ('상자에서 원기둥을 빼면 구멍이 생기는 예를 생각해 보세요. 이것은 우리 도식의 부피 연산이며 게임 화면의 구현을 확인한 것은 아닙니다.','Subtracting a cylinder from a box makes an opening in our solid diagram; it does not identify a game implementation.','상자 − 원기둥 → 구멍 / 원래 도식'),
 ('메타볼처럼 부피나 암시적 함수를 사용하는 방법도 있습니다. 이런 표현과, 화면에 그릴 표면을 저장하는 표현은 목적이 다릅니다.','Metaballs and implicit functions offer other volume descriptions; representation and display-surface storage serve different purposes.','부피·암시적 함수 ↔ 표시할 표면'),
 ('삼각형 메시는 표면을 작은 평면 조각으로 연결합니다. 반드시 닫힌 물체일 필요는 없고, 열린 천이나 잎 같은 표면도 가능합니다.','Triangle meshes connect planar surface pieces; they may represent open cloth or leaves rather than closed solids.','삼각형: 평면 표면 조각 / 열린 메시 가능'),
 ('편집 도구의 다각형은 정점 수가 다양할 수 있습니다. 렌더링용으로 삼각형을 나누되, 이전 장에서 배운 유효한 삼각분할을 사용합니다.','Editing polygons can have varying vertex counts. Rendering triangulates them with the valid methods developed earlier.','편집용 다각형 → 유효한 삼각분할'),
 ('이제 관심은 삼각형 하나의 성질보다 여러 삼각형이 어떤 정점을 공유하는지입니다. 정점, 모서리와 면의 관계를 데이터로 옮깁니다.','We now focus on shared vertices rather than one triangle, translating vertex, edge and face relationships into data.','정점 / 모서리 / 면 → 연결 정보')])
E(4,'네 정점과 두 삼각형의 메모리를 계산하기','indexed',[
 ('사각형을 두 삼각형으로 나눕니다. 정점은 영, 일, 이, 삼 네 개이고 삼각형 목록은 영 일 이, 영 이 삼으로 정합니다.','Split a quad into triangles012 and023 using four vertices numbered0 through3.','V: 0,1,2,3 / T: (0,1,2),(0,2,3)'),
 ('단순 배열은 삼각형마다 정점 데이터 세 개를 저장합니다. 여기서는 같은 위치와 속성을 가진 영번과 이번 정보를 두 번 저장합니다.','A triangle array stores three records per face, duplicating vertices0 and2 with their attributes.','단순 배열: 정점 레코드 6개'),
 ('인덱스 방식은 정점 목록과 정수 목록을 나눕니다. 삼각형은 실제 데이터를 복사하는 대신 그 목록의 번호 세 개를 가리킵니다.','Indexed storage separates vertex records from integers, with three indices referencing the data for each triangle.','정점 목록 + 인덱스 6개'),
 ('정점 하나가 삼십이 바이트이고 인덱스가 이 바이트라고 약속합니다. 단순 배열은 육 곱하기 삼십이, 백구십이 바이트입니다.','Assume32-byte vertices and2-byte indices. The triangle array uses6 times32, or192 bytes.','가정: V 32B / index 2B → 192B'),
 ('인덱스 방식은 사 곱하기 삼십이와 육 곱하기 이를 더합니다. 백이십팔 더하기 십이, 모두 백사십 바이트입니다.','Indexed storage uses4 times32 plus6 times2:128 plus12 equals140 bytes.','4×32 + 6×2 = 128+12 = 140B'),
 ('노션의 다른 계산은 정점 하나를 여섯 면이 공유하는 국소 예입니다. 데이터 삼십이와 인덱스 십이를 합해 사십사 바이트이며, 사각형 전체의 백사십과 범위가 다릅니다.','The source separate local example shares one vertex among six faces:32 plus12 equals44 bytes, unlike the whole quad140.','정점 하나 6회: 192→44B / 전체 quad: 192→140B'),
 ('총량은 정점 크기와 공유 정도, 인덱스 형식에 따라 달라집니다. 위치뿐 아니라 법선, 유브이, 색과 스키닝 정보도 같은 정점 레코드에 포함될 수 있습니다.','Total savings depend on attributes, sharing and index format; records may include normals, UVs, colors and skinning data.','총량: 정점 속성·공유·인덱스 형식에 의존')])
E(5,'같은 좌표와 같은 정점은 다릅니다','topology',[
 ('인덱스가 같으면 같은 정점 데이터를 사용합니다. 위치만 같은 두 레코드는 법선이나 유브이가 다르면 별도 정점이어야 합니다.','An identical index shares a record; equal positions with different normals or UVs require separate records.','같은 위치 ≠ 같은 전체 정점 레코드'),
 ('앞면을 정하는 정점 순서는 먼저 약속합니다. 원문의 시계 방향 규약도 하나의 선택이며 실제 렌더러의 앞면 설정과 함께 맞춰야 합니다.','Declare the winding convention. The source clockwise choice must agree with the renderer front-face configuration.','앞면 규약: winding + 렌더러 설정'),
 ('영 일 이를 일 이 영으로 순환하면 같은 방향입니다. 영 이 일처럼 두 번호를 바꾸면 방향이 반대가 됩니다.','Cyclic012 to120 preserves orientation; swapping two indices to021 reverses it.','012 → 120: 유지 / 012 → 021: 반전'),
 ('두 삼각형은 영번과 이번 사이 모서리를 공유합니다. 하지만 인덱스 목록에 이웃 면 번호가 바로 저장되어 있는 것은 아닙니다.','The triangles share edge0–2, but a plain index list does not explicitly store neighboring face references.','공유 edge(0,2) / 인접 면은 암묵적'),
 ('이웃을 자주 찾는 편집 도구는 모서리와 연결 면의 참조를 따로 저장할 수 있습니다. 윙드 에지 같은 구조가 그 예입니다.','Editors can store explicit edges and adjacent-face references, as in winged-edge structures.','편집·순회: 명시적 인접 참조'),
 ('열린 모서리는 한 면만 연결되고 비다양체 모서리는 둘보다 많을 수도 있습니다. 모든 모서리에 이웃 면이 정확히 둘이라고 가정하면 안 됩니다.','Boundary edges may have one face and nonmanifold edges more than two, so exactly-two adjacency is not universal.','경계: 1면 / 비다양체: 2면 초과 가능'),
 ('같은 속성이나 재질로 묶은 삼각형은 렌더링 배치로 보낼 수 있습니다. 편집 자료구조와 GPU 전달 형식을 꼭 같은 클래스로 만들 필요는 없습니다.','Triangles can be batched by compatible attributes or materials; editor structures need not match GPU delivery structures.','편집 구조 ↔ 렌더링 전달 형식')])
A(6,'벽의 격자를 정점 연결선으로 읽어도 될까요?',W,[(200,260)],[
 ('빅 워크의 녹색 방을 돌아보겠습니다. 가까운 판 위의 검은 격자와, 그 뒤의 둥근 벽과 바위를 나누어 보세요.','Explore the green room in Big Walk, separating the black grid on a nearby panel from curved walls and rocks.'),
 ('시점이 움직이면 판의 바깥 테두리와 면 안의 선이 함께 보입니다. 테두리는 보이는 형태를 구분하고, 격자는 면의 세부 모습으로 읽힙니다.','Moving views show panel boundaries and internal lines, separating visible shape from surface detail.'),
 ('뒤쪽에는 원형 구멍과 원통 모양 받침도 있습니다. 직선 격자와 둥근 윤곽이 같은 장면 안에 나타납니다.','Circular openings and cylindrical bases appear behind them, placing straight patterns and curved outlines together.'),
 ('그러나 검은 선이 모두 삼각형 인덱스의 모서리라는 증거는 아닙니다. 무늬, 별도 표면이나 다른 표현일 수도 있습니다.','Black lines do not prove triangle-index edges; they could be patterns, separate surfaces or another representation.'),
 ('앞에서 만든 인덱스 목록이라면 영번과 이번의 연결을 직접 확인할 수 있습니다. 완성 게임 화면에는 그 목록이 공개되어 있지 않습니다.','Our explicit index list proves the0–2 connection; these rendered game pixels do not expose such a list.'),
 ('형태를 저장하는 데이터와 빛 계산에 필요한 방향도 나누어야 합니다. 다음 도식에서는 표면은 그대로 두고 법선만 바꾸어 비교합니다.','Separate shape data from shading directions. The next diagram keeps geometry fixed while changing normals.'),
 ('카메라가 돌아갈 때 보이는 판의 면과 윤곽을 다시 확인해 보세요. 이 관찰을 바탕으로 면 법선과 정점 법선의 역할을 연결하겠습니다.','Observe the panel faces and outline during the camera movement, motivating face and vertex normals.')],
 '실제 방 이동에서 검은 격자 판·둥근 벽·원형 구멍의 표면과 윤곽','화면 격자는 숨은 토폴로지 증거가 아니며 기하와 셰이딩 방향은 별도')
E(7,'면의 법선과 정점의 법선','normal-kinds',[
 ('면 법선은 그 평면에 수직인 방향입니다. 두 모서리의 외적으로 구하고, 앞면 약속에 맞는 방향을 선택한 뒤 단위 길이로 만듭니다.','A face normal is perpendicular to its plane: cross two edges, choose the declared orientation and normalize.','face: normalize((v1−v0)×(v2−v0))'),
 ('정점에서는 여러 평면이 만납니다. 날카로운 모서리에 수학적으로 하나뿐인 면 법선이 있다고 말할 수는 없습니다.','Several planes meet at a vertex, so a sharp corner has no unique geometric surface normal.','모서리: 여러 면 / 유일한 기하 법선 없음'),
 ('매끄러운 곡면을 삼각형으로 근사할 때는 그 곡면의 방향을 정점에 저장합니다. 이를 셰이딩 법선으로 사용합니다.','For a smooth surface approximated by triangles, vertex normals approximate its directions for shading.','vertex normal: 매끄러운 표면 방향의 근사'),
 ('육각기둥 옆면은 평평해도 정점 법선을 바깥으로 조금씩 돌리면 밝기가 부드럽게 바뀔 수 있습니다. 위치와 연결은 그대로입니다.','A hexagonal prism can have smoother shading with radial vertex normals while its positions and connections remain unchanged.','같은 육각기둥 / 면 방향 ↔ 정점 방향'),
 ('빛 계산에서 단위 법선과 단위 빛 방향을 내적하면 각도의 코사인을 얻습니다. 길이가 달라지면 방향 외에 크기까지 섞이므로 다시 정규화합니다.','Dotting unit normal and unit light direction gives a cosine; renormalization prevents vector length contaminating that angle.','|n|=|l|=1 → n·l = cosθ'),
 ('앞면 설정과 셰이딩 법선도 같은 정보는 아닙니다. 화면에서 면이 사라졌다면 인덱스 방향과 제거 설정을, 빛이 이상하면 법선과 조명을 구분해 점검합니다.','Front-face configuration differs from shading normals; distinguish winding/culling issues from lighting-direction issues.','면 제거: winding / 밝기: 법선·조명')])
E(8,'밝기를 보간할까, 법선을 보간할까?','interpolation',[
 ('평면 셰이딩은 한 면의 방향으로 조명을 계산합니다. 이웃 면 방향이 다르면 경계에서 밝기 차이가 나타납니다.','Flat shading evaluates a face direction, allowing brightness discontinuities across neighboring faces.','flat: 면 법선으로 계산'),
 ('구로 셰이딩은 정점마다 조명 결과를 구한 다음 그 결과를 면 안으로 보간합니다. 법선 자체를 보간하는 방식과 다릅니다.','Gouraud shading evaluates lighting at vertices and interpolates the resulting values rather than normals.','Gouraud: 정점 조명 결과 → 보간'),
 ('픽셀별 셰이딩은 정점 법선을 보간하고 다시 정규화한 뒤, 면 안쪽 표본마다 조명 식을 계산합니다.','Per-pixel shading interpolates vertex normals, renormalizes them and evaluates lighting at covered samples.','per-pixel: 법선 보간 → normalize → 조명'),
 ('오른쪽 방향과 위쪽 방향을 절반씩 섞으면 영 점 오, 영 점 오가 됩니다. 길이는 약 영 점 칠공칠이므로 단위벡터가 아닙니다.','A half blend of right and up gives(.5,.5), whose length is about.707 rather than one.','(1,0),(0,1) → (.5,.5) / length≈.707'),
 ('다시 정규화하면 두 성분이 약 영 점 칠공칠입니다. 보간한 방향을 밝기에 넣기 전에 이 단계를 거칩니다.','Normalizing produces components about.707; do this before using the interpolated direction in lighting.','normalize(.5,.5) ≈ (.707,.707)'),
 ('노션의 퐁 셰이딩이라는 이름은 이 법선 보간 방식을 가리킵니다. 정반사에 쓰는 퐁 반사 모델과 구별해야 합니다.','The source Phong shading name refers to normal interpolation, distinct from the Phong specular reflection model.','Phong shading ≠ Phong 반사 모델'),
 ('밝기가 매끄러워져도 육각형 실루엣은 여전히 육각형입니다. 법선만으로 실제 표면 위치나 구멍의 모양이 바뀌지는 않습니다.','Smooth brightness does not change a hexagonal silhouette; normals alone do not move the surface or reshape holes.','부드러운 셰이딩 ≠ 실루엣 변경')])
A(9,'둥근 구멍과 평평한 벽을 함께 보기',W,[(580,640)],[
 ('이번에는 빅 워크의 노란 구조물 사이를 걸어갑니다. 넓고 평평한 벽과 둥근 구멍의 가장자리를 동시에 보세요.','Walk between yellow structures in Big Walk, observing broad flat walls and circular opening boundaries.'),
 ('시점이 옮겨지면서 벽의 밝기와 그림자가 바뀌어 보입니다. 면 안의 밝기 변화와 실제 구멍의 윤곽은 서로 다른 단서입니다.','Changing views reveal brightness and shadows; variation within a face differs from the opening outline.'),
 ('다른 캐릭터가 구멍을 통과하면 벽의 두께와 통로가 드러납니다. 표면의 방향을 부드럽게 계산해도 이 통로의 공간은 실제 형태로 남습니다.','A character passing through reveals thickness and passage space, distinct from smooth shading directions.'),
 ('이 장면만 보고 정점 수나 법선 생성 알고리즘을 알 수는 없습니다. 지금의 질문은 같은 거친 형태라도 왜 밝기가 더 매끄러울 수 있느냐입니다.','We cannot infer vertex counts or normal generation here; the question is why fixed coarse geometry can shade more smoothly.'),
 ('그 답은 법선에 있습니다. 다음 계산에서는 정점에 연결된 면을 모두 모아 평균 방향을 만드는 과정을 처음부터 끝까지 보여줍니다.','Normals provide the answer. We next show the complete accumulation of neighboring face directions.'),
 ('평평한 벽에서는 방향을 일정하게, 부드러운 곡면에서는 방향을 연속적으로 만들고 싶습니다. 하지만 두 면을 무조건 평균하면 모서리가 잘못 보일 수 있습니다.','Flat walls and smooth curves need different directions; unconditional averaging can incorrectly shade sharp corners.'),
 ('벽과 구멍의 경계를 다시 보면서, 어떤 곳을 이어서 매끄럽게 만들고 어떤 곳을 분리할지 생각해 보세요.','Revisit wall and opening boundaries and consider which directions should blend and which should remain separate.')],
 '실제 걷기·구멍 통과로 평평한 면 밝기와 둥근 윤곽·두께를 함께 관찰','셰이딩 방향 근사와 실루엣·실제 표면은 구분한다')
E(10,'이웃 면의 법선을 끝까지 합산하기','accumulation',[
 ('법선이 없는 메시에서 단순한 평균 방향을 만들어 보겠습니다. 먼저 모든 정점의 누적 벡터를 영으로 초기화합니다.','Generate simple averaged normals for a mesh without them, starting every vertex accumulator at zero.','1. 모든 vertex sum = (0,0,0)'),
 ('각 삼각형의 두 모서리로 외적을 구합니다. 길이가 거의 영인 퇴화 삼각형은 정규화하지 말고 제외하거나 오류로 기록합니다.','Cross each triangle edges; reject or report nearly-zero degenerate faces before normalization.','2. face cross / zero 검사'),
 ('유효한 면 법선을 단위 길이로 만들고, 그 삼각형의 세 인덱스가 가리키는 정점 누적값에 각각 더합니다.','Normalize a valid face normal and add it to each of the three indexed vertex accumulators.','3. normalize face → 3개 정점에 더하기'),
 ('예제 정점에 오른쪽, 위쪽과 앞쪽 방향이 한 번씩 연결되면 합은 일, 일, 일입니다. 길이 루트 삼으로 나누면 각 성분은 약 영 점 오칠칠입니다.','One right, up and front direction sum to(1,1,1); dividing by square root three gives components about.577.','sum=(1,1,1) / normalize≈(.577,.577,.577)'),
 ('모든 면을 처리한 뒤에 정점마다 합을 정규화합니다. 면 개수로 먼저 나누어도 영이 아닌 벡터의 최종 방향은 같습니다.','After processing every face, normalize each nonzero sum; dividing by face count first preserves the final direction.','4. 모든 면 완료 → normalize sum'),
 ('하지만 고립 정점이나 반대 방향의 합은 영이 될 수 있습니다. 이 경우는 자동 정규화하지 말고 분리, 사용자 법선이나 오류 정책을 선택합니다.','Isolated vertices and canceling directions can produce zero sums; use explicit split, authored-normal or error policies.','sum=0: 분리 / 지정 / 오류 정책'),
 ('이 기본 알고리즘은 면마다 한 표를 줍니다. 날카로운 경계와 삼각분할의 편향은 다음 두 단계에서 따로 해결하겠습니다.','This basic algorithm gives each face one vote; sharp boundaries and triangulation bias need separate treatment.','기본: 면마다 1표 / 한계 별도 처리')])
E(11,'모서리에서 정점을 복제하는 이유','hard-edges',[
 ('상자 꼭짓점 하나에 세 면이 만납니다. 모든 면이 같은 정점 법선을 공유하면 서로 다른 방향이 섞여 밝기 경계가 부드러워집니다.','Three cube faces meet at a corner; sharing one shading normal blends their directions and brightness boundaries.','상자 8개 위치 / 공유 법선은 혼합'),
 ('상자 모양은 그대로인데 둥근 물체처럼 보이는 문제가 생깁니다. 의도한 날카로운 모서리라면 면 사이 법선을 섞지 않아야 합니다.','The cube geometry stays fixed but can shade like a rounded object; intentional hard edges must not blend directions.','날카로운 edge: 법선 혼합 금지'),
 ('그래서 같은 위치의 정점을 면마다 복제합니다. 여덟 위치의 상자를 여섯 면에 네 정점씩, 스물네 레코드로 표현할 수 있습니다.','Duplicate records at equal positions: a cube with eight locations can use six faces times four, or24 records.','같은 위치 / face별 4개 → 6×4=24'),
 ('위쪽 레코드에는 위쪽 법선을, 옆쪽 레코드에는 옆쪽 법선을 저장합니다. 인덱스도 해당 레코드를 가리키게 바꿉니다.','Store the top normal in top-face records and side normals in side records, updating indices accordingly.','위 n=(0,1,0) / 옆 n=(1,0,0)'),
 ('유브이 이음매에서도 위치는 같지만 이미지의 다른 부분을 가리켜야 할 수 있습니다. 그때도 전체 정점 데이터를 분리합니다.','UV seams can require equal positions pointing to different image locations, also requiring separate records.','UV seam: 위치 같아도 UV가 다름'),
 ('양면 잎처럼 반대 법선을 같은 정점에 더하면 합이 영입니다. 앞뒤를 분리하거나 양면 처리와 방향 규칙을 따로 정해야 합니다.','Opposing normals on two-sided leaves cancel to zero; split the sides or define two-sided orientation treatment explicitly.','n + (−n)=0 / 양면 처리 별도'),
 ('정점 복제는 틈을 벌리는 작업이 아닙니다. 좌표가 같아도 속성과 논리적 연결을 나누는 것이며, 편집 도구의 연결 정보는 따로 보존할 수 있습니다.','Duplicating records need not open a physical gap; it separates attributes and logical references while tools can preserve geometric adjacency.','좌표 보존 / 속성·논리 연결 분리')])
E(12,'삼각형 수가 많으면 그 방향이 이길까요?','weighting',[
 ('윗면의 삼각형 두 개와 옆면 두 개가 한 정점에 연결된다고 합시다. 단위 법선을 한 번씩 더하면 윗면 방향에 두 표가 갑니다.','Suppose two top triangles and two side faces meet at a vertex; equal face votes give the top direction two votes.','윗면 2표 / 두 옆면 각각 1표'),
 ('좌표축 방향으로 쓰면 합은 일, 이, 일입니다. 정규화하면 약 영 점 사공팔, 영 점 팔일육, 영 점 사공팔로 위쪽에 치우칩니다.','Axis-aligned votes sum to(1,2,1), normalized to approximately(.408,.816,.408), biased upward.','(1,2,1)/√6 ≈ (.408,.816,.408)'),
 ('같은 사각형의 대각선만 바꾸어도 어떤 꼭짓점이 두 삼각형에 연결되는지가 달라집니다. 원래 표면 모양은 같아도 평균이 바뀔 수 있습니다.','Changing a quad diagonal changes which vertices touch two triangles, potentially altering averages without changing the surface.','대각선 변경 → 면 개수 편향 변경'),
 ('한 방법은 그 정점의 내각을 가중치로 쓰는 것입니다. 사각형 꼭짓점의 구십 도를 둘로 나누어도 합은 구십 도입니다.','Angle weighting uses the corner angle: splitting a quad corner ninety degrees preserves its total ninety.','angle weighting: α1+α2=90°'),
 ('이렇게 각 면 방향에 내각을 곱해 합산한 뒤 정규화합니다. 면적 가중치처럼 다른 정책도 있으니 무엇을 근사하려는지 먼저 정합니다.','Accumulate angle times direction and normalize; other policies such as area weighting approximate different intended surfaces.','sum αf nf → normalize / 정책 선언'),
 ('상자처럼 원래 날카로워야 하는 경우는 가중치만으로 해결하지 않습니다. 먼저 면을 분리하고, 매끄럽게 이을 부분에만 적절한 평균을 사용합니다.','Weighting does not fix intentionally sharp cubes; first separate hard edges, then average only intended smooth regions.','hard edge 분리 → smooth 영역 평균')])
A(13,'평평한 면과 둥근 경계의 역할을 나누기',W,[(640,706)],[
 ('노란 구조물의 다른 구멍으로 이동합니다. 카메라가 벽에 가까워지면서 넓은 평면과 둥근 가장자리의 방향 차이가 잘 보입니다.','Move to another opening in the yellow structure, observing broad planes and curved boundaries up close.'),
 ('구멍으로 캐릭터를 바라보면 바깥 윤곽이 화면에서 분명한 경계가 됩니다. 면 안의 밝기를 부드럽게 만든다고 그 경계까지 사라지지는 않습니다.','Viewing a character through the opening produces a clear silhouette boundary that smooth shading cannot remove.'),
 ('표면이 여러 방향으로 이어지는 곳과 날카롭게 꺾이는 곳을 나누어 생각하세요. 실제 모델의 레코드 수는 여기서 측정하지 않습니다.','Distinguish gradual surface directions from sharp joins without measuring this model vertex-record count.'),
 ('앞의 상자 계산에서는 같은 위치라도 위쪽과 옆쪽 방향을 따로 저장했습니다. 반대로 매끄러운 곡면의 내부에서는 이웃 방향을 연결했습니다.','Our cube example split directions at equal positions, whereas intended smooth interiors blend neighboring directions.'),
 ('이 선택은 빛의 변화와 형태가 어울리게 만드는 일입니다. 무조건 정점을 적게 저장하거나 무조건 평균하는 것이 목표는 아닙니다.','The choice aligns shading with shape, rather than universally minimizing records or averaging every join.'),
 ('이제 같은 물체를 가로로 늘렸다고 생각해 보겠습니다. 정점 위치가 바뀌면 법선도 옮겨야 하지만 같은 계산을 그대로 쓰면 틀릴 수 있습니다.','Now imagine stretching a shape horizontally: normal directions must change, but applying the position transform directly can fail.'),
 ('다음 예제에서는 접선과 법선의 내적을 직접 계산합니다. 벽 화면의 밝기를 역산하는 대신, 우리가 정한 수치로 수직 조건을 검증하겠습니다.','Next we verify perpendicularity with explicitly defined tangent and normal values, without reverse-engineering brightness from pixels.')],
 '실제 구멍 사이 이동에서 노란 평면·곡선 윤곽·방향 변화','법선 공유 정책은 의도한 표면에 맞춰 선택하고 변환 뒤 수직 조건을 검증한다')
E(14,'법선은 접선과 수직이어야 합니다','normal-matrix',[
 ('법선 변환에서 지켜야 할 조건은 접선과 수직이라는 것입니다. 열벡터 규약으로 원래 접선을 티, 법선을 엔이라고 쓰겠습니다.','Normals must remain perpendicular to tangents. Use column vectors t and n with n transpose t equal zero.','열벡터 / nᵀt=0'),
 ('위치와 접선에 적용하는 가역 선형 행렬을 엠이라고 합시다. 평행이동은 접선이나 방향 벡터에 더하지 않습니다.','Let M be the invertible linear transform of positions and tangents; do not add translation to directions.','접선 t′=Mt / 평행이동 제외'),
 ('법선에는 엠의 역전치를 적용합니다. 역행렬을 구한 뒤 전치해도, 전치한 뒤 역행렬을 구해도 같습니다.','Transform normals with the inverse transpose M inverse transpose; inverse and transpose commute in this expression.','n′=M⁻ᵀn / (M⁻¹)ᵀ=(Mᵀ)⁻¹'),
 ('새 법선과 새 접선을 내적하면 가운데 역행렬과 원래 행렬이 상쇄됩니다. 결과는 원래 내적 영이므로 수직 관계가 유지됩니다.','The transformed dot product cancels M inverse M and equals the original zero dot product, preserving perpendicularity.','(M⁻ᵀn)ᵀ(Mt)=nᵀt=0'),
 ('회전 같은 정규직교 행렬은 역전치가 원래 행렬과 같습니다. 양의 균일 확대도 방향만 보면 같지만 마지막 단위 길이는 맞춥니다.','For orthogonal rotations the inverse transpose equals M; positive uniform scale preserves the normalized direction.','회전: M⁻ᵀ=M / 균일 scale: normalize'),
 ('비균일 확대나 기울임에서는 역전치 후 정규화합니다. 어떤 축을 영으로 만드는 특이 행렬은 역행렬이 없으므로 이 공식을 그대로 쓸 수 없습니다.','Nonuniform scale and shear require inverse transpose then normalization; singular zero-axis transforms have no inverse.','비균일·shear → inverse transpose / singular 별도'),
 ('반사처럼 방향을 뒤집는 변환은 앞면 규약과도 함께 확인합니다. 여기서는 음의 확대가 없는 예제로 수직 조건에 집중하겠습니다.','Orientation-reversing transforms also require consistent front-face handling; our worked example uses positive scales.','반사: winding 함께 점검 / 예제는 양의 scale')])
E(15,'가로 두 배 확대를 직접 검산하기','normal-example',[
 ('접선을 일, 마이너스 일로, 법선을 일, 일로 정합니다. 내적은 일 빼기 일, 영입니다. 먼저 수직이라는 조건을 확인했습니다.','Choose tangent(1,−1) and normal(1,1): their dot product1−1 is zero.','t=(1,−1) / n=(1,1) → dot0'),
 ('가로만 두 배 늘리는 행렬을 적용하면 새 접선은 이, 마이너스 일입니다. 물체 표면의 기울기가 달라집니다.','Scaling x by two produces tangent(2,−1), changing the surface slope.','M=diag(2,1) / t′=(2,−1)'),
 ('법선에도 같은 행렬을 쓰면 이, 일이 됩니다. 새 접선과 내적은 사 빼기 일, 삼이므로 수직이 아닙니다.','Applying M to the normal gives(2,1), whose dot with the new tangent is4−1=3 rather than zero.','잘못된 Mn=(2,1) / dot=3'),
 ('이 잘못된 벡터를 루트 오로 나누어 정규화해도 내적은 삼 나누기 루트 오입니다. 길이만 고쳐서 방향 오류를 없앨 수는 없습니다.','Normalizing the wrong vector by square root five leaves dot3 divided by square root five, so its direction remains wrong.','normalize만: dot=3/√5 ≠0'),
 ('역전치의 가로 성분은 이분의 일입니다. 법선은 영 점 오, 일이 되고, 새 접선과 내적은 일 빼기 일, 영입니다.','The inverse transpose scales x by one half, giving(.5,1) with transformed dot1−1=0.','M⁻ᵀn=(.5,1) / dot=0'),
 ('마지막으로 단위 길이를 만들면 약 영 점 사사칠, 영 점 팔구사입니다. 순서는 수직인 방향을 먼저 만든 뒤 길이를 맞추는 것입니다.','Final normalization gives approximately(.447,.894): first correct the perpendicular direction, then normalize.','normalize(.5,1) ≈ (.447,.894)'),
 ('이차원 단면의 계산이지만 삼차원에서도 같은 수직 조건을 사용합니다. 조명 코드에서는 위치 변환의 선형 부분과 법선 행렬을 분리해 기록하세요.','The same perpendicularity condition extends to3D; distinguish the linear position transform from the normal matrix in lighting code.','3D도 같은 조건 / position matrix ↔ normal matrix')])
A(16,'벽돌 무늬와 창문 격자는 어디에서 올까요?',S,[(135,165),(195,209)],[
 ('선셋 오버드라이브의 다른 지붕과 벽을 보겠습니다. 사각 창문이 반복되는 면과 경사 지붕이 한 화면에 나타납니다.','Inspect another Sunset Overdrive roof and wall, where repeated rectangular windows meet a sloped roof.'),
 ('먼저 큰 형태의 윤곽을 보고 그다음 표면 안의 반복 무늬를 보세요. 같은 면 안에 많은 세부가 있어도 그만큼 정점이 있다고 말할 수는 없습니다.','Observe the large outline first, then internal patterns; abundant detail does not imply one vertex per detail.'),
 ('다음 가까운 벽에서는 벽돌처럼 반복되는 무늬와 격자가 보입니다. 이 세부를 이미지의 위치와 표면의 위치를 연결하는 문제로 생각해 봅시다.','The closer wall shows brick-like patterns and grids, motivating correspondence between image locations and surface locations.'),
 ('게임의 실제 텍스처 파일이나 주소 모드를 확인한 것은 아닙니다. 지금 화면은 왜 기하와 별도로 무늬 좌표가 필요한지 보여주는 출발점입니다.','We have not inspected game texture files or address modes; the visible patterns motivate separate pattern coordinates.'),
 ('우리 도식에서는 네 정점의 작은 판에 직접 만든 색과 숫자 무늬를 붙입니다. 같은 판을 유지하면서 어떤 이미지 부분을 사용할지 바꾸어 보겠습니다.','Our diagram applies an original labeled texture to a four-vertex plate and changes its image mapping while keeping the plate fixed.')],
 '지붕 이동·벽 접근에서 반복 창문·벽돌형 무늬와 큰 실루엣','표면의 형태와 이미지 좌표의 대응은 별도 데이터이며 게임 내부 방식은 단정하지 않는다')
E(17,'픽셀과 텍셀, 위치와 UV','uv-basics',[
 ('텍스처는 표면의 색이나 다른 속성을 담는 이미지입니다. 그 이미지의 한 칸을 텍셀이라고 부르고, 최종 화면의 픽셀과 구분합니다.','A texture stores surface color or other attributes; its texels differ from pixels in the final image.','texture texel ≠ 화면 pixel'),
 ('화면에 크게 보이면 한 텍셀이 여러 픽셀에 영향을 줄 수 있습니다. 멀리 보이면 여러 텍셀이 한 화면 표본에 기여할 수도 있습니다.','One texel may affect multiple screen pixels when magnified, while multiple texels may contribute to a smaller screen footprint.','크기·거리·필터 → texel/pixel 대응 변화'),
 ('유는 이미지 가로, 브이는 세로 좌표 이름입니다. 여기서는 왼쪽 위를 영 영, 오른쪽 아래를 일 일로 정하고 브이를 아래쪽으로 증가시킵니다.','Here u runs right and v down, with top-left(0,0) and bottom-right(1,1).','이번 예제: top-left(0,0), v↓'),
 ('이 원점은 예제의 명시적 약속입니다. 파일의 행 순서와 도구, 변환에 따라 달라질 수 있으므로 API 이름만으로 뒤집힘을 결정하지 않습니다.','This is an explicit example convention; file row order, tools and transforms matter, so API names alone do not decide orientation.','원점·행 순서·변환을 명시'),
 ('이미지가 팔 곱하기 팔이든 더 크든 전체 영역은 영에서 일로 표현할 수 있습니다. 이 정규화 좌표는 정점의 삼차원 위치와 독립적입니다.','Normalized0-to1 coordinates cover an image regardless of whether it is8 by8 or larger, independently of3D positions.','정규화 UV / 3D 위치와 별도'),
 ('평면, 원통이나 구면 매핑은 이 대응을 만드는 방법입니다. 편집 도구로 지정하거나 절차적으로 계산해 정점에 유브이를 저장할 수 있습니다.','Planar, cylindrical and spherical mapping construct the correspondence, authored in tools or computed procedurally at vertices.','매핑 방법 → 정점 UV'),
 ('면 안에서는 정점의 유브이를 보간해 조회 위치를 얻습니다. 앞 강의의 원근 보정은 유지하고, 이번에는 어떤 좌표를 보간할지에 집중합니다.','Interpolate vertex UVs inside faces, retaining the earlier perspective-correct treatment while focusing on the data being interpolated.','정점 UV → 면 내부 UV → texture 조회')])
E(18,'같은 판에 전체·확대·회전 무늬 붙이기','uv-mapping',[
 ('천에 핀을 꽂는다고 생각해 보세요. 판의 네 정점에 이미지의 어느 위치를 연결할지 정하면 내부에서는 그 대응을 이어 갑니다.','Imagine pinning cloth to four plate vertices; their selected image locations define the interior correspondence.','판 정점 ↔ 이미지의 UV 핀'),
 ('네 모서리에 영 영, 일 영, 일 일, 영 일을 차례로 주면 이미지 전체가 판을 덮습니다. 판의 위치 데이터는 바꾸지 않습니다.','Assign(0,0),(1,0),(1,1),(0,1) in order to cover the plate with the entire image without moving vertices.','전체: (0,0),(1,0),(1,1),(0,1)'),
 ('유와 브이를 영 점 이오에서 영 점 칠오 사이로 줄이면 가운데 절반 영역을 같은 판에 늘려 붙입니다.','Restrict both coordinates to.25 through.75, stretching the central half-width and half-height over the plate.','crop: [.25,.75]² → 같은 판'),
 ('유브이 핀을 한 모서리씩 순환하면 무늬 방향이 회전합니다. 삼차원 판을 회전한 것이 아니라 이미지와 정점의 연결을 바꾼 것입니다.','Cycling the UV corners rotates the pattern correspondence rather than rotating the3D plate.','UV 핀 순환 → 무늬 회전'),
 ('유를 일 빼기 유로 바꾸면 좌우가 뒤집힙니다. 이 변환도 표면 위치와 면의 앞뒤 순서는 그대로 두고 무늬 좌표만 바꿉니다.','Using1−u flips the image horizontally while preserving geometry positions and face winding.','u′=1−u → 무늬 좌우 반전'),
 ('사각형만 가능한 것은 아닙니다. 여러 삼각형의 각 정점에 다른 유브이를 주면 같은 메시에서도 무늬의 늘어남과 배치를 바꿀 수 있습니다.','UVs also apply to multi-triangle meshes, changing placement and stretching without changing their geometry.','같은 메시 / 다른 UV 배치'),
 ('늘어나는 천의 비유는 대응을 돕는 설명입니다. 실제 텍스처가 물리적인 천처럼 움직이거나 모든 면적을 그대로 보존한다는 뜻은 아닙니다.','The cloth analogy explains correspondence, not physical cloth simulation or guaranteed area preservation.','대응 비유 / 면적·길이 왜곡 가능')])
A(19,'무늬는 면을 따라가고 윤곽은 남습니다',S,[(720,750),(588,603),(400,408)],[
 ('붉은 벽면 가까이를 이동하는 장면입니다. 곡선으로 이어지는 큰 형태 안에 글자와 표면 무늬가 놓여 있습니다.','Move near a red facade where markings sit within a larger curved form.'),
 ('카메라가 바뀌면 벽의 무늬가 화면에서 기울어지고 크기도 달라 보입니다. 이미지 좌표와 최종 화면 좌표가 같지 않다는 점을 떠올려 보세요.','View changes alter the apparent pattern orientation and size, reminding us that texture and screen coordinates differ.'),
 ('다음 경사 지붕에는 길게 반복되는 줄과 유리창이 보입니다. 마지막 컨테이너에서는 윗면과 옆면의 패널 방향이 다르게 보입니다.','The next roof shows repeated strips and glass panes; the container then reveals differently oriented top and side panels.'),
 ('이 세 장면의 실제 유브이를 읽은 것은 아닙니다. 보이는 무늬와 표면의 대응을 질문으로 삼아, 직접 정한 유브이 예제를 연결합니다.','We do not read these game UVs; the observed pattern-surface relationships motivate our explicitly authored examples.'),
 ('앞 도식처럼 같은 판에 전체 이미지나 일부 이미지를 붙일 수 있습니다. 그다음은 유브이가 영에서 일 범위를 벗어났을 때의 규칙입니다.','As with our plate, a surface can map a whole image or a portion; next consider coordinates outside0 through1.'),
 ('무늬가 반복돼 보인다는 이유만으로 반복 주소 모드라고 단정하지 않습니다. 별도 기하나 이미지 안의 반복으로도 비슷한 결과를 만들 수 있습니다.','Repeated appearance alone does not prove repeat addressing: separate geometry or repeated content in an image can look similar.')],
 '실제 곡선 외벽→경사 줄무늬 지붕→컨테이너의 윗면·옆면 패턴','무늬와 표면 대응을 관찰하되 UV·주소 모드 구현은 화면에서 추정하지 않는다')
E(20,'범위 밖의 UV를 조회하는 규칙','addressing',[
 ('유브이는 영에서 일 바깥 값도 가질 수 있습니다. 같은 정점과 같은 유브이에 반복이나 클램프 규칙을 다르게 적용해 보겠습니다.','UVs can exceed0 through1. Keep vertices and UVs identical while comparing repeat and clamp addressing.','동일한 메시·UV / 다른 조회 규칙'),
 ('반복은 정수 타일을 넘으면 같은 이미지를 다시 사용합니다. 음수에서도 일관되게 하려면 유에서 유의 바닥값을 뺍니다.','Repeat reuses the image across integer tiles; use u minus floor u consistently for negative coordinates.','repeat(u)=u−floor(u)'),
 ('일 점 이오는 바닥값 일이므로 영 점 이오가 됩니다. 마이너스 영 점 칠오의 바닥값은 마이너스 일이므로 역시 영 점 이오입니다.','For1.25 floor is1, giving.25; for−.75 floor is−1, also giving.25.','1.25→.25 / −.75→.25'),
 ('영 쪽으로 정수를 잘라내면 음수에서 결과가 다릅니다. 반복 구현에 사용할 함수가 바닥값인지 절삭인지 구분해야 합니다.','Truncating toward zero differs for negative inputs; distinguish floor from truncation when implementing repeat.','floor(−.75)=−1 / trunc=0'),
 ('클램프는 영보다 작으면 영, 일보다 크면 일로 제한합니다. 바깥에는 이미지 가장자리의 값이 이어집니다.','Clamp limits below-zero to0 and above-one to1, extending edge values outward.','clamp(u)=min(1,max(0,u))'),
 ('미러 반복은 타일마다 방향을 번갈아 뒤집습니다. 유와 브이는 서로 다른 주소 모드를 사용할 수도 있습니다.','Mirrored repeat alternates tile orientation, and u and v may use separate address modes.','mirror: 교대 반전 / u·v 모드 독립'),
 ('이것은 주소 선택 규칙입니다. 이웃 텍셀을 어떻게 섞는 필터링과는 별도입니다. 경계의 실제 필터 결과는 필터와 규약까지 함께 정의해야 합니다.','Addressing selects coordinates independently of filtering, which combines texels; exact edge behavior also depends on those sampling conventions.','주소 모드 ≠ 필터 / 경계 규약 별도')])
E(21,'정점에서 먼저 반복하면 정보가 사라집니다','repeat-order',[
 ('한 변의 유를 영에서 이까지 주면 면을 따라 이미지가 두 번 반복되어야 합니다. 두 끝의 정점 좌표는 영과 이를 그대로 저장합니다.','A0-to2 u edge should display two repeats; store the unmodified endpoint coordinates0 and2.','정점 UV: 0 → 2'),
 ('면을 따라 사분의 일 지점에서 보간한 유는 영 점 오입니다. 사분의 삼 지점에서는 일 점 오입니다.','Interpolation gives.5 at one quarter and1.5 at three quarters along the edge.','t=.25→u=.5 / t=.75→u=1.5'),
 ('각 위치에서 조회할 때 반복을 적용하면 두 지점 모두 영 점 오를 읽습니다. 다른 타일의 같은 상대 위치에 해당합니다.','Applying repeat at lookup maps both positions to.5, the same relative location in different tiles.','lookup: .5→.5 / 1.5→.5'),
 ('반대로 정점에서 영과 이를 먼저 반복하면 둘 다 영이 됩니다. 그 영을 보간하면 면 안의 모든 유도 영이 됩니다.','Wrapping endpoints0 and2 first turns both into zero, so interpolation loses the entire0-to2 variation.','잘못된 순서: endpoints 0,0 → 모두0'),
 ('영에서 이라는 범위가 사라져 두 번 반복할 정보도 사라졌습니다. 먼저 보간하고 마지막 텍스처 조회에서 주소 모드를 적용해야 합니다.','The two-repeat span is lost; interpolate first and apply addressing only at texture lookup.','보간 → 주소 처리 → 텍스처 조회'),
 ('원근 장면에서는 앞에서 배운 원근 보정 유브이 보간을 이 앞단에 사용합니다. 원근 보정과 반복 순서는 서로 다른 문제이므로 둘 다 지킵니다.','Use the preceding perspective-correct UV interpolation before this step; perspective correction and repeat order are separate requirements.','원근 보정 보간 / 그 뒤 주소 처리')])
A(22,'윤곽·방향·무늬를 나누어 다시 관찰하기',S,[(615,650),(566,570),(374,386)],[
 ('마지막으로 선셋 오버드라이브의 계단과 건물 사이를 이동합니다. 가까운 면과 멀리 보이는 면의 경계부터 찾아보세요.','Move among stairs and buildings in Sunset Overdrive, first identifying near and distant surface boundaries.'),
 ('옥상과 건물 옆면이 나타나면 형태를 이루는 면, 그 면의 빛과 표면 무늬를 세 질문으로 나누어 봅니다.','As roofs and building sides appear, separate three questions: geometry, lighting direction and surface pattern.'),
 ('다음 짧은 벽 장면에서는 창문이 반복되고, 뒤의 지붕에서는 사각 패널이 이어집니다. 반복 개수만으로 정점 개수나 주소 모드를 알 수는 없습니다.','The following wall has repeated windows and the roof repeated panels, which do not reveal vertex counts or address modes.'),
 ('우리 계산에서는 인덱스로 정점 레코드를 연결했고 법선으로 수직 방향을, 유브이로 이미지 대응을 저장했습니다. 이 역할은 서로 바꿔 쓸 수 없습니다.','Our calculations used indices for vertex records, normals for perpendicular directions and UVs for image correspondence; their roles differ.'),
 ('여러분이 모델을 확인할 때도 먼저 실루엣, 다음 법선 경계, 마지막 무늬의 배치를 따로 검사해 보세요. 이상한 결과의 원인을 좁히기 쉬워집니다.','When checking a model, inspect silhouettes, normal boundaries and pattern placement separately to narrow the source of an error.'),
 ('이제 직접 정한 작은 메시 문제로 답을 확인하겠습니다. 게임의 내부 수치를 맞히는 문제가 아니라 저장과 계산의 순서를 검산하는 연습입니다.','Finish with explicitly defined mesh exercises that verify storage and calculation order rather than guessing game internals.')],
 '실제 계단·옥상 이동→반복 창문 벽→지붕 패널의 형태와 표면','정점·법선·UV의 역할을 구분한 모델 검수 질문으로 정리')
E(23,'세 가지 질문으로 계산을 검산하기','practice',[
 ('첫 문제입니다. 삼십이 바이트 정점 네 개와 이 바이트 인덱스 여섯 개라면 모두 백사십 바이트입니다. 정점 개수와 인덱스 개수를 섞지 않았는지 확인하세요.','First exercise: four32-byte vertices and six2-byte indices total140 bytes; distinguish record count from index count.','4×32+6×2=140B'),
 ('두 번째는 상자 모서리입니다. 같은 위치의 위쪽과 옆쪽 법선을 분리하려면 정점 레코드를 복제하고 해당 면의 인덱스를 바꿉니다.','Second, split a cube corner shading direction by duplicating records and updating the corresponding face indices.','같은 좌표 / 서로 다른 normal·index'),
 ('접선 이, 마이너스 일과 법선 영 점 오, 일을 내적하면 영입니다. 비균일 확대 뒤에는 이 수직 조건과 단위 길이를 모두 검사합니다.','The transformed tangent(2,−1) and normal(.5,1) have zero dot product; verify perpendicularity and unit length after nonuniform scale.','t′·n′=0 / normalize 이후 |n′|=1'),
 ('세 번째는 영에서 이까지의 유브이입니다. 먼저 보간하고 조회할 때 반복하며, 음수 좌표에서는 바닥값을 사용합니다.','Third, preserve0-to2 UVs for interpolation, repeat at lookup and use floor for negative coordinates.','UV 보간 → repeat(u)=u−floor(u)'),
 ('형태를 연결하는 인덱스, 빛 방향을 근사하는 법선, 무늬를 연결하는 유브이를 구분했습니다. 위치가 같아도 모든 속성을 공유해야 하는 것은 아닙니다.','We separated topology indices, shading normals and UV correspondence; equal positions need not share all attributes.','index / normal / UV는 별도 역할'),
 ('다음 강의에서는 이 법선을 실제 조명 식에 넣고 광원과 재질의 영향을 계산하겠습니다. 오늘 만든 방향과 표면 정보가 그 계산의 입력이 됩니다.','Next we evaluate lighting with these normals and examine lights and materials; today surface data supplies those inputs.','다음: 법선 → 광원·재질 계산')])
data=dict(slug=slug,chapter=10,part=5,totalParts=8,renderModule='mesh_uv',sourceDependencies=['manim/projects/game-math-part2-full-series/lesson.py','manim/projects/game-math-part2-full-series/rendering_light.py'],sourceSections=['10.4','10.4.1','10.4.2','10.5'],scenes=scenes,
 contract={'memory':'Whole quad:6×32=192 versus4×32+6×2=140; source local one-vertex-six-use example32+6×2=44 is independently retained, not confused with total mesh memory.','mesh':'Clockwise source convention declared as a selectable front-face contract; diagrams use consistent explicitly chosen winding. Same positions can require distinct normals/UVs. Adjacency is implicit, not O(1) in plain indices.','normal':'Face cross from ordered edges; unit-face equal-weight accumulation then nonzero normalization. Degenerate/isolated/opposing cases explicit, hard seams detached before averaging. Angle-weighting avoids arbitrary quad diagonal votes; no claim of universal optimal normals.','matrix':'Column vectors and nonsingular linear M: normalize(M^-T n). Positive scale examplet(1,-1),n(1,1),Mdiag2/1; naive dot3 remains wrong after normalization; correct(.5,1)dot0. Singular and reflection conventions explicit.','uv':'Explicit top-left v-down illustration; normalized UV independent of texture resolution. Interpolate unmodified UV using applicable perspective correction before repeat floor/clamp/mirror lookup; filtering separate.','gameEvidence':'Actual existing-game real-time shots illustrate visible surface/outline/pattern; never assert proprietary topology, vertex counts, normals, UVs, address modes or CSG from rendered pixels.'},
 coverage={'10.4':['02','03','05'],'10.4.1':['04','05','06','11','23'],'10.4.2':['07','08','09','10','11','12','13','14','15','23'],'10.5':['16','17','18','19','20','21','22','23']},
 gameCandidates={'reviewedAt':'2026-10-09','selected':[{'game':'Sunset Overdrive','sourceId':S,'reason':'Fresh title and recording after recent-use searches; directly reviewed roof planes, vents, curved facade and repeated surface patterns, with recorder free-use statement.'},{'game':'Big Walk','sourceId':W,'reason':'Already used in rendering-light; newly inspected nonoverlapping green-grid/yellow-opening intervals support explicit surface-versus-shading questions. Not represented as a fresh title.'}], 'rejected':[{'game':'Half-Life: Alyx official gameplay','reason':'Official source and publisher policy checked; all coarse sheets inspected, dark combat and rapidly changing subjects unsuitable for sustained surface instruction.'},{'game':'Superflight / Subnautica 2','reason':'Already used in recent lessons; do not automatically recycle those titles or clips.'},{'game':'Sunset combat, explosions, highway and long skyline','reason':'Exclude effects-obscured or unrelated intervals from actual-footage quota.'},{'game':'Big Walk dialogue-heavy red deck/long night intervals','reason':'Exclude chat-focused/static and poorly readable surfaces. Previously used rendering-light intervals remain reserved.'}], 'historyReview':'Full project/source search plus rendering-light actual timeline checked; all new Big Walk cuts exclude its9 prior intervals. Native Studio UV query found legacyDirectX sampler tutorial and its full transcript was reviewed. Current source and fine pixels precede this narration.'},
 timingReview={'status':'awaiting measured narration','episodeBoundaryIfLong':'Finish normal construction/transform exercise before independent UV episode; never cut the accumulation algorithm. All10.4–10.5 claims remain in coverage.','maximumPlannedSourceSeconds':sum(s.get('maxSeconds',0) for s in scenes)})
assert len(scenes)==23 and sum(s['kind']=='actual' for s in scenes)==7
p=B/'lessons'/f'{slug}.json'; assert not p.exists(),'Resume saved work rather than overwrite it'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(slug=slug,scenes=len(scenes),paragraphs=sum(len(s['ko']) for s in scenes),koCharacters=sum(len(x) for s in scenes for x in s['ko']),actualCapacitySeconds=data['timingReview']['maximumPlannedSourceSeconds']),ensure_ascii=False))
