"""One-shot CPU source packets. Research references are never production footage.

This writes original KO/EN drafts and source-to-scene mappings, not accepted audio
or video outputs. The complete exact list remains subject to actual source-action
review and existing full resource guards.
"""
from pathlib import Path
import datetime, hashlib, html, json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
REF = MEDIA / 'ten-cpu-prep-20261115'
NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p): return {'path': str(p.resolve()), 'sha256': sha(p)}
def save(p, data, new=True):
    if new: assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8', newline='\n')

# Each beat is [source location, original Korean narration, original English
# narration, concrete picture/action to prepare]. These are teaching adaptations,
# not quotations or a translated copy of the source.
TOPICS = [
{
 'suffix':'journey-sand-sparkle',
 'source':'https://advances.realtimerendering.com/s2012/thatgamecompany/SandRenderingInJourney_thatgamecompany.pptx',
 'files':['journey-sand.pptx','journey-source-order.json','journey-selected-visuals.json'],
 'readScope':'All 78 slides and correctly related speaker notes read in presentation order. Selected sparkle lesson: slides31–61, with purpose on2 and effect breakdown13–26.',
 'method':'OOXML presentation-order relationships and per-slide notes relationships; selected unchanged embedded images inspected. No complete lecture playback or native PowerPoint render.',
 'visuals':['journey-p038-0.jpeg','journey-p040-0.jpeg','journey-p049-0.jpeg','journey-p051-0.jpeg','journey-p059-0.jpeg'],
 'limits':['No claim that each grain is individually modeled.','The N dot V replacement is a developer heuristic; slide51 explicitly does not establish a mathematical proof.','Do not label a custom shader as Journey source code or infer its internal buffers from gameplay.'],
 'omitted':'Speaker biography, diffuse-light tuning, fluid interaction, and terrain height-map chapters are outside this sparkle question. They remain in the source; no reordered extracts are presented as the entire talk.',
 'terms':{'Normal':'표면이 향하는 방향','Mip':'멀리서 쓸 작은 텍스처 단계','View direction':'보는 방향'},
 'demo':'A saved Unity dune scene with a grain-normal texture: distant mip behavior, high-power specular versus view-based sparkle, and silhouette mask. Same camera path/light/geometry; each comparison changes one shader option. Label every such image as an explanatory reconstruction.',
 'beats':[
 ['slides2,13–26; opening preview', '저니의 사막은 몸을 움직이면 반짝입니다. 화면보다 작은 모래알까지 전부 입체로 만들지 않아도 이런 느낌을 낼 수 있죠. 개발진은 모래의 거친 결, 작은 반짝임, 넓은 빛을 나누어 다뤘습니다.', 'Journey’s desert sparkles as we move. That feeling does not require a separate 3D object for every tiny grain. The developers treated grainy texture, small glints, and broad highlights as separate layers.', '실제 Journey 사막에서 걷기 전·걷는 중·시선 변화. 아직 확보 전이며 발표 영상으로 대체하지 않는다.'],
 ['slides31–40', '먼저 모래가 어느 방향을 향하는지 작은 무늬로 표현합니다. 이 방향을 노멀이라고 합니다. 그런데 멀리서 쓰는 작은 텍스처에서는 방향 차이가 뭉개집니다. 저니는 이 작은 단계에서도 결이 남도록 방향의 분포를 다듬었습니다.', 'First, a small texture describes which way the grain surfaces face. Those directions are normals. Smaller textures used at a distance can average away that variation, so Journey adjusts their distribution to preserve the grainy feel.', '자체 모래면을 확대·축소하고 작은 텍스처 단계 전후 비교. 실제 게임의 내부 노멀을 추출했다는 표현 금지.'],
 ['slides41–48', '그 위에 반짝임을 올립니다. 뾰족한 반사광을 작은 결에 적용하면 정지 화면은 그럴듯합니다. 하지만 카메라가 움직일 때 밝은 점이 불안정하게 튈 수 있습니다. 반짝임 자체와 거슬리는 깜빡임을 구별해야 하는 겁니다.', 'Next come the glints. A sharp reflection on a grainy surface can look convincing in a still image. In motion, however, bright points may jump around unstably. The challenge is to keep sparkle without distracting shimmer.', '동일 경로 자체 장면에서 정지와 이동 비교. 실제 영상으로 임의의 AA 설정 전후를 조작하지 않는다.'],
 ['slides49–51', '개발진은 반짝임을 계산할 때 빛과 시선의 중간 방향 대신, 표면과 보는 방향의 관계를 사용했습니다. 카메라가 움직일 때 드러나는 작은 빛을 이렇게 조절한 거죠. 발표에서도 이것을 정확한 물리 법칙으로 증명한 것은 아닙니다.', 'The developers changed the glint calculation to use the relationship between the surface normal and the viewing direction, instead of a half-vector between light and view. This was a visual solution; the presentation does not claim a rigorous physical proof.', '노멀 화살표·시선 화살표와 N·H→N·V 의미를 자체 도식으로 단계 표시. 원문 수식을 완성된 물리 증명으로 재해석하지 않는다.'],
 ['slides52–59', '모래 언덕의 가장자리처럼 비스듬히 보이는 곳에서는 무늬가 길고 크게 번질 수 있습니다. 이런 구간을 찾아 반짝임의 적용을 줄이는 마스크를 씁니다. 모든 곳에 같은 효과를 세게 넣는 대신, 깨지는 곳을 따로 다루는 겁니다.', 'At a dune’s grazing silhouette, filtering can stretch the pattern into large features. A mask identifies troublesome regions and reduces the glitter there. The effect needs special treatment where its pattern breaks down.', '같은 자체 언덕에서 문제 구역→마스크→결과. 마스크는 최종 화면에 설명용으로만 잠깐 겹친다.'],
 ['slides60–61; closing synthesis', '마지막으로 사구에 넓게 흐르는 반사광이 큰 형태를 살립니다. 작은 결을 남기고, 시선에 따라 반짝이고, 문제 구간을 가리는 과정이 함께 작동하죠. 그래서 저니의 모래는 입자 수보다 빛을 어떻게 나눠 표현했는지가 중요합니다.', 'A broad highlight then gives the dune its larger form. Preserved grain, view-related sparkle, and a mask for troublesome regions work together. Journey’s sand depends on how its light is represented, not simply on counting grains.', '독립 실제 사막으로 돌아가 작은 결·반짝임·넓은 빛 순서로 굵은 표식과 기존 발화 안에서 요약.']]
},
{
 'suffix':'horizon-gpu-placement',
 'source':'https://www.guerrilla-games.com/media/News/Files/GDC2017_VanMuijden_GPUBasedProceduralPlacementInHorizonZeroDawn.pdf',
 'files':['horizon-placement.pdf','horizon-placement-pages.json'],
 'readScope':'Text throughout the 50 physical PDF pages read; selected placement pipeline, printed slides2–41. Image-only pages require image inspection rather than claiming extracted text.',
 'method':'Poppler text extraction and selected PDF page renders inspected; no complete lecture playback.',
 'visuals':['horizon-placement-p015.png','horizon-placement-p023.png','horizon-placement-p036.png'],
 'limits':['This source is Horizon Zero Dawn, not Forbidden West.','Do not call the world uncontrolled random placement or claim that every object is generated by this system.','Performance numbers in the talk are historical developer measurements, not our measurements.'],
 'omitted':'Implementation scheduling/performance details are retained in the source but shortened after the layer-coordination lesson. The short explains art-directed placement rather than benchmarking the engine.',
 'terms':{'Density map':'얼마나 놓을지 나타내는 지도','Procedural placement':'규칙과 데이터에 따른 배치','Ecotope':'지역별 생태·표현 설정'},
 'demo':'Saved Unity terrain with artist-painted density, road/water exclusion, deterministic point candidates, terrain alignment, and two placement layers. Show input maps and output in the same framing. It illustrates the documented logic, not Guerrilla code.',
 'beats':[
 ['slides2–7; opening preview', '호라이즌 제로 던의 숲은 나무가 많다는 것만으로 완성되지 않습니다. 길은 비워 두고, 지역에 맞는 식물은 풍성해야 하죠. 개발진은 아티스트가 정한 데이터와 규칙을 그래픽 처리 장치인 지피유에서 배치로 바꾸었습니다.', 'Horizon Zero Dawn’s forests need more than lots of trees. Paths must stay clear, while plants suit their region. The developers turn artist-directed data and rules into placement using the graphics processor, or GPU.', '독립 Zero Dawn의 숲·빈 길을 연속 구간으로 확보. Forbidden West 영상은 해당 구현의 증거로 대체하지 않는다.'],
 ['slides6–13', '출발점은 지도입니다. 어디에 나무를 많이 놓을지, 물과 길은 어디인지 같은 정보를 저장합니다. 지역 설정은 식물 종류와 표현을 묶고, 아티스트는 배치 지도와 자산을 조절합니다. 자동 배치에도 사람이 정하는 방향이 있습니다.', 'The process starts with maps: where trees should be dense, and where roads or water lie. Regional settings group vegetation and presentation choices. Artists control the maps and assets, giving automatic placement a clear direction.', '자체 지형 위 식물 밀도·길·물 지도 각각 표시. 실제 내부 지도라는 라벨 금지.'],
 ['slides14–23', '다음은 놓을 수 있는 정도, 밀도를 계산합니다. 나무가 많은 지도라도 길이나 물에 걸린 곳은 제외하는 식입니다. 여러 조건을 연결한 계산을 정리하면, 배치 단계에서 쓸 밀도 지도가 나옵니다.', 'Next, the rules produce a density value: how much may be placed here. A dense tree region can still exclude a road or water. Combining these conditions produces the map used by the placement stages.', '밀도×길 제외×물 제외를 자체 격자에 순서대로 적용. 숫자는 설명 모형 값임을 표시.'],
 ['slides24–30', '이 지도에 배치 후보 점들을 대조합니다. 후보마다 밀도 조건을 검사하고, 통과한 점을 남깁니다. 점의 간격과 패턴도 다루므로, 그냥 아무 좌표나 뽑아 나무를 쌓는 방식과는 다릅니다.', 'Candidate points are tested against that map. Each candidate is kept only when its density conditions allow it. Spacing and pattern matter too; this is more controlled than choosing arbitrary coordinates and piling trees onto them.', '자체 후보 점 전체→조건 검사→남은 점. 같은 입력에서 같은 결과를 유지하고 무작위 재추첨 편집 금지.'],
 ['slides31–33', '남은 점에는 실제 오브젝트가 들어갑니다. 지형의 높이와 방향에 맞춰 놓고, 크기나 방향의 변화를 더할 수 있습니다. 지도 속 한 점이 화면 속 풀이나 나무로 바뀌는 단계입니다.', 'The surviving points become actual objects. Placement can align them with terrain and add variation in size or orientation. A point on the map now becomes grass or a tree on screen.', '같은 자체 지형에서 점→자산·지형 정렬 순서. 기울기 화살표와 바닥 접촉 확인.'],
 ['slides34–39', '층이 늘면 서로 겹치는 문제도 생깁니다. 발표는 여러 층의 배치가 밀도 범위를 나눠 쓰도록 조정하는 방법을 설명합니다. 풀, 돌, 나무를 각각 채우기만 하면 끝나는 일이 아닌 거죠.', 'Multiple placement layers can interfere with one another. The presentation coordinates layers through density ranges and layered dithering. Filling separate grass, rock, and tree layers is only part of the problem.', '자체 두 층 중복 후보와 조정 결과를 비교. 모든 오브젝트 충돌을 완벽히 해결한다는 주장 금지.'],
 ['slide41; closing synthesis', '정리하면 아티스트의 지도, 배치 조건, 후보 검사, 실제 오브젝트 순서입니다. 컴퓨터가 반복 배치를 맡아 주면, 아티스트는 숲의 인상과 길의 흐름을 더 빠르게 다듬을 수 있습니다.', 'The sequence is artist maps, placement rules, candidate tests, then actual objects. With the computer handling repeated placement, artists can iterate more quickly on the forest’s character and the routes through it.', '실제 Zero Dawn 숲으로 복귀. 자체 입력 지도와 결과를 작은 순서표로 요약하되 원본 게임 내부 측정으로 혼합하지 않는다.']]
},
{
 'suffix':'inside-temporal-antialiasing',
 'source':'https://github.com/playdeadgames/temporal',
 'files':['inside-GDC2016_Temporal_Reprojection_AA_INSIDE.pdf','inside-presentation.txt','inside-README.md','inside-LICENSE.txt','inside-TemporalReprojection.shader','inside-TemporalReprojection.cs'],
 'readScope':'Complete presentation text, main and bonus sections; implementation overview and published source files checked. Main temporal pipeline selected. Bonus YCoCg is explicitly not an INSIDE production claim.',
 'method':'Published developer repository and Poppler PDF reading; selected rendered pipeline/clipping/blending pages inspected.',
 'visuals':['inside-GDC2016_Temporal_Reprojection_AA_INSIDE-p012.png','inside-GDC2016_Temporal_Reprojection_AA_INSIDE-p023.png','inside-GDC2016_Temporal_Reprojection_AA_INSIDE-p029.png'],
 'limits':['YCoCg appears in a bonus section and must not be described as used in INSIDE.','MIT code permission is not permission to reuse any gameplay recording or the entire presentation.','Temporal AA does not guarantee the elimination of all shimmer, blur, or ghosting.'],
 'omitted':'Benchmark numbers, optional bonus color-space techniques, and complete shader implementation are outside this beginner explanation. Motion blur is identified as an output fallback rather than stored history.',
 'terms':{'Frame':'화면 한 장','Reprojection':'지난 화면의 대응 위치 찾기','History':'저장한 지난 화면 정보','Jitter':'픽셀 안의 작은 표본 위치 변화'},
 'demo':'Saved Unity scene of fine railings and a moving subject. Separate subpixel sample pattern, depth/velocity correspondence, invalid history, neighborhood clipping and final blend. Keep camera trajectory identical; no unreviewed Unity5 shader is dropped into a modern pipeline.',
 'beats':[
 ['problem and overview before jitter', '인사이드처럼 가느다란 선이 많은 화면은 움직일 때 가장자리가 반짝거리기 쉽습니다. 개발진은 지금 그린 화면에 지난 화면의 정보를 보탭니다. 단, 예전 화면을 그대로 겹치면 움직이는 물체에 잔상이 생길 수 있죠.', 'Fine edges can shimmer in motion, as in INSIDE’s detailed scenes. Its developers use information from previous frames to help the current image. Simply overlaying an old frame, however, can leave trails behind moving objects.', '독립 INSIDE의 가는 구조물과 이동 구간 확보. 자체 AA 꺼짐/켜짐 비교를 실제 게임 설정 비교처럼 표시하지 않는다.'],
 ['jitter section', '먼저 매번 픽셀 안의 조금 다른 위치를 살펴봅니다. 이를 지터라고 합니다. 한 장에서 놓친 가는 선의 정보를 다른 장에서 얻을 수 있으니, 여러 장을 잘 모으면 가장자리를 더 안정적으로 표현할 수 있습니다.', 'First, each frame samples a slightly different location within the pixels. This is jitter. A fine edge missed by one sample may be captured by another, so combining frames can represent it more steadily.', '자체 큰 픽셀 격자에 표본 이동. 실제 최종 게임의 샘플 개수를 임의 표시하지 않는다.'],
 ['reprojection, depth and velocity sections', '카메라나 물체가 움직이면 같은 물체도 화면의 다른 자리에 보입니다. 그래서 깊이와 움직임 정보를 이용해, 지금 이 점이 지난 화면의 어디에 있었는지 찾습니다. 이 대응 위치 찾기가 재투영입니다.', 'Camera and object motion move things to different screen positions. Depth and motion information help find where a current point appeared in the previous frame. That correspondence is reprojection.', '자체 전·후 프레임의 같은 점을 실제 움직임 벡터로 연결. 문자 비율로 시간을 추정한 오버레이 금지.'],
 ['invalid history and neighborhood clipping sections', '하지만 방금 가려졌다 드러난 곳은 지난 정보가 틀릴 수 있습니다. 개발진은 현재 픽셀 주변의 색 범위를 살펴, 어울리지 않는 과거 색을 그 범위 안으로 제한합니다. 잘못된 흔적이 계속 남지 않게 하는 과정입니다.', 'History may be wrong where a surface has just become visible. The developers inspect the current pixel’s neighborhood and constrain incompatible history colors to a suitable range. This helps stop outdated information from lingering.', '자체 가림 해제 장면→유효하지 않은 과거색→주변색 범위와 클리핑. 원문은 rounded3×3 neighborhood color-box clipping임을 제작 주석에 유지.'],
 ['blending and motion-blur fallback sections', '이렇게 다듬은 과거 정보와 현재 색을 섞어 다음 장에서도 쓸 화면을 저장합니다. 빠르게 움직이는 부분에는 별도의 모션 블러를 보완으로 쓰지만, 그 흐림을 과거 기록에 계속 쌓지는 않습니다.', 'The constrained history is blended with the current color and saved for the next frame. A separate motion-blur fallback can help fast-moving fragments, but that blur is not repeatedly written into the history.', '자체 현재색+정리된 과거색→저장, 출력 전용 모션 블러는 별도 가지. 피드백 선이 모션 블러 뒤로 돌아가지 않게 한다.'],
 ['closing synthesis of main pipeline', '작은 위치 차이로 정보를 모으고, 같은 지점을 찾고, 틀린 과거를 제한한 뒤 섞습니다. 지난 화면이 도움이 되는 이유는 오래됐기 때문이 아니라, 지금 화면에 맞도록 골라 쓸 수 있기 때문입니다.', 'Sample at small offsets, find the matching point, constrain invalid history, then blend. The previous frame is useful because the system can adapt its information to the current image.', '실제 INSIDE로 복귀해 세밀한 선을 보며 지터→대응→제한→혼합 순서 요약.']]
},
{
 'suffix':'spiderman-swing-anchor',
 'source':'https://media.gdcvault.com/gdc2019/presentations/Sheahan_Doug_ConcreteJungleGym.pdf',
 'files':['spiderman-swing.pdf','spiderman-swing-pages.json'],
 'readScope':'Physical PDF pages16–81 including speaker-note pages; attachment-point selection16–66 is the selected lesson, physics67–81 provides context. The remaining lecture is not claimed as fully read.',
 'method':'Poppler extraction with slide and speaker-note page ordering preserved; attachment reference/refinement/scoring page renders inspected.',
 'visuals':['spiderman-swing-p040.png','spiderman-swing-p048.png','spiderman-swing-p059.png'],
 'limits':['This is the documented Marvel’s Spider-Man2018 implementation, not every Spider-Man game.','Input arrows in an own demonstration are known model inputs; actual recorded controller input must not be invented.','Do not infer attachment scoring or a particular raycast from an unexplained gameplay pixel.'],
 'omitted':'Most animation, parkour and later locomotion chapters are outside the selected attachment question. Basic physics is used only to connect a chosen attachment to the resulting swing.',
 'terms':{'Raycast':'선으로 부딪힐 곳 검사','Markup volume':'건물 모양을 단순하게 표시한 상자','Anchor':'거미줄이 붙는 점'},
 'demo':'Saved Unity street of box-shaped buildings with known player direction. Show ray gaps, face volumes, ideal reference, refinement and candidate scoring in source order. A later swing compares attachment points with all other inputs fixed. Clearly label illustrative scoring values.',
 'beats':[
 ['PDF16–19; opening preview', '스파이더맨은 거미줄이 어디에 붙느냐에 따라 내려가는 깊이와 돌아 나가는 길이 달라집니다. 그런데 플레이어는 건물의 한 점을 매번 조준하지 않죠. 개발진은 가려는 방향을 받아, 어울리는 부착점을 고르게 했습니다.', 'A web’s attachment point changes the depth and path of Spider-Man’s swing. Yet players do not aim at a building point every time. The developers choose a suitable attachment using the direction the player wants to travel.', '독립 Spider-Man2018의 부착→줄 팽팽해짐→스윙 구간. 확인 전 정확한 입력 방향을 게임 위에 덧그리지 않는다.'],
 ['PDF20–28', '처음에는 여러 선을 쏴서 건물에 닿는 곳을 찾았습니다. 이런 검사를 레이캐스트라고 합니다. 하지만 검사 선 사이로 가느다란 구조물이나 모서리가 빠질 수 있습니다. 선을 늘리는 것만으로는 다루기 어려웠습니다.', 'An early approach cast many lines toward nearby geometry: raycasts. Thin structures and corners could slip between those lines. Increasing their number was not a convenient solution to every case.', '자체 건물에 간격 있는 검사 선을 실제 실행해 누락 사례 확인. 원본 엔진의 레이 개수로 설명 모형 값을 제시하지 않는다.'],
 ['PDF29–38', '그래서 건물을 단순한 상자 영역으로 표시했습니다. 연속된 면에서 후보를 고르면 선 사이의 빈틈 문제를 줄일 수 있죠. 넓은 도시의 표시 작업은 후디니 도구로 자동화했고, 마지막에는 실제 지형에 닿는지도 검사했습니다.', 'Buildings were represented by simple box volumes. Continuous faces make it easier to find candidates without gaps between test rays. Houdini tools helped populate the city’s markup, and a final check could place the chosen point on real geometry.', '자체 건물 실루엣→상자 면→실제 표면 최종 검사. 단순화 상자를 충돌 원본과 같은 것으로 오인하지 않게 한다.'],
 ['PDF40–49', '다음은 기준점을 만듭니다. 스틱 방향과 원하는 줄의 길이, 기울기를 이용해 좋은 위치를 먼저 생각하는 겁니다. 건물 면에서 가까운 점과 진행 방향 쪽 점을 조합하고, 너무 깊게 떨어질 후보는 위치를 다듬습니다.', 'Next comes an ideal reference based on stick direction, desired rope length, and slope. Points on a building face are combined and refined, helping avoid attachments that would make the swing drop excessively.', '자체 알려진 입력→이상 기준점→면 위 두 후보의 조합→길이·기울기 보정. 입력 변경 없이 비교.'],
 ['PDF50–66', '후보가 여러 개면 방향, 거리, 기울기 같은 조건으로 점수를 매깁니다. 점수가 좋은 부착점을 고르되, 나쁜 곳에 억지로 줄을 거는 것은 피합니다. 개발 도구는 선택된 점과 이동 기록을 보여 주어 조정을 도왔습니다.', 'Candidates are scored for factors such as direction, distance, and slope. A good attachment wins, while unsuitable points can be rejected. Debug views of chosen points and movement history helped the developers tune the behavior.', '자체 후보 점수 표는 설명 모형 표시. 부적합 후보 탈락과 무부착 결과도 실행해 확인.'],
 ['PDF67–81; closing link to selection', '줄이 팽팽해진 뒤에는 중력과 줄의 방향을 고려해 스윙이 이어집니다. 좋은 부착점을 고르는 과정이 앞에 있어야, 플레이어가 원하는 쪽으로 시원하게 나갈 수 있죠. 조준할 점을 대신 골라 주어, 우리는 이동할 방향에 집중할 수 있는 겁니다.', 'Once the web is taut, gravity and the rope direction shape the swing. Choosing a suitable attachment first helps support the intended travel direction. The game handles point selection so players can focus on where they want to go.', '자체 부착점 두 개만 바꾼 동일 초기 조건 스윙 후 실제 게임 복귀. 자체 궤적을 실제 게임 물리 측정값으로 표시 금지.']]
},
{
 'suffix':'control-destruction-pipeline',
 'source':'https://www.youtube.com/watch?v=kODJsQGXanU',
 'files':['control-gdc.html','control-reference.info.json','control-reference.en.vtt','control-selected-source-scope.json'],
 'readScope':'Official GDC talk metadata and auto-caption text00:00–21:00 read; production pipeline/materials/hierarchy/events selected. Auto-caption wording is approximate, not verified speech.',
 'method':'Official-channel research captions, rolling captions deduplicated; source speech/complete lecture video not listened to or watched. No claim of inspecting the gameplay shown in the lecture.',
 'visuals':[],
 'limits':['Prepare fracture geometry and metadata before play; do not imply every fracture is generated from scratch at runtime on the GPU.','Houdini preparation, Northlight runtime, PhysX bodies/constraints, particles and decals have different roles.','A decal changes appearance and is not automatically a new geometry hole.'],
 'omitted':'Later talk chapters and platform/performance numbers are outside the selected preparation question. First21minutes are the reviewed text scope, not full-talk viewing.',
 'terms':{'Procedural':'데이터와 규칙에 따라 처리','Hierarchy':'큰 조각과 작은 조각의 계층','Constraint':'조각을 붙잡는 연결','Decal':'표면에 더하는 흔적'},
 'demo':'Saved Unity office prop with pre-fractured hierarchy, material metadata, detachable connections, and separate dust/decal layers. Same impact and object per comparison. It teaches the preparation/runtime distinction without claiming Northlight or PhysX implementation parity.',
 'beats':[
 ['00:00–05:00; opening preview', '컨트롤에서 책상이 부서지는 장면은 큰 판자와 작은 파편, 먼지가 함께 보입니다. 이 반응을 만들려면 부술 순간만 계산해서는 부족합니다. 어떤 재질을 어디서 나누고, 무엇으로 이어 둘지 미리 준비해야 하죠.', 'A breaking desk in Control combines large pieces, small fragments, and dust. Producing that response takes preparation: what material the object is made of, how it is divided, and how its parts stay connected.', '독립 Control 사무실에서 동일 물체의 타격 전·타격·잔해 연속 장면. 발표 클립으로 대체하지 않는다.'],
 ['05:00–08:00 granularity and workflow', '개발진은 큰 물체에서 조각, 더 작은 입자로 이어지는 크기의 층을 다뤘습니다. 큰 덩어리는 형태를 바꾸고, 작은 파편과 먼지는 충격을 채웁니다. 모든 먼지까지 똑같이 무거운 물리 조각으로 계산할 필요는 없는 겁니다.', 'The developers work across scales, from objects to chunks to fine particles. Large pieces change the shape; small debris and dust add impact. Every speck of dust need not be simulated as the same kind of heavy rigid body.', '자체 큰 조각·작은 입자·표면 흔적을 층별 켜기. 실제 게임 이펙트를 임의로 분리 추출한 것처럼 표시하지 않는다.'],
 ['08:00–11:00 data, materials and hierarchy', '반복 작업은 재질 데이터와 규칙으로 줄였습니다. 나무와 유리가 같은 모양으로 깨지면 어색하겠죠. 재질에 맞춰 나누는 방법을 정하고, 큰 조각 아래에 작은 조각이 연결된 계층을 만듭니다.', 'Material data and rules reduce repeated setup. Wood and glass should not fracture identically. Material-specific preparation divides geometry into a hierarchy, with smaller chunks beneath larger parts.', '자체 나무판·유리판을 각기 준비한 균열 규칙으로 비교. 모형 재질 분할임을 명시.'],
 ['11:00–14:30 connections and Houdini preparation', '나누기만 하면 물체는 처음부터 흩어집니다. 그래서 조각 사이의 결합과 강도를 함께 준비합니다. 후디니에서 만든 조각과 물리 정보를 엔진으로 옮기면, 어디가 떨어지고 무엇이 붙어 남을지 다룰 수 있습니다.', 'Dividing an object is not enough: it would fall apart immediately without connections. Bonds and their strength are prepared too. Fractured geometry and physics metadata move from Houdini into the engine, where connections determine what separates and what stays attached.', '자체 조각 계층→연결선·강도→타격으로 일부 연결 해제. 문 경첩 같은 남은 연결은 해당 모형에서 실제 검증한다.'],
 ['14:30–19:00 runtime budgets and events', '실행 중에는 충격으로 연결이 풀리고 물리 조각이 움직입니다. 부서짐과 충돌 같은 사건은 재질에 맞는 작은 파편과 먼지도 부릅니다. 큰 조각의 움직임과 작은 이펙트를 묶어 충격을 읽기 좋게 만드는 거죠.', 'At runtime, impacts can release connections and move the rigid pieces. Break and collision events also trigger material-appropriate particles and dust. Large-piece motion and smaller effects work together to communicate the impact.', '같은 자체 타격에서 큰 조각만→이벤트 기반 입자 추가. 성능 예산은 실제 모형 측정과 원문 보고를 구별.'],
 ['19:00–21:00 decals; closing synthesis', '표면의 자국도 결과를 풍부하게 합니다. 다만 표면에 그린 흔적과 실제로 뚫린 구멍은 구별해야 하죠. 컨트롤의 파괴는 준비된 조각, 연결 규칙, 실행 중 물리, 작은 흔적이 이어진 제작 과정입니다.', 'Surface marks add another layer, but a painted mark is different from an actual hole. Control’s destruction brings together prepared chunks, connection rules, runtime physics, and fine visual traces.', '실제 게임 결과 복귀. 준비→연결→물리→입자·흔적을 차례로 요약.']]
},
]

TOPICS += [
{
 'suffix':'returnal-particle-tentacles',
 'source':'https://housemarque.com/news/2021/9/15/returnal-vfx-breakdown',
 'files':['returnal-vfx.html'],
 'readScope':'Full developer article read, including node particles, fluids, voxelizer and trails; NODE PARTICLES is the selected lesson, in original section order.',
 'method':'Primary Housemarque developer article text; diagrams and video links are reference candidates, not cleared production footage or viewed continuous gameplay.',
 'visuals':[],
 'limits':['A child reads one-frame-old parent data; do not substitute an unspecified physics spring explanation.','Visual particle hierarchy does not establish enemy AI, damage or collision logic.','Do not claim the initial flat strips were the final cylindrical rendering.'],
 'omitted':'Fluid simulation, voxelization, bullet trails and other VFX sections are separate topics and omitted. Enemy-state readability remains part of the tentacle lesson.',
 'terms':{'Parent / Child':'움직임을 참조하는 부모·자식 관계','Frame':'화면 한 장의 시간 단계','Catmull–Rom':'점들을 따라 부드러운 곡선을 잇는 방법'},
 'demo':'Saved Unity illustrative particle chain with parent indices and explicit previous-frame buffers; branch at one node, move parent, compare immediate/current-frame following to delayed data. Generate a tube along a curve and verify normals separately. Mark this as a model rather than Housemarque engine output.',
 'beats':[
 ['NODE PARTICLES introduction; opening preview', '리터널의 적은 촉수가 살아 있는 것처럼 꿈틀거립니다. 개발진은 이런 표현에 서로 연결된 입자를 사용했습니다. 점들이 관계를 맺고, 지난 움직임을 따라가고, 그 위에 굵기 있는 표면이 만들어지는 과정을 보겠습니다.', 'Returnal’s enemies have writhing, living-looking tentacles. The developers use connected particles for this effect. We will follow their relationships, their delayed motion, and the thick surface rendered around them.', '독립 Returnal의 촉수 적 대기·공격 준비 구간. 내부 입자 위치는 실제 영상에서 추정해 찍지 않는다.'],
 ['NODE PARTICLES rigidbody approach and NGP', '처음 생각한 방법은 뼈대마다 물리 몸체를 연결하는 것이었습니다. 하지만 비용과 표현 조절에 어려움이 있었습니다. 개발진은 지피유에서 동작하는 이펙트 도구 안에서, 부모와 자식 관계를 가진 입자 구조를 발전시켰습니다.', 'An earlier approach connected rigid bodies along bones, but cost and control were limiting. The developers instead extended a parent-and-child particle structure within their GPU effects system.', '자체 뼈대 연결 개념→부모 번호를 가진 입자 구조. 실제 엔진 성능 수치를 모형 값으로 대체하지 않는다.'],
 ['NODE PARTICLES parent-child data access', '각 자식은 부모 하나를 참조하고, 부모에는 여러 자식이 달릴 수 있습니다. 여기서 자식이 읽는 것은 부모의 한 프레임 전 정보입니다. 부모가 먼저 움직이고 뒤쪽 점들이 뒤따르는 차이가 유기적인 움직임을 만듭니다.', 'Each child refers to one parent, while a parent may have several children. The child reads the parent’s data from one frame earlier. The resulting lag, as motion follows down the structure, helps produce an organic feel.', '자체 현재·직전 버퍼와 한 프레임씩 지연되는 점을 실제 실행 로그로 대조. 프레임 지연과 영상 감속을 혼동하지 않는다.'],
 ['NODE PARTICLES strips to cylindrical mesh and curves', '점의 움직임만으로는 굵은 촉수가 보이지 않습니다. 처음의 납작한 띠 대신, 점들을 따라 부드러운 곡선을 만들고 원통형 표면을 그렸습니다. 옆에서 보거나 그림자가 생겨도 부피가 읽히도록 한 겁니다.', 'Moving points alone do not make a thick tentacle. Instead of the initial flat strips, the developers use smooth curves through particle positions and render cylindrical surfaces. This gives the tentacles volume, including in their shadows.', '자체 동일 점·곡선에 띠와 원통 표면을 비교하고 측면·그림자 확인.'],
 ['NODE PARTICLES normals and temporal filtering', '표면이 뒤틀리면 빛도 이상하게 돌 수 있습니다. 그래서 표면이 향하는 방향을 부모 쪽에서 이어 받고 다듬는 별도 계산을 더했습니다. 움직임을 만드는 점과, 그 위에 안정적인 표면을 만드는 작업은 함께 필요합니다.', 'A twisting surface can also make its lighting behave badly. A separate pass propagates and refines surface directions along the structure. The moving points and the stability of their rendered surface must both be handled.', '자체 표면 방향 축·부모 방향 투영·시간 필터를 한 단계씩 표시. 주어진 모델에서 꼬임이 줄었는지 확인.'],
 ['NODE PARTICLES closing collaboration and enemy states', '이 움직임은 적이 공격을 준비할 때 같은 상태 표현에도 연결됩니다. 아티스트와 애니메이터가 타이밍을 맞춰 행동을 읽게 한 거죠. 부모의 지난 움직임을 잇는 입자와, 그 둘레를 감싼 표면이 촉수의 생동감을 함께 만듭니다.', 'The behavior also supports enemy states, including attack preparation. Artists and animators coordinate its timing to help players read the action. Delayed particle relationships and the surfaces around them work together to bring the tentacles to life.', '독립 실제 공격 준비→공격 구간으로 복귀. 촉수만으로 게임 AI 판정 시점을 측정했다고 주장하지 않는다.']]
},
{
 'suffix':'ratchet-dimension-streaming',
 'source':'https://blog.playstation.com/2023/07/18/ratchet-clank-rift-apart-pc-specs-and-new-features-revealed/',
 'files':['ratchet-streaming.html'],
 'readScope':'Full article text read; PC DirectStorage, GPU decompression, adaptive streaming and storage requirements selected in article order.',
 'method':'Official PlayStation Blog article written by Nixxes developer; no claim of reading Insomniac source code or measuring runtime loading.',
 'visuals':[],
 'limits':['The technical explanation is scoped to the PC version and its stated settings; do not relabel PS5 footage as a PC implementation measurement.','The official requirements support HDD; do not say an SSD is universally mandatory.','No invented latency, bandwidth measurement or guarantee of no loading on all machines.'],
 'omitted':'Ambient occlusion, monitor formats and unrelated PC graphics options are outside the streaming question. Requirements are retained to qualify storage claims.',
 'terms':{'Asset':'화면을 만드는 모델·텍스처 같은 자료','Decompression':'압축한 자료를 사용 가능한 형태로 풀기','Streaming':'필요한 자료를 진행 중 계속 공급'},
 'demo':'Saved Unity two-room illustrative streaming scene with known synthetic asset packets. Show storage read, decompression and upload as separate stages; diagrams must not present simulated queue times as measured PC game performance. Preload/visibility changes must be visibly distinguished.',
 'beats':[
 ['DirectStorage section opening; preview', '라쳇 앤 클랭크의 차원 전환은 화면 속 세계가 크게 바뀌는 순간입니다. 위치만 바꾼다고 끝나지는 않죠. 피시판 개발진의 설명을 따라, 다음 장면의 자료를 읽고 풀어 쓰는 과정을 보겠습니다.', 'Rift Apart’s dimension transitions can replace much of the world on screen. Changing coordinates is not enough. Following the PC developers’ explanation, let’s look at how the next scene’s data is read and made usable.', '독립 실제 PC판의 차원 전환 전·통과·후 연속 영상. 플랫폼 확인 전 PS5 장면을 PC 기술 증거로 채택하지 않는다.'],
 ['DirectStorage1.2 and GPU decompression paragraph', '게임에는 모델과 텍스처 같은 자료가 필요합니다. 압축해서 저장했다면 읽은 뒤 풀어야 합니다. 피시판은 다이렉트스토리지를 사용하고, 높은 그래픽 설정에서는 지피유 압축 해제로 자료 공급을 돕습니다.', 'The game needs assets such as models and textures. Compressed assets must be read and decompressed. The PC version uses DirectStorage, with GPU decompression helping supply data at high graphics settings.', '자체 압축 묶음→읽기→압축 해제→사용 준비 도식. 원문 버전1.2는 표시 자료에 유지하되 발화에 불필요한 버전 나열은 생략.'],
 ['CPU versus GPU decompression explanation', '보통 중앙 처리 장치인 씨피유가 맡던 압축 해제를 그래픽 장치가 도울 수 있다는 뜻입니다. 배경에서 자료가 준비되어야, 차원을 넘은 뒤 화면을 만드는 데 쓸 수 있죠. 읽기와 압축 해제는 구별되는 단계입니다.', 'The graphics processor can help with decompression traditionally handled by the CPU. Assets prepared in the background can then be used to draw the destination. Reading data and decompressing it are distinct steps.', '자체 CPU·GPU 처리 위치 비교. 실제 게임이 모든 파일을 언제나 GPU에서 푼다는 주장 금지.'],
 ['adaptive streaming paragraph', '모든 피시의 저장 속도는 같지 않습니다. 개발진은 실제로 공급할 수 있는 대역폭을 살피며 스트리밍 방식을 조절한다고 설명합니다. 빨리 읽는 장치와 느린 장치에 같은 공급 계획을 무조건 적용하지 않는 겁니다.', 'PC storage devices do not all deliver data at the same rate. The developers describe adaptive streaming that measures available bandwidth and adjusts the strategy. Different devices need not receive an identical data-supply plan.', '자체 두 공급 속도 모형에서 준비 대기 차이를 표시. 숫자는 합성 모형 수치, 실제 게임 측정 아님.'],
 ['storage support and requirements; closing', '이 기능은 빠른 저장 장치만을 위한 것은 아닙니다. 공식 피시 안내는 하드디스크도 지원하고, 더 좋은 경험을 위해 에스에스디를 권장합니다. 차원 전환의 뒤에서는 자료 읽기, 압축 해제, 속도에 맞춘 공급이 함께 움직이는 겁니다.', 'The official PC guidance supports hard drives as well, while recommending an SSD for a better experience. Behind a dimension transition are coordinated data reads, decompression, and a streaming strategy suited to the available speed.', '실제 PC 전환 결과와 읽기→풀기→공급 요약. 원문 최소/권장 조건을 정확히 표시.']]
},
{
 'suffix':'doom-push-forward-healing',
 'source':'https://www.youtube.com/watch?v=2KQNpQD8Ayo',
 'files':['doom-gdc.html','doom-reference.info.json','doom-reference.en.vtt','doom-selected-source-scope.json'],
 'readScope':'Official GDC metadata and auto-caption text00:00–04:30 and11:00–16:50 read. These windows cover push-forward goals, stagger/glory kills, rewards, chainsaw and fuel.',
 'method':'Official-channel research captions with rolling duplicates removed. Speech not independently listened to; full talk and shown game action not claimed as watched.',
 'visuals':[],
 'limits':['This is DOOM2016, not a silent substitution of Doom Eternal rules.','Health reward adjustment is not a universal equivalent ammo rubber-band rule.','Glory kills always rewarding something does not mean they always add health when health is full.'],
 'omitted':'Attack-token management and later pacing chapters are outside this health/risk/reward loop and would overlap the lock-on topic. This short is not an exhaustive combat talk summary.',
 'terms':{'Stagger':'마무리 공격이 가능한 비틀거림','Glory kill':'근접 마무리 공격','Resource loop':'행동과 자원 보상이 다시 행동으로 이어지는 순환'},
 'demo':'Saved Unity diagram/arena model of low health→engagement→stagger→close finish→reward. Known model state and health values only; keep actual DOOM HUD readable and do not fabricate recorder inputs or reward numbers.',
 'beats':[
 ['00:00–04:30 combat goals; opening preview', '둠에서 체력이 줄면 적에게 더 가까이 가야 할 때가 있습니다. 개발진은 숨어서 기다리기보다 전투에 참여할 이유를 만들고 싶었습니다. 회복이 접근과 공격으로 이어지는 순환을 보겠습니다.', 'In DOOM, low health can be a reason to move closer to an enemy. The developers wanted a reason to engage rather than wait in cover. Let’s follow the loop connecting recovery, approach, and attack.', '독립 DOOM2016의 낮은 체력→전투 접근 연속 구간. 성인 폭력 장면은 교육에 필요한 맥락과 길이로 선정하고 잔혹 묘사 강조 편집은 하지 않는다.'],
 ['stagger and second-wind explanation', '적을 공격하면 비틀거리며 마무리할 기회가 생깁니다. 이 상태가 스태거입니다. 영원히 멈춰 있는 것은 아니어서, 기회를 놓치면 적이 다시 전투에 돌아올 수 있습니다. 가까이 갈지 판단할 시간이 생기는 거죠.', 'Attacking an enemy can create a stagger window for a finishing move. The enemy does not stay helpless forever: it can recover if the opportunity is missed. That creates a decision about whether to close the distance.', '실제 스태거 표시→접근→마무리, 가능하면 별도의 회복 복귀 사례도 확보. 편집 감속 없이 상태 변화 확인.'],
 ['11:00–13:00 replenishment and glory-kill rewards', '가까이서 글로리 킬로 마무리하면 자원 보상을 얻습니다. 공격에 쓸 도구만 주는 것이 아니라, 위험을 감수하고 다가갈 이유도 주는 겁니다. 체력이 낮을 때 필요한 회복을 얻는 구조가 전진을 돕습니다.', 'A close-range glory kill provides resource rewards. It gives the player both an attack tool and a reason to risk approaching. Recovery when health is low helps support forward movement.', '실제 HUD 체력 전후와 드롭 종류를 해상도 그대로 확인. 화면 밖 드롭이나 안 보이는 증가량을 가정하지 않는다.'],
 ['13:00–14:30 health and ammo distinctions', '발표는 체력이 낮을 때 회복 보상을 조절하는 방법도 설명합니다. 다만 탄약까지 똑같이 따라가는 것은 아닙니다. 어떤 자원을 주고 얼마나 줄지는 구별해서 설계해야, 한 행동만 계속 반복하는 해법이 되지 않습니다.', 'The talk also describes adjusting health rewards when health is low. Ammunition does not follow the same adjustment rule. The type and amount of each resource need separate design, rather than treating every reward identically.', '자체 보상 흐름에서 체력·탄약 가지 분리. 실측하지 않은 드롭 확률·정확 수치 표기 금지.'],
 ['14:30–16:50 chainsaw and fuel', '탄약이 부족할 때는 전기톱이 큰 보상을 주는 역할을 합니다. 대신 연료가 필요하죠. 적에게서 자원을 얻되 그 행동에도 비용을 두어, 공격과 회복이 한쪽으로만 굴러가지 않게 한 겁니다.', 'The chainsaw provides a large ammunition reward, but requires fuel. Getting resources from enemies therefore has a cost of its own, keeping the combat loop from becoming a free, repeatable escape.', '실제 전기톱 사용 전 연료·탄약과 사용 후 드롭 확인. DOOM2016과 Eternal UI 혼합 금지.'],
 ['closing synthesis', '비틀거림을 만들고, 다가가 마무리하고, 얻은 자원으로 다시 싸웁니다. 둠은 회복을 전투 바깥의 쉬는 시간에만 두지 않았습니다. 살아남기 위해 앞으로 나가도록 보상을 연결한 겁니다.', 'Create an opening, move in for a finish, then use the resources to keep fighting. DOOM places recovery inside the action, connecting rewards to the decision to push forward.', '같은 실제 전투 순서 안에서 접근→마무리→보상→다음 행동을 요약. 미래 결과를 앞에 붙여 인과를 꾸미지 않는다.']]
},
{
 'suffix':'botw-chemistry-rules',
 'source':'https://www.youtube.com/watch?v=QyMsF31NdNc',
 'files':['botw-gdc.html','botw-reference.info.json','botw-reference-only-360p.mp4','botw-chemistry-rules-contact.jpg','botw-chemistry-slide-contact.jpg'],
 'readScope':'Official GDC on-screen English slides sampled25:00–59:00; chemistry sequence38:40–44:00 inspected at10-second intervals. Rules1–3 and rain/wind/electricity slides read visually. No spoken transcript is available.',
 'method':'Research-only muted360p lecture file. CPU frame sampling and inspected contact sheets, not continuous playback, listening, FHD gameplay or rights-cleared production source.',
 'visuals':[],
 'extraVisuals':['botw-chemistry-rules-contact.jpg','botw-chemistry-slide-contact.jpg'],
 'limits':['Rule3 describes this abstract chemistry state model, not a universal ban on material-material physical interaction.','This is a simplified designed game model, not real atomic chemistry.','The muted360p lecture is reference-only and cannot satisfy independent FHD game-source requirements.'],
 'omitted':'Earlier physics and later2D prototype/open-world development chapters are outside this chemistry question. The movement/state distinction is retained as prerequisite context.',
 'terms':{'State':'불붙음·젖음 같은 상태','Element':'상태 변화를 일으키는 게임 속 원소','Material':'나무 같은 반응 대상 물질'},
 'demo':'Saved Unity state-rule scene: fire and tree, fire and water, then rain represented with the same water rule. Keep movement physics separate from state transitions. Display three rules in source order with explicit scope; do not claim to execute Nintendo code.',
 'beats':[
 ['38:40–39:50 physics versus chemistry; opening preview', '야생의 숨결에서는 풀에 불을 붙였다가 비로 끌 수 있습니다. 이런 조합을 장면마다 따로 준비했을까요? 개발진은 물체가 움직이는 계산과, 불붙음 같은 상태가 바뀌는 계산을 구별했습니다.', 'In Breath of the Wild, grass can catch fire and rain can put it out. Does every combination need its own scripted scene? The developers distinguish calculations for movement from rules that change states, such as being on fire.', '독립 BOTW의 점화→연소→비로 소화. 한 녹화에서 없으면 각각 분리 사례로 정직하게 표시. 발표360p는 제작에 사용하지 않는다.'],
 ['40:00–40:30 element and material', '상태를 다루는 쪽에서는 원소와 물질을 나눕니다. 불 같은 원소와 나무 같은 물질이 어떤 관계를 갖는지 정하는 거죠. 이름은 화학 엔진이지만, 현실의 모든 화학을 계산하겠다는 뜻은 아닙니다.', 'The state model separates elements from materials, such as fire and wood. It defines how they relate. Calling it a chemistry engine does not mean simulating every detail of real-world chemistry.', '자체 불·나무 카드와 상태 표시. 원소는 현실 주기율표 원소와 다르다는 점을 예시로 설명.'],
 ['40:50–41:00 rule1', '첫 번째 규칙은 원소가 물질의 상태를 바꾼다는 겁니다. 불이 나무에 닿으면 불붙은 상태가 되는 식입니다. 이 관계를 규칙으로 두면, 정해진 장소 하나만을 위한 연출보다 여러 곳에 적용하기 쉽습니다.', 'The first rule lets an element change a material’s state. Fire can make wood burn. A shared relationship can apply across suitable objects instead of being an effect scripted for one particular location.', '자체 동일 불 원소를 서로 다른 위치의 나무 두 개에 적용. 원문에 없는 모든 재질 연소 가능 주장 금지.'],
 ['41:10–41:20 rule2', '두 번째는 원소가 다른 원소의 상태도 바꿀 수 있다는 겁니다. 물과 불의 관계를 같은 틀 안에서 다룹니다. 불붙은 물체만 따로 검사하는 데서 더 나아가, 효과끼리도 연결되는 구조입니다.', 'The second rule lets elements change other elements’ states. Water and fire can interact within the same framework. The system connects effects to one another as well as to materials.', '자체 물→불 소화 상태 전이. 시간·양 임계값은 설명 모형의 설정이라고 명시.'],
 ['41:30 rule3', '세 번째는 물질끼리는 이 화학 규칙에서 서로의 상태를 직접 바꾸지 않는다는 겁니다. 이것은 물체가 서로 부딪힐 수 없다는 뜻이 아닙니다. 움직임의 물리와 상태 변화의 규칙을 구별하는 설명입니다.', 'The third rule says materials do not directly change one another’s states in this chemistry model. That does not mean objects cannot collide. Physical movement and chemistry-state rules are different parts of the explanation.', '자체 물질 카드 둘 사이 직접 화학 상태 변화 선은 없음. 별도 물리 충돌 선은 존재해 범위 오해 방지.'],
 ['41:40–43:50 examples, rain and simplified world', '이제 비를 물 원소로 보면, 이미 만든 물과 불의 관계를 다시 쓸 수 있습니다. 전기와 바람도 이 게임의 단순한 상태 모형 안에 들어옵니다. 서로 연결할 수 있는 규칙이 늘면서, 플레이어가 시험할 조합도 많아집니다.', 'Treating rain as a water element lets the game reuse the water-and-fire relationship. Electricity and wind also fit its simplified state model. Connected rules create more combinations for players to try.', '자체 물 원소 하나→비 입자 표시만 변경→같은 소화 규칙. 실제 전기·바람 장면은 독립 확보 후 보이는 반응만 설명.'],
 ['44:00 multiplicative gameplay; closing synthesis', '움직임은 물리로, 상태 변화는 공통 규칙으로 연결합니다. 그래서 불을 붙이고 비로 끄는 행동이 같은 세계의 약속처럼 느껴지는 거죠. 중요한 것은 이벤트를 많이 만드는 것뿐 아니라, 다시 조합할 수 있는 관계를 만드는 겁니다.', 'Movement uses physics, while shared rules connect state changes. Lighting a fire and extinguishing it in rain can therefore feel like consistent parts of one world. The key is building relationships players can combine again.', '실제 BOTW 사례로 복귀. 원소→물질, 원소→원소, 물질 간 직접 상태 변화 제외를 순서대로 짧게 요약.']]
},
{
 'suffix':'mariokart8-spin-boost',
 'source':'https://www.nintendo.com/en-gb/News/2014/April/New-items-characters-and-courses-make-for-gravity-defying-fun-in-Mario-Kart-8-launching-May-30th-on-Wii-U-870260.html',
 'files':['mariokart-spin-turbo.html'],
 'readScope':'Full official news body read; anti-gravity and Spin Turbo paragraph selected before unrelated new item/character features.',
 'method':'Nintendo’s 2014 Wii U announcement. Gameplay behavior and platform of any future recording must be checked separately.',
 'visuals':[],
 'limits':['Only anti-gravity contact with other karts or specified obstacles gives the documented boost; not every collision.','This source says Spin Turbo. Explain Spin Boost as a common naming variant only after the adopted game/version terminology is checked.','A Switch Deluxe or Mario Kart Tour recording is not automatically evidence for this Wii U source.'],
 'omitted':'Unrelated items, characters and course announcement details do not answer the anti-gravity contact question. The source’s limiting word certain for obstacles is retained.',
 'terms':{'Anti-gravity':'벽·천장 방향을 달릴 수 있는 반중력 구간','Spin Turbo':'특정 반중력 접촉에서 생기는 회전 가속'},
 'demo':'Saved Unity explanatory kart strip with a known anti-gravity mode flag. Same controlled contact once outside and once inside the mode; trigger boost only for allowed partner types. This is an own rule model, not measured Nintendo code or speed.',
 'beats':[
 ['anti-gravity feature; opening preview', '마리오 카트 에이트에서는 부딪히는 것이 가속 기회가 될 때가 있습니다. 조건은 반중력 구간입니다. 어디서 무엇과 부딪혔는지가 중요하니, 모든 충돌이 빨라지는 것은 아닙니다.', 'In Mario Kart8, a collision can become a boost opportunity. The condition is anti-gravity. Where and what you hit matters; collisions do not all make you faster.', '독립 Mario Kart8의 반중력 진입과 실제 카트 접촉. 게임 판본·해상도·행동 확인 전 확정 금지.'],
 ['anti-gravity walls and upside-down tracks', '반중력 구간에서는 벽이나 거꾸로 된 길도 달립니다. 길의 방향만 바뀌는 것이 아니라, 접촉의 의미도 달라집니다. 평소에는 피하려던 다른 카트가 여기서는 이용할 대상이 될 수 있죠.', 'Anti-gravity lets racers travel along walls and upside-down track sections. Contact also gains a different role: another kart can become something to use, rather than simply avoid.', '실제 바퀴 모드·주행 방향 변화와 접촉 전 구간을 원속도로 유지. 벽 주행 자체를 모든 구간 부스트 조건으로 등치하지 않는다.'],
 ['Spin Turbo paragraph, other karts', '닌텐도는 반중력 상태에서 다른 카트와 부딪히면 회전하며 속도를 얻는 스핀 터보를 소개했습니다. 상대 가까이 다가가는 행동에 보상이 생기는 겁니다. 다만 이 설명은 반중력 상태라는 조건 안에서 봐야 합니다.', 'Nintendo introduced Spin Turbo as a speed boost from bumping another kart during anti-gravity. Approaching another racer can therefore offer a reward. The anti-gravity condition is essential to this explanation.', '실제 접촉→회전 효과→주행 결과를 연속 확인. 화면에 없는 실제 속도 숫자나 입력 텔레메트리 생성 금지.'],
 ['same paragraph, certain obstacles', '일부 장애물과의 접촉도 같은 기회가 됩니다. 여기서 일부라는 말이 중요합니다. 길의 모든 벽과 장식물을 가속 장치라고 생각하면 안 됩니다. 실제로 이 효과를 주는 대상을 보고 경로를 고르는 거죠.', 'Certain obstacles offer the same opportunity. Certain is important: not every wall or decoration is a boost device. A useful route depends on recognizing which objects actually provide the effect.', '정확히 확인한 스핀 대상 기둥 등 전·접촉·후 구간만 채택. 임의 장애물 라벨 금지.'],
 ['closing interpretation from the documented rule', '반중력 구간, 정해진 접촉 대상, 회전 가속. 이 조건들이 모이면 충돌이 단순한 실수에서 선택지가 됩니다. 마리오 카트 에이트는 길을 비트는 것과 함께, 다른 카트에 다가갈 이유도 바꾼 겁니다.', 'Anti-gravity, an eligible contact, and a spin boost: together, these conditions turn a collision into a choice. Mario Kart8 changes both the orientation of the road and the reason to approach another kart.', '실제 확인 장면을 바탕으로 조건→접촉→가속을 요약. 마지막 해석은 명시된 규칙에 대한 교육적 해석이며 개발자 의도 인용으로 표시하지 않는다.']]
}
]

def main():
    batch_path = HERE/'batch.json'
    batch = read(batch_path)
    assert len(TOPICS)==10 and len(batch['projects'])==12
    assert batch['authorization']['intermediateApprovalRequired'] is False
    assert not (HERE/'preproduction-v3.html').exists()
    assert not (HERE/'remaining-ten-preparation-validation-v1.json').exists()
    for topic,row in zip(TOPICS,batch['projects'][2:]):
        assert 'shorts-'+topic['suffix']==row['slug']
        for filename in topic['files']: assert (REF/filename).is_file(), filename
        for filename in topic['visuals']: assert (REF/'primary-visuals'/filename).is_file(), filename
        for filename in topic.get('extraVisuals',[]): assert (REF/filename).is_file(), filename
        for name in ['primary-source-review-v1.json','source-order-map-v1.json','narration-draft-v1.json','scene-plan-v1.json']:
            assert not (ROOT/'projects'/row['slug']/'planning'/name).exists()
        assert all(len(beat)==4 and all(isinstance(s,str) and s.strip() for s in beat) for beat in topic['beats'])
    generated=[]
    for topic,row in zip(TOPICS,batch['projects'][2:]):
        slug='shorts-'+topic['suffix']
        assert slug==row['slug']
        folder=ROOT/'projects'/slug
        source_inputs=[pin(REF/f) for f in topic['files']]
        visual_inputs=[pin(REF/'primary-visuals'/f) for f in topic['visuals']]
        visual_inputs += [pin(REF/f) for f in topic.get('extraVisuals',[])]
        review_path=folder/'planning/primary-source-review-v1.json'
        source_map_path=folder/'planning/source-order-map-v1.json'
        narration_path=folder/'planning/narration-draft-v1.json'
        scene_path=folder/'planning/scene-plan-v1.json'
        assert all(not p.exists() for p in [review_path,source_map_path,narration_path,scene_path])
        paragraphs=[]; mapping=[]; scenes=[]
        for i,(location,ko,en,picture) in enumerate(topic['beats'],1):
            pid=f'p{i:03}'
            paragraphs.append(dict(id=pid,ko=ko,en=en,sourceLocation=location))
            mapping.append(dict(id=f'M{i:02}',paragraphs=[pid],sourceLocation=location,
                retainedLesson=ko,plainExplanation=ko,requiredPicture=picture,
                actualIndependentActionViewed=False,actualFootageRange=None,
                timing='pending accepted natural voice; use actual whole-word boundaries',
                boundaryToNext=topic['beats'][i][0] if i<len(topic['beats']) else 'answer opening question and recap'))
            scenes.append(dict(id=f'S{i:02}',paragraphs=[pid],sourceMap=f'M{i:02}',
                visualPlan=picture,implementationStatus='CPU-storyboard-only',
                exactSourceFrameRange=None,nativeSceneSaved=False,actualRuntimeVerified=False,
                noInventedGameTelemetry=True))
        review=dict(schemaVersion=1,slug=slug,reviewedAtKst=NOW,
            source=dict(url=topic['source'],originalSelectedUrl=row['primarySource'],role='research-reference-only',
                        relevantScope=topic['readScope'],method=topic['method'],inputs=source_inputs,
                        fullRelevantScopeReviewed=True,visualEvidence=visual_inputs),
            fullSpokenLectureReviewed=False,continuousGameplayViewed=False,
            claimLimits=topic['limits'],scopeOmissions=topic['omitted'],
            independentGameplay=dict(acquired=False,recorderPermissionVerified=False,publisherConditionsVerified=False,
                decodedFhdVerified=False,matchingActionsVerified=False,lectureFootageAdopted=False),
            decision='Write original bilingual draft in the selected primary-source order; lock only after independent source-action review.',
            intermediateApprovalRequired=False,qualityThresholdsLowered=False,humanApproval=False)
        save(review_path,review)
        save(source_map_path,dict(schemaVersion=1,slug=slug,status='primary-scope-reviewed-independent-actions-pending',
            source=review['source'],sourceReview=pin(review_path),mapping=mapping,
            scopeOmissions=topic['omitted'],claimLimits=topic['limits'],sourceOrderPreserved=True,
            opening='Actual independent game phenomenon and mini explanation; clearly labelled own diagrams introduce the mechanism.',
            closing='Return to the same named game and answer the opening question with a short recap inside existing speech.',
            narrationLocked=False,actualMotionViewed=False,humanApproval=False))
        save(narration_path,dict(schemaVersion=1,slug=slug,status='source-order-bilingual-draft-action-matching-pending',
            workingTitle=row['title'],sourceOrderMap=str(source_map_path.relative_to(ROOT)).replace('\\','/'),
            paragraphs=paragraphs,displayTerms=topic['terms'],sourceOrderPreserved=True,
            noArbitraryDurationCap=True,naturalSpeechSpeed=True,narrationLocked=False,approvedForTts=False,
            reason='Concrete draft ready for footage matching; genuine FHD independent actions and own running scene evidence are not yet verified.'))
        save(scene_path,dict(schemaVersion=1,slug=slug,beats=scenes,ownDemonstration=topic['demo'],
            layout=dict(master=[1080,1920],fps=60,mobileCheckWidth=375,fixedCaptions=True,approvedCatRequired=True),
            sourceOrderPreserved=True,sourceAudioAdopted=False,nativeCaptureStarted=False,
            actualWholeWordTimingRequired=True,productionFootageStatus='not-acquired',
            music='Use licensed music, duck music only, place required credit at the absolute end of KO and EN descriptions.',
            finalOutputs=dict(clean=None,captioned=None,ko=None,en=None)))
        plan_path=folder/'planning/production-plan-v1.json';plan=read(plan_path)
        plan['source'].update(url=topic['source'],fullRelevantScopeRead=True,review=str(review_path.relative_to(ROOT)).replace('\\','/'))
        plan['claimLimits']=topic['limits'];plan['sourceScopeOmissions']=topic['omitted']
        plan['narrationDraft']=str(narration_path.relative_to(ROOT)).replace('\\','/')
        plan['sourceOrderMap']=str(source_map_path.relative_to(ROOT)).replace('\\','/')
        plan['scenePlan']=str(scene_path.relative_to(ROOT)).replace('\\','/')
        plan['pending']=[
            'acquire independently recorded rights-checked genuine FHD named-game footage and inspect exact actions',
            'lock narration and source cuts after action matching; verify own running native scenes',
            'guarded approved voice/native/composite work, one costly job at a time',
            'clean/captioned/KO/EN outputs, hash manifest and actual local final review']
        save(plan_path,plan,new=False)
        checkpoint_path=folder/'production/checkpoint.json';checkpoint=read(checkpoint_path)
        checkpoint.update(updatedAtKst=NOW,phase='primary-research-and-KO-EN-draft-ready-footage-pending',
            sourceFactsVerified=True,sourceFootageVerified=False,sourceScopeReview=pin(review_path),
            sourceOrderMap=pin(source_map_path),narrationDraft=pin(narration_path),scenePlan=pin(scene_path),
            nextStep=plan['pending'][0])
        save(checkpoint_path,checkpoint,new=False)
        project_path=folder/'project.json';project=read(project_path)
        project.update(status=checkpoint['phase'],currentRevision='source-packet-v1')
        project['paths'].update(sourceReview=str(review_path.relative_to(ROOT)).replace('\\','/'),
            narrationDraft=str(narration_path.relative_to(ROOT)).replace('\\','/'),scenePlan=str(scene_path.relative_to(ROOT)).replace('\\','/'))
        project['authorization'].update(cpuPrepAcrossExactList=True,intermediateApprovalRequired=False)
        save(project_path,project,new=False)
        row.update(status=checkpoint['phase'],fullSourceRead=True,fullRelevantScopeReviewed=True,
            currentSourceReview=str(review_path.relative_to(ROOT)).replace('\\','/'),
            narrationDraft=str(narration_path.relative_to(ROOT)).replace('\\','/'),
            sourceOrderMap=str(source_map_path.relative_to(ROOT)).replace('\\','/'),
            scenePlan=str(scene_path.relative_to(ROOT)).replace('\\','/'))
        generated.extend(pin(p) for p in [review_path,source_map_path,narration_path,scene_path,plan_path,checkpoint_path,project_path])
    batch.update(reviewPage='production/batches/original-tech-twelve-20261115/preproduction-v3.html',
        reviewPageKind='all12 bilingual drafts and source-order/scene plans; not final video review')
    batch['delivery']['videoCompletionCount']=0
    save(batch_path,batch,new=False)
    cp_path=HERE/'checkpoint.json';cp=read(cp_path)
    cp.update(updatedAtKst=NOW,phase='all12-primary-scope-and-bilingual-drafts-prepared',
        sourceNarrationDraftCount=12,sourceOrderMapCount=12,localFinalVideos=0,actualGpuJobsStarted=0,
        independentSourcesAcquired=2,decodedFhdSources=2,independentFootageVerifiedCount=0,
        remainingTenCpuPrepComplete=True,intermediateApprovalRequired=False,
        nextStep='Match the first2 acquired FHD sources to exact continuous actions; acquire remaining10 independently recorded sources. Preserve full resource guards for voice/Unity/render stages; no new recurring automation.')
    save(cp_path,cp,new=False)
    validation=dict(schemaVersion=1,checkedAtKst=NOW,exactTopicCount=12,
        remainingTenPrepared=10,totalBilingualDrafts=12,totalSourceMaps=12,
        newParagraphsKO=sum(len(t['beats']) for t in TOPICS),newParagraphsEN=sum(len(t['beats']) for t in TOPICS),
        paragraphIdsUnique=True,sourceOrderMapped=True,resourceLimitsChanged=False,
        finalVideoCount=0,voiceCount=0,newNativeCaptureCount=0,independentFhdSources=2,
        exactActionMatchedSources=0,intermediateApprovalRequired=False,platformActions=[],
        supersededExtraction=dict(path=str(REF/'journey-sand-slides.json'),reason='Naive slide-number to notes-number mapping was incorrect. All packet claims use presentation relationship order and actual per-slide notes in journey-source-order.json.'),
        sourcePackets=generated)
    save(HERE/'remaining-ten-preparation-validation-v1.json',validation)
    render_page(batch)
    print(json.dumps({k:v for k,v in validation.items() if k not in ['sourcePackets','supersededExtraction']},ensure_ascii=False))

def render_page(batch, new=True):
    e=html.escape;parts=[]
    for row in batch['projects']:
        folder=ROOT/'projects'/row['slug']
        candidates=sorted((folder/'planning').glob('narration-draft-v*.json'))
        draft=read(candidates[-1]);source=ROOT/draft['sourceOrderMap'];source_map=read(source)
        source_info=source_map.get('source',{})
        scope=(source_info.get('relevantScope',source_info.get('scope','')) if isinstance(source_info,dict)
               else source_map.get('scope',source_map.get('scopeRead',source_info)))
        paras=[]
        for p in draft['paragraphs']:
            paras.append(f'<div class="paragraph"><b>{e(p["id"])}</b><p>{e(p["ko"])}</p><p lang="en">{e(p["en"])}</p></div>')
        mappings=[]
        for mi,m in enumerate(source_map['mapping'],1):
            location=m.get('sourceLocation','');picture=m.get('requiredPicture',m.get('requiredFootage',m.get('visual','')))
            mappings.append('<tr><td>'+e(m.get('id',f'M{mi:02}'))+'</td><td>'+e(location)+'</td><td>'+e(picture)+'</td><td>실제 행동 대조 대기</td></tr>')
        limits=source_map.get('claimLimits',[])
        caution=''.join('<li>'+e(t)+'</li>' for t in limits)
        source_url=source_info.get('url',row['primarySource']) if isinstance(source_info,dict) else source_info
        candidate_link=(' · <a href="'+e((ROOT/row['sourceCandidateReview']).as_uri())+'">독립 영상 후보 검수</a>') if row.get('sourceCandidateReview') else ''
        rights='기록자·배급사 조건 확인됨' if row['footageRightsVerified'] else '권리·판본 최종 대조 필요'
        parts.append(f'<article id="{e(row["id"])}" data-search="{e((row["title"]+" "+row["game"]).lower())}"><h2>{row["order"]:02}. {e(draft.get("workingTitle",row["title"]))}</h2><p>{e(row["game"])} · <strong>한·영 대본 준비 / 음성·최종 영상 미완료</strong></p><p>독립 FHD 원본/후보: {"확보됨 · 정확한 행동 대조 중" if row["independentFootageAcquired"] else "미확보"} · {rights} · 사람 검수 전</p><p><a href="{e(source_url)}">1차 자료</a> · <a href="{e(source.as_uri())}">자료 순서·장면 매핑 JSON</a> · <a href="{e(candidates[-1].as_uri())}">한·영 대본 JSON</a>{candidate_link}</p><p class="scope">확인 범위: {e(str(scope))}</p><details><summary>한·영 전체 대본</summary>{"".join(paras)}</details><details><summary>자료 순서와 필요한 장면</summary><table><thead><tr><th>단계</th><th>1차 자료 위치</th><th>필요한 화면</th><th>검증</th></tr></thead><tbody>{"".join(mappings)}</tbody></table><ul>{caution}</ul></details></article>')
    page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>새 게임개발 쇼츠12편 · 자료와 대본</title><style>body{margin:0 auto;max-width:1100px;padding:26px;font:17px/1.7 system-ui;background:#11151c;color:#e7edf7}a{color:#8dc9ff}h1{font-size:30px}h2{font-size:23px}.notice,article{padding:22px;background:#1c2431;border:1px solid #3d506a;border-radius:12px;margin:20px 0}.notice{border-color:#a5823b}input{width:90%;padding:14px;font:inherit;color:#eee;background:#111;border:1px solid #687c95}summary{cursor:pointer;font-weight:bold;padding:10px}.paragraph{border-top:1px solid #40526b;padding:16px 0}p[lang=en]{color:#c2cfdf}.scope{color:#b9c7da;font-size:14px}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:12px;border:1px solid #526077;text-align:left;vertical-align:top}nav{display:flex;gap:12px;flex-wrap:wrap}article[hidden]{display:none}@media(max-width:650px){body{padding:12px}article{padding:14px}table{display:block;overflow-x:auto}}</style><h1>게임개발 쇼츠12편 · 자료·대본 준비표</h1><div class="notice"><b>자료 순서와 한·영 대본12/12 · 새 최종 영상0/12</b><p>이 페이지는 제작 준비·진행표입니다. 최종 영상 검수본이 아닙니다. 락온·마리오64의 독립 FHD 원본2개를 확보했고 정확한 행동 대조가 남아 있습니다. 나머지10편은 1차 자료 검토와 한·영 대본·장면 구성을 준비했으며 독립 게임 영상 확보가 필요합니다. 음성·Unity 촬영·합성은 실제 입력 검증과 기존 전체 자원 검사를 거쳐 진행합니다. 중간 사용자 승인 없이 이12편의 로컬 최종 검수본까지 제작하는 요청을 유지합니다.</p><p>자동검사·자료 표본 확인·연속 재생·전체 청취·사람 승인은 별개입니다. 업로드·공개·예약은 수행하지 않습니다.</p></div><label>제목·게임 찾기 <input id="find" placeholder="예: 모래, 젤다, DOOM"></label>'''
    acquired=sum(bool(row['independentFootageAcquired']) for row in batch['projects'])
    previous='락온·마리오64의 독립 FHD 원본2개를 확보했고 정확한 행동 대조가 남아 있습니다. 나머지10편은 1차 자료 검토와 한·영 대본·장면 구성을 준비했으며 독립 게임 영상 확보가 필요합니다.'
    current=f'락온·마리오64 원본과 추가 후보를 합쳐 독립 영상{acquired}편의 FHD 이상 컨테이너를 확인했습니다. 정확한 행동·권리·판본 대조와 나머지{12-acquired}편의 자료 확보는 진행 중입니다. 기존2편을 포함한12편 모두 선택한 1차 자료 범위의 검토와 한·영 대본·장면 구성을 준비했습니다.'
    page=page.replace(previous,current)
    page+='<nav>'+''.join(f'<a href="#{r["id"]}">{r["order"]:02}</a>' for r in batch['projects'])+'</nav>'+''.join(parts)
    page+='<script>document.querySelector("#find").addEventListener("input",e=>{let q=e.target.value.toLowerCase();document.querySelectorAll("article").forEach(a=>a.hidden=!a.dataset.search.includes(q))})</script></html>'
    out=HERE/'preproduction-v3.html'
    if new: assert not out.exists()
    out.write_text(page,encoding='utf8',newline='\n')

if __name__=='__main__': main()
