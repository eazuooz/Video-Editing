"""Save the direct whole-text review and exact complete sentence contexts.

Recognition alternatives are held for independent/joined review, not approved.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, wave, numpy as np
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
execution=read(BASE/'voice-whole-asr-execution-v1.json')
assert execution['exitCode']==0 and execution['actualExitObserved'] and execution['completed']==11
asr=read(BASE/'voice-whole-asr-v1/asr.json'); assert asr['complete'] and len(asr['results'])==11
notes={
 'r01-overview': 'Three complete sentences and all promised steps present. 기여가 is recognized 기어가 at9.26–9.62s; hold phonetic alternative for complete independent second sentence and final mixed context.',
 'r04-evaluation-weights-p2': 'Both complete sentences preserve starting hand, chips/multiplier, and selected cards not necessarily contributing. 없습니다 ending at10.36s present.',
 'r05-events-and-total-p2': 'Both complete sentences and hand versus cumulative versus transient distinction present. 중의 is recognized 중에; hold particle alternative for independent second sentence and complete join.',
 'r07-name-and-unit-p2': 'Both sentences complete, including 말할 수 있죠 at7.66s. The failed decay heuristic is not a content approval; independent full second sentence and joined review still required.',
 'r09-feedback-hierarchy-p2': 'Complete hand calculation, cumulative round and target separation plus stable reading position; 유지됩니다 ending present.',
 'r10-audit-and-close-p2': 'Both requested review sentences present, but a zero-duration 자 plus 스테트리스에서는 at onset are unresolved ASR additions. Hold for padded complete first sentence and complete joined context; do not cut PCM based on this recognition.',
 'r13-observe-action-label-p1': '7/3/6 are numeric normalization of 칠/세/육; selected extra card exclusion, contribution distinction and 보세요 ending complete.',
 'r14-observe-notice-and-record-p1': '560/1327 exactly match spoken five hundred sixty/thirteen hundred twenty-seven; transient not final distinction and 아닙니다 ending complete.',
 'r24-observe-named-fields-clear-start-p1': 'Complete 족보/계산값/라운드 fields and name-purpose distinction; 달라집니다 ending present.',
 'r18-observe-stable-reading-p1': '704/1200 match expected spoken values; reference remains after response and 남습니다 ending present.',
 'r19-observe-reading-audit-p1': 'Diamond marks/response, contribution versus selection and named-value audit all complete, 점검입니다 ending present.'
}
rows=[]
for r in asr['results']:
 assert sha(ROOT/r['sourcePath'])==r['audioSha256']==r['sourceSha256']
 rows.append(dict(id=r['id'],sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],expectedKo=r['expectedKo'],actualWholeText=r['text'],words=r['words'],directReview=notes[r['id']],wholeTextDirectlyCompared=True,completeContextStillRequired=True,currentCompleteVoiceApproved=False))
proof=BASE/'voice-whole-direct-review-v1.json'
save(proof,dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),scope='All eleven current whole recognition texts and word timestamps directly compared; independent context and joined adoption remain pending.',asrPath=(BASE/'voice-whole-asr-v1/asr.json').relative_to(ROOT).as_posix(),asrSha256=sha(BASE/'voice-whole-asr-v1/asr.json'),actualOuterSession=25653,actualOuterExitCode=0,allWholeTextsDirectlyCompared=True,results=rows,recognitionAlternatives=['r01 기여가/기어가','r05 중의/중에','r10 zero-duration 자 and 스테트리스 onset'],currentCompleteVoiceApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending'))
by={r['id']:r for r in asr['results']}
def metric(r,t):
 with wave.open(str(ROOT/r['sourcePath']),'rb') as w:a=np.frombuffer(w.readframes(w.getnframes()),np.int16)
 n=round(t*24000); s=a[max(0,n-120):n+120].astype(float)
 return dict(seconds=t,sample=n,rms=float(np.sqrt(np.mean(s*s))),peak=int(np.max(np.abs(s))),windowSamples=240)
# Quiet PCM gaps were directly compared to both adjacent complete words. Never trim voice.
overview=by['r01-overview']; cuts=[0,110400,319200,528000] #4.600/13.300s
save(BASE/'voice-overview-boundaries-v1.json',dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),sourcePath=overview['sourcePath'],sourceSha256=overview['sourceSha256'],boundariesSamples=cuts,currentWordsAndQuietPcmDirectlyCompared=True,quietMetrics=[metric(overview,4.6),metric(overview,13.3)],adjacentWords=[dict(before='알려줄까요?',beforeEnd=4.4,after='먼저',afterStart=4.8,quietAt=4.6,actualPcmOnsetRisesAfter=4.63),dict(before='보겠습니다.',beforeEnd=12.98,after='그다음',afterStart=13.32,quietAt=13.3,actualPcmOnsetRisesAt=13.32)],allOriginalSamplesPreserved=True))
specs=[
 ('r01-overview','overview-complete-p2',4.6,13.3,'먼저 테트리스의 줄 수와 점수를 구분하고, 발라트로에서 카드 한 장의 기여가 이번 손패와 누적 점수로 이어지는 과정을 보겠습니다.'),
 ('r04-evaluation-weights-p2','weights-complete-last-sentence',7.36,None,'선택한 카드가 모두 점수를 만들지는 않습니다.'),
 ('r05-events-and-total-p2','events-complete-last-sentence',4.06,None,'이번 결과와 누적값, 숫자가 더해지는 중의 중간값을 구분해야 합니다.'),
 ('r07-name-and-unit-p2','names-complete-last-sentence',3.66,None,'회수한 물품 수와 종합 평가 점수도 서로 다른 정보를 말할 수 있죠.'),
 ('r09-feedback-hierarchy-p2','hierarchy-complete-last-sentence',5.34,None,'숫자가 반응하더라도 다시 읽을 위치는 안정적으로 유지됩니다.'),
 ('r10-audit-and-close-p2','audit-complete-leading-sentence',0,4.58,'테트리스에서는 줄 수와 평가 점수, 상대와의 차이를 구분했습니다.'),
 ('r10-audit-and-close-p2','audit-complete-second-sentence',4.58,None,'발라트로에서는 카드의 기여, 이번 손패와 누적 점수, 그 값을 읽는 순서를 확인했죠.'),
 ('r13-observe-action-label-p1','cards-complete-last-sentence',5.68,None,'선택과 기여를 구분해 보세요.'),
 ('r14-observe-notice-and-record-p1','round-complete-last-sentence',5.84,None,'움직이는 중간값은 최종 점수가 아닙니다.'),
 ('r24-observe-named-fields-clear-start-p1','fields-complete-last-sentence',6.12,None,'이름이 다르면 숫자를 읽는 목적도 달라집니다.'),
 ('r18-observe-stable-reading-p1','stable-complete-last-sentence',4.18,None,'계산에 반응하는 숫자가 사라진 뒤에도 비교 기준은 남습니다.'),
 ('r19-observe-reading-audit-p1','diamond-complete-last-sentence',2.68,None,'선택한 카드가 점수에 기여하는지, 어떤 이름의 값을 보고 있는지 확인하는 점검입니다.')
]
inputs=[]
for ident,cid,start,end,text in specs:
 r=by[ident]; s=round(start*24000); e=round(end*24000) if end is not None else r['samples']
 assert 0<=s<e<=r['samples']
 inputs.append(dict(id=cid,originalId=ident,sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],startSample=s,endSample=e,expectedKo=text,zeroPaddingSamplesEachSide=9600,quietStartMetric=metric(r,start) if start else None,quietEndMetric=metric(r,end) if end is not None else None,scope='One complete natural sentence; exact current PCM bytes plus0.4s zero margins, no expected recognizer prompt'))
save(BASE/'voice-contexts-asr-plan-v1.json',dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),wholeDirectReview=proof.relative_to(ROOT).as_posix(),wholeDirectReviewSha256=sha(proof),boundariesDirectlyComparedWithCurrentWordsAndPcm=True,inputs=inputs,automaticApproval=False))
# Explicitly distinguish baseline approvals from every pending revision gate.
cpPath=BASE.parent/'latest-checkpoint.json'; cp=read(cpPath)
cp['baselineHistoricalApprovedGates']={k:cp.get(k) for k in ['finalTimingApproved','finalMixedAsrApproved','pairRendered','allFinalPixels','qa','collected']}
cp.update(recordedAt=datetime.now(timezone.utc).isoformat(),stage='revision-whole-direct-review-contexts-prepared',finalTimingApproved=False,finalMixedAsrApproved=False,pairRendered=False,allFinalPixels=False,qa=False,collected=False,private=False,actualVideoId=None,revisionWholeTextDirectReview=proof.relative_to(ROOT).as_posix(),nextAction='Run twelve complete independent CPU contexts, then read every actual whole context and five complete PCM joins before voice/timing adoption.')
cpPath.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print('All11 whole texts/words directly compared;12 exact complete sentence contexts prepared;3 recognition alternatives remain unapproved.')
