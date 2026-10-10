"""Seal the directly read 12 complete contexts and prepare two full paragraphs.

No expected recognizer prompt, voice approval or process/control mutations.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, wave
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
state = read(BASE/'current-contexts-asr-execution-v1.json')
assert state['actualExitObserved'] and state['actualOuterExitCode'] == state['exitCode'] == 0
assert state['completed'] == state['total'] == 12
asr = read(BASE/'current-contexts-asr-v1/asr.json')
slices = read(BASE/'current-contexts-asr-v1/pcm-slices.json')['slices']
assert asr['complete'] and len(asr['results']) == len(slices) == 12
observations = [
 'Both complete ordered-example/benefit paragraphs match apart from punctuation/spacing; intact ending.',
 'Both complete common-action/contrast/choice paragraphs match apart from punctuation/spacing; intact ending.',
 'Both complete fire/water and condition/space/action design paragraphs match apart from punctuation/spacing.',
 'Complete caution against treating smoke as invulnerability and distinction among appearance, judgment and counterplay are intact. 강한지뿐 is recognized as 강한 짓뿐; pronunciation remains pending.',
 'Both complete useful-strength paragraphs are intact. 가까이 붙어 is again recognized 가까이부터, and 뒤의 as 뒤에; retain human phonetic review pending.',
 'All three complete p2–p4 paragraphs match apart from punctuation/spacing. The independent word clock puts 연결됩니다. at18.96–19.84 and 플레이어 at20.16–20.60, resolving the whole-window timestamp overlap without claiming a PCM repair.',
 'Both complete p2–p3 paragraphs are intact. 뒤섞게 is now recognized correctly; 한 순간의 remains 한순간에. Percentage notation has no changed numerical assertion.',
 'Both complete separated-shot/current-turn paragraphs are intact; 장면이므로 is now recognized correctly. 맞힌/마친, 읽지는/익지는 and 영구/연구 persist; the last complete paragraph will be independently checked again.',
 'Separate boss shot and condition/target/time advice are intact. 구현/구형 persists; the last complete paragraph will be independently checked again.',
 'Both complete repeated-condition and role-preservation paragraphs are intact; 경기의/경기에 remains a particle uncertainty.',
 'Both complete rule-cost/role-sentence paragraphs match apart from punctuation/spacing. 있는가 ending and following 이 are separately timestamped17.80 and18.12; no whole-window overlap remains.',
 'Both complete conclusion paragraphs are intact. 능력치 표 is again recognized 능력 지표; retain human phonetic review pending rather than claim corrected pronunciation.'
]
rows=[]
for i,r in enumerate(asr['results']):
 s=slices[i]
 assert s['id']==r['id'] and s['exactSourceSampleBytesMatched']
 assert sha(ROOT/r['sourcePath'])==r['sourceSha256']
 assert sha(ROOT/r['contextPath'])==r['contextSha256'] and not r['expectedWasRecognizerPrompt']
 rp=BASE/'current-contexts-asr-v1'/(r['id']+'.json')
 rows.append(dict(id=r['id'],resultPath=rel(rp),resultSha256=sha(rp),sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],contextSha256=r['contextSha256'],expectedKo=r['expectedKo'],actualText=r['text'],entireExpectedAndActualRead=True,allWordTimestampsRead=True,completeParagraphs=r['completeParagraphs'],exactSourceSampleBytesMatched=True,recognizedWholeSentenceOmission=False,recognizedWholeSentenceRepetition=False,observation=observations[i],humanPronunciation='pending'))
stamp=datetime.now(timezone.utc).isoformat()
rp=BASE/'current-context-direct-review-v1.json'
assert not rp.exists()
rp.write_text(json.dumps(dict(schemaVersion=1,slug='character-parameters',reviewedAt=stamp,actualOuterSession=51374,actualOuterExitCode=0,allIndependentTextsDirectlyCompared=True,completeContexts=12,completeParagraphs=25,rows=rows,sourcePcmChanged=False,expectedWasRecognizerPrompt=False,currentVoiceApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',automaticApproval=False),ensure_ascii=False,indent=2)+'\n','utf-8')
whole=BASE/'current-whole-direct-review-v1.json'
contexts=[]
for index,start in [(7,19.86),(8,19.19)]:
 r=asr['results'][index]
 with wave.open(str(ROOT/r['sourcePath']),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
  total=w.getnframes(); pcm=w.readframes(total)
 n=round(start*24000)
 b=np.frombuffer(pcm[(n-120)*2:(n+120)*2],dtype='<i2').astype(float)
 rms=float(np.sqrt(np.mean(b*b))); peak=int(np.max(np.abs(b)))
 assert rms<100 and peak<350
 contexts.append(dict(id=r['id'][:2]+'-complete-final-paragraph',sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],startSample=n,endSample=total,zeroPaddingSamplesEachSide=6000,expectedKo=[r['expectedKo'][-1]],completeParagraphs=[3],boundaryEvidence=dict(startSeconds=start,startSample=n,boundary10msRms=rms,boundary10msPeak=peak,displayed10msPcmBinRead=True,fullOriginalEndingRetained=True,wordTimestampsAreRecognizerEstimates=True),purpose='Independent complete final paragraph with multiple complete sentences, checking persistent semantic-word uncertainty without expected recognizer prompting.'))
pp=BASE/'current-targeted-leading-context-plan-v1.json'
assert not pp.exists()
pp.write_text(json.dumps(dict(schemaVersion=1,createdAt=stamp,wholeReview=rel(whole),wholeReviewSha256=sha(whole),contextReview=rel(rp),contextReviewSha256=sha(rp),contextCount=2,contexts=contexts,boundariesDirectlyComparedWithCurrentWordsAndPCM=True,sourcePcmChanged=False,expectedWasRecognizerPrompt=False,automaticApproval=False,humanListening='pending',humanPronunciation='pending'),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(contextReview=rel(rp),completeContexts=12,targetedCompleteParagraphs=2,voiceApproved=False),ensure_ascii=False))
