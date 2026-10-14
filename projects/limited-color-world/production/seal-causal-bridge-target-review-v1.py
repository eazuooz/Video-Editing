"""Close the actual targeted ASR session and preserve its unresolved lexical alternatives."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil,os
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
 t=p.with_name(p.name+'.sealing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
sp=BASE/'causal-bridge-targets-asr-execution-v1.json';s=read(sp)
assert s['exitCode']==0 and s['completed']==s['total']==2
assert not psutil.pid_exists(s['pid']) or abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01
stamp=datetime.now(timezone.utc).isoformat()
s.update(actualExitObserved=True,actualOuterSession=88663,actualOuterExitCode=0,actualToolExitObservation='5bd74c',actualExitObservedAt=stamp,sessionId=88663);save(sp,s)
sessionPath=sp.with_name(sp.stem+'.session.json');assert not sessionPath.exists()
save(sessionPath,dict(recordedAt=stamp,sessionId=88663,pid=s['pid'],createTime=s['createTime'],processIdentity=s['processIdentity'],
 actualExitObserved=True,actualExitCode=0,actualToolExitObservation='5bd74c',
 identityEvidenceScope='Worker startup state recorded actual PID/createTime/cmd/cwd. Session association made after actual tool completion; later live-recorder991b46 found it already closed and created no file.',liveCimObservationClaim=False))
ap=BASE/'causal-bridge-targets-asr-v1/asr.json';a=read(ap);assert a['complete'] and len(a['results'])==2
rows=[]
notes=[('Full contrast-check sentence recognized with 밝고→밟고 persisting in whole, padded paragraph and complete-sentence results. Human pronunciation remains unresolved.',['밝고→밟고']),
 ('Full cue-list sentence recognized, but beginning varies from 끝까지 to 마스크까지 across independent decodes. This instability cannot establish the exact spoken 지금까지 or a confirmed omission. 무늬 is correctly recognized in both independent decodes; whole 문이 corrected by context. Human beginning-word review remains unresolved.',['지금까지→끝까지/마스크까지'])]
for r,(note,alts) in zip(a['results'],notes):
 assert sha(ROOT/r['sourcePath'])==r['sourceSha256'] and sha(ROOT/r['contextPath'])==r['contextSha256'] and r['exactSourceSampleBytesMatched']
 rows.append(dict(id=r['id'],expectedKo=r['expectedKo'],expectedEn=r['expectedEn'],actualFullSentence=r['text'],words=r['words'],
  currentPcmSha256=r['sourceSha256'],contextSha256=r['contextSha256'],completeSentenceDirectlyCompared=True,recognitionAlternatives=alts,comparison=note,humanPronunciation='pending'))
rp=BASE/'causal-bridge-targeted-voice-direct-review-v1.json';assert not rp.exists()
save(rp,dict(schemaVersion=1,reviewedAt=stamp,actualSession=88663,actualExitCode=0,actualToolExitObservation='5bd74c',asr=rel(ap),asrSha256=sha(ap),
 allTwoCompleteSentenceTextsDirectlyCompared=True,rows=rows,expectedWasRecognizerPrompt=False,heuristicIsApproval=False,
 current3WholePlus3IndependentPlus2AdaptiveContextsDirectlyCompared=True,currentThreePcmPreserved=True,
 recognitionAlternativesUnresolved=True,humanListening='pending',humanPronunciation='pending',narrationApproved=False,finalMixedAsrApproved=False,
 automaticExtraRecognitionOrPcmRegenerationRequested=False))
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=stamp,stage='current11PCM-measured-and-bounded-text-reviewed',ownedJob=None,
 bridgeWholeAndIndependentTextReviewComplete=True,bridgeAdaptiveCompleteSentenceReviewComplete=True,all11RawPcmSeconds=232.64008333333334,
 bridgeRecognitionAlternativesPending=['밝고→밟고','지금까지→끝까지/마스크까지'],narrationApproved=False,
 nextAction='Preserve all11PCM and source approvals. Inspect two new useful native navigation windows for natural scene gaps, then allocate exact60:40 and measured KOEN/black motion. Final mix/pixels/QA/upload pending.');save(BASE/'latest-checkpoint.json',cp)
print('Whole3+complete3+target2 full texts compared; 11 PCM preserved; lexical/human and final-mix approval remain pending.')
