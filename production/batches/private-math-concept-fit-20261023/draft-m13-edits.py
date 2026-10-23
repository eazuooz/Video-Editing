from common import *
authorized('M13')
edits={
 'QG01':{
  '1':['타이니 글레이드에서 건물을 놓고 크기를 바꿉니다. 가운데 표시와 바깥선이 서로 다른 정보라는 점을 보세요.','Place and resize a building in Tiny Glade. A central reference and its complete outline convey different information.'],
  '2':['이제 모형에서 같은 기준점의 좌우로 건물을 넓혀 보겠습니다. 기준점은 그대로인데 외곽은 달라집니다. 이 모형은 실제 게임 내부 계산을 측정한 것이 아닙니다.','Widen our model on both sides of the same reference. The reference stays fixed while the outline changes. This model is not a measurement of the game’s internal calculation.']},
 '05':{
  '1':['삼각형 모양의 발판에 가운데 표시를 놓겠습니다. 이번에는 표시의 위치뿐 아니라, 가장자리까지 남은 거리도 함께 보세요.','Place a marker on a triangular platform. Observe both its position and the remaining distance to each boundary.'],
  '5':['복잡한 길을 다룰 때도 이 구분은 필요합니다. 발판을 마음대로 삼각형 하나로 바꾸면 원래의 경계나 빈 공간이 사라질 수 있습니다.','The distinction also matters for complex paths. Replacing a platform with one arbitrary triangle can erase boundaries or empty space.']},
 'QG02':{
  '1':['타이니 글레이드에서 벽을 지우고 다시 그립니다. 남은 벽과 새로 열린 빈 공간을 함께 보세요.','Erase and redraw a wall in Tiny Glade. Observe the remaining wall and the newly opened space together.'],
  '2':['길을 벽 너머로 잇자 아치가 생깁니다. 모형에서도 벽과 빈 통로를 따로 표시하겠습니다. 중심 하나만 기록하면 이런 경계 정보가 빠집니다.','Drawing a path through the wall creates an arch. Our model also distinguishes wall from open passage. Recording only a center loses that boundary information.']},
 '08':{
  '1':['모형의 윤곽을 따라가 보겠습니다. 앞으로 튀어나온 부분과 안으로 들어간 홈을 차례로 보세요.','Follow the model’s outline, observing protrusions and inward notches in order.'],
  '5':['이 모형은 경계 순서의 의미를 보여주려고 직접 정한 것입니다. 실제 게임의 지형이 같은 삼각형 메시라고 단정하는 설명은 아닙니다.','We define this model to explain boundary order. It does not assert that real game terrain uses the same triangle mesh.']},
 'QG03':{
  '2':['이번에는 높이가 같은 엘자 모형의 홈을 보세요. 파란 점 두 개는 모두 땅 위에 있지만, 곧게 연결한 선은 빈 곳을 지나갑니다. 높이 차이와 평면 안의 오목함은 다른 문제입니다.','Now inspect the notch in a flat L-shaped model. Both blue points lie on land, but their segment crosses empty space. Height differences and planar concavity are different problems.']},
 'QB11':{
  '1':['도르프로만틱의 타일과 타이니 글레이드의 건물은 배치할 위치를 정합니다. 모형의 삼각형 발판은 가장자리까지의 거리를, 엘자 경계는 남은 땅과 빈 공간을 구분하게 해 줍니다.','Dorfromantik tiles and Tiny Glade buildings need placement references. Our triangular panel distinguishes boundary clearance, while the L-shaped boundary distinguishes retained land from empty space.']},
 'QG08':{
  '1':['엘자 안의 두 점을 다시 연결해 보겠습니다. 각 점에 표시를 놓아도, 둘 사이의 선분이 빈 홈을 가로지른다는 사실은 따로 확인해야 합니다.','Reconnect two points inside the L. Marking the endpoints does not check whether their segment crosses the empty notch.'],
  '2':['이번에는 홈을 따라 경계를 차례로 그립니다. 바깥 모서리만 곧게 이어 버리면 빈 공간이 채워집니다. 같은 점들을 쓰더라도 연결 순서가 중요한 이유입니다.','Now trace the boundary around the notch in order. Connecting only the outer corners fills empty space. This is why connection order matters even when using the same points.']}}
save(B/'m13-narration-edits.json',dict(episode='M13',edits=edits,visualOnlyScenes=['02','11'],status='concept-matched-source-inspection-and-own-models',notes=['Keep all three-center definitions, 3/4/5 calculations, six-vertex L, input validation, convexity and turn tests in original order.','Keep original Dorfromantik narration but recut actual rotation/placement briefly, then show center/boundary models.','Remove Serious Sam and Noita traversal without rewriting unchanged mathematics.']))
print(sum(map(len,edits.values())),'changed complete paragraphs')
