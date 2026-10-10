"""Freeze compared, observed Portal surface actions before dependent narration.

Keeps original22 dictionaries/media untouched. These remain screen observations,
not measurements of hidden game-world planes, colliders or mesh triangles.
"""
from pathlib import Path
import json,datetime,hashlib,copy
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
flow=read(B/'planes-flow-draft.json')
assert not any((ROOT/'shared/output/narration/game-math-planes-teaching-additions-v2').rglob('*.wav'))
# Tighten only this unrecorded draft; preserve every prerequisite and example.
replace={
'PB05':([
'삼각형의 변 길이를 알았습니다. 이제 점이 세 꼭짓점과 연결되는 비율을 구하려고 넓이를 계산합니다.',
'앞의 법선 예제는 가로 육, 세로 사이었습니다. 지금은 세 넓이 공식을 비교하기 쉬운 가로 사, 세로 삼의 별도 삼각형을 씁니다. 가중치 예제에서는 육과 사로 돌아옵니다.'
],[
'We know the side lengths. Area will let us describe a point in proportions of the three vertices.',
'The normal example used six and four. Compare the three area formulas on a separate four-by-three triangle; return to six and four for the weights.'
]),
'PB06':([
'앞 강의의 중간점은 두 위치를 반씩 섞었습니다. 삼각형은 이를 세 꼭짓점으로 늘립니다. 좌표 예제는 처음의 가로 육, 세로 사로 돌아옵니다.',
'첫 꼭짓점 이십 퍼센트, 둘째 삼십 퍼센트, 셋째 오십 퍼센트면 합은 백 퍼센트입니다. 각 위치에 비율을 곱해 더합니다. 이 비율이 무게중심 좌표입니다. 이름과 달리 실제 질량을 반드시 재는 것은 아닙니다.'
],[
'The earlier midpoint mixed two positions equally. Extend that idea to three vertices, returning to the original six-by-four triangle.',
'Twenty, thirty and fifty percent total one hundred percent. Multiply each position by its proportion and add. These are barycentric coordinates; the name does not require real masses.'
]),
'PB07':([
'비율을 넣어 일 점 팔, 이, 영을 만들었습니다. 이번에는 그 점에서 비율을 거꾸로 구합니다. 삼각형과 점은 그대로입니다.',
'가로 육, 세로 사인 전체 넓이는 십이입니다. 점을 꼭짓점들과 이으면 부분 넓이는 이 점 사, 삼 점 육, 육입니다. 십이로 나누면 영 점 이, 영 점 삼, 영 점 오입니다. 밖의 점도 다루려면 다음 계산의 넓이 부호를 유지해야 합니다.'
],[
'Weights constructed one point eight, two, zero. Recover the weights from that same point and triangle.',
'The six-by-four triangle has area twelve. Joining the point to the vertices gives subareas two point four, three point six and six. Divide by twelve to recover point two, point three and point five. Keep signed areas to handle outside points.'
]),
'PB08':([
'삼각형 주소를 구했습니다. 하지만 정면에서 보면 면 위로 떨어진 점도 같은 위치에 보일 수 있습니다.',
'삼각형은 제트가 영인 면입니다. 일 점 팔, 이, 영과 일 점 팔, 이, 칠은 엑스와 와이가 같아도 둘째 점은 면에서 칠만큼 떨어져 있습니다. 투영 위치와 원래 점이 면 위인지 따로 검사해야 합니다. 그림자 비유는 위치 겹침만 설명하며 실제 조명 계산은 아닙니다.'
],[
'We found a triangle address. Viewed straight on, a point away from the plane can appear at the same position.',
'The triangle lies at z zero. One point eight, two, zero and one point eight, two, seven share x and y, but the second is seven units off-plane. Test projected address and coplanarity separately. The shadow analogy explains position overlap, not lighting.'
]),
}
beforeChars=sum(len(t) for s in flow['additions'] for t in s['ko'])
for s in flow['additions']:
 if s['id'] in replace:s['ko'],s['en']=replace[s['id']]
flow['unrecordedDraftTightening']={'originalKoCharacters':beforeChars,'currentKoCharacters':sum(len(t) for s in flow['additions'] for t in s['ko']),'baselineMaterialRemoved':False,'purpose':'remove draft verbal repetition while retaining all prerequisites, numerical examples, transitions and analogy limits; durations must follow measured voice'}
flow['orders']=[
 ['PF01','01','02','PB01','PG01','03','PB02','04','PG02','05','PB03','06','PB04','07','08','PG03','PC09','09','PF02'],
 ['PF03','10','11','PB05','PG04','12','PB06','13','14','15','PB07','16','17','PB08','18','PG06','19','PB09','20','PG07','21','22']
]
write(B/'planes-flow-draft.json',flow)
proofs={key:read(O/key/'native-playback.json') for key in ['planes-source-candidates','planes-portal-secondary','planes-moving-surfaces','planes-fresh-official','planes-extra-candidates']}
assert all(x['ended'] and x['rate']==1 for rows in proofs.values() for x in rows)
sources={r['id']:r for key in ['planes-source-candidates','planes-portal-secondary','planes-moving-surfaces'] for r in read(O/key/'candidate-records.json')}
for r in sources.values():assert hashlib.sha256((ROOT/r['sourceFile']).read_bytes()).hexdigest()==r['sha256']
rows=[]
def scene(ident,title,groups,ko,en,visible,reason,occlusion,starts):
 segments=[{'sourceId':sid,'sourceFile':sources[sid]['sourceFile'],'sourceSha256':sources[sid]['sha256'],'in':a,'maxSeconds':z-a} for sid,a,z in groups]
 capacity=sum(s['maxSeconds'] for s in segments)
 row={'id':ident,'title':title,'kind':'actual','sourceType':'actual-footage','sourceId':groups[0][0],'intervals':[[a,z] for sid,a,z in groups],'sourceSegments':segments,'sourceFile':segments[0]['sourceFile'],'maximumSeconds':capacity,'ko':ko,'en':en,'sourceGroupStartsAtLines':starts,
 'selection':{'visibleBeforeActionAfter':visible,'chosenReason':reason,'camera':'Keep each native action at1x. Announce the source/view changes in narration; reset landmarks at actual cuts.','occlusion':occlusion,'UI':'Portal reticle/weapon and retained preview framing. Label above bottom-center captions, away from reticle and active indicators.','nativeAndDenseComparison':True,'finalAnnotatedPixels':'pending','priorUseOverlap':[]},
 'annotation':{'red':'visible surface edge/connection','blue':'visible query point or comparison target','teal':'projected surface patch/reference axes','reveal':'narration order; per-source-group reset','tracking':'editable observed object/camera landmarks; hide during occlusion/cuts; never extrapolate unobserved corners','classification':'full-screen action-led existing gameplay; diagram-led/frozen portions separately explanation','worldMeasurement':False,'engineInternalsAsserted':False,'movingPixelApproval':False}}
 assert len(starts)==len(groups)
 rows.append(row)
scene('PG01','바닥에서 떨어졌다가 표면으로 돌아옵니다',[
 ('portal2-steam-5791',14,43),('portal2-steam-5788',16,35)], [
 '포털 투의 공개 데모입니다. 파란 바닥에서 튀어 오른 뒤 다시 표면으로 돌아옵니다. 빨간 선은 보이는 바닥의 경계, 푸른 점은 움직임을 볼 기준입니다. 화면의 높이를 실제 거리로 재는 것은 아닙니다.',
 '다른 장치로 넘어갑니다. 큐브가 발사판에서 떠나고 버튼 쪽으로 이동하는 시작과 결과를 보세요. 표면을 따라가는 움직임과 표면에서 떨어지는 움직임은 다릅니다. 그래서 방금의 법선 방향으로 거리를 따로 구합니다.'
 ],[
 'In this Portal 2 preview, bounce from the blue floor and return to a surface. Red follows a visible floor boundary and blue marks the observed moving reference. Screen height is not measured world distance.',
 'Here is another device. Watch the cube leave a faith plate and move toward the button. Travel along a surface differs from travel away from it, which is why we use the normal for distance.'
 ],'14–43 blue floor/wall contact →bounce/travel →platform contact;16–35 independent cube launch →button-side result','Sustained visible contact/departure/result outperforms promotional montage, dark shop scenes or a two-second combat bridge.','Hide anchors when gel, cube or weapon covers the observed surface; perpendicular world arrow belongs to explanation, not inferred camera direction.',[0,1])
scene('PG02','발판의 위치와 경사를 따로 봅니다',[
 ('portal2-steam-5795',14,26),('portal2-steam-5795',26,43.5),('portal2-steam-5795',48,61)], [
 '이번에는 주황색 바닥입니다. 같은 표면을 따라 빨라지는 이동을 보세요. 색이 바뀌었다고 방금 계산한 법선이나 거리를 그대로 알 수 있는 것은 아닙니다.',
 '다음 구간에서는 버튼을 누른 뒤 경사진 발판에 젤이 내려옵니다. 수평 바닥과 기울어진 발판은 방향이 다릅니다. 빨간 선은 눈에 보이는 발판 가장자리만 따라갑니다.',
 '이어서 틈을 건너 반대편에 도착합니다. 도착할 표면의 위치와 방향을 함께 알아야 합니다. 다음 설명에서는 같은 점을 수직으로 옮겨 가장 가까운 표면 위치를 구하겠습니다.'
 ],[
 'Now watch travel along the orange floor. Its color does not reveal the normal or distance from our previous calculation.',
 'In the next excerpt, a button changes the setup and gel reaches a tilted ramp. A horizontal floor and tilted platform have different orientations. Red follows only the visible platform edge.',
 'Next, cross the gap and reach the other side. Both position and orientation matter. The next explanation moves the same point perpendicularly to find its closest plane location.'
 ],'14–26 painted floor and travel;26–43.5 button →gel/ramp change;48–61 run →gap crossing →opposite-side arrival','Keep complete observed operations;reject43.5–48 foreground gel occlusion and66–76 a funnel unrelated to this distance/normal question.','Hide during gel blobs, weapon occlusion and actual cuts. Do not call projected edge angles world slope measurements.',[0,1,2])
scene('PG03','방향이 바뀌어도 경계 순서를 따라갑니다',[
 ('portal2-steam-80739',18,30.5),('portal2-steam-5786',66,86)], [
 '짧은 여러 장면으로 방향이 다른 패널을 비교합니다. 한 물체의 연속 동작은 아닙니다. 들어 올리거나 기울이면 보이는 가장자리도 달라집니다. 가려진 변은 그리지 않습니다.',
 '다른 구간에서는 로봇을 집어 장치에 연결하자 벽이 열립니다. 평면 위치만으로는 열린 통로의 끝을 알 수 없습니다. 다음에는 경계의 꼭짓점을 둘레 순서대로 모아 면 방향을 구합니다.'
 ],[
 'Compare differently oriented panels in several short shots, not one continuous object motion. Lifting or tilting changes the visible edges. Hidden edges are not drawn.',
 'In another excerpt, connect the robot to the device and the wall opens. A plane alone does not define the opening boundary. Next, accumulate boundary vertices in their perimeter order to find orientation.'
 ],'18–30.5 multiple explicitly announced lift/tilt/steps shots;66–86 robot pickup →plug-in →wall opening','Panels are chosen only as visibly changing surface comparisons with explicit camera resets. Wheatley86–104 rejected after fine review: rails, darkness, robot/gun and fades obscure a reliable three-corner patch.','Reset every panel cut;hide dark overhead/occluded patches. The66–86 device action gives finite opening purpose, not evidence of Newell implementation.',[0,1])
scene('PG04','면 위여도 통로 안인지 따로 확인합니다',[
 ('portal2-steam-5790',19.5,35.5),('portal2-steam-5790',36.5,55.5),('portal2-steam-5926',34,41)], [
 '바닥의 포털 가까이 있는 터릿이 장치에 빨려 올라갑니다. 빨간 선은 보이는 바닥 경계입니다. 면의 방향을 아는 것과 어느 범위가 실제 통로인지 아는 것은 다릅니다.',
 '다음 복도에서는 바닥과 벽의 포털을 옮기자 패널의 이동 경로가 바뀝니다. 파편이 경계를 가리는 동안은 도형을 숨기겠습니다. 다시 보이는 표면에서 꼭짓점과 안쪽 위치를 구분해 보세요.',
 '짧은 협동 플레이에서는 포털을 거쳐 발판에 도착합니다. 유한한 발판의 끝이 있다는 점을 보세요. 이제 삼각형 넓이로 안쪽 점의 비율을 계산합니다.'
 ],[
 'A turret near a floor portal is drawn into the device. Red marks the visible floor boundary. Knowing plane orientation differs from knowing the finite passage region.',
 'In the next corridor, moving floor and wall portals changes the panels\' path. Hide geometry while debris obscures the edges; distinguish corners and interior positions when the surface returns.',
 'A short cooperative excerpt passes through a portal and reaches a finite platform. Notice its edge. Next use triangle area to calculate an interior point\'s proportions.'
 ],'19.5–35.5 turret placement →vacuum lift;36.5–55.5 portals/panels →debris →return;34–41 independent launch →platform landing','Bright, sustained floor/wall actions expose finite regions more clearly than dark/railed Wheatley86–104 or vegetation montages.','Hide debris42–48, weapon and rapid pans;Coop7s is a short outcome comparison, not a long derivation. No real engine triangles inferred.',[0,1,2])
scene('PG06','떠 있는 물체와 바닥의 투영 위치를 구분합니다',[
 ('portal2-steam-5790',55.5,70),('portal2-steam-5790',74,91)], [
 '터릿이 바닥에서 떠서 장치로 이동합니다. 물체와 아래 표면이 화면에서 겹쳐 보여도 표면 위의 같은 점이라는 뜻은 아닙니다. 두 대상을 다른 색으로 구분하겠습니다.',
 '밝은 방의 다음 구간입니다. 바닥 타일에 포털을 만든 뒤 로봇이 위로 올라갑니다. 타일의 보이는 모서리로 그린 삼각형은 설명용 투영 도형입니다. 실제 게임 메시라고 부르지 않습니다. 이 차이를 확인한 뒤 면 위와 삼각형 안을 따로 검사합니다.'
 ],[
 'The turret rises from the floor toward the device. Apparent overlap with the surface below does not mean it occupies that same plane point. Different colors distinguish the objects.',
 'In the next bright room, a floor portal precedes the robot rising. A triangle traced on visible tile corners is an illustrative projected shape, not the actual game mesh. Test coplanarity and triangle inclusion separately.'
 ],'55.5–70 turret above floor →vacuum;74–81.5 pan/aim →floor portal;82–85 barrier/debris;85.5–91 clear floor patch →robot rising','Fine0.5s samples confirm a readable bright floor patch and explicit off-surface object, unlike rejected86–104 Wheatley dark rails.','Hide75–78 rightward pans,78.5–80 turn/weapon overlap and84–85 debris as appropriate;only verified visible corners at75–77/80–83/85.5–87;reset at source-group boundary.',[0,1])
scene('PG07','같은 위치의 표면 값을 따로 생각합니다',[
 ('portal2-steam-5791',43,60),('portal2-steam-5795',61,66),('portal2-steam-5795',78,84.5)], [
 '파란 젤이 있는 발판에 닿았다가 다음 위치로 이동합니다. 표면 위치를 찾는 질문과 그 표면에 어떤 값이 저장됐는지를 묻는 질문을 구분해 보세요.',
 '다른 구간에서는 큐브가 공중으로 옮겨집니다. 물체의 위치가 바뀌어도 표면의 색을 계산하려면 먼저 어느 위치를 다루는지 정해야 합니다.',
 '마지막 파란 벽의 접촉과 튀어 오르는 결과를 보세요. 젤의 효과가 앞의 색 보간 식으로 구현됐다고 주장하지 않습니다. 같은 주소로 값을 읽는 생각을 연결했으니, 다음에는 더 큰 경계를 여러 삼각형으로 나눕니다.'
 ],[
 'Contact the blue-coated platform and move on. Separate the question of surface location from the value stored at that location.',
 'Another excerpt moves a cube through the air. Calculating a surface color still requires identifying which surface position is in question.',
 'Finally observe contact with the blue wall and the resulting bounce. This does not assert the gel effect uses our color formula. Having connected an address to its value, divide larger boundaries into triangles next.'
 ],'43–60 platform contact/fall/exit;61–66 independent airborne cube;78–84.5 wall contact →bounce','Choose separate complete visible actions;reject85+ logos and66–76 the unrelated funnel. Narration explicitly separates observed gel behavior from illustrative linear RGB.','Hide fast-turn/cube-occluded regions;surface patch/color labels explain only visible behavior;never infer barycentric implementation from gel color.',[0,1,2])
comparison=read(B/'planes-candidate-comparison.json')
for r in comparison['candidates']:
 if r['source']=='portal2-steam-5786':
  r['tentative']=[[66,86]];r['rejected']=[[0,64],[86,104],[104,176],[176,192.93]]
  r['reason']='66–86 complete pickup/plug-in/wall opening retained.86–104 rejected after all five fine sheets: robot/weapon, railing, darkness and fade obscure stable three corners. No triangle teaching claims for this interval.'
comparison.update(selectionFinal=True,chosenIntervals=[{'scene':s['id'],'segments':s['sourceSegments']} for s in rows],targetedFineReview={'Wheatley86–104':'all5 directly reviewed/rejected','Vents74–91':'all5 directly reviewed/chosen with occlusion windows','Panels18–30.5':'all4 directly reviewed;short-shot comparison with explicit narration/reset'},reviewedAt=datetime.datetime.now().astimezone().isoformat())
write(B/'planes-candidate-comparison.json',comparison)
fine=read(O/'planes-chosen-fine/index.json');fine['directlyReviewed']=True;fine['reviewDecisions']=comparison['targetedFineReview'];write(O/'planes-chosen-fine/index.json',fine)
write(B/'planes-game-insertions.json',{'revisionOf':'game-math-planes-barycentric','reviewedAt':comparison['reviewedAt'],'scenes':rows,'sourceRecords':list(sources.values()),'review':{'allSelectedNativePlaybackCompared':True,'denseActionPixelsCompared':True,'targetedFineReview':comparison['targetedFineReview'],'nativeProofs':proofs,'candidateComparison':(B/'planes-candidate-comparison.json').relative_to(ROOT).as_posix(),'overlaps':[],'priorUse':'Exact official source IDs were searched in existing lesson/revision selection records;no retained planes-baseline interval is repeated as new footage. Other familiar Portal footage is preserved only as original content.','rights':'Valve public video policy and source metadata retained;human/game-IP record pending','currentAnnotationPixelsApproved':False}})
print(json.dumps({'newExplanationKoCharacters':flow['unrecordedDraftTightening'],'newActualCapacity':sum(s['maximumSeconds'] for s in rows),'episodeCapacities':[sum(s['maximumSeconds'] for s in rows if s['id'] in order) for order in flow['orders']],'newActualScenes':len(rows)},ensure_ascii=False))
