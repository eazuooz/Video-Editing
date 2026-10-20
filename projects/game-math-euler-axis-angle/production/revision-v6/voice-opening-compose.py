"""Select two approved complete opening contexts and retain original bodies.

CPU only. Raw context, all original41 PCM/ASR and earlier takes are immutable.
The derived ASR is a provenance-preserving offset of independently recognized
fragments, explicitly not a fresh recognition of the composite waveform.
"""
from pathlib import Path
import importlib.util,json,hashlib
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v6_opening_context',H/'voice-opening.py');opening=importlib.util.module_from_spec(spec);spec.loader.exec_module(opening)
v,r,R,P,V,D=opening.v,opening.r,opening.R,opening.P,opening.V,opening.D
spec=importlib.util.spec_from_file_location('v6_opening_quiet',H/'voice-pacing.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
DEST=V/'effective-openings'
def rel(file):return file.relative_to(R).as_posix()
def pcmsha(data):return hashlib.sha256(np.ascontiguousarray(data).tobytes()).hexdigest()
def once(file,data):
 if file.exists():assert v.read(file)==data,'Preserve an existing different composition record'
 else:v.save(file,data)
def tail_measure(data,rate):
 x=np.asarray(data[-round(rate*.02):],dtype=np.float64)/32768
 return dict(last20msRms=float(np.sqrt(np.mean(x*x))),last20msPeak=float(np.max(np.abs(x))),lastSample=int(data[-1]),humanListening='pending')
def main():
 v.selected();plan=v.read(opening.PLAN);opening.preserve_all(plan)
 assert v.read(D/'asr-execution.json')['status']=='complete'
 review_file=D/'direct-review.json';review=v.read(review_file)
 assert review['complete'] and review['contextCount']==2 and review['fullExpectedAndRecognizedTextDirectlyRead']
 take=v.read(D/'retake-current.json');by={x['id']:x for x in take['scenes']}
 DEST.mkdir(exist_ok=True);rows=[]
 for job in plan['jobs']:
  sid=job['id'];item=by[sid];context_file=R/item['file'];asr_file=D/'asr'/f'{sid}.json';asr=v.read(asr_file)
  note=next(x for x in review['scenes'] if x['id']==sid)
  assert note['acceptedForFragmentSelection'] and note['sourceSha256']==v.sha(context_file)==item['sha256']==asr['audio_sha256'] and note['asrSha256']==v.sha(asr_file)
  context,rate=sf.read(context_file,dtype='int16',always_2d=True);old=job['originalScene'];old_file=R/old['file'];original,old_rate=sf.read(old_file,dtype='int16',always_2d=True)
  assert rate==old_rate==24000 and context.shape[1]==original.shape[1]==1
  # Exact reviewed neighboring words, not a forced transcript, identify the
  # context-only prefix sentence and the complete first target word.
  boundary=note['prefixBoundary'];j=boundary['terminalWordIndex'];words=asr['words'];terminal,following=words[j:j+2]
  assert terminal==boundary['terminalWord'] and following==boundary['nextWord']
  low,high=terminal['timestamp'][1],following['timestamp'][0]
  prefix=p.quiet_seam(context[:,0].astype(np.float32)/32768,rate,low,high);assert prefix
  start=prefix['sampleOffset'];assert low<=start/rate<high
  old_asr_file=V/'asr'/f'{sid}.json';old_asr=v.read(old_asr_file);assert old_asr['audio_sha256']==old['sha256']==v.sha(old_file)
  rest=job['originalRestSeam'];old_low,old_high=rest['observedAsrWordGap'];quiet=p.quiet_seam(original[:,0].astype(np.float32)/32768,rate,old_low,old_high)
  assert quiet==rest['quietCandidate'];old_start=quiet['sampleOffset']
  assert all(not (w['timestamp'][0]<old_start/rate<w['timestamp'][1]) for w in old_asr['words'])
  # Keep the entire target tail up to exact sourceEOF; no word or release is
  # cut at the opening's end. EOF's near-zero sample joins the old quiet gap.
  left=context[start:];right=original[old_start:];joined=np.concatenate([left,right],axis=0)
  assert abs(int(left[-1,0]))<=4 and abs(int(right[0,0]))<=4,'A nonzero hard join needs review, not an automatic fade'
  output=DEST/f'{sid}-scene.wav'
  if output.exists():
   observed,sr=sf.read(output,dtype='int16',always_2d=True);assert sr==rate and np.array_equal(observed,joined)
  else:sf.write(output,joined,rate,subtype='PCM_16')
  observed,sr=sf.read(output,dtype='int16',always_2d=True);assert np.array_equal(observed[:len(left)],left) and np.array_equal(observed[len(left):],right)
  new_words=[]
  for word in words[j+1:]:
   a,b=word['timestamp'];assert a>=start/rate and b<=len(context)/rate+.001
   new_words.append(dict(text=word['text'],timestamp=[a-start/rate,b-start/rate]))
  original_suffix=[w for w in old_asr['words'] if w['timestamp'][0]>=old_start/rate]
  for word in original_suffix:
   a,b=word['timestamp'];shift=(len(left)-old_start)/rate
   new_words.append(dict(text=word['text'],timestamp=[a+shift,b+shift]))
  assert all(a['timestamp'][0]<=b['timestamp'][0] for a,b in zip(new_words,new_words[1:]))
  output_asr=DEST/f'{sid}.asr.json';source_hash=v.sha(output)
  fragments=[dict(role='complete-target-opening-lines1-2',file=rel(context_file),sha256=item['sha256'],sourceSampleStart=start,sourceSampleEnd=len(context),destinationSampleStart=0,selectedPcmSha256=pcmsha(left),asrFile=rel(asr_file),asrSha256=v.sha(asr_file)),
   dict(role='unchanged-original-body-lines3-end',file=rel(old_file),sha256=old['sha256'],sourceSampleStart=old_start,sourceSampleEnd=len(original),destinationSampleStart=len(left),selectedPcmSha256=pcmsha(right),asrFile=rel(old_asr_file),asrSha256=v.sha(old_asr_file))]
  derived=dict(scene=sid,audio_sha256=source_hash,text=''.join(w['text'] for w in new_words),words=new_words,alignmentSidecar=True,
   freshCompositeAsrPerformed=False,method='Offset and concatenate recognized words from the exact selected PCM fragments; no script words substituted.',
   fragments=fragments,contextOnlyPrefixExcluded=True,contextBoundaryQuiet=prefix,originalBodyBoundaryQuiet=quiet,sourceScriptChanged=False,humanListening='pending')
  once(output_asr,derived)
  row=dict(id=sid,file=rel(output),sha256=source_hash,samples=len(joined),sampleRate=rate,seconds=len(joined)/rate,asrFile=rel(output_asr),asrSha256=v.sha(output_asr),origin='protected-opening-fragment-composition',
   originalFile=rel(old_file),originalSha256=old['sha256'],originalAsrFile=rel(old_asr_file),originalAsrSha256=v.sha(old_asr_file),fragments=fragments,
   exactSelectedFragmentsEqual=True,compositePcmSha256=pcmsha(joined),prefixNotRepeated=True,openingEofTail=tail_measure(left[:,0],rate),joinSampleDifference=int(right[0,0])-int(left[-1,0]),
   originalBodyFromLine=3,humanListening='pending')
  rows.append(row)
 report=dict(schemaVersion=1,revision='article-flow-v6',status='two-fragment-compositions-ready-for-direct-whole-text-review',
  inputs=dict(contextPlanSha256=v.sha(opening.PLAN),contextDirectReviewSha256=v.sha(review_file),implementationSha256=v.sha(Path(__file__))),scenes=rows,
  original41PcmAndAsrPreserved=True,earlierTakesPreserved=True,sourceScriptChanged=False,newInferenceJobs=0,humanWholeListening='pending')
 once(DEST/'compositions.json',report);opening.preserve_all(plan)
 print('Two exact selected openings + unchanged original bodies saved; whole derived-text review remains required.')
if __name__=='__main__':main()
