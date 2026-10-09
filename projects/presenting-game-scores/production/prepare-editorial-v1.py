"""Independent commentary written after source observation; no media synthesis."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,subprocess,time,os
ROOT=Path(__file__).resolve().parents[3];PROJECT=ROOT/'projects/presenting-game-scores';BASE=PROJECT/'production'
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-presenting-game-scores'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+f'.{os.getpid()}.writing')
 t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
now=lambda:datetime.now(timezone.utc).isoformat()
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
bank=read(PROOF/'source-action-bank-v4.json');assert bank['sourceSamplesAndFramingApproved']
# Sources and source-to-claim connections are saved before narration.
candidates=dict(schemaVersion=4,slug='presenting-game-scores',reviewedAt=now(),
 status='reviewed-source-bank-selected-for-independent-commentary; measured adoption pending',
 sourceActionBank=str((PROOF/'source-action-bank-v4.json').relative_to(ROOT)).replace('\\','/'),sourceBankSha256=sha(PROOF/'source-action-bank-v4.json'),
 sourceCandidates=bank['sources'],selectedIntervals=bank['cuts'],rejected=bank['rejected'],reviewProofs=bank['reviewProofs'],
 maximumUniqueNormalSpeedActionSeconds=bank['selectedMaximumUniqueActionSeconds'],
 recentUse=dict(method='Repository source-candidate exact title search plus already-read recent delivery sources',
  search='rg -n "Ballionaire|Balatro|Tetris Effect" projects --glob game-candidates.json',
  matches=['projects/game-reward-planning/sources/game-candidates.json'],
  finding='Balatro was considered in game-reward-planning, not selected in its delivered Cult of the Lamb examples. No prior TEC intervals were found by this title search. This does not claim an exhaustive search of every frame.',
  newSegments=True),sourceAudioSelected=False,selfCreatedExamples=False,loop=False,slowdown=False,
 allSelectedSourceSamplesAndFramingDirectlyReviewed=True,allNativeFramesDirectlyReviewed=False,
 allActualNarrationCuePixelsReviewed=False,finalFootageRendered=False,bodyRatioApproved=False,publicRightsApproved=False,
 newRasterGitAdditions=0,
 rightsCaveats=['Tetris official owner B-roll supplied through official media page. Read record/stream policy does not grant blanket reuse of arbitrary third-party recordings.',
  'Balatro historic official press master; read video-policy scope preserved. No third-party recording/music adopted.',
  'Ballionaire remains held because the functional product-link condition was not silently removed under public-credit omission preferences.'])
save(PROJECT/'sources/game-candidates.json',candidates)
(PROJECT/'sources/SOURCES.md').write_text('''# Sources and reviewed action bank

Research concept: [Presenting Scores — Masahiro Sakurai](https://www.youtube.com/watch?v=FeekeBW26AI). The complete Japanese research transcript was read; its examples/order and audiovisual content are not copied. Our independent question concerns quantity versus evaluation, comparison baselines, and readable scoring feedback.

## Official existing-game recordings

- [Tetris Effect: Connected official media](https://www.tetriseffect.game/connected/media/) → official press B-roll folder `1LyBkTx4u-6cNnS1dIYmsKx6UWysop0F0`. Owner Enhance Games. [Record/stream support conditions](https://www.tetriseffect.game/support/) were read. Use the owner-supplied Classic Score Attack and Score Attack recordings with independent commentary and no source music. This is not arbitrary third-party stream reuse permission or proof of the current patch.
- [Balatro official press kit](https://www.playbalatro.com/press-kit/) supplies `Balatro_trailer_Master_Final.mp4`. Owner LocalThunk/Playstack. Historic press closeups show selected cards, hand name, chips and multiplier. Do not turn the montage into a claimed continuous run, exact strategy, final round result, or current-patch proof. All source sound is omitted. The complete linked video conditions and individual scope were read; final public-rights review remains pending.
- [Raw Fury Let's Play conditions](https://rawfury.com/letsplay/) and Ballionaire official launch master were researched. **Held**: the functional product-link requirement remains unresolved under the user's public-description credit omission preference. No adopted Ballionaire time.

Exact original hashes/native timebases/exclusive frame boundaries, observed actions, captions and semantic connections are in `game-candidates.json` and the proof `source-action-bank-v4.json`. Eleven reviewed intervals offer at most183.324967s of unique normal-speed action; this is a source bank, not a measured final timeline or60:40 approval.

## Framing and internal proof

Tetris retains full horizontal width, shifts the original down-screen layout upward120px without scaling, and fills only the vacated120px with a blur of the same frame. SCORE/LINES/playfields/NEXT/player names/WINS were directly checked with fixed two-line caption trials. Balatro's selected-hand shot uses the original closeup and one-line cues; count-up shifts48px with same-frame fill to clear enlarged glyphs. The original official closeup already truncates part of Round score; our commentary does not use that field as evidence.

All149 nominal boards/886 samples,50 native trial boards/295 overlays,23 corrected Tetris boards/133 samples,5 Balatro boards/25 samples and2 repaired count-up boards/10 samples were directly read. These sets overlap: they are not a sum of unique native frames or approval of every continuous source frame. Original caption collisions, failed unescaped FFmpeg filter and successful preserved-PTS recovery remain in the proof history.

Original media/info/transcripts/source frames/contact boards/QA remain local-only. Final measured timing, actual narration-cue pixels, continuous final playback, human listening/pronunciation and public rights remain pending.
''','utf-8')
rows=[
('01-overview','점수는 무엇을 말해 줄까?','What does a score tell us?',[
 '숫자가 커졌다는 것만으로 무엇을 잘했는지 알 수 있을까요?',
 '이번에는 테트리스의 점수와 지운 줄 수를 비교하고, 상대와의 차이가 숫자의 의미를 어떻게 바꾸는지 보겠습니다.',
 '마지막으로 발라트로의 계산 연출을 살펴보며, 성과를 읽기 쉽게 만드는 이름과 표현을 정리해 보죠.'
],[
 'A bigger number does not automatically tell us what a player did well.',
 'We will compare points and cleared lines in Tetris, then see how a difference from an opponent changes what a total means.',
 'Finally, Balatro will help us connect visible calculation feedback to names and presentations that make performance easier to read.'
]),
('02-score-and-lines','진행량과 평가는 다르다','Quantity and evaluation',[
 '테트리스 이펙트 커넥티드 화면에는 점수와 지운 줄 수가 따로 있습니다.',
 '블록을 놓는 동안 점수가 바뀌어도 줄 수는 그대로인 순간이 있고, 줄이 지워지면 두 숫자가 함께 움직입니다.',
 '얼마나 진행했는지와 어떻게 평가됐는지를 한 숫자로 합치면 이런 차이를 놓치기 쉽습니다.'
],[
 'Tetris Effect: Connected displays points and cleared lines in separate fields.',
 'A placement can change points while the line count stays still. Clearing a row can change both displays.',
 'Treating progress and evaluation as one quantity would hide this distinction.'
]),
('03-same-count','같은 양, 다른 점수','Equal quantities, different scores',[
 '지운 줄 수가 같다면 점수도 같아야 할까요?',
 '두 사람의 줄 수가 같아지는 순간에도 점수는 다릅니다. 같은 양의 결과를 냈다는 말과 같은 평가를 받았다는 말은 다르죠.',
 '설계할 때는 횟수를 세는 지표와 플레이를 평가하는 지표를 먼저 구분해 보세요.'
],[
 'Does the same number of cleared lines have to mean the same score?',
 'Here, both players reach an equal line count but have different point totals. Equal quantities do not imply equal evaluations.',
 'Start a design by separating what you count from what you choose to evaluate.'
]),
('04-evaluation-weights','무엇을 높게 평가할까?','Choose what to value',[
 '점수를 만드는 규칙은 어떤 플레이를 높게 평가할지 정하는 기준입니다.',
 '이 화면에는 티 스핀 더블과 백 투 백이라는 알림이 나타납니다. 줄 수만 세는 화면보다 행동의 종류를 더 구체적으로 알려 주죠.',
 '전체 배점표를 화면만 보고 알아낼 수는 없지만, 내가 강조할 행동과 점수의 이름은 함께 설계할 수 있습니다.'
],[
 'A scoring rule expresses a choice about which kinds of play deserve more value.',
 'The visible T-SPIN DOUBLE and BACK-TO-BACK notices describe the action more specifically than a line count alone.',
 'The clip does not expose the complete scoring table. In our own design, however, the action we value and its score label should agree.'
]),
('05-events-and-total','이번 행동과 누적 결과','The event and the running total',[
 '계속 쌓이는 총점만 보면 방금 어떤 행동이 반영됐는지 놓칠 수 있습니다.',
 '줄이 사라지는 순간의 알림과 바뀌는 점수를 같이 보세요. 하나는 이번 행동을 가리키고, 다른 하나는 지금까지의 결과를 남깁니다.',
 '두 표시를 나란히 읽을 수 있어야 큰 숫자 속에서 방금 한 행동의 의미가 사라지지 않습니다.'
],[
 'A running total alone can make the latest contribution hard to identify.',
 'Watch the event notice as rows clear and the point display changes. One describes this action; the other retains the accumulated result.',
 'Keeping both readable helps a new contribution remain understandable inside a large total.'
]),
('06-relative-gap','누구와 비교한 숫자일까?','Choose the comparison reference',[
 '총점이 커도 상대보다 앞서는지는 별도의 질문입니다.',
 '두 사람이 스물일곱 줄을 지웠을 때도 점수 차이는 이천구백이십 점입니다. 나중에는 줄 수가 적은 쪽이 점수로는 백사십일 점 앞서기도 하죠.',
 '총점 옆의 차이를 읽으면 비교 기준이 분명해집니다. 다만 경기 중의 앞섬을 최종 승리와 같은 뜻으로 읽지는 말아야 합니다.'
],[
 'A large total and a lead over an opponent answer different questions.',
        'When both line counts show 27, the displayed scores differ by 2920. In a later shot, the player with fewer cleared lines leads by 141 points.',
 'A signed difference makes the comparison reference explicit. A lead during play still does not establish the final winner.'
]),
('07-name-and-unit','이름과 단위를 붙이기','Give the number a name and unit',[
 '숫자에 이름을 붙이면 플레이어가 무엇을 읽어야 하는지 달라집니다.',
 '이 화면의 점수와 줄 수처럼, 회수한 물품 수와 종합 평가 점수도 서로 다른 정보를 말할 수 있죠.',
 '어떤 결과를 세는지, 단위는 무엇인지, 높은 값과 낮은 값 중 무엇이 좋은지까지 분명하게 정해 보세요.'
],[
 'A label tells the player which meaning to attach to a number.',
 'Just as points and lines differ here, recovered items and an overall evaluation would communicate different things in a hypothetical design.',
 'Specify what is measured, its unit, and whether a higher or lower value represents a better result.'
]),
('08-scoring-feedback','계산을 읽는 순간','Make the calculation readable',[
 '발라트로의 짧은 계산 화면에서는 선택한 카드와 손패 이름, 칩과 배수가 차례로 눈에 들어옵니다.',
 '카드의 반응 뒤에 숫자가 커지고 강조되는 모습을 보세요. 결과를 한 번에 던지기보다 변화하는 과정을 보여 줍니다.',
 '내 게임에서도 중요한 기여를 먼저 보이고 합계를 읽게 할 수 있습니다. 연출이 커질수록 숫자와 단위가 가려지지 않는지도 확인해야 하죠.'
],[
 'These short Balatro closeups draw attention to the selected cards, hand name, chips, and multiplier.',
 'After the card reactions, numbers grow and receive emphasis. The result is presented through visible changes rather than only as a static final value.',
 'A design can reveal important contributions before its total. As the animation expands, keep the number and its meaning unobscured.'
]),
('09-feedback-hierarchy','남아 있는 숫자와 지나가는 알림','Persistent values and transient notices',[
 '모든 정보를 똑같이 크게 보여 주면 중요한 결과를 찾기 어렵습니다.',
 '플레이가 이어지는 동안 총점과 줄 수는 남아 있고, 개별 행동의 알림은 나타났다 사라집니다. 읽는 역할과 시간이 다르죠.',
 '계속 비교할 값은 안정된 위치에 두고, 이번 행동의 강조는 짧게 구분해 주세요. 강조가 본래 숫자를 밀어내지 않게 하는 것도 중요합니다.'
],[
 'If every detail receives the same visual weight, the useful result becomes harder to find.',
 'During play, totals and line counts remain available while individual event notices appear and disappear. They serve different reading times.',
 'Keep values used for repeated comparison in stable positions and distinguish brief event emphasis without displacing those values.'
]),
('10-audit-and-close','세 가지 질문으로 점검하기','Audit the score display',[
 '점수를 넣기 전에 무엇을 센 숫자인지, 누구와 비교하는지, 변화를 알아볼 수 있는지 물어보세요.',
 '테트리스의 줄 수와 점수, 경기 중의 차이, 발라트로의 계산 연출이 각각 이 질문을 보여 줬습니다. 큰 숫자보다 읽을 수 있는 성과가 먼저입니다.',
 '직접 만든 화면에서도 이름과 기준을 설명해 보세요. 게임 프로그래밍을 함께 설계하고 구현해 보고 싶다면 설명란의 과외 안내를 확인해 주세요.'
],[
 'Before adding a score, ask what it measures, what it is compared with, and whether its changes are readable.',
 'Tetris showed quantity versus evaluation and a live comparison; Balatro showed calculation feedback. Meaningful performance comes before an impressive-looking total.',
 'Try explaining the labels and baselines in your own interface. For guided game-programming design and implementation, the description links to our coaching information.'
])]
ko=dict(title=read(PROJECT/'project.json')['titles']['ko'],language='ko',independentlyWritten=True,scenes=[])
en=dict(title=read(PROJECT/'project.json')['titles']['en'],language='en',independentlyWritten=True,scenes=[])
for sid,kt,et,kl,el in rows:
 ko['scenes'].append(dict(id=sid,title=kt,lines=kl));en['scenes'].append(dict(id=sid,title=et,lines=el))
save(PROJECT/'script/narration.ko.json',ko);save(PROJECT/'script/narration.en.json',en)
spatial=[
 ('three-stations','Three projected plinths: quantity/evaluation, opponent baseline, calculation. Camera eases across their tops in the promised order, then first plinth comes forward.'),
 ('separate-counters','Two projected block towers share a floor. A score block rises while the line tower stays still, then a line block arrives; top/side faces and occlusion show independent changes.'),
 ('equal-lines-different-points','Equal-height teal line towers in front of different-height gold score towers; camera shifts to expose the hidden height difference without implying a scoring formula.'),
 ('event-to-value','Three distinguishable event tokens slide along separate spatial lanes to an evaluation gate. Unequal output heights are explicitly illustrative, not proprietary Tetris weights.'),
 ('persistent-total-and-event','A small orange event token moves onto a retained score stack. The transient label fades while the stack stays; front/top/side faces show the contribution becoming part of the total.'),
 ('baseline-and-difference','Two score towers share an axis; a teal ruler spans their height difference. A second view aligns equal line towers. Show observed2920 and later141 as separate snapshots, not a computed win.'),
 ('named-units','A projected tray of three counted objects becomes a named quantity; another score tower uses its own label. Rotate viewpoint to reveal the tops while labels remain screen-facing. Mark the invented objects as a design diagram.'),
 ('chips-times-mult','Two spatial input stacks feed a multiplication bridge and a result stack. Use a labeled illustrative2×3=6, not a claimed transcription of the press clip. Orange contribution moves, count-up settles.'),
 ('stable-and-transient','Persistent value stacks stay anchored on a floor while one orange event token enters from behind, rises, then exits. Two projection views visibly differ; a stable label never moves into the caption region.'),
 ('three-audit-gates','Meaning, reference and readable change are three spatial gates. A labeled score token passes in order with occlusion and camera parallax, then settles beside the canonical coaching-link card above the caption safe area.')]
visual=dict(schemaVersion=1,slug='presenting-game-scores',style='research-black-v1',
 palette=read(ROOT/'shared/publishing/explanation-style-policy.json'),independentScenes=True,
 caption=dict(id='boxed-white-forest-v1',centerPx=[960,970],motionCanvasCenter=[0,430],maxLines=2,
  balatroMaxLines=1,contentSafeBottomPx=850),sceneContracts=[],
 measuredNarrationTimingAvailable=False,actualAnimatedPixelsApproved=False,finalPixelsApproved=False)
for (sid,kt,et,kl,el),(kind,contract) in zip(rows,spatial):
 visual['sceneContracts'].append(dict(id=sid,title=kt,diagram=kind,spatialContract=contract,
  sourceCutIds=[x['cutId'] for x in bank['cuts'] if x['scene']==sid],
  paragraphCount=len(kl),paragraphMotionReview=False,durationSeconds=None))
save(BASE/'visual-contract-v1.json',visual)
manifest=read(PROJECT/'project.json');manifest.update(status='independent-editorial-written-awaiting-whole-text-review',publishReady=False)
manifest['paths']['scriptEn']='projects/presenting-game-scores/script/narration.en.json'
manifest['editing'].update(exampleSeconds=0,timingStatus='pending-approved-voice-measurement-and-source-allocation',
 openingOverview=dict(required=True,scene='01-overview',targetSeconds=[20,30],measuredSeconds=None,
  question='숫자의 크기만으로 무엇을 잘했는지 알 수 있을까?',outcome='구체적인 지표의 이름·단위·비교 기준과 계산 표시를 점검한다.',
  orderedSteps=['Tetris quantity versus evaluation','Opponent difference and labels','Balatro calculation feedback'],
  firstExample='02-score-and-lines',classification='explanation',reviewedBeforeTts=False),
 sourceBank=bank['selectedMaximumUniqueActionSeconds'],sourceActionBank=candidates['sourceActionBank'],
 visualContract='projects/presenting-game-scores/production/visual-contract-v1.json')
manifest['audio'].update(mixStatus='pending-voice-and-measured-timeline',sourceAudioPolicy='No source game audio/music; approved narration and continuous Nimbus only.')
manifest['audio']['backgroundMusic']=dict(required=True,approvalStatus='approved-continuous-Nimbus-by-user-production-defaults',
 title='Nimbus',artist='Eveningland',file='shared/assets/music/youtube-audio-library/Nimbus-Eveningland-restored.m4a',
 sha256=sha(ROOT/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland-restored.m4a'),originalLibraryFileApproval='pending')
manifest['approvals']=dict(wholeScriptReview='pending',voice='reuse-user-approved-Qwen1.7B-reference',
 humanListening='pending',humanPronunciation='pending',publicRights='pending',finalMixedAsr=False,allFinalPixels=False)
save(PROJECT/'project.json',manifest)
outline='''# 점수는 무엇을 말해 줄까?

중심 질문은 숫자의 크기만으로 무엇을 잘했는지 알 수 있는가다. 결과의 양과 평가를 구분하고, 이름·단위·비교 기준·표현을 함께 점검한다. 보상 경제나 플레이 동기의 일반론을 다시 설명하지 않는다.

## 전체 안내와 독립 해설

원본 고양이2초 다음01-overview의 세 자연스러운 문장은 질문 → 테트리스의 양/평가와 상대 차이 → 발라트로의 계산 연출/적용 순서다. 목표20–30초는 계획값이며 TTS 실측 전에는 승인 시간이 아니다. 첫 세부 예시는02-score-and-lines다. 본론과 결론이 이 순서를 실제로 이행한다. 모든30문단은 원본 강의의 전체 복사번역이 아닌, 먼저 직접 본 새 게임 행동을 설명하는 독립 KO/EN이다.

## 장별 실제 행동과 설명 연결

| 독립 씬 | 설명할 질문 | 검토한 source-bank 컷 | 공간 설명 |
|---|---|---|---|
|01-overview|점수의 의미를 어떤 순서로 읽을까?|안내 도식;본편 설명40%|서로 다른 깊이의 세 관찰 지점으로 시점을 이동|
|02-score-and-lines|진행량과 평가는 같은가?|classic-01|독립 두 탑의 증가 시점 비교|
|03-same-count|같은 줄 수가 같은 점수인가?|classic-02|동일 높이의 줄 탑과 서로 다른 점수 탑|
|04-evaluation-weights|어떤 행동을 높게 평가할까?|modern-01|행동 토큰과 평가 게이트;그림 값은 예시|
|05-events-and-total|이번 행동과 총점을 함께 읽을 수 있나?|modern-02|새 기여가 누적 탑에 합쳐지고 알림만 사라짐|
|06-relative-gap|누구와 비교한 차이인가?|modern-03/04|공통 기준축과 차이 자;2920/141은 별도 관찰 순간|
|07-name-and-unit|무슨 결과·단위를 세는가?|classic-03|이름 붙인 물품 트레이와 별도 평가 탑|
|08-scoring-feedback|기여와 계산 과정을 읽을 수 있나?|balatro-hand/countup|칩·배수 입력과 곱셈 다리;2×3=6은 설명 예제|
|09-feedback-hierarchy|남길 값과 잠깐 강조할 값은 무엇인가?|classic-04|고정 누적 탑과 깊이 방향에서 오는 이벤트|
|10-audit-and-close|의미·기준·변화를 점검했는가?|modern-05|세 질문의 공간 게이트와 코칭 안내|

각 컷의 원본 native frame/PTS·배타적 끝·행동·초점·문단 연결은 `sources/game-candidates.json`을 따른다. 장 안에서 관찰과 설명을 교차하고 게임은 전체 화면 정상 속도로 보여준다. 확보한 최대183.324967초를 그대로 최종 비중으로 승인하지 않는다. 실측 PCM을 보존한 뒤 고유 구간을 적절히 세분/축약하고 부족하면 관련 실제 자료를 추가한다. 필요한 설명을 자르거나 루프·저속·무관한 대기로 할당하지 않는다.

## 검정 배경의 실제2.5D

`research-black-v1`: #000배경,흰 본문,금색 제목,청록 선/축,주황 초점. 독립10개 MC에서 앞/옆/윗면,높이,가림,시점의 상대 이동을 실제 투영하고 각 문단 의미에 맞춰 움직인다. 평면 카드의 그림자만으로 승인하지 않는다. 도형과 보조 문구는 화면y850이내에 유지해 고정 두 줄 자막 상단y897과 여백을 둔다. 실제 움직이는 렌더와 모든 문단/자막 큐를 직접 검토해야 한다.

## 보존과 미완료

고양이120프레임·회원600프레임과 원본12행 신원/제목을 보존한다. 본편 actual60/explanation40 최대1프레임오차, fixed boxed-white-forest `(960,970)`/MC`(0,430)`. Tetris는 fullwidth 위120px 재배치, Balatro는 한 줄 큐와 countup48px 보정으로 원래 숫자/단위가 자막에 가려지지 않게 한다. 모든 실제 최종 큐를 별도로 검토한다. 연속 Nimbus와 기존 승인 목소리를 재사용하며 소스 음성·음악0이다.

GPU는 실제 연구 작업의 최종 저장/검증/done 경계 뒤 자기 토큰의 협력 정지로만 배정한다. 기존 다른 TTS 인계는 보존하고 앞 작업 종료를 기다린다. 성공/실패 후 원래 연구 명령·폴더·큐의 실제 재개를 확인한다. 전체 음성/독립 문맥 및 최종 혼합 ASR, 두decode/90000PTS/동일AAC/음량,최종픽셀,4파일,단일 비공개 설정,선택 Git는 아직미완료다. 사람 전체 청취·발음·공개 권리·Nimbus원본·잘린회원핸들·백업·자동더빙·optionalCC·비공개댓글은pending으로 남긴다.
'''
(PROJECT/'planning/outline.md').write_text(outline,'utf-8')
(PROJECT/'README.md').write_text('# '+ko['title']+'\n\nIndependent30-paragraph KO/EN and ten projected research-black-v1 scene contracts are prepared after current content/Studio duplicate review and official source-bank observation. No TTS/render/mix/QA/collection/upload is complete. Source-bank maximum183.324967s is not final60:40 timing. Preserve local originals and shared research queues.\n','utf-8')
save(BASE/'latest-checkpoint.json',dict(schemaVersion=1,slug='presenting-game-scores',recordedAt=now(),
 stage='independent-editorial-written-awaiting-whole-text-review',scenes=10,paragraphs=30,
 sourceBankSha256=sha(PROOF/'source-action-bank-v4.json'),scriptKoSha256=sha(PROJECT/'script/narration.ko.json'),
 scriptEnSha256=sha(PROJECT/'script/narration.en.json'),ttsStarted=False,finalTimingApproved=False,
 finalMixedAsrApproved=False,pairRendered=False,allFinalPixels=False,qa=False,collected=False,private=False,
 actualVideoId=None,nextAction='Read every KO/EN paragraph and source connection, seal current review; prepare single GPU request behind existing lease, then measured narration and spatial scenes.'))
print(json.dumps(dict(scenes=10,paragraphs=30,koCharacters=sum(len(x) for s in ko['scenes'] for x in s['lines']),
 overviewCharacters=sum(len(x) for x in ko['scenes'][0]['lines']),ttsStarted=False),ensure_ascii=False))
