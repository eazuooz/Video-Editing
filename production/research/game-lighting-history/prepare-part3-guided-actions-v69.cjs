// New narration only. Retained111 paragraphs and five framing takes are immutable.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const b='projects/game-lighting-history-04/production',s='projects/game-lighting-history-04/script';
const out=s+'/physical-part3-guided-actions.koen.v69.json';
if(fs.existsSync(out))throw Error('Preserve reviewed preparation');
const contextPath='production/research/game-lighting-history/local/guided-context-v70/execution.json',context=read(contextPath);
if(context.status!=='context-samples-ready'||context.boards.length!==6||context.samples.length!==21)throw Error('Completed context extraction required');
const contextReview=b+'/guided-source-context-direct-review-v70.json';
if(fs.existsSync(contextReview)&&read(contextReview).extraction.sha256!==sha(contextPath))throw Error('Preserve changed context review');
for(const p of [b+'/physical-framing-selected-execution-v55.json','shared/voice-reference/reference-15-35s.wav','shared/voice-reference/reference-15-35s.ko.txt',...context.boards.map(x=>x.path)])if(!fs.existsSync(p))throw Error('Missing prerequisite '+p);
if(!fs.existsSync(contextReview))fs.writeFileSync(contextReview,JSON.stringify({reviewedAt:new Date().toISOString(),extraction:{path:contextPath,sha256:sha(contextPath),actualExit:0},allSixBoardsDirectlyRead:true,boards:context.boards.map(x=>({...x,directlyRead:true})),observations:{capture:'8 capture controls;18 captured frame loaded;28 command list selected/unbound;38 ClearRenderTargetView blue;48 CloseCommandList black;58 EID14 DrawInstanced triangle;68 VS stage pipeline;78 mesh POSITION table;88/98 vertex shader input/output;108 triangle target. Explicit stage selection before retained pixel shader return.',postColor:'1927 Auto Exposure/camera;1935 GlobalPostProcess5 selects Post Process Blendable;1943 blend search;1953 Post Process Materials entry;1963 T_EpicLUT256x16 texture preview. LUT appears later than source window start, so narration corrected before TTS.',postFocus:'2465 return transient documentation/taskbar overlap;2480/2495 normal view BokehDOF FocalDistance1259.073364, NearTransition300, FarTransition2059.633057, Scale0.2, MaxBokeh8. 2510 play dropdown;2525 return. Do not claim continuously edited focus values; cut transient UI and static idle after dense motion review.'},sourceTextCorrectionsBeforeTts:true,originalPcmChanged:false,exactCutApproved:false,continuousMotionApproved:false,allFinalPixelsReviewed:false,newGitImages:0},null,2)+'\n');
cp.execFileSync(process.execPath,['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],{stdio:'inherit'});
const sources={
 re:{id:'MhLWH18vXH4',game:'Resident Evil Requiem',path:'production/research/game-lighting-history/local/cross-game-comparisons-v51/resident-evil-requiem-dlss5-preview.mp4',review:b+'/cross-game-source-direct-review-v52.json'},
 star:{id:'-vMVlfxUDe4',game:'Starfield',path:'production/research/game-lighting-history/local/cross-game-comparisons-v51/starfield-dlss5-preview.mp4',review:b+'/cross-game-source-direct-review-v52.json'},
 hog:{id:'t50AdVMuxZE',game:'Hogwarts Legacy',path:'production/research/game-lighting-history/local/cross-game-comparisons-v51/hogwarts-legacy-dlss5-preview.mp4',review:b+'/cross-game-source-direct-review-v52.json'},
 nba:{id:'LHUzFnq70b8',game:'NBA 2K27',path:'production/research/game-lighting-history/local/nba2k27-dlss5-official-2026.mp4',review:'production/research/game-lighting-history/local/nba2k27-dlss5-acquisition-native-review-v1.json'},
 post:{id:'DFT7hFz_DpE',path:'production/research/game-lighting-history/local/epic-post-processing.mp4',review:b+'/native-process-review-v4.json'},
 capture:{id:'eiT2GlSeSeU',path:'production/research/game-lighting-history/local/episode04-native-v1/own-renderdoc-capture.mp4',review:b+'/renderdoc-native-direct-review-v38.json'},
 resource:{id:'inGlMVhYB1s',path:'production/research/game-lighting-history/local/episode04-additional-action-v47/virtual-texture-editor-goldcoast2024.mp4',review:b+'/additional-action-direct-review-v48.json'}
};
for(const v of Object.values(sources)){v.sha256=sha(v.path);v.reviewSha256=sha(v.review);v.sourceAudio=false;v.loop=false;v.slowdown=false;v.rightsApprovedForPublicUse=false;}
if(sources.nba.sha256!=='102800354e8af924023cca9a8df7fb8a08903e77e7c1bd1826ea4e556cf80a9a')throw Error('Complete alternative NBA source required');
const scenes=[];
function add(id,role,source,ranges,after,ko,en,focus){scenes.push({id,role,source,ranges,insertAfter:after,ko,en,focus,sourceTimeIsNativeFileSeconds:true,annotationPolicy:'Red marks observed surface/control; teal connects roles. Track camera/object, preserve original condition labels, UI and bottom captions. An illustrative calculation is explicitly labelled, not measured game-world data.',normalSpeed:true,exactCutAndMovingPixelsApproved:false});}
add('appearance-prerequisite','explanation',null,[],'original-22-4',
'같은 역할을 서로 다른 게임에서 비교해 보죠. 앞의 세 영상은 이천이십육년 삼월의 디엘에스에스 오 미리보기입니다. 끄기와 켜기 표시를 먼저 읽고, 얼굴과 옷에 입혀진 빛을 보겠습니다. 구월의 농구 게임 출시 사례는 이 미리보기와 따로 구분하죠.',
'Compare the same responsibility across different games. The first three sources are March2026 DLSS5 previews. Read Off and On first, then examine the light on faces and clothing. The September basketball release is a separate example.',
'Projected base image → appearance result, with separate March preview and September release date labels. No simulated extra frames.');
add('appearance-resident','actual','re',[[5.5,10.5],[11.5,15],[16,23.5]],'appearance-prerequisite',
'먼저 레지던트 이블입니다. 어두운 실내에서 빗속의 차 옆으로 바뀌죠. 고개를 돌리는 인물의 얼굴과 젖은 옷을 보세요. 원본의 켜짐 표시와 함께 표면 표현이 달라집니다. 자세가 다른 두 순간을 같은 픽셀의 정답으로 비교하지는 않겠습니다.',
'Start with Resident Evil, moving from a dark room to the rainy vehicle shot. Watch the turning face and wet clothing. The labelled On condition changes their surface appearance. Different poses are not a pixel-aligned ground truth.',
'Announce each shot change; track face and shoulder highlights, retaining the source wipe/condition.');
add('appearance-starfield','actual','star',[[5.5,9.5],[10,14],[14.5,18],[19,21.5]],'appearance-resident',
'스타필드에서는 밝은 실내의 주황색 외투와 우주복을 보겠습니다. 대화창은 상대를 알려 주는 인터페이스이지 화질 점수가 아닙니다. 앞의 빗속과 조명 조건은 달라도, 질문은 같습니다. 피부와 천에 입혀진 최종 빛의 표현이 어디서 달라질까요?',
'Starfield provides an orange coat and suits in brighter interiors. The dialogue UI identifies a character; it is not a quality score. Lighting differs from the rainy scene, but the question remains: where does the final appearance of light on skin and fabric change?',
'Reset tracked markers at each cut. Retain Marika Boros/skill UI, then announce the crew and subsequent dialogue views.');
add('appearance-hogwarts','actual','hog',[[6,9.5],[10,12.5],[13.5,18],[19.5,23.5]],'appearance-starfield',
'호그와트 레거시는 실내에서 거리와 지하로 옮겨 갑니다. 장면이 바뀔 때마다 새 인물의 얼굴과 옷을 잡으세요. 같은 장면의 끄기와 켜기를 비교해야 합니다. 빛나는 지팡이나 증기가 함께 보이더라도, 그것만으로 새로운 물리 계산이 증명되지는 않습니다.',
'Hogwarts Legacy moves through an interior, a street and an underground shot. At each cut, select the new face and clothing. Compare Off and On within that shot. A glowing wand or visible steam alone does not establish new physical simulation.',
'Narrate scene changes; distinguish the observed cloth/skin from wand/steam. No marker carried across a cut.');
add('appearance-nba','actual','nba',[[13,24.8],[27,39],[40,49]],'appearance-hogwarts',
'이번에는 농구 코트입니다. 선수의 피부와 유니폼, 팔이 올라갈 때의 밝은 부분을 따라가세요. 디트로이트 이 번 선수의 가까운 장면에서는 끄기에서 켜기로 표시가 바뀝니다. 다른 각도의 덩크 장면은 따로 보죠. 최종 화면 표현을 비교하는 것이며, 공의 물리 계산이나 입력 반응이 바뀌었다는 실험은 아닙니다. 앞의 어두운 옷, 밝은 외투, 지하의 천과 비교하면 같은 표시 처리도 서로 다른 표면 조건을 만난다는 점이 보입니다.',
'Now examine skin, jerseys and arm highlights on the basketball court. The close Detroit number-two shot changes from Off to On; subsequent dunks use other camera angles. This compares displayed appearance, not ball physics or input response. Compare those surfaces with dark wet clothing, a bright coat and underground fabric: the same display-stage task meets different surface conditions.',
'Same-shot closeup OFF at19.5–21 / ON21.5–22.5; reset at the later dunk cuts. Track arm/jersey, keep ball/hands and original condition labels clear. Exact transition boundary remains a final cut check.');
add('appearance-to-controls','explanation',null,[],'appearance-nba',
'네 게임의 차이를 최종 화면의 표면 표현으로 비교했습니다. 이제 원인을 직접 조절해 보죠. 조명을 옮기지 않고도 노출과 초점 설정만으로 화면은 바뀔 수 있습니다. 먼저 편집기에서 설정과 결과를 연결하고, 그다음 프레임 안의 실제 자료를 검사하겠습니다.',
'We compared surface appearance across four games. Next, control a cause directly: exposure and focus can change the image without moving lights. Connect editor settings to results, then inspect the actual resources inside a frame.',
'Four projected surfaces converge on exposure/focus controls, then a producer→resource→consumer chain.');
add('exposure-context','actual','post',[[1570,1586]],'original-22p-2',
'이것은 이천십칠년 언리얼 엔진 편집기 시연입니다. 화면의 상자 배치와 오른쪽 포스트 프로세스 설정을 먼저 구별하세요. 시연자는 카메라와 설정을 함께 움직입니다. 따라서 두 화면의 밝기 차이를 기능 하나의 효과로 곧바로 계산하지 않고, 어떤 입력을 만지는지부터 따라가겠습니다.',
'This is a2017 Unreal editor demonstration. Separate the cube arrangement from the post-process controls on the right. Camera and parameters both change, so we first identify the edited inputs rather than attributing every brightness difference to one feature.',
'Red outline around post-process control, teal around the viewport reference object. Explicit2017/UE4 label.');
add('exposure-after-limit','actual','post',[[1602.88,1618]],'21-guide-post-exposure',
'노출 설정에는 밝기의 아래쪽과 위쪽 제한, 그리고 바이어스가 보입니다. 숫자의 이름을 읽는 것과 화면의 픽셀 밝기를 재는 것은 다르죠. 상자의 밝은 면과 어두운 면을 같은 관찰 대상으로 잡고, 값이 바뀔 때 전체 표현이 어떻게 따라오는지 확인하세요.',
'The exposure panel shows lower and upper brightness limits and a bias. Reading those settings differs from measuring displayed pixel intensity. Keep the same bright and dark cube faces in view while following the changes.',
'Track the same cube face across camera motion; label control values as source settings, not measured luminance.');
add('histogram-open','actual','post',[[1621,1644.5]],'exposure-after-limit',
'다음에는 히스토그램 시각화로 바뀝니다. 사진 전체를 그대로 보여 주는 대신, 밝기 분포를 읽을 자료를 더한 화면입니다. 아래 그래프와 오른쪽 설정을 연결해서 보세요. 여기서 보이는 초록색과 파란색은 실제 벽의 재질 색을 읽으라는 뜻이 아니라 시각화의 표시입니다.',
'The demonstration switches to histogram visualization. It adds information for reading a brightness distribution instead of showing only the ordinary image. Connect the lower graph to the controls. Its green and blue colors are visualization, not the wall material colors.',
'Name HDR Histogram visualization before colors. Red graph boundary, teal control pointer, never cover its legend.');
add('histogram-log-scale','actual','post',[[1644.5,1668]],'histogram-open',
'시각화 이름에 로그 스케일이 적혀 있습니다. 같은 가로 간격이 밝기 하나의 같은 차이를 뜻한다고 읽으면 안 됩니다. 어두운 값부터 밝은 값까지 넓은 범위를 한 화면에 펼쳐 놓는 방식이죠. 먼저 눈금의 뜻을 확인해야 그래프의 위치 변화와 실제 밝기의 변화를 연결할 수 있습니다.',
'The visualization explicitly names a logarithmic scale. Equal horizontal spacing does not mean an equal additive brightness change. It displays a wide dark-to-bright range in one view. Read the scale before relating graph position to brightness.',
'Highlight the source logarithmic label and its tick sequence; do not invent histogram counts or units.');
add('histogram-camera-condition','actual','post',[[1668,1691.5]],'histogram-log-scale',
'카메라가 움직이면 화면 안에 들어오는 면의 비율도 달라집니다. 같은 조명 장면이어도 밝은 상자를 더 많이 보면 밝기 분포가 달라질 수 있죠. 그래서 노출 비교의 기록에는 설정값뿐 아니라 카메라 구도도 필요합니다. 지금은 그 연결을 관찰하는 시연이며, 고정 카메라의 수치 실험은 아닙니다.',
'Camera movement changes the proportions of surfaces in the image. Seeing more bright cubes can change the brightness distribution within the same lit scene. Exposure comparisons therefore need camera framing as well as settings. This is an observation demonstration, not a fixed-camera numerical experiment.',
'Track visible cube proportions. Keep camera motion visible; no split-screen claim of matched frames.');
add('histogram-control-result','actual','post',[[1691.5,1715]],'histogram-camera-condition',
'이제 설정, 시각화, 최종 화면이라는 세 가지 역할을 나누어 읽을 수 있습니다. 설정은 바꾸는 입력이고, 그래프는 관찰을 돕는 자료입니다. 우리가 보는 화면은 뒤의 표시 처리까지 거친 결과죠. 그래프 한 장의 색을 그대로 최종 픽셀의 색이라고 생각하지 않는 것이 다음 비교의 출발점입니다.',
'We can now separate three roles: edited settings, diagnostic visualization and the final image. Settings are inputs; the graph helps inspection; the displayed image includes later display processing. A diagnostic graph color is not itself a final surface pixel color.',
'Three small role labels anchored to their actual areas; action remains dominant, no frozen slide replacement.');
add('bloom-surface','actual','post',[[1735,1755]],'original-22p-3',
'블룸 조절 화면입니다. 밝은 영역 둘레의 번짐과 상자 표면의 밝기를 따로 보세요. 번짐이 넓어지는 표현과 다른 면에 빛이 반사되어 도달하는 계산은 서로 다른 질문입니다. 광원 옆이 반짝인다는 인상만으로 간접광 구현을 확정하지 않고, 지금 편집기가 바꾸는 효과의 역할을 확인합니다.',
'In the bloom controls, distinguish spread around bright regions from the cube surfaces themselves. A wider glow and light bouncing onto another surface answer different questions. Inspect the edited effect rather than treating a bright impression as proof of an indirect-lighting implementation.',
'Red marks observed bright-edge spread; teal names display effect. No light-ray annotation presented as captured transport.');
add('tone-range','actual','post',[[1783,1806.333333]],'bloom-surface',
'이제 색과 톤 관련 설정으로 넘어갑니다. 상자는 그대로 남아 있는데 화면의 표현은 조절할 수 있죠. 앞에서는 장면의 빛을 만드는 방법을 배웠고, 지금은 그 결과를 보여 줄 범위로 옮기는 단계를 보고 있습니다. 입력을 계산하는 단계와 표시를 다듬는 단계를 구별해서 따라가세요.',
'Next come color and tone controls. The cubes remain while their displayed appearance can be adjusted. Earlier chapters created scene lighting; this stage maps its result into a display range. Distinguish computing the input from shaping its presentation.',
'Announce the change of stage. Track unchanged cube arrangement and current color/tone panel.');
add('tone-highlight-reference','actual','post',[[1806.333333,1829.666667]],'tone-range',
'같은 상자에서 밝은 면과 그늘진 면을 함께 기준으로 잡겠습니다. 밝은 부분만 보면 대비의 변화를 놓칠 수 있고, 어두운 부분만 보면 밝은 값이 눌리는 정도를 놓칠 수 있습니다. 시연의 조절값과 두 영역을 같이 보면서, 전체가 달라진 것인지 특정 밝기 범위가 달라진 것인지 구분해 보세요.',
'Use both a bright face and a shaded face on the same cube. Looking only at highlights can miss contrast changes; looking only at shadows can miss highlight compression. Follow the control and both regions to distinguish overall changes from changes concentrated in a brightness range.',
'Two tracked observed regions with bright/shaded labels. Never invent numeric pixel values.');
add('tone-material-distinction','actual','post',[[1829.666667,1853]],'tone-highlight-reference',
'표면이 더 진하게 보인다고 원래 재질 파일을 바꿨다고 단정할 수는 없습니다. 여기서는 후처리 조절과 결과의 연결을 관찰합니다. 재질 입력의 변경을 주장하려면 그 입력을 따로 확인해야 하죠. 같은 화면 변화라도 어느 단계에서 바뀌었는지에 따라 원인 설명은 달라집니다.',
'A darker-looking surface does not by itself establish that its material asset changed. Here we observe post-process controls and their results. A claim about material inputs requires inspecting those inputs separately. Similar image changes can originate at different stages.',
'Role pointer from actual post-process panel to viewport, explicitly observation rather than implementation proof.');
add('grade-channel-controls','actual','post',[[1855,1873.666667]],'tone-material-distinction',
'색 조절에서는 밝기와 색의 균형을 따로 읽어야 합니다. 같은 상자 배열을 두고 어떤 조절 항목을 선택하는지 보세요. 화면이 더 따뜻하거나 차갑게 느껴지는 결과와, 광원의 실제 색을 바꾼 결과는 같아 보일 수 있어도 같은 작업이라고 말할 수는 없습니다.',
'Read brightness and color balance as separate aspects of grading. Keep the cube arrangement as a reference and identify the chosen control. A warmer or cooler appearance can resemble a changed light color without establishing the same underlying operation.',
'Show active selected grading control, then observed surface appearance; no claim that a light object was edited.');
add('grade-shared-reference','actual','post',[[1873.666667,1892.333333]],'grade-channel-controls',
'비교할 면을 바꾸지 않는 이유는 변화의 기준을 유지하기 위해서입니다. 화면의 한쪽 면을 빨간 표시로 따라가고, 설정 이름은 다른 색으로 구별하겠습니다. 표시가 가리키는 것은 관찰 위치이며, 게임 안의 거리나 물리 단위가 아닙니다. 카메라가 바뀌면 같은 면을 다시 잡아야 합니다.',
'Keeping the same surface preserves a reference for comparison. Red follows the observed face; another color identifies the setting. The mark is an observation location, not a game-world distance or physical unit. Reacquire the surface when the camera changes.',
'Narration-timed tracked red region and teal setting label; reset at camera discontinuities.');
add('grade-to-lookup','actual','post',[[1892.333333,1911]],'grade-shared-reference',
'앞의 조절을 한 화면의 인상으로만 끝내지 말고, 입력과 표시 결과의 관계로 적어 보세요. 무엇을 바꿨는지, 어느 면에서 차이가 보였는지, 어떤 조건이 함께 달라졌는지입니다. 다음에는 색 변환을 다른 자료로 지정하는 화면을 보며, 최종 색이 원래 조명값과 곧바로 같지는 않다는 점을 이어가겠습니다.',
'Record the edited input, the surface where a change appears and any simultaneous condition changes. Next we examine a separate color-transform resource, continuing the distinction between final displayed color and the original lighting value.',
'Guide labels attached to control/resource/viewport; announce the next resource rather than a generic cut.');
add('lookup-resource','actual','post',[[1927,1948]],'grade-to-lookup',
'먼저 색 변환을 적용할 설정을 찾습니다. 시연자는 여러 상자 배치 중 포스트 프로세스 블렌더블이라고 적힌 구역을 선택하고, 오른쪽 검색칸에 블렌드를 입력합니다. 화면의 상자와 그 상자에 적용할 효과 설정은 다른 역할입니다. 다음 자료가 어디에 연결될지부터 확인해 보죠.',
'First locate the setting that will apply the color transform. The demonstrator selects the area labelled Post Process Blendable and searches for blend in the right panel. The scene cubes and the effect settings have separate roles. Establish where the next resource will be connected.',
'1927 exposure panel/camera →1935 GlobalPostProcess5 selection →1943 blend search. Do not show a LUT label before its later preview.');
add('lookup-endpoint','actual','post',[[1948,1969]],'lookup-resource',
'오른쪽에는 포스트 프로세스 재질 항목이 보이고, 이어서 색띠 모양의 룩업 테이블 자료를 엽니다. 줄여서 엘유티라고 부르죠. 색의 대응 관계를 담은 자료이지 게임 세계의 작은 지도는 아닙니다. 색을 다루는 자료를 확인했으니, 다음에는 같은 상자 배치에서 거리와 초점의 역할을 구분하겠습니다.',
'The panel shows a post-process material entry, followed by a lookup-table asset displayed as a strip of colors, or LUT. It represents color correspondence rather than a small map of the game world. After identifying the color resource, distinguish distance and focus in the same cube arrangement.',
'1953 Post Process Materials→1963 T_EpicLUT256x16 asset preview. Do not claim a demonstrated parameter/result change where none is visible.');
add('focus-legend-context','actual','post',[[2325,2330],[2336.02,2353]],'original-22p-4',
'초점 시각화에서는 먼저 범례를 읽습니다. 파란색은 먼 영역, 초록색은 가까운 영역, 검정은 초점 영역을 가리킵니다. 이 색은 상자의 원래 색이 아닙니다. 오른쪽의 거리와 전이 설정을 만질 때 색 영역이 달라지는 위치를 보며, 무엇이 초점 기준이고 무엇이 경계의 폭인지 나누겠습니다.',
'Read the focus legend first: blue marks far regions, green near regions and black the focused region. These are not cube material colors. As distance and transition settings are edited, distinguish the focus reference from the width of its transition.',
'Preserve debug legend and label its exact semantic colors; prior2330–2336.02 source interval remains reserved for the original guide.');
add('focus-distance-transition','actual','post',[[2353,2369]],'focus-legend-context',
'초점 거리와 흐림으로 넘어가는 전이 폭은 같은 숫자가 아닙니다. 하나는 기준 위치를 잡고, 다른 하나는 그 주변의 변화 범위와 연결됩니다. 조절 항목의 이름을 읽은 뒤 화면의 어느 영역이 바뀌는지 확인하세요. 서로 다른 시점의 설정을 같은 조건의 켜기와 끄기로 붙이지 않겠습니다.',
'Focus distance and transition width are not the same quantity. One establishes a reference location; the other relates to the surrounding change range. Read the edited field before inspecting the affected regions, without pairing different settings as an identical-condition On/Off comparison.',
'Active field/affected region pointers; exact field/value boundaries require native dense cut review.');
add('focus-normal-return','actual','post',[[2380.1,2396]],'22-guide-post-focus',
'일반 화면으로 돌아오면 같은 상자의 가까운 면이 흐려 보입니다. 디버그 색과 일반 색을 곧바로 겹쳐 읽지 말고, 두 화면이 어떤 역할인지 구분하세요. 이 시연에서는 카메라와 초점 관련 값도 변합니다. 보이는 흐림을 설명할 때 그 조건을 함께 적어야 합니다.',
'Back in the ordinary view, a nearer cube appears blurred. Separate diagnostic colors from ordinary scene colors. Camera and focus-related settings also change in this demonstration, so record those conditions when explaining the blur.',
'Track the near white cube and the active blur setting, never claim identical debug/normal conditions.');
add('focus-error-isolation','actual','post',[[2396,2411]],'focus-normal-return',
'반사 복원을 비교하는 화면에 이런 초점 효과가 켜져 있으면, 번진 가장자리의 원인을 잘못 찾기 쉽습니다. 먼저 초점과 카메라 조건을 확인하고, 그다음 복원 기능의 조건을 비교해야 합니다. 보이는 결과를 단계별로 나누면 비슷한 흐림도 서로 다른 원인으로 설명할 수 있습니다.',
'When focus effects are enabled during reconstruction comparisons, a blurred edge can be misattributed. Check focus and camera conditions first, then the reconstruction conditions. Separating stages lets similar-looking blur be explained by different causes.',
'Source focus controls remain visible; role labels distinguish focus blur from reconstruction as an explanatory comparison.');
add('focus-later-settings','actual','post',[[2465,2489.333333]],'focus-error-isolation',
'뒤의 편집기 구간에서도 같은 상자 배치가 기준입니다. 조절창에서 선택한 항목과 가까운 면, 먼 면을 번갈아 보세요. 화면 전체의 흐림 정도만 기억하면 어떤 거리 영역이 달라졌는지 놓칠 수 있습니다. 초점 기준과 앞뒤 영역을 나누면 변화가 일어난 위치를 더 구체적으로 설명할 수 있습니다.',
'The later editor interval retains the cube arrangement as a reference. Follow the selected control and compare near and far surfaces. An overall impression of blur can hide which distance region changed. Separating the focus reference and its surrounding regions makes the observation more specific.',
'Only fields actually visible in each native shot receive labels. Track near/far surfaces independently.');
add('focus-observation-protocol','actual','post',[[2489.333333,2513.666667]],'focus-later-settings',
'시연을 다시 볼 때에는 먼저 입력 이름을 읽고, 그 값이 바뀌는 순간을 찾고, 마지막으로 영향을 받은 면을 보세요. 카메라가 함께 움직이면 그 변화도 별도로 기록합니다. 이렇게 원인 후보를 나누는 방법은 다른 엔진의 후처리 비교에서도 쓸 수 있지만, 모든 엔진의 내부 순서가 같다는 뜻은 아닙니다.',
'Read the input name, locate its change, then inspect the affected surface. Record camera changes separately. This observation method transfers to other engines without assuming their internal post-process order is identical.',
'Narration reveals input→change→observed surface labels in order, anchored to actual moving UI/view.');
add('focus-to-frame-inspection','actual','post',[[2513.666667,2538]],'focus-observation-protocol',
'지금까지 네 게임의 최종 표현과 편집기의 노출, 색, 초점을 비교했습니다. 화면에서 변화를 보는 방법은 생겼지만, 어느 명령이 어떤 자료를 읽었는지는 아직 별도의 질문입니다. 다음 프레임 검사에서는 기능의 이름보다 실제 입력과 출력의 연결을 찾아보겠습니다.',
'We compared final appearance in four games with editor exposure, color and focus controls. We can observe changes, but identifying which command read which resource is another question. Frame inspection now follows actual inputs and outputs rather than relying on feature names.',
'Keep active editor operation visible; announce inspection and retain the original22r paragraphs after this insertion.');
add('capture-context','actual','capture',[[8,26]],'original-22r-1',
'이번 자료는 우리 채널의 간단한 다이렉트 엑스 십이 시연입니다. 복잡한 게임의 조명 구현을 증명하려는 장면은 아닙니다. 프레임 검사 창과 이벤트 목록을 구별하고, 선택한 작업에 따라 다른 자료가 열리는 순서를 보세요. 화면의 모양과 그 모양을 만든 명령을 연결하는 연습입니다.',
'This is our channel’s simple DirectX12 demonstration, not evidence of a complex game lighting implementation. Separate the frame inspection window from its event list and follow how selecting an operation exposes different data. We connect a visible shape with the command that produced it.',
'Label event list and resource view only when visible. Real editor/debugger source, no simulated test counted as game coverage.');
add('capture-event-purpose','actual','capture',[[26,48]],'original-22r-2',
'이벤트 목록의 이름은 무엇을 검사할지 고르는 단서입니다. 화면을 비우는 명령과 삼각형을 그리는 명령을 같은 역할로 읽으면 안 됩니다. 어떤 결과를 묻는지 먼저 정하고, 그 결과를 만든 작업을 선택하세요. 목록에 항목이 있다는 사실만으로 그 작업이 모든 픽셀에 영향을 주었다고 단정하지 않겠습니다.',
'Event names guide inspection. Clearing an image and drawing a triangle have different roles. Start with the result being investigated, then select its producing operation. An item appearing in a list does not establish that it affected every pixel.',
'Red around selected event; teal marks clear/draw role, with no false Pixel History draw attribution.');
add('capture-target-view','actual','capture',[[48,64]],'original-22r-4',
'이제 드로 인스턴스드 명령을 선택하면 파란 배경 위에 색이 섞인 삼각형이 나타납니다. 목록의 화면 지우기 명령과 다른 역할이죠. 먼저 어떤 명령 뒤의 출력을 보고 있는지 확인하고, 그다음 메시의 꼭짓점과 셰이더 입력으로 넘어가겠습니다. 결과 그림에서 입력 자료로 질문을 옮기는 순서입니다.',
'Selecting DrawInstanced exposes a colored triangle on the blue background, unlike the clear operation. Identify the selected command’s output first, then move to mesh vertices and shader inputs. The investigation moves from the output image to its input data.',
'48 CloseCommandList can show black;58 selectedEID14 DrawInstanced shows triangle. Name event before the image; mesh data is introduced only in the next range.');
add('capture-position-input','actual','capture',[[67,91]],'23-pre-capture-dataflow',
'메시와 입력을 보는 창에서는 위치와 색을 구분합니다. 위치 숫자는 삼각형의 모양과 연결되고, 색 입력은 뒤의 표현과 연결될 수 있습니다. 화면에 보이는 색 표만 보고 모든 조명값을 안다고 할 수는 없죠. 선택한 명령과 셰이더의 입력 이름이 서로 맞는지 확인하는 것이 먼저입니다.',
'Separate position from color in the mesh and input views. Positions relate to triangle shape, while color inputs can affect appearance. A color table does not reveal every lighting quantity. First match the selected command to its shader input names.',
'Distinct labelled position/color regions; source shader stage must be named before a return-value arrow.');
add('capture-stage-selection','actual','capture',[[91,109.52]],'capture-position-input',
'셰이더 단계가 바뀌면 같은 반환이라는 말도 다른 일을 가리킵니다. 꼭짓점 셰이더의 반환을 픽셀 셰이더의 최종 색으로 설명하지 않겠습니다. 지금 선택한 단계와 입력을 읽고, 다음에 남겨 둔 색 반환 시연으로 연결하세요. 자료의 이름과 만든 작업을 함께 기록해야 화면의 인상보다 구체적인 근거가 됩니다.',
'A return value means different things at different shader stages. Do not describe a vertex-shader return as the pixel shader’s final color. Read the selected stage and input, then connect to the retained color-return demonstration. Resource names and producing operations provide more concrete evidence than appearance alone.',
'No numeric final-return claim before stepping. Retained109.52–125 and earlier125–132.5 source ranges are reserved.');
add('resource-viewer-context','actual','resource',[[862,884]],'original-22r-7',
'이번에는 언리얼 엔진의 자원 보기 창으로 바뀝니다. 여러 자료의 이름이 함께 나타나지만 모두 같은 텍스처는 아닙니다. 그림자 페이지 풀과 가상 텍스처의 물리 풀을 구분해서 읽으세요. 앞 편에서 페이지가 나뉘는 방식을 배웠다면, 이제 실제 창에서 그 자료를 어떻게 찾아보는지 연결할 수 있습니다.',
'Switch to Unreal’s resource viewer. Several names appear, but they do not all describe the same texture. Distinguish a shadow-page pool from a virtual-texture physical pool. The earlier page discussion now connects to locating actual resources in the viewer.',
'Actual labels ShadowVirtualPhysicalPagePool and VirtualPhysicalTexture receive distinct role colors. Source native offset350 retained.');
add('resource-name-limits','actual','resource',[[884,906]],'resource-viewer-context',
'자료 이름을 찾았으면 다음에는 크기와 쓰임을 확인해야 합니다. 루멘의 방사휘도 자료와 그림자 자료를 한 덩어리의 빛이라고 뭉뚱그리지 마세요. 이름은 좋은 출발점이지만 어떤 작업이 만들고 어떤 작업이 읽는지까지 확인해야 연결이 완성됩니다. 이 창만으로 전체 프레임의 모든 의존 관계를 검증한 것은 아닙니다.',
'After locating a name, inspect dimensions and usage. Lumen radiance data and shadow data should not be collapsed into one generic light resource. Names start the investigation; producers and consumers complete it. This viewer alone does not verify every dependency in the frame.',
'Name LumenSceneRadiance only on its actual entry; no arrows asserted as captured dependencies.');
add('resource-upload-control','actual','resource',[[906,928]],'original-22rb-4',
'다음 조절은 가상 텍스처 자료의 업로드와 관련된 것입니다. 설정 이름의 프레임이라는 단어를 보고 프레임 생성 기능이라고 혼동하면 안 됩니다. 여기서 다루는 자료가 무엇인지 먼저 구별하고, 설정과 화면 반응을 보세요. 같은 성능 관련 숫자라도 어느 작업의 예산인지에 따라 뜻이 달라집니다.',
'The next control concerns virtual-texture uploads. The word frame in its name does not make it frame generation. Identify the data being handled before relating the setting to the visible response. Performance-related numbers mean different things depending on which task receives the budget.',
'Actual r.VT.MaxUploadsPerFrame_Streaming label. Highlight VT/upload role, never DLSS Frame Generation.');
add('resource-budget-to-measure','actual','resource',[[928,950]],'resource-upload-control',
'자료를 얼마나 빨리 올릴지와 한 프레임을 얼마나 빨리 그릴지는 같은 측정이 아닙니다. 캐시와 로딩 상태, 카메라 구간도 함께 기록해야 비교할 수 있죠. 실제 자원을 읽는 법까지 연결했으니, 뒤의 성능 설명에서는 한 순간의 숫자 대신 조건과 반복 측정을 기준으로 삼겠습니다.',
'How quickly resources upload and how quickly a frame renders are different measurements. Record cache, loading and camera conditions. Having connected the resource view to its controls, the retained performance discussion now uses conditions and repeated measurements rather than one instantaneous number.',
'Maintain actual upload-control interaction. No benchmark claim without repeated timing evidence.');
const reviewFiles=[b+'/cross-game-source-direct-review-v52.json',b+'/native-process-review-v4.json',b+'/postprocess-native-direct-review-v34.json',b+'/renderdoc-native-direct-review-v38.json',b+'/additional-action-direct-review-v48.json',b+'/guided-source-context-direct-review-v70.json'];
const boundary='production/research/game-lighting-history/local/nba-boundary-v67/execution.json',nb=read(boundary);
if(nb.status!=='selection-samples-ready'||nb.boards.length!==3||nb.samples.length!==12)throw Error('Completed NBA selection samples required');
const boundaryReview={recordedAt:new Date().toISOString(),execution:{path:boundary,sha256:sha(boundary)},allThreeBoardsDirectlyRead:true,boards:nb.boards.map(x=>({...x,directlyRead:true})),observed:'19s rear Detroit2 ON; cut by19.5s to close Detroit2 OFF,20/20.5/21 OFF;21.5/22/22.5 same close shot ON;23 rear dunk ON;24/24.5 front celebration ON. Close shot changes pose continuously. Original condition label is preserved. Earlier summary jersey3 corrected to directly visible2.',publicLiveSamples:[{seconds:20,condition:'OFF',rate:1,jersey:'Detroit2'},{seconds:26.640141,condition:'ON',rate:1,jersey:'Cleveland Harden1',differentShot:true}],oldPartialSource:'79D8SVjB3HQ stays unused; no partial MP4 accepted',sourceSha256:sources.nba.sha256,exactEveryFrameBoundaryApproved:false,continuousFinalMotionApproved:false,fourGameCoverageApproved:false,newGitImages:0};
const boundaryOut=b+'/nba-source-selection-direct-review-v69.json';if(fs.existsSync(boundaryOut))throw Error('Preserve source review');fs.writeFileSync(boundaryOut,JSON.stringify(boundaryReview,null,2)+'\n');reviewFiles.push(boundaryOut);
const record={schemaVersion:1,preparedAt:new Date().toISOString(),physicalPart:'game-lighting-history-04-3',status:'source-informed paired additions; exact allocation after measured PCM',sources,scenes,sourceReviews:reviewFiles.map(path=>({path,sha256:sha(path)})),preservedOriginalParagraphs:111,preservedFramingScenes:5,regenerateOriginalPcm:false,style:'research-black-v1',fixedCaption:{style:'boxed-white-forest-v1',center:[960,970],fontSize:48,maxLines:2},causalChain:'Retained DLSS roles → four labelled surface comparisons → exposure/histogram → tone/color resource → focus → actual command/resource/stage inspection → virtual-resource budget → retained performance/conclusion',voiceApproved:false,currentMixedAsrApproved:false,allFinalPixelsReviewed:false,fourGamesFullyTaughtAndReviewed:false,measuredBody60to40Approved:false,uploaded:false,avoidIdleQuota:true,nativeSourceCapacitySeconds:scenes.filter(x=>x.role==='actual').reduce((n,x)=>n+x.ranges.reduce((v,r)=>v+r[1]-r[0],0),0),koCharacters:scenes.reduce((n,x)=>n+x.ko.length,0)};
fs.writeFileSync(out,JSON.stringify(record,null,2)+'\n');
for(const language of ['ko','en'])fs.writeFileSync(s+`/physical-part3-guided-actions.${language}.v69.json`,JSON.stringify({title:language==='ko'?'최종 화면의 원인을 확인하는 네 게임과 편집기 시연':'Four games and editor controls for reading the final image',scenes:scenes.map(x=>({id:x.id,title:x.id,lines:[x[language]],screenRole:x.role}))},null,2)+'\n');
const manifest=read('projects/game-lighting-history-04/project.json');
const audioDir='shared/output/narration/game-lighting-history-04/qwen3-1.7b-part3-guided-actions-v69',stem='game-lighting-history-04-part3-guided-actions-v69';
manifest.paths={...manifest.paths,script:s+'/physical-part3-guided-actions.ko.v69.json',scriptEn:s+'/physical-part3-guided-actions.en.v69.json',narration:audioDir+'/'+stem+'.wav',captionsKo:audioDir+'/'+stem+'.srt',captionsEn:audioDir+'/'+stem+'.en.srt'};
manifest.tts={...manifest.tts,outputDir:audioDir,filenameStem:stem,maxNewTokens:1536,maxRenderAttempts:3,maxNewTokensReason:'Only new independent guided paragraphs. Never regenerate original111 or five framing takes.'};manifest.editing={...manifest.editing,exampleSeconds:0};
const mf=b+'/part3-guided-actions-tts-manifest-v69.json',req=b+'/part3-guided-actions-tts-request-v69.json',review=b+'/part3-guided-actions-script-review-v69.json';
for(const p of [mf,req,review])if(fs.existsSync(p))throw Error('Preserve prepared TTS input');
fs.writeFileSync(mf,JSON.stringify(manifest,null,2)+'\n');
fs.writeFileSync(review,JSON.stringify({reviewedAt:new Date().toISOString(),fullPairedKoEnDirectlyCompared:true,sourceBeforeScript:true,retained111TextAndPcmPreserved:true,framingFivePreserved:true,causalOrderReviewed:true,scope:'Narration draft is bound to already directly sampled sources; exact dense motion, native in/out, traced annotations and measured screen roles remain separate gates. Do not count inventories as four-game approval or use idle footage for quota.',sourceSelectionCaveats:record.sources,scenes:scenes.map(x=>({id:x.id,ko:x.ko,en:x.en,insertAfter:x.insertAfter,role:x.role})),finalMixedAsrApproved:false,humanListeningApproved:false,pronunciationApproved:false,fourGamesFullyReviewed:false},null,2)+'\n');
const retained=b+'/additive-unmixed-review-assembly-v2.json',ret=read(retained);
const protectedPaths=['projects/game-lighting-history-04/project.json',out,manifest.paths.script,manifest.paths.scriptEn,mf,review,retained,ret.audio.path,b+'/physical-framing-selected-execution-v55.json',...reviewFiles,manifest.tts.reference,manifest.tts.referenceText];
fs.writeFileSync(req,JSON.stringify({schemaVersion:1,slug:'game-lighting-history-04',preparedAt:new Date().toISOString(),scriptReview:review,manifestOverride:mf,protectedInputs:[...new Set(protectedPaths)].map(path=>({path,sha256:sha(path)})),scenes:scenes.map(x=>({id:x.id,path:audioDir+'/chunks/'+x.id+'-scene.wav'})),cpuThreads:2,gpuJobs:1,batchSize:1,wholeAsrRequired:true,independentContextsRequired:true,original111Regenerated:false,researchRestoreRequired:true},null,2)+'\n');
console.log(JSON.stringify({scenes:scenes.length,actual:scenes.filter(x=>x.role==='actual').length,sourceCapacitySeconds:record.nativeSourceCapacitySeconds,koCharacters:record.koCharacters,newTtsStarted:false,measuredRatioApproved:false}));
