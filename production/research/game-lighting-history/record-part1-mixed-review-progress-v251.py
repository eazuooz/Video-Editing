"""Record only manually read current-mix results; never approve from similarity."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manual={
 'context-part1-conclusion':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete renderer-choice and part-conclusion paragraphs match through the full next-part transition. Every word timestamp read. No missing sentence, repetition, invented greeting or time reversal.',
  'recognitionVariants':['띄어쓰기: 조명 수, 투명 효과, 다음 편'],
  'independentContextRequired':False,'endingObserved':'다음 편은 그 예산 안에서 빛의 경로와 광원 표본을 고르는 문제로 이어집니다.','humanPronunciation':'pending'},
 'context-four-game-transfer-conclusion':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both full armor/surface and four-case transfer-conclusion paragraphs appear through the complete common-method ending. No omitted sentence, repetition, invented greeting or time reversal. The recognizer still maps initial 네 게임 to 내 게임, while later 네 경우 is correct; preserve this pronunciation uncertainty rather than claiming the initial syllable was resolved. A0.10s alignment overlap is retained.',
  'recognitionVariants':['네 게임 / 내 게임','띄어쓰기: 빛 자료'],
  'independentContextRequired':False,'humanPronunciationConcern':'Initial 네 게임/내 게임 recognizer distinction remains pending human listening; the complete four-role/common-principle sentences are present.',
  'endingObserved':'어떤 자료를 만들고 저장하며 다시 읽는지 묻는 방법은 네 경우에 모두 적용됩니다.','humanPronunciation':'pending'},
 'context-rivalry-surface-observation':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both full2014-history and armor/surface observation paragraphs match through the complete final motion connection. No news ending, repeated sentence or time reversal; the long independent history again resolves whole10. A0.26s and0.18s alignment overlap is documented without inventing repeated speech.',
  'recognitionVariants':['앞의 / 앞에','네 종 /4종','이천십사년 /2014년','띄어쓰기: 사례 수, 성능 순위'],
  'independentContextRequired':False,'resolvesWholeChunkArtifact':'whole-10','endingObserved':'앞에서 살펴본 화면 자료를 실제 움직임에 연결해 보세요.','humanPronunciation':'pending'},
 'context-rivalry-mobile-history':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete Fortnite wall/material and2014 engine-history paragraphs are present. 달라집니다 is complete without the zero-duration insertion, and the history paragraph has no invented news ending, repeated sentence or time reversal. Resolves both whole10 artifacts. Small0.12s and0.10s word overlaps are preserved as alignment evidence.',
  'recognitionVariants':['벽의 / 벽에','앞의 / 앞에','네 종 /4종','이천십사년 /2014년','띄어쓰기: 사례 수, 남겨 두고'],
  'independentContextRequired':False,'resolvesWholeChunkArtifact':'whole-10','endingObserved':'표현의 목표와 관찰 방법을 비교하는 데 쓰겠습니다.','humanPronunciation':'pending'},
 'context-fortnite-mobile-test':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete transfer/mobile-map paragraphs are present through the closing record-the-scene-and-measurement sentence. Quality labels, graph and surface comparison all match. No omitted sentence, repetition, invented greeting or time reversal.',
  'recognitionVariants':[],
  'independentContextRequired':False,'endingObserved':'어떤 장면에서 어떤 자료를 읽었는지 함께 남겨야 합니다.','humanPronunciation':'pending'},
 'context-mobile-compiler-availability':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete console-profile and missing-offline-compiler paragraphs are present including the blank-measurement caution and full closing sentence. No omission, repetition, invented greeting or time reversal. 셰이더/세이더 remains a pronunciation-review variant; a0.22s 경고/일부 alignment overlap does not repeat a sentence.',
  'recognitionVariants':['셰이더 / 세이더','띄어쓰기: 비어 있는, 안 됩니다'],
  'independentContextRequired':False,'endingObserved':'측정의 빈칸도 기록에 남기는 것이 정확한 검수입니다.','humanPronunciation':'pending'},
 'context-geometry-car-material':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete programmable-material and car-material paragraphs and final observation are present. No omitted sentence, repetition, invented greeting or time reversal. The 분기/붕기 and 뒤의/뒤에 recognition variants remain documented for human pronunciation review; no claim of actual mispronunciation. A0.18s 따라서 boundary overlap is alignment evidence.',
  'recognitionVariants':['분기 / 붕기','뒤의 / 뒤에','셰이딩 / 쉐이딩','띄어쓰기: 안 됩니다 / 안됩니다'],
  'independentContextRequired':False,'endingObserved':'모양과 재질 표현을 따로 읽어 보세요.','humanPronunciation':'pending'},
 'context-geometry-barrier-views':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete road-mask and wireframe/material comparison paragraphs appear with full endings. No invented goodbye or repeated/backward chunk; resolves the whole07 road-mask chunk artifact. Small0.14s word-alignment overlap at 있죠/시각화를 is preserved.',
  'recognitionVariants':['바뀌므로 / 바뀜으로','앞의 / 앞에'],
  'independentContextRequired':False,'resolvesWholeChunkArtifact':'whole-07','endingObserved':'새 색의 의미를 읽기 전에 같은 대상을 찾는 순서를 지키겠습니다.','humanPronunciation':'pending'},
 'context-cyber-surface-observation':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both full light-reconstruction and wet-floor/sign/umbrella observation paragraphs are present with the complete final motion-stability sentence. No omitted sentence, repetition, invented greeting or time reversal. A0.18s alignment overlap at 보입니다/켜진과 is retained.',
  'recognitionVariants':['바닥의 / 바닥에','켜짐과 꺼짐 / 켜진과 꺼진','표면의 / 표면에','앞의 / 앞에','디엘에스에스 삼 점 오 / DLSS3.5'],
  'independentContextRequired':False,'endingObserved':'이동 중에 세부가 얼마나 안정적으로 이어지는지가 관찰 대상입니다.','humanPronunciation':'pending'},
 'context-cyber-light-reconstruction':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete Cyberpunk comparison/conditions paragraphs are present including DLSS3.5, multiple-stage conditions, reflection/indirect-light separation and the final different-input distinction. No omission, repetition, invented greeting or time reversal.',
  'recognitionVariants':['앞의 / 앞에','디엘에스에스 삼 점 오 / DLSS3.5','띄어쓰기: 입력 자료'],
  'independentContextRequired':False,'endingObserved':'앞의 자수와는 입력 자료가 다릅니다.','humanPronunciation':'pending'},
 'context-outer-displayed-frames':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete comparison-role paragraphs appear through the final display-frequency distinction, but the initial 자수의 again loses 자 in this boundary-starting recognition. It does not resolve whole06. Require a complete preceding Horizon paragraph plus this transition and Outer paragraph, bound to current PCM, before approval.',
  'recognitionVariants':['자수의 / 수의','앞의 / 앞에','아우터 월드 / 아우터월드'],
  'independentContextRequired':True,'contextTarget':'outer-comparison-before','contextScope':'Complete preceding Horizon detail paragraph, the complete 자수의 transition and following Outer displayed-frame paragraph; preserve original PCM rather than inferring a true missing syllable from the two recognizer outputs.',
  'endingObserved':'이번 비교는 표시 빈도의 역할입니다.','humanPronunciation':'pending'},
 'context-horizon-detail-motion':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both full four-games transfer introduction and Aloy embroidery observation are present; complete ending at17.32s. No missing sentence, repetition, invented greeting or time reversal.',
  'recognitionVariants':['네 종 /4종','띄어쓰기: 옮겨 보죠 / 옮겨보죠'],
  'independentContextRequired':False,'endingObserved':'두 복원 표시를 읽고 같은 무늬의 경계를 보세요.','humanPronunciation':'pending'},
 'context-tsr-rotation-vectors':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both full mannequin-history and rotation-vector paragraphs are present through the final endpoints/background observation. No invented greeting, repeated sentence or time reversal. This longer independent context also resolves whole05 silhouette chunk repetition. Alignment overlaps0.26s and0.14s are preserved, not treated as repeated audio.',
  'recognitionVariants':['얇은 / 얄은','앞의 / 앞에','배경 사이 경계 / 배경 사이의 경계','그 자리의 / 그 자리에'],
  'independentContextRequired':False,'endingObserved':'끝점과 새로 드러난 배경을 각각 따라가겠습니다.','humanPronunciation':'pending'},
 'context-tsr-silhouette-history':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete reveal/history and mannequin-boundary paragraphs and the full final sentence are present. No invented goodbye, repeated sentence or time reversal in this complete independent context; it resolves the whole05 chunk-boundary insertion and backward repetition. Small0.16s and0.18s word-alignment overlaps do not repeat speech.',
  'recognitionVariants':['배경 사이 경계 / 배경 사이의 경계','그 자리의 / 그 자리에','띄어쓰기: 보여줄'],
  'independentContextRequired':False,'resolvesWholeChunkArtifact':'whole-05','endingObserved':'과거의 표면과 현재의 표면이 같은지를 먼저 따져야 하는 이유입니다.','humanPronunciation':'pending'},
 'context-texture-scene-return':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete pool-policy and scene-return paragraphs and full ending are present. Independently reads 편집하는 동안 and 실제 장면 correctly where whole04 differed. No sentence omission, repetition or greeting. A0.18s 보세요/무늬가 alignment overlap does not repeat a sentence.',
  'recognitionVariants':['그때의 / 그때'],
  'independentContextRequired':False,'endingObserved':'통계를 함께 남기는 것이 다음 실험의 기준입니다.','humanPronunciation':'pending'},
 'context-runtime-texture-size':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete texture-consumer and size/address paragraphs and their endings appear. No sentence omission, repetition or greeting. However, this recognizer context substitutes 전구 for 정보 at2.90s, while the current whole04 result reads 정보 형식 correctly. Preserve this conflict and check a complete producer/consumer/size context with current PCM before approval.',
  'recognitionVariants':['정보 / 전구','앞의 / 앞에','텍셀 / 택셀','색 자료 / 색자료'],
  'independentContextRequired':True,'contextTarget':'runtime-texture-consumer','contextScope':'A complete preceding producer, consumer and following size paragraph independently checks the 정보 형식 phrase; neither recognition result alone establishes actual mispronunciation.',
  'endingObserved':'주소와 내용을 각각 예산으로 잡아야 합니다.','humanPronunciation':'pending'},
 'context-shadow-wheel-change':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both full surface/movement and cache-validity paragraphs and their final sentences are present. Independently resolves the whole02 도식의/도시계 variant: this context reads 도식의 correctly. No sentence omission, repetition or greeting. The initial timestamp lines omitted by the first tool-output truncation were directly reread separately.',
  'recognitionVariants':['그 아래 / 그 아래의','주소 칸 / 주소칸'],
  'independentContextRequired':False,'endingObserved':'도식의 주소 칸을 찾는 화살표와 갱신하는 화살표가 다른 역할을 맡았던 이유죠.','humanPronunciation':'pending'},
 'context-04-guide-vsm-motion':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'Both complete cache/recalculation and camera-motion paragraphs match the expected text and final comparison sentence. No missing sentence, repetition or greeting. A0.14s boundary overlap at 조건입니다/어떤 is preserved as alignment evidence.',
  'recognitionVariants':[],'independentContextRequired':False,'endingObserved':'다시 그린 자료와 재사용한 자료를 비교할 수 있습니다.','humanPronunciation':'pending'},
 'context-part1-overview':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'The independent complete overview matches all three sentences, including question, shadows/upscaling/mobile order and first-example connection. Every timestamp read; no omission, repetition or invented greeting.',
  'recognitionVariants':[],'independentContextRequired':False,'endingObserved':'먼저 필요한 그림자만 저장하는 방법부터 살펴보죠.','humanPronunciation':'pending'},
 'whole-01':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All nine expected paragraphs and the final observation sentence are present. No whole-sentence omission or repetition. Small word-boundary overlaps are retained without treating them as repeated speech.',
  'recognitionVariants':['언리얼 / 얼리얼','출발해 / 출발에','사이버펑크의 비교에서 / 사이버펑크에 비교해서','앞선 열여섯 칸 / 앞에 열여섯 칸','다섯 칸에 / 다섯 칸의'],
  'independentContextRequired':False,'endingObserved':'여기서는 엔진이 표시하는 영역을 관찰합니다.','humanPronunciation':'pending'},
 'whole-02':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All six paragraphs on address/cache/movement/invalidation/SMRT are present. Full compact word-timestamp reread completed after an earlier pretty-JSON output had truncated the middle. No invented greeting, sentence omission or repetition.',
  'recognitionVariants':['그 아래 / 그 아래의','도식의 / 도시계','언리얼의 / 얼리얼의','반그림자를 / 반그림 자를'],
  'independentContextRequired':False,'endingObserved':'장면의 모든 실제 삼각형을 레이로 검사하는 방식과 구별해야 합니다.','humanPronunciation':'pending'},
 'whole-03':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All six intended paragraphs appear, but the chunked recognizer adds an unrequested news ending at69.98s, then repeats words with timestamps returning to60s. This is unresolved recognition evidence, not a claim that the PCM contains that ending or repetition.',
  'recognitionVariants':['이름에 / 이름의','맡습니다 / 맞습니다','무늬 / 문의','자산 / 자상','여기의 / 여기에'],
  'chunkArtifact':{'extraText':'지금까지 뉴스 스토리였습니다.','timestamps':[[69.32,69.98],[69.98,69.98],[69.98,69.98]],'followingWord':'무늬를','followingTimestamp':[60.0,60.46],'repeatedSpanApproxSeconds':[60,69.5]},
  'independentContextRequired':True,'contextTarget':'texture-streaming-input','contextScope':'Complete preceding resource-cache paragraph, whole texture-streaming-input paragraph and following texture-stack-uv paragraph from the current mix.',
  'endingObserved':'설정을 바꾸기 전에 어떤 표면과 필터 조건을 위해 쓰는지부터 정하는 이유입니다.','humanPronunciation':'pending'},
 'whole-04':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All seven intended paragraphs appear. At the ordinary texture-pool transition the chunked recognizer adds an unrequested goodbye at69.98s and returns to60s, repeating words. This is unresolved recognition evidence, not a claim about actual speech. The existing runtime-size independent window does not cover the complete ordinary-pool paragraph.',
  'recognitionVariants':['변위 / 변이','앞의 / 앞에','편집하는 동안 / 편집을 동안','장면 / 장�면','그때의 / 그때'],
  'chunkArtifact':{'extraText':'다음 영상에서 만나요.','timestamps':[[69.92,69.98],[69.98,69.98]],'followingWord':'주소와','followingTimestamp':[60.0,60.52],'repeatedSpanApproxSeconds':[60,69.86]},
  'independentContextRequired':True,'contextTarget':'ordinary-streaming-budget','contextScope':'Complete preceding runtime-size paragraph, whole ordinary texture-pool paragraph and following virtual-pool-policy paragraph from the current mix.',
  'endingObserved':'현재 프레임과 이전 프레임의 정보를 이용해 더 높은 해상도의 화면을 복원하는 시간적 업스케일링입니다.','humanPronunciation':'pending'},
 'whole-05':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All seven intended paragraphs appear. The recognizer adds a zero-duration goodbye at129.98s and repeats the last silhouette paragraph with timestamps returning to120s. The existing independent silhouette window must resolve this. A separate mathematical recognition variant reverses 사분의 일 to 1분의4 twice; independently check that complete numerical explanation rather than treating it as approved speech.',
  'recognitionVariants':['언리얼 / 얼리얼','구현 / 구형','사분의 일 / 1분의4','기하 / 기아','지터 / 짙어','복원 / 보건','그 자리의 / 그 자리에'],
  'chunkArtifact':{'extraText':'다음 영상에서 만나요.','timestamps':[[129.92,129.98],[129.98,129.98],[129.98,129.98]],'followingWord':'인물이','followingTimestamp':[120.0,120.28],'repeatedSpanApproxSeconds':[120,130]},
  'independentContextRequired':True,'contextTarget':'tsr-silhouette-history','contextAlreadyRequested':True,'additionalSemanticContextTarget':'original-18t-3','contextScope':'Existing complete silhouette context resolves the chunk boundary; additional complete grid/numerical-cost/vector context checks the quarter-pixel statements.',
  'endingObserved':'과거의 표면과 현재의 표면이 같은지를 먼저 따져야 하는 이유입니다.','humanPronunciation':'pending'},
 'whole-06':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All nine rotation and four-game comparison paragraphs and the final frame-generation distinction are present. No invented greeting or repeated chunk. The recognizer drops the first syllable of 자수의 at54.50s; use the already-requested complete Outer comparison context to resolve that boundary before approval.',
  'recognitionVariants':['얇은 / 얄은','앞의 / 앞에','자수의 / 수의','바닥의 / 바닥에','켜짐과 꺼짐 / 켜진과 꺼진','표시용 / 표시형'],
  'independentContextRequired':True,'contextTarget':'outer-displayed-frames','contextAlreadyRequested':True,'contextScope':'Existing context includes the preceding complete 자수의 복원 transition and the whole Outer displayed-frame paragraph.',
  'endingObserved':'표시 프레임 수가 증가한 것과 게임의 시뮬레이션이나 입력 처리 횟수가 같은 비율로 증가한 것은 같지 않습니다.','humanPronunciation':'pending'},
 'whole-07':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All seven intended paragraphs appear. A zero-duration goodbye at69.98s repeats the road-mask introduction after returning to60s. Existing complete barrier context includes the road-mask paragraph. Numerical interpolation also has an overlapping duplicated 1입니다 at123.36s and split quarter tokens; check that full calculation independently.',
  'recognitionVariants':['디퍼드 / 딥퍼드','기하 / 기아','삼각형 번호 칠 / 삼각형 번호치','세 꼭짓점 / 색꼭지점','보간 / 보관','바뀌므로 / 바뀜으로','같게 / 갖게','세 / 새'],
  'chunkArtifact':{'extraText':'다음 영상에서 만나요.','timestamps':[[69.62,69.98],[69.98,69.98],[69.98,69.98]],'followingWord':'지오메트리','followingTimestamp':[60.0,60.86],'repeatedSpanApproxSeconds':[60,69.74]},
  'independentContextRequired':True,'contextTarget':'geometry-barrier-views','contextAlreadyRequested':True,'additionalSemanticContextTarget':'07-pre-visibility-interpolation',
  'contextScope':'Existing complete road-mask/barrier context resolves the chunk boundary; additional full interpolation context checks all coordinates, weights and 0.25 results.',
  'endingObserved':'원근 조건이 달라지면 보정도 필요합니다.','humanPronunciation':'pending'},
 'whole-11':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All five transfer/limitations/transparency/renderer-choice/conclusion paragraphs appear with full final sentence. No invented greeting, omitted sentence or repeated chunk. 네 게임 is rendered 내 게임 at the beginning; verify the already-requested complete transfer context. A0.02s word-boundary overlap at 것이/아니라 is retained without claiming repeated speech.',
  'recognitionVariants':['네 게임 / 내 게임','에이피아이 / API','앞의 / 앞에','띄어쓰기: 투명층, 조명수, 다음편, 광원표본'],
  'independentContextRequired':True,'contextTarget':'four-game-transfer-conclusion','contextAlreadyRequested':True,
  'contextScope':'Existing independent complete transfer-conclusion context verifies the initial four-games phrase; final-conclusion context independently verifies the full closing transition.',
  'endingObserved':'다음 편은 그 예산 안에서 빛의 경로와 광원 표본을 고르는 문제로 이어집니다.','humanPronunciation':'pending'},
 'whole-10':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All seven mobile/tile-memory, Fortnite diagnostic and2014 engine-observation paragraphs appear. A zero-duration news ending at109.98s returns to100s and repeats part of the engine-history paragraph. Also a zero-duration 달라은 precedes 달라집니다 at66s. Full compact word timestamps were reread separately after the combined output truncated two words. Existing complete Fortnite and Rivalry contexts must resolve these recognizer artifacts.',
  'recognitionVariants':['언리얼 / 얼리얼','지 버퍼 / G버퍼','앞의 / 앞에','복원 / 보건','달라집니다 / 달라은 달라집니다','띄어쓰기: 사례수, 성능순위'],
  'chunkArtifact':{'extraText':'지금까지 뉴스 스토리였습니다.','timestamps':[[109.30,109.98],[109.98,109.98],[109.98,109.98]],'followingWord':'목표를','followingTimestamp':[100.0,100.40],'repeatedSpanApproxSeconds':[100,109.5]},
  'independentContextRequired':True,'contextTarget':'rivalry-mobile-history','contextAlreadyRequested':True,
  'contextScope':'The actual request for context-rivalry-mobile-history includes both the complete preceding fortnite-normal-material paragraph and the complete longer history paragraph; it therefore independently checks both observed insertions. The Fortnite mobile-test context itself has no normal-material paragraph.',
  'endingObserved':'앞에서 살펴본 화면 자료를 실제 움직임에 연결해 보세요.','humanPronunciation':'pending'},
 'whole-09':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All seven mobile hardware, profile, size, console-variable, compiler-warning and local-memory paragraphs appear with complete endings. No invented greeting, omitted sentence or repeated chunk. A setting/그 boundary overlaps0.02s; retained as word alignment, not repeated audio.',
  'recognitionVariants':['무늬를 / 무의를','기기에 / 기기의','여기의 / 여기에','셰이더 / 세이더','띄어쓰기: 비어있는, 안됩니다'],
  'independentContextRequired':False,'endingObserved':'밖으로 내보냈다가 다시 가져오는 왕복을 줄일 수 있습니다.','humanPronunciation':'pending'},
 'whole-08':{
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,
  'finding':'All seven geometry/visibility/material/mobile transition paragraphs appear with complete endings. No invented greeting, omitted sentence or chunk repetition. A small 개발 boundary overlaps0.02s; retain it as word-alignment evidence without claiming repeated speech.',
  'recognitionVariants':['분기 / 붕기','뒤의 / 뒤에','셰이딩 / 쉐이딩','띄어쓰기: 텍스처 가, 비용 이'],
  'independentContextRequired':False,'endingObserved':'디퍼드는 재질 정보와 조명 계산을 어떤 순서로 나누는지에 관한 선택입니다.','humanPronunciation':'pending'}
}
execution=read(P/'part1-final-mixed-asr-execution-v243.json');request=read(P/'part1-final-mixed-asr-request-v243.json')
rows=[]
for name,note in manual.items():
 result=next(r for r in execution['results'] if r['label']==name);j=read(ROOT/result['path'])
 assert sha(ROOT/result['path'])==result['sha256'] and j['mixSha256']==request['mixSha256']
 rows.append({'label':name,'path':result['path'],'sha256':result['sha256'],'paragraphIds':j['window']['paragraphIds'],'windowPcmSha256':j['windowSha256'],**note})
dest=P/'part1-final-mixed-asr-direct-progress-v251.json'
record={'recordedAt':datetime.now(timezone.utc).isoformat(),'currentMixSha256':request['mixSha256'],'planSha256':request['planSha256'],'manuallyReadResults':rows,'wholeResultsManuallyRead':sum(r['label'].startswith('whole-') for r in rows),'independentResultsManuallyRead':sum(not r['label'].startswith('whole-') for r in rows),'requestTotal':30,'allWholeAndIndependentTextsDirectlyCompared':len(rows)==30,'allWordEndingsAndTimestampsCompared':len(rows)==30,'finalMixedAsrApproved':False,'allFinalPixelsReviewed':False,'qaApproved':False,'uploaded':False,'humanWholeListening':'pending','humanPronunciation':'pending','newTts':0,'newGitImages':0,'next':'Continue the live30-window ASR; direct-read every result. After it completes, recognize only evidenced artifacts in complete independent contexts, then compare current PCM before any approval.'}
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'manuallyReadWholeResults':record['wholeResultsManuallyRead'],'manuallyReadIndependentResults':record['independentResultsManuallyRead'],'finalApproved':False}))
