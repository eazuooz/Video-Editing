"""Original complete10.2 lecture after full overlap and actual footage review."""
from pathlib import Path
import json
B=Path(__file__).parent;slug='game-math-camera-frustum';scenes=[]
S='8RZ1nPWzWtg';T='FRfnXAIbA-M'
def E(i,title,mode,rows):
 assert all(len(x)==3 for x in rows)
 scenes.append(dict(id=f'{i:02}',title=title,kind='explanation',mode=mode,ko=[x[0] for x in rows],en=[x[1] for x in rows],beats=[x[2] for x in rows]))
def A(i,title,source,segments,rows,focus,claim):
 assert all(len(x)==2 for x in rows)
 scenes.append(dict(id=f'{i:02}',title=title,kind='actual',sourceId=source,sourceSegments=[{'in':a,'maxSeconds':z-a} for a,z in segments],**{'in':segments[0][0]},maxSeconds=sum(z-a for a,z in segments),ko=[x[0] for x in rows],en=[x[1] for x in rows],focus=focus,claim=claim))
E(1,'카메라를 바꾸는 네 가지 질문','overview',[
 ('같은 세계를 보고 있는데, 카메라를 옮기는 것과 줌을 바꾸는 것은 왜 다를까요?','Why do moving a camera and changing its zoom give different views of the same world?','위치·방향 / 시야각 / 출력 창'),
 ('먼저 실제 분할 화면을 보며 카메라와 출력 창을 나누고, 픽셀 비율을 계산하겠습니다.','First, real split-screen gameplay will help separate cameras from output windows, followed by a pixel-aspect calculation.','실제 두 화면 → 출력 창·픽셀'),
 ('이어서 시야각과 줌을 숫자로 연결하고, 카메라를 앞으로 옮기는 경우와 비교합니다.','Then we connect field of view with zoom numerically and compare that with moving the camera forward.','시야각·줌 → 이동과 비교'),
 ('마지막에는 직교 투영과 분할 화면 예제를 풀어, 어떤 값을 바꿔야 할지 직접 판단해 보겠습니다.','Finally, orthographic projection and a split-screen exercise will show which parameters to change.','직교 상자 → 분할 화면 실습')])
A(2,'같은 게임의 두 화면을 따로 보기',S,[(30,63)],[
 ('스플릿 픽션에서는 두 플레이어의 화면이 가운데를 경계로 나뉘어 있습니다. 왼쪽과 오른쪽의 캐릭터를 각각 따라가 보세요.','Split Fiction divides the two players at a central boundary. Follow each character in its own view.'),
 ('캐릭터가 다른 곳을 향하면 각 화면의 배경과 가려지는 물체도 달라집니다. 같은 장면 전체를 똑같이 잘라 붙인 모습과는 다릅니다.','Different directions produce different backgrounds and occlusion; these are more than identical pieces of one picture.'),
 ('여기서 카메라는 무엇을 볼지 정하고, 출력 창은 그 결과를 화면의 어느 영역에 놓을지 정합니다.','The camera determines the view; the output window determines where that result goes.'),
 ('이 게임의 내부 설정값을 추측하는 대신, 두 역할을 분리한 원래 도식으로 계산해 보겠습니다.','We will calculate with our own defined diagram rather than infer this game’s internal settings.')],
 '가운데 경계와 각 플레이어를 따르는 별도 실제 시점','카메라의 관찰과 출력 창의 배치는 구별한다')
E(3,'그림을 저장할 곳과 놓을 영역','output',[
 ('렌더 타깃은 렌더링 결과를 기록할 저장소입니다. 화면에 표시할 버퍼일 수도 있고, 다른 계산에서 읽을 텍스처일 수도 있습니다.','A render target stores rendering results, either in a display buffer or a texture used by another calculation.','렌더 타깃 = 결과 저장소'),
 ('출력 창은 그 저장소 위에서 사용할 직사각형입니다. 오늘은 왼쪽 위가 원점이고, 오른쪽과 아래로 픽셀 좌표가 증가한다고 정하겠습니다.','Our output rectangle uses a top-left origin with pixel coordinates increasing rightward and downward.','왼쪽 위 원점 / 오른쪽+x / 아래+y'),
 ('창의 왼쪽 위 위치와 가로, 세로 크기를 따로 저장합니다. 예를 들어 가로 천구백이십, 세로 천팔십 화면을 세로로 나누어 봅시다.','Store the rectangle’s position and width and height separately. Split a1920-by1080 image vertically.','전체1920×1080 / 위치와 크기'),
 ('왼쪽 창은 영, 영에서 시작해 가로 구백육십, 세로 천팔십입니다. 오른쪽 창은 구백육십, 영에서 시작하고 크기는 같습니다.','The left window begins at(0,0) with size960 by1080; the right begins at(960,0) with the same size.','왼쪽(0,0;960,1080) / 오른쪽(960,0;960,1080)'),
 ('왼쪽 창의 마지막 정수 열은 구백오십구입니다. 위치에 크기를 더한 구백육십은 다음 경계라는 점을 구분하세요.','The left window’s last integer column is959; position plus width gives the next boundary at960.','열0…959 / 다음 경계960'),
 ('같은 카메라 결과를 두 창에 표시할 수도 있고, 서로 다른 카메라 결과를 각 창에 놓을 수도 있습니다. 저장소와 관찰 방법은 일대일로 묶인 개념이 아닙니다.','One camera result may appear in two windows, or different camera results may occupy them. Storage and viewing are separate choices.','한 결과→두 창 / 두 카메라→각 창'),
 ('그림자 맵이나 게임 속 모니터도 결과를 텍스처에 저장한다는 관점으로 이해할 수 있습니다. 실제 구현과 픽셀 변환 순서는 다음 강의에서 연결하겠습니다.','Shadow maps and in-world monitors can store results in textures. Implementation and the full pixel transformation come in the next lecture.','화면 외부 텍스처도 렌더 타깃')])
E(4,'화면 비율과 픽셀 비율을 나누기','pixel-aspect',[
 ('가로 천구백이십, 세로 천팔십 영상의 화면 비율은 십육 대 구입니다. 하지만 그 안의 픽셀 한 칸이 십육 대 구라는 뜻은 아닙니다.','A1920-by1080 image has aspect16:9; an individual pixel is not16:9.','영상16:9 ≠ 픽셀16:9'),
 ('표시 영역도 십육 대 구이고 해상도도 십육 대 구라면, 픽셀 한 칸의 물리적 가로와 세로는 같습니다. 픽셀 비율은 일 대 일입니다.','If display and resolution both have aspect16:9, a physical pixel has equal width and height:1:1.','(16/9)×(1080/1920)=1'),
 ('계산은 표시 영역의 가로 세로 비에, 해상도의 세로 가로 비를 곱합니다. 오늘 비율의 순서는 항상 너비 나누기 높이로 통일하겠습니다.','Multiply physical display width-to-height by resolution height-to-width; all aspect ratios here use width divided by height.','픽셀비=(표시너비/높이)×(세로픽셀/가로픽셀)'),
 ('반대로 픽셀 배열은 사 대 삼인데 물리적으로 십육 대 구 전체에 늘려 표시한다면, 픽셀의 너비 높이 비는 삼 분의 사입니다.','A4:3 pixel array stretched across a16:9 physical area gives physical pixel aspect4/3.','(16/9)×(3/4)=4/3'),
 ('정사각형 픽셀을 가정해 그린 원도 이렇게 표시하면 가로로 늘어납니다. 화면을 늘린 문제를 카메라 회전이나 물체 크기로 고치면 다른 부분까지 틀어집니다.','A circle drawn assuming square pixels becomes horizontally stretched. Fixing that with camera rotation or object scale breaks other relationships.','표시 단계의 늘어남 → 원이 타원'),
 ('출력 창을 오른쪽으로 옮기거나 반으로 나누어도 픽셀 자체의 물리적 비율이 바뀌지는 않습니다. 다만 창의 가로 세로 비는 바뀝니다.','Moving or splitting a window does not change physical pixel aspect, although the rectangle’s aspect changes.','창 위치·크기 / 픽셀 자체는 별도'),
 ('화면 밖 비트맵은 보통 정사각형 픽셀로 다룹니다. 아나모픽처럼 나중에 늘릴 계획이 있다면, 저장한 모양과 최종 표시 약속을 함께 기록해야 합니다.','Off-screen bitmaps commonly assume square pixels; an anamorphic plan must record the later display stretch.','저장 비트맵 → 명시한 최종 표시'),
 ('자료에 나온 천백오십삼 곱하기 칠백이십은 정확한 십육 대 십이 아닙니다. 정확한 값은 천백오십이 곱하기 칠백이십입니다. 숫자 목록보다 비율을 직접 나눠 확인하세요.','The source’s1153-by720 is not exactly16:10;1152-by720 is. Verify ratios rather than memorize resolution lists.','1152/720=16/10 / 원문1153 교정')])
A(5,'건물의 모양과 화면의 움직임',T,[(175,246)],[
 ('타운스케이퍼에서는 물 위의 작은 건물을 바라보다가, 건물 가까이로 화면이 바뀝니다. 먼저 지붕의 꼭짓점과 창문을 기준점으로 골라 보세요.','Townscaper moves from a small waterside building to a closer view. Choose a roof corner and window as landmarks.'),
 ('이어 시점이 돌아가면 처음에 보이지 않던 옆면과 계단이 나타납니다. 모양이 바뀌어 보인다고 해서 픽셀 자체의 비율이 바뀐 것은 아닙니다.','Orbiting reveals sides and stairs. A changed appearance does not mean physical pixel aspect changed.'),
 ('새 블록이 추가되며 건물의 실제 형태도 달라집니다. 화면 변화 중 무엇이 건축이고, 무엇이 관찰 위치의 변화인지 나누어 보세요.','Adding blocks changes the building itself. Distinguish construction from changes of viewpoint.'),
 ('같은 지붕을 계속 따라가면 어느 부분은 앞에 오고, 어느 부분은 뒤에 가려집니다. 카메라의 위치와 방향은 장면을 읽는 순서를 바꿉니다.','Tracking the same roof shows parts coming forward or being hidden; camera position and direction change how the scene reads.'),
 ('지금 영상만으로 게임이 사용하는 투영 행렬을 알아낼 수는 없습니다. 카메라의 확대 방식도 수치로 단정하지 않겠습니다.','These pixels alone do not establish the game’s projection matrix or numeric zoom method.'),
 ('대신 원래 도식에서는 카메라 위치, 시야각, 출력 창을 각각 고정하고 하나씩 바꿀 수 있습니다. 이렇게 통제해야 계산의 원인을 확인할 수 있습니다.','Our original diagram can hold position, field of view and output rectangle fixed and change one at a time.'),
 ('건물의 세 면이 어떻게 겹치는지 기억해 두세요. 다음에는 카메라가 잠재적으로 보는 공간을 입체로 그려 보겠습니다.','Keep the overlap of the building faces in mind as we construct the camera’s potential viewing volume.')],
 '실제 건축·가까워진 화면·회전하면서 드러나는 옆면','장면 형태의 변화와 카메라·표시 매개변수의 변화는 독립적으로 확인한다')
E(6,'카메라가 보는 공간은 입체입니다','frustum',[
 ('화면은 평면이지만, 원근 카메라가 잠재적으로 보는 공간은 부피입니다. 카메라에서 네 모서리 방향으로 뻗는 선을 먼저 생각해 보세요.','The screen is flat, but a perspective camera’s potential view is a volume. Begin with four corner rays.','카메라 → 네 모서리 방향'),
 ('이 선들이 만드는 피라미드를 가까운 평면과 먼 평면으로 잘라내면 시야 절두체가 됩니다. 영어 이름이 뷰 프러스텀입니다.','Cut the pyramid by near and far planes to obtain the view frustum.','near와 far로 자른 피라미드'),
 ('절두체 안의 점도 반드시 화면에서 보이는 것은 아닙니다. 앞의 불투명한 물체에 가려질 수 있으므로, 잠재적으로 볼 수 있는 공간이라는 뜻입니다.','A point inside is only potentially visible: an opaque object may still occlude it.','시야 안 ≠ 반드시 보임'),
 ('카메라를 옮기면 이 부피도 함께 옮겨집니다. 카메라를 돌리면 부피의 방향이 바뀌고, 시야각을 바꾸면 벌어지는 모양이 바뀝니다.','Moving translates the volume, rotating changes its orientation and changing FOV changes its opening.','위치 이동 / 방향 회전 / 각도 변화'),
 ('출력 창의 위치만 오른쪽으로 옮기는 일은 이 세 가지와 다릅니다. 같은 그림을 저장소의 다른 곳에 놓을 수 있기 때문입니다.','Moving the output rectangle rightward is different: the same view may simply be placed elsewhere.','출력 위치 이동 ≠ 카메라 이동'),
 ('이제 안과 밖을 어떻게 구분하는지 보겠습니다. 피라미드 그림의 선만 보는 대신, 경계를 만드는 여섯 평면을 하나씩 확인하겠습니다.','We will classify inside and outside with the six boundary planes, beyond the outline of a pyramid.','여섯 경계 평면 → 반공간')])
E(7,'여섯 클립 평면으로 안쪽 고르기','planes',[
 ('프러스텀에는 왼쪽, 오른쪽, 위, 아래, 가까운 쪽과 먼 쪽의 여섯 경계가 있습니다. 각 경계는 무한히 뻗은 평면입니다.','A frustum has left,right,top,bottom,near and far boundaries; each boundary is an infinite plane.','left / right / top / bottom / near / far'),
 ('평면 하나마다 안쪽 반공간을 정하고, 여섯 조건을 모두 만족하는 부분만 남깁니다. 그래서 시야 부피는 여섯 반공간의 교집합입니다.','Choose the inner half-space of each plane and retain their intersection.','여섯 안쪽 반공간의 교집합'),
 ('오늘 도식은 카메라 앞쪽을 양의 제트 방향으로 정합니다. 가까운 평면은 일, 먼 평면은 십일에 둡니다. 이 숫자는 게임에서 측정한 값이 아니라 우리가 정한 예제입니다.','Our example faces positive z with near1 and far11; these are defined values, not measurements of the game.','예제규약: 앞+z / near1 / far11'),
 ('제트가 영 점 오인 점은 가까운 경계 밖이고, 제트가 육인 점은 두 거리 경계 사이입니다. 제트가 십이인 점은 먼 경계 밖입니다.','Points at z0.5,z6 and z12 are before near,between the distance planes and beyond far.','z0.5 밖 / z6 사이 / z12 밖'),
 ('제트가 육이라고 무조건 안쪽은 아닙니다. 그 거리에서 옆면 경계보다 가로 위치가 멀리 나가면, 옆쪽 조건을 통과하지 못합니다.','Being at z6 is insufficient if x extends beyond a side boundary at that depth.','거리 조건 + 옆면 조건'),
 ('삼각형이 경계를 가로지르면 일부만 남길 수 있습니다. 꼭짓점 하나가 밖에 있다는 이유로 삼각형 전체를 지우면 화면 가장자리에서 오류가 생깁니다.','A triangle crossing a boundary may retain a portion. One outside vertex does not justify deleting the whole primitive.','경계를 가로지름 → 남는 부분 클리핑'),
 ('가까운 경계와 먼 경계는 깊이 표현의 정밀도와도 연결됩니다. 단순히 먼 거리를 많이 보이는 것만 생각하지 말고, 실제 깊이 형식과 투영의 약속까지 확인해야 합니다.','Near and far also affect depth precision; the actual depth format and projection convention matter.','near·far / 실제 깊이 형식·정밀도'),
 ('깊이를 언제 계산하고 나눗셈을 언제 하는지는 다음 편에서 숫자로 확인합니다. 지금은 거리 경계와 화면 네 변의 경계를 함께 보관하세요.','The next lecture calculates depth and division order; retain both distance boundaries and four screen-side boundaries.','다음 편: 클립 → 나눗셈 → 픽셀')])
A(8,'시점이 돌아도 같은 건물을 추적하기',T,[(399,469)],[
 ('건물 위쪽에 층이 더해지고, 카메라는 낮은 쪽에서 옆면을 바라봅니다. 화면 안의 빈 공간과 지붕의 경계를 함께 보세요.','Floors are added while a low view reveals the building’s side. Observe empty screen space and the roof boundary.'),
 ('시점이 올라가며 위쪽 지붕과 안쪽 테라스가 드러납니다. 물체가 화면에 들어오는 일과, 다른 물체 뒤에서 드러나는 일은 구분할 수 있습니다.','An elevated view reveals roofs and terraces; entering the view and becoming unoccluded are different events.'),
 ('앞에서 볼 때는 겹치던 벽이, 비스듬한 시점에서는 서로 떨어져 보입니다. 카메라 방향을 바꾸면 같은 위치 관계가 다른 화면 배치로 나타납니다.','Walls overlapping frontally separate in an oblique view; the same spatial relationship gives a different arrangement.'),
 ('뒤에는 화면이 멀어졌다가 다시 가까워집니다. 확대된 정도와, 어느 면이 보이는지를 따로 기록해 보세요.','Later framing becomes wider and closer again. Record apparent size separately from which faces are visible.'),
 ('화면 밖으로 나갔다고 실제 건물이 사라졌다고 말할 수는 없습니다. 앞에서 정한 시야 부피가 어느 영역을 담는지 생각하면 됩니다.','Leaving the image does not prove that the building vanished; consider the viewing volume.'),
 ('하지만 이 장면만 보고 가까운 평면이나 먼 평면의 숫자를 읽을 수는 없습니다. 실제 그림과 우리가 정한 수학 예제를 구분해야 합니다.','The recording does not reveal numeric near or far planes. Keep observed pixels separate from defined math examples.'),
 ('다음 도식에서는 카메라 자리를 고정한 채 시야각만 바꿉니다. 그렇게 해야 위치 이동과 시야각 변화의 차이를 분명히 볼 수 있습니다.','Our next diagram holds camera position fixed while changing FOV, isolating it from movement.')],
 '새 층·낮은 측면→높은 시점·실제 확대 변화','시야에 들어옴·가림에서 드러남·화면 크기 변화는 구별한다')
E(9,'시야각은 얼마나 벌어지는 각도일까요?','fov',[
 ('위에서 내려다본 도식에서 카메라와 왼쪽 끝, 오른쪽 끝을 연결합니다. 두 방향 사이의 전체 각도가 수평 시야각입니다.','In a top view, connect the camera to the left and right boundaries; their whole angle is horizontal FOV.','왼쪽 방향 ↔ 오른쪽 방향 / 전체θx'),
 ('중심 방향과 한쪽 끝 사이의 각도는 시야각의 절반입니다. 수평 구십 도라면 각 끝은 중심에서 사십오 도씩 벌어집니다.','The angle from the center to either edge is half the FOV:45 degrees for a90-degree horizontal view.','θx90° → 반각45°'),
 ('카메라 앞쪽 거리를 삼으로 정해 봅시다. 가로 절반 폭은 거리 삼에 사십오 도의 탄젠트를 곱한 값이므로 삼입니다.','At depth3, the half-width is3 times tan45 degrees, or3.','반폭=z tan(θx/2)=3'),
 ('같은 거리에서 왼쪽 마이너스 삼부터 오른쪽 삼까지, 전체 가로 폭은 육이 됩니다. 거리가 육이면 전체 폭은 십이로 커집니다.','The horizontal span at that depth runs from−3 to3, width6; at depth6 it becomes12.','z3→폭6 / z6→폭12'),
 ('시야각을 작게 하면 같은 거리에서 담는 범위가 줄어듭니다. 같은 물체가 그 좁은 범위에서 더 큰 몫을 차지하므로 화면에서 커 보입니다.','A smaller FOV captures less at the same depth; the same object occupies a larger fraction of the image.','각도 감소 → 범위 감소 → 화면 점유 증가'),
 ('좌우로 보는 각도와 위아래로 보는 각도는 각각 필요합니다. 화면 비율을 정하면 한쪽 값으로 다른 쪽을 계산할 수 있지만, 두 값을 같은 숫자로 두는 것은 별개입니다.','Horizontal and vertical FOV are distinct; an aspect ratio links them, but equal numeric angles are a separate choice.','θx와θy / 비율로 연결')])
E(10,'줌 두 배가 되는 시야각 계산','zoom',[
 ('자료의 줌은 구십 도 시야각을 기준으로 정한 배율입니다. 줌 값은 시야각 절반의 탄젠트로 일을 나눈 값입니다.','The source defines zoom relative to90-degree FOV as one divided by tan of the half-angle.','zoom=1/tan(θ/2)'),
 ('구십 도의 절반은 사십오 도이고 탄젠트는 일입니다. 따라서 줌은 일이며, 오늘 비교의 기준이 됩니다.','For90 degrees, tan45 is1, giving zoom1 as our reference.','θ90° → zoom1'),
 ('줌을 이로 바꾸려면 반각의 탄젠트가 영 점 오가 되어야 합니다. 일 나누기 이의 아크탄젠트로 반각을 구한 뒤, 그 각도를 두 배로 합니다.','Zoom2 requires half-angle tangent0.5; FOV is twice arctan of one half.','θ=2atan(1/2)'),
 ('계산 결과는 약 오십삼 점 일 삼 도입니다. 구십 도를 반으로 나눈 사십오 도가 아니므로, 각도와 줌의 관계를 단순 비례로 외우면 안 됩니다.','The result is about53.13 degrees, not45: FOV and zoom are not linearly proportional.','zoom2 → θ≈53.13° / 45° 아님'),
 ('카메라와 물체를 고정하면 화면 중심 주변의 크기는 두 배가 됩니다. 더 넓은 물체가 보인다는 뜻이 아니라, 담는 범위를 좁혀 확대하는 것입니다.','With camera and objects fixed, central image sizes double because the captured range narrows.','위치 고정 / 범위 절반 / 크기2배'),
 ('코드에서 탄젠트나 아크탄젠트가 라디안을 받는지도 확인하세요. 도 단위로 정한 값을 계산 함수에 그대로 넣으면 시야각이 달라집니다.','Check whether tangent functions accept radians; passing degree values directly changes the result.','도→라디안 / 함수 규약'),
 ('여기서 줌은 투영의 숫자입니다. 뒤에서 볼 직교 투영의 줌과는 뜻과 단위가 다르므로, 이름이 같다는 이유로 값을 섞지 않겠습니다.','This zoom is a projection parameter; orthographic zoom has a different meaning and units.','원근 줌과 직교 줌의 뜻 구별')])
A(11,'캐릭터 크기와 함께 보이는 공간',S,[(293,326)],[
 ('두 플레이어가 서로 다른 위치에서 사탕 마을을 통과합니다. 캐릭터 몸의 크기와, 그 주변에 들어오는 길의 범위를 함께 보세요.','The players cross the candy town from different positions. Compare character size with the surrounding paths in view.'),
 ('한쪽 캐릭터가 크게 보인다고 시야각만 다르다고 단정할 수는 없습니다. 캐릭터와 카메라의 거리, 방향과 장면 배치도 함께 달라질 수 있습니다.','A larger character does not prove a different FOV: distance,direction and scene arrangement may also differ.'),
 ('실제 화면은 관찰할 질문을 보여줍니다. 원인을 확인하려면 다음 예제처럼 위치와 각도를 나누어 한 가지씩 바꿔야 합니다.','The gameplay supplies an observation question; controlled examples isolate position and angle.')],
 '두 캐릭터의 크기와 주변 길의 범위','최종 화면 크기만으로 카메라 내부 값의 원인을 단정하지 않는다')
E(12,'두 시야각을 화면 비율로 연결하기','aspect-fov',[
 ('정사각형 픽셀의 십육 대 구 출력 창을 사용하겠습니다. 가로 줌은 일이고, 물체가 늘어나지 않으려면 세로 줌은 십육 나누기 구입니다.','For square pixels in a16:9 window, horizontal zoom1 requires vertical zoom16/9 to preserve shape.','zoomy/zoomx=16/9'),
 ('가로 시야각은 구십 도입니다. 세로 시야각은 구 나누기 십육의 아크탄젠트로 구한 반각을 두 배로 하여, 약 오십팔 점 칠이 도가 됩니다.','Horizontal FOV is90 degrees; vertical FOV is twice arctan(9/16), about58.72 degrees.','θy=2atan(9/16)≈58.72°'),
 ('가로가 넓은 창이므로 가로에 더 큰 각도를 담습니다. 두 축의 시야각을 구십 도로 똑같이 두면 같은 원이 표시 과정에서 가로로 늘어날 수 있습니다.','A wider window captures a larger horizontal angle; using90 degrees on both axes can stretch a circle horizontally.','정상 원 / 두 축 같은 줌→가로 늘어남'),
 ('관계식은 세로 줌 나누기 가로 줌이 창의 물리적 가로 세로 비와 같다는 것입니다. 픽셀이 정사각형이 아니면 픽셀 수의 비만 넣어서는 부족합니다.','Vertical-to-horizontal zoom equals the window’s physical aspect; nonsquare pixels need more than pixel counts.','zoomy/zoomx=(W/H)×픽셀너비/높이'),
 ('같은 천구백이십 곱하기 천팔십이라도 나중에 물리적으로 늘려 표시하는 약속이라면 그 비율까지 곱합니다. 앞의 픽셀 비율 계산이 여기서 연결됩니다.','Include any physical display stretch in addition to1920-by1080 counts; this connects the pixel-aspect calculation.','픽셀 수 비 × 물리적 픽셀 비'),
 ('엔진 설정에서 에프오브이가 하나만 보이면, 수평인지 수직인지 먼저 확인하세요. 나머지 각도를 화면 비율로 구하는 방식도 확인해야 합니다.','If an engine exposes one FOV parameter, check whether it is horizontal or vertical and how aspect derives the other.','한 FOV 설정 → 축·계산 방식 확인'),
 ('화면 비율이 바뀔 때 가로 각도를 고정할지 세로 각도를 고정할지도 선택입니다. 크기를 바꾸고 난 뒤 무엇이 더 보이고 무엇이 줄었는지 비교하면 약속을 검증할 수 있습니다.','Resizing may preserve horizontal or vertical FOV; verify what becomes visible or disappears.','가로 고정 / 세로 고정 / 실제 비교')])
A(13,'확대 전후 같은 지붕을 따라가기',T,[(759,798)],[
 ('타운스케이퍼에서 물가의 건물을 더 크게 만드는 동안 지붕 하나를 기준점으로 잡아 보세요. 건축으로 새로 생기는 면을 먼저 구분합니다.','Track one roof while the waterside structure grows, separating newly constructed faces.'),
 ('이어 전체 건물이 작게 보이는 화면이 가까운 화면으로 바뀝니다. 지붕은 커지고 주변 물의 영역은 줄어드는 것을 볼 수 있습니다.','Wider framing changes to a closer view: the roof grows while less surrounding water fits in the image.'),
 ('화면 뒤쪽의 다른 지붕도 함께 보세요. 앞의 대상만 커졌는지, 여러 깊이의 대상이 어떻게 달라졌는지 비교하면 관찰이 더 정확해집니다.','Compare roofs at other depths as well as the foreground target.'),
 ('이 게임의 입력이 줌인지 이동인지는 단정하지 않고, 다음에는 두 깊이의 물체를 두는 통제된 예제로 차이를 계산하겠습니다.','We will not label this game’s input as zoom or movement; a defined two-depth example will calculate the distinction.')],
 '실제 넓은 화면→가까운 화면과 지붕·물 영역','대상의 크기와 담는 영역을 함께 관찰한 뒤 통제된 비교로 원인을 구분한다')
E(14,'앞으로 이동하면 모든 물체가 두 배일까요?','dolly',[
 ('같은 크기의 두 판을 카메라 앞쪽 거리 사와 팔에 놓겠습니다. 원근 화면의 크기는 물체 크기에 비례하고, 카메라 앞쪽 거리에 반비례합니다.','Place equal-sized panels at forward depths4 and8; perspective size is proportional to object size and inversely proportional to depth.','두 판 / 깊이4와8 / 크기∝1/z'),
 ('카메라는 그대로 두고 줌만 두 배로 바꾸면 두 판 모두 화면에서 두 배 커집니다. 가까운 판과 먼 판의 화면 크기 비는 그대로입니다.','Doubling zoom without moving the camera doubles both panels while preserving their relative image-size ratio.','줌2배 → 가까운2배 / 먼2배'),
 ('이번에는 줌을 유지하고 카메라를 앞쪽으로 이만큼 옮깁니다. 가까운 판의 깊이는 사에서 이로, 먼 판은 팔에서 육으로 바뀝니다.','Move the camera forward2 at fixed zoom: depths change4→2 and8→6.','이동+2 → 깊이4→2 / 8→6'),
 ('가까운 판은 사 나누기 이이므로 두 배입니다. 먼 판은 팔 나누기 육, 즉 삼 분의 사 배로만 커집니다. 두 판의 상대적인 화면 크기도 달라집니다.','The near panel grows by4/2=2; the far grows by8/6=4/3, changing their relative image sizes.','가까운2 / 먼4/3≈1.33'),
 ('앞의 판을 두 배 크게 만드는 결과는 같아도 뒤의 판은 다릅니다. 그래서 앞으로 가는 이동과 렌즈 줌은 같은 효과가 아닙니다.','Both methods can double the front panel, but the rear differs; camera movement and lens zoom are different.','앞 대상 같음 / 뒤 대상 비교'),
 ('여기서 거리는 카메라 앞쪽 축의 제트 좌표입니다. 화면 옆으로 치우친 점의 직선 거리를 그대로 분모에 넣는 것으로 바꾸면 이 투영식과 맞지 않습니다.','The denominator is forward-axis z, not the Euclidean distance to an off-axis point.','분모=카메라 앞쪽 깊이z'),
 ('한 물체만 보며 맞추면 다른 물체의 관계가 바뀐 것을 놓칩니다. 줌과 위치를 시험할 때는 서로 다른 깊이의 기준물을 두 개 이상 남겨 보세요.','Use landmarks at multiple depths; one target can hide changes in their relationship.','서로 다른 깊이의 기준물')])
E(15,'렌즈와 센서에서 시야각 구하기','physical',[
 ('실제 카메라에서는 초점 거리만으로 시야각이 정해지지 않습니다. 센서의 크기도 함께 필요합니다. 오늘은 가로 센서 크기만 보겠습니다.','Physical-camera FOV depends on sensor size as well as focal length; consider sensor width.','초점 거리f + 센서 너비s'),
 ('센서 너비를 초점 거리의 두 배로 나눈 값의 아크탄젠트로 반각을 구한 뒤, 그 각도를 두 배로 하면 가로 시야각입니다. 같은 단위로 계산해야 합니다.','Horizontal FOV is twice arctan of sensor width divided by twice focal length, using consistent units.','θx=2atan(s/(2f))'),
 ('센서 너비를 삼십육 밀리미터, 초점 거리를 십팔 밀리미터로 정하면 안의 비율은 일입니다. 시야각은 구십 도가 됩니다.','A36mm-wide sensor with18mm focal length gives ratio1 and horizontal FOV90 degrees.','s36mm / f18mm → θ90°'),
 ('센서는 유지하고 초점 거리를 삼십육 밀리미터로 늘리면 비율은 영 점 오입니다. 시야각은 약 오십삼 점 일 삼 도로 좁아집니다.','Keeping the sensor and using36mm focal length gives ratio0.5 and FOV about53.13 degrees.','s36mm / f36mm → θ53.13°'),
 ('초점 거리는 십팔 밀리미터로 유지하고 센서 너비를 십팔 밀리미터로 줄여도 같은 시야각을 얻습니다. 숫자 하나만 보고 화면을 단정하면 안 되는 이유입니다.','An18mm sensor width at18mm focal length gives the same FOV; one number alone is insufficient.','s18mm / f18mm → 같은53.13°'),
 ('앞의 수학 도식에서 화면을 놓은 거리와 실제 렌즈의 초점 거리는 약속을 구분해야 합니다. 임의의 투영 평면을 옮겼다고 물리 카메라의 렌즈가 바뀐 것은 아닙니다.','Distinguish an arbitrary mathematical projection-plane distance from the physical lens focal length.','수학 투영 평면 / 물리 렌즈 약속'),
 ('물리 카메라 옵션을 사용하는 엔진이라면 센서, 초점 거리와 창에 맞추는 방식까지 확인하세요. 오늘 계산은 시야각을 설명하며, 심도나 렌즈 왜곡까지 계산한 것은 아닙니다.','Check sensor,focal length and fit policy in physical-camera settings. These calculations address FOV, not depth of field or lens distortion.','센서·초점·맞춤 방식 / 시야각 범위')])
A(16,'가까운 면과 먼 건물을 같이 보기',T,[(798,843),(895,936)],[
 ('건물의 큰 벽과 뒤쪽 지붕을 동시에 기준점으로 삼아 보세요. 새 블록이 붙어 바뀌는 형태와, 시점이 돌아가며 드러나는 면을 나누어 봅니다.','Use a large wall and rear roof as landmarks, separating newly added geometry from orbit-revealed faces.'),
 ('가까운 화면에서는 큰 벽의 일부가 화면을 많이 차지합니다. 넓은 화면에서는 건물 주변의 물과 다른 덩어리를 함께 볼 수 있습니다.','Close framing emphasizes the wall; wide framing includes water and other structures.'),
 ('같은 지붕을 비교할 때 방향까지 바뀌었다면, 보이는 면적의 차이는 단순한 확대 배율만으로 설명되지 않습니다. 시점 조건도 함께 적어야 합니다.','Changing orientation affects visible area beyond a simple enlargement factor; record viewpoint conditions.'),
 ('뒤의 장면에서는 위쪽 테라스 주변에 블록이 추가됩니다. 기존 난간과 새로 생긴 벽을 구분하면, 물체 변화와 화면 변화를 혼동하지 않게 됩니다.','The next interval adds blocks around an upper terrace; distinguish existing railings from new walls.'),
 ('이어 멀리서 보는 화면이 가까운 화면으로 바뀝니다. 앞쪽 면과 뒤쪽 지붕을 함께 추적하는 습관을 실제 장면에서도 적용해 보세요.','Wider framing returns to a close view; track front and rear landmarks together.'),
 ('여기서 실제 게임이 어떤 카메라 함수를 호출했다고 말하지는 않겠습니다. 통제된 도식에서 얻은 두 배와 삼 분의 사라는 값도 이 영상에서 측정한 값이 아닙니다.','We do not infer game camera calls; our factors2 and4/3 belong to the defined diagram, not this recording.'),
 ('실제 플레이에서는 보기 편한 결과가 중요합니다. 수학 예제에서는 어떤 변수를 바꿨는지 아는 것이 중요합니다. 두 역할을 연결하되 근거의 범위는 구분해야 합니다.','Gameplay motivates a readable result; the mathematical example isolates its changed variables. Connect them while respecting the evidence.'),
 ('이제 거리 때문에 크기가 줄어드는 효과를 없애고 싶다고 생각해 봅시다. 지도나 모델링의 도면처럼 볼 때는 다른 투영 방식을 사용할 수 있습니다.','If distance-based shrinking is unwanted, maps and modeling drawings can use another projection.')],
 '서로 다른 깊이의 기존 벽·지붕과 실제 건축·회전·확대','통제된 줌·이동 수치와 실제 화면 관찰을 연결하되 게임 내부 방식은 추정하지 않는다')
E(17,'직교 투영에서는 투영선이 평행합니다','orthographic',[
 ('원근 투영의 선은 카메라 위치에서 만납니다. 직교 투영에서는 같은 화면 방향으로 뻗는 투영선이 서로 평행합니다.','Perspective rays meet at the camera; orthographic projection lines are parallel.','한 점에 모임 / 서로 평행'),
 ('같은 크기와 방향의 판을 거리 이와 십에 놓겠습니다. 원근 화면에서는 먼 판이 작지만, 직교 화면에서는 두 판의 크기가 같습니다.','Equal panels at depths2 and10 shrink differently in perspective but have equal orthographic image sizes.','동일 크기 / z2와10 / 직교 크기 같음'),
 ('이것은 모든 모양을 그대로 보존한다는 뜻은 아닙니다. 판을 돌리면 옆에서 본 가로 폭은 줄어들고, 시선 방향의 정보는 평면에 투영됩니다.','Orthographic projection does not preserve all shape: rotating a panel reduces its projected width and collapses viewing-direction information.','거리 축소 없음 ≠ 모든 모양 보존'),
 ('카메라를 시선 방향으로 앞뒤로 움직여도, 남아 있는 물체의 가로 세로 크기는 바뀌지 않습니다. 다만 클립 경계를 넘거나 가림 관계가 달라지는 경우는 별도로 확인해야 합니다.','Moving along the viewing direction leaves surviving image sizes unchanged; clipping and occlusion still require checks.','앞뒤 이동 / 크기 유지 / 클리핑·가림 별도'),
 ('직교 투영의 시야 부피는 벌어지는 피라미드가 아니라 상자입니다. 따라서 시야각 대신 상자의 가로와 세로 크기로 범위를 지정합니다.','Its viewing volume is a box, described by width and height rather than an opening angle.','피라미드 대신 상자 / 너비·높이'),
 ('지도나 도면을 일정한 축척으로 보여줄 때 이 성질이 유용합니다. 타운스케이퍼의 실제 화면이 어떤 투영인지는 별도로 확인하지 않았으므로, 지금 증명은 우리 도식에서만 적용합니다.','A constant scale is useful for maps and drawings. This proof uses our diagram; Townscaper’s actual projection remains unverified.','원래 도식의 증명 / 게임 내부 투영 미확인')])
E(18,'직교 상자의 크기로 줌 계산하기','ortho-size',[
 ('이번에는 직교 투영의 상자를 가로 팔과 세로 사 점 오로 정합니다. 십육 대 구 출력 천구백이십 곱하기 천팔십입니다.','Use an orthographic box8 by4.5 with aspect16:9 and a1920-by1080 output.','상자8×4.5 / 출력1920×1080'),
 ('가로 팔이 천구백이십 픽셀입니다. 공간에서 정한 길이 한 단위는 이백사십 픽셀입니다. 세로 축척도 나눠 확인하세요.','Mapping width8 to1920 pixels gives240 pixels per world unit; check the same scale vertically.','1920/8=1080/4.5=240px/단위'),
 ('상자의 가로를 사, 세로를 이 점 이오로 함께 줄이면 한 단위는 사백팔십 픽셀이 됩니다. 카메라를 앞으로 옮기지 않고 두 배 확대할 수 있습니다.','Halve both dimensions to4 by2.25 for480 pixels per unit, doubling image size without moving forward.','상자 절반 →480px/단위'),
 ('자료의 직교 줌은 크기로 이를 나눈 값입니다. 가로 크기 팔에서는 영 점 이오, 크기 사에서는 영 점 오가 됩니다.','The source’s orthographic zoom is2 divided by size:0.25 for width8 and0.5 for width4.','zoomx=2/sizeX / 0.25→0.5'),
 ('원근 줌은 각도에서 얻은 비율이지만, 직교 줌은 공간에서 정한 길이의 역수에 해당합니다. 화면상 두 배라는 결과가 비슷해도 입력의 뜻은 다릅니다.','Perspective zoom comes from an angle ratio; orthographic zoom corresponds to inverse world length.','원근:각도 배율 / 직교:세계길이 역수'),
 ('가로 크기만 줄이고 세로는 그대로 두면 가로와 세로 축척이 달라져 원이 타원이 됩니다. 줌을 바꿀 때도 출력 창의 물리적 비율을 함께 유지하세요.','Changing only width creates unequal scales and turns a circle into an ellipse; preserve physical output aspect.','너비·높이 함께 / 같은 축척'),
 ('직교 투영에서도 가까운 평면과 먼 평면은 필요합니다. 거리 축소가 없다는 성질과 깊이를 비교하지 않는다는 말은 같지 않습니다.','Orthographic rendering still uses near,far and depth comparison; absence of shrinking does not remove depth.','직교에도 near·far·깊이')])
A(19,'정면과 지붕 위 시점을 나누어 보기',T,[(936,978)],[
 ('이번에는 테라스 위에서 건물을 더하고, 시점을 바꾸며 벽과 지붕을 살펴봅니다. 같은 건물을 정면에서 볼 때와 위에서 볼 때를 구분해 보세요.','More construction and viewpoint changes reveal terrace walls and roofs. Separate frontal and overhead views.'),
 ('어느 면을 잘 읽고 싶은지가 달라지면 카메라 방향의 선택도 달라집니다. 크기를 더 키우는 것만으로 가려진 지붕이나 벽이 모두 드러나지는 않습니다.','Reading a different face requires another direction; enlargement alone cannot reveal every hidden roof or wall.'),
 ('앞의 직교 도식은 거리 축소가 없는 축척을 보여주었습니다. 실제 게임 화면의 투영을 단정하는 예제가 아니라, 원하는 보기 방식의 선택지를 설명한 것입니다.','The orthographic diagram demonstrated a constant scale as an option, not an inferred property of the game.'),
 ('출력 영역을 나누기 전에는 관찰할 방향, 원근감의 필요와 담을 범위를 먼저 정해 보세요. 다음 문제에서는 두 플레이어의 창 크기로 돌아가겠습니다.','Choose viewing direction,perspective and range before dividing the output; our next problem returns to two player windows.')],
 '실제 테라스 건축과 정면·위쪽 시점에서 보이는 면','카메라 방향·투영 종류·창의 크기는 별도의 선택이다')
E(20,'두 플레이어 화면에서 유지할 값 정하기','exercise',[
 ('첫 문제입니다. 정사각형 픽셀의 천구백이십 곱하기 천팔십 전체 화면에서 수평 시야각 구십 도를 사용합니다. 가로 줌은 일, 세로 줌은 십육 나누기 구입니다.','Start with square pixels,1920 by1080,horizontal FOV90,zoomX1 and zoomY16/9.','전체16:9 / zx1 / zy16/9'),
 ('화면을 세로로 반씩 나누면 각 창은 구백육십 곱하기 천팔십이 됩니다. 각 창의 가로 세로 비는 십육 대 구가 아니라 팔 대 구입니다.','Each vertical half is960 by1080 with aspect8:9 rather than16:9.','각 창960×1080 / 8:9'),
 ('이번에는 세로 시야각을 유지한다고 정하겠습니다. 세로 줌도 유지하고, 세로 줌 나누기 가로 줌이 팔 나누기 구가 되게 해야 합니다.','Preserve vertical FOV and zoomY; their zoom ratio must become8/9.','zy 고정 / zy/zx=8/9'),
 ('계산하면 가로 줌은 이입니다. 각 창의 수평 시야각은 약 오십삼 점 일 삼 도가 되고, 양옆에서 보이는 범위가 줄어듭니다.','This gives zoomX2 and horizontal FOV about53.13 degrees, narrowing the visible sides.','zx=(16/9)/(8/9)=2 / θx53.13°'),
 ('이전과 같은 수평 시야각을 고정하고 싶다면 다른 결과를 선택할 수도 있습니다. 어떤 축을 유지하는지부터 선언해야 두 창에서 모양과 범위를 검증할 수 있습니다.','Preserving horizontal FOV instead is another choice; declare the preserved axis before validating shape and range.','가로 고정은 다른 선택 / 약속 먼저'),
 ('두 번째 문제는 직교 보기입니다. 가로 팔, 세로 사 점 오에서 한 단위는 이백사십 픽셀입니다. 같은 출력에서 두 배 키우려면 상자 크기를 사와 이 점 이오로 줄입니다.','For the orthographic exercise,8 by4.5 gives240 pixels per unit;4 by2.25 doubles it in the same output.','직교8×4.5→4×2.25 / 240→480'),
 ('두 문제 모두 카메라 앞쪽 이동을 사용하지 않았습니다. 창의 비율과 투영 매개변수를 바꾼 것이므로, 위치 이동과 구분해서 코드 이름에도 남겨 보세요.','Neither exercise moved the camera forward; name output-aspect and projection changes separately in code.','출력 크기 / 투영 크기 / 카메라 위치')])
A(21,'건축과 관찰을 따로 기록하기',T,[(1097,1139)],[
 ('마지막으로 지붕이 가까운 화면에서 정면을 살펴보다가, 더 넓은 범위와 높은 시점으로 바뀌는 장면을 보겠습니다.','The final example changes from a close roof and frontal view to wider,elevated framing.'),
 ('뒤에는 블록이 더해지며 건물의 형태도 바뀝니다. 새로 생긴 면은 물체 변화이고, 기존 면이 더 잘 보이는 것은 관찰 변화일 수 있습니다.','Later blocks change the building itself. New faces differ from existing faces revealed by another view.'),
 ('여러분이라면 어디를 봐야 하는지, 어느 방향에서 볼지, 얼마만큼 담을지와 어느 창에 놓을지를 각각 적어 보세요.','Write what to observe,from which direction,over what range and in which output window.'),
 ('그다음 한 가지 조건만 바꾸어 같은 기준점을 비교합니다. 이런 순서로 확인하면 보기 좋은 결과와 올바른 카메라 계산을 함께 점검할 수 있습니다.','Change one condition and compare the same landmarks to check both readability and the camera calculation.')],
 '가까운 지붕→정면→넓은 높은 시점과 실제 블록 추가','카메라 관찰과 장면 변경을 나눠 실습한다')
E(22,'시야·줌·출력 창의 계산을 정리하기','summary',[
 ('오늘은 카메라가 무엇을 보는지와 결과를 어디에 놓는지를 나누었습니다. 위치와 방향, 투영의 범위와 출력 창은 서로 연결되지만 같은 값은 아닙니다.','We separated what a camera sees from where the result goes: position,direction,projection range and output rectangle are related but distinct.','위치·방향 / 투영 범위 / 출력 창'),
 ('픽셀 자체가 일 대 일이어도 화면은 십육 대 구일 수 있습니다. 두 축의 줌 비율은 출력 창의 물리적 비율에 맞추어 계산해야 합니다.','Square pixels can form a16:9 image; the two zoom axes must match physical window aspect.','픽셀1:1 / 화면16:9 / zy/zx'),
 ('원근 줌 두 배는 구십 도에서 약 오십삼 점 일 삼 도로 바꾸는 예제로 확인했습니다. 앞으로 이동하면 깊이가 다른 두 물체의 크기 배율은 달라집니다.','Zoom2 changed90 degrees to about53.13; moving forward instead changes objects at different depths by different factors.','줌2배 / 이동2 → 두 깊이 비교'),
 ('직교 투영에서는 시야각 대신 상자의 크기를 지정합니다. 거리 축소는 없지만 가림, 클리핑과 두 축의 축척은 여전히 확인해야 합니다.','Orthographic projection uses box size instead of FOV; occlusion,clipping and axis scales still matter.','직교 상자 / 클립·가림·축척'),
 ('실습에서는 출력 창의 크기와 유지할 시야각 축을 먼저 기록하고, 서로 다른 깊이의 물체를 비교해 보세요. 실제 게임의 내부 숫자는 화면만 보고 단정하지 않습니다.','Record window size and the preserved FOV axis,compare multiple depths and avoid inferring game internals from pixels.','입력 약속 → 한 조건 변경 → 비교'),
 ('다음 강의에서는 한 점의 좌표를 로컬 공간부터 클립 공간과 화면 픽셀까지 끝까지 계산하겠습니다. 오늘 정한 카메라와 출력 창이 그 계산의 입력이 됩니다.','Next we follow one point from local space through clip space to a screen pixel,using these camera and output choices as inputs.','다음 편: 한 점→화면 픽셀')])
data={'slug':slug,'chapter':10,'part':2,'totalParts':7,'renderModule':'camera_frustum','sourceDependencies':['manim/projects/game-math-part2-full-series/lesson.py'],'sourceSections':['10.2.1','10.2.2','10.2.3','10.2.4','10.2.5'],'contract':{'axes':'Illustrative viewing camera faces+z,up+y,right+x. Native viewport pixel origin top-left,right+x,down+y. Projection stages and matrix/vector conventions follow in separate10.3 lecture.','aspect':'Every aspect is width/height. Pixel physical aspect distinct from image/window aspect. Original stretched4:3→16:9 gives4/3 pixel; 1153×720 source typo corrected1152×720.','perspective':'Defined zoom=1/tan(FOV/2) dimensionless; zoomY/zoomX=physicalWindowAspect; square-pixel16:9 with horizontal90 gives vertical58.715507. Different-depth dolly compares z4,8→2,6 giving2 and4/3.','physical':'Horizontal FOV2atan(sensorWidth/(2*focalLength)),same units.36mm/18mm gives90deg;36/36 or18/18 gives53.130102. Mathematical arbitrary projection plane is not necessarily a physical lens.','orthographic':'Width8,height4.5 gives240pixels/world-unit at1920×1080; width4,height2.25 gives480. Zoom2/size has inverse-world-length units. Parallel rays remove depth scaling but not angular foreshortening,clipping or occlusion.','gameEvidence':'Real gameplay motivates viewing questions; no projection matrix/FOV/near/far/physical values inferred. Split source bottom captions removed only via approved source-only aspect-preserving full-screen crop; exact visible Gameplay – @Candepril credit required.'},'coverage':{'10.2.1':['02','03','20'],'10.2.2':['04','05','12','20'],'10.2.3':['06','07','08','17'],'10.2.4':['09','10','11','12','13','14','15','16','20'],'10.2.5':['17','18','19','20','22'],'completePractice':['20','21','22']},'scenes':scenes,'gameCandidates':{'reviewedAt':'2026-10-08','selected':[{'game':'Split Fiction','sourceId':S,'reason':'Fresh permitted actual two-player split gameplay with different views; exact recorder credit retained on-frame.'},{'game':'Townscaper','sourceId':T,'reason':'Fresh permitted actual construction/orbit/zoom frames; no unsupported orthographic claim.'}],'rejected':[{'game':'Split Fiction long fight/cinematic/deaths','reason':'Reject326.5+fullscreen face,495–510cinematic,repeated black/deaths724–782 and unrelated static intervals.'},{'game':'Unverified other camera-game recordings','reason':'No inspected reuse permission and scene match; use current two fresh verified recordings.'}],'historyReview':'43-project active source/title inventory and recent-game use checked; exact recordings fresh before this research. Separate nonoverlapping windows reserved for next coordinate-chain lecture. Recording permission separate from pending public game-IP review.'}}
assert len(scenes)==22 and sum(s['kind']=='actual' for s in scenes)==8
p=B/'lessons'/f'{slug}.json';assert not p.exists(),'Resume saved authoring rather than overwrite it'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'slug':slug,'scenes':len(scenes),'paragraphs':sum(len(s['ko']) for s in scenes),'koCharacters':sum(len(x) for s in scenes for x in s['ko']),'actualCapacitySeconds':sum(s.get('maxSeconds',0) for s in scenes),'noBgm':True}))
