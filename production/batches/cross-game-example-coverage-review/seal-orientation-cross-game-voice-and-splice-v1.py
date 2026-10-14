"""Seal current diagnostic comparison and create a separate byte-preserving21a candidate."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,wave,numpy as np
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
wholep=O/'cross-game-whole-asr-execution-v2.json';contextp=O/'cross-game-contexts-asr-execution-v2.json';whole=read(wholep);context=read(contextp)
assert whole['actualExitObserved'] and context['actualExitObserved'] and context['actualOuterSession']==64080 and context['actualOuterExitCode']==0 and context['completed']==19
tts=read(O/'narration-cross-game-repair-execution-v1.json')
for x in tts['protectedInputs']+tts['results']:assert sha(ROOT/x['path'])==x['sha256']
for row in context['results']:
 assert sha(ROOT/row['sourcePath'])==row['sourceSha256'] and sha(ROOT/row['contextPath'])==row['contextSha256'] and row['exactSourceSampleBytesMatched']
expected=read(O/'script/cross-game-repair-batch.ko.json')
assert [r['expectedKo'] for r in context['results']]==[line for s in expected['scenes'] for line in s['lines']]
repair=next(r for r in context['results'] if r['id']=='21r-p01');assert repair['text'].strip().startswith('시작 자세와 목표 자세를 안다고') and repair['text'].strip().endswith('안전해지는 것은 아닙니다')
proof=O/'cross-game-whole-and-independent-direct-review-v1.json'
save(proof,dict(reviewedAt=datetime.now(timezone.utc).isoformat(),wholeExecution=rel(wholep),wholeSha256=sha(wholep),independentExecution=rel(contextp),independentSha256=sha(contextp),wholeFiveAndAll19ExpectedCurrentFullTextsCompared=True,all19FirstAndLastWordLandmarksRead=True,actualCompleteContextRead='631b37 exit0',allExactSourcePcmBytesMatched=True,wholeRows=[dict(id=r['id'],expected=' '.join(r['expectedKo']),recognized=r['text']) for r in whole['results']],contextRows=[dict(id=r['id'],expected=r['expectedKo'],recognized=r['text'],firstWords=r['words'][:2],lastWords=r['words'][-2:]) for r in context['results']],findings=['01b and allfive Descenders paragraphs recovered completely.', '07b-p02 independent recovers 탈것; p03–p05 recover observed takeoff/viewpoint/wing comparison and both explicit role lines.', '07b-p06 retains camera-motion, observation-display and separate90degree mathematicalmodel, but exact 화면의 선은 is not recovered by either decoding. Keep this one phrasing held for a bounded alternate decoder; do not infer a confirmed acoustic failure or regenerate the full scene.', '10b-p03 전의/전에 grammatical alternative preserves unplaced-preview meaning; public/human pronunciation approval remains pending. All other SpaceEngineers paragraphs recovered.', '21r recovers 시작 and the entire exact firstsentence in both whole and padded independent currentPCM; safe to prepare a separate splice candidate, then review its whole and seam.'],heldExactPhrasing=['07b-p06'],repair21CandidateCurrentContentApproved=True,spliced21CurrentApproval=False,allNewVoiceExactWordingApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,currentMixedApproved=False,minimumFourGameFinalApproved=False))
original=ROOT/'shared/output/narration/game-math-orientation-matrices/teaching-clarity-additions-v1/chunks/21a-scene.wav';candidate=ROOT/repair['sourcePath']
def raw(p):
 with wave.open(str(p),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2);return w.getparams(),w.readframes(w.getnframes())
params,old=raw(original);_,new=raw(candidate);cut=122400
signal=np.frombuffer(old,dtype='<i2');e=signal[cut-240:cut+240].astype(float)
assert len(old)//2==334080 and len(new)//2==128640
gap=b'\x00\x00'*2400;data=new+gap+old[cut*2:]
folder=ROOT/'shared/output/narration/game-math-orientation-matrices/cross-game-repair-batch-v1/repair';folder.mkdir(exist_ok=False)
spliced=folder/'21a-first-paragraph-spliced-v1.wav'
with wave.open(str(spliced),'wb') as w:w.setparams(params);w.writeframes(data)
_,actual=raw(spliced);assert actual==data and actual[len(new)+len(gap):]==old[cut*2:]
# Whole firsttwo paragraphs around the actual seam, with independent quiet padding.
seamdata=b'\x00\x00'*7200+data[:round((5.36+.1+11.1-5.1)*24000)*2]+b'\x00\x00'*7200
seam=folder/'21a-spliced-first-two-paragraphs-v1.wav'
with wave.open(str(seam),'wb') as w:w.setparams(params);w.writeframes(seamdata)
assert raw(seam)[1]==seamdata
record=O/'21a-first-paragraph-splice-execution-v1.json'
save(record,dict(createdAt=datetime.now(timezone.utc).isoformat(),candidateCurrentReview=rel(proof),candidateCurrentReviewSha256=sha(proof),originalPath=rel(original),originalSha256=sha(original),candidatePath=rel(candidate),candidateSha256=sha(candidate),originalP2OnwardStartSample=cut,originalP2OnwardStartSeconds=5.1,observedWordGapSeconds=[4.9,5.3],cutWindowRmsInt16=float(np.sqrt(np.mean(e**2))),cutWindowPeakInt16=int(np.max(np.abs(e))),quietGapSamples=2400,quietGapSeconds=.1,p2OnwardAllBytesPreserved=True,originalFilesOverwritten=False,outputPath=rel(spliced),outputSha256=sha(spliced),samples=len(data)//2,seconds=len(data)/48000,seamPath=rel(seam),seamSha256=sha(seam),seamSeconds=len(seamdata)/48000,currentWholeAndSeamApproved=False,humanListeningApproved=False))
all21=next(s for s in read(O/'script/additions.ko.json')['scenes'] if s['id']=='21a')['lines']
plan=O/'post-splice-current-voice-review-plan-v1.json'
held=next(r for r in context['results'] if r['id']=='07b-p06')
save(plan,dict(preparedAt=datetime.now(timezone.utc).isoformat(),scope='CPU2GPU0 only: new21a whole and firsttwo completeparagraph seam, plus one held07b-p06 alternatebeam3 diagnostic. Expected text is comparison data, never a recognizer prompt.',inputs=[dict(id='21a-spliced-whole',path=rel(spliced),sha256=sha(spliced),expectedKo=all21,wordTimestamps=True,numBeams=1),dict(id='21a-spliced-seam',path=rel(seam),sha256=sha(seam),expectedKo=all21[:2],wordTimestamps=True,numBeams=1),dict(id='07b-p06-alternate',path=held['contextPath'],sha256=held['contextSha256'],expectedKo=[held['expectedKo']],wordTimestamps=False,numBeams=3)],currentSplice=rel(record),currentSpliceSha256=sha(record),modelExecuted=False))
print(json.dumps(dict(wholeFiveReviewed=True,independent19Reviewed=True,heldExactPhrase='07b-p06',splicedSeconds=len(data)/48000,cutSeconds=5.1,cutRms=float(np.sqrt(np.mean(e**2))),cutPeak=int(np.max(np.abs(e))),p2OnwardBytesMatched=True,wholeSeamApproval=False)))
