"""Meaning-paired subtitles, without assigning unreviewed voice timestamps."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
DATA={
'shorts-horizon-gpu-placement': '''
호라이즌 제로 던의 숲은 || A forest in Horizon Zero Dawn
나무가 많다는 것만으로 완성되지 않습니다. || takes more than simply adding trees.
길은 비워 두고, || Paths need to remain clear,
지역에 맞는 식물은 풍성해야 하죠. || while suitable plants fill each region.
개발진은 아티스트가 정한 데이터와 규칙을 || The developers turn artist-defined data and rules
그래픽 처리 장치인 지피유에서 배치로 바꾸었습니다. || into placements on the GPU, the graphics processor.

출발점은 지도입니다. || The starting point is a map.
어디에 나무를 많이 놓을지, || It stores where trees should be dense
물과 길은 어디인지 같은 정보를 저장합니다. || and where water and paths are located.
지역 설정은 식물 종류와 표현을 묶고, || Regional settings group plant types and appearance.
아티스트는 배치 지도와 자산을 조절합니다. || Artists adjust the placement maps and assets.
자동 배치에도 사람이 정하는 방향이 있습니다. || Automated placement still has human direction.

다음은 놓을 수 있는 정도, 밀도를 계산합니다. || Next, calculate how much can be placed: density.
나무가 많은 지도라도 || Even in a densely wooded area,
길이나 물에 걸린 곳은 제외하는 식입니다. || positions on paths or water can be excluded.
여러 조건을 연결한 계산을 정리하면, || Combining these conditions produces
배치 단계에서 쓸 밀도 지도가 나옵니다. || a density map for the placement stage.

이 지도에 배치 후보 점들을 대조합니다. || Candidate positions are tested against this map.
후보마다 밀도 조건을 검사하고, || Check the density condition at each candidate
통과한 점을 남깁니다. || and retain the points that pass.
점의 간격과 패턴도 다루므로, || Spacing and patterns also matter.
그냥 아무 좌표나 뽑아 나무를 쌓는 방식과는 다릅니다. || This is more than piling trees at arbitrary positions.

남은 점에는 실제 오브젝트가 들어갑니다. || Actual objects are placed at the remaining points.
지형의 높이와 방향에 맞춰 놓고, || Align them with the terrain’s height and orientation,
크기나 방향의 변화를 더할 수 있습니다. || and add variation in scale or rotation.
지도 속 한 점이 || A point in the map becomes
화면 속 풀이나 나무로 바뀌는 단계입니다. || a tuft of grass or a tree on screen.

층이 늘면 서로 겹치는 문제도 생깁니다. || More placement layers can introduce overlaps.
발표는 여러 층의 배치가 || The presentation explains how multiple layers
밀도 범위를 나눠 쓰도록 조정하는 방법을 설명합니다. || can be coordinated by sharing density ranges.
풀, 돌, 나무를 각각 채우기만 하면 끝나는 일이 아닌 거죠. || Filling grass, rocks and trees separately is not enough.

정리하면 아티스트의 지도, 배치 조건, || In order: artist maps, placement conditions,
후보 검사, 실제 오브젝트 순서입니다. || candidate tests, then actual objects.
컴퓨터가 반복 배치를 맡아 주면, || With the computer handling repetitive placement,
아티스트는 숲의 인상과 길의 흐름을 || artists can refine the forest’s character
더 빠르게 다듬을 수 있습니다. || and the flow of its paths more quickly.
''',
'shorts-inside-temporal-antialiasing': '''
인사이드처럼 가느다란 선이 많은 화면은 || Scenes with thin lines, as in INSIDE,
움직일 때 가장자리가 반짝거리기 쉽습니다. || can have shimmering edges in motion.
개발진은 지금 그린 화면에 || The developers add information
지난 화면의 정보를 보탭니다. || from a previous image to the current one.
단, 예전 화면을 그대로 겹치면 || But simply overlaying the old image
움직이는 물체에 잔상이 생길 수 있죠. || can leave ghosts behind moving objects.

먼저 매번 픽셀 안의 || First, each frame samples
조금 다른 위치를 살펴봅니다. || a slightly different position inside the pixel.
이를 지터라고 합니다. || This is called jitter.
한 장에서 놓친 가는 선의 정보를 || One image can capture thin-line information
다른 장에서 얻을 수 있으니, || that another image missed.
여러 장을 잘 모으면 || Combining those images carefully
가장자리를 더 안정적으로 표현할 수 있습니다. || can make the edges more stable.

카메라나 물체가 움직이면 || When the camera or an object moves,
같은 물체도 화면의 다른 자리에 보입니다. || the same object appears at a different screen position.
그래서 깊이와 움직임 정보를 이용해, || Depth and motion information help locate
지금 이 점이 지난 화면의 어디에 있었는지 찾습니다. || where this point was in the previous image.
이 대응 위치 찾기가 재투영입니다. || Finding that correspondence is reprojection.

하지만 방금 가려졌다 드러난 곳은 || A newly uncovered region, however,
지난 정보가 틀릴 수 있습니다. || can have incorrect historical information.
개발진은 현재 픽셀 주변의 색 범위를 살펴, || The developers examine nearby current colors
어울리지 않는 과거 색을 || and restrict unsuitable history colors
그 범위 안으로 제한합니다. || to that range.
잘못된 흔적이 계속 남지 않게 하는 과정입니다. || This helps prevent incorrect traces from persisting.

이렇게 다듬은 과거 정보와 현재 색을 섞어 || Blend the adjusted history with the current color
다음 장에서도 쓸 화면을 저장합니다. || and store the result for the next frame.
빠르게 움직이는 부분에는 || Fast-moving regions can use
별도의 모션 블러를 보완으로 쓰지만, || separate motion blur as a fallback,
그 흐림을 과거 기록에 계속 쌓지는 않습니다. || but that blur is not accumulated in the history.

작은 위치 차이로 정보를 모으고, || Gather information with small sample shifts,
같은 지점을 찾고, || find the corresponding point,
틀린 과거를 제한한 뒤 섞습니다. || restrict unsuitable history, then blend.
지난 화면이 도움이 되는 이유는 || Previous images help
오래됐기 때문이 아니라, || not simply because they are old,
지금 화면에 맞도록 골라 쓸 수 있기 때문입니다. || but because we can select information that fits now.
'''
}
def main():
    spec=importlib.util.spec_from_file_location('ot12_meaning_caption_writer',HERE/'prepare-camera-caption-clauses-v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    for slug,text in DATA.items():
        m.P=m.ROOT/'projects'/slug;m.PAIRS=[[line.split(' || ',1)for line in block.splitlines()]for block in text.strip().split('\n\n')];m.main()
if __name__=='__main__':main()
