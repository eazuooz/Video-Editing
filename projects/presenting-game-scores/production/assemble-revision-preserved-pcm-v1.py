"""Join exact retained PCM with directly reviewed changed passages, once.

These unmixed files are only complete-context ASR inputs, not final approval.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def pcm(p):
 with wave.open(str(p),'rb') as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000)
  return w.getnframes(),w.readframes(w.getnframes())
whole=BASE/'voice-whole-direct-review-v1.json';contexts=BASE/'voice-contexts-direct-review-v1.json'
for p in [whole,contexts]:assert read(p)['allWholeTextsDirectlyCompared']
tts=read(BASE/'narration-tts-execution-v2.json');assert tts['actualExitObserved'] and tts['generationComplete'] and tts['exitCode']==0
assert read(BASE/'research-handoff-verification-v2.json')['restorationVerified']
request=read(BASE/'narration-tts-request-v1.json')
for r in request['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
dest=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/complete-pcm-joins-v1';proof=BASE/'preserved-pcm-complete-joins-v1.json';assert not dest.exists() and not proof.exists()
overview=read(BASE/'voice-overview-boundaries-v1.json');assert overview['currentWordsAndQuietPcmDirectlyCompared']
ko=read(BASE/'script/narration.ko.json');en=read(BASE/'script/narration.en.json');selection=read(BASE/'pcm-preservation-selection-v1.json');baseline=read(ROOT/selection['baselineSelection'])
originalPlan=read(ROOT/'projects/presenting-game-scores/production/final-v1/plan.json')
fresh={x['id']:x for x in tts['results']};changed={'01-overview':'r01-overview','13-observe-action-label':'r13-observe-action-label-p1','14-observe-notice-and-record':'r14-observe-notice-and-record-p1','24-observe-named-fields-clear-start':'r24-observe-named-fields-clear-start-p1','18-observe-stable-reading':'r18-observe-stable-reading-p1','19-observe-reading-audit':'r19-observe-reading-audit-p1'}
joinIds=['04-evaluation-weights','05-events-and-total','07-name-and-unit','09-feedback-hierarchy','10-audit-and-close'];dest.mkdir(parents=True);rows=[];joins=[]
for ks,es in zip(ko['scenes'],en['scenes']):
 ident=ks['id'];assert ident==es['id'] and len(ks['lines'])==len(es['lines']);bounds=None
 if ident in selection['wholePreservedScenes']:
  r=next(x for x in baseline['scenes'] if x['id']==ident);p=ROOT/r['path'];assert sha(p)==r['sha256'];n,data=pcm(p)
  if len(ks['lines'])==3:bounds=originalPlan['paragraphBoundaries'][ident]
  else:bounds=[0,n]
  scope='Whole unchanged baseline PCM'
 elif ident in changed:
  r=fresh[changed[ident]];p=ROOT/r['path'];assert sha(p)==r['sha256'];n,data=pcm(p);bounds=overview['boundariesSamples'] if ident=='01-overview' else [0,n]
  scope='Whole newly reviewed changed scene/guide'
 else:
  assert ident in joinIds;r=fresh['r'+ident+'-p2'];freshPath=ROOT/r['path'];assert sha(freshPath)==r['sha256'];freshN,freshPcm=pcm(freshPath)
  retained=sorted([x for x in selection['preservedRanges'] if x['id']==ident],key=lambda x:x['paragraph']);assert [x['paragraph'] for x in retained]==[1,3]
  pieces=[];pieceProof=[];offset=0;gap=2880 #0.12s natural splice gaps, separate from preserved voice samples
  for index,x in enumerate(retained):
   src=ROOT/x['sourcePath'];assert sha(src)==x['sourceSha256'];_,old=pcm(src);part=old[x['sourceStartSample']*2:x['sourceEndSampleExclusive']*2];assert len(part)==x['samples']*2
   if index==0:
    pieces.append(part);pieceProof.append({**x,'joinedStartSample':offset,'joinedEndSampleExclusive':offset+x['samples'],'pcmSha256':hashlib.sha256(part).hexdigest()});offset+=x['samples'];p2start=offset+gap
    pieces.extend([b'\x00\x00'*gap,freshPcm,b'\x00\x00'*gap]);offset+=gap+freshN+gap;p3start=offset
   else:
    pieces.append(part);pieceProof.append({**x,'joinedStartSample':offset,'joinedEndSampleExclusive':offset+x['samples'],'pcmSha256':hashlib.sha256(part).hexdigest()});offset+=x['samples']
  data=b''.join(pieces);n=len(data)//2;p=dest/(ident+'-complete-review-join.wav')
  with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(data)
  assert pcm(p)[1]==data
  for x in pieceProof:assert hashlib.sha256(data[x['joinedStartSample']*2:x['joinedEndSampleExclusive']*2]).hexdigest()==x['pcmSha256']
  bounds=[0,p2start,p3start,n];scope='Exact original p1/p3 plus whole current changed p2 and two0.12s splice gaps'
  joins.append(dict(id=ident,path=p.relative_to(ROOT).as_posix(),sha256=sha(p),samples=n,preservedPieces=pieceProof,newP2=dict(path=r['path'],sha256=r['sha256'],samples=freshN,joinedStartSample=p2start),addedSilenceSamples=gap*2,sourcePcmAltered=False,completeJoinedContextApproved=False))
 assert len(bounds)==len(ks['lines'])+1 and bounds[0]==0 and bounds[-1]==n and all(a<b for a,b in zip(bounds,bounds[1:]))
 rows.append(dict(id=ident,path=p.relative_to(ROOT).as_posix(),sha256=sha(p),pcmSha256=hashlib.sha256(data).hexdigest(),samples=n,seconds=n/24000,sampleRate=24000,paragraphBoundariesSamples=bounds,expectedKo=ks['lines'],expectedEn=es['lines'],scope=scope,currentCompleteVoiceApproved=False))
save(proof,dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),scenes=rows,joins=joins,totalNarrationSeconds=sum(x['seconds'] for x in rows),wholeChangedVoiceReview=dict(path=whole.relative_to(ROOT).as_posix(),sha256=sha(whole)),independentChangedContextReview=dict(path=contexts.relative_to(ROOT).as_posix(),sha256=sha(contexts)),allRetainedSourcePcmBytesMatched=True,completeJoinedContextApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',sourceFilesChanged=False))
save(BASE/'voice-joined-asr-plan-v1.json',dict(schemaVersion=1,wholeDirectReview=whole.relative_to(ROOT).as_posix(),wholeDirectReviewSha256=sha(whole),boundariesDirectlyComparedWithCurrentWordsAndPcm=True,inputs=[dict(id=x['id'],sourcePath=x['path'],sourceSha256=x['sha256'],samples=x['samples'],expectedKo=x['expectedKo'],seconds=x['seconds']) for x in rows if x['id'] in joinIds]))
print('Exact retained PCM and reviewed changed voice assembled for five complete joined-context ASR inputs; no final approval.')
