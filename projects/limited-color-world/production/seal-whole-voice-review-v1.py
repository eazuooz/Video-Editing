"""Seal directly read whole texts and prepare independent complete paragraphs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
 t=p.with_name(p.name+'.sealing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
sp=BASE/'current-whole-asr-execution-v1.json';state=read(sp);session=read(BASE/'current-whole-asr-execution-v1.session.json')
assert state['exitCode']==0 and state['completed']==state['total']==8 and session['sessionId']==62160
assert not psutil.pid_exists(state['pid']) or abs(psutil.Process(state['pid']).create_time()-state['createTime'])>.01
state.update(actualExitObserved=True,actualOuterSession=62160,actualOuterExitCode=0,actualToolExitObservation='391710',actualExitObservedAt=datetime.now(timezone.utc).isoformat());save(sp,state)
session.update(actualExitObserved=True,actualExitCode=0,actualToolExitObservation='391710');save(BASE/'current-whole-asr-execution-v1.session.json',session)
asrp=BASE/'current-whole-asr-v1/asr.json';asr=read(asrp);assert asr['complete'] and len(asr['results'])==8
ko=read(ROOT/'projects/limited-color-world/script/narration.ko.json')
en=read(ROOT/'projects/limited-color-world/script/narration.en.json')
notes={
 '01-overview':('All four sentences/3paragraphs, central question, three examples/order, first-house link recognized. Only spacing/punctuation differences.',[]),
 '02-contours':('Full fills/black boundaries/retained structure and diagram contrast recognized, including entire final “따라갈 수 있습니다.”. Tail heuristic .119 is not pronunciation approval.',[]),
 '03-pattern-and-erasing':('All claims and hypothetical-device qualification recognized; alternatives 빗급/화면에/집에 against 빗금/화면의/집의 require independent context and human pronunciation review. Entire final 예시입니다 recognized.', ['빗금→빗급','화면의→화면에','집의→집에']),
 '04-height-and-motion':('All rise/bounce, different hues, height/top/motion cues and compression-diagram sentences recognized in order. Full final 만드는 겁니다 recognized.',[]),
 '05-state-not-hue':('Full paint-shortens/erase-tall separate-shot and nonpermanent-state claims recognized. 높아지므로→높아짐으로 is an inflection recognition alternative, retained for context/human review.', ['높아지므로→높아짐으로']),
 '06-route-information':('All foreground cues, decorative occlusion warning and design order recognized. Initial 꽃→가스꽃 and 차이에→차이의 are unresolved recognition alternatives; inspect complete first/last paragraphs independently. Entire final 정리하는 겁니다 recognized.', ['꽃→가스꽃','차이에→차이의']),
 '07-local-contrast':('All local-circle scope, lightness vs darkness warning and diagram comparison recognized. Not global illumination or universal readability. Full final 함께 설계해야 합니다 recognized.',[]),
 '08-check-and-conclusion':('All preview limits, actual-play test, cue combination and conclusion recognized; 색인지 spacing is not a new device or omitted claim. Full final 설계해 보세요 recognized.',[])}
rows=[]
for k,e,r in zip(ko['scenes'],en['scenes'],asr['results']):
 assert k['id']==e['id']==r['id'] and r['expectedKo']==k['lines'] and sha(ROOT/r['sourcePath'])==r['sourceSha256']
 note,alts=notes[k['id']]
 rows.append(dict(id=k['id'],expectedKo=k['lines'],expectedEn=e['lines'],actualWholeText=r['text'],
     sourcePath=r['sourcePath'],currentPcmSha256=r['sourceSha256'],seconds=r['seconds'],allThreeParagraphsDirectlyCompared=True,
     omissionOrRepeatedSentenceDetected=False,recognitionAlternatives=alts,comparison=note,lastWords=r['words'][-5:],
     independentContextApproved=False,humanPronunciation='pending'))
review=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),wholeAsr=rel(asrp),wholeAsrSha256=sha(asrp),
     actualSession=62160,actualExitCode=0,actualToolExitObservation='391710',allWholeTextsDirectlyCompared=True,
     completeExpected24ParagraphsRead=True,currentPcmHashesMatched=True,expectedWasRecognizerPrompt=False,
     heuristicIsApproval=False,endingOnlyApproval=False,rows=rows,independentContextsApproved=False,
     narrationApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',
     nextAction='Transcribe all24 full independent paragraphs from exact currentPCM with200ms zero padding eachside. Directly compare all complete texts and recognition alternatives; do not regenerate or grant pronunciation approval from an ending heuristic.')
rp=BASE/'current-whole-voice-direct-review-v1.json';assert not rp.exists();save(rp,review)
# Boundaries are directly located between the last complete word of paragraph
# and the first word of the next paragraph in the read current whole word list.
bounds=[[0,5.97,13.38,21.92],[0,7.02,12.18,20.8],[0,8.5,14.85,25.92],
        [0,9.69,17.45,25.52],[0,6.88,16.25,24.56],[0,9.05,18.88,27.040041666666667],
        [0,8.12,17,25.2],[0,9.6,20.94,28.56]]
contexts=[]
for k,e,r,bs in zip(ko['scenes'],en['scenes'],asr['results'],bounds):
 with wave.open(str(ROOT/r['sourcePath']),'rb') as w:
  assert w.getframerate()==24000 and w.getnchannels()==1 and w.getsampwidth()==2
  assert w.getnframes()==r['sourceSamples'];full=w.readframes(w.getnframes())
 samples=[round(b*24000) for b in bs];assert samples[0]==0 and samples[-1]==r['sourceSamples']
 assert sum(samples[i+1]-samples[i] for i in range(3))==r['sourceSamples']
 for i in range(3):
  a,b=samples[i:i+2];words=[x for x in r['words'] if x['timestamp'][0]>=bs[i]-.01 and x['timestamp'][0]<bs[i+1]-.001]
  assert words and words[-1]['text'].strip()[-1] in '.?!'
  assert all(x['timestamp'][1] is not None and x['timestamp'][1]<=bs[i+1]+.001 for x in words)
  pcm=full[a*2:b*2];assert len(pcm)==(b-a)*2
  contexts.append(dict(id=k['id']+f'-p{i+1:02}',sceneId=k['id'],paragraph=i+1,
     sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],startSample=a,endSample=b,
     startSeconds=a/24000,endSeconds=b/24000,seconds=(b-a)/24000,
     expectedKo=[k['lines'][i]],expectedEn=[e['lines'][i]],wholeRecognizedContext=''.join(x['text'] for x in words).strip(),
     wholeFirstWord=words[0],wholeLastWord=words[-1],zeroPaddingSamplesEachSide=4800,
     partitionPcmSha256=hashlib.sha256(pcm).hexdigest(),completeOriginalParagraph=True,
     preservesEveryOriginalPcmSampleAcrossScenePartition=True,boundaryScope='Complete-word gap and exact source samples; independent ASR partition only, not approved final timeline.'))
plan=dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),wholeReview=rel(rp),wholeReviewSha256=sha(rp),
     currentWholeAsrSha256=sha(asrp),boundariesDirectlyComparedWithCurrentWordsAndPCM=True,
     exactSamplePartitionPreservesAll8OriginalPcm=True,contexts=contexts,total=24,
     independentRecognitionCompleted=False,automaticApproval=False,humanPronunciation='pending')
pp=BASE/'current-independent-context-plan-v1.json';assert not pp.exists();save(pp,plan)
print(json.dumps(dict(whole8DirectlyRead=True,actualExit=0,paragraphContexts=24,allPcmSamplesPreserved=True,narrationApproved=False),ensure_ascii=False))
