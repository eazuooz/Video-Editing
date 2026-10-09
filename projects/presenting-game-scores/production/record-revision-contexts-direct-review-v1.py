"""Direct comparison notes for every complete independent current context."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=read(BASE/'voice-contexts-asr-execution-v1.json');assert state['exitCode']==0 and state['actualExitObserved'] and state['completed']==12
asr=read(BASE/'voice-contexts-asr-v1/asr.json');assert asr['complete'] and len(asr['results'])==12
notes={
 'overview-complete-p2':'Complete second overview sentence retains sequence and ending. 기여가/기어가 persists; human pronunciation and final mixed complete-context comparison pending, not a confirmed audible substitution.',
 'weights-complete-last-sentence':'Entire selected-versus-contributing sentence and 않습니다 ending match.',
 'events-complete-last-sentence':'Entire transient/cumulative distinction and 합니다 ending present. 중의/중에 persists as a particle recognition alternative; not an omitted clause.',
 'names-complete-last-sentence':'Full second sentence including 말할 수 있죠 recognized, confirming content ending beyond failed decay heuristic; full joined context still required.',
 'hierarchy-complete-last-sentence':'Full stable-position sentence and 유지됩니다 ending match.',
 'audit-complete-leading-sentence':'Zero-duration 자 from whole result disappears under independent padded sentence, but 스테트리스 onset persists. Hold onset pending full p1/p2/p3 joined context; do not trim or approve a stutter from ASR alone.',
 'audit-complete-second-sentence':'Entire Balatro contribution/hand/round/reading order and 확인했죠 ending match.',
 'cards-complete-last-sentence':'Entire selection/contribution distinction and 보세요 ending match.',
 'round-complete-last-sentence':'Entire transient is not final statement and 아닙니다 ending match; whitespace normalization only.',
 'fields-complete-last-sentence':'Entire names determine reading purpose statement and 달라집니다 ending match.',
 'stable-complete-last-sentence':'Entire comparison-reference sentence and 남습니다 ending match.',
 'diamond-complete-last-sentence':'Entire contribution/named-value audit and 점검입니다 ending match.'
}
rows=[]
for r in asr['results']:
 assert sha(ROOT/r['sourcePath'])==r['sourceSha256'] and sha(ROOT/r['contextPath'])==r['contextSha256']==r['audioSha256']
 assert r['exactSourceSampleBytesMatched'] and not r['expectedWasRecognizerPrompt']
 rows.append(dict(id=r['id'],originalId=r['originalId'],contextPath=r['contextPath'],contextSha256=r['contextSha256'],sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],expectedKo=r['expectedKo'],actualWholeContext=r['text'],words=r['words'],sourceSliceSamples=[r['startSample'],r['endSample']],zeroPaddingSamplesEachSide=r['zeroPaddingSamplesEachSide'],directReview=notes[r['id']],wholeContextDirectlyCompared=True))
out=BASE/'voice-contexts-direct-review-v1.json';assert not out.exists()
out.write_text(json.dumps(dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),asrPath=(BASE/'voice-contexts-asr-v1/asr.json').relative_to(ROOT).as_posix(),asrSha256=sha(BASE/'voice-contexts-asr-v1/asr.json'),actualOuterSession=28138,actualOuterExitCode=0,allWholeTextsDirectlyCompared=True,all12CompleteSentenceContextsDirectlyCompared=True,allExactCurrentSourceSamplesMatched=True,results=rows,approvalScope='Comparison complete; assembly permitted only to test whole joins. Current complete voice/final mixed/phonetic approvals not granted.',recognitionAlternatives=['overview 기여가/기어가','events 중의/중에','audit 스테트리스 onset'],currentCompleteVoiceApproved=False,completeJoinedContextApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending'),ensure_ascii=False,indent=2)+'\n','utf-8')
print('Twelve complete independent contexts directly compared; three alternatives held for joined/mixed/human review.')
