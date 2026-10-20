"""One a09 opening repair; complete context, unchanged tail PCM and raw caches."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,time
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_opening_review',H/'voice-review.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
s=importlib.util.spec_from_file_location('v7_opening_quiet',H/'audio-prepare.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
F=c.O/'repair-a09-attempt3';F.mkdir(exist_ok=True)
def generate(token):
 plan=c.validate(preserve_pcm=True);c.lease_worker(token);c.wait_memory(plan['resources']['tts']['minimumFreeMiB'],'tts-opening-worker')
 tts=c.read(H/'voice-tts-manifest.json')['tts'];scene=c.read(H/'voice-input.json')['scenes'][8];assert scene['id']=='v7-a09'
 output=F/'prefix-attempt3.wav';receipt=F/'prefix-tts.json'
 assert not output.exists()and not receipt.exists(),'This selected repair is once only; preserve existing candidate'
 import torch
 from qwen_tts import Qwen3TTSModel
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['tts']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
 model=Qwen3TTSModel.from_pretrained(str(c.R/tts['model']),device_map='cuda:0',dtype=torch.bfloat16)
 prompt=model.create_voice_clone_prompt(ref_audio=str(c.R/tts['reference']),ref_text=(c.R/tts['referenceText']).read_text(encoding='utf-8').strip(),x_vector_only_mode=False)
 warmup='이제 숫자에 붙은 약속을 확인하겠습니다.';assert warmup in c.read(H/'voice-input.json')['scenes'][7]['lines'][-1]
 text=warmup+' '+scene['lines'][0];print('Rendering only complete a09 opening paragraph for first-sentence repair',flush=True);started=time.time()
 audios,rate=model.generate_voice_clone(text=[text],language='Korean',voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=tts['maxNewTokens'])
 raw=np.asarray(audios[0],dtype=np.float32);assert rate==24000 and raw.ndim==1 and np.isfinite(raw).all()
 sf.write(output,raw,rate,subtype='PCM_16');check,_=sf.read(output,dtype='float32')
 c.save(receipt,dict(scene=scene['id'],approvedText=text,textSha256=hashlib.sha256(text.encode()).hexdigest(),file=c.rel(output),sha256=c.sha(output),sampleRate=rate,samples=len(raw),seconds=len(raw)/rate,rawFloatPeak=float(np.max(abs(raw))),hardClipSamples=int(np.sum(abs(check)>=32766/32768)),identitySha256=plan['identitySha256'],elapsedSeconds=time.time()-started,purpose='Only first sentence may replace original after measured complete-word quiet joins; not an automatic whole-scene retake',humanListening='pending'))
def transcribe(token):
 plan=c.validate(preserve_pcm=True);c.lease_worker(token);c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'],'source-opening-worker')
 prefix=c.read(F/'prefix-tts.json');scene=c.read(H/'voice-input.json')['scenes'][8];assert prefix['approvedText']=='이제 숫자에 붙은 약속을 확인하겠습니다. '+scene['lines'][0]
 assert c.sha(c.R/prefix['file'])==prefix['sha256']
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['sourceAsr']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
 local=r.model_path();assert c.sha(local/'config.json')==plan['asrIdentity']['configSha256']
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
 r.suppress_unused_encoder_attention_retention(model);model.to('cuda:0');processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
 simple=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0')
 raw,rate=sf.read(c.R/prefix['file'],dtype='int16');padding=round(.75*rate);padded=F/'prefix-asr-context.wav';sf.write(padded,np.concatenate([np.zeros(padding,dtype=np.int16),raw,np.zeros(padding,dtype=np.int16)]),rate,subtype='PCM_16')
 result=simple(str(padded),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 c.save(F/'prefix-asr.json',dict(audioSha256=prefix['sha256'],recognitionContextSha256=c.sha(padded),text=result['text'],words=result['chunks'],recognitionOnlyPadSeconds=.75,padNotInProduction=True,expectedTextPrompt=None))
 assert '지금까지쓴오일러각은' in r.normalized(result['text']),'Opening not verified; preserve candidate and do not select it'
 words=[dict(text=w['text'],timestamp=[max(0,t-.75) if t is not None else None for t in w['timestamp']])for w in result['chunks']]
 next_index=next(i for i,w in enumerate(words)if r.normalized(w['text'])=='어떤')
 assert '방식입니다'in r.normalized(words[next_index-1]['text'])
 newlow=words[next_index-1]['timestamp'][1];newhigh=words[next_index]['timestamp'][0]
 begin=next(i for i,w in enumerate(words)if '지금' in r.normalized(w['text']))
 assert begin>0 and '확인하겠습니다' in r.normalized(words[begin-1]['text'])
 beginning=a.quiet_window(raw.astype(np.float32)/32768.,rate,words[begin-1]['timestamp'][1],words[begin]['timestamp'][0],a.rms(raw.astype(np.float32)/32768.))
 assert beginning,'No measured complete-word quiet after warmup'
 ns=beginning['sampleOffset']
 oldrow=c.read(c.O/'tts-current.json')['scenes'][8];assert oldrow['id']=='v7-a09';oldfile=c.R/oldrow['file'];assert c.sha(oldfile)==oldrow['sha256']
 old,oldrate=sf.read(oldfile,dtype='int16');assert oldrate==rate
 oldasr=c.read(c.O/'asr/v7-a09.json');assert oldasr['audio_sha256']==oldrow['sha256']
 oldwords=oldasr['words'];idx=next(i for i,w in enumerate(oldwords)if r.normalized(w['text'])=='어떤')
 assert '방식입니다'in r.normalized(oldwords[idx-1]['text'])
 oldlow=oldwords[idx-1]['timestamp'][1];oldhigh=oldwords[idx]['timestamp'][0]
 newquiet=a.quiet_window(raw.astype(np.float32)/32768.,rate,newlow,newhigh,a.rms(raw.astype(np.float32)/32768.))
 oldquiet=a.quiet_window(old.astype(np.float32)/32768.,rate,oldlow,oldhigh,a.rms(old.astype(np.float32)/32768.))
 assert newquiet and oldquiet,'No verified80ms quiet seam; preserve existing source'
 nc,oc=newquiet['sampleOffset'],oldquiet['sampleOffset']
 composed=np.concatenate([raw[ns:nc],old[oc:]]);file=F/'v7-a09-first-sentence-repaired.wav';assert not file.exists()
 assert abs(int(raw[nc-1])-int(old[oc]))/32768<.002,'Quiet join discontinuity requires review'
 sf.write(file,composed,rate,subtype='PCM_16');readback,_=sf.read(file,dtype='int16')
 assert np.array_equal(readback[:nc-ns],raw[ns:nc])and np.array_equal(readback[nc-ns:],old[oc:])
 proof=dict(scene='v7-a09',sourceFile=c.rel(oldfile),sourceSha256=oldrow['sha256'],sourceAsrSha256=c.sha(c.O/'asr/v7-a09.json'),prefixFile=prefix['file'],prefixSha256=prefix['sha256'],prefixAsrFile=c.rel(F/'prefix-asr.json'),prefixAsrSha256=c.sha(F/'prefix-asr.json'),newQuiet=newquiet,oldQuiet=oldquiet,newRangeSamples=[ns,nc],warmupExcluded=True,warmupEndQuiet=beginning,unchangedSourceTailRangeSamples=[oc,len(old)],composedFile=c.rel(file),composedSha256=c.sha(file),composedSamples=len(composed),sampleRate=rate,seconds=len(composed)/rate,unchangedTailSamples=len(old)-oc,unchangedTailByteEquivalent=True,newFirstSentenceOriginalSamplesPreserved=True,newPrefixWords=result['text'],productionSilenceAddedSamples=0,timeStretch=False,voiceReferenceUnchanged=True,directCurrentFullTextReview='pending')
 c.save(F/'repair-proof.json',proof);print('First sentence repaired; unchanged source tail sample-exact; recognize new current scene once',flush=True)
 long=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
 current=long(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 c.save(F/'composed-asr.json',dict(scene='v7-a09',audio_sha256=c.sha(file),text=current['text'],words=current['chunks'],configuration=r.CONFIG,recognizer=plan['asrIdentity'],expectedTextPrompt=None,recognizedAt=time.time(),directFullTextReview='pending',humanListening='pending'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--generate',action='store_true');p.add_argument('--review',action='store_true');p.add_argument('--worker');x=p.parse_args()
 if x.worker:
  lease=c.read(c.LEASE)
  if lease['state']=='tts-opening-repair3_running':return generate(x.worker)
  assert lease['state']=='source-opening-repair3_running';return transcribe(x.worker)
 assert x.generate!=x.review;plan=c.validate();phase='tts'if x.generate else'sourceAsr';resources=plan['resources'][phase]
 c.run_worker('tts-opening-repair3'if x.generate else'source-opening-repair3',Path(__file__).resolve(),resources['allocatorCapMiB'],resources['minimumFreeMiB'])
if __name__=='__main__':main()
