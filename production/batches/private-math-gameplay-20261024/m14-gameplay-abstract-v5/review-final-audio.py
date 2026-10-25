"""Blind recognition of the mixed added abstract after edge fades and ducking."""
from pathlib import Path
import importlib.util,json,hashlib,difflib
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent;P=R/'projects/game-math-polygon-partition-v2';H=P/'production/gameplay-abstract-v5';O=P/'production/local/gameplay-abstract-v5';file=O/'intro-mix.wav'
spec=importlib.util.spec_from_file_location('u',R/'projects/game-math-euler-axis-angle/production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
torch.set_num_threads(3);local=u.model_path();model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True);u.suppress_unused_encoder_attention_retention(model)
processor=AutoProcessor.from_pretrained(str(local),local_files_only=True);rec=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
audioHash=hashlib.sha256(file.read_bytes()).hexdigest()
r=rec(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
assert audioHash==hashlib.sha256(file.read_bytes()).hexdigest(),'Audio changed while recognition was running.'
expected=' '.join(' '.join(s['lines']) for s in json.loads((B/'intro.ko.json').read_text('utf8'))['scenes']);a,b=u.normalized(expected),u.normalized(r['text']);m=difflib.SequenceMatcher(None,a,b,autojunk=False)
out=dict(audio=file.relative_to(R).as_posix(),audioSha256=hashlib.sha256(file.read_bytes()).hexdigest(),expected=expected,recognized=r['text'],similarity=m.ratio(),differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l]) for t,i,j,k,l in m.get_opcodes() if t!='equal'],words=r['chunks'],expectedPrompt=None,sourceTtsTailGuards=dict(A='best of3; tail0.259 / decay61ms',B='clean; tail0.044 / decay118ms',C='best of3; tail0.094 / decay72ms'),edgeTreatment='40ms fade at new intro sentence ends only; existing body untouched',actualListening=False)
(H/'intro-mix-asr.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='words'},ensure_ascii=False),flush=True)
