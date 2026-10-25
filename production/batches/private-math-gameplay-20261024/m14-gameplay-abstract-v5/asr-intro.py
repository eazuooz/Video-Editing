"""Blind local ASR of only the newly added abstract, with exact WAV cache."""
from pathlib import Path
import json,hashlib,importlib.util,difflib
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent
O=R/'projects/game-math-polygon-partition-v2/production/local/gameplay-abstract-v5/intro-audio';Q=O/'asr';Q.mkdir(exist_ok=True)
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
spec=importlib.util.spec_from_file_location('voice_util',R/'projects/game-math-euler-axis-angle/production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
transcriber=None;rows=[]
for s in json.loads((B/'intro.ko.json').read_text('utf8'))['scenes']:
 file=O/'chunks'/f'{s["id"]}-scene.wav'
 if not file.exists():continue
 digest=hashlib.sha256(file.read_bytes()).hexdigest();dest=Q/(s['id']+'.json')
 cache=json.loads(dest.read_text('utf8')) if dest.exists() else None
 if cache is None or cache['audio_sha256']!=digest:
  if transcriber is None:
   import torch
   from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
   torch.set_num_threads(3);local=u.model_path()
   model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True);u.suppress_unused_encoder_attention_retention(model)
   processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
   transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu',chunk_length_s=25,stride_length_s=3,batch_size=1)
  result=transcriber(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  cache=dict(scene=s['id'],audio_sha256=digest,text=result['text'],words=result['chunks'],expectedPrompt=None)
  save(dest,cache)
 expected=' '.join(s['lines']);a,b=u.normalized(expected),u.normalized(cache['text']);match=difflib.SequenceMatcher(None,a,b,autojunk=False)
 rows.append(dict(scene=s['id'],expected=expected,recognized=cache['text'],similarity=match.ratio(),differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l]) for t,i,j,k,l in match.get_opcodes() if t!='equal'],actualListening=False))
 print(json.dumps(rows[-1],ensure_ascii=False),flush=True)
save(B/'intro-asr-review.json',dict(scenes=rows,complete=len(rows)==3,actualListening=False))
