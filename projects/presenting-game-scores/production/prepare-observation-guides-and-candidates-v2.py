"""Preserve the ten original PCM scenes; prepare guides and two unadopted takes."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os, psutil

ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
targetstate=BASE/'current-targets-asr-execution-v1.json';d=read(targetstate)
assert d['exitCode']==0 and d['completed']==d['total']==2
try:
 p=psutil.Process(d['pid']);assert abs(p.create_time()-d['createTime'])>=.01
except psutil.NoSuchProcess:pass
d.update(actualExitObserved=True,actualOuterExitCode=0,actualOuterSessionId=49538,actualWorkerAlive=False,actualExitObservedAt=now);save(targetstate,d)
session=BASE/'current-targets-asr-execution-v1.session.json';s=read(session);s.update(actualExitObserved=True,exitCode=0,workerExpectedRunning=False,observedAt=now);save(session,s)
rows=[]
for p in sorted((BASE/'current-targets-asr-v1').glob('[0-9]*.json')):
 x=read(p);assert x['exactSourceSampleBytesMatched'] and sha(ROOT/x['contextPath'])==x['contextSha256']
 rows.append(dict(path=rel(p),sha256=sha(p),expectedKo=x['expectedKo'],actualText=x['text'],allWordsAndEndingDirectlyRead=True,
  currentSourcePcmMatched=True,recognizedVariantPersists=True))
targetreview=BASE/'current-targets-direct-review-v1.json';assert not targetreview.exists()
save(targetreview,dict(schemaVersion=1,reviewedAt=now,rows=rows,allTargetTextsDirectlyCompared=True,
 currentVoiceApproved=False,actualSynthesisErrorConfirmed=False,humanListening='pending',humanPronunciation='pending',
 decision='Two complete paragraphs retain meaning-changing recognition variants in three contexts. Preserve every original byte; prepare separate exact-text takes and compare before adopting. Do not treat ASR spelling as proven audible error.',
 noWholeSentenceOmissionOrRepetitionIndicated=True,endingHeuristicUsedForApproval=False))

guides=[
 ('11-observe-separate-updates','02-score-and-lines','classic-01','두 표시가 움직이는 때',
 ['먼저 줄 수를 기준으로 화면을 읽어 보세요. 새 블록을 놓는 동안 줄 수가 그대로인데 점수는 움직이는 순간을 찾을 수 있습니다.',
  '이어서 줄이 사라질 때 두 표시를 함께 보죠. 하나의 숫자만 따라갈 때와 무엇이 달라지는지 비교해 보세요.'],
 ['First, follow the line counter. As new pieces are placed, look for a moment when the line count stays unchanged while the score moves.',
  'Then watch both fields when a line disappears. Compare what you notice with following only one number.']),
 ('12-observe-equal-quantity','03-same-count','classic-02','같아지는 줄 수부터 보기',
 ['이번에는 양쪽의 줄 수부터 비교해 보죠. 두 값이 같아지는 순간을 찾은 다음, 점수와 가운데 차이 표시로 시선을 옮겨 보세요.',
  '같은 양이라는 판단과 같은 평가라는 판단을 따로 읽을 수 있으면, 지표의 역할도 더 분명해집니다.'],
 ['This time, compare the two line counts first. Find a moment when they match, then move your attention to the scores and the difference between them.',
  'Reading equal quantity separately from equal evaluation makes each measure’s role clearer.']),
 ('13-observe-action-label','04-evaluation-weights','modern-01','알림의 이름 읽기',
 ['블록의 움직임과 함께 나타나는 동작 이름을 읽어 보세요. 알림은 방금 무엇을 했는지, 점수는 그 결과가 어떻게 남는지 보게 합니다.',
  '두 표시를 연결하되, 이 한 장면으로 모든 보너스 규칙을 단정하지는 마세요.'],
 ['Read the action label that appears with the moving pieces. The notice draws attention to what just happened, while the score shows a retained result.',
  'Connect those displays without treating this one shot as proof of every bonus rule.']),
 ('14-observe-notice-and-record','05-events-and-total','modern-02','사라지는 알림과 남는 기록',
 ['이번에는 알림이 나타나는 순간과 사라진 뒤를 나누어 보겠습니다. 알림이 지나가도 총점은 화면에 남아서 계속 비교할 수 있죠.',
  '잠깐 읽는 평가와 계속 확인하는 기록이 같은 크기와 같은 표시일 필요는 없습니다.'],
 ['Separate the moment when the notice appears from the view after it passes. The total stays available for comparison after the notice is gone.',
  'A brief evaluation and a persistent record do not need the same size or display.']),
 ('15-observe-equal-lines-gap','06-relative-gap','modern-03','같은 줄 수에서 비교하기',
 ['줄 수가 스물일곱으로 같은 순간, 왼쪽은 만사천구십육 점이고 오른쪽은 만칠천십육 점입니다.',
  '양쪽이 지운 양은 같지만 점수 기준에서는 오른쪽이 앞섭니다. 같은 화면에서도 비교할 단위를 먼저 정해야 하죠.'],
 ['At the observed moment when both line counts are twenty-seven, the left score is 14,096 and the right score is 17,016.',
  'The cleared quantity matches, but the right player leads in points. Choose the unit before comparing the same display.']),
 ('16-observe-later-point-lead','06-relative-gap','modern-04','다른 장면의 앞섬',
 ['나중 장면에서는 왼쪽의 줄 수가 적지만, 점수는 오히려 앞섭니다. 이 앞섬은 경기 중에 보이는 상태입니다.',
  '줄 수의 앞섬과 점수의 앞섬을 나누어 읽고, 이후에 바뀌는 차이도 함께 살펴보세요.'],
 ['In the later shot, the left player has fewer cleared lines but a higher score. That lead is a state observed during play.',
  'Separate a lead in lines from a lead in points, and keep watching how the difference changes afterward.']),
 ('17-observe-named-fields','07-name-and-unit','classic-03','이름을 따라 숫자 읽기',
 ['지금은 점수를 보는지 줄 수를 보는지 먼저 정하고 읽어 보세요. 이름이 빠진 숫자만으로는 어느 결과가 좋아졌는지 고르기 어렵습니다.',
  '내 화면의 숫자에도 같은 질문을 붙여 보죠. 무엇을 센 값인지 설명할 수 있어야 비교도 시작할 수 있습니다.'],
 ['Decide whether you are reading points or lines before following the values. A number without a name makes it hard to choose which result improved.',
  'Ask the same question of the numbers in your own display. A comparison starts with being able to explain what was counted.']),
 ('18-observe-stable-reading','09-feedback-hierarchy','classic-04','다시 찾을 위치',
 ['블록은 계속 떨어져도 총점과 줄 수를 다시 찾을 위치는 유지됩니다. 잠깐 나타나는 알림과 이 위치를 따로 보세요.',
  '효과를 크게 만들기 전에 플레이 중 다시 읽을 자리를 정하면, 강조가 지나간 뒤에도 비교를 이어갈 수 있습니다.'],
 ['Pieces keep falling, while the places to find the total and line count remain stable. Look at those locations separately from the brief notices.',
  'Choose where players can return to read during play before enlarging effects, so comparisons can continue after the emphasis passes.']),
 ('19-observe-reading-audit','10-audit-and-close','modern-05','실제 화면에서 다시 점검하기',
 ['이번에는 점수의 이름, 양쪽의 비교, 값이 바뀌는 순간을 차례로 읽어 보세요. 같은 플레이를 보더라도 확인하는 질문은 다릅니다.',
  '하나의 큰 숫자로 모든 성과를 대신하기보다, 플레이어가 어떤 기록을 보고 있는지 설명할 수 있게 만드는 것이 목표입니다.'],
 ['Read the score’s name, the comparison between players, and the moment when a value changes, in that order. These are different questions about the same play.',
  'The aim is to let players explain which record they are reading, rather than use one large number to stand for every achievement.'])
]
ko=read(BASE.parent/'script/narration.ko.json');en=read(BASE.parent/'script/narration.en.json')
bankp=ROOT/'production/batches/sakurai-planning-game-design/proof-presenting-game-scores/source-action-bank-v4.json';bank=read(bankp)
candidate_rows=[];ks=[];es=[]
for sid,parent,cutid,title,kl,el in guides:
 cut=next(c for c in bank['cuts'] if c['cutId']==cutid)
 assert cut['sourceSamplesDirectlyReviewed'] and cut['scene']==parent
 ks.append(dict(id=sid,title=title,lines=kl));es.append(dict(id=sid,title=title,lines=el))
 candidate_rows.append(dict(id=sid,kind='new-action-observation-guide',parentScene=parent,sourceCutIds=[cutid],
  sourceNativeRange=[cut['startFrame'],cut['endFrameExclusive']],visibleAction=cut['visibleAction'],diagramConnection=cut['diagramConnection'],
  insertion='Between the chapter’s actual observation and its retained explanation; exact paragraph/clip placement follows measured approved voice.',
  uniqueNativePartitionRequired=True,nativeFramesMayNotOverlapOriginalObservation=True,actualDurationSeconds=None))
for sid,parent in [('20-candidate-evaluation-p3','04-evaluation-weights'),('21-candidate-contribution-p3','08-scoring-feedback')]:
 k=next(x for x in ko['scenes'] if x['id']==parent);e=next(x for x in en['scenes'] if x['id']==parent)
 ks.append(dict(id=sid,title=k['title']+' · 独립 문단 후보',lines=k['lines'][2:]));es.append(dict(id=sid,title=e['title']+' · separate paragraph candidate',lines=e['lines'][2:]))
 candidate_rows.append(dict(id=sid,kind='same-exact-text-unadopted-paragraph-take',parentScene=parent,paragraph=3,
  sourceCutIds=[],sourceTextUnchanged=True,originalPcmPreserved=True,replacementAdopted=False,
  reason='Persistent recognition ambiguity; no audible-error assertion. Require direct whole and independent-context review of the new take, plus complete joins, before adoption.'))
kp=BASE.parent/'script/observation-candidates-v2.ko.json';ep=BASE.parent/'script/observation-candidates-v2.en.json'
assert not kp.exists() and not ep.exists()
save(kp,dict(language='ko',slug='presenting-game-scores',scenes=ks));save(ep,dict(language='en',slug='presenting-game-scores',scenes=es))
mp=BASE/'observation-candidates-voice-manifest-v2.json';m=copy.deepcopy(read(BASE.parent/'project.json'))
out='shared/output/narration/presenting-game-scores/qwen3-observation-candidates-v2'
m['paths'].update(script=rel(kp),scriptEn=rel(ep),narration=out+'/observation-candidates-v2.wav',captionsKo=out+'/observation-candidates-v2.srt',captionsEn=out+'/observation-candidates-v2.en.srt')
m['tts'].update(outputDir=out,filenameStem='observation-candidates-v2');save(mp,m)
reviewp=BASE/'observation-candidates-paired-direct-review-v2.json';save(reviewp,dict(schemaVersion=1,reviewedAt=now,
 contentReadyForApprovedVoiceMeasurement=True,pairedWholeTextReview=True,overviewPromiseReview=True,
 fullIndependentKoEnDirectlyCompared=True,sourceBank=rel(bankp),sourceBankSha256=sha(bankp),rows=candidate_rows,
 guides=9,guideParagraphs=18,exactTextParagraphCandidates=2,
 scope='Nine guides specify where to look during the already observed normal-speed existing-game actions; two exact-text candidates are not adopted. No new game, formula, optimal strategy or winner is asserted.',
 bodyRatioApproved=False,allContinuousSourcePixelsReviewed=False,currentVoiceApproved=False,
 measuredTimelineAdopted=False,humanListening='pending',humanPronunciation='pending',publicRights='pending'))
oldreq=read(BASE/'narration-tts-request-v1.json');oldtts=read(BASE/'narration-tts-execution-v1.json')
protected=[x for x in oldreq['protectedInputs'] if not x['path'].endswith('/project.json')]
protected += [dict(path=x['path'],sha256=x['sha256']) for x in oldtts['results']]
protected += [dict(path=rel(p),sha256=sha(p)) for p in [kp,ep,mp,reviewp,targetreview]]
for x in protected:assert sha(ROOT/x['path'])==x['sha256'],x['path']
requestp=BASE/'observation-candidates-tts-request-v2.json';assert not requestp.exists()
save(requestp,dict(schemaVersion=1,slug='presenting-game-scores',preparedAt=now,pairedWholeTextReview=True,
 overviewPromiseReview=True,scriptReview=rel(reviewp),manifestOverride=rel(mp),protectedInputs=protected,
 queueDir=oldreq['queueDir'],device='cuda:0',cpuThreads=2,batchSize=1,total=11,
 scenes=[dict(id=x['id'],title=x['title'],paragraphs=len(x['lines']),text=' '.join(x['lines']),
  path=out+'/chunks/'+x['id']+'-scene.wav') for x in ks],
 originalTenPcmRegenerated=False,replacementsAdopted=False,allGuideAsrApproved=False,
 policy='Finish the current research checkpoint/validation/done, then one owned cooperative TTS batch; restore the exact original queue on success/failure. No forced kill, suspend or foreign control removal.'))
print(json.dumps(dict(guides=9,exactTextCandidates=2,total=11,request=rel(requestp),originalPcmChanged=False)))
