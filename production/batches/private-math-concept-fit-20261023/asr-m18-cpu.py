"""Blind recognition of all nine changed scene joins, with exact-audio caches."""
from common import *
import importlib.util,difflib,time,re
P=R/'projects/game-math-projection-depth';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2/audio';Q=O/'asr';Q.mkdir(exist_ok=True)
authorized('M18');T=read(H/'timeline.json');script={s['id']:s for s in read(P/'script/concept-fit-v2/narration.ko.json')['scenes']};edit=read(B/'m18-narration-edits.json')['edits']
spec=importlib.util.spec_from_file_location('math_asr_util',R/'projects/game-math-euler-axis-angle/production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
state=dict(device='cpu',startedAt=now(),reason='Insufficient free GPU memory; preserve other apps and run the same blind ASR model on CPU.')
try:
 transcriber=None;rows=[]
 for s in T['scenes']:
  if s['id'] not in edit:continue
  authorized('M18');file=R/s['voice'];assert sha(file)==s['voiceSha256'];dest=Q/(s['id']+'.json')
  if dest.exists():
   cache=read(dest);assert cache['audioSha256']==s['voiceSha256'],'Preserve different-ASR cache'
  else:
   if transcriber is None:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(4)
    local=u.model_path();model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True);u.suppress_unused_encoder_attention_retention(model);model.to('cpu')
    processor=AutoProcessor.from_pretrained(str(local),local_files_only=True);transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu',chunk_length_s=25,stride_length_s=3,batch_size=1)
   print('Recognizing',s['id'],s['seconds'],flush=True)
   result=transcriber(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   cache=dict(scene=s['id'],audioSha256=s['voiceSha256'],text=result['text'],words=result['chunks'],recognizedAt=now(),expectedPrompt=None,automaticSpeechPass=False,configuration=u.CONFIG);save(dest,cache)
  expected=' '.join(script[s['id']]['lines']);a,b=u.normalized(expected),u.normalized(cache['text']);m=difflib.SequenceMatcher(None,a,b,autojunk=False)
  rows.append(dict(scene=s['id'],expected=expected,recognized=cache['text'],audioSha256=s['voiceSha256'],asrFile=rel(dest),similarity=m.ratio(),differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l]) for t,i,j,k,l in m.get_opcodes() if t!='equal'],directTextReview='pending',listening='pending'))
  save(H/'changed-scene-asr-review.json',dict(complete=len(rows)==len(edit),scenes=rows,actualAudioReviewed=False))
 state['state']='complete'
finally:
 state['endedAt']=now();save(O/'asr-execution.json',state)
