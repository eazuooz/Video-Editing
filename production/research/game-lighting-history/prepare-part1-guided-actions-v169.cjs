// Add only new source-informed narration. Never rewrite retained PCM or completed parts.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production',s='projects/game-lighting-history-04/script';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,j)=>{if(fs.existsSync(path.join(root,p)))throw Error('Preserve '+p);fs.writeFileSync(path.join(root,p),JSON.stringify(j,null,2)+'\n');};
const selection=read(b+'/part1-native-continuous-observations-v169.json');
if(!selection.sourceBeforeScriptReviewed)throw Error('Direct candidate observations required before new narration');
cp.execFileSync(process.execPath,['scripts/review-video-duplicates.cjs','game-lighting-history-04-1','--candidate-file','production/research/game-lighting-history/candidate-04-1.json','--check'],{cwd:root,stdio:'inherit'});
const src=read(b+'/part1-source-selection-direct-review-v167.json').sources,scenes=[];
function add(id,role,source,ranges,after,ko,en,focus){scenes.push({id,role,source,ranges,insertAfter:after,ko,en,focus,sourceTimeIsNativeFileSeconds:true,normalSpeed:true,sourceAudio:false,loop:false,slowdown:false,exactCutAndMovingPixelsApproved:false});}
add('shadow-address-view','actual','vsmInitial',[[17,29]],'03-guide-vsm-regions',
'이제 실제 편집기입니다. 여러 색으로 나뉜 그림자 시각화와 일반 화면을 구별하세요. 색 구역은 그림자 자료를 살펴보는 표시입니다. 벽에 새 색의 조명을 단 장면은 아니죠.',
'In the editor, distinguish the colored shadow visualization from the ordinary view. The colored regions inspect shadow data; they are not new colored lights on the wall.',
'Track the original shadow visualization and its return to the lit view. Preserve its legend.');
add('shadow-wheel-surface','actual','vsmInitial',[[112,146]],'04-guide-vsm-motion',
'바퀴와 차체 주변으로 카메라가 이동합니다. 먼저 바퀴의 표면과 그 아래 그림자를 따로 잡아 보세요. 관찰 방향이 달라지면 필요한 그림자 영역도 달라질 수 있습니다. 그림자가 부드러워 보인다는 인상과, 어떤 영역을 새로 계산했는지는 별도의 질문입니다. 지금 화면에서는 물체와 카메라의 움직임을 연결해서 보는 것이 먼저입니다.',
'As the camera moves around the wheel and body, identify the wheel surface and its shadow separately. A changed view can require different shadow regions. Apparent softness and which regions were recomputed are different questions. First connect the visible object with the camera movement.',
'Red outline tracks wheel-ground contact; teal follows the separate shadow region. No unobserved cache-hit claim.');
add('shadow-wheel-change','actual','vsmInitial',[[146,181]],'shadow-wheel-surface',
'이번에는 화면에 새로 들어오는 면을 따라가세요. 이전 화면에 있었다는 이유만으로 모든 그림자 자료를 계속 재사용할 수는 없습니다. 물체나 빛이 바뀌면 그 자료가 나타내던 조건도 바뀌기 때문이죠. 페이지 캐시는 큰 지도를 잘게 나누어 필요한 부분을 다루는 방법입니다. 실제로 다시 그렸는지 판단하려면 이런 움직임과 함께 엔진의 무효화 시각화도 확인해야 합니다.',
'Follow surfaces entering the view. Previous presence does not guarantee valid reusable shadow data when objects or lights change. A page cache divides a large map so the required regions can be handled separately. Establishing actual redraws also requires the engine’s invalidation visualization.',
'Use moving surface boundaries as observation; describe invalidation as a separate diagnostic requirement.');
add('shadow-resource-cache','actual','vsmPool',[[98,122],[184,198]],'original-18v-7',
'자원 보기 창으로 옮겨 갑니다. 이름에 그림자와 물리 페이지 풀이 함께 적힌 자료를 찾아보세요. 가상 주소는 어느 영역인지 알려 주고, 물리 풀은 실제 저장 공간을 맡습니다. 앞의 도식에서 그린 주소 칸과 저장 칸을 이 두 역할에 연결할 수 있죠. 카메라를 움직이는 장면과 자원 이름을 읽는 장면을 함께 보되, 이름 하나로 이번 프레임의 재사용률까지 알았다고 말하지는 않겠습니다.',
'In the resource viewer, locate the shadow physical-page pool. Virtual addresses identify regions, while the physical pool supplies storage. Connect those roles with the address and storage cells in the diagram. A resource name alone does not reveal this frame’s reuse rate.',
'Only label the resource actually shown; separate page address from physical storage. Do not claim a512→128 pool edit.');
add('texture-streaming-input','actual','vt',[[6,35]],'shadow-resource-cache',
'같은 메모리 문제를 표면 무늬에서도 보겠습니다. 먼저 텍스처 설정의 가상 스트리밍 항목을 바꾸고, 이어서 머티리얼 그래프로 들어갑니다. 무늬를 저장하는 자산과 그 무늬를 읽는 셰이더 입력이 연결되어 있죠. 그림자 페이지에는 빛에서 본 깊이가 들어갔지만, 이번 타일에는 표면 자료가 들어갑니다. 둘 다 필요한 부분을 다룬다는 생각은 공유해도, 저장한 정보와 읽는 작업은 다릅니다.',
'The same memory question appears in surface textures. A virtual-streaming setting is followed by the material graph, connecting the texture asset with its shader input. Shadow pages stored light-view depth; these tiles store surface data. They share selective residency, but hold different information and serve different readers.',
'Follow the actual checkbox then material sampler; distinguish shadow depth from surface texels.');
add('texture-stack-uv','actual','vt',[[96,120]],'texture-streaming-input',
'그래프에서는 같은 좌표를 쓰는 입력들을 보세요. 입력을 복제하고 연결을 바꾸자 표시된 가상 텍스처 스택 수가 달라집니다. 스택은 함께 묶을 수 있는 읽기 작업과 연결된 개념입니다. 좌표를 공유하면 같은 주소 계산을 묶을 여지가 생기지만, 연결이 달라지면 묶음도 달라질 수 있죠. 여기의 스택 숫자를 전체 프레임의 시간이나 모든 텍스처 읽기 횟수로 바꾸어 읽지는 않습니다.',
'Follow inputs sharing coordinates as nodes are duplicated and reconnected. The displayed virtual-texture stack count changes. Sharing coordinates can allow address work to be grouped, while different connections can alter that grouping. A stack count is not total frame time or the number of all texture reads.',
'Point to actual UV connections and displayed stack count3→4, not invented lookup totals.');
add('texture-dependent-conversion','actual','vt',[[202,219]],'texture-stack-uv',
'변환 창에서는 제목의 방향부터 읽습니다. 여기서는 가상 텍스처를 일반 텍스처로 바꾸는 창입니다. 아래에는 영향을 받는 텍스처와 머티리얼이 함께 나옵니다. 자산 하나의 표시만 바꾸는 일이 아니라, 그 자산을 읽는 입력도 맞아야 한다는 점을 보세요.',
'Read the conversion direction first: this window converts virtual textures to ordinary textures. Its affected textures and materials show that the readers must match the changed asset as well.',
'Preserve the actual ConvertVTTextures toTextures window title and dependency list.');
add('texture-project-tile-settings','actual','vt',[[246,266]],'texture-dependent-conversion',
'프로젝트 설정에서 가상 텍스처 항목을 찾습니다. 타일 크기와 경계 설정을 별도로 읽어 보세요. 타일을 크게 잡으면 한 번에 가져오는 영역이 커지고, 경계는 이웃을 걸쳐 필터링할 때 필요한 자료와 연결됩니다. 경계를 넓히는 선택에는 저장 공간의 비용도 있습니다. 설정을 바꾸기 전에 어떤 표면과 필터 조건을 위해 쓰는지부터 정하는 이유입니다.',
'Locate virtual-texture settings and distinguish tile size from border size. Larger tiles fetch larger regions; borders provide neighboring data for filtering and also consume storage. Select them with the surface and filtering requirements in mind.',
'Label only the visible tile/border fields; no performance result is inferred from settings.');
add('runtime-texture-producer','actual','vt',[[394,409]],'texture-project-tile-settings',
'화면은 런타임 가상 텍스처 자산입니다. 먼저 변위 자료를 저장하는 항목을 보세요. 실행 중에 필요한 표면 결과를 만들어 캐시에 두는 방식이죠. 처음 자료를 만드는 비용과, 나중에 저장한 자료를 읽는 비용을 나누어 생각하겠습니다.',
'This runtime virtual-texture asset specifies displacement data. Runtime-generated surface results can be cached. Separate the initial production cost from later reads of the stored data.',
'Read actual RVT_Displacement asset/content field. No material write/read graph is claimed.');
add('runtime-texture-consumer','actual','vt',[[441,467]],'runtime-texture-producer',
'다음 자산은 색 자료입니다. 저장할 정보 형식과 타일 관련 값이 함께 보이죠. 같은 가상 텍스처라도 무엇을 담는지가 다르면 읽는 표면의 역할도 달라집니다. 앞의 그림자 페이지는 깊이를 비교할 자료였고, 이번에는 표면 표현에 쓸 자료입니다. 타일을 크게 고르는 선택과 색 형식을 고르는 선택을 구분하세요. 크기가 같다는 사실만으로 두 자료의 의미나 만드는 비용이 같아지지는 않습니다.',
'The next asset stores color information, alongside tile settings. Different contents serve different readers: shadow pages supplied depth comparisons, while this asset supplies surface data. Choosing tile size and choosing content format are separate decisions; equal dimensions do not imply equal meaning or production cost.',
'Read RVT_Color/content format and actual edited tile size. Exclude the middle stationary asset interval409–441.');
add('runtime-texture-size','actual','vt',[[514,533],[553,564]],'runtime-texture-consumer',
'이번 자산 창에서는 가상 텍스처 크기와 타일 관련 항목이 보입니다. 주소로 표현할 수 있는 큰 영역과 실제로 남겨 둘 자료의 크기를 구분하세요. 큰 주소 범위를 준비했다고 모든 텍셀이 한꺼번에 메모리에 올라온다는 뜻은 아닙니다. 필요한 타일을 찾는 자료에도 공간이 들기 때문에, 주소와 내용을 각각 예산으로 잡아야 합니다.',
'The asset exposes virtual dimensions and tile settings. Distinguish the addressable extent from the resident contents. A large address range does not mean every texel is simultaneously resident. Addressing data also needs storage, so budget addresses and contents separately.',
'Point to actual RVT asset fields, keeping them distinct from the VSM pool.');
add('ordinary-streaming-budget','actual','vt',[[648,656],[670,682]],'runtime-texture-size',
'다음 통계는 일반 텍스처 스트리밍입니다. 화면의 스트리밍 이름과 풀 크기 콘솔 항목을 먼저 읽어 보세요. 앞의 가상 텍스처 물리 풀과 한 숫자로 합치면 어떤 자료가 부족한지 놓치게 됩니다. 예산을 확인할 때에는 수치보다 먼저 그 수치가 어느 저장 공간을 뜻하는지 적어 두겠습니다.',
'These are ordinary texture-streaming statistics. Read the Streaming label and pool-size control before interpreting the numbers. Combining them with the virtual-texture physical pool would hide which storage is constrained. Identify the resource represented by a value first.',
'Highlight stat Streaming and r.Streaming.PoolSize as ordinary streaming, never VT residency.');
add('virtual-pool-policy','actual','vt',[[746,770]],'ordinary-streaming-budget',
'이제 가상 텍스처 풀 설정으로 돌아옵니다. 기본 크기와 고정 풀, 편집기에서 자동으로 늘리는 항목을 구분하세요. 편집하는 동안 맞는 크기를 찾는 과정과, 배포할 설정을 저장하는 과정은 다릅니다. 자동으로 늘었다는 경험만 기억하면 다시 실행했을 때 같은 조건이 재현되지 않을 수 있죠. 자료 종류와 풀 설정을 함께 기록해야 비교가 이어집니다.',
'Return to virtual-texture pool settings: default capacity, fixed pools and editor auto-growth have different roles. Discovering capacity while editing differs from saving a deployment configuration. Record both the resource type and its pool policy to reproduce the comparison.',
'Preserve actual AutoGrowInEditor and fixed/transient fields; avoid asserting cooked-game behavior from the editor alone.');
add('texture-scene-return','actual','vt',[[1047,1069]],'virtual-pool-policy',
'설정을 본 뒤 실제 장면으로 돌아옵니다. 바닥과 벽을 가로지르는 카메라, 선택한 표면의 경계를 보세요. 무늬가 선명하다는 결과만으로 캐시 상태를 모두 알 수는 없습니다. 장면을 이동하며 새로 보이는 표면을 구별하고, 필요한 경우 그때의 스트리밍 통계를 함께 남기는 것이 다음 실험의 기준입니다.',
'Return to the scene and follow the camera across floors and walls. Sharp-looking textures alone do not reveal the cache state. Identify newly exposed surfaces during movement and record the relevant streaming statistics when a measurement is required.',
'Track only visible selected surfaces and camera motion, without claiming a cache effect from the image.');
add('tsr-silhouette-history','actual','tsrMan',[[0,37]],'06-guide-tsr-reveal',
'이제 움직이는 마네킹을 보겠습니다. 내부에서 적은 픽셀을 그린 결과와, 시간 자료를 이용해 보여 줄 화면을 만드는 과정을 연결하는 사례입니다. 먼저 인물의 몸통과 배경 사이 경계를 따라가세요. 경계가 움직이면 이전 프레임에서 같은 자리에 있던 자료가 지금은 다른 표면일 수 있습니다. 과거 자료를 많이 모으는 것만큼, 어느 자료를 계속 믿을지 정하는 일이 필요하죠. 작은 해상도에서 시작한다는 조건과 최종 출력 해상도를 따로 읽겠습니다.',
'Follow the moving mannequin’s silhouette against the background. Starting with fewer internal pixels makes valid temporal information valuable, but a previous pixel can represent a different surface after motion. Reuse therefore requires deciding which history remains trustworthy. Read internal resolution separately from output resolution.',
'Track silhouette/disocclusion; preserve the source’s resolution labels. End before the Note on TSR lecture.');
add('tsr-rotation-vectors','actual','tsrFan',[[0,32]],'tsr-silhouette-history',
'회전하는 날개에서는 얇은 경계를 잡아 보세요. 빠르게 위치가 바뀌는 경계와 새로 드러나는 배경은 과거 자료를 그대로 가져오기 어려운 곳입니다. 움직임 벡터는 대응 위치를 찾는 단서지만, 가려졌다가 나온 배경의 정답을 저절로 만들어 주지는 않습니다. 앞의 마네킹은 큰 윤곽을 보여 주었고, 이번 날개는 얇고 빠른 윤곽을 보여 줍니다. 같은 시간 복원 원리도 이 두 조건을 따로 처리해야 합니다.',
'Thin rotating blades expose rapidly changing edges and newly uncovered background. Motion vectors help locate corresponding samples but do not supply the correct newly revealed background by themselves. Compare the mannequin’s broad silhouette with these thin fast edges: both use temporal reconstruction under different history-validity conditions.',
'Track a blade tip and uncovered background; keep vector visualization colors diagnostic, not material colors.');
add('horizon-comparison-before','explanation',null,[],'tsr-rotation-vectors',
'같은 질문을 실제 게임 네 종으로 옮겨 보죠. 먼저 호라이즌에서는 복원 방식 표시와 움직이는 가방의 자수를 함께 봅니다. 같은 물체의 경계를 따라가야 비교가 됩니다.',
'Transfer the question to four games. In Horizon, read the reconstruction-method labels and follow the embroidery on the moving bag, keeping the same object as the reference.',
'Projected silhouette → same-object detail; game switch announces method labels, no invented input-resolution value.');
add('horizon-detail-motion','actual','horizon',[[1,7.35]],'horizon-comparison-before',
'알로이의 가방 자수가 움직입니다. 두 복원 표시를 읽고 같은 무늬의 경계를 보세요.',
'Follow the moving embroidery on Aloy’s bag and compare its edges under the two labelled reconstruction methods.',
'Same bag detail under CNN/Transformer SR labels; no freeze, loop or invented quantitative score.');
add('outer-comparison-before','explanation',null,[],'horizon-detail-motion',
'자수의 복원과 화면을 더 자주 표시하는 일은 다릅니다. 아우터 월드에서는 프레임 생성 배수 표시를 읽어 보죠.',
'Detail reconstruction differs from displaying more frames. In The Outer Worlds, inspect the frame-generation multiplier.',
'Projected rendered-image and displayed-image cells stay distinct from simulation tick.');
add('outer-displayed-frames','actual','outer',[[0.5,16]],'outer-comparison-before',
'카메라와 장면이 바뀌면서 생성 배수 표시도 바뀝니다. 표시된 프레임 수는 원본 시연의 값입니다. 더 자주 보이는 화면과 게임 상태를 더 자주 계산하는 일을 구분하세요. 앞의 가방 비교는 표면 세부의 복원이었고, 이번 비교는 표시 빈도의 역할입니다.',
'The source changes scenes and its generation multiplier. Its FPS is the source demonstration’s value. Distinguish more frequent displayed images from more frequent game-state updates. The bag comparison reconstructed detail; this example examines display frequency.',
'Retain original dynamic-MFG multiplier/FPS labels and reset targets at every shot cut.');
add('cyber-comparison-before','explanation',null,[],'outer-displayed-frames',
'이번에는 사이버펑크의 빛 복원입니다. 표시된 조건을 읽고, 움직이는 장면의 반사와 간접광을 따로 살펴보겠습니다.',
'Next inspect light reconstruction in Cyberpunk. Read the conditions and identify reflection and indirect-light regions in the moving scene.',
'Separate surface-detail, display-rate and light-reconstruction roles on projected planes.');
add('cyber-light-reconstruction','actual','cyber',[[44,62]],'cyber-comparison-before',
'원본은 디엘에스에스 삼 점 오를 소개하는 게임 장면입니다. 인물과 카메라가 움직일 때 표면의 빛과 반사를 보세요. 여기에는 여러 처리 단계가 함께 적용됩니다. 한 기능만 바꾼 고정 카메라 실험으로 단정하지 않고, 적은 빛 샘플을 화면으로 복원한다는 역할을 비교하겠습니다. 앞의 자수와는 입력 자료가 다릅니다.',
'This DLSS3.5 game demonstration combines several processing stages. Follow surface light and reflections during motion. It is not an isolated single-feature fixed-camera experiment. Compare the role of reconstructing sparse lighting information with the different inputs used for embroidery detail.',
'Track an actual reflective/light region with source conditions retained; end before Phantom Liberty title.');
add('geometry-road-mask','actual','nanite',[[24,42]],'original-18a-3',
'지오메트리 시각화로 돌아옵니다. 굽은 길과 표지판이 있는 장면에서 도로의 표시를 따라가세요. 초록색 영역은 현재 선택한 시각화의 자료입니다. 일반 장면에서 보던 무늬와 디버그 색을 구별하면, 어느 자료를 검사하는지 먼저 묻는 습관을 이어갈 수 있습니다.',
'Return to geometry diagnostics and follow the curved road and sign. Green regions belong to the selected visualization. Distinguish debug colors from ordinary material appearance and identify the inspected data first.',
'Track road mask and spatial curve; keep the source mode label.');
add('geometry-barrier-views','actual','nanite',[[96,134]],'geometry-road-mask',
'이번에는 같은 장면을 선과 삼각형 표시, 일반 표현으로 바꿉니다. 겉으로 보이는 면이 어떤 작은 요소로 나뉘었는지와, 그 면에 어떤 재질이 입혀졌는지를 각각 볼 수 있죠. 시각화를 바꾼다고 같은 숫자 하나를 다른 색으로 칠한 것은 아닙니다. 읽는 자료가 바뀌므로 범례도 다시 확인해야 합니다. 앞의 그림자 페이지와 텍스처 타일 역시, 작은 칸이라는 모양만 같고 칸 안의 의미는 달랐습니다.',
'The scene switches among wireframe, triangle diagnostics and ordinary shading. Geometry subdivision and material appearance answer different questions, so read each mode’s legend again. A shared small-cell appearance does not make geometry elements, shadow pages and texture tiles the same data.',
'Preserve each mode transition; no invented triangle count. Cut before loading/blank frame.');
add('geometry-courtyard-data','actual','nanite',[[180,217]],'07-pre-visibility-interpolation',
'사람이 움직이는 마당에서도 진단 표시와 일반 화면이 번갈아 나옵니다. 표시가 달라져도 인물과 벽의 위치를 기준으로 유지하세요. 표면을 찾는 자료와 그 표면의 색을 계산할 자료를 나눠 읽기 위한 비교입니다. 앞에서 배운 가시성 버퍼는 어떤 면이 보이는지의 식별 자료를 남기는 생각이었죠. 다만 이 진단 색 하나만으로 이 장면의 모든 버퍼 구조를 알아냈다고 말할 수는 없습니다.',
'In the moving courtyard, keep people and walls as spatial references while diagnostics alternate with ordinary shading. Separate locating a surface from shading it. The visibility-buffer idea retains visible-surface identifiers, but a diagnostic color alone does not verify every buffer in this scene.',
'Track people/wall boundaries; clearly label the current diagnostic before naming colors.');
add('geometry-programmable-material','actual','nanite',[[306,350]],'original-18a-6',
'이제 프로그래머블 표시로 바뀝니다. 메뉴 선택 뒤 나무와 바닥의 표시가 달라지는 순서를 보세요. 복잡한 표면의 역할을 분리해서 검사하는 방법입니다. 면의 위치를 아는 것과 그 면의 표현에 필요한 작업을 아는 것은 다르죠. 같은 지오메트리를 보여도 머티리얼의 입력과 분기는 비용에 영향을 줄 수 있습니다. 따라서 작은 지오메트리 식별 자료를 쓴다는 설명을, 뒤의 모든 셰이딩 비용이 사라졌다는 뜻으로 받아들이면 안 됩니다.',
'Follow selection of the programmable diagnostic and the changing tree and ground colors. Knowing a surface location differs from knowing its shading work. Material inputs and branches can still affect cost. Compact geometry identifiers do not remove all subsequent shading work.',
'Name actual Pixel Programmable mode only when visible; no asserted buffer layout or timing from colors.');
add('geometry-car-material','actual','nanite',[[372,381]],'geometry-programmable-material',
'자동차 표면의 표현이 바뀝니다. 같은 차체와 바퀴를 기준으로, 모양과 재질 표현을 따로 읽어 보세요.',
'The car’s surface appearance changes. Keep the body and wheel as references while separating shape from material appearance.',
'Track body surface silver→rust; do not hold the later unchanged shot.');
add('mobile-texture-group','actual','mobile',[[0,16]],'original-18m-2',
'모바일 편집기에서는 텍스처 그룹부터 고릅니다. 같은 돌 무늬라도 어느 용도로 묶는지에 따라 사용할 크기 정책을 따로 정할 수 있죠. 화면 오른쪽의 그룹 선택과 왼쪽의 실제 무늬를 연결해서 보세요. 그룹 이름을 고른 장면이며, 기기의 속도를 측정한 결과는 아닙니다.',
'The mobile editor selects a texture group. Grouping the stone texture by usage permits a corresponding size policy. Connect the selected group with the texture preview; this is policy selection rather than a device-speed measurement.',
'Crop actual embedded editor, preserve group dropdown and texture preview, remove lecture surroundings.');
add('mobile-device-policy','actual','mobile',[[30,50]],'mobile-texture-group',
'다음에는 기기 프로파일 목록입니다. 안드로이드 항목과 그 안의 설정을 보세요. 플랫폼 이름 하나로 모든 기기의 메모리와 화면 조건이 같아지지는 않습니다. 프로파일은 조건에 맞춰 어떤 설정을 적용할지 정하는 연결점입니다. 같은 무늬를 그려도 어떤 크기를 고르고 어떤 기능을 켤지 달라질 수 있죠. 비교할 때에는 선택한 프로파일 이름을 먼저 남기겠습니다.',
'The device-profile list connects Android conditions with settings. A platform name does not make every device’s memory and display identical. Record the selected profile before comparing policies for texture size or enabled features.',
'Preserve actual Android profile selection, profile fields and override UI; no general device capability claim.');
add('mobile-lod-settings','actual','mobile',[[66,91]],'mobile-device-policy',
'프로파일 안에서 텍스처 상세도 항목을 조절합니다. 큰 원본 무늬가 있어도 이번 기기에 어느 수준까지 가져올지는 따로 정할 수 있죠. 여기의 최대 크기와 상세도 설정은 그 선택을 기록하는 입력입니다. 작은 자료를 쓰면 저장 공간과 전송량을 줄일 여지가 있지만, 가까이 보이는 표면 세부도 함께 확인해야 합니다. 설정값과 결과 화면을 둘 다 남기는 이유입니다.',
'Texture-detail controls decide how much of a large source texture to use on this device. Maximum-size and LOD fields record that choice. Smaller data can reduce storage and transfer requirements, but inspect nearby surface detail as well as the chosen settings.',
'Track LOD field/dropdown changes; no invented memory reduction or direct before/after result.');
add('mobile-console-policy','actual','mobile',[[91,116]],'mobile-lod-settings',
'이어지는 콘솔 변수 목록도 프로파일에 붙는 설정입니다. 같은 값이라도 무엇을 조절하는 이름인지 알아야 해석할 수 있죠. 텍스처 크기, 그림자 처리, 화면 복원처럼 다른 단계의 예산을 한 숫자로 묶지 마세요. 지금은 어느 기기에 어느 설정을 적용할지 확인하는 시연입니다. 실제 이득은 그 기기에서 장면과 해상도 조건을 고정해 따로 측정해야 합니다.',
'Console variables attach further policies to the profile. Interpret each value through the control it names. Texture size, shadows and image reconstruction receive different budgets. This demonstration selects device settings; benefits require a separate measurement under defined scene and resolution conditions.',
'Highlight only visible CVar names; distinguish configuration from measured result.');
add('mobile-compiler-availability','actual','mobile',[[132,150]],'mobile-console-policy',
'셰이더 통계 화면에서는 먼저 경고를 보겠습니다. 일부 대상 플랫폼에 필요한 오프라인 컴파일러가 준비되지 않았다는 표시입니다. 비어 있는 항목을 가벼운 셰이더라는 점수로 읽으면 안 됩니다. 자료가 나온 항목과 나오지 않은 항목을 구분하고, 도구와 대상 플랫폼을 확인한 뒤 비교해야 합니다. 측정의 빈칸도 기록에 남기는 것이 정확한 검수입니다.',
'The shader statistics view warns that one target platform requires an offline compiler. Separate available entries from unavailable ones; an empty entry is not evidence of a cheap shader. Verify the tool and target platform, and record missing measurements honestly.',
'Keep actual compiler warning readable, no fabricated shader-cost values.');
add('fortnite-comparison-before','explanation',null,[],'09-guide-mobile-limits',
'앞의 세 게임은 복원과 표시를 비교했습니다. 포트나이트에서는 실제 모바일 테스트 장면과 성능 자료를 연결해 보겠습니다.',
'The preceding games compared reconstruction and display. Fortnite now connects a mobile test scene with performance diagnostics.',
'Four game roles: same object detail/history, generated display frequency, reconstructed lighting, target-device budget.');
add('fortnite-mobile-test','actual','mobile',[[240,260]],'fortnite-comparison-before',
'포트나이트의 모바일 테스트 맵입니다. 캐릭터와 카메라가 바위를 지나갑니다. 돌 표면의 고품질과 저품질 표시를 먼저 읽고, 왼쪽 그래프와 표면을 따로 보세요. 서로 다른 재질 조건을 확인하는 자료입니다. 기기 예산을 논의하려면 어떤 장면에서 어떤 자료를 읽었는지 함께 남겨야 합니다.',
'In Fortnite’s mobile test map, the character and camera move past rocks. Read the high- and low-quality surface labels, then separate the left diagnostic graph from the surfaces. Record both the material conditions and the diagnostic being inspected.',
'Crop full phone game view, preserve HQ/LQ noise-bump labels and graph; exclude presenter before240. Not an ordinary Battle Royale benchmark.');
add('fortnite-normal-material','actual','mobile',[[276,289.8]],'fortnite-mobile-test',
'벽의 테스트 항목으로 옮겨 갑니다. 카메라가 가까워질 때 표면과 원본 통계를 함께 보세요. 같은 게임에서도 재질 조건은 달라집니다. 앞의 복원 사례들과 마찬가지로 비교 대상과 입력 조건을 먼저 구별하는 원칙이 적용됩니다.',
'Move to the wall’s test surface. Inspect the surface and source diagnostics as the camera approaches. Material conditions vary even within one game. As in the reconstruction examples, identify the object and input conditions before interpreting the comparison.',
'Crop the later phone inset to full screen; preserve actual GBuffer Normals label without claiming this is a complete GBuffer visualization. No tile-memory transfer assertion.');
add('rivalry-mobile-history','actual','rivalry',[[26,41],[51,90]],'fortnite-normal-material',
'시간을 이천십사년으로 돌려 모바일 엔진 기술 시연을 보겠습니다. 갑옷을 입은 인물과 빛이 움직이는 장면입니다. 게임 네 종의 사례 수에는 더하지 않지만, 당시 모바일에서 어떤 표현을 보여 주려 했는지 확인할 수 있죠. 밝은 금속면과 어두운 배경을 같은 기준으로 따라가세요. 이 영상의 연도와 시연이라는 조건을 남겨 두고, 뒤에 나온 모바일 디퍼드 방식의 구현 증거로 바꿔 읽지 않겠습니다. 모바일 화면의 목표와 그 목표를 실현하는 방식의 역사를 구별하는 사례입니다.',
'Return to2014 for a mobile engine technology demonstration. Follow the armored figure, bright metal and dark background. It adds historical context, not a fifth game. Retain its year and demonstration status rather than treating it as proof of a later mobile-deferred implementation. Separate a display goal from the implementation history.',
'Track armor/metal lighting at normal speed; exclude the intervening cartoon/title. No game-count inflation.');
add('four-game-transfer-conclusion','explanation',null,[],'rivalry-mobile-history',
'네 게임에서 본 것은 하나의 화질 점수가 아닙니다. 표면 세부를 복원하고, 화면을 더 자주 표시하고, 빛 자료를 복원하고, 기기의 예산을 확인하는 서로 다른 질문이었죠. 어떤 자료를 만들고 저장하며 다시 읽는지 묻는 방법은 네 경우에 모두 적용됩니다.',
'The four games did not supply one universal quality score. They examined detail reconstruction, display frequency, lighting reconstruction and a device budget. The transferable question is which data is produced, stored and reused.',
'Projected four inputs converge on producer→storage→reader; retain role differences, no common numerical score.');
// Complete observations with algorithmic questions while retaining each actual moving reference.
const extra={
'shadow-wheel-surface':[
' 여기서 기준을 바퀴에 둔 이유는 세 가지 움직임을 구분하기 위해서입니다. 물체가 움직였는지, 시점이 움직였는지, 빛의 조건이 바뀌었는지를 차례로 묻습니다. 같은 화면 변화라도 이 셋은 필요한 그림자 자료를 다르게 바꿀 수 있습니다.',
' Keep the wheel as a reference while separating object movement, viewpoint movement and changed lighting conditions. Similar image changes can alter the required shadow data in different ways.'],
'shadow-wheel-change':[
' 화면 밖으로 나갔다는 이유와 내용이 낡았다는 이유도 구분해야 합니다. 보이지 않는 영역을 당장 쓰지 않는 선택과, 잘못된 과거 값을 버리는 선택은 서로 다른 일입니다. 도식의 주소 칸을 찾는 화살표와 갱신하는 화살표가 다른 역할을 맡았던 이유죠.',
' Also distinguish no longer needed from no longer valid: skipping an unseen region differs from discarding stale contents. The diagram’s address lookup and update arrows therefore have different roles.'],
'shadow-resource-cache':[
' 자료를 찾는 창, 자료가 쓰이는 장면, 자료를 갱신하는 조건을 연결하면 기능 이름보다 구체적인 설명이 됩니다. 다른 엔진을 볼 때에도 이 순서로 질문해 보세요.',
' Connect the resource view, the consuming scene and the update conditions. This investigation method transfers to another engine even when its implementation differs.'],
'tsr-silhouette-history':[
' 인물이 지나간 뒤 배경이 다시 나타나는 부분이 좋은 관찰 지점입니다. 그 자리의 오래된 인물 색을 계속 섞으면 배경의 경계를 흐릴 수 있습니다. 과거의 표면과 현재의 표면이 같은지를 먼저 따져야 하는 이유입니다.',
' Newly revealed background behind the figure is a useful observation region. Continuing to mix the old figure’s color can blur its boundary; check whether history and the current pixel represent the same surface.'],
'tsr-rotation-vectors':[
' 한 방향으로 천천히 가는 넓은 면과 회전하는 얇은 날개는 대응의 난도가 다릅니다. 그래서 결과를 볼 때에는 전체 화면의 인상만 기억하지 말고, 끝점과 새로 드러난 배경을 각각 따라가겠습니다.',
' A broad slowly translating surface and a thin rotating blade present different correspondence challenges. Follow the tip and newly revealed background separately instead of relying only on an overall impression.'],
'geometry-barrier-views':[
' 비교의 기준은 장면 속 같은 벽과 장애물입니다. 카메라가 움직여도 그 위치를 따라가면 표시가 바뀐 것인지 대상이 바뀐 것인지 나눌 수 있습니다. 새 색의 의미를 읽기 전에 같은 대상을 찾는 순서를 지키겠습니다.',
' Keep the same wall and barrier as references across camera movement. First identify the same object, then interpret the new diagnostic; distinguish a changed visualization from a changed target.'],
'geometry-courtyard-data':[
' 사람 뒤로 드러나는 벽도 함께 보세요. 어느 표면이 앞에 있는지 결정하는 과정과, 드러난 표면의 무늬와 빛을 계산하는 과정은 구분됩니다. 이 둘을 따로 이해해야 뒤에서 읽어 올 자료가 무엇인지 설명할 수 있습니다.',
' Watch the wall revealed behind a person. Resolving which surface is in front differs from calculating the revealed surface’s texture and light. Separating those tasks identifies the data required later.'],
'geometry-programmable-material':[
' 여기서는 메뉴의 선택, 화면의 표시, 표면의 위치를 차례로 읽습니다. 선택한 항목을 놓치면 보라색이나 빨간색을 원래 재질의 색으로 오해할 수 있죠. 같은 표면을 어떤 자료의 관점으로 보고 있는지가 이번 장의 질문입니다.',
' Read the menu selection, diagnostic appearance and surface location in that order. Otherwise red or purple can be mistaken for the original material color. Ask which data perspective is being applied to the same surface.'],
'rivalry-mobile-history':[
' 인물이 움직일 때에는 밝은 금속면의 위치도 바뀝니다. 반짝임을 본 뒤에는 다음 질문이 필요합니다. 지금 비교하는 것은 표면의 표현일까요, 화면을 만드는 시간일까요? 앞의 포트나이트에는 통계 자료가 함께 있었지만, 이 기술 시연의 장면에는 같은 측정 조건이 없습니다. 그래서 두 영상을 같은 기기의 성능 순위로 붙이지 않고, 표현의 목표와 관찰 방법을 비교하는 데 쓰겠습니다.',
' The bright metal regions move with the figure. After observing the highlight, ask whether the comparison concerns appearance or rendering time. Fortnite supplied diagnostics, while this scene supplies no matching measurement conditions. Compare goals and observation methods rather than ranking device performance.']
};
for(const x of scenes)if(extra[x.id]){x.ko+=extra[x.id][0];x.en+=extra[x.id][1];}
const stamp=new Date().toISOString(),out=s+'/physical-part1-guided-actions.koen.v169.json';
for(const v of Object.values(src)){if(sha(v.path)!==v.sha256)throw Error('Changed native source '+v.path);}
const record={schemaVersion:1,preparedAt:stamp,physicalPart:'game-lighting-history-04-1',status:'source-informed paired additions; measured timing pending',sources:src,scenes,sourceObservation:{path:b+'/part1-native-continuous-observations-v169.json',sha256:sha(b+'/part1-native-continuous-observations-v169.json')},preservedOriginalParagraphs:111,preservedFramingScenes:5,regenerateOriginalPcm:false,style:'research-black-v1',fixedCaption:{style:'boxed-white-forest-v1',center:[960,970],fontSize:48,maxLines:2},voiceApproved:false,currentMixedAsrApproved:false,allFinalPixelsReviewed:false,fourGamesFullyTaughtAndReviewed:false,measuredBody60to40Approved:false,uploaded:false,avoidIdleQuota:true,nativeSourceCapacitySeconds:scenes.filter(x=>x.role==='actual').reduce((n,x)=>n+x.ranges.reduce((v,[a,z])=>v+z-a,0),0),koCharacters:scenes.reduce((n,x)=>n+x.ko.length,0)};
write(out,record);
for(const language of ['ko','en'])write(s+`/physical-part1-guided-actions.${language}.v169.json`,{title:language==='ko'?'제한된 픽셀과 메모리를 읽는 실제 사례':'Reading limited pixels and memory in actual examples',scenes:scenes.map(x=>({id:x.id,title:x.id,lines:[x[language]],screenRole:x.role}))});
const manifest=read('projects/game-lighting-history-04/project.json'),audioDir='shared/output/narration/game-lighting-history-04/qwen3-1.7b-part1-guided-actions-v169',stem='game-lighting-history-04-part1-guided-actions-v169';
manifest.paths={...manifest.paths,script:s+'/physical-part1-guided-actions.ko.v169.json',scriptEn:s+'/physical-part1-guided-actions.en.v169.json',narration:audioDir+'/'+stem+'.wav',captionsKo:audioDir+'/'+stem+'.srt',captionsEn:audioDir+'/'+stem+'.en.srt'};
manifest.tts={...manifest.tts,outputDir:audioDir,filenameStem:stem,maxNewTokens:1536,maxRenderAttempts:3,maxNewTokensReason:'Only new independent guided paragraphs; retained111 and five framing takes immutable.'};manifest.editing={...manifest.editing,exampleSeconds:0};
const mf=b+'/part1-guided-actions-tts-manifest-v169.json',req=b+'/part1-guided-actions-tts-request-v169.json',review=b+'/part1-guided-actions-script-review-v169.json';write(mf,manifest);
write(review,{reviewedAt:stamp,fullPairedKoEnDirectlyCompared:true,sourceBeforeScript:true,retained111TextAndPcmPreserved:true,framingFivePreserved:true,causalOrderReviewed:true,scope:'Exact cropped/native boundaries, complete four-game transfer, current mixed audio and final moving pixels remain independent gates.',scenes:scenes.map(x=>({id:x.id,ko:x.ko,en:x.en,insertAfter:x.insertAfter,role:x.role})),finalMixedAsrApproved:false,humanListeningApproved:false,pronunciationApproved:false,fourGamesFullyReviewed:false});
const retained=b+'/additive-unmixed-review-assembly-v2.json',ret=read(retained),protectedPaths=['projects/game-lighting-history-04/project.json',out,manifest.paths.script,manifest.paths.scriptEn,mf,review,retained,ret.audio.path,b+'/physical-framing-selected-execution-v55.json',b+'/physical-framing-asr-direct-progress-v58.json',b+'/physical-framing-direct-text-review-v59.json',b+'/part1-native-continuous-observations-v169.json',b+'/part1-source-selection-direct-review-v167.json','production/preflight/game-lighting-history-04-1.json','production/research/game-lighting-history/candidate-04-1.json',manifest.tts.reference,manifest.tts.referenceText];
for(const p of protectedPaths)if(!fs.existsSync(path.join(root,p)))throw Error('Missing protected '+p);
write(req,{schemaVersion:1,slug:'game-lighting-history-04',duplicateCandidate:'game-lighting-history-04-1',preparedAt:stamp,scriptReview:review,manifestOverride:mf,protectedInputs:[...new Set(protectedPaths)].map(path=>({path,sha256:sha(path)})),scenes:scenes.map(x=>({id:x.id,path:audioDir+'/chunks/'+x.id+'-scene.wav'})),cpuThreads:2,gpuJobs:1,batchSize:1,wholeAsrRequired:true,independentContextsRequired:true,original111Regenerated:false,researchRestoreRequired:true});
console.log(JSON.stringify({scenes:scenes.length,actual:scenes.filter(x=>x.role==='actual').length,sourceCapacitySeconds:record.nativeSourceCapacitySeconds,koCharacters:record.koCharacters,newTtsStarted:false,measuredRatioApproved:false}));
