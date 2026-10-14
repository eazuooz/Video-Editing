"""Retain complete sentences at directly inspected quiet boundaries, without a fade."""
from pathlib import Path
import os,json,hashlib,datetime,numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):
 assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
ep=B/'part1-protected-onsets-asr-execution-v214.json';e=read(ep)
assert e.get('exitCode')==0 and len(e['completed'])==2 and e.get('endedAt')
review=[]
for x in e['completed']:
 p=ROOT/x['result'];assert sha(p)==x['sha256'];r=read(p)
 review.append(dict(label=x['label'],result=x,expected=r['job']['sources'][0]['ko'],actualFullText=r['text'],actualAllWords=r['chunks'],fullTextAndAllWordTimesDirectlyRead=True,notes=('Preface has initial 자, and zero-duration 먼저; all four literal sentences follow, including 이번 자산 창에서는 and intact 합니다. at23.86–24.22.' if 'size' in x['label'] else 'Preface, 자동차2.60–2.92, first sentence, complete second sentence read. Recognition completeness does not override preserved failed terminal-decay gate.'),humanListening='pending',finalLiteralApproved=False))
write(B/'part1-protected-onsets-direct-review-v219.json',dict(reviewedAt=stamp(),execution={'path':ep.relative_to(ROOT).as_posix(),'sha256':sha(ep)},sessionId=66669,sessionClosedExitCode=0,rows=review,all2CompleteTextsAndWordsRead=True,finalMixedAsrApproved=False,tailFailureStillPreserved=True))
inspection=read(B/'part1-protected-boundary-inspection-v218.json');rr={x['label']:x for x in inspection['rows']}
assert all(x['quietBoundaryObserved'] and x['neighbor20msPeak']<.001 for x in rr.values())
def segment(label,end=None):
 r=rr[label];p=ROOT/r['source']['path'];assert sha(p)==r['source']['sha256'];d,sr=sf.read(p,dtype='int16');assert sr==24000 and d.ndim==1
 a=r['boundarySample'];z=len(d)if end is None else rr[end]['boundarySample'];assert a<z
 return d[a:z],dict(path=r['source']['path'],sha256=r['source']['sha256'],sampleRange=[a,z],pcmInt16Sha256=hashlib.sha256(d[a:z].tobytes()).hexdigest())
folder=ROOT/'shared/output/narration/game-lighting-history-04/part1-literal-onsets-v219';folder.mkdir(exist_ok=False)
segments={};size,sizeref=segment('size-preface');first,firstref=segment('car-preface','car-first-close');second,secondref=segment('car-second-open')
segments['runtime-texture-size']=(size,[sizeref]);segments['geometry-car-material']=(np.concatenate([first,second]),[firstref,secondref])
results=[]
for id,(data,refs)in segments.items():
 p=folder/(id+'-scene.wav');sf.write(p,data,24000,subtype='PCM_16');check,sr=sf.read(p,dtype='int16');assert np.array_equal(check,data)
 v=check.astype('float32')/32768;ratio=float(np.sqrt(np.mean(v[-1200:]**2))/np.sqrt(np.mean(v**2)));tail=np.abs(v[-9600:]);sm=np.convolve(tail,np.ones(120)/120,'same');peak=int(np.argmax(sm));below=np.where(sm[peak:]<sm[peak]*.1)[0];decay=float(below[0]/24)if len(below)else None
 passed=(ratio<=.07 and(decay is None or decay>=70))or(ratio<=.025 and(decay is None or decay>=35));assert passed,(id,ratio,decay)
 results.append(dict(id=id,path=p.relative_to(ROOT).as_posix(),sha256=sha(p),samples=len(data),sampleRate=sr,seconds=len(data)/sr,tailRatio=ratio,tailDecayMs=decay,technicalTailGatePassed=passed,derivedCompleteSentences=refs,temporaryLeadInRemoved=True,fadeApplied=False,tailPaddingAdded=False,asrDirectlyReviewed=False))
selected=read(B/'part1-selected-current-tts-execution-v208.json');newmap={x['id']:x for x in results}
selected['results']=[newmap.get(x['id'],x)for x in selected['results']]
for r in selected['results']:assert sha(ROOT/r['path'])==r['sha256'] and r['technicalTailGatePassed']
request=read(B/'part1-selected-current-tts-request-v208.json')
request.update(preparedAt=stamp(),selectionMethod='35 byte-identical takes plus two protected-onset sentence assemblies at inspected quiet boundaries; no new synthesis',derivedSources=results,literalScript={'path':'projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v175.json','sha256':sha(ROOT/'projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v175.json')},sourceDiagnosticExitCode=1,sourceDiagnosticTailFailurePreserved=True)
request['protectedInputs']+=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}for p in [B/'part1-protected-boundary-inspection-v218.json',B/'part1-protected-onsets-direct-review-v219.json',ep,*[ROOT/r['path']for r in results]]]
rp=B/'part1-selected-current-tts-request-v219.json';write(rp,request)
selected.update(status='37-technical-selected-takes-derived-2-awaiting-five-literal-context-reviews',selectedAt=stamp(),requestSha256=sha(rp),leaseToken=read(B/'part1-protected-onsets-tts-execution-v211.json')['leaseToken'],generationComplete=True,generationCompleteMeaning='All37 selected PCM candidates exist and pass the technical tail gate; the v211 diagnostic synthesis remains failed exit1.',sourceDiagnosticExitCode=1,assemblyExitCode=0,exitCode=0,wholeAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False,allFinalPixelsReviewed=False,uploaded=False)
write(B/'part1-selected-current-tts-execution-v219.json',selected)
proof=dict(assembledAt=stamp(),results=results,joins=[dict(id='geometry-car-material',outputSample=len(first),leftLastInt16=int(first[-1]),rightFirstInt16=int(second[0]),stepAmplitude=float(abs(int(first[-1])-int(second[0]))/32768),completeSentencePausePreserved=True)],original111And35OtherTakesPreserved=True,literalFinalWordsUnchanged=True,currentAsrApproved=False,humanListening='pending',uploaded=False)
write(B/'part1-literal-onset-assembly-v219.json',proof)
print(json.dumps([dict(id=x['id'],samples=x['samples'],seconds=x['seconds'],tail=x['tailRatio'],decay=x['tailDecayMs'])for x in results]))
