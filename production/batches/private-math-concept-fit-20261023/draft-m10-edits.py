from common import *
authorized('M10')
edits={
'10':{
'1':['둥근 머리를 가진 모형을 보겠습니다. 복잡한 표면을 둘러싸는 둥근 범위부터 찾아보세요.','Consider a model with a rounded head. First observe a spherical region enclosing its detailed surface.'],
'3':['다만 둥근 윤곽이 곧 물체의 정확한 표면이나 실제 피해 범위라는 뜻은 아닙니다. 반지름은 우리가 정의한 계산 데이터입니다.','A rounded outline is not necessarily the exact object surface or an actual damage region. The radius is calculation data that we define.']},
'LG04':{
'1':['같은 모형의 둥근 머리와 긴 팔다리를 비교하세요. 어떤 부분을 감쌀지에 따라 필요한 범위가 달라집니다.','Compare the rounded head and long limbs of the same model. The required bounds depend on which parts we enclose.'],
'2':['초록색 구는 머리를 감싸는 계산용 비교입니다. 게임의 실제 판정 구가 아닙니다. 다음에는 중심과 반지름을 직접 정해 구의 안팎을 계산합니다.','The green sphere is a computational comparison enclosing the head, not a game collision sphere. Next we define its center and radius to calculate inside and outside.']},
'13':{'1':['이 모형의 팔을 펼쳐 보겠습니다. 머리, 팔과 몸통의 윤곽을 하나씩 모두 검사한다고 생각해 보세요.','Let us extend this model’s arms. Imagine testing every part of the head, arms and torso outline.']},
'LG05':{
'1':['타이니 글레이드에서 건물을 놓고 늘립니다.','In Tiny Glade, a building is placed and resized.'],
'2':['벽과 지붕이 차지하는 범위를 보세요. 이제 모형에서 건물의 윤곽을 감싸는 상자를 그려 보겠습니다.','Observe the space occupied by the walls and roof. Now we draw a box around a building outline in our model.'],
'3':['기울어진 지붕 위의 빈 공간도 상자에 들어갑니다. 이 상자는 설명을 위해 계산한 범위이며 게임 내부 판정의 측정값이 아닙니다.','The box also contains empty space above the sloping roof. It is a calculated teaching bound, not a measurement of the game’s internal collision data.'],
'4':['모양과 그 모양을 감싼 상자는 다릅니다. 다음에는 상자 겹침이 실제 물체의 접촉과 다른 이유를 이어서 보겠습니다.','A shape differs from the box enclosing it. Next we examine why overlapping bounds do not necessarily mean the objects touch.']},
'16':{'1':['서로 떨어진 두 길쭉한 모형을 보겠습니다. 각 모양을 월드 축에 나란한 상자로 감싸 보세요.','Consider two separate elongated models. Enclose each shape in a box aligned with the world axes.']},
'LG06':{
'1':['길쭉한 모형의 위치는 고정하고 제자리에서 돌리겠습니다. 물체에 붙은 상자와 월드 축에 나란한 상자를 비교하세요.','Keep the elongated model in place and rotate it. Compare an object-attached box with a box aligned to the world axes.'],
'2':['물체를 따라 도는 상자는 방향이 함께 바뀝니다. 월드 축 상자는 축 방향을 유지하면서 모형을 감쌀 크기가 바뀝니다.','The object-attached box rotates with the model. The world-aligned box keeps its axis directions while changing its extents to enclose the model.'],
'3':['이번에는 물체를 멈추고 카메라만 옮깁니다. 화면 윤곽은 바뀌지만 고정된 물체의 월드 경계는 그대로입니다.','Now stop the object and move only the camera. Its screen outline changes, but the fixed object’s world bounds remain the same.']},
'19':{'1':['같은 건물 모형은 고정하고 카메라만 옮깁니다. 다른 쪽에서 보며 화면의 가로세로 범위를 비교하세요.','Keep the same building model fixed and move only the camera. Compare its screen-space width and height from different viewpoints.']},
'LG07':{
'1':['이번에는 건물 높이가 달라집니다.','This time the building height changes.'],
'2':['카메라 이동과 달리 물체 자체의 모양이 변했습니다. 모형에서도 벽의 높이를 바꾸고, 그 모양을 감싸는 경계를 다시 계산하겠습니다.','Unlike moving the camera, this changes the object itself. In our model we also change the wall height and recalculate the enclosing bounds.'],
'3':['기울어진 지붕과 계산용 상자 사이에는 빈 공간이 남습니다. 실제 표면의 점과 상자의 꼭짓점은 다릅니다. 다음 장면에서는 무엇을 감쌀지 먼저 정하겠습니다.','Empty space remains between the sloping roof and its bounding box. Surface points differ from box corners. Next we first decide what to enclose.']},
'21':{'1':['긴 다리 모형과 팔을 펼친 모형을 나란히 보겠습니다. 고정된 구조물의 범위와 자세에 따라 바뀌는 몸의 범위를 나누어 생각하세요.','Compare a long bridge model with a model extending its arms. Distinguish the bounds of a fixed structure from those of a body changing pose.']}}
save(B/'m10-narration-edits.json',dict(episode='M10',edits=edits,status='source-actions-reviewed',notes=['Preserve all original circle/sphere, min-max, AABB/OBB, overlap, transformed-corner and absolute-matrix formulas and worked values.','Replace repeated fighting/traversal with isolated mathematical bounds around recognisable models.','Two distinct Tiny Glade operations: placement/width and height. No game-internal collision data claimed.','Keep head/limbs and animation-bound limitations in the original order; do not replace the lesson with construction-only topics.']))
print(sum(map(len,edits.values())),'game-dependent paragraphs revised')
