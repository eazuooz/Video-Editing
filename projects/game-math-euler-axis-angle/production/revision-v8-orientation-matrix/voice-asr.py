"""Recognize all current13 assembled source scenes once; no expected prompt."""
from pathlib import Path
import argparse,difflib,hashlib,importlib.util,json,time
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_source_asr_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
# Reuse only the already tested recognizer/model-loading utility, not V7 text.
s=importlib.util.spec_from_file_location('v8_whisper_utilities',c.P/'production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
CONFIG=u.CONFIG
def worker(token):
 plan=c.validate();c.lease_worker(token);completed=c.read(c.O/'tts-current.json');assert completed['sceneCount']==13 and completed['paragraphCount']==76
 script=c.read(H/'voice-input.json');byid={x['id']:x for x in script['scenes']};qa=c.O/'asr';qa.mkdir(exist_ok=True)
 identity=hashlib.sha256(json.dumps(dict(config=CONFIG,model=plan['asrIdentity']),sort_keys=True).encode()).hexdigest();transcriber=None;rows=[]
 for audio in completed['scenes']:
  c.selected();file=c.R/audio['file'];assert c.sha(file)==audio['sha256'];cache_file=qa/(audio['id']+'.json')
  if cache_file.exists():
   cache=c.read(cache_file);assert cache['audio_sha256']==audio['sha256']and cache['recognitionIdentitySha256']==identity;print('Reused exact successful source ASR',audio['id'],flush=True)
  else:
   if transcriber is None:
    c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'])
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['sourceAsr']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
    local=u.model_path();assert c.sha(local/'config.json')==plan['asrIdentity']['configSha256']
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
    u.suppress_unused_encoder_attention_retention(model);model.to('cuda:0');processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
   print('Recognizing current source once',audio['id'],flush=True)
   result=transcriber(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   cache=dict(scene=audio['id'],audio_sha256=audio['sha256'],recognitionIdentitySha256=identity,configuration=CONFIG,text=result['text'],words=result['chunks'],recognizedAt=time.time(),expectedPrompt=None,automaticSpeechPass=False)
   c.save(cache_file,cache);torch.cuda.empty_cache()
  expected=' '.join(byid[audio['id']]['lines']);a,b=u.normalized(expected),u.normalized(cache['text']);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
  rows.append(dict(scene=audio['id'],audioFile=audio['file'],audioSha256=audio['sha256'],asrFile=c.rel(cache_file),asrSha256=c.sha(cache_file),expected=expected,recognized=cache['text'],similarity=matcher.ratio(),
   differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l])for t,i,j,k,l in matcher.get_opcodes()if t!='equal'],directFullTextReview='pending',humanListening='pending'))
  c.save(c.O/'source-asr-review.json',dict(revision='orientation-matrix-v8',complete=len(rows)==13,sceneCount=len(rows),paragraphCount=76,scenes=rows,wholeFinalMixAsr='separate current encoded mix review later; source ASR cannot substitute'))
 print('All13 source ASRs cached; full76-paragraph direct review and actual word alignment pending',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worker',required=True);x=p.parse_args();worker(x.worker)
