"""Seal four directly read beam results; prepare one clearer unapproved guide.

Preserve original thirty paragraphs, all ten original PCM scenes, eleven v3
candidate PCM, two v4 takes and every previous recognition result.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,os,psutil
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
 t=p.with_name(p.name+'.recording');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--outer-exit-code',type=int,required=True);ap.add_argument('--session-id',type=int,required=True);a=ap.parse_args()
stamp=datetime.now(timezone.utc).isoformat();sp=BASE/'localized-decoding-asr-execution-v5.json';state=read(sp)
assert state['exitCode']==a.outer_exit_code==0 and state['completed']==state['total']==4
sessionp=sp.with_name(sp.stem+'.session.json');s=read(sessionp);assert s['sessionId']==a.session_id and s['pid']==state['pid']
try:assert abs(psutil.Process(state['pid']).create_time()-state['createTime'])>=.01
except psutil.NoSuchProcess:pass
state.update(actualExitObserved=True,actualOuterExitCode=0,actualOuterSessionId=a.session_id,actualWorkerAlive=False,actualExitObservedAt=stamp);save(sp,state)
s.update(actualExitObserved=True,exitCode=0,workerExpectedRunning=False,observedAt=stamp);save(sessionp,s)
data=read(BASE/'localized-decoding-asr-v5/asr.json');assert data['complete'] and len(data['results'])==4
prior=read(BASE/'localized-voice-repair-contexts-asr-v4/asr.json')['results'];rows=[]
notes=[
 'Beam5 still begins 점수를 and does not represent 지금은; both complete clauses and ending are otherwise represented.',
 'Beam5 still preserves 점수의 but transcribes 배점표 as 배전표; entire complete paragraph and ending represented.',
 'The complete semantic original lead remains correct. Beam5 still does not represent 지금은 in the complete guide; no audible omission is asserted.',
 'The complete original-head/new-p3 join and all action names remain represented, including 점수의; 배점표 remains 배전표.'
]
for d,old,note in zip(data['results'],prior,notes):
 p=BASE/'localized-decoding-asr-v5'/(d['id']+'.json');assert read(p)==d and not d['expectedWasRecognizerPrompt']
 assert d['decoding']['num_beams']==5 and sha(ROOT/d['sourcePath'])==d['sourceSha256']==d['audioSha256']==old['contextSha256']
 rows.append(dict(id=d['id'],path=rel(p),sha256=sha(p),expectedKo=d['expectedKo'],actualText=d['text'],
  allExpectedAndEntireActualTextDirectlyRead=True,wordsAndFinalSoundDirectlyRead=True,exactCurrentContextPcmMatched=True,
  greedyText=old['text'],beamTextMatchesGreedy=d['text']==old['text'],observation=note,
  noRecognizedWholeSentenceOmission=True,noRecognizedWholeSentenceRepetition=True,noRecognizedInventedGreeting=True))
proofp=BASE/'localized-decoding-direct-review-v5.json';assert not proofp.exists()
save(proofp,dict(schemaVersion=1,reviewedAt=stamp,completeWindowCount=4,rows=rows,allWholeTextsDirectlyCompared=True,
 currentVoiceApproved=False,finalMixedAsrApproved=False,actualSynthesisErrorConfirmed=False,
 humanListening='pending',humanPronunciation='pending',endingHeuristicUsedForApproval=False,
 actualOuterExitCode=0,sessionId=a.session_id,researchProcessOrControlChanges=0,
 conclusion='Different decoding preserves the same onset/term uncertainty. Do not repeat diagnostic recognition or adopt either v4 take. Preserve the better complete v3 evaluation/contribution candidates for later selection; ordinary particle differences remain human pronunciation review.'))
ko='먼저 점수와 줄 수 가운데 무엇을 읽을지 정해 보세요. 이름이 빠진 숫자만으로는 어느 결과가 좋아졌는지 고르기 어렵습니다.'
en='First decide whether to read the score or the number of lines. A number without a name makes it hard to choose which result improved.'
id='24-observe-named-fields-clear-start'
kp=ROOT/'projects/presenting-game-scores/script/named-guide-repair-v6.ko.json';ep=kp.with_name('named-guide-repair-v6.en.json')
assert not kp.exists() and not ep.exists()
save(kp,dict(language='ko',slug='presenting-game-scores',scenes=[dict(id=id,title='이름을 따라 숫자 읽기',lines=[ko])]))
save(ep,dict(language='en',slug='presenting-game-scores',scenes=[dict(id=id,title='Read the named fields',lines=[en])]))
pairp=BASE/'named-guide-paired-direct-review-v6.json';assert not pairp.exists()
save(pairp,dict(schemaVersion=1,reviewedAt=stamp,koPath=rel(kp),koSha256=sha(kp),enPath=rel(ep),enSha256=sha(ep),
 allKoEnDirectlyRead=True,independentGuideCount=1,completeParagraphCount=1,expectedKo=ko,expectedEn=en,
 replacesUnapprovedGuide='17-observe-named-fields; v4 22 candidate held',
 preservation='Original thirty paragraphs and ten PCM scenes are unchanged; approved other guide content and entire second sentence are preserved.',
 change='Rephrase the unapproved first sentence naturally as 먼저 점수와 줄 수 가운데 무엇을 읽을지 정해 보세요. Preserve both the deliberate choice of metric and inability to compare unnamed results; do not edit text to claim an old recording matches.',
 sourceConnection=dict(parentScene='07-name-and-unit',sourceBankId='classic-03',nativeFrames=[2200,2575],
  visibleAction='Normal-speed existing Tetris play with separate SCORE and LINES fields; follow the chosen named metric.',
  claimsNotAdded=['An exact scoring table','Optimal strategy','Final victory']),
 sourceBank='production/batches/sakurai-planning-game-design/proof-presenting-game-scores/source-action-bank-v4.json',
 sourceBankSha256='6317296ed845e2aefb34f45872f880e8f63557a1a0c3ffc44fb87cac52923ab2',
 preparedOnly=True,actualTtsStarted=False,currentVoiceApproved=False,finalMixedAsrApproved=False))
mp=BASE/'named-guide-voice-manifest-v6.json';assert not mp.exists();m=copy.deepcopy(read(ROOT/'projects/presenting-game-scores/project.json'))
m['tts'].update(outputDir='shared/output/narration/presenting-game-scores/qwen3-named-guide-v6',filenameStem='named-guide-v6')
m['paths'].update(script=rel(kp),scriptEn=rel(ep),narration='shared/output/narration/presenting-game-scores/qwen3-named-guide-v6/named-guide-v6.wav',
 captionsKo='shared/output/narration/presenting-game-scores/qwen3-named-guide-v6/named-guide-v6.srt',captionsEn='shared/output/narration/presenting-game-scores/qwen3-named-guide-v6/named-guide-v6.en.srt')
save(mp,m)
previous=read(BASE/'localized-voice-repair-tts-request-v4.json')
protected={r['path']:dict(path=r['path'],sha256=sha(ROOT/r['path'])) for r in previous['protectedInputs']}
for r in previous['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
extra=[kp,ep,mp,pairp,proofp,BASE/'localized-voice-repair-whole-direct-review-v4.json',BASE/'localized-voice-repair-contexts-direct-review-v4.json']
for r in read(BASE/'localized-voice-repair-tts-execution-v4.json')['results']:extra.append(ROOT/r['path'])
for p in extra:protected[rel(p)]=dict(path=rel(p),sha256=sha(p))
rp=BASE/'named-guide-tts-request-v6.json';assert not rp.exists()
save(rp,dict(schemaVersion=1,preparedAt=stamp,slug='presenting-game-scores',manifest=rel(mp),manifestSha256=sha(mp),
 scriptKo=rel(kp),scriptEn=rel(ep),pairedReview=rel(pairp),pairedReviewSha256=sha(pairp),
 scenes=[dict(id=id,text=ko,lines=[ko],path='shared/output/narration/presenting-game-scores/qwen3-named-guide-v6/chunks/'+id+'-scene.wav')],
 protectedInputs=list(protected.values()),totalScenes=1,cpuThreads=2,gpuJobs=1,originalTenChunksRegenerated=False,
 originalThirtyParagraphsPreserved=True,preparedOnly=True,currentVoiceApproved=False,finalMixedAsrApproved=False,
 reason='One unapproved guide is independently rephrased with unchanged meaning after two exact-text takes and complete-context/beam diagnostics. No completed voice/media or whole batch is repeated.'))
print(json.dumps(dict(beamWindowsDirectlyRead=4,namedGuidePrepared=1,request=rel(rp),requestSha256=sha(rp),currentVoiceApproved=False)))
