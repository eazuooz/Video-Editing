"""Original meaning-paired subtitles; no inferred speech timing."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
DATA={
'shorts-spiderman-swing-anchor': '''
스파이더맨은 거미줄이 어디에 붙느냐에 따라 || Where Spider-Man’s web attaches
내려가는 깊이와 돌아 나가는 길이 달라집니다. || changes the depth and path of the swing.
그런데 플레이어는 || Yet the player
건물의 한 점을 매번 조준하지 않죠. || does not aim at a building point every time.
개발진은 가려는 방향을 받아, || The developers take the intended travel direction
어울리는 부착점을 고르게 했습니다. || and choose a suitable attachment point.

처음에는 여러 선을 쏴서 || An early approach cast multiple lines
건물에 닿는 곳을 찾았습니다. || to find places where they meet buildings.
이런 검사를 레이캐스트라고 합니다. || This kind of test is called a raycast.
하지만 검사 선 사이로 || But between those test lines,
가느다란 구조물이나 모서리가 빠질 수 있습니다. || thin structures and corners could be missed.
선을 늘리는 것만으로는 다루기 어려웠습니다. || Adding more rays alone was not a convenient fix.

그래서 건물을 단순한 상자 영역으로 표시했습니다. || Buildings were marked with simple box volumes.
연속된 면에서 후보를 고르면 || Choosing candidates on continuous faces
선 사이의 빈틈 문제를 줄일 수 있죠. || helps reduce the gaps between test lines.
넓은 도시의 표시 작업은 || Marking the large city
후디니 도구로 자동화했고, || was automated with Houdini tools.
마지막에는 실제 지형에 닿는지도 검사했습니다. || A final check tested the actual geometry.

다음은 기준점을 만듭니다. || Next, construct an ideal reference.
스틱 방향과 원하는 줄의 길이, 기울기를 이용해 || Use stick direction, desired rope length and slope
좋은 위치를 먼저 생각하는 겁니다. || to identify a good starting position.
건물 면에서 가까운 점과 진행 방향 쪽 점을 조합하고, || Combine nearby and travel-oriented face candidates,
너무 깊게 떨어질 후보는 위치를 다듬습니다. || and refine those that would cause excessive drops.

후보가 여러 개면 || When there are several candidates,
방향, 거리, 기울기 같은 조건으로 점수를 매깁니다. || score factors such as direction, distance and slope.
점수가 좋은 부착점을 고르되, || Choose a well-scoring attachment,
나쁜 곳에 억지로 줄을 거는 것은 피합니다. || while avoiding unsuitable points.
개발 도구는 선택된 점과 이동 기록을 보여 주어 || Debug views of selected points and movement history
조정을 도왔습니다. || helped the developers tune the behavior.

줄이 팽팽해진 뒤에는 || Once the web is taut,
중력과 줄의 방향을 고려해 스윙이 이어집니다. || gravity and rope direction shape the swing.
좋은 부착점을 고르는 과정이 앞에 있어야, || Choosing a suitable attachment first
플레이어가 원하는 쪽으로 시원하게 나갈 수 있죠. || helps support the player’s intended direction.
조준할 점을 대신 골라 주어, || The game handles point selection,
우리는 이동할 방향에 집중할 수 있는 겁니다. || so we can focus on where to travel.
''',
'shorts-control-destruction-pipeline': '''
컨트롤에서 책상이 부서지는 장면은 || A desk breaking in Control
큰 판자와 작은 파편, 먼지가 함께 보입니다. || combines large planks, small fragments and dust.
이 반응을 만들려면 || To create this response,
부술 순간만 계산해서는 부족합니다. || calculating only the moment of impact is not enough.
어떤 재질을 어디서 나누고, || Materials and fracture locations,
무엇으로 이어 둘지 미리 준비해야 하죠. || along with their connections, need preparation.

개발진은 큰 물체에서 조각, || The developers considered layers from whole objects
더 작은 입자로 이어지는 크기의 층을 다뤘습니다. || to fragments and smaller particles.
큰 덩어리는 형태를 바꾸고, || Large pieces change the shape,
작은 파편과 먼지는 충격을 채웁니다. || while small fragments and dust fill out the impact.
모든 먼지까지 똑같이 무거운 물리 조각으로 || Even the smallest dust need not be treated
계산할 필요는 없는 겁니다. || as an equally expensive simulated body.

반복 작업은 재질 데이터와 규칙으로 줄였습니다. || Material data and rules reduced repetitive work.
나무와 유리가 같은 모양으로 깨지면 어색하겠죠. || Wood and glass should not fracture identically.
재질에 맞춰 나누는 방법을 정하고, || Define material-appropriate fracture methods,
큰 조각 아래에 작은 조각이 연결된 계층을 만듭니다. || then build a hierarchy of large and small fragments.

나누기만 하면 물체는 처음부터 흩어집니다. || Fracturing alone would leave loose pieces.
그래서 조각 사이의 결합과 강도를 함께 준비합니다. || Prepare the connections and their strength as well.
후디니에서 만든 조각과 물리 정보를 || Transfer Houdini’s fragments and physics data
엔진으로 옮기면, || into the engine
어디가 떨어지고 무엇이 붙어 남을지 다룰 수 있습니다. || to control what separates and what stays attached.

실행 중에는 충격으로 연결이 풀리고 || At runtime, impacts can release connections
물리 조각이 움직입니다. || and the simulated pieces move.
부서짐과 충돌 같은 사건은 || Events such as breaking and collisions
재질에 맞는 작은 파편과 먼지도 부릅니다. || also trigger material-appropriate debris and dust.
큰 조각의 움직임과 작은 이펙트를 묶어 || Combining large-piece motion and smaller effects
충격을 읽기 좋게 만드는 거죠. || makes the impact easier to read.

표면의 자국도 결과를 풍부하게 합니다. || Surface marks also enrich the result.
다만 표면에 그린 흔적과 || But a mark drawn on a surface
실제로 뚫린 구멍은 구별해야 하죠. || is different from an actual geometric hole.
컨트롤의 파괴는 준비된 조각, 연결 규칙, || Control’s destruction links prepared fragments, bonds,
실행 중 물리, 작은 흔적이 이어진 제작 과정입니다. || runtime physics and smaller visual traces.
'''
}
def main():
    spec=importlib.util.spec_from_file_location('ot12_sc_caption_writer',HERE/'prepare-camera-caption-clauses-v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    for slug,text in DATA.items():
        m.P=m.ROOT/'projects'/slug;m.PAIRS=[[line.split(' || ',1)for line in block.splitlines()]for block in text.strip().split('\n\n')];m.main()
if __name__=='__main__':main()
