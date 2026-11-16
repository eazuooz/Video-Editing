"""Original beginner explanations inserted beside the retained source passages.

Pairs are Korean narration/display and English meaning captions. A vertical bar
marks a proposed semantic caption break, to be accepted only at an ASR word edge.
"""
CONTENT={
'journey':dict(
 replace={
 'r0122':[('작은 모래 면이 카메라를 향하는 정도로|반짝임을 조절한 겁니다.','The sparkle is controlled by|how much a tiny sand surface faces the camera.')],
 'r0123':[],
 'u014':[('실제 모래를 그대로 재현한 공식보다는,|움직일 때 보기 좋은 표현을 택한 겁니다.','This is an artistic rendering choice,|rather than an exact model of real sand.')],
 },
 after={
 'p001':[('발밑의 작은 빛점과|언덕 전체의 밝은 띠를 따로 보세요.','Look separately at the small bright points|and the broad light across a dune.'),('작은 점은 모래알 느낌을,|넓은 빛은 언덕 모양을 알려 줍니다.','The tiny points suggest grains;|the broad light reveals the dune’s shape.')],
 'p002':[('작은 거울을 여러 방향으로|기울여 놓았다고 생각해 보세요.','Imagine many tiny mirrors|tilted in different directions.'),('같은 빛을 받아도|우리 쪽으로 빛을 보내는 면만 밝게 보이죠.','Under the same light,|only some faces send light toward us.'),('입체 모래알 대신|그 방향 차이를 무늬에 담는 겁니다.','The pattern stores those direction differences|instead of modeling every grain.')],
 'p003':[('여기서는 카메라만 움직이고|모래 언덕은 그대로입니다.','Here the camera moves|while the dune stays in place.'),('그런데 밝게 보이는 작은 점은 달라지죠.','Yet the small bright points change.'),('모래에 전구를 박은 게 아니라|보는 방향에 따라 반사가 달라지는 겁니다.','The sand is not covered in tiny lamps;|its reflections change with the view.')],
 'p004':[('비교 모형에서 시선을 옮기면|밝아지는 작은 면도 바뀝니다.','As the view moves in this comparison model,|different small faces become bright.'),('중요한 것은 점을 많이 켜는 것보다|움직여도 모래처럼 보이게 하는 겁니다.','The goal is not simply more bright dots,|but sand that remains convincing in motion.')],
 'p005':[('언덕을 위에서 볼 때와|옆으로 비껴 볼 때를 비교해 보세요.','Compare looking down onto the dune|with viewing it at a grazing angle.'),('길게 늘어난 빛까지 그대로 강조하면|작은 모래알 느낌이 깨집니다.','Emphasizing stretched highlights equally|would spoil the tiny-grain appearance.')],
 'p006':[('작은 빛점만 있으면|언덕의 둥근 모양은 잘 읽히지 않겠죠.','Tiny bright points alone|would not clearly describe the dune’s rounded shape.'),('거친 결과 작은 반짝임,|넓은 반사광을 함께 봐야 합니다.','Read the coarse texture, fine sparkles,|and broad reflection together.')]
 }),
'inside':dict(
 before={
 'p001':[('화면을 확대하면|작은 색 칸들이 모여 있습니다.','Zoom into an image|and you find small cells of color.'),('이 칸이 픽셀이고,|그 칸으로 만든 한 장의 화면이 프레임입니다.','A cell is a pixel;|one complete image is a frame.')],
 },
 after={
 'p001':[('얇은 나뭇가지가 칸 사이에 걸리면|어떤 화면에서는 잡히고 다음에는 빠집니다.','A thin branch can fall between sample positions,|appearing in one image and missing the next.'),('그래서 실제 물체는 그대로인데도|선이 깜빡이는 것처럼 보일 수 있죠.','The object can stay the same|while its thin edge appears to flicker.')],
 'p002':[('첫 장에서는 칸의 왼쪽,|다음 장에서는 오른쪽을 보는 식입니다.','Think of sampling the left side of a cell first,|then its right side in the next image.'),('한 번씩 다르게 살펴본 결과를 모으면|가는 선의 위치를 더 잘 짐작할 수 있죠.','Combining those different samples|gives a better estimate of the thin edge.')],
 'p003':[('소년이 오른쪽으로 가는데|이전 소년을 왼쪽에 그대로 섞으면 잔상이 생깁니다.','If the boy moves right,|mixing his old position in place leaves a ghost.'),('먼저 같은 소년의 위치를 맞춘 뒤|과거 정보를 가져와야 합니다.','First align the corresponding position,|then bring in the earlier information.')],
 'p004':[('소년이 지나가서 드러난 배경에는|예전 소년의 색이 필요 없겠죠.','A background revealed behind the boy|does not need his old color.'),('주변은 어두운데 과거 색만 밝다면|그 밝은 색을 그대로 믿지 않는 겁니다.','If the current neighborhood is dark,|a bright historical color should not be trusted unchanged.')],
 'p005':[('가장자리를 안정시키는 일과|빠른 움직임을 흐리게 보이는 일은 목적이 다릅니다.','Stabilizing an edge and blurring fast motion|serve different purposes.'),('흐린 결과까지 계속 모으면|다음 화면도 더 흐려질 수 있겠죠.','Repeatedly accumulating an already blurred result|could blur later images further.')],
 'p006':[('시간을 쓴다는 말은|여러 장에서 얻은 정보를 활용한다는 뜻입니다.','Using time means|using information collected across several images.')]
 }),
'spiderman':dict(after={
 'p001':[('실제 장면에서 내려갔다가|앞으로 올라가는 곡선을 먼저 보세요.','First watch the real swing|dip and then rise forward.'),('모형에서는 줄의 위쪽 끝만 옮겨|그 곡선이 어떻게 달라지는지 비교합니다.','In the model, move only the upper attachment|to compare how the arc changes.')],
 'p002':[('손전등 빛을 여러 줄 쏜다고 생각하면 쉽습니다.','Imagine sending out several narrow flashlight beams.'),('가는 기둥이 빛줄기 사이에 있으면|검사에 걸리지 않을 수 있죠.','A thin post between the beams|can escape those tests.')],
 'p003':[('이제 가는 선 대신|건물 벽 전체를 후보 구역으로 보는 겁니다.','Now treat a whole building face|as the candidate region instead of isolated lines.'),('상자는 후보를 찾기 쉽게 만든 표시이고,|마지막에는 진짜 지형도 확인합니다.','The box makes candidate selection easier;|the real geometry is still checked afterward.')],
 'p004':[('앞으로 가고 싶은데|줄이 뒤에 붙으면 몸을 뒤로 당기겠죠.','If you want to move forward,|an attachment behind you would pull backward.'),('또 너무 낮게 붙으면|바닥 가까이 내려갈 수 있습니다.','An attachment that is too low|can also send the swing close to the ground.'),('실제 장면의 줄 방향과 이동을 보고,|모형의 높은 점과 낮은 점을 비교해 보세요.','Watch the real line and movement,|then compare the model’s higher and lower anchors.')],
 'p005':[('후보마다 가고 싶은 쪽인지,|줄 길이가 알맞은지 따져 보는 겁니다.','Each candidate is checked for direction|and a suitable line length.'),('실제 영상만으로 그 점수는 보이지 않지만,|매번 손으로 조준하지 않고 스윙하는 결과는 보이죠.','Those scores are hidden in gameplay,|but the resulting swings do not require aiming at every point.')],
 'p006':[('같은 도시라도 붙일 곳을 잘 골라야|다음 스윙으로 자연스럽게 이어집니다.','Choosing a suitable attachment in the same city|helps one swing lead naturally into the next.')]
 }),
'control':dict(after={
 'p001':[('이 사무실에서는 총을 쏜 뒤|조각과 먼지가 함께 튀어나옵니다.','In this office, shots are followed by|flying fragments and dust.'),('같은 충격을 큰 변화와|작은 효과로 나누어 보여 주는 거죠.','One impact is shown through|both large changes and small effects.')],
 'p002':[('비교 모형에서 큰 판이 떨어지면|책상의 윤곽이 바뀝니다.','When a large panel falls in the model,|the desk’s outline changes.'),('그 옆의 작은 조각과 먼지는|어디에 충격이 났는지 더 잘 보여 줍니다.','Nearby chips and dust|make the impact location easier to read.')],
 'p003':[('나무판은 길쭉한 조각으로,|유리판은 다른 모양으로 나눈다고 생각해 보세요.','Imagine splitting a wooden panel into long pieces,|while a glass panel uses a different fracture pattern.'),('이 차이를 재질의 규칙으로 준비하면|책상마다 같은 일을 반복하지 않아도 됩니다.','Preparing that difference as a material rule|avoids repeating the work for every desk.')],
 'p004':[('잘라 둔 퍼즐 조각을|약한 접착제로 붙여 둔 모습과 비슷합니다.','Think of prepared puzzle pieces|held together by weak glue.'),('충격을 받은 연결은 풀리고|멀리 있는 연결은 남도록 다룰 수 있죠.','Connections near an impact can release|while other connections remain intact.')],
 'p005':[('큰 판이 떨어지는 순간과|그 자리에서 먼지가 퍼지는 순간을 함께 보세요.','Watch the large panel fall|as dust spreads from the same location.'),('물리 조각은 모양을 바꾸고,|입자 효과는 부서지는 느낌을 채웁니다.','Physical fragments change the shape;|particles fill out the impression of a break.')],
 'p006':[('벽에 검은 자국을 그리는 것과|벽 조각이 떨어져 나가는 것은 다릅니다.','Painting a dark mark on a wall|differs from a piece of wall falling away.'),('자국, 파편, 연결 해제를|함께 준비해야 반응이 풍부해집니다.','Marks, fragments, and released connections|work together to create a richer response.')]
 }),
'returnal':dict(after={
 'p001':[('촉수의 뿌리와 끝을|따로 따라가 보세요.','Follow the root and tip|of the tentacle separately.'),('둘이 똑같이 한꺼번에 움직이지 않아|부드럽게 휘는 느낌이 납니다.','Their motion is not identical at every instant,|which helps the shape feel flexible.')],
 'p002':[('긴 줄마다 무거운 몸체를 붙이면|계산할 연결도 많아집니다.','Adding a physical body along every long chain|creates many connections to simulate.'),('입자로 바꾸면 움직임 규칙을|이펙트 도구에서 직접 조절할 수 있습니다.','Particles let artists control the motion rules|inside their effects tools.')],
 'p003':[('앞사람의 바로 전 동작을 보고|뒤 사람이 따라 하는 줄을 떠올려 보세요.','Imagine a line of people, each following|the person ahead from a moment earlier.'),('앞쪽은 이미 돌아섰는데|뒤쪽은 조금 뒤에 꺾이는 모습입니다.','The front has already turned|while the back bends a little later.'),('모형의 점들이 따라가는 시간 차이를 보면|부모와 자식의 관계가 더 잘 보입니다.','The model’s delayed points|make the parent-child relationship visible.')],
 'p004':[('납작한 리본은 옆에서 보면|두께가 거의 사라집니다.','A flat ribbon can lose nearly all its thickness|when viewed edge-on.'),('같은 길을 따라 원통을 만들면|방향이 바뀌어도 굵기가 남습니다.','A tube around the same path|retains volume as the viewing direction changes.')],
 'p005':[('원통을 감싼 줄무늬를 보면|표면이 얼마나 뒤틀리는지 알 수 있죠.','Stripes around a tube|make its surface twist easier to see.'),('방향을 이어 받고 부드럽게 바꾸면|빛도 갑자기 뒤집히지 않습니다.','Passing along and smoothing the orientation|helps the lighting avoid abrupt flips.')],
 'p006':[('단순히 계속 흔들리는 것과|공격 준비에 맞춰 움직이는 것은 다릅니다.','Constantly waving is different from|moving in step with an attack preparation.'),('생물 같은 움직임을 만들면서|플레이어가 적의 상태도 읽게 한 겁니다.','The aim is lively motion|that also helps players read an enemy’s state.')]
 }),
'doom':dict(after={
 'p001':[('숨은 자리에서 체력 회복만 기다리면|전투의 흐름이 끊기겠죠.','Waiting behind cover for health|would interrupt the flow of combat.'),('개발진은 회복 기회를 적 쪽에 두어|다시 싸움으로 들어가게 했습니다.','The designers placed recovery opportunities near enemies|to encourage re-entering the fight.')],
 'p002':[('적이 잠깐 빛나며 비틀거리는 순간이|다가갈 수 있는 짧은 기회입니다.','The enemy briefly flashes and staggers,|creating a short opening to approach.'),('너무 오래 망설이면|그 기회를 놓칠 수 있습니다.','Wait too long|and that opportunity can disappear.')],
 'p003':[('여기서는 마무리 뒤 파란 회복물이 나오고|체력이 올라가는 것을 보세요.','Watch the blue health drops after the finisher|and the health increase that follows.'),('적을 줄이는 행동이|다음 싸움을 버틸 자원으로 이어집니다.','Reducing the enemy count|also supplies resources for the next exchange.')],
 'p004':[('체력이 넉넉할 때와 부족할 때|같은 보상이 똑같이 필요하지는 않겠죠.','A healthy player and a wounded player|do not need exactly the same reward.'),('회복을 돕는 규칙과|탄약을 주는 규칙은 나누어 봐야 합니다.','Separate the rules that help restore health|from those that provide ammunition.')],
 'p005':[('총알이 부족할 때는|전기톱과 남은 연료를 함께 생각하게 됩니다.','When ammunition runs low,|the chainsaw and its remaining fuel become relevant.'),('아무 때나 공짜로 쓰는 회복 버튼이 아니라|자원을 바꾸는 선택인 겁니다.','It is a resource trade-off,|rather than a free recovery button.')],
 'p006':[('위험을 감수하고 다가간 보상이|다음 공격을 할 여유로 돌아옵니다.','The reward for approaching danger|creates room for the next attack.')]
 }),
'botw':dict(before={
 'p002':[('이 상태 변화를 공통으로 처리하는 체계가|화학 엔진입니다.','The system that handles these shared state changes|is the Chemistry Engine.'),('물리 엔진이 물체가 어디로 움직이는지 계산한다면,|화학 엔진은 불붙거나 젖는 관계를 다룹니다.','Physics handles how objects move;|chemistry handles relationships such as burning and becoming wet.')],
 },after={
 'p001':[('불이 닿기 전과 후의 풀밭을|나란히 비교해 보세요.','Compare the grass|before and after contact with fire.')],
 'p003':[('실제 장면에서는 불 가까이에 둔 얼음이|작아지는 것도 볼 수 있습니다.','The actual footage also shows ice|shrinking near a fire.'),('밀어서 위치가 바뀌는 것과,|열 때문에 상태가 달라지는 일을 구별해 보세요.','Distinguish pushing an object to a new position|from changing its state through heat.')],
 'p004':[('비교 모형에서는 나무에 붙은 불에|물을 닿게 해 보겠습니다.','In the explanatory model,|bring water into contact with the fire.'),('불이라는 효과도|다른 효과의 영향을 받는 겁니다.','The fire effect itself|is affected by another effect.')],
 'p005':[('나무 상자 둘이 부딪혀 움직여도|그것만으로 서로 불붙는 것은 아니죠.','Two wooden boxes can collide and move|without setting one another on fire.'),('충돌로 밀리는 일과|화학적 상태가 바뀌는 일은 다른 층입니다.','Being pushed by a collision|and changing a chemical state are different layers.')],
 'p006':[('그래서 새 장소의 풀밭에도|불과 물의 관계를 다시 적용할 수 있습니다.','The same relationship between fire and water|can be reused in a different patch of grass.'),('장소 이름마다 결과를 따로 쓰기보다|대상과 효과 사이의 약속을 만드는 겁니다.','Instead of scripting a separate result for each location,|define relationships between materials and effects.')],
 'p007':[('물리 엔진이 움직임을,|화학 엔진이 상태의 연결을 맡습니다.','Physics handles motion;|the Chemistry Engine connects states.')]
 }),
'kart':dict(after={
 'p001':[('우선 바퀴가 옆으로 펴지고|차체가 떠 있는 구간을 확인하세요.','First identify the section where the wheels turn sideways|and the kart hovers.'),('같은 접촉도 어떤 주행 상태인지에 따라|보상이 달라지는 겁니다.','The reward for contact depends|on the kart’s driving state.')],
 'p002':[('길이 벽으로 돌아가면|피해야 할 것만 찾던 시선도 바뀝니다.','When the road turns onto a wall,|you begin looking for more than things to avoid.'),('어디에 닿으면 앞으로 나갈 수 있을지도|함께 보게 되는 거죠.','You also look for contact opportunities|that can send you forward.')],
 'p003':[('반중력 구간에서 다른 카트와 닿으면|회전하며 속도를 얻는 규칙입니다.','In an anti-gravity section, contact with another kart|can trigger a spin and speed boost.'),('이 효과가 있으니 접촉을 무조건 피하는 대신|일부러 가까이 가는 선택도 생깁니다.','That reward creates a choice to approach,|instead of avoiding every contact.')],
 'p004':[('여기서는 빛나는 기둥에 닿은 직후|카트가 한 바퀴 도는 모습을 보세요.','Here, watch the kart spin|immediately after contacting the glowing post.'),('옆의 평범한 벽 전체가|같은 가속 장치라는 뜻은 아닙니다.','That does not turn every ordinary wall nearby|into the same boost device.')],
 'p005':[('이 규칙은 접촉을 벌점만이 아니라|속도를 얻는 기회로도 바꿉니다.','The rule turns some contact|from a penalty into a speed opportunity.'),('그래서 반중력 구간에서는|상대와 장치를 보고 경로를 고르게 됩니다.','In an anti-gravity section,|other racers and devices become part of route choice.'),('새로운 주행 공간에|새로운 상호작용을 더한 셈이죠.','The new driving space|also gains a new kind of interaction.')]
 })}
