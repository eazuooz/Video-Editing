"""Seal the agent's complete direct comparison only after actual worker exit.

This checks hashes/identities; it does not infer language quality from endings
or previous unmixed approval, and it cannot approve human hearing or rights.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--outer-exit-code',type=int,required=True);ap.add_argument('--exit-chunk',required=True);args=ap.parse_args()
assert args.outer_exit_code==0
sp=R/'current-mixed-contexts-asr-execution-v2.json';s=read(sp)
assert s['pid']==58748 and s['createTime']==1791662021.0094805 and s['exitCode']==0 and s['completed']==s['total']==66
assert not psutil.pid_exists(s['pid']), 'Read actual CIM identity before handling any reused PID.'
side=sp.with_name(sp.stem+'.session.json');session=read(side)
assert session['sessionId']==79003 and session['pid']==s['pid'] and session['createTime']==s['createTime']
manual=read(R/'current-mixed-context-direct-review-complete-v1.json')
assert manual['reviewedCount']==66 and manual['eachFullExpectedKoEnAndRecognizedTextAndEveryWordRowDirectlyRead']
assert manual['all66DirectlyCompared'] and manual['currentMixedContentReviewPassed'] and not manual['unresolvedContentOmissionsOrRepetitions']
findings={v['id']:v for v in manual['findings']};assert len(findings)==66
assert set(findings)=={v['id'] for v in s['results']}
whole=read(R/'current-mixed-whole-asr-direct-review-v1.json');assert whole['all14WholeTextsDirectlyCompared'] and len(whole['rows'])==14
mix=read(R/'current-mix-execution-v1.json')
assert mix['actualExitCode']==0 and s['mixAacSha256']==whole['mixAacSha256']==mix['mixAacSha256']==manual['currentMixAacSha256']
assert s['decodedAacSha256']==whole['decodedAacSha256']
assert sha(ROOT/mix['mixAac'])==mix['mixAacSha256']
protected=read(R/'narration-tts-waiting-v1.json')['protectedInputs']
for p in protected:assert sha(ROOT/p['path'])==p['sha256']
contexts=[]
for v in s['results']:
 p=R/f'current-mixed-contexts-asr-v1/{v["id"]}.json';assert read(p)==v
 assert v['expectedWasRecognizerPrompt']==False and v['exactSourceStereoPcmBytesMatched'] and v['independentCompleteSentence']
 assert sha(ROOT/v['contextPath'])==v['contextSha256']
 contexts.append(dict(id=v['id'],path=p.relative_to(ROOT).as_posix(),sha256=sha(p),
  contextPath=v['contextPath'],contextSha256=v['contextSha256'],sourceSha256=v['sourceSha256'],
  expectedKo=v['expectedKo'],expectedEn=v['expectedEn'],recognizedText=v['text'],
  fullTextAndEveryWordRowDirectlyRead=True,finding=findings[v['id']]['finding'],humanPronunciationApproved=False))
for v in whole['rows']:assert sha(ROOT/v['path'])==v['sha256'] and v['allFullTextsAndWordsDirectlyRead']
dest=R/'current-mixed-complete-direct-review-v1.json';assert not dest.exists()
now=datetime.now(timezone.utc).isoformat()
session.update(actualOuterExitCode=0,actualExitToolChunk=args.exit_chunk,workerCurrentlyAlive=False,observedAt=now);save(side,session)
s.update(actualOuterExitCode=0,actualExitObserved=True,actualExitToolChunk=args.exit_chunk);save(sp,s)
save(dest,dict(schemaVersion=1,reviewedAt=now,currentMixedContentReviewPassed=True,
 all14WholeAnd66IndependentContextsDirectlyCompared=True,wholeCount=14,independentCount=66,
 wholeEvidence=whole['rows'],independentEvidence=contexts,
 wholeOverlapResolution=manual['wholeOverlapResolution'],humanPronunciationFindings=manual['humanPronunciationFindings'],
 unresolvedContentOmissionsOrRepetitions=[],exactWordPronunciationApproved=False,
 mixAacSha256=s['mixAacSha256'],decodedAacSha256=s['decodedAacSha256'],mixWavSha256=s['mixWavSha256'],
 actualSession=79003,actualOuterExitCode=0,actualExitToolChunk=args.exit_chunk,workerCurrentlyAlive=False,
 sourceExecution=sp.relative_to(ROOT).as_posix(),sourceExecutionSha256=sha(sp),all26ProtectedInputsUnchanged=True,
 expectedWasRecognizerPrompt=False,originalPcmRegenerated=0,humanListeningApproved=False,
 humanPronunciationApproved=False,publicRightsApproved=False,allFinalPixelsApproved=False,researchManipulations=0))
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now,stage='current-mixed80-contexts-direct-review-complete; measured-captions-pair-pending',
 currentMixedContentReviewPassed=True,currentMixedReview=dest.relative_to(ROOT).as_posix(),allFinalPixelsApproved=False,qaApproved=False,
 currentDuplicateReview='projects/motion-sickness-games/production/revision-teaching-clarity-v1/inventory-change-direct-review-v7.json',
 ownedJob=dict(pid=s['pid'],createTime=s['createTime'],sessionId=79003,exitCode=0,workerCurrentlyAlive=False,state=sp.relative_to(ROOT).as_posix()),
 next='Prepare measured fixed captions and chapters; refresh duplicate/resources before the one guarded pair worker, then directly review all final pixels and continuous flow.')
save(R/'latest-checkpoint.json',cp)
B=Path(__file__).resolve().parent;qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
q['execution'].update(currentSlug='motion-sickness-games',stage=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next'])
next(v for v in q['items'] if v['slug']=='motion-sickness-games').update(status=cp['stage'],currentMixedAudioReview=dest.relative_to(ROOT).as_posix())
q['updatedAt']=now;assert qp.read_text('utf-8-sig')==raw;save(qp,q)
print(json.dumps(dict(currentMixedContentReviewPassed=True,whole14=True,independent66=True,humanListeningApproved=False,finalPixelsApproved=False)))
