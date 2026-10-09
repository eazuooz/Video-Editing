"""Replace only overview and held audit p2; reuse every other measured PCM/join."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,wave
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def pcm(p):
 with wave.open(str(p),'rb') as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000)
  return w.getnframes(),w.readframes(w.getnframes())
def fresh(p,j):
 assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
whole=B/'voice-whole-direct-review-v3.json';context=B/'voice-contexts-direct-review-v3.json'
assert read(whole)['allWholeTextsDirectlyCompared'] and read(context)['allFiveCompleteSentencesDirectlyCompared']
tts=read(B/'narration-tts-execution-v3.json');assert tts['actualExitObserved'] and tts['exitCode']==0
assert read(B/'research-handoff-verification-v3.json')['restorationVerified']
for r in read(B/'narration-tts-request-v3.json')['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
old=read(B/'preserved-pcm-complete-joins-v1.json');rows=copy.deepcopy(old['scenes'])
for r in rows:assert sha(ROOT/r['path'])==r['sha256']
ko={x['id']:x for x in read(B/'script/narration-v2.ko.json')['scenes']};en={x['id']:x for x in read(B/'script/narration-v2.en.json')['scenes']}
new={x['id']:x for x in tts['results']};bounds=read(B/'voice-repair-boundaries-v3.json')['boundaries']
r=next(x for x in rows if x['id']=='01-overview');s=new['r01-overview'];n,data=pcm(ROOT/s['path'])
r.update(path=s['path'],sha256=s['sha256'],pcmSha256=hashlib.sha256(data).hexdigest(),samples=n,seconds=n/24000,paragraphBoundariesSamples=bounds['r01-overview'],expectedKo=ko[r['id']]['lines'],expectedEn=en[r['id']]['lines'],scope='Whole local overview candidate; exact current measured PCM')
dest=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/complete-pcm-joins-v3';assert not dest.exists();dest.mkdir(parents=True)
sid='10-audit-and-close';s=new['r10-audit-and-close-p2'];nn,newpcm=pcm(ROOT/s['path']);selection=read(B/'pcm-preservation-selection-v1.json')
retained=sorted([x for x in selection['preservedRanges'] if x['id']==sid],key=lambda x:x['paragraph']);assert [x['paragraph'] for x in retained]==[1,3]
parts=[];evidence=[];offset=0;gap=2880
for i,x in enumerate(retained):
 p=ROOT/x['sourcePath'];assert sha(p)==x['sourceSha256'];_,oldpcm=pcm(p);part=oldpcm[x['sourceStartSample']*2:x['sourceEndSampleExclusive']*2]
 assert len(part)==x['samples']*2
 evidence.append({**x,'joinedStartSample':offset,'joinedEndSampleExclusive':offset+x['samples'],'pcmSha256':hashlib.sha256(part).hexdigest()});parts.append(part);offset+=x['samples']
 if i==0:
  p2start=offset+gap;parts.extend([b'\0\0'*gap,newpcm,b'\0\0'*gap]);offset+=gap+nn+gap;p3start=offset
data=b''.join(parts);n=len(data)//2;p=dest/(sid+'-complete-review-join.wav')
with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(data)
assert pcm(p)[1]==data
for x in evidence:assert hashlib.sha256(data[x['joinedStartSample']*2:x['joinedEndSampleExclusive']*2]).hexdigest()==x['pcmSha256']
r=next(x for x in rows if x['id']==sid);r.update(path=rel(p),sha256=sha(p),pcmSha256=hashlib.sha256(data).hexdigest(),samples=n,seconds=n/24000,paragraphBoundariesSamples=[0,p2start,p3start,n],expectedKo=ko[sid]['lines'],expectedEn=en[sid]['lines'],scope='Exact approved original p1/p3 plus complete local repaired p2; all source bytes retained')
assert all(x['expectedKo']==ko[x['id']]['lines'] and x['expectedEn']==en[x['id']]['lines'] for x in rows)
proof=dict(schemaVersion=3,createdAt=datetime.now(timezone.utc).isoformat(),scenes=rows,joins=[dict(id=sid,path=rel(p),sha256=sha(p),samples=n,preservedPieces=evidence,newP2=dict(path=s['path'],sha256=s['sha256'],samples=nn,joinedStartSample=p2start),addedSilenceSamples=gap*2,sourcePcmAltered=False)],totalNarrationSeconds=sum(x['seconds'] for x in rows),priorSelection='projects/presenting-game-scores/production/revision-balatro60-v2/preserved-pcm-complete-joins-v1.json',unchangedPhysicalScenePcmReused=17,otherFourJoinsReassembled=False,allRetainedSourcePcmBytesMatched=True,completeJoinedContextApproved=False,currentCompleteVoiceApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',sourceFilesChanged=False)
fresh(B/'preserved-pcm-complete-joins-v3.json',proof)
fresh(B/'voice-joined-asr-plan-v3.json',dict(schemaVersion=3,wholeDirectReview=rel(whole),wholeDirectReviewSha256=sha(whole),boundariesDirectlyComparedWithCurrentWordsAndPcm=True,inputs=[dict(id=sid,sourcePath=rel(p),sourceSha256=sha(p),samples=n,seconds=n/24000,expectedKo=r['expectedKo'])]))
print(json.dumps(dict(newJoinCount=1,unchangedPcmReused=17,voiceTotalSeconds=proof['totalNarrationSeconds'],joinSeconds=n/24000,p2startSample=p2start,p3startSample=p3start,currentCompleteVoiceApproved=False)))
