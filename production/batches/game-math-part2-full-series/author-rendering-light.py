"""Full Notion10.1 lecture; original examples after current recording/pixel review."""
from pathlib import Path
import json
B=Path(__file__).parent;slug='game-math-rendering-light';scenes=[]
def E(i,title,mode,ko,en,beats):
 assert len(ko)==len(en)==len(beats)
 scenes.append(dict(id=f'{i:02}',title=title,kind='explanation',mode=mode,ko=ko,en=en,beats=beats))
def A(i,title,vid,segments,ko,en,focus,claim):
 assert len(ko)==len(en)
 scenes.append(dict(id=f'{i:02}',title=title,kind='actual',sourceId=vid,sourceSegments=[{'in':a,'maxSeconds':b-a} for a,b in segments],**{'in':segments[0][0]},maxSeconds=sum(b-a for a,b in segments),ko=ko,en=en,focus=focus,claim=claim))
W='wzQLP0Z3zII';S='dYyWmhVuc3w'
E(1,'화면의 한 점은 어떻게 색을 얻을까요?','overview',[
 '화면의 한 점에 어떤 표면이 보이고, 그 표면은 왜 그 색과 밝기로 보일까요?',
 '먼저 실제 게임에서 가려지는 물체를 보고, 보이는 표면을 고르는 방법부터 구분합니다.',
 '이어서 빛의 양과 단위를 손으로 계산하고, 재질과 시선이 반사를 어떻게 바꾸는지 설명하겠습니다.',
 '마지막에는 이 요소를 렌더링 방정식으로 연결하고, 간단한 밝기 계산을 직접 풀어 보겠습니다.'
],[
 'Which surface appears at a screen location, and why does it have that color and brightness?',
 'We begin with occlusion in real games and distinguish methods for selecting visible surfaces.',
 'Then we calculate light quantities and units and examine how material and view direction affect reflection.',
 'Finally we connect them with the rendering equation and solve a simple brightness problem.'
],['표면 선택 → 빛 계산 → 픽셀 색','실제 가림 → 광선·래스터·깊이','빛의 단위 → 재질·시선','렌더링 방정식 → 직접 계산'])
A(2,'바위 뒤의 캐릭터가 사라지는 이유',W,[(716,773)],[
 '빅 워크에서 다른 캐릭터를 따라 바위와 나무 사이를 걸어갑니다. 캐릭터와 앞쪽 바위가 겹치는 부분을 보세요.',
 '카메라가 움직이면 보이던 몸이 바위 뒤로 가려졌다가 다시 나타납니다. 화면의 같은 위치를 여러 표면이 차지하려고 합니다.',
 '불투명한 표면이라면 카메라에서 그 방향으로 가장 먼저 만나는 표면이 보입니다. 뒤의 물체가 없어졌다는 뜻은 아닙니다.',
 '가까운 표면을 고르는 문제와, 선택한 표면을 밝게 만드는 문제는 구분할 수 있습니다.',
 '빛을 더 켜도 앞의 불투명한 바위가 자동으로 투명해지는 것은 아닙니다. 먼저 어떤 표면을 계산할지 알아야 합니다.',
 '이 게임의 내부 코드를 추측하지 않고, 같은 가림을 만드는 두 가지 기본 접근을 원래 도식으로 비교하겠습니다.'
],[
 'Follow a character among rocks and trees in Big Walk. Observe where the character overlaps foreground rock.',
 'Moving the camera makes the body disappear behind rock and reappear. Several surfaces compete for a screen location.',
 'For opaque surfaces, the first surface along that camera direction is visible; the hidden object still exists.',
 'Selecting that surface and determining its illumination are separate questions.',
 'Adding light does not automatically make an opaque foreground rock transparent. First select the surface to evaluate.',
 'Our independent diagram compares two basic approaches without inferring this game implementation.'
],'카메라 이동에 따른 바위·캐릭터의 실제 가림','불투명 가시성 선택과 조명 계산은 별도 문제')
E(3,'픽셀에서 출발할까, 삼각형에서 출발할까?','ray-raster',[
 '렌더링의 출력은 픽셀마다 색을 가진 영상입니다. 프레임 버퍼에는 이 결과를 저장하고, 표시 전에 후처리를 더할 수도 있습니다.',
 '광선 방식은 화면의 표본에서 카메라 광선을 만듭니다. 장면과 교차 검사한 뒤, 가장 가까운 유효 교점을 찾습니다.',
 '교점이 있으면 위치, 법선, 재질로 카메라 쪽 빛을 계산합니다. 아무것도 만나지 않으면 배경을 사용합니다.',
 '래스터 방식은 삼각형에서 출발합니다. 화면에 투영한 삼각형이 어떤 표본을 덮는지 찾고, 깊이를 비교합니다.',
 '바깥 순서가 화면 표본인지, 장면의 삼각형인지가 다른 것입니다. 둘 다 가시성과 셰이딩이라는 질문을 해결합니다.',
 '픽셀마다 반드시 광선 한 개만 쓰는 것은 아닙니다. 여러 표본으로 경계 등을 계산할 수 있고, 광선을 쓴다는 사실만으로 빛이 정확해지지도 않습니다.'
],[
 'Rendering outputs colors at image samples. A framebuffer stores them, possibly followed by display postprocessing.',
 'Ray-based visibility constructs a camera ray for a screen sample and finds the nearest valid scene intersection.',
 'An intersection supplies position, normal and material for shading toward the camera; a miss uses the background.',
 'Rasterization starts with projected triangles, determines sample coverage and compares depths.',
 'The outer traversal differs: screen samples or scene primitives. Both address visibility and shading.',
 'A pixel need not use exactly one ray. Multiple samples help reconstruction, and rays alone do not guarantee accurate illumination.'
],['프레임 버퍼: 계산된 색의 영상','광선: 표본 → 교차 → 최근접 표면','교점 정보 → 셰이딩 / miss → 배경','래스터: 삼각형 → 덮는 표본 → 깊이','시작 순서가 달라도 같은 두 질문','여러 표본 가능 / 광선 ≠ 정확한 조명'])
E(4,'깊이 8과 3을 순서대로 비교하기','depth-test',[
 '같은 표본을 빨간 삼각형과 파란 삼각형이 덮는 예제입니다. 가까울수록 값이 작다고 약속하고, 깊이를 각각 팔과 삼으로 둡니다.',
 '처음 깊이는 무한대로 둡니다. 빨간 삼각형 팔을 먼저 넣으면 통과합니다. 다음 파란 삼각형 삼이 더 가까워 색과 깊이를 교체합니다.',
 '순서를 바꾸면 파란 삼각형 삼이 먼저 기록됩니다. 뒤에 온 빨간 삼각형 팔은 더 멀기 때문에 버립니다.',
 '두 순서 모두 결과는 파란색과 깊이 삼입니다. 불투명한 표면과 유효한 비교 규칙에서 순서가 달라도 최근접 표면을 고릅니다.',
 '이 숫자는 원리를 위한 예제입니다. 실제 깊이 버퍼는 보통 거리를 그대로 저장하지 않고, 투영 뒤에 변환된 깊이를 저장합니다.',
 '멀수록 작게 저장하는 반전 깊이도 있습니다. 초기 값과 비교 방향을 함께 정해야 하며, 깊이가 같을 때의 규칙도 별도로 필요합니다.'
],[
 'Red and blue triangles cover one sample. In our toy convention smaller is nearer, with depths eight and three.',
 'Initialize depth to infinity. Red eight passes first; blue three then replaces its color and depth.',
 'Reverse the order: blue three is stored first, and the farther red eight is rejected.',
 'Both orders produce blue at depth three under the defined opaque depth rules.',
 'These are explanatory values. Actual depth buffers usually store transformed projected depth rather than metric distance.',
 'Reversed depth uses the opposite order. Initialize and compare consistently, and define equal-depth behavior separately.'
],['불투명 예제: 빨강 8 / 파랑 3','∞ → 8 → 3','∞ → 3 / 8은 거절','두 순서: 파랑·깊이 3','예제 깊이 ≠ 실제 거리 인코딩','반전 깊이: 초기값·비교 방향 함께'])
A(5,'구멍으로 보이는 것과 투명하게 보이는 것',W,[(510,545),(1553,1578)],[
 '노란 구조물의 둥근 구멍으로 다른 캐릭터가 보입니다. 구멍 앞의 벽과 구멍 안의 배경을 구분해 보세요.',
 '구멍에는 막는 벽 표면이 없기 때문에 뒤의 표면을 볼 수 있습니다. 불투명한 벽 한 장의 색을 흐리게 만든 경우와 다릅니다.',
 '다음 장면에서는 손으로 투명한 상자 가까이를 살펴봅니다. 상자의 표면과 안쪽 빨간 모양이 함께 보입니다.',
 '투명한 물체는 앞 표면 하나만 고르고 끝낼 수 없습니다. 뒤에서 오는 빛과 투과, 경우에 따라 굴절까지 함께 생각해야 합니다.',
 '화면에 보이는 이 차이가 설명의 출발점입니다. 게임이 어떤 투명 렌더링 기법을 썼는지는 이 화면만으로 확정하지 않습니다.'
],[
 'Observe characters through circular openings in the yellow structure, distinguishing wall and opening.',
 'No wall surface blocks the opening. This differs from making one opaque wall color faint.',
 'Next, examine the transparent tank near the player hands: its surface and the red interior are both visible.',
 'Transparency requires more than selecting one front surface: transmitted background light and sometimes refraction matter.',
 'These visible differences motivate the explanation but do not identify the game transparency technique.'
],'실제 구멍의 가림과 투명 상자·내부의 동시 기여','최근접 불투명 표면 한 층 모델의 범위')
E(6,'포워드와 디퍼드는 계산을 묶는 순서입니다','forward-deferred',[
 '포워드 방식은 삼각형을 처리하며 필요한 재질과 조명을 계산해서 색을 기록합니다. 깊이 검사와 셰이딩의 실제 실행 순서는 최적화에 따라 달라질 수 있습니다.',
 '디퍼드 방식은 먼저 보이는 표면 정보를 저장합니다. 위치나 깊이, 법선, 재질 정보를 모은 지 버퍼를 생각하세요.',
 '다음 패스에서 이 정보를 읽고 여러 광원의 기여를 계산합니다. 삼각형 표면을 처리하는 단계와 조명을 계산하는 단계를 나눈 것입니다.',
 '광원이 많을 때 표면 정보를 다시 처리하는 비용을 줄일 수 있습니다. 대신 여러 버퍼의 메모리와 대역폭, 투명 물체 처리 같은 비용이 있습니다.',
 '포워드의 광원마다 항상 모든 삼각형을 다시 그려야 하는 것은 아닙니다. 현대의 타일이나 클러스터 방식도 있으므로 어느 하나가 언제나 빠르다고 단정하지 마세요.',
 '이는 계산을 나누는 구조입니다. 가시성이나 반사의 물리 법칙을 바꾼 것이 아니며, 복잡한 투과와 안개처럼 공간 안에서 일어나는 산란에는 별도 처리가 필요합니다.'
],[
 'Forward shading evaluates material and illumination while processing primitives. Optimization can change actual depth-test and shading order.',
 'Deferred shading first stores visible-surface information in a G-buffer: depth or position, normal and material.',
 'A later pass reads that information and evaluates light contributions, separating triangle-surface processing from lighting calculation.',
 'Many lights can benefit from reusing surface information, at the cost of buffer memory, bandwidth and transparency handling.',
 'Modern tiled or clustered forward methods need not redraw every triangle for each light. Neither organization always wins.',
 'This reorganizes computation rather than changing visibility or reflection laws; complex transmission and scattering within space, such as fog, require additional handling.'
],['포워드: 표면 처리 중 재질·조명 → 색','디퍼드 1: 깊이·법선·재질 → G-buffer','디퍼드 2: 저장 정보 → 광원 기여','기하 재사용 / 메모리·대역폭·투명성 비용','현대 forward도 tiled·clustered 가능','계산 구조와 물리 법칙을 구분'])
E(7,'재질은 색 하나보다 더 많은 질문에 답합니다','brdf-directions',[
 '같은 빨간 표면도 손전등과 카메라 위치에 따라 반짝임이 달라집니다. 색 숫자 하나만으로 모든 방향의 반사를 설명할 수 없습니다.',
 '비알디에프는 한 표면 위치에서, 어느 방향에서 들어온 빛이 어느 방향으로 반사되는지 설명하는 분포입니다.',
 '입력에는 표면 위치, 들어오는 방향, 나가는 방향과 파장 또는 색 표현이 들어갑니다. 위치가 달라지면 같은 물체의 재질도 달라질 수 있습니다.',
 '여기서는 들어오는 방향 벡터를 표면에서 광원 쪽으로 향하게 정하겠습니다. 빛이 실제로 진행하는 화살표와는 반대라는 점을 기억하세요.',
 '나가는 방향은 표면에서 관찰자 쪽입니다. 법선은 표면 바깥쪽을 향합니다. 이 약속은 뒤의 코사인 부호까지 결정합니다.',
 '넓게 퍼지는 반사와 좁은 방향에 몰리는 반사를 구별하세요. 관찰 방향을 바꾸면 좁은 반사 봉우리를 만나거나 놓칠 수 있습니다.'
],[
 'A red surface can change highlights as light and camera positions change; one color cannot describe all directions.',
 'A BRDF describes directional reflection at one surface location.',
 'It depends on location, incident and outgoing directions and wavelength or a chosen color representation.',
 'We define the incident-direction vector from the surface toward the source, opposite actual light travel.',
 'The outgoing vector points toward the viewer and the normal points outward; these conventions determine cosine signs.',
 'Distinguish broad reflection from a narrow directional lobe that a changing view can intersect or miss.'
],['재질·빛·시선이 함께 외관 결정','fᵣ: 한 위치의 방향별 반사 분포','x / ωᵢ / ωₒ / λ','ωᵢ: 표면 → 광원 / 실제 진행은 반대','ωₒ: 표면 → 눈 / n: 바깥 법선','넓은 분포와 좁은 반사 봉우리'])
A(8,'밝은 벽과 어두운 벽을 함께 관찰하기',S,[(638,650),(407,421),(739,753)],[
 '서브노티카 투의 기지에서 카메라가 흰 벽과 어두운 수납장 쪽으로 돌아갑니다. 같은 화면 안의 표면을 비교해 보세요.',
 '바깥의 어두운 물에서 기지로 들어오면 밝은 벽이 눈에 들어옵니다. 재질 색과 조명 조건이 함께 결과를 만듭니다.',
 '천장과 벽을 따라 시선을 움직일 때 밝은 부분의 모양도 달라집니다. 건설용 초록 미리 보기 표시는 게임 화면의 도구 표시입니다.',
 '완성된 픽셀만 보고 반사 함수나 광원 값을 역으로 확정할 수는 없습니다.',
 '다음 원래 예제에서는 조건을 직접 정해서, 반사 분포와 에너지 보존을 구분하겠습니다.'
],[
 'In the Subnautica2 base, compare a white wall and dark storage surfaces as the camera turns.',
 'Approaching the bright base from dark water changes the view. Both material response and illumination affect pixels.',
 'The bright patterns change along walls and ceiling; green construction previews are visible game tool overlays.',
 'Finished pixels alone do not uniquely identify a BRDF or light value.',
 'Our independent example explicitly defines conditions to distinguish a reflection distribution from energy conservation.'
],'실제 기지 접근·벽과 천장·재질 대비','완성 영상은 재질과 조명을 함께 보여주며 수치 역추정의 증거가 아님')
E(9,'반사 분포가 1보다 크면 틀린 걸까요?','brdf-energy',[
 '비알디에프 값은 영에서 일 사이의 단순한 반사 확률이 아닙니다. 방향에 대한 분포이므로 단위는 입체각의 역수입니다.',
 '빛을 좁은 방향에 모으면 그 방향의 분포 값이 일보다 클 수도 있습니다. 값 하나가 크다고 에너지를 새로 만든 것은 아닙니다.',
 '에너지 보존은 반사되는 모든 방향의 기여를 코사인과 입체각으로 가중해 합한 뒤 검사합니다. 수동 표면은 받은 에너지보다 더 많이 반사하지 않습니다.',
 '반사 분포는 음수가 아니어야 합니다. 일반적인 상반성을 만족하는 재질에서는 두 방향을 바꾸어도 같은 반사 응답을 얻습니다.',
 '자체 발광은 반사에서 공짜로 에너지를 늘린 것이 아니라 별도의 방출 항입니다. 형광 같은 더 복잡한 현상도 지금의 단순 모델 범위와 구분합니다.',
 '오래된 정규화 없는 블린 퐁 식은 이런 보존 조건을 어길 수 있습니다. 익숙한 반짝임 모델을 물리 법칙 전체로 생각하지 마세요.'
],[
 'A BRDF is not a scalar reflection probability between zero and one; its directional density has inverse-solid-angle units.',
 'A narrow lobe can exceed one locally without creating energy.',
 'Energy conservation tests the cosine-weighted integral over outgoing directions: passive reflection cannot exceed incident energy.',
 'The distribution must be nonnegative; reciprocal ordinary materials have the same response after exchanging directions.',
 'Emission is a separate contribution. More complex phenomena such as fluorescence require broader models.',
 'Historical unnormalized Blinn–Phong formulas can violate conservation; a familiar highlight model is not the whole physical law.'
],['BRDF 단위: sr⁻¹ / 확률 값이 아님','좁은 봉우리: fᵣ > 1도 가능','반구 전체 ∫fᵣ cosθ dω ≤ 1','비음수 / 상반성: fᵣ(ωᵢ,ωₒ)=fᵣ(ωₒ,ωᵢ)','반사와 자체 방출은 별도 항','정규화 없는 역사적 Blinn–Phong 주의'])
E(10,'반사·투과·표면하 산란의 범위','scattering',[
 '반사는 표면의 같은 쪽으로 빛이 돌아오는 경우입니다. 반사만 다루는 비알디에프에서 시작했습니다.',
 '반대편으로 투과되는 빛을 다루는 함수는 비티디에프입니다. 같은 위치에서 반사와 투과를 함께 묶으면 보통 비에스디에프라고 부릅니다.',
 '피부나 우유처럼 안으로 들어간 빛이 다른 위치로 나오는 경우도 있습니다. 입사 위치와 출사 위치를 따로 두는 비에스에스알디에프로 구분합니다.',
 '그래서 방향만 추가하는 일반화와, 위치까지 두 개로 늘리는 일반화는 다릅니다. 원문의 중복된 약자를 그대로 한 개념으로 외우지 마세요.',
 '안개나 물속 산란은 표면만의 반사가 아닙니다. 공간 속 산란과 흡수, 방향 분포를 별도로 다루어야 합니다.',
 '이 강의의 뒤 계산은 불투명한 표면의 반사와 방출로 범위를 정합니다. 물속 게임 장면을 곧바로 그 단순 표면식 하나로 전부 설명하지 않겠습니다.'
],[
 'Reflection returns light to the same side of the surface; a BRDF describes that case.',
 'A BTDF describes transmission. A BSDF combines reflection and transmission at the same location.',
 'Subsurface scattering can move light between different entry and exit positions; a BSSRDF distinguishes both locations.',
 'Adding directions and adding a second position are different extensions; do not conflate repeated source abbreviations.',
 'Fog and underwater scattering require volume scattering, absorption and directional distributions beyond surface reflection.',
 'Our calculations concern an opaque surface with reflection and emission, rather than all underwater effects in one surface equation.'
],['BRDF: 같은 쪽으로 반사','BTDF: 투과 / BSDF: 반사+투과','BSSRDF: xᵢ와 xₒ가 다른 표면하 산란','같은 위치의 방향 vs 서로 다른 위치','체적: 산란·흡수·위상 함수','계산 범위: 불투명 표면 반사·방출'])
A(11,'밝은 색과 빛의 스펙트럼을 구분하기',W,[(773,799),(1848,1877)],[
 '빅 워크의 밝은 바깥에서 빨간 구조물 안쪽으로 움직입니다. 빨간 표면과 그늘의 어두운 부분을 함께 보세요.',
 '이어지는 장면에는 파란 장치와 녹색 지형이 있습니다. 화면의 빨강, 초록, 파랑은 우리가 표시한 색의 좌표입니다.',
 '실제 빛이 언제나 세 가지 파장만으로 이루어졌다는 뜻은 아닙니다. 서로 다른 스펙트럼이 같은 색처럼 보일 수도 있습니다.',
 '게임의 색은 재질과 조명, 카메라와 표시 변환의 결과입니다. 화면이 어두워졌다는 이유만으로 재질이 바뀌었다고 단정하지 마세요.',
 '빛 에너지와 사람이 보는 색을 구분한 뒤, 에너지의 양부터 숫자로 계산하겠습니다.'
],[
 'Move from bright outdoors into a red structure in Big Walk, observing red surfaces and shaded regions.',
 'The next shot shows blue instruments and green terrain. Display RGB values are coordinates for represented color.',
 'Physical light need not contain exactly three wavelengths; different spectra can appear alike.',
 'Pixels reflect materials, lighting, camera and display transforms. A darker pixel alone does not prove a changed material.',
 'Separate physical light and perceived color before calculating energy quantities.'
],'실제 햇빛·그늘과 빨강 구조물·파랑 장치','표시된 RGB와 실제 스펙트럼·물리 에너지의 구분')
E(12,'줄·와트·제곱미터당 와트','energy-units',[
 '빛의 에너지 총량은 줄로 나타냅니다. 사 줄이 이 초 동안 전달됐다면, 평균 일률은 이 와트입니다.',
 '복사속은 빛 에너지가 시간당 흐르는 총량입니다. 일 와트는 일 초에 일 줄이 흐르는 양입니다.',
 '그 이 와트가 이 제곱미터에 균일하게 도착한다면, 평균 복사조도는 제곱미터당 일 와트입니다.',
 '들어오는 면적당 양은 복사조도이고, 떠나는 면적당 양은 복사출사도입니다. 총량과 밀도는 같은 숫자처럼 보여도 단위가 다릅니다.',
 '복사 측정은 물리 에너지를 다룹니다. 측광은 파장마다 사람 눈의 민감도로 가중해 광속이나 조도로 표현합니다.',
 '와트와 루멘, 제곱미터당 와트와 럭스를 구분하세요. 측광량을 사람의 주관적인 밝기 느낌이나 화면의 감마 값과 동일하게 보지 않습니다.'
],[
 'Radiant energy is measured in joules. Four joules delivered over two seconds give an average power of two watts.',
 'Radiant flux is total energy flow per time; one watt equals one joule per second.',
 'If those two watts arrive uniformly across two square metres, average irradiance is one watt per square metre.',
 'Irradiance measures arrival per area and exitance measures departure per area; total and density differ in units.',
 'Radiometry measures physical energy; photometry weights wavelengths by human visual sensitivity.',
 'Distinguish watts from lumens and irradiance from lux. Photometric quantities are not subjective brightness or display gamma.'
],['에너지 Q=4 J / 시간 Δt=2 s','복사속 Φ=4/2=2 W','균일한 A=2 m² → E=1 W/m²','총량 Φ / 도착 E / 출사 M','복사 측정: 에너지 / 측광: 시감 가중','W ≠ lm / W/m² ≠ lx'])
E(13,'면적과 방향을 모두 구별해야 합니다','solid-angle',[
 '같은 면적당 총량을 받아도, 사방에서 들어오는 빛과 좁은 한 방향에서 들어오는 빛은 다릅니다. 반짝임을 계산하려면 방향별 양이 필요합니다.',
 '평면의 각도는 원의 호와 연결됩니다. 입체각은 관찰점에서 바라본 영역을 단위 구에 투영한 면적으로 생각할 수 있습니다.',
 '입체각의 단위는 스테라디안입니다. 구 전체는 사 파이, 반구는 이 파이 스테라디안입니다. 화면의 평면 각도와 혼동하지 마세요.',
 '복사휘도는 투영 면적당, 입체각당 복사속입니다. 단위는 와트를 제곱미터와 스테라디안으로 나눈 것입니다.',
 '여기서 투영 면적은 광선 방향에 수직으로 바라본 면적입니다. 표면 자체의 넓이와 같은 경우도 있지만 기울면 달라집니다.',
 '그러므로 복사조도와 복사휘도를 바로 같은 값으로 대입할 수 없습니다. 방향별 기여를 합할 때 입체각과 코사인이 필요합니다.'
],[
 'Equal irradiance can arrive from many directions or one narrow beam. Highlights require directional quantities.',
 'A solid angle corresponds to the projected area of a region on a unit sphere around the observation point.',
 'Its unit is the steradian: four pi for a sphere and two pi for a hemisphere.',
 'Radiance is flux per projected area per solid angle, in watts per square metre per steradian.',
 'Projected area is measured perpendicular to the ray direction and changes with surface orientation.',
 'Irradiance and radiance cannot simply substitute for one another; directional integration needs cosine and solid-angle factors.'
],['같은 E / 넓은 방향과 좁은 방향','입체각: 단위 구에서 차지하는 면적','구 4π sr / 반구 2π sr','L 단위: W/(m²·sr)','투영 면적: 광선에 수직인 면적','E=∫ Lᵢ cosθ dω'])
A(14,'손전등이 비스듬한 바위를 비출 때',S,[(240,270),(350,374)],[
 '손전등을 든 채 바위 아래와 옆으로 움직입니다. 밝은 빛이 닿는 부분과 주변의 어두운 면을 보세요.',
 '굴곡진 바위는 위치마다 표면 방향이 다릅니다. 같은 빛이 오는 방향에서도 법선과 이루는 각이 달라집니다.',
 '밝기가 달라지는 데에는 거리, 가림, 재질과 물속 효과도 있습니다. 이 영상은 각도 하나만 바꾸는 통제 실험은 아닙니다.',
 '그래서 다음 도식에서는 빛의 조건을 고정하고 판의 방향만 바꾸겠습니다. 빛이 비스듬하면 넓은 면에 퍼지는 관계를 분리합니다.',
 '관찰한 바위의 밝기에서 특정 수치를 읽어내지 않고, 우리가 정한 영 도와 육십 도를 직접 비교하겠습니다.'
],[
 'Move with a handheld lamp beneath and beside rock, observing illuminated patches and dark neighboring faces.',
 'A curved rock has different local surface orientations relative to incoming light.',
 'Distance, visibility, material and water effects also matter. This recording is not a controlled angle-only experiment.',
 'Our next diagram fixes illumination and changes only a plate orientation to isolate projected-area effects.',
 'We compare explicitly defined zero and sixty degrees rather than inferring radiometric numbers from the game.'
],'실제 손전등 광점과 굴곡진 바위 면','통제 예제의 코사인 법칙으로 연결하되 게임 수치 추정은 하지 않음')
E(15,'판을 60도 기울이면 왜 절반일까요?','projected-cosine',[
 '한 방향에서 오는 같은 빛을 받는 판입니다. 법선과 광원 쪽 방향이 같으면 각도는 영이고, 코사인은 일입니다.',
 '판을 기울여 두 방향 사이의 각도를 육십 도로 만들면 코사인은 영 점 오입니다. 같은 실제 면적의 투영 면적이 절반입니다.',
 '같은 방향별 빛 조건에서, 판의 면적당 도착 기여도 절반이 됩니다. 재질의 반사 법칙을 바꾸지 않아도 생기는 기하 효과입니다.',
 '벡터를 단위 길이로 만들면 법선과 광원 쪽 방향의 내적이 이 코사인입니다. 단위 길이를 잊으면 방향뿐 아니라 길이까지 곱해집니다.',
 '우리 약속에서는 표면에서 광원 쪽을 향하므로 앞면의 내적이 양수입니다. 빛의 진행 방향을 쓰는 식에는 반대 부호가 필요합니다.',
 '불투명한 한쪽 면의 직접 조명에서는 뒤쪽 방향을 영으로 제한합니다. 양면 표면과 투과는 별도의 모델입니다.'
],[
 'For fixed directional illumination, a plate normal aligned with the source direction has angle zero and cosine one.',
 'At sixty degrees, cosine is one half and the same actual area has half the projected area.',
 'Its directional irradiance contribution halves under these defined conditions, independently of changing material response.',
 'The dot product equals cosine only for unit normal and unit direction vectors.',
 'Our source-facing incident vector gives positive front-side cosine; a light-travel vector requires the opposite sign.',
 'One-sided opaque direct lighting clamps back-side contributions to zero; two-sided transmission needs another model.'
],['θ=0°: cosθ=1','θ=60°: cosθ=0.5','A⊥=A cosθ / 같은 Lᵢ의 기여는 절반','단위 벡터: n·ωᵢ=cosθ','표면→광원: +dot / 빛 진행: -dot','한쪽 불투명 면: max(0,n·ωᵢ)'])
E(16,'나가는 빛은 방출과 반사의 합입니다','rendering-equation',[
 '이제 한 표면 위치에서 눈 쪽으로 나가는 복사휘도를 계산합니다. 렌더링 방정식은 자체 방출과 반사 기여의 합입니다.',
 '발광하는 표면은 자체 방출 항을 가집니다. 일반적인 비발광 표면에서는 그 항을 영으로 둡니다.',
 '반사 항은 표면 위 반구의 각 방향에서 들어오는 복사휘도에 반사 분포와 코사인을 곱한 뒤, 입체각 전체에 대해 더합니다.',
 '눈 쪽 방향은 고정하고 들어오는 방향을 바꾸며 합하는 것입니다. 비알디에프가 이 둘을 연결합니다.',
 '복사휘도에 스테라디안의 역수인 반사 분포를 곱하고, 스테라디안인 미소 입체각으로 적분합니다. 최종 단위는 다시 복사휘도입니다.',
 '공식의 위치와 파장 인자는 이 계산이 한 점과 한 색 표현에 대한 것임을 뜻합니다. 표시할 픽셀 색에는 카메라와 색 변환 등의 단계도 이어집니다.'
],[
 'At one surface location, outgoing radiance equals emitted radiance plus reflected radiance.',
 'Emissive surfaces have an emission term; ordinary nonemissive surfaces use zero for that term.',
 'Integrate incident radiance times BRDF times cosine over the incident hemisphere.',
 'Hold the outgoing direction fixed while summing incident directions; the BRDF connects both.',
 'BRDF inverse-steradian units cancel the solid-angle integration, leaving radiance units.',
 'Location and wavelength specify the point and spectral quantity; camera and color transforms later produce display pixels.'
],['Lₒ=Lₑ+반사 기여','비발광 표면: Lₑ=0','Lₒ=Lₑ+∫Ω Lᵢ fᵣ cosθ dω','ωₒ 고정 / ωᵢ 방향들을 합산','W/(m² sr) × sr⁻¹ × sr → W/(m² sr)','한 점·방향·파장 → 카메라·색 표시'])
A(17,'천장 조명을 설치하면 벽도 밝아집니다',S,[(579,620),(764.5,778)],[
 '녹색 물속에서 밝은 기지 쪽으로 움직입니다. 보이는 표면과 그 표면을 향해 오는 빛을 나누어 생각하세요.',
 '이어지는 장면에서는 플레이어가 천장에 조명을 설치합니다. 미리 보기 모양이 설치된 조명으로 바뀌는 부분을 보세요.',
 '조명 자체가 빛을 내는 것과, 주변 벽이 빛을 받아 반사하는 것은 서로 다른 역할입니다.',
 '설치 뒤 천장과 벽이 넓게 밝아진 모습은 두 역할을 연결하는 관찰입니다. 벽이 모두 발광 재질로 바뀌었다는 뜻은 아닙니다.',
 '게임이 간접 조명을 어떤 방식으로 구현했는지는 단정하지 않습니다. 다음에는 빛의 이동 관계와 계산 비용을 도식으로 설명합니다.'
],[
 'Approach a bright base through green water, separating visible surfaces from arriving light.',
 'Next the player installs a ceiling light; observe the construction preview becoming an installed fixture.',
 'A light emitting and a wall receiving and reflecting light play different roles.',
 'Broadly brighter walls and ceiling after placement connect those roles, rather than proving that every wall became emissive.',
 'We do not identify the game indirect-lighting implementation. The diagram explains light transport relationships and cost.'
],'실제 기지 접근과 천장 조명 설치·벽 밝기 변화','방출 항과 표면 반사 항의 구별')
E(18,'한 표면의 출사광은 다른 표면의 입사광입니다','light-transport',[
 '광원에서 바로 오는 빛은 직접 조명입니다. 벽이나 바닥을 거쳐서 오는 빛은 간접 조명으로 구분합니다.',
 '첫 표면에서 나온 빛이 다른 표면에 도착하면, 첫 표면의 출사광이 둘째 표면의 입사광이 됩니다.',
 '그러면 한 점의 입사광을 구하려고 다른 점의 출사광도 알아야 합니다. 렌더링 방정식은 장면의 점들을 서로 연결합니다.',
 '여러 번 반사되는 길이 늘어나면 계산량이 커집니다. 가림과 그림자, 반사, 빛이 닿는 경로를 함께 고려해야 합니다.',
 '실시간 게임은 유한한 예산 안에서 이를 근사합니다. 사전 계산, 제한된 경로, 화면 공간 계산이나 다른 혼합 방법을 선택할 수 있습니다.',
 '광선 추적도 표본 수와 경로 길이, 재질 모델에 따라 오차가 있습니다. 기법 이름보다 무엇을 계산하고 무엇을 생략했는지 보세요.'
],[
 'Direct lighting arrives from a light; indirect lighting arrives after another surface interaction.',
 'One surface outgoing radiance becomes another surface incident radiance along an unoccluded path.',
 'Thus evaluating one point can require evaluating other points: the equation couples the scene.',
 'More bounces increase work; visibility, shadows, reflection and paths all matter.',
 'Real-time budgets motivate precomputation, limited paths, screen-space estimates and hybrid methods.',
 'Ray tracing also has finite samples, path limits and model error. Examine computed and omitted effects rather than technique names.'
],['광원 → 표면: 직접 / 표면 경유: 간접','A의 Lₒ → B의 Lᵢ','장면 여러 점이 연결된 방정식','가림·경로·다중 반사 → 계산량','실시간: 예산 안의 근사·혼합','광선도 유한 표본·경로·모델 오차'])
A(19,'밝은 바닥의 그늘도 계산 대상입니다',W,[(1933,1978)],[
 '바위와 나무 사이를 걸으며 밝은 땅과 그늘을 비교합니다. 카메라가 움직여도 표면과 그림자의 관계가 계속 바뀌어 보입니다.',
 '그늘은 특정 광원 방향이 가려졌다는 뜻일 수 있습니다. 모든 방향에서 오는 빛이 반드시 영이라는 뜻은 아닙니다.',
 '주변 표면과 하늘에서 오는 기여까지 생각하면, 한 방향의 밝기 하나로 전체를 끝낼 수 없습니다.',
 '이 게임의 그림자나 간접 조명 구현을 특정하지 않고, 방향별 기여를 합한다는 질문에 집중하겠습니다.',
 '마지막 계산에서는 방향 표본을 두 배로 늘려도 밝기를 두 배로 만들지 않는 이유를 확인합니다.'
],[
 'Walk among rocks and trees, comparing lit ground with shadow while camera motion changes the view.',
 'Shadow can mean one light direction is blocked, without making all incident directions zero.',
 'Surrounding surfaces and sky can contribute; one directional value is not the whole illumination.',
 'Focus on summing directional contributions without identifying this game shadow or indirect-lighting method.',
 'Our final example explains why doubling sample count should not double expected brightness.'
],'실제 이동 중 햇빛·나무와 바위 그림자','가려진 한 방향과 전체 입사광의 차이')
E(20,'표본 수를 늘려도 밝기를 두 배로 만들지 않기','sampling',[
 '적분을 컴퓨터로 계산할 때는 여러 방향에서 표본을 얻습니다. 각 표본에 방향이 대표하는 입체각의 가중치가 필요합니다.',
 '모든 방향에서 값이 같아도, 표본 값만 계속 더하면 표본 수에 따라 밝기가 커집니다. 이것은 같은 적분을 계산한 것이 아닙니다.',
 '반구에 균일하게 방향을 뽑았다면 확률 밀도는 이 파이의 역수입니다. 몬테카를로 추정에서는 각 기여를 그 밀도로 나누고, 표본 수로 평균합니다.',
 '표본이 두 배가 되어도 정규화된 추정의 기대 밝기는 같습니다. 대신 오차나 잡음이 달라질 수 있습니다.',
 '지금 다루는 표면 위 반구는 일반 함수 모델입니다. 면적이 영인 점광원 같은 이상화는 별도의 총량과 표본 규칙으로 다루어야 합니다.',
 '색 채널로 빛을 곱하고 더할 때도 선형인 빛의 값에서 계산합니다. 화면 표시용 감마 값에 바로 같은 식을 적용하면 다른 결과가 됩니다.'
],[
 'Numerical integration samples directions with weights for their represented solid angle.',
 'Simply adding more unweighted samples makes brightness scale with count rather than estimating the same integral.',
 'Uniform hemisphere sampling has density one over two pi. Divide each contribution by its density and average over samples.',
 'Doubling normalized samples preserves expected brightness while potentially changing noise.',
 'Ideal point lights require separate total-flux and sampling treatment beyond an ordinary finite-area function.',
 'Multiply and sum light in linear color values, not directly in gamma-encoded display values.'
],['수치 적분: 방향마다 가중치 필요','단순한 합 → N에 따라 밝기가 변함','p=1/(2π) / 추정=(1/N)Σ g(ω)/p(ω)','2N에서도 기대값 동일 / 잡음 변화','점광원 이상화는 별도 처리','linear light에서 계산 → 표시 변환'])
A(21,'보이는 표면과 밝기를 나누어 관찰하기',W,[(1615,1642),(1700,1727)],[
 '구멍이 있는 구조물 옆을 걷다가, 색이 다른 캐릭터가 앞뒤로 겹치는 장면으로 이어집니다. 어느 표면이 앞에 있는지 보세요.',
 '같은 화면에서 밝은 면과 어두운 면도 비교합니다. 앞뒤 순서를 고르는 계산과 그 면의 밝기를 계산하는 것은 별개입니다.',
 '빨강이나 초록의 색만으로도, 면의 방향만으로도 결과는 정해지지 않습니다. 들어오는 빛과 눈 쪽으로 나가는 반사를 연결합니다.',
 '실제 게임에서 출발해, 표면을 고르고, 단위를 구분하고, 방향별 반사를 합하는 세 단계를 돌아보세요.',
 '마지막은 조건을 정한 확산면입니다. 반사율과 도착한 빛으로 눈 방향의 출사량을 계산하겠습니다.'
],[
 'Walk beside the perforated structure, then observe differently colored characters overlapping. Identify the foreground surface.',
 'Compare bright and dark faces separately from their front-to-back ordering.',
 'Neither surface color nor orientation alone determines pixels: connect arriving light with directional reflection.',
 'Review three steps: select the surface, keep quantities consistent, then integrate directional reflection.',
 'Our last defined diffuse example calculates outgoing radiance from reflectance and received irradiance.'
],'실제 이동·표면 겹침·색과 그림자 비교','가시성 → 단위 → 방향별 반사의 전체 연결')
E(22,'반사율0.6과 입사10을 직접 계산하기','practice',[
 '첫 문제입니다. 깊이 팔의 빨강과 깊이 삼의 파랑이라면, 작은 값이 가까운 이 예제에서는 어느 것을 먼저 처리해도 파랑이 남습니다.',
 '둘째 문제는 빛을 스스로 내지 않는 이상적인 람버트 확산면입니다. 반사율은 영 점 육, 도착하는 복사조도는 제곱미터당 십 와트로 정합니다.',
 '반사 분포는 반사율을 파이로 나눕니다. 출사 복사휘도는 영 점 육에 십을 곱하고 파이로 나눈 값, 약 일 점 구 일입니다.',
 '단위는 와트를 제곱미터와 스테라디안으로 나눈 것입니다. 복사출사도는 제곱미터당 육 와트이므로, 두 값을 같은 양으로 다루면 안 됩니다.',
 '이것은 반사율과 입사광을 직접 정한 계산입니다. 게임 화면의 밝은 픽셀에서 이 수치를 바로 측정한 것은 아닙니다.',
 '보이는 표면을 고르고, 단위를 구분하고, 빛과 재질과 시선을 연결했습니다. 다음 강의에서는 카메라와 투영의 좌표를 연결해 삼차원 점을 화면으로 옮기겠습니다.'
],[
 'First: with smaller-is-nearer toy depths red eight and blue three, either processing order leaves blue.',
 'Next define a nonemissive ideal Lambertian surface with reflectance zero point six and irradiance ten watts per square metre.',
 'Its BRDF is reflectance divided by pi; outgoing radiance is zero point six times ten divided by pi, approximately one point nine one.',
 'Radiance units are watts per square metre per steradian. Exitance is six watts per square metre, a different quantity.',
 'These are explicitly defined reflectance and illumination conditions, not values measured from game display pixels.',
 'Select a surface, distinguish quantities, connect light with material and view. Next we connect camera and projection coordinates to map3D points to the screen.'
],['깊이 8과 3: 순서에 관계없이 파랑','비발광 Lambert / ρ=0.6 / E=10 W/m²','fᵣ=ρ/π / Lₒ=ρE/π=6/π≈1.91','Lₒ: W/(m² sr) / M=6 W/m²','조건을 정한 계산 / 게임 수치 측정이 아님','다음: 카메라·투영·좌표 공간'])
assert [s['id'] for s in scenes]==[f'{i:02}' for i in range(1,23)]
data={'slug':slug,'chapter':10,'part':1,'totalParts':6,'renderModule':'rendering_light','sourceDependencies':['manim/projects/game-math-part2-full-series/lesson.py'],'sourceSections':['10.1.1','10.1.2','10.1.3','10.1.4'],'contract':{'visibility':'Original toy opaque depths8/3 with smaller-is-nearer; actual depth encoding, reversed-Z and tie rules are distinct. Surface selection differs from lighting; no game engine inference.','directions':'Both wi and wo point away from the same surface position; n outward and unit vectors. Front-side cosine positive n dot wi; actual incident travel is -wi.','quantities':'J, W, irradiance/exitance W/m2, radiance W/(m2 sr), BRDF1/sr. RGB is a color representation, not literally3 wavelengths. Photometry weights spectral response; not subjective brightness.','reflection':'Nonnegative passive reciprocal BRDF; integral energy restriction, not pointwise <=1. BSDF same-position reflection/transmission; BSSRDF distinct positions; volumes separate. Nonemissive Lambertian f=rho/pi with0<=rho<=1.','equation':'Lo=Le+integral hemisphere Li fr max(0,n dot wi) dwi. Toyrho.6/E10 gives6/pi; exitance6. Finite quadrature weights/normalized sampling and linear-light values.'},'coverage':{'10.1.1':['02','03','04','05','06','22'],'10.1.2':['07','08','09','10'],'10.1.3':['11','12','13','14','15','20','22'],'10.1.4':['16','17','18','19','20','21','22']},'scenes':scenes,'gameCandidates':{'reviewedAt':'2026-10-08','selected':[{'game':'Big Walk','sourceId':W,'reason':'Fresh existing-game recording with observed uploader permission; opaque occlusion, transparent tank, colored surfaces, shadows and moving camera.'},{'game':'Subnautica 2','sourceId':S,'reason':'Fresh distinct title/recording; actual lamp orientation, lit base surfaces and ceiling-light placement visibly connect emission and reflection.'}],'rejected':[{'game':'Other rendering-game candidates','reason':'No confirmed reusable recording inspected; selected two fresh permitted existing-game sources instead.'},{'game':'Big Walk dusk/long chat','reason':'Unrelated floating conversation and nearly static shots distract from the exact lesson; excluded.'},{'game':'Subnautica 2 long dark caves and menus','reason':'Menus/storage/build selection and poorly readable intervals excluded; fine boundary guards trimmed remaining clips.'}],'historyReview':'Current project/source/history search found no exact title/recording match. Original Subnautica existed in prior work and is distinguished. Source-index native permission, fine pixels and boundary review precede narration; game IP public review pending.'}}
# After measured speech, refine real source boundaries and align each subject's
# shots with its spoken paragraphs. Initial pre-synthesis approval is preserved.
refinement=json.loads((B/'preflight/rendering-light-source-groups.json').read_text(encoding='utf8'))
for scene in scenes:
 if scene['id'] in refinement['groups']:
  segments=refinement['groups'][scene['id']]
  scene.update(sourceSegments=segments,**{'in':segments[0]['in']},maxSeconds=sum(s['maxSeconds'] for s in segments))
 if scene['id']=='17':
  for language in ['ko','en']:scene[language]=[scene[language][i] for i in refinement['paragraphOrder17']]
data['postNarrationSourceRefinement']='production/batches/game-math-part2-full-series/preflight/rendering-light-source-groups.json'
out=B/'lessons'/f'{slug}.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'slug':slug,'scenes':len(scenes),'koLines':sum(len(s['ko']) for s in scenes),'koChars':sum(sum(map(len,s['ko'])) for s in scenes),'actualCapacitySeconds':sum(s.get('maxSeconds',0) for s in scenes)}))
