"""Recognize only selected QA candidates or the one actually changed scene."""
from pathlib import Path
import argparse,difflib,hashlib,importlib.util,json,time
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_repair_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_repair_whisper',c.P/'production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
def worker(token,mode):
 plan=c.validate();c.lease_worker(token);script={s['id']:s for s in c.read(H/'voice-input.json')['scenes']};source=c.read(c.O/'tts-current.json')
 if mode in ['candidates','alias']:
  candidates=c.read(c.O/'retake-candidates.json')['candidates'];candidates=[r for r in candidates if bool(r.get('pronunciationAlias'))==(mode=='alias')]
  assert len(candidates)==(1 if mode=='alias'else 2)and all(r['scene']=='m07'and r['line']==2 for r in candidates)
  targets=[dict(id=r['id'],scene=r['scene'],file=r['file'],sha256=r['sha256'],expected=script[r['scene']]['lines'][r['line']-1])for r in candidates]
 else:
  decision=c.read(c.O/'repair-selection.json');assert decision['token']==token and decision['sourceReceiptSha256']==c.sha(c.O/'tts-current.json');row=next(s for s in source['scenes']if s['id']=='m07')
  targets=[dict(id='m07',scene='m07',file=row['file'],sha256=row['sha256'],expected=' '.join(script['m07']['lines']))]
 identity=hashlib.sha256(json.dumps(dict(config=u.CONFIG,model=plan['asrIdentity'],scope=mode),sort_keys=True).encode()).hexdigest();q=c.O/'repair-asr';q.mkdir(exist_ok=True);recognizer=None;rows=[]
 for target in targets:
  file=c.R/target['file'];assert c.sha(file)==target['sha256'];cachefile=q/(target['id']+'.json')
  if cachefile.exists():
   row=c.read(cachefile);assert row['audio_sha256']==target['sha256']and row['recognitionIdentitySha256']==identity
  else:
   if recognizer is None:
    c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'])
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['sourceAsr']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
    local=u.model_path();assert c.sha(local/'config.json')==plan['asrIdentity']['configSha256']
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
    u.suppress_unused_encoder_attention_retention(model);model.to('cuda:0');proc=AutoProcessor.from_pretrained(str(local),local_files_only=True)
    recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
   print('Recognize changed-scope only',target['id'],flush=True)
   result=recognizer(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   row=dict(scene=target['scene'],id=target['id'],audioFile=target['file'],audio_sha256=target['sha256'],recognitionIdentitySha256=identity,configuration=u.CONFIG,
    expectedPrompt=None,text=result['text'],words=result['chunks'],recognizedAt=time.time(),humanListening='pending',directTextReview='pending')
   c.save(cachefile,row);torch.cuda.empty_cache()
  rows.append(row)
 if mode in ['candidates','alias']:
  c.save(c.O/('alias-asr-review.json'if mode=='alias'else'retake-asr-review.json'),dict(revision='orientation-matrix-v8',sourceReceiptSha256=c.sha(c.O/'tts-current.json'),candidateAsrs=rows,selected=False,humanListening='pending'))
 else:
  row=rows[0];review=c.read(c.O/'source-asr-review.json');target=targets[0];a,b=u.normalized(target['expected']),u.normalized(row['text']);m=difflib.SequenceMatcher(None,a,b,autojunk=False)
  replacement=dict(scene='m07',audioFile=target['file'],audioSha256=target['sha256'],asrFile=c.rel(q/'m07.json'),asrSha256=c.sha(q/'m07.json'),
   expected=target['expected'],recognized=row['text'],similarity=m.ratio(),differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l])for t,i,j,k,l in m.get_opcodes()if t!='equal'],
   directFullTextReview='pending changed-scene direct comparison',humanListening='pending',repairSelection=c.rel(c.O/'repair-selection.json'))
  review['scenes']=[replacement if x['scene']=='m07'else x for x in review['scenes']];review['reusedUnchangedSceneAsrs']=12;c.save(c.O/'source-asr-review.json',review)
 print('Finished bounded',mode,'ASR phase',len(targets),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worker',required=True);p.add_argument('--mode',choices=['candidates','alias','current'],required=True);x=p.parse_args();worker(x.worker,x.mode)
