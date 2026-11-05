"""M22: one spoken clause per English counterpart. The second string is for captions."""
ROWS={
4:[
("팔꿈치가 굽을 때, 소매의 한 점은 어디로 가야 할까요?","When an elbow bends, where should a point on the sleeve go?"),
("파란 점은 그 정점이 위팔만 따라갈 때의 위치이고, 초록 점은 아래팔만 따라갈 때의 위치예요.","Blue marks where the upper arm alone would put the vertex; green marks the forearm's proposal."),
("두 점 사이에서 각 본의 영향만큼 섞은 곳이 실제 소매의 위치입니다.","The sleeve vertex lies between them, blended according to each bone's influence."),
("이게 선형 블렌드 스키닝이에요. 섞는 대상은 회전각이 아니라, 본이 옮겨 놓은 두 위치입니다.","This is linear blend skinning. We blend the transformed positions, rather than the angles.")],
5:[
("그럼 어느 본이 이 점을 더 많이 끌어가는 걸까요?","Which bone has more influence on this vertex?"),
("팔의 자세를 그대로 두고, 아래팔의 영향만 서서히 늘려 볼게요.","Hold the pose still and gradually increase the forearm's share."),
("아래팔의 몫이 늘면 위팔의 몫은 줄어들고, 소매의 점이 초록 점 쪽으로 다가갑니다.","As the forearm gains influence, the upper arm loses it and the sleeve point approaches green."),
("팔꿈치 주변의 정점마다 이 비율을 조금씩 다르게 주면, 소매가 한 덩어리로 꺾이지 않고 이어져요.","Varying that blend across neighboring vertices gives the sleeve a continuous bend.")],
10:[
("기준 자세에 있던 정점이 지금 어디에 있는지 구해 볼게요.","Where is a bind-pose vertex in the current pose?"),
("먼저 바인드 행렬의 역행렬로, 그 점을 본에서 본 위치로 바꿉니다.","The inverse bind matrix expresses the point relative to its bone."),
("이제 현재 본의 행렬을 적용하면, 같은 점이 지금 자세의 모델 공간에 놓이죠.","The current bone matrix then places the point in model space in the new pose."),
("매번 원래 바인드 위치에서 시작해야, 지난 프레임의 움직임을 또 더하지 않습니다.","Always start from the bind position so last frame's motion is not applied twice.")],
11:[
("이 두 단계가 왜 필요한지 소매에 단추 하나를 달아 보면 분명해요.","A button on the sleeve makes those two steps easier to see."),
("처음 팔꿈치에서 단추까지 선을 그어 볼게요. 이 간격이 본을 기준으로 본 단추의 위치입니다.","Draw a line from the original elbow to the button. It locates the button relative to the bone."),
("팔꿈치를 옮기면 이 선도 함께 옮겨지고, 그 끝이 단추의 새 위치가 되죠.","Move the elbow: the line follows it, and its tip is the button's new position."),
("처음 팔꿈치가 어디에 있었는지를 빼 주지 않으면, 그 자리까지 움직임에 다시 들어갑니다.","Without removing the original elbow placement, we would count that offset twice.")],
16:[
("노멀 맵에서 꺼내려는 건 색이 아니라, 표면이 어느 쪽을 향하느냐예요.","What we need from a normal map is the surface direction, not its color."),
("빨강은 가로 기울기, 초록은 세로 기울기, 파랑은 표면 밖을 향하는 성분을 담습니다.","Red carries the first tangent component, green the second, and blue the outward component."),
("방향에는 음수가 있지만 색 채널에는 보통 음수가 없어서, 저장할 때 범위를 옮기고 읽을 때 되돌립니다.","A direction can be negative; an ordinary color channel cannot. Encoding and decoding convert between those ranges."),
("기울지 않은 곳은 바깥쪽 성분이 가장 커서 푸른색으로 보이죠.","At an untilted point the outward component dominates, giving the map its familiar blue tint.")],
20:[
("이제 같은 표면점에서 빨강 채널만 바꾸면 법선이 어디로 기우는지 보죠.","At the same surface point, what happens to the normal when only red changes?"),
("표시된 식은 색에 저장된 성분을 꺼내서, 길이가 일정한 방향 화살표로 만드는 식입니다.","The formula decodes the stored channels and normalizes the resulting arrow."),
("빨강을 낮추면 화살표가 접선의 반대쪽으로 기울고, 같은 빛에서도 그 자리의 밝기가 바뀝니다.","Lower red and the arrow leans against the tangent; illumination changes under the same light."),
("여덟 비트 색에는 저장할 수 있는 단계가 정해져서, 원래 방향을 정확히 되찾지 못할 수도 있어요.","Eight-bit channels have finite steps, so decoding may introduce a small direction error.")],
21:[
("그 화살표가 실제 모델에서는 어느 쪽을 향할까요?","Which way does that arrow point on the model itself?"),
("텍스처의 가로 성분이 음수라는 건 화면 왼쪽이 아니라, 표면에서 유가 줄어드는 쪽을 뜻해요.","A negative first component points toward decreasing surface U, not toward screen left."),
("가로, 세로, 바깥쪽 성분을 각각 접선, 비탄젠트, 법선 방향에 얹어 더하면 모델 공간의 법선이 됩니다.","Combine the three components along the tangent, bitangent and surface normal to obtain a model-space normal."),
("면을 돌려 볼게요. 기준축과 합성한 화살표가 같이 돌아서 요철이 표면에 붙어 있습니다.","Rotate the face. Its axes and the resulting arrow turn together, keeping the detail attached.")],
26:[
("우리가 찾을 건 텍스처에서 가로로 갈 때와 세로로 갈 때, 모델 위에서 각각 어느 쪽으로 움직이느냐입니다.","We want the two model-space directions corresponding to horizontal and vertical texture travel."),
("먼저 첫 번째 변을 따라가 보죠. 텍스처에서 가로로 간 몫과 세로로 간 몫을 합치면, 모델에서는 바로 그 변이 됩니다.","For the first edge, its horizontal and vertical texture contributions add up to the observed model edge."),
("두 번째 변도 같은 두 방향으로 나눌 수 있어요. 두 변의 길과 유브이 변화는 이미 압니다.","The second edge uses the same two directions. Both model edges and both UV changes are known."),
("그래서 두 식을 함께 풀면 아직 모르는 접선과 비탄젠트를 구할 수 있어요.","Solving those two equations gives the unknown tangent and bitangent.")],
27:[
("두 변에서 접선과 비탄젠트를 따로 꺼내려면, 유브이 삼각형이 넓이를 갖는지부터 봅니다.","To separate the tangent from the bitangent, first check whether the UV triangle has area."),
("식의 분모는 두 유브이 변의 행렬식입니다. 그 크기는 삼각형 넓이의 두 배이고, 부호에는 꼭짓점 순서가 남아요.","The denominator is the UV determinant. Its magnitude is twice the triangle area, and its sign records orientation."),
("첫 식은 두 변에서 세로 몫을 지워 접선을 남기고, 둘째 식은 가로 몫을 지워 비탄젠트를 남깁니다.","The first expression eliminates the vertical contribution to isolate T; the second eliminates the horizontal contribution to isolate B."),
("이렇게 얻은 벡터에는 방향뿐 아니라, 텍스처 좌표가 변할 때 모델에서 얼마나 이동하는지도 들어 있어요.","These vectors encode travel per texture unit as well as direction, so they need not have unit length.")],
28:[
("식을 그림으로 확인해 볼게요. 텍스처 위의 작은 점을 오른쪽으로만 움직여 봅니다.","Check the formula visually: move a point only to the right on the texture."),
("모델에서 같은 점이 지나가는 길이 바로 접선 방향입니다.","The matching point on the model follows the tangent."),
("이번에는 텍스처에서 위로 움직여 볼게요. 모델에서는 비탄젠트를 따라가죠.","Move the texture point up instead. The model point now follows the bitangent."),
("화살표의 길이를 같게 맞춰도 각각 가리키는 쪽은 그대로예요. 그런데 텍스처를 뒤집으면 어떨까요?","Normalizing the arrows preserves their directions. What changes when the texture is mirrored?")]
}
# (literal spoken anchor, normalized animation position).
ANCHORS={
4:[('파란 점은',.12),('초록 점은',.38),('두 점 사이에서',.68),('선형 블렌드',1)],
5:[('팔의 자세를',.08),('아래팔의 몫이',.28),('초록 점 쪽으로',.75),('정점마다',1)],
10:[('바인드 행렬의',.16),('행렬을 적용하면',.56),('매번 원래',1)],
11:[('처음 팔꿈치에서',.12),('팔꿈치를 옮기면',.5),('새 위치가',.9),('처음 팔꿈치가',1)],
16:[('빨강은 가로',.22),('방향에는 음수가',.5),('푸른색으로',1)],
20:[('표시된 식은',.15),('빨강을 낮추면',.36),('밝기가 바뀝니다',.9),('저장할 수 있는',1)],
21:[('텍스처의 가로',.14),('바깥쪽 성분을',.38),('면을 돌려',.65),('요철이 표면에',1)],
26:[('첫 번째 변을',.15),('세로로 간 몫',.47),('두 번째 변도',.62),('두 식을 함께',1)],
27:[('삼각형이 넓이를',.12),('분모는',.32),('세로 몫을',.56),('가로 몫을',.8),('방향뿐 아니라',1)],
28:[('오른쪽으로만',.16),('접선 방향',.46),('위로 움직여',.62),('비탄젠트를 따라',.86),('텍스처를 뒤집으면',1)]}

