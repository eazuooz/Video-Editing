"""Seal explicitly read v311 texts plus exact retained v292 evidence; no new ASR."""
from pathlib import Path
import json, hashlib, copy, os, psutil
from datetime import datetime, timezone
R=Path(__file__).resolve().parents[3]; P=R/'projects/game-lighting-history-04/production'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
rel=lambda p:p.relative_to(R).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def ref(p):return {'path':rel(p),'sha256':sha(p)}
def save(p,j):
 assert not p.exists(), 'Preserve prior review'
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(t,p)
PP=P/'part1-final-input-plan-v309.json';plan=rd(PP)
mix=rd(P/'part1-final-mix-settings-v310.json');execution=rd(P/'part1-current-mixed-asr-execution-v311.json')
assert execution['status']=='complete' and execution['exitCode']==0 and len(execution['results'])==2
w=execution['worker'];assert not psutil.pid_exists(w['pid']) or abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01
assert execution['mixSha256']==mix['wavSha256']==sha(R/mix['wav']) and execution['planSha256']==sha(PP)
reusePath=P/'part1-current-mixed-window-reuse-v310.json';reuse=rd(reusePath)
assert reuse['reusedCount']==35 and reuse['freshCount']==1 and reuse['planSha256']==sha(PP)
oldPath=P/'part1-final-current-mixed-asr-direct-review-v292.json';old=rd(oldPath)
records=[]
for q in reuse['reusedExactWindows']:
 assert q['stereo48kSamplesExact'] and q['oldSampleSha256']==q['currentSampleSha256']
 assert q['currentMixSha256']==mix['wavSha256'] and sha(R/q['oldResult']['path'])==q['oldResult']['sha256']
 assert q['oldDirectReviewFile']==ref(oldPath)
 row=copy.deepcopy(q['oldDirectReview']);assert row['expectedParagraphsAndFullActualTextDirectlyRead'] and row['allWordTimestampsDirectlyRead']
 assert row['window']['expectedKo']==q['window']['expectedKo']
 assert sha(R/row['directReviewEvidence']['path'])==row['directReviewEvidence']['sha256']
 row.update(currentMixSamplesExact=True,reusedExactRecognition=True,currentStereoSampleSha256=q['currentSampleSha256'],currentExactReuse=ref(reusePath))
 records.append(row)
freshPath=P/'part1-current-mixed-fresh-direct-review-v312.json'
fresh=[]
observations={
 'whole-03': 'All six expected paragraphs and every257 word timestamp were directly read. At69.32-69.98 the chunked recognizer invents 전국의 모든 인물이 이, then jumps to87.00 and omits the streaming closing sentence and beginning of UV-stack paragraph. This is recognizer evidence, not a PCM claim. The exact retained stereo48k artifact-context-texture-streaming-input independently includes all three resource/streaming/UV paragraphs once, including 둘 다 필요한 부분...작업은 다릅니다 and 그래프...스택은 함께 묶을 수 있는 읽기 작업과 연결된 개념입니다. Fresh independent-vt-direction-neighbours independently includes the entire UV paragraph and corrected VT direction and tile paragraph. Corrected guide appears once at101.98-117.16; last tile ending at141.56. 이름의/이름에, 맞습니다/맡습니다, 앞에/앞의, 쉐이더/셰이더, 여기에/여기의 remain human pronunciation/particle variants.',
 'independent-vt-direction-neighbours': 'All three complete expected paragraphs and all130 word timestamps directly read, ending65.68. UV-stack paragraph0-25.14 is complete; corrected conversion paragraph26.10-41.04 says ordinary textures to virtual textures, affected textures/materials and matching reader inputs exactly once; tile/border paragraph42.18-65.68 is complete. No invented greeting, missing sentence, repeated sentence or time reversal. The0.02s 읽습니다/여기서는 word-alignment overlap and punctuation differences do not repeat speech. 여기에/여기의 retained for human pronunciation review.'}
for q in execution['results']:
 dest=R/q['path'];assert sha(dest)==q['sha256'];j=rd(dest)
 assert j['mixSha256']==mix['wavSha256'] and j['planSha256']==sha(PP) and j['expectedTextUsedAsPrompt'] is False
 fresh.append({'label':q['label'],'path':q['path'],'sha256':q['sha256'],'window':j['window'],'fullActualText':j['text'],
  'expectedParagraphsAndFullActualTextDirectlyRead':True,'allWordTimestampsDirectlyRead':True,'wordCount':len(j['words']),
  'observedResolution':observations[q['label']],'recognitionOnlyConcernsResolvedByCompleteContexts':True,'humanWholeListening':'pending','humanPronunciation':'pending'})
save(freshPath,{'reviewedAt':stamp(),'execution':ref(P/'part1-current-mixed-asr-execution-v311.json'),'records':fresh,
 'currentMixSha256':mix['wavSha256'],'planSha256':sha(PP),'humanWholeListening':'pending','humanPronunciation':'pending'})
for row in fresh:
 records.append({**row,'currentMixSamplesExact':True,'reusedExactRecognition':False,'directReviewEvidence':ref(freshPath)})
assert len(records)==37 and len({r['label'] for r in records})==37
assert sum(r['label'].startswith('whole-') for r in records)==11
pcmPath=P/'part1-final-pcm-preservation-v310.json';pcm=rd(pcmPath)
assert pcm['allSelectedPcmValuesExact'] and pcm['allOriginalChapterSamplesPartitionedOnce'] and pcm['allOtherNormalized48kSamplesExact']
approval={**{k:copy.deepcopy(v) for k,v in old.items() if k not in ['records','reviewedAt','pcmPreservation','freshDirectReview','windowReuse']},
 'reviewedAt':stamp(),'records':records,'currentMixSha256':mix['wavSha256'],'planSha256':sha(PP),
 'mainWindows':30,'additionalCompleteContexts':7,'freshCurrentWindows':2,'bitExactReusedWindows':35,
 'windowReuse':ref(reusePath),'freshDirectReview':ref(freshPath),'pcmPreservation':ref(pcmPath),'previousDirectReview':ref(oldPath),
 'all37CurrentMixWindowSamplesExact':True,'allWholeAndIndependentTextsDirectlyCompared':True,'allWordEndingsAndTimestampsCompared':True,
 'allObservedRecognitionConcernsResolved':True,'noRemainingContentFailures':True,'finalMixedAsrApproved':True,
 'currentWhole03Concern':observations['whole-03'],'technicalScope':'Private technical sentence-coverage review; human listening and pronunciation remain pending. No heuristic-only approval.',
 'allFinalPixelsReviewed':False,'qaApproved':False,'uploaded':False}
approval.pop('all36CurrentMixWindowSamplesExact',None)
save(P/'part1-final-current-mixed-asr-direct-review-v312.json',approval)
semOldPath=P/'part1-semantic-caption-review-v291.json';semOld=rd(semOldPath)
oldPlan=rd(P/'part1-final-input-plan-v288.json');previous={r['id']:r for r in oldPlan['paragraphs']}
for r in plan['paragraphs']:
 if r['id']!='texture-dependent-conversion':assert r['ko']==previous[r['id']]['ko'] and r['en']==previous[r['id']]['en']
selected=rd(P/'part1-vt-direction-direct-review-v309.json');changed=next(r for r in plan['paragraphs'] if r['id']=='texture-dependent-conversion')
assert (changed['ko'],changed['en'])==(selected['ko'],selected['en'])
save(P/'part1-semantic-caption-review-v312.json',{'reviewedAt':stamp(),'planSha256':sha(PP),'approved':True,'manualSemanticReview':True,
 'unchanged76ParagraphsExact':True,'previous76DirectReview':ref(semOldPath),'changedParagraph':changed,'changedDirectReview':ref(P/'part1-vt-direction-direct-review-v309.json'),
 'observation':'Independent KO/EN express ordinary→virtual conversion and the same texture/material dependency and shader-reader agreement. Timing uses four matching complete sentences. Source Convert to Virtual Texture and Convert To VT Textures dialog were directly observed; the earlier opposite-direction claim is historical and rejected.',
 'paragraphCount':77,'allEncodedPixelsReviewed':False,'humanWholeListening':'pending','humanPronunciation':'pending'})
print(json.dumps({'currentWindows':37,'fresh':2,'exactReuse':35,'mixedSentenceCoverageApproved':True,'finalPixelsApproved':False}))
