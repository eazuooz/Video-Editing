"""Preserve all greedy evidence; diagnose unresolved complete contexts with beam5."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]; CPBASE=Path(__file__).parent;BASE=CPBASE/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=read(BASE/'voice-joined-asr-execution-v1.json');assert state['exitCode']==0 and state['actualExitObserved'] and state['completed']==5
asr=read(BASE/'voice-joined-asr-v1/asr.json');assert asr['complete'] and len(asr['results'])==5
notes={
 '04-evaluation-weights':'All original p1/p3 PCM bytes and full new p2 present in correct order. Recognizer drops possessive 의 in retained 점수의 이름, with no missing claim/sentence; human phonetic review retained.',
 '05-events-and-total':'All three paragraphs complete in exact original/new/original order. 중의/중에 particle alternative persists across whole/independent/joined results; human phonetics remain pending.',
 '07-name-and-unit':'All three paragraphs including 있죠 and the retained 어떤 onset are complete. No source sample lost or repeated at the corrected11.20s original boundary.',
 '09-feedback-hierarchy':'All three complete paragraphs and full endings match; no omitted/duplicated clause at joins. Keep current final mixed comparison pending.',
 '10-audit-and-close':'All three paragraphs complete, including coaching conclusion, but 스테트리스 onset persists inside full joined context. It cannot be dismissed solely as a start-of-file zero timestamp; resolve via secondary unprompted diagnostic before technical voice adoption.'
}
rows=[]
for r in asr['results']:
 assert sha(ROOT/r['sourcePath'])==r['sourceSha256']==r['audioSha256']
 rows.append(dict(id=r['id'],sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],expectedKo=r['expectedKo'],actualWholeText=r['text'],words=r['words'],directReview=notes[r['id']],wholeContextDirectlyCompared=True,completeCurrentVoiceApproved=False))
rp=BASE/'voice-joined-direct-review-v1.json';assert not rp.exists()
rp.write_text(json.dumps(dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),asrPath=(BASE/'voice-joined-asr-v1/asr.json').relative_to(ROOT).as_posix(),asrSha256=sha(BASE/'voice-joined-asr-v1/asr.json'),allFiveCompleteJoinedContextsDirectlyCompared=True,allWholeTextsDirectlyCompared=True,allRetainedPcmBytesMatched=True,results=rows,currentCompleteVoiceApproved=False,finalMixedAsrApproved=False,leadingAuditOnsetUnresolved=True,humanListening='pending',humanPronunciation='pending'),ensure_ascii=False,indent=2)+'\n','utf-8')
context=read(BASE/'voice-contexts-asr-v1/asr.json')['results'];by={x['id']:x for x in context}
inputs=[]
for cid in ['audit-complete-leading-sentence','overview-complete-p2','events-complete-last-sentence']:
 x=by[cid];inputs.append(dict(id=cid,sourcePath=x['contextPath'],sourceSha256=x['contextSha256'],expectedKo=x['expectedKo'],originalPcmPath=x['sourcePath'],originalPcmSha256=x['sourceSha256'],zeroPaddingSamplesEachSide=x['zeroPaddingSamplesEachSide']))
x=next(x for x in asr['results'] if x['id']=='10-audit-and-close');inputs.append(dict(id='audit-whole-joined',sourcePath=x['sourcePath'],sourceSha256=x['sourceSha256'],expectedKo=x['expectedKo'],originalPcmPath=x['sourcePath'],originalPcmSha256=x['sourceSha256'],zeroPaddingSamplesEachSide=0))
for x in inputs:assert sha(ROOT/x['sourcePath'])==x['sourceSha256']
plan=BASE/'voice-decoding-asr-plan-v2.json';assert not plan.exists()
plan.write_text(json.dumps(dict(schemaVersion=2,preparedAt=datetime.now(timezone.utc).isoformat(),priorReview=rp.relative_to(ROOT).as_posix(),priorReviewSha256=sha(rp),inputs=inputs,expectedWasRecognizerPrompt=False,automaticApproval=False),ensure_ascii=False,indent=2)+'\n','utf-8')
old=(CPBASE/'review-localized-decoding-v5.py').read_text('utf-8');tail=old[old.index("for key in ['OMP_NUM_THREADS'"):]
tail=tail.replace("cpp=BASE/'latest-checkpoint.json'","cpp=CPBASE/'latest-checkpoint.json'")
tail=tail.replace("unprompted-beam5-localized-CPU-ASR-v5","revision-unprompted-beam5-CPU-ASR-v2")
tail=tail.replace("No new synthesis or research control; measured production and every final gate remain pending.","No new synthesis or research control; measured candidate is prepared only and all final gates remain false.")
prefix='''"""CPU2/GPU0 unprompted beam5 of four unresolved revision contexts; no approval."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,sys,time,traceback
import psutil
ROOT=Path(__file__).resolve().parents[3];CPBASE=Path(__file__).parent;BASE=CPBASE/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
STATE=BASE/'voice-decoding-asr-execution-v2.json';SESSION=STATE.with_name(STATE.stem+'.session.json');LOG=BASE/'voice-decoding-asr-v2.log';DEST=BASE/'voice-decoding-asr-v2'
assert not STATE.exists() and not DEST.exists() and not LOG.exists(),'Inspect actual existing diagnostic; do not repeat.'
resource=read(ROOT/args.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
for mode in ['whole','contexts','joined']:
 s=read(BASE/f'voice-{mode}-asr-execution-v1.json');assert s['exitCode']==0 and s['actualExitObserved']
restored=read(BASE/'research-handoff-verification-v2.json');assert restored['restorationVerified'] and restored['ownedCoordinatorClosed']
for row in read(BASE/'narration-tts-request-v1.json')['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
plan=read(BASE/'voice-decoding-asr-plan-v2.json');reviewp=ROOT/plan['priorReview'];assert sha(reviewp)==plan['priorReviewSha256'] and read(reviewp)['allFiveCompleteJoinedContextsDirectlyCompared']
inputs=plan['inputs'];assert len(inputs)==4
for x in inputs:assert sha(ROOT/x['sourcePath'])==x['sourceSha256']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
'''
worker=CPBASE/'review-revision-voice-decoding-v2.py';assert not worker.exists();worker.write_text(prefix+tail,'utf-8')
print('Five full joins directly compared; four unprompted beam5 inputs prepared. Persistent audit onset is held, all current PCM unchanged.')
