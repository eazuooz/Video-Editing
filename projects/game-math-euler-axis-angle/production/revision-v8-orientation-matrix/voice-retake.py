"""Explicit selected-paragraph QA candidates; originals remain immutable.

The input is authored only after full source QA and a root resource handoff.
This file is preparation, not an automatic outlier detector or next job.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,random,time
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_retake_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_retake_level_math',H/'voice-render.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def worker(token):
 plan=c.validate();c.lease_worker(token);selection_file=H/'voice-retake-input.json';selection=c.read(selection_file)
 assert selection['approvedScriptSha256']==c.APPROVED and selection['reason']and 1<=len(selection['paragraphs'])<=2
 assert selection['sourceReceiptSha256']==c.sha(c.O/'tts-current.json'),'Read actual full source QA before selecting repairs'
 source=c.read(c.O/'tts-current.json');byid={s['id']:s for s in source['scenes']};script={s['id']:s for s in c.read(H/'voice-input.json')['scenes']}
 c.wait_memory(plan['resources']['tts']['minimumFreeMiB'])
 import numpy as np,soundfile as sf,torch
 from qwen_tts import Qwen3TTSModel
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['tts']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
 tts=c.read(H/'voice-tts-manifest.json')['tts'];model=Qwen3TTSModel.from_pretrained(str(c.R/tts['model']),device_map='cuda:0',dtype=torch.bfloat16)
 prompt=model.create_voice_clone_prompt(ref_audio=str(c.R/tts['reference']),ref_text=(c.R/tts['referenceText']).read_text(encoding='utf8').strip(),x_vector_only_mode=False)
 output=c.O/'retake-candidates.json';done=c.read(output)if output.exists()else dict(revision='orientation-matrix-v8',selectionSha256=c.sha(selection_file),candidates=[])
 assert done['selectionSha256']==c.sha(selection_file)
 for selected in selection['paragraphs']:
  sid,line=selected['scene'],selected['line'];old=byid[sid]['lines'][line-1];text=script[sid]['lines'][line-1]
  assert old['takeSha256']==selected['originalTakeSha256']and hashlib.sha256(text.encode()).hexdigest()==old['textSha256']
  seeds=selected['seeds'];assert 1<=len(seeds)<=2 and len(set(seeds))==len(seeds)
  for attempt,seed in enumerate(seeds,2):
   ident=f'{sid}.L{line:02}.attempt{attempt}';existing=next((x for x in done['candidates']if x['id']==ident),None)
   if existing:
    assert existing['seed']==seed and c.sha(c.R/existing['file'])==existing['sha256'];continue
   file=c.O/'repairs'/f'{sid}.L{line:02}'/(ident+'.wav');file.parent.mkdir(parents=True,exist_ok=True);assert not file.exists()
   random.seed(seed);np.random.seed(seed%(2**32));torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
   began=time.time();print('Selected whole-paragraph candidate',ident,'seed',seed,flush=True)
   audio,rate=model.generate_voice_clone(text=[text],language='Korean',voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=tts['maxNewTokens'])
   raw=np.asarray(audio[0],dtype=np.float32);assert raw.ndim==1 and rate==24000 and len(raw)>0 and np.isfinite(raw).all();sf.write(file,raw,rate,subtype='FLOAT')
   before=v.level_measure(raw,rate,tts['lineLevelEqualization']);gain=float(np.clip(-22-before['speechFrameMedianDbfs'],-12,12));processed=raw*np.float32(10**(gain/20))
   row=dict(id=ident,scene=sid,line=line,attempt=attempt,seed=seed,torchInitialSeed=torch.initial_seed(),file=c.rel(file),sha256=c.sha(file),textSha256=old['textSha256'],
    identitySha256=plan['identitySha256'],originalTake=old['takeFile'],originalTakeSha256=old['takeSha256'],originalSeed='not explicitly set/captured by the original worker; do not claim exact seed reproducibility',
    samples=len(raw),sampleRate=rate,seconds=len(raw)/rate,originalSeconds=(old['endSample']-old['startSample'])/rate,
    actualDurationRatio=len(raw)/(old['endSample']-old['startSample']),sourceSpeed=1,gainDb=gain,before=before,after=v.level_measure(processed,rate,tts['lineLevelEqualization']),
    rawFloatPeak=float(abs(raw).max()),normalizedFloatPeak=float(abs(processed).max()),normalizedSamplesOutsideUnitRange=int(np.sum(abs(processed)>=1)),
    generationParameters=dict(language='Korean',nonStreaming=True,maxNewTokens=tts['maxNewTokens'],batchSize=1),elapsedSeconds=time.time()-began,
    sourcePcmPreserved=True,contentReview='pending actual changed-scene ASR/direct comparison',humanListening='pending',selected=False)
   done['candidates'].append(row);c.save(output,done);print('Candidate complete',ident,'normalized peak',row['normalizedFloatPeak'],flush=True)
   del audio,raw,processed
 done['status']='candidates-only; no current source/scene/ASR selected or overwritten';c.save(output,done)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worker',required=True);x=p.parse_args();worker(x.worker)
