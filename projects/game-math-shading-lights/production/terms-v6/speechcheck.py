"""Recognize the eight fitted sentences without a transcript prompt; measure subtitle anchor shifts."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',OMP_NUM_THREADS='2')
import re
from difflib import SequenceMatcher
from pathlib import Path
import numpy as np
import torch
import soundfile as sf
from scipy.signal import resample_poly
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
from voice import VOICE,WORK,read,write

def norm(s):return ''.join(re.findall('[가-힣a-z0-9]',s.lower()))
def chars(words):
    out='';seconds=[]
    for word in words:
        text=norm(word['text']);a,b=word['timestamp']
        if not text or a is None:continue
        b=b if b is not None else a+.14*len(text)
        for i,ch in enumerate(text):
            out+=ch;seconds.append(a+(i+.5)*(b-a)/len(text))
    return out,seconds
def run():
    model_dir=Path.home()/'.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9'
    torch.set_num_threads(3);torch.set_num_interop_threads(1)
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_dir),dtype=torch.float32,low_cpu_mem_usage=True,attn_implementation='eager').eval()
    processor=AutoProcessor.from_pretrained(str(model_dir))
    pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,device=-1)
    audit=[];maps=[]
    for t in read(VOICE/'mix.json'):
        wav,sr=sf.read(VOICE/(t['id']+'-fitted.wav'),dtype='float32');assert sr==48000
        rec=pipe({'array':resample_poly(wav,1,3),'sampling_rate':16000},return_timestamps='word',generate_kwargs={'language':'korean','task':'transcribe','condition_on_prev_tokens':False})
        expected=t['spoken'];heard=rec['text'];fine=SequenceMatcher(None,norm(expected),norm(heard),autojunk=False).ratio()
        audit.append(dict(id=t['id'],expected=expected,heard=heard,match=round(fine,3),words=rec['chunks']))
        prev=read(WORK.parent/'render-v4/final-mix-review/paragraphs'/(t['scene']+'-01.json'))
        old_text,old_time=chars(prev['chunks']);new_text,new_time=chars(rec['chunks'])
        base=t['beginSample']/sr;end=t['endSample']/sr
        times=[prev['entry']['start']+x for x in old_time];selected=[j for j,z in enumerate(times) if base<z<end]
        sequence=''.join(old_text[i] for i in selected);anchors=[(base,base)]
        for b in SequenceMatcher(None,sequence,new_text,autojunk=False).get_matching_blocks():
            if b.size<2:continue
            for k in range(b.size):
                a=times[selected[b.a+k]];d=base+new_time[b.b+k]
                if base<a<end and base<d<end and a>anchors[-1][0] and d>anchors[-1][1]:anchors.append((a,d))
        anchors.append((end,end));maps.append(dict(id=t['id'],anchors=anchors))
    write(VOICE/'speech-check.json',audit);write(VOICE/'timing-maps.json',maps)
    print([(m['id'],m['match'],m['heard']) for m in audit],flush=True)
if __name__=='__main__':run()
