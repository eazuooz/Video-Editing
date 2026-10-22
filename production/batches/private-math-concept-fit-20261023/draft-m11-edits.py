from common import *
authorized('M11')
edits={
'02':{
'1':['폴리 브리지 쓰리의 다리 윗면을 보세요.','Observe the top surface of a bridge in Poly Bridge 3.'],
'2':['차량이 놓인 높이와 다리의 표면을 나누어 보겠습니다. 모형에서는 물체의 한 점이 표면 위에 있는지, 그 표면에 가까워지는지 확인합니다.','Distinguish the vehicle’s height from the bridge surface. In our model, test whether a point of an object lies above the surface or approaches it.']},
'PG01':{
'1':['바닥 모형과 그 위의 점을 보겠습니다. 먼저 점을 바닥과 나란히 움직이고, 이번에는 위아래로 움직입니다. 같은 이동이라도 표면을 따라가는 방향과 표면에서 떨어지는 방향은 다릅니다.','Observe a floor model and a point above it. Move the point parallel to the floor, then vertically. Moving along a surface differs from moving away from it.'],
'2':['이제 점을 수직으로 내려 바닥으로 돌려놓습니다. 초록 화살표는 표면을 따라가는 방향이고, 파란 화살표는 법선 방향입니다. 거리를 구할 때는 이 두 방향을 구분해야 합니다.','Lower the point perpendicularly back to the floor. Green marks a direction along the surface; blue marks its normal direction. Distinguish these directions when calculating distance.']},
'PG02':{
'1':['이번에는 다리 가운데가 열립니다.','This time the middle of the bridge opens.'],
'2':['양쪽 끝은 연결된 채 다리의 각 부분이 기울어집니다. 같은 바닥이라고 해도 수평인 부분과 기울어진 부분은 방향이 다릅니다. 모형에서 면과 그에 수직인 법선을 함께 돌려 보겠습니다.','The bridge sections tilt while their outer ends stay connected. Horizontal and tilted sections have different orientations. In our model, rotate a surface together with its perpendicular normal.'],
'3':['같은 점이더라도 표면의 위치와 방향이 달라지면 표면까지의 거리도 바뀝니다. 다음 설명에서는 그 점을 법선 방향으로 옮겨 가장 가까운 표면 위치를 구하겠습니다.','Even for the same point, changing a surface position or orientation changes its distance from that surface. Next move the point along the normal to find its closest surface location.']},
'05':{
'1':['수평 바닥 모형의 높이는 고정하고, 점을 그 위와 아래로 옮겨 보겠습니다. 파란 화살표는 위쪽을 가리키는 법선입니다.','Keep a horizontal floor model at a fixed height and move a point above and below it. The blue arrow is its upward normal.'],
'2':['같은 기준면보다 위에 있는지 아래에 있는지는 높이 차이의 부호로 구분할 수 있습니다.','The sign of the height difference distinguishes above and below the same reference plane.'],
'3':['이번에는 점과 바닥을 그대로 두고, 그림을 보는 위치만 바꿉니다. 화면 아래쪽은 고정된 월드 바닥이 아닙니다. 점과 기준면을 같은 좌표계에서 비교해야 합니다.','Now keep the point and floor unchanged and alter only the viewpoint. The screen bottom is not a fixed world floor. Compare the point and reference plane in the same coordinate frame.'],
'6':['다음 그림에서는 직접 정의한 평면으로 가장 가까운 점까지 구합니다. 앞의 게임이 같은 식으로 구현됐다고 단정하는 것은 아닙니다.','Next calculate the closest point on our explicitly defined plane. This does not establish that the earlier game uses the same implementation.']},
'08':{
'1':['다리 편집 화면에서 삼각형을 만듭니다.','Triangles are constructed in the bridge editor.'],
'2':['세 연결점과 그 사이의 선을 보세요. 이 옆모습을 곧바로 삼차원 표면으로 생각하면 안 됩니다. 같은 표면도 카메라 방향에 따라 화면에서는 납작하게 보일 수 있습니다.','Observe three joints and the lines between them. A side-view drawing is not automatically a three-dimensional surface. The same surface can appear flattened from a different camera direction.'],
'4':['삼각형 구조가 보인다고 다리 전체의 실제 메시 구성을 알 수 있는 것은 아닙니다. 여기서는 세 점을 골라 수학 예제의 삼각형을 직접 만들겠습니다.','A triangular structure does not reveal the bridge’s entire rendering mesh. Here we choose three points to construct a mathematical triangle.'],
'5':['삼각형 안의 점을 옮기며 어느 꼭짓점에 가까운지 보세요. 세 기준점 사이의 위치를 숫자로 표현하는 방법이 다음 편에서 이어집니다.','Move a point within the triangle and observe its proximity to each vertex. The next episode expresses this relative location numerically.']},
'PG03':{
'1':['이제 삼각형 대신 꼭짓점이 다섯 개인 판을 보겠습니다. 같은 판을 기울이면 화면에 보이는 가장자리 모양은 달라집니다. 가려진 변은 따로 구분합니다.','Now use a five-vertex panel instead of a triangle. Tilting the same panel changes the projected outline; hidden edges are distinguished.'],
'2':['면의 위치만으로는 이 판의 끝을 알 수 없습니다. 경계의 꼭짓점을 둘레 순서대로 모아야 합니다. 마지막 점에서 첫 점으로 돌아오면서, 여러 꼭짓점이 정하는 면 방향을 구해 보겠습니다.','The plane location alone does not define the panel’s edge. Gather its vertices in perimeter order, returning from the last to the first, to find the orientation defined by the boundary.']}}
save(B/'m11-narration-edits.json',dict(episode='M11',edits=edits,status='source-actions-reviewed',notes=['Preserve the full normal/d, signed-distance, normalization, closest-point, cross-product and Newell teaching sequence and numerical examples.','Different observed bridge operations: finite deck, articulated opening, constructing triangular trusses. No repeated traversal filler.','Do not claim a 2D bridge truss is the internal rendering mesh or infer game world distances.','Original mathematical scope and useful depth retained; no added observation silence.']))
print(sum(map(len,edits.values())),'game-dependent paragraphs revised')
