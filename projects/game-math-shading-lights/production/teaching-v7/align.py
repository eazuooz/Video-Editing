"""Listen via unprompted local ASR; align the independently written bilingual clauses."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',OMP_NUM_THREADS='3')
import json,re,time
from pathlib import Path
from difflib import SequenceMatcher
from bisect import bisect_left
import torch
import soundfile as sf
import numpy as np
from scipy.signal import resample_poly
from math import gcd
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
from narration import LESSONS
voice=Path(__file__).resolve().parents[2]/'production/local/render-v7/speech'
def norm(s):return ''.join(re.findall('[가-힣a-z0-9]',s.lower()))
def display(s):
    for word,screen in [('구로 셰이딩','Gouraud Shading (구로 셰이딩)'),('퐁 셰이딩','Phong Shading (퐁 셰이딩)'),('퐁 조명 모델','Phong Reflection Model (퐁 반사 모델)'),('이레디언스','Irradiance (복사조도)'),('하프 램버트','Half Lambert (하프 램버트)'),('마이너스 엘','−L'),('엘은','L은'),('엘과','L과'),('알을','R을'),('씨는','C는'),('람다는','λ는'),('케이는','k는'),('디는','d는'),('엑스는','x는'),('에스 엑스는','sₓ는')]:
        s=s.replace(word,screen)
    return s.replace('에스 x는','sₓ는').replace('d는 각 광원','D는 각 광원')
def chunks(text):
    words=text.split();parts=[];start=0
    while len(' '.join(words[start:]))>30:
        options=[]
        for j in range(start+1,len(words)):
            a=' '.join(words[start:j]);b=' '.join(words[j:])
            if len(a)>34:break
            if len(a)>=12 and len(b)>=8:options.append((abs(len(a)-22)-(6 if a.endswith(',') else 0),j))
        if not options:break
        j=min(options)[1];parts.append(' '.join(words[start:j]));start=j
    return parts+[' '.join(words[start:])]
def run():
    modeldir=Path.home()/'.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9'
    torch.set_num_threads(3);torch.set_num_interop_threads(1)
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modeldir),dtype=torch.float32,low_cpu_mem_usage=True,attn_implementation='eager').eval()
    proc=AutoProcessor.from_pretrained(str(modeldir))
    pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,device=-1)
    for sid,clauses in LESSONS.items():
        f=voice/'chunks'/f'{sid:03}-scene.wav';deadline=time.monotonic()+1600
        while not f.is_file() or f.stat().st_size<1000:
            if time.monotonic()>deadline:raise RuntimeError(f'Missing {f}')
            time.sleep(2)
        audio,sr=sf.read(f,dtype='float32');duration=len(audio)/sr
        rec=pipe({'array':resample_poly(audio,16000//gcd(sr,16000),sr//gcd(sr,16000)),'sampling_rate':16000},return_timestamps='word',generate_kwargs={'language':'korean','task':'transcribe','condition_on_prev_tokens':False})
        observed='';times=[]
        for word in rec['chunks']:
            w=norm(word['text']);a,b=word['timestamp']
            if a is None or not w:continue
            b=duration if b is None else b
            for i,ch in enumerate(w):observed+=ch;times.append(a+(b-a)*(i+.5)/len(w))
        expected=norm(''.join(ko for ko,en in clauses));match=SequenceMatcher(None,expected,observed,autojunk=False);anchors=[(0,0.)]
        for blk in match.get_matching_blocks():
            if blk.size<2:continue
            for k in range(blk.size):
                x=blk.a+k+.5;t=times[blk.b+k]
                if x>anchors[-1][0] and t>anchors[-1][1] and t<duration:anchors.append((x,t))
        anchors.append((len(expected),duration));xx,tt=zip(*anchors)
        def when(i):return round(float(np.interp(i,xx,tt)),4)
        ko_rows=[];en_rows=[];bound=[];pos=0
        for ko,en in clauses:
            a=when(pos);bound.append(a)
            for phrase in chunks(ko):
                k0=when(pos);pos+=len(norm(phrase));k1=when(pos)
                ko_rows.append(dict(start=k0,end=k1,text=display(phrase)))
            en_rows.append(dict(start=a,end=when(pos),text=en))
        data=dict(scene=sid,duration=duration,asr=rec['text'],similarity=round(match.ratio(),3),clauses=bound,ko=ko_rows,en=en_rows)
        (voice/f'{sid:03}-alignment.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8');print(sid,data['similarity'],duration,flush=True)
if __name__=='__main__':run()
