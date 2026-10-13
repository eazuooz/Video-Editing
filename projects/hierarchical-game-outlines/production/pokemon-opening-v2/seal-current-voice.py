from pathlib import Path
import json,hashlib,datetime,copy,re,psutil
import numpy as np,soundfile as sf
P=Path(__file__).resolve().parent;R=P.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (P/'voice-current-inputs.json').exists()
a=read(P/'voice-repair08-asr.json');assert a['exitCode']==0
try:assert abs(psutil.Process(a['pid']).create_time()-a['createTime'])>.01
except psutil.NoSuchProcess:pass
norm=lambda s:re.sub(r'[^가-힣a-zA-Z0-9]','',s).lower()
assert norm(a['actual'])==norm(a['expected'])
first=P/'generated-narration/chunks/08p01-scene.wav';second=P/'repair08-narration/chunks/08p01s02-scene.wav'
x,sr=sf.read(first,dtype='int16');y,yr=sf.read(second,dtype='int16');assert sr==yr==24000 and sha(second)==a['sourceSha256']
cut=73920;z=np.concatenate([x[:cut],y]);folder=P/'current-generated-narration';folder.mkdir()
dest=folder/'08p01-scene.wav';sf.write(dest,z,sr,subtype='PCM_16');check,_=sf.read(dest,dtype='int16');assert np.array_equal(check[:cut],x[:cut]) and np.array_equal(check[cut:],y)
old=read(P/'voice-asr-v1.json');current=copy.deepcopy(old);current.update(status='composite-current-approved-regions',createdAt=now(),scope='Four unchanged whole ASR results plus byte-exact retained first sentence and independently transcribed replacement second sentence. Full current mix ASR follows.',humanListening=False)
row=next(r for r in current['results'] if r['id']=='08p01');firstwords=[w for w in row['words'] if w['timestamp'][1]<=3.08]
assert norm(''.join(w['text'] for w in firstwords))==norm('이 방법은 게임 기획서에만 쓰이지 않습니다.')
words=copy.deepcopy(a['words'])
for w in words:w['timestamp']=[round(t+3.08,6) for t in w['timestamp']]
line='이 방법은 게임 기획서에만 쓰이지 않습니다. '+a['expected']
row.update(path=dest.relative_to(R).as_posix(),sha256=sha(dest),expected=line,actual=''.join(w['text'] for w in firstwords)+a['actual'],words=firstwords+words,directReview=True,provenance=['voice-asr-v1.json first sentence','voice-repair08-asr.json complete second sentence'])
inputs=read(P/'voice-execution-v1.json')['completed'];inputs=copy.deepcopy(inputs)
g=next(r for r in inputs if r['key']=='08p01-scene');g.update(path=dest.relative_to(R).as_posix(),samples=len(z),seconds=len(z)/sr,sha256=sha(dest))
for r in inputs:assert sha(R/r['path'])==r['sha256']
for lang in ['ko','en']:
 f=P/f'narration.{lang}.json';raw=f.read_bytes();backup=P/f'narration-before-sentence-repair.{lang}.json';assert not backup.exists();backup.write_bytes(raw)
 j=read(f);sc=next(s for s in j['scenes'] if s['id']=='08')
 sc['lines'][0]=line if lang=='ko' else 'This method is not limited to game design documents. You can add detailed explanations to video topics, or organize study material and questions.'
 assert not re.search('사쿠라이|마사히로|Sakurai|桜井',json.dumps(j,ensure_ascii=False),re.I)
 write(f,j)
write(P/'voice-current-inputs.json',dict(at=now(),completed=inputs,sourceExecution='voice-execution-v1.json',repairExecution='voice-repair08-execution-v1.json',unchangedFirstSentenceSamples=cut,unchangedFirstSentenceByteExact=True,secondSentenceByteExact=True,new08Duration=len(z)/sr,repairAsrSession=17164,repairAsrCompletion='b2d1fd',repairAsrOuterExit=0,repairAsrWorkerDead=True))
write(P/'voice-current-asr.json',current)
write(P/'voice-direct-review.json',dict(at=now(),generatedAudioCompleteForEditing=True,currentInputsSha256=sha(P/'voice-current-inputs.json'),currentAsrSha256=sha(P/'voice-current-asr.json'),completeTextsRead=['01','01a','02p02','07p01','08p01'],notes={'01':'complete text; spacing only','01a':'complete text; 아래의/아래에 particle variant, no lost claim','02p02':'complete text; 안의/안에 particle variant','07p01':'complete text including 목적이 다릅니다; heuristic is not the approval','08p01':'first sentence byte exact; new second sentence actual ASR fully matches expected 더하거나 through 있습니다'},originalAmbiguousTakePreserved=True,wholeMixPending=True,humanListening=False,pronunciationApproved=False,publicRightsApproved=False))
s=read(P/'script-review.json');s.update(koSha256=sha(P/'narration.ko.json'),enSha256=sha(P/'narration.en.json'),boundedRepair='08p01 second sentence, equivalent independent wording; voice-repair08-reason.json');write(P/'script-review.json',s)
cp=read(P/'latest-checkpoint.json');cp.update(updatedAt=now(),stage='current-voice-reviewed-timeline-next',worker=None,newPcm=True,next='Build measured timeline once, then render only two new document scenes.');write(P/'latest-checkpoint.json',cp)
print(json.dumps(dict(duration=len(z)/sr,retainedFirstSamples=cut,seamLast10msPeak=int(np.max(np.abs(x[cut-240:cut].astype(np.int32)))),repairFirst10msPeak=int(np.max(np.abs(y[:240].astype(np.int32))))),ensure_ascii=False))
