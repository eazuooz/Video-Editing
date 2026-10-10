"""Author source-dependent narration only after native and dense comparisons."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
for folder,expected in [('lines-portal-candidates',4),('lines-post-candidates',2),('lines-bound-candidates',3),('lines-funnel-candidates',1)]:
 proof=O/folder/'native-ended-ax.txt';raw=proof.read_text(encoding='utf8')
 assert raw.count('"ended": true')==expected and raw.count('"rate": 1')==expected and 'all ended' in raw,folder
scenes=[]
def game(i,title,source,intervals,ko,en,visible,reason,occlusion):
 scenes.append(dict(id=i,title=title,kind='actual',sourceType='actual-footage',sourceId=source,intervals=intervals,maximumSeconds=sum(z-a for a,z in intervals),ko=ko,en=en,selection=dict(visibleBeforeActionAfter=visible,chosenReason=reason,camera='Projected observation only. Narrate camera/cut changes; hide or reset tracks at each cut.',occlusion=occlusion,UI='Health/ammunition bottom corners and score top; geometry labels above fixed captions. Reframe source when necessary without moving captions.',nativeAndDenseComparison=True,finalAnnotatedPixels='pending'),annotation=dict(red='visible connection or object contour',blue='visible target/extent, not an inferred engine collider',teal='projected screen reference explicitly labelled; world numbers only in separate fixed calculation',reveal='current narration cues in order',tracking='editable per-object observed landmarks; hide unobservable anchors; no extrapolation through occlusion',classification='full-screen action-led moving existing gameplay; frozen/diagram-led portions must be explanation',worldMeasurement=False,engineInternalsAsserted=False,movingPixelApproval=False)))
game('LG01','직선 빛줄기를 꺾었더니 길이 열립니다','yFRbGppLaUI',[[40,56.5],[72,85]],
 ['포털 투의 공식 공개 데모입니다. 빨간 선으로 출발점에서 큐브까지의 빛줄기를 따라가세요. 큐브를 옮기면 이어지는 선의 방향이 바뀝니다.','이번에는 다른 구간입니다. 수신 장치로 빛을 보내면 표시가 바뀌고 길이 열립니다. 출발, 방향 변경, 결과를 연결해서 보세요.','화면의 선은 투영된 관찰입니다. 실제 엔진의 계산 방식이나 거리 값은 알 수 없습니다. 다음 그래플에서도 두 연결점을 먼저 찾겠습니다.'],
 ['This is an official Portal 2 preview demonstration. Red follows the beam from its origin to the cube. Moving the cube changes the outgoing direction.','Here is a different excerpt. A beam aimed at the receiver changes its indicator and opens the route. Connect the origin, direction change and visible result.','These are projected screen observations; the engine method and world distances are unverified. Next, identify both endpoints of a grapple as well.'],
 '40 cube pickup →46 reaim and redirected red beam →50–56.5 floor changes; independent72–80 reaim/receiver indicator →80–85 passage traversed',
 'Both intervals show input/action/result, unlike16–35 which loses beam endpoints and60–66 which points upward without a readable receiver result.',
 'Cube can hide beam origin; annotate only visible straight portions. Do not draw a hidden world ray through the cube.')
game('LG02','연결선과 실제 이동 경로를 구분합니다','SSekdYTL4Ck',[[1317,1357],[1358,1380]],
 ['앞의 그래플과 다른 구간입니다. 손이 바위를 향해 연결되는 순간, 빨간 선으로 두 점을 잇겠습니다.','다음 바위를 향하면 연결점과 방향이 함께 바뀝니다. 화면의 푸른 빛과 몸이 이동한 경로를 같은 직선이라고 생각하지 마세요.','출발점과 연결점을 잇는 선분은 지금 정한 계산용 연결입니다. 몸은 공중을 이동하고 카메라도 따라 움직입니다.','뒤 구간으로 넘어갑니다. 연결을 끊고 바위 가까이에 도착한 결과까지 보세요. 그 사이의 점을 비율로 만들려면 다음 매개변수식이 필요합니다.'],
 ['This is a different excerpt from the earlier grapple. When the hand connects to a rock, red joins the two observed endpoints.','Selecting the next rock changes the endpoint and direction. Do not treat the blue effect and the body travel path as the same straight line.','The segment joining origin and attachment is our defined calculation connection. The body travels through space while the camera follows it.','We now move to the later excerpt. Observe release and arrival near the rock. Generating intermediate connection points requires the next parameter formula.'],
 '1317 approach/rock aim →1329–1344 multiple visible grapples →1353 near-rock arrival;1358 new grapple chain →1377 descent →1380 rock-side landing',
 'Fresh intervals with visible endpoint changes and arrival;reject1305–1317 village dialogue/dark pan and1383–1385 an unfinished new grapple.',
 'Hands and beam can hide attachment; use projected endpoint connector only when both endpoints visible, never assume curved effect is a straight physical path.')
game('LG03','같은 비율 계산을 새로운 두 점에 적용합니다','SSekdYTL4Ck',[[1519,1546],[1567,1594]],
 ['다른 연결 구간입니다. 빨간 선의 두 끝점을 새로 잡으세요. 바위가 바뀌면 출발점과 차이 벡터도 다시 정해야 합니다.','티가 영이면 출발, 일이면 연결점이라는 계산 규칙은 같습니다. 하지만 화면의 이동 속도가 곧 티의 값이나 미터 거리는 아닙니다.','다음 구간에서도 연결, 이동, 착지를 차례로 보세요. 손과 바위가 가려지면 선도 숨기겠습니다.','앞의 숫자는 고정 좌표에서 계산한 예시입니다. 이 게임의 측정값으로 쓰지 않습니다. 이제 세로선에서도 쓸 수 있는 표현을 찾겠습니다.'],
 ['In another connection, identify the two red endpoints afresh. A new rock requires a new origin and displacement.','The calculation rule remains: t zero is the origin and t one the attachment. Screen travel speed is not itself t or a distance in meters.','In the following excerpt, observe connection, travel and landing in order. Hide the line when the hand or rock is obscured.','Our earlier numbers were a fixed-coordinate example, not measurements from this game. Next, find a representation that also handles vertical lines.'],
 '1519–1525 grapple →1528 rock arrival →1537–1543 new connection →1546 standing;1567 approach →1573 grapple →1576 arrival →1579–1585 grapple →1594 wooden platform arrival',
 'Complete travel outcomes with distinct visible endpoint updates;reject1546–1567 dark cave walking as a connection example.',
 'Endpoint glyphs glow but not all rocks are visible; hide projected connector at particles1534 and camera occlusion, reset at the independent1567 cut.')
game('LG04','둥근 머리와 움직이는 몸의 범위','4s7nMfXt8uQ',[[571,599]],
 ['앞 장면과 다른 마을 구간입니다. 파란 캐릭터의 둥근 머리를 빨간 윤곽으로 따라가세요. 몸의 다리와 팔은 머리 바깥으로 뻗습니다.','청록색 둥근 범위는 설명을 위해 정한 화면상의 비교입니다. 실제 게임의 판정 구나 피해 반경을 측정한 것이 아닙니다.','몸이 움직일 때도 머리와 몸을 구별해 보세요. 다음 계산에서는 중심과 반지름을 직접 정한 구로 안팎을 검사합니다.'],
 ['This is a different village excerpt. Red follows a blue character round head while its legs and arms extend beyond that head.','The teal round range is an illustrative screen comparison, not a measured game collision sphere or damage radius.','Distinguish head and body as they move. The next calculation tests a sphere whose center and radius we explicitly define.'],
 '571 approaching blue/gray bodies →575 head/body silhouettes near camera →578 body turns →581–599 bodies separate and new targets approach',
 'Round head and thin extended limbs are clearer than original daylight cart effects, so viewers can distinguish the visible shape from the chosen round proxy.',
 'Overlapping bodies and red/green effects; hide obscured head contour, no fabricated back half or damage region.')
game('LG05','상자가 겹쳐도 몸의 접촉과는 다릅니다','4s7nMfXt8uQ',[[600,620],[630,652]],
 ['겹침 계산을 마을의 움직임과 비교해 보겠습니다. 빨간 선은 보이는 몸의 윤곽이고, 파란 범위는 그 몸을 감싸도록 정한 화면상의 상자입니다.','상자에는 팔 사이와 다리 옆의 빈 공간도 들어갑니다. 두 상자가 겹쳐 보인다고 몸이 실제로 닿았다고 결론 내릴 수는 없습니다.','이제 다른 구간입니다. 가까운 몸과 멀리 있는 몸은 카메라로 겹쳐 보일 수도 있습니다. 화면의 상자 겹침은 월드에서의 겹침 증거가 아닙니다.','경계는 다음 검사 후보를 좁히는 도구입니다. 실제 접촉을 판단하려면 좌표와 물체 모양으로 더 검사해야 합니다.'],
 ['Compare our overlap calculation with moving village bodies. Red follows visible contours; blue is our explicitly defined enclosing screen box.','The box includes empty regions between arms and beside legs. Apparent box overlap alone cannot establish actual body contact.','Here is a different excerpt. Near and distant bodies can overlap through the camera, so screen overlap is not evidence of world overlap.','Bounds narrow candidates for the next test. Contact needs further checks in the defined coordinates and geometry.'],
 '600 gray/green approaches →605 gray extends arms →614–617 gray advances/swings →620 camera turns;630 blue nearby →642 two blue bodies near →648 body at stairs →652 wide separated view',
 'Visible silhouettes change and separate; unlike close crop669, these cuts show empty space and clearer relationships between different bodies.',
 'Weapon, projectiles and other bodies overlap contours; annotate only observable extrema and hide lines during effect occlusion.')
game('LG06','몸의 회전과 화면 범위의 변화를 나눠 봅니다','4s7nMfXt8uQ',[[665,676],[678,698],[731,739]],
 ['다른 시점의 짧은 게임 장면입니다. 같은 큰 몸이 돌면서 등과 앞쪽이 바뀝니다. 빨간 윤곽과 파란 화면 범위의 변화를 보세요.','다시 플레이 화면입니다. 몸의 자세와 카메라 위치가 모두 바뀔 수 있으므로, 화면 범위만으로 월드 회전 값을 되찾지는 못합니다.','뒤 구간에서는 가까운 파란 몸이 다른 방향으로 지나갑니다. 가려진 윤곽은 숨기고, 보이는 부분만 따라가겠습니다.','앞에서 계산한 사십오 도는 고정 축의 예시입니다. 지금의 측정 각도가 아닙니다. 다음에는 카메라만 바뀌는 구조물과 구별하겠습니다.'],
 ['This brief game shot uses a different viewpoint. The same large body turns from a back view to its front. Watch red contours and the blue screen extent change.','Back in gameplay, both pose and camera can change. Screen extents alone cannot recover world rotation values.','In the later excerpt, a nearby blue body moves in another direction. Hide obscured contours and follow only the visible parts.','The earlier forty-five degrees was a fixed-axis calculation, not a measurement here. Next, separate this from structures viewed by a changing camera.'],
 '665 two gray figures at gate →666–675 large gray turns back to front;678–698 same large moving targets observed during attacks;731–739 blue moving close to hut',
 'The gate shot provides an identifiable turning body. Later moving cuts make camera/occlusion limits explicit rather than presenting a screen rectangle as the engine AABB.',
 'Close crop669 and explosion684–687 hide parts; do not track unobservable extrema, and announce each viewpoint/cut reset.')
game('LG07','빈 공간을 포함한 범위와 실제 윤곽','4s7nMfXt8uQ',[[560,571],[652,665],[723,731]],
 ['다른 구간에서 고정된 집을 가까이 지나갑니다. 빨간 선으로 보이는 벽과 기둥을 따라가고, 파란 화면 범위와 빈 공간을 비교하세요.','넓은 마을 시점으로 바뀝니다. 카메라가 움직여 화면 범위는 바뀌지만, 그것만으로 집의 월드 경계가 달라졌다고 말할 수는 없습니다.','다시 집 가까이에서 보겠습니다. 계산용 상자에 포함된 빈 공간은 실제 벽의 점과 다릅니다. 다음 장면에서 무엇을 감쌀지 먼저 정하는 이유가 여기 있습니다.'],
 ['In a different excerpt, pass a stationary house. Red follows its visible wall and posts; compare them with the blue screen extent and included empty space.','The view changes to the wider village. Camera motion changes the screen extent without establishing a changed world bound for the stationary house.','Observe another close house view. Empty space included in a calculation box differs from actual wall points. That motivates defining what the next bound must enclose.'],
 '560 wall and posts close →563 walk along wall →566–571 wide village;652–665 wide walk and turn;723–731 walk into/around hut and return view',
 'These moving camera examples contain stable building geometry, contrasting the moving body shots and motivating point-set versus whole-box inputs.',
 'Weapon occludes lower wall and pillars hide rear edges; track only visible face/edges, no invented world axes or camera-invariant box measurement.')
# Remove source intervals overlapping the retained chapter, then author their
# replacements after playing the new official Steam recording in full.
scenes=[s for s in scenes if s['id'] not in ['LG04','LG05']]
game('LG04','둥근 머리와 길쭉한 몸을 나눠 봅니다','4s7nMfXt8uQ',[[633,650]],
 ['다른 구간입니다. 파란 몸의 둥근 머리는 빨간 윤곽으로, 길쭉한 팔과 다리는 따로 따라가세요.','청록색 둥근 범위는 화면상의 설명용 비교입니다. 실제 판정 구가 아닙니다. 다음에는 중심과 반지름을 직접 정해 구의 안팎을 계산합니다.'],
 ['This is a different excerpt. Red follows the blue body round head; distinguish its extended arms and legs.','The teal round range is an illustrative screen comparison, not the game collision sphere. Next, define a center and radius to test a sphere.'],
 '633 blue silhouette near hut →642 blue bodies approach →645–648 body passes stairs →650 wide view',
 'No overlap with retained578–632. Rounded head and extended body remain observable; rejected571–599 repeats the retained chapter.',
 'Post, flames and other bodies can obscure head; hide the affected outlines rather than inferring their extent.')
game('LG05','옮겨진 큐브의 윤곽과 감싸는 범위','portal2-steam-5787',[[48,88.5]],
 ['새로운 포털 투 공식 데모입니다. 발판에 포털을 놓고 버튼을 누르자 큐브가 이동합니다. 큐브가 보일 때 빨간 윤곽을 따라가세요.','큐브를 집어 들고 옮겨 놓는 동안 보이는 방향과 화면 범위가 바뀝니다. 파란 상자는 그 순간의 보이는 윤곽을 감싸는 비교입니다.','모서리의 빈 공간도 상자에 들어갑니다. 빛줄기에 닿거나 장치 표시가 바뀌었다고 해서, 이 파란 상자가 실제 내부 판정이라고 결론 내리지는 않겠습니다.','출발, 이동, 놓인 결과를 확인했습니다. 다음 게임에서는 상자 겹침이 실제 몸의 접촉과 다른 이유를 이어서 보겠습니다.'],
 ['This is a new official Portal 2 preview. Placing portals and pressing a button moves the cube. Red follows its outline when visible.','Picking up, moving and placing it changes its visible orientation and screen extent. Blue illustrates an enclosure of the observed outline at that moment.','The box also includes empty corner regions. A beam contact or changed indicator does not establish this blue box as the engine collision method.','We have observed the origin, movement and placed result. Next, distinguish enclosing-box overlap from actual body contact.'],
 '48 portal platform view →50–54 portals placed →61–62 button pressed →68–75 cube transported →76–82 held/placed cube →84 lifted cube redirects beam →86–88 indicator check and path',
 'Fresh official recording: complete manipulation and result, visible cube faces/contour, no repeated baseline source ranges. Reject0–17 diagram intro and89–105 branding.',
 'Cube initially hidden until transported, then gun can cover lower corners; reveal geometry only on visible cube, hide near portals and occlusion.')
history=[]
for f in (ROOT/'production/batches/game-math-part2-full-series/lessons').glob('*.json'):
 lesson=read(f)
 for s in lesson.get('scenes',[]):
  if s.get('sourceId') not in ['SSekdYTL4Ck','4s7nMfXt8uQ','yFRbGppLaUI']:continue
  for seg in s.get('sourceSegments',[dict(in_=s.get('in',0),maxSeconds=s.get('maxSeconds',0))]):
   a=seg.get('in',seg.get('in_',0));z=a+seg.get('maxSeconds',0)
   for n in scenes:
    if n['sourceId']==s['sourceId']:
     for x,y in n['intervals']:
      if max(a,x)<min(z,y):history.append(dict(newScene=n['id'],existingLesson=lesson.get('slug',f.stem),existingScene=s['id'],overlap=[max(a,x),min(z,y)]))
for s in scenes:s['selection']['priorUseOverlap']=[r for r in history if r['newScene']==s['id']]
proofs=[dict(path=(O/f/'native-ended-ax.txt').relative_to(ROOT).as_posix(),sha256=hashlib.sha256((O/f/'native-ended-ax.txt').read_bytes()).hexdigest()) for f in ['lines-portal-candidates','lines-post-candidates','lines-bound-candidates','lines-funnel-candidates']]
out=dict(revisionOf='game-math-lines-bounds',reviewedAt=datetime.datetime.now().astimezone().isoformat(),scenes=scenes,review=dict(allSelectedNativePlaybackCompared=True,denseActionPixelsCompared=True,nativeProofs=proofs,priorUse='Existing recordings reused deliberately; selected ranges checked against all current PART2 lesson source intervals. Overlaps below are disclosed, not labelled fresh.',overlaps=history,rights='NCR uploader explicit recording reuse statements retained; Valve official video policy retained for2010 preview. No source audio; game-IP/human rights pending.',rightsPrimary='https://store.steampowered.com/video_policy/',rejected=[dict(source='Portal2',interval=[16,35],reason='Beam endpoints lost during camera turn; no complete action/result.'),dict(source='Portal2',interval=[60,72],reason='Upward view and moving cube without readable receiving result.'),dict(source='Uncle',interval=[1305,1317],reason='Dialogue and dark pan rather than visible endpoint/action/result.'),dict(source='Uncle',interval=[1546,1567],reason='Cave wandering and occlusion, weaker connection example.'),dict(source='Sam2',interval=[705,721],reason='Red-screen damage and overlapping explosions obscure bodies; not chosen for geometry teaching.')],annotationsAndFinalRender='pending',narrationAuthoredAfterComparison=True))
(B/'lines-game-insertions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(newActualScenes=len(scenes),capacities=[sum(s['maximumSeconds'] for s in scenes[:3]),sum(s['maximumSeconds'] for s in scenes[3:])],priorUseOverlaps=history,ttsComplete=False),ensure_ascii=False))
