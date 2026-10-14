"""Separate07b candidate: preserve every original firstfive-paragraph PCM byte."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,wave,numpy as np
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
statep=O/'guide-candidate-voice-asr-execution-v1.json';s=read(statep);assert s['actualOuterExitCode']==0 and s['actualExitObserved'] and s['completed']==1
r=s['results'][0];assert sha(ROOT/r['path'])==r['sha256']
proof=O/'07b-guide-candidate-direct-review-v1.json'
save(proof,dict(reviewedAt=datetime.now(timezone.utc).isoformat(),execution=rel(statep),executionSha256=sha(statep),actualSession=75651,actualCompletion='339d15',fullExpectedText=r['expectedKo'],fullRecognizedText=r['text'],allWordsAndFirstLastRead=True,firstWord=r['chunks'][0],lastWord=r['chunks'][-1],findings=['The previously unrecovered screen-line subject is now explicit: 그린 선은 관찰용 표시입니다 is present, along with camera motion and the separately defined ninety-degree calculation.', '화면에/화면의 and 수학 예/수확예 are recorded recognizer alternatives. This bounded content comparison does not approve exact acoustic pronunciation or human listening.'],candidateContentSufficientForSeparateSplice=True,exactWordingApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,currentSplicedApproved=False,finalMixedApproved=False))
original=ROOT/'shared/output/narration/game-math-orientation-matrices/cross-game-repair-batch-v1/chunks/07b-scene.wav';candidate=ROOT/r['path']
def raw(p):
 with wave.open(str(p),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2);return w.getparams(),w.readframes(w.getnframes())
params,old=raw(original);_,new=raw(candidate);cut=506520;assert len(old)//2==641280 and len(new)//2==180480
signal=np.frombuffer(old,dtype='<i2');e=signal[cut-240:cut+240].astype(float);assert np.max(np.abs(e))<250
# The directly read whole-p5 end20.96/p6 start21.18 gap plus exact low-energy window.
gap=b'\x00\x00'*2400;data=old[:cut*2]+gap+new
folder=ROOT/'shared/output/narration/game-math-orientation-matrices/07b-guide-repair-v1/repair';folder.mkdir(exist_ok=False)
spliced=folder/'07b-last-paragraph-spliced-v1.wav'
with wave.open(str(spliced),'wb') as w:w.setparams(params);w.writeframes(data)
assert raw(spliced)[1]==data and raw(spliced)[1][:cut*2]==old[:cut*2]
seamstart=401160;seamdata=b'\x00\x00'*7200+data[seamstart*2:]+b'\x00\x00'*7200
seam=folder/'07b-spliced-last-two-paragraphs-v1.wav'
with wave.open(str(seam),'wb') as w:w.setparams(params);w.writeframes(seamdata)
assert raw(seam)[1]==seamdata
scriptrefs={}
for lang in ['ko','en']:
 doc=read(O/f'script/cross-game-additions.{lang}.json');guide=read(O/f'script/07b-guide-repair-v1.{lang}.json')['scenes'][0]['lines'][0]
 scene=next(x for x in doc['scenes'] if x['id']=='07b');prior=scene['lines'][:5];scene['lines'][5]=guide;assert scene['lines'][:5]==prior
 doc['status']='current-separate-splice-review-pending';p=O/f'script/cross-game-additions.current-guide-v1.{lang}.json';save(p,doc);scriptrefs[lang]=dict(path=rel(p),sha256=sha(p))
record=O/'07b-last-paragraph-splice-execution-v1.json'
save(record,dict(createdAt=datetime.now(timezone.utc).isoformat(),candidateReview=rel(proof),candidateReviewSha256=sha(proof),originalPath=rel(original),originalSha256=sha(original),candidatePath=rel(candidate),candidateSha256=sha(candidate),originalPrefixEndSample=cut,originalPrefixEndSeconds=cut/24000,observedWordGapSeconds=[20.96,21.18],cutWindowRmsInt16=float(np.sqrt(np.mean(e**2))),cutWindowPeakInt16=int(np.max(np.abs(e))),quietGapSamples=2400,quietGapSeconds=.1,firstFiveParagraphAllBytesPreserved=True,originalFilesOverwritten=False,outputPath=rel(spliced),outputSha256=sha(spliced),samples=len(data)//2,seconds=len(data)/48000,seamPath=rel(seam),seamSha256=sha(seam),seamStartOriginalSample=seamstart,seamSeconds=len(seamdata)/48000,scriptRefs=scriptrefs,currentWholeAndSeamApproved=False,humanListeningApproved=False))
lines=next(x for x in read(ROOT/scriptrefs['ko']['path'])['scenes'] if x['id']=='07b')['lines']
save(O/'guide-spliced-voice-review-plan-v1.json',dict(inputs=[dict(id='07b-spliced-whole',path=rel(spliced),sha256=sha(spliced),expectedKo=lines),dict(id='07b-spliced-seam',path=rel(seam),sha256=sha(seam),expectedKo=lines[-2:])],splice=rel(record),spliceSha256=sha(record),modelExecuted=False,currentMixedApproved=False))
print(json.dumps(dict(seconds=len(data)/48000,prefixSeconds=cut/24000,prefixAllBytesMatched=True,cutRms=float(np.sqrt(np.mean(e**2))),cutPeak=int(np.max(np.abs(e))),modelJobs=0)))
